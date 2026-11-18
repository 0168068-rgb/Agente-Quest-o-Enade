import {norm,raKey} from './core.mjs';
import {unitKey,courseMatches,classPeriod,disciplineName} from './batch-core.mjs';

export function avaDestination(course,d){
  if(d.periodo?.text!==course.period||!d.disciplina)return false;
  if(disciplineName(d.disciplina.text)!==disciplineName(course.discipline))return false;
  if(course.campus&&unitKey(course.campus)!==unitKey(d.unidade?.text))return false;
  const modality=norm(d.turma?.text).match(/^([A-Z])\s*-/)?.[1];
  const entry=norm(d.turma?.text).match(/^[A-Z]\s*-\s*20\d{2}\.[12]\.([1-4])\.\d+P\b/)?.[1];
  if(entry&&course.offerings?.length&&!course.offerings.includes(entry))return false;
  return !course.modality||!modality||course.modality===modality;
}

// The AVA roster is the source of this comparison. Uploaded files may resolve
// a unique RA/course for a visible name, but never manufacture an AVA student.
export function reconcileAva({records,report,destinations,courses,fields,recordInAva}){
  const students=[],classes=[],warnings=[];
  for(const c of courses.filter(c=>c.verified&&c.teacher)){
    const related=destinations.filter(d=>avaDestination(c,d));
    const portalRows=related.flatMap(d=>d.roster.map(p=>({...p,destination:d})));
    const candidates=records.filter(r=>recordInAva(r,c,c.period));
    const failed=(report.portalMap||[]).some(d=>d.periodo?.text===c.period&&(!c.campus||!d.unidade||unitKey(d.unidade.text)===unitKey(c.campus))&&(d.failed||d.turma&&!d.disciplina));
    const scopeKnown=!!(c.modality||c.campus);
    const coverage=!!report.complete&&!failed&&scopeKnown&&related.every(d=>d.rosterKnown&&!d.failed);
    const problems=[];let found=0,missing=0,unresolved=0;
    if(!related.length)problems.push(coverage?'Disciplina/turma AVA não localizada no SophiA':'Correspondência SophiA não concluída');
    if(related.some(d=>!d.roster.length&&!d.failed))problems.push('Há turma SophiA sem lista de alunos');
    if(!c.rosterComplete){problems.push('Lista de alunos do AVA incompleta');warnings.push(c.name+': lista de alunos do AVA não totalmente verificada.');}
    if(!coverage)problems.push('Consulta SophiA incompleta');
    if(!scopeKnown)problems.push('Modalidade/unidade da turma AVA não identificada; correspondência precisa de conferência');
    for(const p of c.students||[]){
      const source=candidates.filter(r=>p.ra?raKey(r.ra)===raKey(p.ra):norm(r.name)===norm(p.name));
      const sourceRA=[...new Set(source.map(r=>raKey(r.ra)).filter(r=>/^\d{5,20}$/.test(r)))];
      const ra=p.ra?raKey(p.ra):sourceRA.length===1?sourceRA[0]:'';
      const method=p.ra?'RA exibido no AVA':ra?'RA do arquivo por nome completo único':'Nome completo; RA não exibido no AVA';
      const matches=portalRows.filter(r=>ra?raKey(r.ra)===ra:norm(r.name)===norm(p.name));
      const identities=new Set(matches.map(r=>raKey(r.ra)));
      const expected=related.filter(d=>source.some(r=>(!r.campus||unitKey(r.campus)===unitKey(d.unidade.text))&&(!r.course||courseMatches(r.course,d.turma.text))&&(!r.period||classPeriod(d.turma.text)===String(r.period))));
      const expectedLabel=expected.map(d=>d.turma.text).join(' / ')||[...new Set(source.map(r=>[r.course,r.period?r.period+'º período':''].filter(Boolean).join(' · ')))].join(' / ')||(related.length?'Turmas compatíveis consultadas: '+related.map(d=>d.turma.text).join(' / '):'Turma SophiA não identificada');
      let status='',notFound=false,confirmed=false,alternativeClasses='';
      if(identities.size===1){
        found++;status='Encontrado no SophiA';
        if(matches.every(r=>norm(r.name)!==norm(p.name)))status='Nome divergente para o mesmo RA';
        else if(matches.length>1)status='RA localizado em mais de uma matrícula/turma';
        else if(expected.length&&!matches.some(r=>expected.includes(r.destination)))status='Aluno localizado em outra turma/período';
        if(status!=='Encontrado no SophiA')problems.push(status);
      }else if(matches.length){status='Nome com mais de um RA no SophiA';unresolved++;problems.push(status);}
      else{
        notFound=true;confirmed=coverage&&!!ra;
        const sameName=ra?portalRows.filter(r=>norm(r.name)===norm(p.name)):[];
        const otherEntries=destinations.filter(d=>!related.includes(d)&&avaDestination({...c,offerings:[]},d)&&d.roster.some(r=>ra?raKey(r.ra)===ra:norm(r.name)===norm(p.name)));
        if(otherEntries.length){status='Aluno localizado em outra entrada/turma do SophiA';confirmed=false;alternativeClasses=otherEntries.map(d=>d.turma.text).join(' / ');}
        else if(sameName.length){status='Nome encontrado com RA diferente; conferir matrícula';confirmed=false;}
        else if(!coverage)status='Sem correspondência nas consultas concluídas; SophiA incompleto';
        else if(ra)status='RA não localizado no SophiA para esta disciplina';
        else status='Nome não localizado; RA indisponível para confirmação';
        if(confirmed)missing++;else unresolved++;problems.push(status);
      }
      students.push({period:c.period,campus:c.campus||[...new Set(source.map(r=>r.campus).filter(Boolean))].join(' / '),avaClass:c.code,discipline:c.discipline,avaName:c.name,avaUrl:c.url||'',ra,name:p.name,method,status,notFound,confirmed,
        sophiaClass:matches.length?[...new Set(matches.map(r=>r.destination.turma.text))].join(' / '):alternativeClasses||expectedLabel,
        source:[...new Set(source.map(r=>r.source))].join(' / ')});
    }
    const fieldProblems=fields.filter(f=>related.some(d=>f.period===d.periodo.text&&f.campus===d.unidade.text&&f.course===d.turma.text&&f.discipline===d.disciplina.text)&&['Ausente','Presente, sem edição','Não verificado'].includes(f.status));
    for(const f of fieldProblems)problems.push(f.course+': '+f.exam+' — '+f.status);
    if(problems.length)classes.push({period:c.period,campus:c.campus||[...new Set(related.map(d=>d.unidade.text))].join(' / '),avaClass:c.code,discipline:c.discipline,sophiaClasses:related.map(d=>d.turma.text).join(' / ')||'Não localizada',
      studentsAva:(c.students||[]).length,rosterComplete:!!c.rosterComplete,found,missing,unresolved,detail:[...new Set(problems)].join('; ')});
  }
  if(!report.ava?.complete)warnings.push('A lista completa de vínculos docentes no AVA não foi confirmada.');
  return {students,onlyAva:students.filter(s=>s.notFound),classDivergences:classes,warnings,complete:!!report.ava?.complete&&courses.filter(c=>c.verified&&c.teacher).every(c=>c.rosterComplete&&(c.modality||c.campus))&&!!report.complete&&!destinations.some(d=>d.failed||!d.rosterKnown)};
}
