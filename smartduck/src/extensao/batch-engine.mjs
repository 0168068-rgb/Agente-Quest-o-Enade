import {portalNavigation} from './navigation.mjs';
import {portalCommand} from './portal.mjs';
import {portalSave} from './save.mjs';
import {norm,equivalent} from './core.mjs';
import {attemptRead,failure} from './resilience.mjs';
import {FIXED_STAGE,classify,periodGroups} from './automatic.mjs';
import {resolveInventory} from './inventory.mjs';
import {unitKey,disciplineMatches,courseMatches,relevantRecords,planTask,finishInventory,reviewedChanges,verifySaved,contextMatches} from './batch-core.mjs';

const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));
const limit=(promise,ms=20000)=>{let timer;return Promise.race([promise,new Promise((_,reject)=>{timer=setTimeout(()=>reject(new Error('O portal não respondeu. Confira se há uma janela aberta ou se a sessão expirou.')),ms);})]).finally(()=>clearTimeout(timer));};
export class PortalClient {
  constructor(tabId,{pause=delay,savePolls=240}={}){this.tabId=tabId;this.pause=pause;this.savePolls=savePolls;this.savePending=null;this.documentId=null;}
  async call(func,command,world='ISOLATED'){
    const timeout=command.action==='apply'?Math.max(20000,Math.min(220000,(command.changes?.length||0)*100+10000)):20000;
    const result=await limit(chrome.scripting.executeScript({target:{tabId:this.tabId,frameIds:[0]},world,func,args:[command]}),timeout);
    if(result.length!==1||!result[0]?.result)throw new Error('O SophiA não respondeu de forma única. Confira a aba antes de continuar.');
    this.documentId=result[0].documentId||null;return result[0].result;
  }
  async state(notices=0){
    const s=await this.call(portalNavigation,{action:'state'},'MAIN');
    if(!s.ok&&s.dismissible&&notices<3){
      const a=await this.call(portalNavigation,{action:'acknowledge'},'MAIN');
      if(a.ok){await this.pause(250);if(s.savedNotice)return this.state(notices+1);throw failure(s.message,s.code);}
    }
    if(!s.ok)throw failure(s.message,s.code);
    if(this.account&&(this.account.school!==s.account?.school||this.account.name&&this.account.name!==s.account?.name))throw failure('A conta exibida no SophiA mudou. Encerre o lote e selecione os arquivos do professor conectado.','ACCOUNT_CHANGED');
    return s;
  }
  async ensureNotes(){const r=await this.call(portalNavigation,{action:'enter'},'MAIN');if(!r.ok)throw failure(r.message,r.code||'SESSION_UNAVAILABLE');return r.unchanged?this.ready():this.stable();}
  async recover(){
    let tab;try{tab=await chrome.tabs.get(this.tabId);}catch{throw failure('A aba do SophiA foi fechada.','TAB_UNAVAILABLE');}
    if(!/^https:\/\/portal\.sophia\.com\.br\//.test(tab.url||''))throw failure('Abra sua conta do SophiA nesta aba para continuar.','SESSION_UNAVAILABLE');
    // A reopened panel must also wait for an already-issued postback.
    if(!this.savePending){
      const saved=await this.call(portalSave,{action:'saveStatus'},'MAIN');
      if(saved.nonce&&!saved.finished)this.savePending={nonce:saved.nonce,documentId:this.documentId,loading:false};
    }
    if(this.savePending)await this.waitSave();
    const guard=await this.call(portalCommand,{action:'prepareRecovery'});
    if(!guard.ok)throw failure(guard.message,guard.code);
    await limit(chrome.tabs.reload(this.tabId));return this.stable();
  }
  async reread(task,exam){
    await this.recover();await this.open(task);return this.scan(exam,{optional:true});
  }
  async confirm(task,exam,rows){
    const snapshot=await this.reread(task,exam);
    if(snapshot&&!contextMatches(snapshot,task))throw failure('A turma mudou durante a verificação.');
    return rows.map(row=>{
      const matches=(snapshot?.rows||[]).filter(p=>p.ra===row.ra&&norm(p.name)===norm(row.name));
      return {row,confirmed:matches.length===1&&equivalent(matches[0].value,row.after)};
    });
  }
  async stable(){
    let previous='',same=0;
    for(let i=0;i<80;i++){
      await this.pause(250);
      let s;
      try{s=await this.state();}catch(e){if(e.code||/expired|expirou|mensagem|identificar/i.test(e.message))throw e;if(i>12)throw e;continue;}
      if(!s.busy&&s.signature===previous)same++;else same=0;
      previous=s.signature;
      if(same>=3)return s;
    }
    throw new Error('O portal não estabilizou os filtros. O lote foi interrompido.');
  }
  async ready(){const s=await this.state();return s.busy?this.stable():s;}
  async command(action,extra={},knownState=null){
    const s=knownState||await this.ready();
    const result=await this.call(portalNavigation,{action,signature:s.signature,account:this.account,...extra},'MAIN');
    if(!result.ok)throw failure(result.message,result.code);
    return result.unchanged?s:await this.stable();
  }
  async reset(){const s=await this.ready();if(s.controls.periodo.disabled)return this.command('new');return s;}
  async select(kind,option,knownState=null){
    const s=knownState||await this.ready(),c=s.controls[kind];
    if(!c.options.some(o=>o.value===option.value&&norm(o.text)===norm(option.text)))throw Object.assign(new Error('O filtro '+kind+' mudou ou não está mais disponível: '+option.text),{code:'OPTION_UNAVAILABLE'});
    if(c.value===option.value&&norm(c.text)===norm(option.text))return s;
    return this.command('select',{kind,value:option.value,text:c.options.find(o=>o.value===option.value).text},s);
  }
  async filters(values){let s=await this.reset();for(const k of ['periodo','unidade','turma','etapa','disciplina'])if(values[k])s=await this.select(k,values[k],s);return s;}
  async open(task){
    const s=await this.ready(),same=['periodo','unidade','turma','etapa','disciplina'].every(k=>s.controls[k].disabled&&s.controls[k].value===task[k].value&&norm(s.controls[k].text)===norm(task[k].text));
    const page=s.page.current||(!s.page.next&&!s.page.numbers.length?1:null);
    // Reuse only the exact rendered result. A fresh scan still checks values
    // before applying; confirm() still reloads the server after every Save.
    if(same&&page===(task.page||1))return s;
    await this.filters(task);await this.command('search');
    for(let page=2;page<=(task.page||1);page++)if(!await this.advance(page))throw new Error('A página de alunos selecionada na conferência não está mais disponível.');
  }
  async advance(wanted){
    const s=await this.ready();
    if(s.page.numbers.includes(wanted))return this.command('page',{page:String(wanted)});
    if(s.page.next)return this.command('page',{page:'Next'});
    if(s.page.total&&wanted<=s.page.total)throw failure('Controle de paginação não reconhecido para a página '+wanted+'.');
    return null;
  }
  async scan(exam,{optional=false}={}){const r=await this.call(portalCommand,{action:'scan',exam});if(!r.ok){if(optional&&r.code==='ASSESSMENT_UNAVAILABLE')return null;throw failure(r.message,r.code);}return r.snapshot;}
  async catalog(){const r=await this.call(portalCommand,{action:'catalog'});if(!r.ok)throw failure(r.message,r.code);return r;}
  async apply(exam,max,snapshot,changes){return this.call(portalCommand,{action:'apply',exam,max,onlyEmpty:true,fingerprint:snapshot.fingerprint,changes});}
  async waitSave(){
    const pending=this.savePending;if(!pending)return;
    for(let poll=0;poll<this.savePolls;poll++){
      await this.pause(250);
      let tab;try{tab=await chrome.tabs.get(this.tabId);}catch{throw failure('A aba do SophiA foi fechada durante Salvar.','TAB_UNAVAILABLE');}
      if(tab.status==='loading'){pending.loading=true;continue;}
      let status;
      try{status=await this.call(portalSave,{action:'saveStatus',nonce:pending.nonce},'MAIN');}
      catch(e){if(poll<this.savePolls-1)continue;throw e;}
      const newDocument=!!pending.documentId&&!!this.documentId&&this.documentId!==pending.documentId;
      if(newDocument||status.finished||(status.missing&&pending.loading)){
        this.savePending=null;
        if(status.error||status.validation)throw failure(status.error||status.validation);
        await this.stable();return;
      }
      // A success notice is a completion signal, but never proof of persistence.
      // state() acknowledges the notice; confirm() will still reread the server.
      const page=await this.call(portalNavigation,{action:'state'},'MAIN');
      if(!page.ok&&page.dialog){
        const notice=await this.call(portalSave,{action:'saveNotice',nonce:pending.nonce},'MAIN');
        if(!notice.completed)continue;
        this.savePending=null;await this.state();
        if(!page.savedNotice)throw failure(page.message,page.code);
        await this.stable();return;
      }
      if(!page.ok&&page.code==='SESSION_UNAVAILABLE'){this.savePending=null;throw failure(page.message,page.code);}
      // If there was definitely no request, keep the failure local and continue.
      if(poll>=19&&status.issued&&!status.started){
        const stopped=await this.call(portalSave,{action:'saveNotStarted',nonce:pending.nonce},'MAIN');
        if(stopped.abandoned){this.savePending=null;throw failure('O link Salvar foi acionado, mas o SophiA não iniciou a gravação.');}
      }
    }
    throw failure('O SophiA ainda está processando Salvar. Aguarde a resposta antes de continuar.','SAVE_IN_FLIGHT');
  }
  async save(exam,changes,token){
    const prepared=await this.call(portalCommand,{action:'prepareSave',exam,changes,token});
    if(!prepared.ok)throw failure(prepared.message,prepared.code);
    const documentId=this.documentId;
    this.savePending={nonce:prepared.nonce,documentId,loading:false};
    let issued;
    try{issued=await this.call(portalSave,{...prepared,action:'saveClick'},'MAIN');}
    catch(e){await this.waitSave();throw e;}
    if(!issued.ok){this.savePending=null;throw failure(issued.message,issued.code);}
    await this.waitSave();
  }
  async verify(task,exam,rows){
    const checked=await this.confirm(task,exam,rows);
    if(checked.some(r=>!r.confirmed))throw failure('A releitura do servidor não confirmou todas as notas. Esta gravação não será repetida automaticamente.');
    return true;
  }
  async focus(){await chrome.tabs.update(this.tabId,{active:true});}
}

export async function discover({client,records,period,stage,exam,options,onProgress=()=>{},cancelled=()=>false}){
  const tasks=[],rows=[],warnings=[];
  const check=()=>{if(cancelled())throw new Error('Consulta interrompida. Nenhuma nota foi alterada.');};
  const first=await client.filters({periodo:period});
  const units=first.controls.unidade.options.filter(u=>records.some(r=>unitKey(r.campus)===unitKey(u.text)));
  const missing=[...new Set(records.map(r=>r.campus))].filter(c=>!units.some(u=>unitKey(c)===unitKey(u.text)));
  if(missing.length)warnings.push('Campi/polos não disponíveis: '+missing.join(', '));
  let consulted=0;
  for(const unit of units){
    check();const unitRecords=relevantRecords(records,{unit});
    const unitState=await client.filters({periodo:period,unidade:unit});
    const classes=unitState.controls.turma.options.filter(c=>unitRecords.some(r=>courseMatches(r.course,c.text)));
    const missingCourses=[...new Set(unitRecords.map(r=>r.course))].filter(c=>!classes.some(t=>courseMatches(c,t.text)));
    if(missingCourses.length)warnings.push(unit.text+': curso sem turma reconhecida: '+missingCourses.join(', '));
    for(const classroom of classes){
      check();onProgress('Consultando '+unit.text+' · '+classroom.text+'…');
      let s=await client.filters({periodo:period,unidade:unit,turma:classroom});
      const stages=s.controls.etapa.options.filter(e=>norm(e.text)===norm(stage.text));
      if(stages.length!==1){warnings.push(classroom.text+': etapa “'+stage.text+'” ausente ou ambígua.');continue;}
      const etapa=stages[0];s=await client.select('etapa',etapa);
      const classRecords=relevantRecords(unitRecords,{classroom});
      const disciplines=s.controls.disciplina.options.filter(d=>classRecords.some(r=>disciplineMatches(r,d)));
      for(const discipline of disciplines){
        check();let page=1;const seen=new Set();
        const task={periodo:period,unidade:unit,turma:classroom,etapa,disciplina:discipline,page,exam,max:options.max};
        await client.open(task);
        while(true){
          check();onProgress('Conferindo '+classroom.text+' · '+discipline.text+' · página '+page+' ('+(++consulted)+' telas)…');
          const snapshot=await client.scan(exam,{optional:true});
          if(!snapshot){warnings.push(classroom.text+' · '+discipline.text+': avaliação '+exam+' não disponível no SophiA.');break;}
          const pageIdentity=JSON.stringify(snapshot.rows.map(r=>[r.ra,r.name]));
          if(seen.has(pageIdentity))throw new Error('A paginação repetiu os mesmos alunos. Consulta interrompida para evitar duplicação.');
          seen.add(pageIdentity);
          const planned=planTask(records,snapshot,{...task,page},options);
          if(planned.rows.length){tasks.push(planned.task);rows.push(...planned.rows);}
          if(!await client.advance(page+1))break;
          if(++page>1000)throw new Error('Paginação excessiva; confira os filtros no portal.');
        }
      }
    }
  }
  check();return {...finishInventory(records,tasks,rows),warnings,period,stage,exam,options,complete:true,created:new Date().toISOString()};
}

// Read every class, discipline and page of one unit before resolving its notes.
// No grade is written here, so an interrupted read can be repeated safely.
export async function scanUnit({client,records,period,unit,onProgress=()=>{},cancelled=()=>false}){
  const entries=[],portalMap=[],warnings=[],byRA=new Map();
  const check=()=>{if(cancelled())throw failure('Consulta pausada pelo usuário.','CANCELLED');};
  const label=base=>[base.unidade?.text,base.turma?.text,base.disciplina?.text,base.exam,base.page?'página '+base.page:''].filter(Boolean).join(' · ');
  const run=(base,read)=>attemptRead({client,read,cancelled,onError:(e,n)=>{
    const text=label(base)+': tentativa '+n+' — '+e.message;warnings.push(text);onProgress(text+' Continuando automaticamente…');
  }});
  const failed=(base,error)=>portalMap.push({...base,failed:true,students:0,status:'Opção tentada sem sucesso: '+error.message});
  for(const r of records){if(!byRA.has(r.ra))byRA.set(r.ra,[]);byRA.get(r.ra).push(r);}
  const unitBase={periodo:period,unidade:unit};
  check();const unitRead=await run(unitBase,()=>client.filters(unitBase));
  if(!unitRead.ok){failed(unitBase,unitRead.error);return {entries,portalMap,warnings};}
  const u=unitRead.value;
  if(!u.controls.turma.options.length)portalMap.push({...unitBase,status:'Sem turmas disponíveis: próxima unidade',students:0});
  for(const classroom of u.controls.turma.options){
    check();onProgress('Consultando '+unit.text+' · '+classroom.text+'…');
    const base={...unitBase,turma:classroom};
    const classRead=await run(base,()=>client.filters(base));
    if(!classRead.ok){failed(base,classRead.error);continue;}
    const stages=classRead.value.controls.etapa.options.filter(e=>norm(e.text)==='SEMESTRE');
    if(stages.length!==1){portalMap.push({...base,status:'Etapa Semestre ausente ou ambígua',students:0});warnings.push(label(base)+': etapa Semestre ausente ou ambígua.');continue;}
    const etapa=stages[0];
    const stageRead=await run({...base,etapa},async attempt=>{const s=attempt>1?await client.filters(base):classRead.value;return client.select('etapa',etapa,s);});
    if(!stageRead.ok){failed(base,stageRead.error);continue;}
    if(!stageRead.value.controls.disciplina.options.length)portalMap.push({...base,etapa,status:'Sem disciplinas disponíveis: próxima turma',students:0});
    for(const discipline of stageRead.value.controls.disciplina.options){
      check();const task={...base,etapa,disciplina:discipline};
      const opened=await run(task,()=>client.open(task));
      if(!opened.ok){failed(task,opened.error);continue;}
      let page=1;const seen=new Set(),needed=records.filter(r=>disciplineMatches(r,discipline));
      while(true){
        check();const current={...task,page};
        onProgress('Consultando '+label(current)+'…');
        const read=await run(current,async attempt=>{
          if(attempt>1)await client.open(current);
          const catalog=await client.catalog();
          if(!contextMatches(catalog,current))throw failure('Os filtros não correspondem à opção consultada.');
          return catalog;
        });
        let resetPage=!read.ok;
        if(!read.ok)failed(current,read.error);
        else{
          const catalog=read.value;
          if(seen.has(catalog.identity)){failed({...task,page,remainingPages:true},failure('Paginação repetida; seguindo para a próxima disciplina.'));break;}
          seen.add(catalog.identity);
          const destination={...current,assessments:catalog.assessments,assessmentsKnown:catalog.assessmentsKnown??catalog.assessments.length>0,columns:catalog.columns,students:catalog.students,roster:catalog.roster,status:catalog.students?'Sem notas correspondentes nos arquivos':catalog.emptyReason||'Sem alunos nesta página'};
          portalMap.push(destination);
          for(const exam of catalog.assessments){
            if(!needed.some(r=>!r.exam||r.exam===exam))continue;
            const scanned=await run({...current,exam},async attempt=>{
              if(attempt>1||resetPage){await client.open(current);resetPage=false;}
              const snapshot=await client.scan(exam,{optional:true});
              if(snapshot&&!contextMatches(snapshot,current))throw failure('Destino divergente durante a leitura.');
              return snapshot;
            });
            if(!scanned.ok){failed({...current,exam},scanned.error);resetPage=true;continue;}
            const snapshot=scanned.value;
            if(!snapshot){warnings.push(label(current)+': avaliação '+exam+' indisponível durante a consulta.');continue;}
            const matched=snapshot.rows.filter(p=>(byRA.get(p.ra)||[]).some(r=>(!r.exam||r.exam===exam)&&disciplineMatches(r,discipline)));
            if(matched.length){entries.push({task:{...current,exam,max:exam==='AD'?100:10},snapshot:{context:snapshot.context,rows:matched}});destination.status='Consultado: correspondências em análise';}
          }
          for(const exam of new Set(needed.map(r=>r.exam).filter(Boolean)))if(!catalog.assessments.includes(exam))warnings.push(label(current)+': avaliação '+exam+' não disponível no SophiA.');
        }
        // Reopen after a failed read because recovery reloads the current tab.
        const advanced=await run({...task,page:page+1},async attempt=>{
          if(attempt>1||resetPage)await client.open(current);
          return client.advance(page+1);
        });
        if(!advanced.ok){failed({...task,page:page+1,remainingPages:true},advanced.error);break;}
        if(!advanced.value)break;
        if(++page>1000){failed({...task,page,remainingPages:true},failure('Limite de paginação atingido; próxima disciplina.'));break;}
      }
    }
  }
  check();return {entries,portalMap,warnings};
}

export async function discoverAutomatic({client,records,fallbackExam='',onProgress=()=>{},cancelled=()=>false,now=new Date()}){
  const classified=classify(records,fallbackExam),first=await client.ensureNotes();
  const groups=periodGroups(classified,first.controls.periodo,now);
  const tasks=[],rows=[],warnings=[],portalMap=[];
  for(const {period,records:group} of groups){
    const entries=[],groupMap=[],firstUnit=await client.filters({periodo:period});
    for(const unit of firstUnit.controls.unidade.options){
      const result=await scanUnit({client,records:group,period,unit,onProgress,cancelled});
      entries.push(...result.entries);groupMap.push(...result.portalMap);warnings.push(...result.warnings);
    }
    const resolved=resolveInventory(group,entries,groupMap);tasks.push(...resolved.tasks);rows.push(...resolved.rows);portalMap.push(...groupMap);
  }
  const periods=groups.map(g=>g.period),catalog=[...new Set(classified.map(r=>r.exam).filter(Boolean))].map(exam=>({exam,count:classified.filter(r=>r.exam===exam).length}));
  return {tasks,rows,warnings:[...new Set(warnings)],period:{text:periods.map(p=>p.text).join(' / ')},periods,stage:FIXED_STAGE,exam:[...new Set(tasks.map(t=>t.exam))].join(' / '),catalog,portalMap,complete:true,created:new Date().toISOString()};
}

// Runs one reviewed page. UI owns the queue and can pause without losing the report.
export async function fillTask(client,task,rows,{exam,max,retry=false}){
  const skipAll=status=>{for(const row of rows){row.ready=false;row.status=status;}return {changes:[],rows:[]};};
  try{await client.open(task);}catch(e){if(e.code==='OPTION_UNAVAILABLE')return skipAll('Não inserido: '+e.message);throw e;}
  const fresh=await client.scan(exam,{optional:true});
  if(!fresh)return skipAll('Não inserido: avaliação '+exam+' indisponível na releitura');
  const {changes,same,skipped}=reviewedChanges(rows,fresh,task);
  for(const row of same){row.ready=false;row.status='Já possui esse valor na releitura';}
  for(const {row,status} of skipped){row.ready=false;row.status=status;}
  if(!changes.length)return {changes:[],rows:[]};
  let result;
  try{result=await client.apply(exam,max,fresh,changes);}
  catch(e){
    const uncertain=new Set(changes.map(c=>c.recordId));
    for(const row of rows)if(uncertain.has(row.recordId)){row.ready=false;row.status='Resultado desconhecido: conferir o portal antes de repetir';}
    throw new Error('A conexão mudou durante o preenchimento. O resultado pode ser parcial; confira a aba e o relatório antes de repetir.');
  }
  if(!result.ok&&result.code==='STALE_SNAPSHOT'&&!retry)return fillTask(client,task,rows,{exam,max,retry:true});
  const byId=new Map(changes.map(c=>[c.recordId,c]));
  const changedRows=rows.filter(r=>byId.has(r.recordId));
  const outcomes=new Map((result.results||[]).map(r=>[r.key,r]));
  for(const row of changedRows){row.ready=false;row.status=outcomes.get(byId.get(row.recordId).key)?.status||'Preenchimento não confirmado; conferir no portal';}
  if(!result.ok)throw new Error(result.message||'O preenchimento não foi confirmado; confira o portal antes de repetir.');
  const applied=changes.filter(c=>!outcomes.get(c.key)?.skipped),appliedIds=new Set(applied.map(c=>c.recordId));
  return {changes:applied,rows:changedRows.filter(r=>appliedIds.has(r.recordId)),token:result.token};
}
