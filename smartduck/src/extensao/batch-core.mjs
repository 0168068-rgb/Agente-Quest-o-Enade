import {norm,buildPlan,equivalent} from './core.mjs';

export const unitKey=v=>norm(v).replace(/[–—]/g,'-').replace(/^(CAMPUS|POLO|UNIDADE)\s+/,'').replace(/\s*[-/]\s*[A-Z]{2}$/,'');
export const disciplineName=v=>norm(v).replace(/^\d+\s*[-–:|]\s*/,'').replace(/\s*\(\d+\)\s*$/,'');
export const courseKey=v=>norm(v).replace(/^(SEMIPRESENCIAL|EAD|PRESENCIAL)\s*[-–—:]?\s*/,'').replace(/^SUPERIOR\s+DE\s+TECNOLOGIA\s+EM\s+/,'').replace(/\bTEC\./g,'TECNOLOGIA').replace(/\bDES\./g,'DESENVOLVIMENTO').replace(/[^A-Z0-9 ]/g,' ').split(/\s+/).filter(t=>t&&!['DE','DA','DO','DAS','DOS','E','EM'].includes(t)).join(' ');
export function courseMatches(course,classroom){
  // SophiA identifies semipresential classes with S; preserve this distinction.
  if(/^SEMIPRESENCIAL\b/.test(norm(course))&&/^[A-Z]\s*-/.test(norm(classroom))&&!/^S\s*-/.test(norm(classroom)))return false;
  const wanted=courseKey(course),label=' '+courseKey(classroom)+' ';
  if(!wanted)return false;
  const index=label.indexOf(' '+wanted+' ');if(index<0)return false;
  const suffix=label.slice(index+wanted.length+2).trim();
  return !suffix||/^(?:\d|[A-Z]{1,3}\d|PERIODO\b|PER\b|TURMA\b|SEM\b|SEMESTRE\b|SEMIPRESENCIAL\b|SEMI\b|EAD\b|PRESENCIAL\b|NOTURNO\b|MATUTINO\b|VESPERTINO\b|INTEGRAL\b|BACHARELADO\b|LICENCIATURA\b|TECNOLOGO\b|[A-Z]\b)/.test(suffix);
}
export function disciplineMatches(record,option){
  if(disciplineName(record.discipline)!==disciplineName(option.text))return false;
  const code=norm(option.text).match(/^(\d+)\s*[-–:|]/)?.[1]||norm(option.text).match(/\((\d+)\)\s*$/)?.[1];
  return !code||!record.code||code.replace(/^0+/,'')===String(record.code).replace(/^0+/,'');
}
export function classPeriod(text){return norm(text).match(/\b(\d{1,2})\s*[º°O]?\s*(?:PERIODO|PER\b)/)?.[1]||norm(text).match(/(?:\.|\s)(\d{1,2})P\b/)?.[1]||'';}
export function relevantRecords(records,{unit,classroom,discipline}){
  const period=classPeriod(classroom?.text||'');
  return records.filter(r=>(!unit||unitKey(r.campus)===unitKey(unit.text))&&(!classroom||courseMatches(r.course,classroom.text))&&(!classroom||!/^S\s*-/.test(norm(classroom.text))||!/(?:^|[^A-Z])EAD(?:[^A-Z]|$)/.test(norm(r.source)))&&(!period||!r.period||Number(r.period)===Number(period))&&(!discipline||disciplineMatches(r,discipline)));
}
export function contextMatches(snapshot,task){
  return ['periodo','unidade','turma','etapa','disciplina'].every(k=>{
    const found=snapshot.context.filter(c=>(c.id||'').toLowerCase().includes(k));
    return found.length===1&&found[0].value===task[k].value&&norm(found[0].text)===norm(task[k].text);
  });
}
export const taskKey=t=>JSON.stringify(['periodo','unidade','turma','etapa','disciplina'].map(k=>t[k].value).concat(t.page||1,t.exam||''));
export const taskLabel=t=>[t.unidade.text,t.turma.text,t.etapa.text,t.disciplina.text,t.exam,'página '+(t.page||1)].filter(Boolean).join(' · ');
export function planTask(records,snapshot,task,options){
  if(!contextMatches(snapshot,task))throw new Error('Os filtros da turma não correspondem ao lote consultado.');
  const candidates=relevantRecords(records,{unit:task.unidade,classroom:task.turma,discipline:task.disciplina});
  const rows=buildPlan(candidates,snapshot,options).filter(r=>r.target&&r.source);
  const id=taskKey(task);
  return {task:{...task,id,label:taskLabel(task),recordIds:candidates.map(r=>r.recordId)},rows:rows.map(r=>({...r,exam:task.exam||'',taskId:id,taskLabel:taskLabel(task)}))};
}
export function finishInventory(records,tasks,rows){
  const found=new Map();
  for(const row of rows){if(!row.recordId)continue;if(!found.has(row.recordId))found.set(row.recordId,[]);found.get(row.recordId).push(row);}
  for(const matches of found.values())if(matches.length>1)for(const row of matches){row.ready=false;row.status='Correspondência em mais de uma turma/página: revisar';}
  for(const r of records)if(!found.has(r.recordId))rows.push({recordId:r.recordId,ra:r.ra,name:r.name,sourceName:r.name,raw:r.grade,before:'',after:'',source:r.source,line:r.line,campus:r.campus,course:r.course,discipline:r.discipline,period:r.period,ready:false,status:'Não localizado com correspondência única no período e etapa consultados'});
  return {tasks,rows};
}
export function reviewedChanges(reviewed,fresh,task){
  if(!contextMatches(fresh,task))throw new Error('A turma mudou após a conferência.');
  const changes=[],same=[],skipped=[];
  const skip=(row,status)=>skipped.push({row,status});
  for(const row of reviewed){
    const matches=fresh.rows.filter(p=>p.ra===row.ra&&norm(p.name)===norm(row.name));
    if(matches.length!==1){skip(row,'Não inserido: aluno sem correspondência única na releitura');continue;}
    const p=matches[0];
    if(equivalent(p.value,row.after)){same.push(row);continue;}
    if(!p.editable){skip(row,'Não inserido: campo bloqueado ou ausente na releitura');continue;}
    if(p.value!==row.before||p.value.trim()){skip(row,'Não inserido: nota existente ou alterada após o mapeamento');continue;}
    const value=p.type==='number'?row.after.replace(',','.'):row.after;
    if(p.maxLength>=0&&value.length>p.maxLength){skip(row,'Não inserido: valor excede o tamanho permitido pelo campo');continue;}
    if(p.type==='number'){
      const n=Number(value),min=p.min??'',max=p.max??'',step=p.step??'';
      if((min!==''&&n<Number(min))||(max!==''&&n>Number(max))){skip(row,'Não inserido: nota fora do limite do campo');continue;}
      if(step&&step!=='any'&&Math.abs((n-Number(min||0))/Number(step)-Math.round((n-Number(min||0))/Number(step)))>1e-8){skip(row,'Não inserido: precisão da nota não aceita pelo campo');continue;}
    }
    changes.push({key:p.key,ra:p.ra,name:p.name,before:p.value,after:row.after,blank:row.blank===true,recordId:row.recordId});
  }
  return {changes,same,skipped};
}
export function verifySaved(snapshot,task,rows){
  if(!contextMatches(snapshot,task))return false;
  return rows.every(r=>{const found=snapshot.rows.filter(p=>p.ra===r.ra&&norm(p.name)===norm(r.name));return found.length===1&&equivalent(found[0].value,r.after);});
}
