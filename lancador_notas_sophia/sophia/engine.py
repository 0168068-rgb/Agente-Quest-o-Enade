from __future__ import annotations

import asyncio
import tempfile
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

from .data import Record, course_in_class, grade_value, identifier, normalize, unit_name
from .portal import BrowserPortal, Cancelled, PortalDialogBlocked, Task
from .report import write_report


@dataclass(frozen=True)
class RunConfig:
    period: str
    exam: str
    courses: tuple[str, ...]
    simulation: bool
    output_folder: Path
    grade_max: int = 10


@dataclass
class RunResult:
    path: Path
    results: list[dict]
    pending: list[dict]
    absent: list[dict]
    omitted: int
    partial: bool
    error: str = ""


def same_discipline(left: str, right: str) -> bool:
    a, b = normalize(left), normalize(right)
    return bool(a and b) and (a == b or SequenceMatcher(None, a, b).ratio() >= 0.90)


def in_task(record: Record, task: Task, single_unit: bool) -> bool:
    unit_ok = unit_name(task.unit.text) in record.units if record.units else single_unit
    return unit_ok and course_in_class(task.classroom.text, record.course) and same_discipline(record.discipline, task.discipline.text)


def match_student(record, students):
    if record.registration:
        candidates = [s for s in students if identifier(s.registration) == record.registration]
    else:
        candidates = [s for s in students if normalize(s.name) == normalize(record.name)] if record.name else []
    return candidates[0] if len(candidates) == 1 else None, len(candidates)


def report_row(record, config, status, task=None):
    return {"Linha de origem": record.line, "Aluno": record.name, "RA": record.registration,
            "Curso": record.course, "Polo": task.unit.text if task else " / ".join(record.units),
            "Turma": task.classroom.text if task else "", "Etapa": task.stage.text if task else "",
            "Disciplina": record.discipline, "Avaliação": config.exam,
            "Nota": record.raw_grade, "Status / Motivo": status}


async def run(config: RunConfig, records: list[Record], cancel_event, emit, portal=None) -> RunResult:
    if config.exam not in {"AD", "AI", "PS", "AE"} or not config.period or not records or config.grade_max not in (10, 100):
        raise ValueError("Configuração de execução inválida.")
    # Verificar a pasta antes de abrir o navegador ou realizar gravações.
    config.output_folder.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=config.output_folder):
        pass
    portal = portal or BrowserPortal(cancel_event, emit, diagnostic_folder=config.output_folder)
    results, absent, decisions = {}, {}, {}
    tasks, units = [], []
    complete_inventory = False
    partial, error = False, ""
    terminal = set()
    def check():
        if cancel_event.is_set():
            raise Cancelled("Cancelado pelo usuário.")
    try:
        await portal.open()
        check()
        periods = await portal.options("periodo")
        period = next((p for p in periods if normalize(p.text) == normalize(config.period)), None)
        if period is None:
            raise RuntimeError(f"Período {config.period} indisponível no portal. Nenhuma nota foi preenchida.")
        await portal.select("periodo", period)
        units = await portal.options("unidade")
        if not units:
            raise RuntimeError("Não há unidades disponíveis no portal.")
        for unit in units:
            check()
            emit({"message": f"Consultando turmas e disciplinas: {unit.text}."})
            await portal.restore(period, unit)
            classrooms = [c for c in await portal.options("turma") if any(course_in_class(c.text, course) for course in config.courses)]
            for classroom in classrooms:
                check()
                await portal.restore(period, unit, classroom)
                stages = await portal.options("etapa")
                if not stages:
                    raise RuntimeError(f"Não há etapas disponíveis em {unit.text} / {classroom.text}; inventário incompleto.")
                for stage in stages:
                    await portal.restore(period, unit, classroom, stage)
                    disciplines = await portal.options("disciplina")
                    if not disciplines:
                        raise RuntimeError(f"Lista de disciplinas vazia em {unit.text} / {classroom.text} / {stage.text}; inventário incompleto.")
                    for discipline in disciplines:
                        tasks.append(Task(period, unit, classroom, stage, discipline))
        complete_inventory = True
        single_unit = len(units) == 1
        relevant_tasks = [task for task in tasks if any(in_task(r, task, single_unit) for r in records)]
        # Duplicatas na fonte não devem gravar duas notas no mesmo cadastro.
        identities = {}
        for record in records:
            identity = (record.units, normalize(record.course), normalize(record.discipline),
                        ("ra", record.registration) if record.registration else ("nome", normalize(record.name)))
            identities.setdefault(identity, []).append(record)
        for group in identities.values():
            if len(group) > 1:
                for record in group:
                    decisions[record.key] = report_row(record, config, "Registro duplicado na planilha; conferir antes do lançamento")
                    terminal.add(record.key)
        for number, task in enumerate(relevant_tasks, 1):
            check()
            emit({"message": f"{task.unit.text} • {task.classroom.text} • {task.discipline.text} ({task.stage.text})", "current": number - 1, "total": len(relevant_tasks)})
            candidates = [r for r in records if in_task(r, task, single_unit)]
            await portal.restore(task.period, task.unit, task.classroom, task.stage, task.discipline)
            await portal.search()
            header, students = await portal.roster(config.exam)
            # Registrar alunos sem fonte apenas nas disciplinas dentro do escopo.
            for student in students:
                source_match = any((r.registration and r.registration == identifier(student.registration)) or
                                   (not r.registration and normalize(r.name) == normalize(student.name)) for r in candidates)
                if not source_match:
                    key = (task.unit.value, task.classroom.value, task.stage.value, task.discipline.value, student.registration, student.name)
                    absent[key] = {"Aluno": student.name, "RA": student.registration,
                                   "Curso": ", ".join(c for c in config.courses if course_in_class(task.classroom.text, c)),
                                   "Polo": task.unit.text, "Turma": task.classroom.text, "Etapa": task.stage.text,
                                   "Disciplina": task.discipline.text, "Avaliação": config.exam,
                                   "Nota": student.value, "Status / Motivo": "Aluno no portal sem correspondência na planilha"}
            matched = []
            for record in candidates:
                check()
                if record.key in terminal:
                    continue
                try:
                    value = grade_value(record.raw_grade, max_grade=config.grade_max)
                except ValueError as exc:
                    decisions[record.key] = report_row(record, config, str(exc), task)
                    terminal.add(record.key)
                    continue
                if value is None:
                    decisions[record.key] = report_row(record, config, "Nota ausente na planilha", task)
                    terminal.add(record.key)
                    continue
                student, count = match_student(record, students)
                if count != 1:
                    reason = "Correspondência ambígua no portal" if count > 1 else "Aluno não localizado nas turmas consultadas"
                    decisions[record.key] = report_row(record, config, reason, task)
                    continue
                if not header or not student.input_selector:
                    decisions[record.key] = report_row(record, config, "Campo da avaliação ausente, bloqueado ou ambíguo", task)
                    continue
                matched.append((record, student, value))
            # Duas linhas (uma sem RA, outra com RA) podem apontar ao mesmo aluno.
            frequencies = {}
            for _, student, _ in matched:
                frequencies[student.key] = frequencies.get(student.key, 0) + 1
            filled = []
            batch_failed = False
            for record, student, value in matched:
                check()
                if frequencies[student.key] != 1:
                    decisions[record.key] = report_row(record, config, "Mais de uma linha aponta ao mesmo aluno; correspondência ambígua", task)
                    terminal.add(record.key)
                    continue
                try:
                    await portal.fill(student, value)
                except Cancelled:
                    raise
                except Exception as exc:
                    batch_failed = True
                    decisions[record.key] = report_row(record, config, f"Falha no preenchimento: {exc}", task)
                    continue
                if config.simulation:
                    results[record.key] = report_row(record, config, "Preenchido em simulação — não gravado", task)
                    terminal.add(record.key)
                    decisions.pop(record.key, None)
                else:
                    decisions[record.key] = report_row(record, config, "Preenchido, mas ainda não gravado", task)
                    filled.append((record, student, value))
            if batch_failed and not config.simulation:
                for record, _, _ in filled:
                    decisions[record.key] = report_row(record, config, "Lote não gravado devido a uma falha no preenchimento; conferir antes de tentar novamente", task)
                filled = []
            if filled and not config.simulation:
                check()
                emit({"message": f"{len(filled)} nota(s) preenchida(s). Solicitando gravação e conferindo novamente no portal."})
                # Não repetir automaticamente uma gravação sem confirmação.
                for record, _, _ in filled:
                    terminal.add(record.key)
                    decisions[record.key] = report_row(record, config, "Gravação não confirmada; conferir no portal antes de tentar novamente", task)
                try:
                    refreshed = await portal.save_and_reload(task, config.exam)
                    for record, _, value in filled:
                        student, count = match_student(record, refreshed)
                        try:
                            verified = count == 1 and grade_value(student.value, max_grade=config.grade_max) == value
                        except ValueError:
                            verified = False
                        if verified:
                            results[record.key] = report_row(record, config, "Gravado — valor confirmado por releitura do portal", task)
                            decisions.pop(record.key, None)
                        elif getattr(portal, "last_portal_message", ""):
                            decisions[record.key] = report_row(record, config, "Gravação não confirmada; mensagem do portal: " + portal.last_portal_message, task)
                except Cancelled:
                    raise
                except PortalDialogBlocked as exc:
                    for record, _, _ in filled:
                        decisions[record.key] = report_row(record, config, "Gravação não confirmada; " + str(exc), task)
                    raise
                except Exception as exc:
                    emit({"message": f"Não foi possível confirmar a gravação: {exc}. O lote ficará pendente e não será repetido."})
            emit({"message": f"Etapa concluída: {len(results)} resultados acumulados.", "current": number, "total": len(relevant_tasks)})
    except Cancelled as exc:
        partial, error = True, str(exc)
    except Exception as exc:
        partial, error = True, str(exc)
        emit({"message": "Processamento interrompido: " + error})
    finally:
        try:
            await portal.close()
        except Exception as exc:
            emit({"message": f"Aviso ao fechar navegador: {exc}"})
    pending, omitted = [], 0
    single_unit = len(units) == 1
    for record in records:
        if record.key in results:
            continue
        available = any(in_task(record, task, single_unit) for task in tasks)
        known_unit = any(unit_name(u.text) in record.units for u in units) if record.units else single_unit
        # Só omitir quando houve um inventário completo, no polo correto.
        if complete_inventory and known_unit and not available:
            omitted += 1
            continue
        if record.key in decisions:
            pending.append(decisions[record.key])
        else:
            if not complete_inventory:
                reason = "Não consultado: inventário interrompido por cancelamento ou erro"
            elif not known_unit:
                reason = "Polo ausente, ambíguo ou não disponível no portal; conferir a coluna Polo"
            elif partial:
                reason = "Não processado: execução interrompida por cancelamento ou erro"
            else:
                reason = "Aluno não localizado nas turmas consultadas"
            pending.append(report_row(record, config, reason))
    assert len(results) + len(pending) + omitted == len(records)
    path = write_report(config.output_folder, list(results.values()), pending, list(absent.values()), partial)
    return RunResult(path, list(results.values()), pending, list(absent.values()), omitted, partial, error)
