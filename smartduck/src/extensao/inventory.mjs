import {norm,buildPlan} from './core.mjs';
import {unitKey,courseMatches,classPeriod,disciplineMatches,contextMatches,taskKey,taskLabel} from './batch-core.mjs';

const pending=(r,status)=>({...r,raw:r.grade,before:'',after:'',ready:false,status});
// Match the scope even when a failed option supplied no student rows. Such an
// unread option must not make another possible destination appear unique.
function scopeAllows(r,task,available){
  if(task.disciplina&&!disciplineMatches(r,task.disciplina))return false;
  const units=available.filter(m=>r.campus&&unitKey(m.unidade?.text)===unitKey(r.campus));
  if(units.length&&!units.some(m=>m.unidade.value===task.unidade.value))return false;
  if(task.turma){
    const classes=(units.length?units:available).filter(m=>r.course&&m.turma&&courseMatches(r.course,m.turma.text));
    if(classes.length&&!classes.some(m=>m.unidade.value===task.unidade.value&&m.turma.value===task.turma.value))return false;
    const curricular=classPeriod(task.turma.text);
    if(curricular&&r.period&&Number(curricular)!==Number(r.period))return false;
    if(/^S\s*-/.test(norm(task.turma.text))&&/(?:^|[^A-Z])EAD(?:[^A-Z]|$)/.test(norm(r.source+' '+r.course)))return false;
    if(/^SEMIPRESENCIAL\b/.test(norm(r.course))&&/^[A-Z]\s*-/.test(norm(task.turma.text))&&!/^S\s*-/.test(norm(task.turma.text)))return false;
  }
  return true;
}
// All portal destinations are visited. Labels constrain a match when the portal
// exposes them; differing local labels may fall back to a unique RA/name/subject.
export function resolveInventory(records,entries,portalMap){
  const byId=new Map(records.map(r=>[r.recordId,r])),byRA=new Map();
  for(const r of records){const key=r.exam+'|'+r.ra;if(!byRA.has(key))byRA.set(key,[]);byRA.get(key).push(r);}
  const candidates=new Map(),divergent=new Set();
  for(const {task,snapshot} of entries){
    if(!contextMatches(snapshot,task))throw new Error('O destino mudou durante o mapeamento.');
    const available=portalMap.filter(m=>m.periodo.value===task.periodo.value);
    for(const p of snapshot.rows){
      for(const r of [...(byRA.get(task.exam+'|'+p.ra)||[]),...(byRA.get('|'+p.ra)||[])]){
        if(!scopeAllows(r,task,available))continue;
        if(norm(p.name)!==norm(r.name)){divergent.add(r.recordId);continue;}
        if(!candidates.has(r.recordId))candidates.set(r.recordId,[]);
        candidates.get(r.recordId).push({task,snapshot,row:p});
      }
    }
  }
  const rows=[],selected=new Map(),destinations=new Map();
  for(const r of records){
    const unread=portalMap.find(m=>m.failed&&(!m.exam||!r.exam||m.exam===r.exam)&&scopeAllows(r,m,portalMap));
    if(unread){rows.push(pending(r,'Não inserido: consulta incompleta deste destino — '+unread.status));continue;}
    const found=candidates.get(r.recordId)||[];
    if(found.length!==1){rows.push(pending(r,found.length?(!r.exam?'Avaliação ou destino ambíguo: informe a avaliação no arquivo':'Correspondência em mais de uma turma/página: revisar'):divergent.has(r.recordId)?'RA confere, mas nome diverge; revisar':'Não localizado com correspondência única no período e etapa consultados'));continue;}
    const c=found[0],key=taskKey(c.task)+'|'+c.row.key;
    if(!destinations.has(key))destinations.set(key,[]);
    destinations.get(key).push(r.recordId);selected.set(r.recordId,c);
  }
  // Never let two files assign different records to the same grade field.
  for(const ids of destinations.values())if(ids.length>1)for(const id of ids){rows.push(pending(byId.get(id),'Mais de um registro dos arquivos corresponde ao mesmo campo: revisar'));selected.delete(id);}
  const grouped=new Map();
  for(const [id,c] of selected){const key=taskKey(c.task);if(!grouped.has(key))grouped.set(key,{...c,records:[]});grouped.get(key).records.push(byId.get(id));}
  const tasks=[];
  for(const [id,g] of grouped){
    const task={...g.task,id,label:taskLabel(g.task),recordIds:g.records.map(r=>r.recordId)};
    tasks.push(task);
    rows.push(...buildPlan(g.records,g.snapshot,{sourceMax:10,max:task.max,overwrite:false,absent:'blank'})
      .filter(r=>r.target&&r.source).map(r=>({...r,exam:task.exam,taskId:id,taskLabel:task.label})));
  }
  return {tasks,rows};
}
