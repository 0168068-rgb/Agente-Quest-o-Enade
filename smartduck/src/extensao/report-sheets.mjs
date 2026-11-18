import {buildAudit} from './audit.mjs';

export function reportSheets(report,records){
  const a=buildAudit(records,report),context=report.period.text+' · Semestre · '+(a.ava.account||'Professor AVA não verificado');
  const scope=a.complete?'Conferência concluída nas opções disponíveis da conta.':'Conferência incompleta: consulte Pendências. Não verificado não significa ausência.';
  const sheet=(name,headers,rows,note=scope)=>({name,title:name,note:context+' — '+note,headers,rows});
  const studentHeaders=['Período','Unidade','Disciplina','Turma no AVA','Turma no SophiA / prevista','RA','Aluno','Resultado','Critério de comparação'];
  const studentRow=s=>[s.period,s.campus,s.discipline,s.avaClass,s.sophiaClass,s.ra,s.name,s.status,s.method];
  return [
    sheet('Turmas com divergências',['Período','Unidade','Disciplina','Turma no AVA','Turmas no SophiA','Alunos AVA lidos','Lista AVA completa','Encontrados','RAs não localizados','Identificação pendente','Divergências'],a.classDivergences.map(c=>[c.period,c.campus,c.discipline,c.avaClass,c.sophiaClasses,c.studentsAva,c.rosterComplete?'Sim':'Não',c.found,c.missing,c.unresolved,c.detail])),
    sheet('Alunos só no AVA',studentHeaders,a.onlyAva.map(studentRow),'Lista obtida dos participantes do AVA. Cada linha informa se a ausência foi confirmada por RA ou se depende de conferência por nome. '+scope),
    sheet('Campos AD AI PS',['Período','Unidade','Turma','Disciplina','Avaliação','Situação','Editáveis','Vazios editáveis','Preenchidos'],a.fields.map(f=>[f.period,f.campus,f.course,f.discipline,f.exam,f.status,f.editable,f.empty,f.filled]),'AD, AI e PS são distintas de AS e AE. '+scope),
    sheet('Pendências',['Tipo','Período','Unidade','Curso','Disciplina','Avaliação','RA','Aluno','Detalhe','Arquivo / aba','Linha'],a.issues.map(i=>[i.kind,i.period,i.campus,i.course,i.discipline,i.exam,i.ra,i.name,i.detail,i.source,i.line])),
    sheet('Alunos dos arquivos',['Período','Unidade','Curso','Período do curso','Disciplina','Código','Vínculo AVA','Esperados nos arquivos','Encontrados','Ausentes','Resultado'],a.groups.map(g=>[g.period,g.campus,g.course,g.curricularPeriod,g.discipline,g.code,g.scope,g.expected,g.found??'Não verificado',g.missing??'Não verificado',g.status]),'Base desta aba: arquivos enviados. A aba Alunos só no AVA usa a lista do próprio AVA.'),
    sheet('Lançamentos',['RA','Aluno','Unidade','Curso','Disciplina','Avaliação','Destino','Nota anterior','Nota original','Nota proposta','Resultado','Arquivo / aba','Linha'],(report.rows||[]).map(r=>[r.ra,r.name,r.campus,r.course,r.discipline,r.exam,r.taskLabel,r.before,r.raw,r.after,r.status,r.source,r.line]),'Somente valores confirmados por releitura são marcados como gravados.'),
    sheet('Mapa SophiA',['Período','Unidade','Turma','Etapa','Disciplina','Página','Avaliações','Alunos','Situação'],(report.portalMap||[]).map(d=>[d.periodo.text,d.unidade?.text,d.turma?.text,d.etapa?.text||'Semestre',d.disciplina?.text,d.page,d.assessments?.join(' / '),d.students,d.status])),
    sheet('Vínculos AVA',['Período','Código da turma','Disciplina','Função','Vínculo verificado','Lista de alunos completa','Correspondência SophiA'],(a.ava.courses||[]).map(c=>[c.period,c.code,c.name,c.role,c.verified?'Sim':'Não',c.teacher?(c.rosterComplete?'Sim':'Não'):'Fora do vínculo docente',a.avaDisciplines.find(d=>d.id===c.id)?.status||c.error||'Fora do vínculo docente'])),
    sheet('Alunos AVA conferidos',studentHeaders,a.students.map(studentRow),'Participantes identificados como alunos nas disciplinas com vínculo docente confirmado. '+scope)
  ];
}
