import {classify,periodGroups,detectPeriod,FIXED_STAGE} from './automatic.mjs';
import {unitKey,taskKey} from './batch-core.mjs';
import {scanUnit} from './batch-engine.mjs';
import {resolveInventory} from './inventory.mjs';

// Persist only the cursor and the still-needed matches, never a browser handle.
// A unit with an explicit, unique campus can be saved before the next unit is
// searched. Cross-unit matches wait for the entire period to avoid guessing.
export async function beginCycle(client,records,now=new Date()){
  const data=classify(records),first=await client.ensureNotes();
  if(first.account)client.account=first.account;
  const groups=[];
  const requested=data.length?periodGroups(data,first.controls.periodo,now):[{period:detectPeriod([],first.controls.periodo,now),records:[]}];
  for(const group of requested){
    const state=await client.filters({periodo:group.period}),units=state.controls.unidade.options;
    const assigned=new Map(group.records.map(r=>{
      const found=units.filter(u=>r.campus&&unitKey(u.text)===unitKey(r.campus));
      return [r.recordId,found.length===1?found[0].value:null];
    }));
    // A source with an unknown campus may conflict with any source for the same
    // RA. Resolve all such sources together after visiting all units.
    const deferredRA=new Set(group.records.filter(r=>!assigned.get(r.recordId)).map(r=>r.ra));
    groups.push({period:group.period,recordIds:group.records.map(r=>r.recordId),
      units:units.map(unit=>({unit,recordIds:group.records.filter(r=>!deferredRA.has(r.ra)&&assigned.get(r.recordId)===unit.value).map(r=>r.recordId)})),
      deferredIds:group.records.filter(r=>deferredRA.has(r.ra)).map(r=>r.recordId),entries:[],cursor:0});
  }
  const periods=groups.map(g=>g.period);
  return {tasks:[],rows:[],warnings:[],portalMap:[],account:first.account,period:{text:periods.map(p=>p.text).join(' / ')},periods,
    stage:FIXED_STAGE,catalog:[...new Set(data.map(r=>r.exam).filter(Boolean))].map(exam=>({exam,count:data.filter(r=>r.exam===exam).length})),
    complete:false,created:new Date().toISOString(),cycle:{groups,cursor:0,unitsAttempted:0}};
}

export function coverage(report){
  const map=report.portalMap||[],groups=report.cycle?.groups||[];
  return {unitsTotal:groups.reduce((n,g)=>n+g.units.length,0),unitsAttempted:report.cycle?.unitsAttempted||0,
    classes:new Set(map.filter(p=>p.turma).map(p=>JSON.stringify([p.periodo.value,p.unidade.value,p.turma.value]))).size,
    disciplines:new Set(map.filter(p=>p.disciplina).map(p=>JSON.stringify([p.periodo.value,p.unidade.value,p.turma.value,p.disciplina.value]))).size,
    pages:map.filter(p=>p.page).length};
}

function append(report,resolved){
  const existing=new Map(report.tasks.map(t=>[t.id,t]));
  for(const task of resolved.tasks)if(!existing.has(task.id)){report.tasks.push(task);existing.set(task.id,task);}
  for(const row of resolved.rows){row.index=report.rows.length;report.rows.push(row);}
  return resolved.tasks.map(t=>({task:existing.get(t.id),rows:resolved.rows.filter(r=>r.taskId===t.id&&r.ready)})).filter(q=>q.rows.length);
}

export function summarizeDestinations(report){
  const rowsByTask=new Map();
  for(const row of report.rows)if(row.taskId){if(!rowsByTask.has(row.taskId))rowsByTask.set(row.taskId,[]);rowsByTask.get(row.taskId).push(row);}
  for(const d of report.portalMap){
    if(!d.page||!d.disciplina||!d.students)continue;
    const rows=(d.assessments||[]).flatMap(exam=>rowsByTask.get(taskKey({...d,exam}))||[]);
    const saved=rows.filter(r=>r.saved).length,ready=rows.filter(r=>r.ready).length;
    d.saved=saved;d.matched=rows.length;
    if(saved)d.status=saved+' nota(s) gravada(s) e verificada(s)'+(rows.length>saved?'; demais registros no relatório':'');
    else if(ready)d.status=ready+' nota(s) aguardando lançamento';
    else if(rows.length)d.status='Consultado: '+[...new Set(rows.map(r=>r.status))].join('; ');
    else if(report.complete)d.status='Consultado: sem correspondência única para lançar';
  }
}

// Returns jobs for the next unit; an empty list never means the cycle is done.
export async function nextCycle({client,records,report,onProgress=()=>{},cancelled=()=>false}){
  const cycle=report.cycle;
  if(cycle.cursor>=cycle.groups.length){report.complete=true;summarizeDestinations(report);return [];}
  const group=cycle.groups[cycle.cursor],byId=new Map(classify(records).map(r=>[r.recordId,r]));
  const data=group.recordIds.map(id=>byId.get(id));
  if(group.cursor<group.units.length){
    const item=group.units[group.cursor],c=coverage(report);
    const prefix='Unidade '+(c.unitsAttempted+1)+' de '+c.unitsTotal+' · ';
    const result=await scanUnit({client,records:data,period:group.period,unit:item.unit,cancelled,onProgress:text=>onProgress(prefix+text)});
    const early=item.recordIds.map(id=>byId.get(id));
    const resolved=resolveInventory(early,result.entries,result.portalMap);
    const deferredRA=new Set(group.deferredIds.map(id=>byId.get(id).ra));
    for(const entry of result.entries){
      const rows=entry.snapshot.rows.filter(r=>deferredRA.has(r.ra));
      if(rows.length)group.entries.push({...entry,snapshot:{context:entry.snapshot.context,rows}});
    }
    report.portalMap.push(...result.portalMap);
    report.warnings=[...new Set([...report.warnings,...result.warnings])];
    group.cursor++;cycle.unitsAttempted++;
    const jobs=append(report,resolved);summarizeDestinations(report);
    onProgress(prefix+item.unit.text+' consultada. '+(jobs.length?'Lançando as notas correspondentes.':'Sem notas liberadas nesta unidade; seguindo o ciclo.'));
    return jobs;
  }
  // Only after the last unit may missing/mismatched campus labels be resolved
  // by a globally unique RA + name + discipline + assessment.
  const deferred=group.deferredIds.map(id=>byId.get(id));
  const resolved=resolveInventory(deferred,group.entries,report.portalMap.filter(p=>p.periodo.value===group.period.value));
  if(!group.units.length)report.warnings.push(group.period.text+': nenhuma unidade disponível na conta.');
  const jobs=append(report,resolved);group.entries=[];cycle.cursor++;
  if(cycle.cursor===cycle.groups.length)report.complete=true;
  summarizeDestinations(report);
  return jobs;
}
