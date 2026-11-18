import {norm} from './core.mjs';
import {collectAva} from './ava.mjs';
import {buildAudit} from './audit.mjs';
import {reportSheets} from './report-sheets.mjs';
import {exportXlsx} from './report-xlsx.mjs';
import {addFiles} from './uploads.mjs';
import {PortalClient,fillTask} from './batch-engine.mjs';
import {classify,periodGroups} from './automatic.mjs';
import {saveSession,loadSession,clearSession} from './session-store.mjs';
import {outcome} from './outcome.mjs';
import {attemptRead,requiresUser} from './resilience.mjs';
import {beginCycle,nextCycle,coverage,summarizeDestinations} from './cycle.mjs';
const $=id=>document.getElementById(id),params=new URLSearchParams(location.search);
const state={files:[],records:[],report:null,client:null,tabId:null,busy:false,stop:false,phase:'idle',pending:null,queue:[],cursor:0,auditTab:'classes'};
const message=(text,type='')=>{$('message').textContent=text;$('message').className=type;};
const progress=text=>{$('progress').textContent=text;};
function controls(){
  const locked=state.busy||['paused','waiting','error','applying'].includes(state.phase);
  $('settings').disabled=locked;$('direct').disabled=locked||!state.records.length||!state.client;
  $('auditOnly').disabled=locked||!state.client;
  $('export').disabled=!state.report;
  $('stop').disabled=!state.busy;$('resume').hidden=!['waiting','paused'].includes(state.phase);$('resume').disabled=state.busy;
  $('resume').textContent=state.pending?'Verificar gravação e continuar':'Continuar o restante';
  $('end').hidden=!['error','waiting','paused'].includes(state.phase);$('end').disabled=state.busy;
  $('tracking').hidden=!state.report&&state.phase==='idle';$('fileDetails').hidden=!state.files.length;
  $('clear').hidden=!state.files.length;
  $('phaseLabel').textContent=({idle:'Pronto para começar',inventory:'Preparando o ciclo completo',scanning:'Consultando todas as opções',running:'Lançando as notas',auditing:'Conferindo AVA e SophiA',applying:'Preenchendo a turma',waiting:state.busy?'Salvando e verificando':'Gravação pendente de verificação',paused:'Lote pausado',error:'Ação necessária no SophiA',recovering:'Recuperando e continuando',done:'Lote concluído',blocked:'O SophiA não recebeu notas'})[state.phase]||'Acompanhamento';
  if(['inventory','scanning','auditing'].includes(state.phase))$('batchProgress').removeAttribute('value');
  else{$('batchProgress').max=Math.max(1,state.queue.length);$('batchProgress').value=state.phase==='done'?Math.max(1,state.queue.length):state.cursor;}
}
function checkpoint(){
  if(!state.tabId)return Promise.resolve();
  const pending=state.pending?{...state.pending,rows:state.pending.rows.map(r=>r.index)}:null;
  return saveSession(state.tabId,{version:6,files:state.files,records:state.records,report:state.report,phase:state.phase,pending,cursor:state.cursor,queue:state.queue.map(q=>({taskId:q.task.id,rows:q.rows.map(r=>r.index)}))});
}
async function operation(fn){if(state.busy)return;state.busy=true;controls();try{await fn();await checkpoint();}catch(e){message(e.message||String(e),'error');}finally{state.busy=false;controls();}}
function invalidate(){state.report=null;state.phase='idle';state.pending=null;state.queue=[];state.cursor=0;$('warnings').hidden=true;$('auditResult').hidden=true;$('destination').textContent='O mapeamento será feito na conta conectada.';progress('');render();}
function fileList(){
  $('fileCount').textContent=state.files.length+' / 4 arquivos carregados';
  $('fileList').replaceChildren(...state.files.map(f=>{const line=document.createElement('div');line.className='file-row';line.append(Object.assign(document.createElement('span'),{textContent:f.name+' · '+f.count.toLocaleString('pt-BR')+' registros'}));const b=Object.assign(document.createElement('button'),{className:'secondary remove-file',textContent:'Remover arquivo',type:'button'});b.setAttribute('aria-label','Remover arquivo '+f.name);b.onclick=()=>operation(async()=>{state.files=state.files.filter(x=>x.hash!==f.hash);state.records=state.records.filter(r=>r.fileId!==f.hash);invalidate();fileList();message(f.name+' removido do lote. '+(state.files.length?'Os demais arquivos continuam carregados.':'Selecione novos arquivos para realizar.'));});line.append(b);return line;}));
  $('selectionSummary').textContent=state.records.length.toLocaleString('pt-BR')+' registros no lote. Todos os arquivos serão processados.';
  const exams=[...new Set(classify(state.records).map(r=>r.exam).filter(Boolean))];
  $('mapping').textContent=state.records.length?'Avaliações: '+(exams.join(', ')||'detectar no SophiA')+' · Etapa: Semestre · Todas as unidades, turmas e disciplinas.':'Aguardando arquivos.';controls();
}
async function portalStatus(){
  try{const s=await state.client.ready(),groups=periodGroups(state.records,s.controls.periodo);$('portalContext').textContent=groups.length?'Período letivo: '+groups.map(g=>g.period.text).join(' / ')+'. O lote usa a mesma aba.':'SophiA conectado. O período letivo será detectado ao realizar.';}
  catch{$('portalContext').textContent='Ao realizar, o programa acessará Notas pela conta conectada nesta aba.';}
}
async function importFiles(files){const r=await addFiles(files,state,message);state.files=r.files;state.records=r.records;$('files').value='';invalidate();fileList();message(r.notices.join('\n')+'\nClique em Realizar para lançar o lote.');}
$('files').onchange=()=>operation(()=>importFiles($('files').files));
const dropbox=document.querySelector('.filebox');dropbox.ondragover=e=>e.preventDefault();dropbox.ondrop=e=>{e.preventDefault();if(!$('settings').disabled)void operation(()=>importFiles(e.dataTransfer.files));};
$('clear').onclick=()=>operation(async()=>{state.files=[];state.records=[];invalidate();fileList();await clearSession(state.tabId);message('Arquivos e relatório removidos deste lote.');});
function showReport(){const r=state.report;if(!r)return;const c=coverage(r);$('destination').textContent=r.period.text+' · Semestre · '+(r.cycle?c.unitsAttempted+' / '+c.unitsTotal+' unidades consultadas · '+c.disciplines+' disciplinas tentadas':(r.portalMap?.length||0)+' destinos consultados');$('warnings').hidden=!r.warnings.length;$('warningList').replaceChildren(...r.warnings.map(w=>Object.assign(document.createElement('li'),{textContent:w})));}
async function perform(mode='write'){
  if(!state.records.length&&mode!=='audit')throw new Error('Selecione de 1 a 4 arquivos.');
  invalidate();state.phase='inventory';state.stop=false;controls();message('Realizando o ciclo: todas as unidades, turmas e disciplinas serão consultadas.');await checkpoint();
  state.client.account=null;
  try{
    const warnings=[];
    const prepared=await attemptRead({client:state.client,read:()=>beginCycle(state.client,state.records),cancelled:()=>state.stop,onError:(e,n)=>{warnings.push('Preparação '+n+': '+e.message);progress('Tentando acessar as opções do SophiA novamente…');}});
    if(!prepared.ok)throw prepared.error;
    state.report=prepared.value;state.report.mode=mode;state.report.warnings.push(...warnings);showReport();
    state.phase='running';render();await checkpoint();await processQueue();
  }catch(e){if(state.phase==='inventory'){state.phase='idle';progress('Mapeamento interrompido. Nenhuma nota foi preenchida.');}throw e;}
}
$('direct').onclick=()=>operation(()=>perform('write'));
$('auditOnly').onclick=()=>operation(()=>perform('audit'));
const settled=r=>/^(Gravado|Já possui|Faltoso:|Nota existente)/.test(r.status);
function render(){
  const rows=state.report?.rows||[];
  $('countMapped').textContent=state.report?.portalMap?.length||0;$('countTasks').textContent=state.report?.tasks.length||0;$('countBlank').textContent=rows.filter(r=>r.blank&&!r.before.trim()).length;$('countSaved').textContent=rows.filter(r=>r.saved).length;
  const query=norm($('search').value),mode=$('viewFilter').value;
  const shown=rows.filter(r=>(!query||norm([r.name,r.ra,r.discipline,r.course].join(' ')).includes(query))&&(mode==='all'||mode==='ready'&&r.ready||mode==='saved'&&r.saved||mode==='pending'&&!r.ready&&!settled(r)));
  const fragment=document.createDocumentFragment();
  for(const row of shown.slice(0,500)){
    const tr=document.createElement('tr');if(row.ready)tr.className='ready';
    const student=document.createElement('td');student.append(Object.assign(document.createElement('span'),{className:'name',textContent:row.name}),Object.assign(document.createElement('span'),{className:'ra',textContent:row.ra+' · '+row.discipline}));tr.append(student);
    for(const value of [row.before||'—',row.raw||'—',row.blank?'Em branco':row.after||'—'])tr.append(Object.assign(document.createElement('td'),{textContent:value}));
    const status=document.createElement('td');status.append(Object.assign(document.createElement('span'),{className:'status',textContent:row.status}),Object.assign(document.createElement('div'),{className:'source-line',textContent:row.taskLabel||[row.campus,row.course,row.discipline].join(' · ')}),Object.assign(document.createElement('div'),{className:'source-line',textContent:row.source+' · linha '+row.line}));tr.append(status);fragment.append(tr);
  }
  if(!shown.length){const tr=document.createElement('tr');tr.append(Object.assign(document.createElement('td'),{colSpan:5,className:'empty',textContent:rows.length?'Nenhuma linha neste filtro.':'O resultado aparecerá durante o lote.'}));fragment.append(tr);}
  $('rows').replaceChildren(fragment);$('tableCount').textContent=shown.length>500?'Exibindo 500 de '+shown.length+' linhas. O relatório contém todas.':shown.length+' linhas exibidas.';controls();
}
$('search').oninput=render;$('viewFilter').onchange=render;
$('stop').onclick=()=>{state.stop=true;progress(['inventory','scanning'].includes(state.phase)?'Pausando a consulta; o restante poderá ser continuado…':'Parando após conferir a gravação da turma atual.');};
$('end').onclick=()=>operation(async()=>{invalidate();message('Lote encerrado. Os arquivos continuam carregados; os valores no SophiA foram mantidos.');});
function recordError(text){
  state.report.warnings=[...new Set([...state.report.warnings,text])];showReport();
}
function deferVerification(task,rows){
  if(!rows.length)return;
  state.report.verifications??=[];
  state.report.verifications.push({taskId:task.id,rows:rows.map(r=>r.index)});
}
async function confirmRows(task,rows){
  progress('Verificando gravação: '+task.label);
  const read=await attemptRead({client:state.client,read:()=>state.client.confirm(task,task.exam,rows),onError:(e,n)=>recordError(task.label+' · verificação '+n+': '+e.message)});
  const confirmed=new Set(read.ok?read.value.filter(x=>x.confirmed).map(x=>x.row.index):[]);
  for(const row of rows){
    row.ready=false;
    if(confirmed.has(row.index)){row.saved=true;row.status='Gravado: nota confirmada por releitura';}
    else row.status='Gravação não confirmada: '+(row.failureReason?row.failureReason+' — ':'')+(read.ok?'valor não encontrado na releitura':read.error.message);
  }
  return rows.filter(r=>!r.saved);
}
async function verifyPending(){
  const p=state.pending;if(!p)return;
  const missing=await confirmRows(p.task,p.rows);
  if(missing.length){recordError(p.task.label+': '+missing.length+' nota(s) sem confirmação. O ciclo segue; será feita outra releitura ao final.');deferVerification(p.task,missing);}
  state.pending=null;state.cursor++;state.phase='running';summarizeDestinations(state.report);showReport();await checkpoint();render();
}
async function skipFailedFill(item,error){
  recordError(item.task.label+' · preenchimento: '+error.message);
  state.phase='recovering';controls();
  const recovery=await attemptRead({client:state.client,read:()=>state.client.recover(),onError:e=>recordError(item.task.label+' · recuperação: '+e.message)});
  for(const row of item.rows){row.ready=false;if(!row.saved){row.failureReason='Preenchimento: '+error.message;row.status='Preenchimento não confirmado: '+error.message;}}
  deferVerification(item.task,item.rows.filter(r=>!r.saved));
  if(!recovery.ok)recordError(item.task.label+': recuperação pendente; seguindo para a próxima opção.');
  state.pending=null;state.cursor++;state.phase='running';await checkpoint();render();
}
async function finalVerification(){
  const r=state.report;r.verificationCursor??=0;
  while(r.verificationCursor<(r.verifications?.length||0)){
    if(state.stop)return false;
    const p=r.verifications[r.verificationCursor],task=r.tasks.find(t=>t.id===p.taskId),rows=p.rows.map(i=>r.rows[i]).filter(x=>!x.saved);
    if(rows.length){
      const missing=await confirmRows(task,rows);
      if(missing.length)recordError(task.label+': '+missing.length+' nota(s) pendente(s) após a verificação final; sem repetir Salvar.');
    }
    r.verificationCursor++;await checkpoint();render();
  }
  return true;
}
async function processQueue(){
  state.phase='running';
  try{
    if(state.pending)await verifyPending();
    while(true){
      if(state.stop){state.phase='paused';message('Lote pausado pelo usuário. Clique em Continuar o restante quando desejar.');render();return;}
      if(state.cursor>=state.queue.length){
        if(state.report.complete)break;
        state.phase='scanning';controls();await checkpoint();
        const jobs=await nextCycle({client:state.client,records:state.records,report:state.report,onProgress:progress,cancelled:()=>state.stop});
        state.queue.push(...jobs);state.phase='running';showReport();render();await checkpoint();
        continue;
      }
      const item=state.queue[state.cursor];progress('Turma/página '+(state.cursor+1)+' de '+state.queue.length+': '+item.task.label);
      if(state.report.mode==='audit'){
        for(const row of item.rows){row.ready=false;row.status='Conferido: campo disponível; lançamento não solicitado';}
        state.cursor++;await checkpoint();render();continue;
      }
      let filled;state.phase='applying';controls();await checkpoint();
      try{filled=await fillTask(state.client,item.task,item.rows,{exam:item.task.exam,max:item.task.max});}
      catch(e){if(requiresUser(e))throw e;await skipFailedFill(item,e);continue;}
      if(!filled.changes.length){state.cursor++;state.phase='running';await checkpoint();render();continue;}
      state.pending={task:item.task,...filled};state.phase='waiting';await checkpoint();render();
      progress('Salvando no SophiA: '+item.task.label+'…');
      try{await state.client.save(item.task.exam,filled.changes,filled.token);}
      catch(e){if(requiresUser(e))throw e;for(const row of filled.rows)row.failureReason='Salvar: '+e.message;recordError(item.task.label+' · Salvar: '+e.message);await state.client.pause(250);}
      // Save is issued once. Even after an error, read server values and carry on.
      await verifyPending();
    }
    state.phase='running';
    if(!await finalVerification()){state.phase='paused';message('Lote pausado pelo usuário antes da verificação final.');render();return;}
    if(!state.report.ava){
      state.phase='auditing';controls();await checkpoint();progress('Lendo vínculos e alunos do AVA para concluir o relatório…');
      try{state.report.ava=await collectAva(state.report.periods.map(p=>p.text),{onProgress:progress,cancelled:()=>state.stop});}
      catch(e){if(e.code==='CANCELLED')throw e;state.report.ava={status:'unavailable',complete:false,courses:[],warnings:[e.message]};}
      await checkpoint();
    }
    summarizeDestinations(state.report);showReport();state.report.audit=buildAudit(state.records,state.report);showAudit();
    const result=state.report.mode==='audit'?{phase:'done',type:state.report.audit.issues.length?'warning':'success',message:'Conferência concluída. '+state.report.audit.summary.divergences+' ocorrência(s) no relatório. Nenhuma nota alterada.'}:outcome(state.report);state.phase=result.phase;
    const c=coverage(state.report);progress((state.report.cycle?c.unitsAttempted+' / '+c.unitsTotal+' unidades · '+c.disciplines+' disciplinas · '+c.pages+' páginas tentadas. ':'')+state.report.rows.filter(r=>r.saved).length+' notas gravadas e verificadas.');
    message(result.message+' Relatório Excel com abas de divergências pronto.',result.type);$('reportDetails').open=true;render();
    if(!state.report.downloadAttempted){state.report.downloadAttempted=downloadReport();}
  }catch(e){
    // A still-active Save must not be cancelled by reloading. An explicit Stop,
    // lost login/tab and manual edits also pause; local failures stay per item.
    state.phase='paused';
    if(e.code!=='CANCELLED')recordError('Acesso pendente: '+e.message);
    message(e.code==='CANCELLED'?'Lote pausado pelo usuário.':e.message+' As demais opções continuam pendentes no ciclo.','warning');render();
  }
}
$('resume').onclick=()=>operation(async()=>{if(!['waiting','paused'].includes(state.phase))return;state.stop=false;await processQueue();});
function showAudit(){
  const a=state.report?.audit;if(!a)return;$('auditResult').hidden=false;
  $('auditSummary').textContent=(a.complete?'Conferência completa':'Conferência com limitações')+' · '+(a.ava.account||'Professor AVA não verificado')+' · '+a.summary.classes+' turma(s) AVA com divergências · '+a.summary.avaMissing+' vínculo(s) aluno/disciplina do AVA sem RA correspondente no SophiA.';
  for(const [key,id] of [['classes','auditClasses'],['students','auditStudents'],['other','auditOther']])$(id).setAttribute('aria-selected',String(state.auditTab===key));
  $('auditPanel').setAttribute('aria-labelledby',({classes:'auditClasses',students:'auditStudents',other:'auditOther'})[state.auditTab]);
  const items=state.auditTab==='classes'?(a.classDivergences||[]).map(c=>[c.discipline,'AVA: '+c.avaClass,'SophiA: '+c.sophiaClasses,c.detail].join(' · ')):state.auditTab==='students'?(a.onlyAva||[]).map(s=>[s.name,s.ra?'RA '+s.ra:'RA não exibido',s.discipline,'AVA: '+s.avaClass,'SophiA: '+s.sophiaClass,s.status,s.method].join(' · ')):a.issues.map(i=>[i.kind,i.discipline,i.campus,i.name,i.ra,i.detail].filter(Boolean).join(' · '));
  const fragment=document.createDocumentFragment();
  for(const value of items.slice(0,300))fragment.append(Object.assign(document.createElement('li'),{textContent:value}));
  if(!items.length)fragment.append(Object.assign(document.createElement('li'),{textContent:a.complete?'Nenhuma divergência encontrada nesta categoria.':'Nenhuma ocorrência confirmada nesta categoria. A conferência está incompleta; consulte Outras ocorrências.'}));
  $('auditIssues').replaceChildren(fragment);$('auditLimit').textContent=items.length>300?'Mostrando 300 ocorrências. O Excel inclui todas.':'O Excel contém abas separadas de turmas e alunos, além dos campos AD/AI/PS e lançamentos.';
}
for(const [key,id] of [['classes','auditClasses'],['students','auditStudents'],['other','auditOther']])$(id).onclick=()=>{state.auditTab=key;showAudit();};
function downloadReport(){
  const r=state.report;if(!r||typeof URL.createObjectURL!=='function')return false;summarizeDestinations(r);
  try{const url=URL.createObjectURL(exportXlsx(reportSheets(r,state.records)));const a=document.createElement('a');a.href=url;a.download='SmartDuck_Conferencia_'+new Date().toISOString().replace(/[:.]/g,'-')+'.xlsx';a.click();setTimeout(()=>URL.revokeObjectURL(url),10000);return true;}
  catch(e){message('Relatório disponível no painel. Não foi possível iniciar o download: '+e.message,'warning');return false;}
}
$('export').onclick=downloadReport;
async function init(){
  const requested=Number(params.get('tab'));const tab=requested>0?await chrome.tabs.get(requested):(await chrome.tabs.query({active:true,currentWindow:true}))[0];
  if(!tab||!/^https:\/\/portal\.sophia\.com\.br\//.test(tab.url||''))throw new Error('Entre no SophiA e clique no pato da própria página.');
  state.tabId=tab.id;state.client=new PortalClient(tab.id);const saved=await loadSession(tab.id);
  if(saved&&[1,2,3,4,5,6].includes(saved.version)){
    state.files=saved.files;state.records=saved.records;state.report=saved.report;state.cursor=saved.cursor;state.phase=saved.phase;
    state.client.account=state.report?.account||null;
    state.queue=saved.queue.map(q=>({task:state.report.tasks.find(t=>t.id===q.taskId),rows:q.rows.map(i=>state.report.rows[i])}));
    state.pending=saved.pending?{...saved.pending,rows:saved.pending.rows.map(i=>state.report.rows[i])}:null;
    if(state.report?.complete)state.report.audit=buildAudit(state.records,state.report);showReport();showAudit();
    if(['inventory','review'].includes(state.phase)){state.phase='idle';message('Seus arquivos foram recuperados. Clique em Realizar para executar o lote completo.');}
    else if(state.phase==='applying'){state.phase='error';message('O painel foi fechado durante o preenchimento. Confira e salve ou descarte os campos no SophiA antes de iniciar outro lote. Não há repetição automática.','error');}
    else if(state.pending){state.phase='waiting';message('Sessão recuperada com gravação pendente de verificação. O programa fará apenas a releitura antes de continuar.');}
    else if(['running','scanning','auditing','recovering','paused'].includes(state.phase)){state.phase='paused';message('Sessão recuperada. Clique em Continuar o restante.');}
    else message('Arquivos e relatório recuperados. Clique em Realizar para um novo lote.');
  }
  fileList();render();await portalStatus();controls();
}
init().catch(e=>{message(e.message,'error');fileList();render();});
