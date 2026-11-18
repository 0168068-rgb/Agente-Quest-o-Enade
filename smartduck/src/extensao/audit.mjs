import {norm,raKey,equivalent,csvText} from './core.mjs';
import {unitKey,courseMatches,classPeriod,disciplineMatches} from './batch-core.mjs';
import {avaScope} from './ava.mjs';
import {reconcileAva,avaDestination} from './reconcile.mjs';

const modality=r=>/^SEMIPRESENCIAL\b/.test(norm(r.course))||/\bSEMI(?:PRESENCIAL)?\b/.test(norm(r.source).replace(/[^A-Z0-9]/g,' '))?'S':/\bEAD\b/.test(norm(r.course+' '+r.source).replace(/[^A-Z0-9]/g,' '))?'G':'';
const periodOf=(r,report,byRecord)=>r.academicPeriod?norm(r.academicPeriod).replace(/(20\d{2})[\/-]([12])/,'$1.$2'):(byRecord?.get(r.recordId)||(report.periods?.length===1?report.periods[0].text:report.periods?.length>1?'':report.period?.text||''));
const destinationKey=d=>JSON.stringify([d.periodo?.value,d.unidade?.value,d.turma?.value,d.disciplina?.value]);
function scopeMatches(r,d,period,ignoreCurricular=false){
  if(d.periodo?.text!==period)return false;
  if(r.campus&&unitKey(r.campus)!==unitKey(d.unidade?.text))return false;
  if(d.turma){
    if(r.course&&!courseMatches(r.course,d.turma.text))return false;
    const m=modality(r),p=classPeriod(d.turma.text);
    if(m==='G'&&/^S\s*-/.test(norm(d.turma.text)))return false;
    if(m==='S'&&/^[A-Z]\s*-/.test(norm(d.turma.text))&&!/^S\s*-/.test(norm(d.turma.text)))return false;
    if(!ignoreCurricular&&p&&r.period&&Number(p)!==Number(r.period))return false;
  }
  return !d.disciplina||disciplineMatches(r,d.disciplina);
}
export function recordInAva(r,c,period){
  if(c.period!==period||!c.verified||!c.teacher)return false;
  if(norm(r.discipline)!==norm(c.discipline))return false;
  if(c.disciplineCode&&r.code&&norm(c.disciplineCode).replace(/^0+/,'')!==norm(r.code).replace(/^0+/,''))return false;
  if(modality(r)&&c.modality&&modality(r)!==c.modality)return false;
  return !c.campus||!r.campus||unitKey(c.campus)===unitKey(r.campus);
}

export function buildAudit(records,report){
  const byRecord=new Map((report.cycle?.groups||[]).flatMap(g=>g.recordIds.map(id=>[id,g.period.text])));
  const ava=report.ava||{status:'unavailable',complete:false,courses:[],warnings:['AVA não verificado.']};
  const courses=(ava.courses||[]).map(avaScope);
  const issues=[],add=(kind,detail,context={})=>issues.push({kind,detail,...context});
  const destinations=new Map();
  for(const d of report.portalMap||[]){
    if(!d.disciplina)continue;
    const key=destinationKey(d);
    if(!destinations.has(key))destinations.set(key,{...d,roster:[],columns:[],pages:[],failed:false,rosterKnown:true});
    const a=destinations.get(key);a.failed||=!!d.failed;a.pages.push(d.page||1);
    // Old reports cannot prove roster coverage. Never convert unknown into zero.
    if(!d.failed&&!Array.isArray(d.roster))a.rosterKnown=false;
    a.roster.push(...(d.roster||[]));
    for(const c of d.columns||[]){let col=a.columns.find(x=>x.exam===c.exam);if(!col){col={exam:c.exam,editable:0,empty:0,filled:0};a.columns.push(col);}col.editable+=c.editable||0;col.empty+=c.empty||0;col.filled+=c.filled||0;}
  }
  const data=[...destinations.values()];
  const rosterGroups=new Map();
  for(const r of records){
    const period=periodOf(r,report,byRecord),scope=courses.filter(c=>recordInAva(r,c,period));
    // The supplied files can include all teachers. Count only confirmed
    // disciplines when AVA coverage is complete; keep the remainder explicit.
    const inScope=scope.length>0,verified=ava.complete;
    const key=JSON.stringify([period,unitKey(r.campus),norm(r.course),r.period,norm(r.code),norm(r.discipline)]);
    if(!rosterGroups.has(key))rosterGroups.set(key,{period,campus:r.campus,course:r.course,curricularPeriod:r.period,code:r.code,discipline:r.discipline,records:[],ava:scope.map(c=>c.code),scope:inScope?'Professor confirmado':verified?'Fora do vínculo docente confirmado':'Vínculo AVA não verificado'});
    rosterGroups.get(key).records.push(r);
  }
  const groups=[];
  for(const group of rosterGroups.values()){
    const unique=new Map();for(const r of group.records){const key=raKey(r.ra);if(!unique.has(key))unique.set(key,r);}
    const source=[...unique.values()],r=source[0];
    if(group.scope!=='Professor confirmado'){groups.push({...group,records:undefined,expected:unique.size,found:null,missing:null,status:group.scope});continue;}
    const relevant=data.filter(d=>scopeMatches(r,d,group.period));
    const failed=(report.portalMap||[]).some(d=>(d.failed||!d.disciplina&&d.turma)&&scopeMatches(r,d,group.period,true));
    const incomplete=!report.complete||failed||relevant.some(d=>!d.rosterKnown||d.failed);
    const broader=data.filter(d=>scopeMatches(r,d,group.period,true));
    const allRows=broader.flatMap(d=>d.roster.map(p=>({...p,destination:d}))),found=new Set(),missing=[];
    let elsewhere=0,invalid=0;
    for(const row of source){
      const matches=allRows.filter(p=>raKey(p.ra)===raKey(row.ra));
      const context={period:group.period,campus:group.campus,course:group.course,discipline:group.discipline,ra:row.ra,name:row.name,source:row.source,line:row.line};
      if(!/^\d{5,20}$/.test(raKey(row.ra))||!row.name){invalid++;add('Identificação inválida','RA ou nome ausente/inválido no arquivo.',context);continue;}
      if(!matches.length){missing.push(row);if(!incomplete)add('Aluno ausente','RA não aparece nas turmas compatíveis consultadas.',context);continue;}
      found.add(raKey(row.ra));
      if(matches.every(p=>!relevant.includes(p.destination))){elsewhere++;add('Turma/período divergente','RA localizado em outra turma do mesmo curso e disciplina: '+[...new Set(matches.map(p=>p.destination.turma.text))].join(' / '),context);}
      if(matches.every(p=>norm(p.name)!==norm(row.name)))add('Nome divergente','O RA existe, mas o nome difere: '+[...new Set(matches.map(p=>p.name))].join(' / '),context);
      if(matches.length>1)add('Matrícula repetida','RA aparece em mais de uma linha, página ou destino compatível.',context);
      for(const p of matches)if(p.status&&!/^(ATIVA|ATIVO|MATRICULAD[OA])$/.test(norm(p.status)))add('Matrícula sem situação ativa','Situação no SophiA: '+p.status,context);
    }
    const status=incomplete?'Consulta incompleta — ausência não confirmada':invalid?'Identificação inválida na base enviada':elsewhere?'RAs localizados em turma/período diferente':!relevant.length?'Disciplina/turma não disponível no SophiA':!allRows.length?'Disciplina sem alunos':missing.length?'Alunos ausentes': 'Todos os RAs da base aparecem';
    if(incomplete)add('Consulta incompleta',status,{period:group.period,campus:group.campus,course:group.course,discipline:group.discipline});
    else if((!relevant.length||!allRows.length)&&!elsewhere)add('Turma sem correspondência',status,{period:group.period,campus:group.campus,course:group.course,discipline:group.discipline});
    // Extra portal students are differences, not automatic removals: the files
    // may be a subset. Record the source boundary explicitly.
    const allSource=new Set(records.filter(x=>periodOf(x,report,byRecord)===group.period&&unitKey(x.campus)===unitKey(r.campus)&&norm(x.course)===norm(r.course)&&norm(x.discipline)===norm(r.discipline)).map(x=>raKey(x.ra)));
    for(const p of relevant.flatMap(d=>d.roster))if(!allSource.has(raKey(p.ra)))add('Aluno fora da base enviada','Consta no SophiA e não consta neste curso/disciplina dos arquivos.',{period:group.period,campus:group.campus,course:group.course,discipline:group.discipline,ra:p.ra,name:p.name});
    groups.push({...group,records:undefined,expected:unique.size,found:found.size,missing:incomplete?null:missing.length,status});
  }
  const fields=[];
  for(const d of data){
    for(const exam of ['AD','AI','PS']){
      const c=d.columns.find(c=>c.exam===exam);
      const status=d.failed||!d.rosterKnown||d.assessmentsKnown===false?'Não verificado':!c?'Ausente':c.editable===0?'Presente, sem edição':c.empty===0?'Presente, campos editáveis preenchidos':'Presente, com campos vazios editáveis';
      const unknown=status==='Não verificado';
      const f={period:d.periodo.text,campus:d.unidade.text,course:d.turma.text,discipline:d.disciplina.text,exam,status,editable:unknown?null:c?.editable??0,empty:unknown?null:c?.empty??0,filled:unknown?null:c?.filled??0};fields.push(f);
      if(status==='Ausente'||status==='Presente, sem edição')add('Campo '+exam,status,f);
    }
  }
  const avaDisciplines=[];
  for(const c of courses.filter(c=>c.verified&&c.teacher)){
    const present=data.filter(d=>avaDestination(c,d));
    const hasBase=records.some(r=>recordInAva(r,c,c.period));
    const complete=report.complete&&!(report.portalMap||[]).some(d=>d.failed);
    const status=!c.modality&&!c.campus?'Turma AVA sem modalidade/unidade reconhecida':present.length?'Localizada no SophiA':complete?'Não localizada nas opções disponíveis da conta':'Consulta SophiA incompleta';
    avaDisciplines.push({...c,status,hasBase,destinations:present.length});
    if(!present.length)add('Disciplina AVA sem correspondência',status,{period:c.period,campus:c.campus,discipline:c.name});
    if(records.length&&!hasBase)add('Sem base de alunos','Os arquivos não contêm alunos desta disciplina. A conferência AVA usa os participantes lidos no portal.',{period:c.period,campus:c.campus,discipline:c.name});
  }
  for(const row of report.rows||[]){
    if(/Mais de um registro|duplicad|ambígu|mais de uma turma/i.test(row.status))add('Correspondência ambígua',row.status,{period:report.period.text,campus:row.campus,course:row.course,discipline:row.discipline,exam:row.exam,ra:row.ra,name:row.name,source:row.source,line:row.line});
    if(row.before?.trim()&&row.after&&!equivalent(row.before,row.after))add('Nota divergente','Nota existente preservada. Portal: '+row.before+'; arquivo convertido: '+row.after+'.',{period:report.period.text,campus:row.campus,course:row.course,discipline:row.discipline,exam:row.exam,ra:row.ra,name:row.name,source:row.source,line:row.line});
    if(/Gravação não confirmada|Preenchimento não confirmado/.test(row.status))add('Lançamento não confirmado',row.status,{period:report.period.text,campus:row.campus,course:row.course,discipline:row.discipline,exam:row.exam,ra:row.ra,name:row.name});
  }
  for(const warning of ava.warnings||[])add('Verificação AVA incompleta',warning);
  for(const warning of report.warnings||[])add('Ocorrência do ciclo',warning);
  const comparison=reconcileAva({records,report,destinations:data,courses,fields,recordInAva});
  for(const warning of comparison.warnings)add('Conferência de alunos AVA incompleta',warning);
  const dedup=[...new Map(issues.map(i=>[JSON.stringify(i),i])).values()];
  return {created:new Date().toISOString(),ava,groups,fields,avaDisciplines,issues:dedup,...comparison,complete:!!report.complete&&!!ava.complete&&comparison.complete&&!(report.portalMap||[]).some(d=>d.failed||d.turma&&!d.disciplina)&&!data.some(d=>!d.rosterKnown),
    summary:{groups:groups.filter(g=>g.scope!=='Fora do vínculo docente confirmado').length,missing:groups.reduce((n,g)=>n+(g.missing||0),0),avaMissing:comparison.onlyAva.filter(r=>r.confirmed).length,classes:comparison.classDivergences.length,divergences:dedup.length,saved:(report.rows||[]).filter(r=>r.saved).length}};
}

export function auditCsv(report,records){
  const a=buildAudit(records,report);
  const out=[['SmartDuck','1.9.0'],['Período letivo',report.period.text],['Etapa','Semestre'],['Conta SophiA',report.account?.name||'Não identificada na página'],['Professor AVA',a.ava.account||'Não verificado'],['Conferência completa',a.complete?'Sim':'Não — veja as ocorrências'],['Cobertura','Alunos esperados = arquivos enviados; AVA confirma o vínculo docente. PS, AS e AE são avaliações distintas.'],[],['RESUMO POR DISCIPLINA'],['Período','Unidade','Curso','Período do curso','Disciplina','Código','Vínculo','Alunos nos arquivos','Encontrados','Ausentes','Situação']];
  for(const g of a.groups)out.push([g.period,g.campus,g.course,g.curricularPeriod,g.discipline,g.code,g.scope,g.expected,g.found??'Não verificado',g.missing??'Não verificado',g.status]);
  out.push([],['DIVERGÊNCIAS E PENDÊNCIAS'],['Tipo','Período','Unidade','Curso','Disciplina','Avaliação','RA','Aluno','Detalhe','Arquivo / aba','Linha']);
  for(const i of a.issues)out.push([i.kind,i.period,i.campus,i.course,i.discipline,i.exam,i.ra,i.name,i.detail,i.source,i.line]);
  out.push([],['CAMPOS AD / AI / PS'],['Período','Unidade','Turma','Disciplina','Avaliação','Situação','Editáveis','Vazios editáveis','Preenchidos']);
  for(const f of a.fields)out.push([f.period,f.campus,f.course,f.discipline,f.exam,f.status,f.editable,f.empty,f.filled]);
  out.push([],['VÍNCULOS AVA'],['Período','Código','Disciplina','Função','Vínculo verificado','Correspondência SophiA','Base de alunos enviada']);
  for(const c of a.ava.courses||[]){const d=a.avaDisciplines.find(x=>x.id===c.id);out.push([c.period,c.code,c.name,c.role,c.verified?'Sim':'Não',d?.status||c.error||'Fora do vínculo de professor',d?.hasBase?'Sim':'Não']);}
  out.push([],['LANÇAMENTOS'],['RA','Aluno','Campus','Curso','Disciplina','Avaliação','Destino','Nota anterior','Nota original','Nota proposta','Situação','Arquivo / aba','Linha']);
  for(const r of report.rows||[])out.push([r.ra,r.name,r.campus,r.course,r.discipline,r.exam,r.taskLabel,r.before,r.raw,r.after,r.status,r.source,r.line]);
  out.push([],['MAPEAMENTO COMPLETO DO SOPHIA'],['Período','Unidade','Turma','Etapa','Disciplina','Página','Avaliações','Alunos','Situação']);
  for(const d of report.portalMap||[])out.push([d.periodo.text,d.unidade?.text,d.turma?.text,d.etapa?.text||'Semestre',d.disciplina?.text,d.page,d.assessments?.join(' / '),d.students,d.status]);
  return csvText(out);
}
