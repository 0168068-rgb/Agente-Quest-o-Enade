(function () {
  'use strict';
  if (window.top!==window.self || !window.SmartFoxBankClient || !window.SmartFoxBankContext || !window.SmartFoxAccess) return;
  const Context=window.SmartFoxBankContext, NAV='smartfoxBankNavigationV11';
  const Core=window.SmartFoxBankClient, QUEUE='smartfoxBankCleanupV11', SESSION='aabSessionV7';
  let busy=false, stopped=false, scopes=[],banks=[],previewSelection='',client=null,dialog=null,previousFocus=null;
  let questionSelection=new Set(),questionPage=0,scopeSelection=new Set(),dialogContext='';
  const owner=()=>window.SmartFoxIdentity.extractAvaliaIdentity(document).normalizedName;
  const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const storageGet=async key=>(await chrome.storage.local.get(key))[key];
  async function locked(name,fn) {
    if(!navigator.locks?.request) throw new Error('Este navegador não oferece o bloqueio necessário. Atualize o Chrome para continuar.');
    return navigator.locks.request(name,fn);
  }
  const parseDocument=html=>new DOMParser().parseFromString(html,'text/html');
  function parseTags(value) {
    if(Array.isArray(value)) return value.map(t=>String(typeof t==='string'?t:t.nome||t.label||'')).filter(Boolean);
    const doc=parseDocument(String(value||''));
    const labels=Array.from(doc.querySelectorAll('.label, .tag, [data-tag]')).map(e=>e.textContent.trim()).filter(Boolean);
    if(labels.length) return labels;
    return doc.body.textContent.trim()?[doc.body.textContent.trim()]:[];
  }
  function status(message,isError=false) {
    if(dialog) { const el=dialog.querySelector('[data-status]'); el.textContent=message;el.dataset.error=String(isError); }
    const launcher=document.getElementById('sf-bank-launcher');
    if(launcher) launcher.title=message;
  }
  async function authorize(expectedOwner) {
    if(!expectedOwner || owner()!==expectedOwner) throw new Error('O perfil do AvaliA mudou. Reabra o banco com a conta que iniciou esta operação.');
    await window.SmartFoxAccess.assertAuthorized({force:false});
  }
  function contextClient(expectedOwner) {return Context.create({fetch:(...args)=>fetch(...args),parseDocument,expectedOwner,onProgress:status,normalizeOwner:window.SmartFoxIdentity.normalizePersonName});}
  function selectedInstitution(records=[]) {
    const ids=[...new Set(records.map(r=>r.institutionId).filter(Boolean).map(String))];
    if(ids.length>1)throw new Error('Um lote precisa manter a mesma instituição. Separe as provas por instituição.');
    return Context.choose(Context.snapshot(document),ids[0]||dialog?.querySelector('[data-institution]')?.value);
  }
  function productsFromPage() {
    return Core.productsFromDocument(document);
  }
  async function loadedProducts(expectedOwner,institution) {
    // Existing blue tabs can supply a rendered selector without navigating the
    // elaboration form. Only matching teacher/institution snapshots are used.
    try {
      const result=await chrome.runtime.sendMessage({type:'SF_AVALIA_PRODUCTS',owner:expectedOwner,institutionId:institution.id});
      if(result?.ok&&result.data?.products?.length)return result.data.products;
    } catch(error) {status(`Conferindo diretamente a página do AvaliA. ${error.message}`);}
    return Core.readRenderedProducts({document,origin:location.origin,institutionId:institution.id,expectedOwner,
      snapshot:Context.snapshot,normalizeOwner:window.SmartFoxIdentity.normalizePersonName,shouldStop:()=>stopped});
  }
  function makeClient(expectedOwner,institution=selectedInstitution()) {
    const context=contextClient(expectedOwner);
    const local=Context.snapshot(document);
    const sameContext=local.current?.id===institution.id&&Context.normalize(local.role)==='professor/tutor';
    return Core.createClient({fetch:(...args)=>fetch(...args),parseDocument,parseTags,institution,initialProducts:sameContext?productsFromPage():[],
      loadProducts:()=>loadedProducts(expectedOwner,institution),
      authorize:async()=>{await authorize(expectedOwner);await context.assertCurrent(institution.id);},onProgress:status,shouldStop:()=>stopped});
  }
  async function navigateInstitution(institution,{runId=null,questionIds=[],retry=false}={}) {
    const state=await contextClient(owner()).read();
    const target=state.institutions.find(i=>i.id===institution.id&&!i.general);
    if(!target)throw new Error('A instituição do envio não está disponível em Minhas Instituições.');
    const navigation={owner:owner(),institutionId:target.id,institutionName:target.name,runId,questionIds,retry,at:Date.now(),stage:'institution',href:target.href};
    await chrome.storage.local.set({[NAV]:navigation});return navigation;
  }
  function navigate(navigation) {
    if(navigation.owner!==owner())throw new Error('O professor mudou antes da troca de instituição.');
    const href=navigation.href;
    const contextRoute=/^\/Contexto\/Alterar(?:Instituicao|Papel)\/[1-9]\d*$/.test(href);
    const bankRoute=navigation.stage==='bank' && /^[1-9]\d*$/.test(String(navigation.scope?.idGradeDisciplina||''))
      && href===`/AssociarConteudoDisciplina/Index?idGradeDisciplina=${navigation.scope.idGradeDisciplina}`;
    const productRoute=navigation.stage==='product' && href==='/Professor';
    if(!contextRoute&&!bankRoute&&!productRoute)throw new Error('Caminho do banco inválido.');
    location.assign(href);
  }
  async function accessInstitution() {const navigation=await navigateInstitution(selectedInstitution());navigate(navigation);}

  function setBusy(value) {
    busy=value;
    dialog?.querySelectorAll('button:not([data-close]):not([data-stop]),input,select').forEach(e=>e.disabled=value);
    if(!value) for(const scope of scopes) { const field=dialog?.querySelector(`input[data-scope="${scope.key}"]`);if(field) field.disabled=scope.readonly; }
    if(!value)dialog?.querySelectorAll('[data-question][data-locked="true"]').forEach(e=>e.disabled=true);
    const stop=dialog?.querySelector('[data-stop]'); if(stop) stop.hidden=!value;
    updateControls();
  }
  async function assertContextIdle() {
    const lock=await storageGet('aabRunLockV7'),session=await storageGet(SESSION);
    if(lock&&Date.now()-Number(lock.heartbeatAt||0)<20000&&session&&session.currentIndex<session.items.length)throw new Error('Aguarde o envio das questões terminar antes de trocar a instituição ou gerenciar likes.');
  }
  async function work(fn) {
    if(busy) return;
    stopped=false;setBusy(true);
    try { await assertContextIdle();return await locked('smartfox-bank-operation-v11',fn); }
    catch(error) {status(error.message,true);}
    finally {setBusy(false);}
  }
  function selectedScopes() { return scopes.filter(s=>scopeSelection.has(s.key)); }
  function updateControls() {
    if(!dialog)return;
    const selection=selectedScopes(),current=selection.map(s=>s.key).sort().join('|');
    let valid=false;
    try{valid=Boolean(banks.length&&previewSelection===current&&plan().actions.length);}catch{}
    dialog.querySelector('[data-apply]').disabled=busy||!valid;
    dialog.querySelector('[data-inspect]').disabled=busy||!selection.length;
    for(const key of ['question-page','question-all','question-none'])dialog.querySelector(`[data-${key}]`).disabled=busy||!banks.length;
    dialog.querySelector('[data-question-prev]').disabled=busy||questionPage===0;
    dialog.querySelector('[data-question-next]').disabled=busy||(questionPage+1)*50>=visibleQuestionEntries().length;
    const counter=dialog.querySelector('[data-scope-count]');if(counter)counter.textContent=`${selection.length} banco(s) selecionado(s) · ${scopes.length} detectado(s)`;
    const context=dialog.querySelector('[data-current-bank]');
    if(context)context.textContent=banks.length?banks.map(b=>scopeLabel(b.scope)).join(' • '):'Escolha as disciplinas ou abra um banco no AvaliA.';
  }
  function invalidatePreview() { banks=[];questionSelection.clear();renderQuestions(); previewSelection='';dialog.querySelector('[data-preview]').textContent='Confira os bancos selecionados para carregar as questões.';updateControls(); }
  function renderScopes() {
    const product=dialog.querySelector('[data-product]').value;
    const visible=scopes.filter(s=>!product || s.modalityId===product);
    dialog.querySelector('[data-scopes]').innerHTML=visible.map(s=>`<label class="sf-bank-scope"><input type="checkbox" data-scope="${s.key}" ${scopeSelection.has(s.key)?'checked':''} ${s.readonly?'disabled':''}><span><strong>${esc(s.name)}</strong><small>Disciplina ${esc(s.idDisciplina)} · alocação ${esc(s.idGradeDisciplina)}</small><small>${esc(s.course)} · ${esc(s.grade)} · ${esc(s.modality)}${s.contextAmbiguous?' · Banco compartilhado/ambíguo: alteração bloqueada':s.readonly?' · Consulta indisponível neste período':''}</small></span></label>`).join('')||'<p>Nenhuma disciplina encontrada neste perfil.</p>';
    dialog.querySelectorAll('[data-scope]').forEach(e=>e.addEventListener('change',()=>{if(e.checked)scopeSelection.add(e.dataset.scope);else scopeSelection.delete(e.dataset.scope);invalidatePreview();}));
    updateControls();
    status(`${scopes.length} banco(s) encontrado(s) em todas as modalidades disponíveis. Selecione os bancos que deseja alterar.`);
  }
  function plan() {return Core.buildPlan(banks,dialog.querySelector('[data-mode]').value,dialog.querySelector('[data-tag]').value,questionSelection);}
  function renderPreview() {
    const mode=dialog.querySelector('[data-mode]').value;
    dialog.querySelector('[data-tag-field]').hidden=!['keep-tag','like-tag'].includes(mode);
    if(!banks.length){updateControls();return;}
    try {
      const p=plan();
      dialog.querySelector('[data-preview]').textContent=`${banks.reduce((n,b)=>n+b.questions.length,0)} questões conferidas · ${p.total} selecionadas · ${p.actions.length} ${p.disliking?'dislikes a aplicar':`likes a ${p.adding?'adicionar':'retirar'}`} · ${p.preserved.length} likes preservados · ${p.blocked.length} bloqueados pelo AvaliA.${p.disliking?' Motivo: Questão com erro (Problema na Questão no AvaliA). Justificativa: “não gostei da questão”.':''}`;
    } catch(error) {dialog.querySelector('[data-preview]').textContent=error.message;}
    updateControls();
  }
  async function discover() {
    scopeSelection.clear();invalidatePreview();
    await authorize(owner());const institution=selectedInstitution();
    const state=await contextClient(owner()).read();
    if(state.current.id!==institution.id||Context.normalize(state.role)!=='professor/tutor') {await accessInstitution();return;}
    client=makeClient(owner(),institution);scopes=await client.discover();banks=[];previewSelection='';
    dialog.querySelector('[data-product]').innerHTML='<option value="">Todos os produtos</option>'+(client.products?.()||[...new Map(scopes.map(s=>[s.modalityId,s.modality])).entries()].map(([id,label])=>({id,label}))).map(p=>`<option value="${esc(p.id)}">${esc(p.label)}${p.count===0?' — sem disciplinas':''}</option>`).join('');
    renderScopes();
  }
  async function inspect() {
    const selected=selectedScopes();
    if(!selected.length) throw new Error('Selecione ao menos uma disciplina.');
    invalidatePreview();client=makeClient(owner());const scanned=[];
    for(const scope of selected)scanned.push(await client.scan(scope));
    banks=scanned;
    previewSelection=selected.map(s=>s.key).sort().join('|');
    questionSelection=new Set(questionEntries().filter(e=>!e.question.readonly).map(e=>e.key));questionPage=0;
    renderTags();renderQuestions();renderPreview();status('Leitura concluída. Selecione as questões e confira a operação.');
  }
  function renderTags() {
    const labels=[...new Set(banks.flatMap(b=>b.questions.flatMap(q=>q.tags)))].sort((a,b)=>a.localeCompare(b,'pt-BR'));
    const field=dialog.querySelector('[data-tag]'),previous=field.value;
    field.innerHTML='<option value="">Escolha a TAG</option>'+labels.map(t=>`<option value="${esc(t)}">${esc(t)}</option>`).join('');
    if(labels.includes(previous))field.value=previous;
  }
  function questionEntries() {return banks.flatMap(b=>b.questions.map(question=>({scope:b.scope,question,key:Core.questionKey(b.scope,question.id)})));}
  function visibleQuestionEntries() {
    const term=Core.normalize(dialog?.querySelector('[data-question-search]')?.value||'');
    return questionEntries().filter(e=>!term||Core.normalize(`${e.question.id} ${e.question.name} ${e.question.tags.join(' ')}`).includes(term));
  }
  function selectQuestionPage(allBanks=false) {
    const entries=allBanks?questionEntries():visibleQuestionEntries().slice(questionPage*50,(questionPage+1)*50);
    for(const e of entries)if(!e.question.readonly&&!e.scope.readonly)questionSelection.add(e.key);
    renderQuestions();renderPreview();
  }
  function renderQuestions() {
    if(!dialog)return;
    const holder=dialog.querySelector('[data-questions]');if(!holder)return;
    const entries=visibleQuestionEntries(),pages=Math.max(1,Math.ceil(entries.length/50));questionPage=Math.max(0,Math.min(questionPage,pages-1));
    const labels={validada:'Com like',pendente:'Sem like',desativada:'Com dislike'};
    holder.innerHTML=entries.slice(questionPage*50,(questionPage+1)*50).map(e=>`<label class="sf-bank-question"><input type="checkbox" data-question="${esc(e.key)}" data-locked="${Boolean(e.question.readonly||e.scope.readonly)}" ${questionSelection.has(e.key)?'checked':''} ${e.question.readonly||e.scope.readonly?'disabled':''}><span><strong>${esc(e.question.id)} · ${esc(e.question.name)}</strong><small>${esc(e.scope.modality)} · ${esc(e.scope.name)} · alocação ${esc(e.scope.idGradeDisciplina)}</small><small>${esc(labels[e.question.state])} · TAGs: ${esc(e.question.tags.join(', ')||'sem TAG')}${e.question.readonly?' · alteração bloqueada':''}</small></span></label>`).join('')||'<p>Confira os bancos ou ajuste a pesquisa para listar as questões.</p>';
    holder.querySelectorAll('[data-question]').forEach(el=>el.onchange=()=>{if(el.checked)questionSelection.add(el.dataset.question);else questionSelection.delete(el.dataset.question);renderQuestions();renderPreview();});
    dialog.querySelector('[data-question-count]').textContent=`${questionSelection.size} selecionadas · página ${questionPage+1} de ${pages} · ${entries.length} na lista`;
    updateControls();
  }
  async function openQuestionSelection({target,questionIds=null,mode='all'}) {
    if(busy)throw new Error('Aguarde a leitura atual terminar. Sua seleção continua na tabela.');
    const expectedOwner=owner();
    if(target.owner&&target.owner!==expectedOwner)throw new Error('O professor mudou após a seleção. Atualize o banco.');
    open();await work(async()=>{
      invalidatePreview();
      await authorize(expectedOwner);const institution=selectedInstitution([{institutionId:target.institutionId}]);
      await contextClient(expectedOwner).assertCurrent(institution.id);
      client=makeClient(expectedOwner,institution);scopes=await client.discover();
      const matches=scopes.filter(s=>s.idGrade===String(target.idGrade)&&s.idDisciplina===String(target.idDisciplina)
        &&(!target.modalityId||s.modalityId===String(target.modalityId))&&(!target.idGradeDisciplina||s.gradeDisciplineIds.includes(String(target.idGradeDisciplina))));
      if(matches.length!==1||matches[0].readonly)throw new Error('O banco aberto não tem um caminho único e editável nesta instituição e produto. Use Detectar disciplinas e confira o código.');
      const scope=matches[0];scopeSelection=new Set([scope.key]);
      dialog.querySelector('[data-institution]').value=institution.id;
      dialog.querySelector('[data-product]').innerHTML='<option value="">Todos os produtos</option>'+(client.products?.()||[]).map(p=>`<option value="${esc(p.id)}">${esc(p.label)}</option>`).join('');renderScopes();
      const checkbox=dialog.querySelector(`input[data-scope="${scope.key}"]`);if(checkbox)checkbox.checked=true;
      banks=[await client.scan(scope)];previewSelection=scope.key;questionSelection.clear();questionPage=0;
      const available=new Set(banks[0].questions.map(q=>q.id));
      if(questionIds!==null&&questionIds.some(id=>!available.has(String(id)))){invalidatePreview();throw new Error('Uma questão selecionada não foi encontrada neste banco. Atualize a tabela.');}
      const ids=questionIds===null?available:new Set(questionIds.map(String));
      for(const q of banks[0].questions)if(ids.has(q.id)&&!q.readonly)questionSelection.add(Core.questionKey(scope,q.id));
      dialog.querySelector('[data-mode]').value=mode;renderTags();renderQuestions();renderPreview();
      status('Confira as questões selecionadas e clique em Aplicar operação.');
      dialog.querySelector('[data-bank-picker]').open=false;
      dialog.querySelector('.sf-bank-body').scrollTop=0;
    });
  }

  async function applyManual() {
    if(!banks.length || previewSelection!==selectedScopes().map(s=>s.key).sort().join('|')) throw new Error('Confira os bancos selecionados antes de aplicar a operação.');
    const p=plan();
    if(!p.total)throw new Error('Selecione ao menos uma questão.');
    if(!p.actions.length) {status(p.blocked.length?'As questões selecionadas estão bloqueadas para esta operação.':'As questões selecionadas já estão no estado escolhido.',Boolean(p.blocked.length));return;}
    if(!confirm(`SmartFox 11.0\n\n${p.disliking?'Dar dislike em':p.adding?'Adicionar like em':'Retirar like de'} ${p.actions.length} questões em ${banks.length} banco(s)?\n${banks.map(b=>scopeLabel(b.scope)).join('\n')}\n\n${p.disliking?'Motivo: Questão com erro (Problema na Questão no AvaliA). Justificativa: não gostei da questão. Se houver like, ele será retirado antes do dislike.':p.mode==='keep-tag'?`Preservar somente os likes existentes na TAG “${p.tag}”.`:p.adding?`Aprovar questões pendentes${p.mode==='like-tag'?` com a TAG “${p.tag}”`:''}. Questões invalidadas não serão reativadas.`:'Todas as questões selecionadas ficarão sem like, quando o AvaliA permitir.'}\n\nEsse é o produto e a disciplina corretos?\nNenhuma questão será apagada.`)) return;
    const results=await client.apply(p);
    // A second complete scan checks that no remaining like was missed or added meanwhile.
    const finalBanks=[];
    if(!results.failed.length && !stopped) for(const b of banks) finalBanks.push(await client.scan(b.scope));
    const remaining=finalBanks.length?Core.buildPlan(finalBanks,p.mode,p.tag,questionSelection).actions.length:null;
    const complete=results.complete && remaining===0;
    status(`${results.confirmed.length} alterações confirmadas. ${results.alreadyDesired.length} já estavam no estado escolhido. ${complete?'Operação concluída. Atualize a tabela do AvaliA para ver o resultado.':`Operação parcial. ${results.intermediate?.some(id=>!results.confirmed.includes(id))?'Um like foi retirado, mas o dislike correspondente não foi confirmado. ':''}${results.failed[0]?.message || (remaining?`${remaining} marcações ainda precisam de conferência.`:'Há questões bloqueadas ou a operação foi pausada.')}`}`,!complete);
    if(finalBanks.length)banks=finalBanks;else invalidatePreview();
    renderQuestions();renderPreview();
    window.dispatchEvent(new CustomEvent('smartfox-bank-updated',{detail:{keys:banks.map(b=>`${b.scope.institutionId}:${b.scope.idGrade}:${b.scope.idDisciplina}`)}}));
  }
  async function changeQueue(fn) {
    return locked('smartfox-bank-queue-v11',async()=>{
      const jobs=(await storageGet(QUEUE))||[];
      const result=await fn(jobs);
      await chrome.storage.local.set({[QUEUE]:jobs});return result;
    });
  }
  async function enqueue({runId,questionId,records,expectedOwner}) {
    if(!expectedOwner || expectedOwner!==owner()) throw new Error('Não foi possível vincular a limpeza ao perfil que enviou a questão.');
    if(!/^[1-9]\d*$/.test(String(questionId))) throw new Error('O envio não tem um ID confirmado para agendar a limpeza.');
    const unresolved=!(records||[]).length || (records||[]).some(r=>!(/^[1-9]\d*$/.test(String(r.idGradeDiscipline||''))));
    const targets=[...new Set((records||[]).map(r=>String(r.idGradeDiscipline||'')).filter(v=>/^[1-9]\d*$/.test(v)))];
    const institutionIds=[...new Set((records||[]).map(r=>String(r.institutionId||'')).filter(Boolean))];
    return changeQueue(jobs=>{
      let job=jobs.find(j=>j.runId===runId && j.owner===expectedOwner);
      if(!job) {job={runId,owner:expectedOwner,questionIds:[],targets:[],revision:0,doneRevision:0,assignments:[],institutionIds:[],events:[],status:'pending'};jobs.push(job);}
      if(job.questionIds.includes(String(questionId))) return;
      job.institutionIds=[...new Set([...(job.institutionIds||[]),...institutionIds])];
      job.questionIds.push(String(questionId));job.assignments ||= [];job.assignments.push({questionId:String(questionId),targets,records:structuredClone(records||[])});job.targets=[...new Set([...job.targets,...targets])];job.revision++;job.unresolved ||= unresolved;job.status=job.unresolved?'attention':'pending';
      job.message=!job.unresolved?'Aguardando limpeza do banco.':'A disciplina do envio não expôs o ID. Abra Likes do banco e selecione-a para a limpeza manual.';
      job.updatedAt=new Date().toISOString();
    });
  }
  const scopeLabel=scope=>`${scope.institutionName||'Instituição'} → ${scope.modality} → ${scope.course} → ${scope.grade} → ${scope.name} (disciplina ${scope.idDisciplina}; alocação ${scope.idGradeDisciplina})`;
  const taskSignature=task=>JSON.stringify([task.policy||"legacy",task.scope.key,[...task.questionIds].sort()]);
  async function updateJob(job,fn) {
    return changeQueue(jobs=>{const current=jobs.find(j=>j.owner===job.owner&&j.runId===job.runId);if(current){fn(current);current.updatedAt=new Date().toISOString();}});
  }
  function bankTasks(job,selected,retry) {
    return selected.map(scope=>{
      const assignments=job.assignments||job.questionIds.map(questionId=>({questionId,targets:job.targets}));
      const relevant=assignments.filter(a=>a.targets.some(id=>scope.gradeDisciplineIds.includes(id)));
      for(const a of relevant) for(const r of a.records||[]) {
        if(scope.gradeDisciplineIds.includes(String(r.idGradeDiscipline))&&r.bankScopeKey&&r.bankScopeKey!==scope.key)
          throw new Error('O produto, curso ou grade da alocação mudou desde o envio. Confira o destino antes de continuar.');
      }
      const task={policy:'latest-batch-v1',key:scope.key,scope,questionIds:[...new Set(relevant.map(a=>a.questionId))],status:'pending',message:'Aguardando conferência.'};
      const previous=(job.banks||[]).find(b=>b.key===scope.key&&taskSignature(b)===taskSignature(task));
      return previous?{...previous,scope,...(retry&&previous.status==='attention'?{status:'pending',message:'Nova conferência solicitada.'}:{})}:task;
    });
  }
  async function saveTask(job,task) {
    await updateJob(job,current=>{
      const index=(current.banks||[]).findIndex(b=>b.key===task.key);
      if(index>=0&&taskSignature(current.banks[index])===taskSignature(task))current.banks[index]=structuredClone(task);
    });
    await renderQueue();
  }
  function bankPageMatches(scope) {
    return /^\/AssociarConteudoDisciplina(?:\/|$)/i.test(location.pathname)
      && new URLSearchParams(location.search||'').get('idGradeDisciplina')===scope.idGradeDisciplina;
  }
  async function assertBankPage(scope) {
    // The association page loads its three dependent selectors asynchronously.
    const until=Date.now()+15000;
    while(Date.now()<until) {
      if(!bankPageMatches(scope))throw new Error('A página aberta não corresponde ao código da disciplina do envio.');
      const actual=['idCurso','idGrade','idDisciplina'].map(id=>document.getElementById(id)?.value);
      if(actual.every(v=>/^[1-9]\d*$/.test(String(v||'')))) {
        if(actual.join(':')!==[scope.idCurso,scope.idGrade,scope.idDisciplina].join(':'))throw new Error('O banco aberto tem curso, grade ou disciplina diferente do destino registrado.');
        return;
      }
      if(stopped)throw new Error('Operação pausada.');
      await new Promise(resolve=>setTimeout(resolve,200));
    }
    throw new Error('Os seletores do banco não terminaram de carregar. Retome a limpeza nesta disciplina.');
  }
  function selectNativeProduct(scope) {
    const select=document.querySelector('#filtroModalidade');
    const option=Array.from(select?.options||[]).find(o=>o.value===scope.modalityId);
    if(!option)throw new Error('O produto do envio não está disponível no seletor da tela azul.');
    if(option.selected)return;
    const radio=document.querySelector(`#comboModalidade input[data-name="selectItem"][value="${scope.modalityId}"]`);
    if(!radio)throw new Error('O seletor de produto mudou. Atualize a tela azul antes de retomar.');
    // Native multipleSelect is single-choice here. Its onClick, not a select
    // change event, updates the product and the dependent discipline table.
    document.querySelector('#comboModalidade .ms-choice')?.click();radio.click();
    if(!option.selected||!radio.checked)throw new Error('A troca do produto não foi confirmada pelo seletor do AvaliA.');
  }
  async function prepareBankNavigation(job,task) {
    const onProfessor=/^\/Professor(?:\/|$)/i.test(location.pathname);
    if(onProfessor)selectNativeProduct(task.scope);
    const navigation={owner:job.owner,institutionId:task.scope.institutionId||job.institutionIds[0],institutionName:task.scope.institutionName,
      runId:job.runId,questionIds:job.questionIds,retry:false,at:Date.now(),scope:task.scope,
      stage:onProfessor?'bank':'product',href:onProfessor?`/AssociarConteudoDisciplina/Index?idGradeDisciplina=${task.scope.idGradeDisciplina}`:'/Professor'};
    await chrome.storage.local.set({[NAV]:navigation});return navigation;
  }
  async function drain({retry=false,runId=null,visual=null}={}) {
    const expectedOwner=owner();if(!expectedOwner)return;
    const jobs=((await storageGet(QUEUE))||[]).filter(j=>j.owner===expectedOwner&&(!runId||j.runId===runId)&&j.revision>j.doneRevision&&(j.status==='pending'||retry));
    for(const job of jobs) {
      try {
        if(job.unresolved||!job.targets.length)throw new Error(job.message);
        const institution=selectedInstitution((job.institutionIds||[]).map(institutionId=>({institutionId})));
        const showBanks=visual??Boolean(job.visual);
        const process=async()=>{
          const c=makeClient(expectedOwner,institution),available=await c.discover();
          const selected=matchTargets(available,job.targets);
          const tasks=bankTasks(job,selected,retry);
          await updateJob(job,current=>{current.banks=tasks;current.visual=showBanks;current.institutionIds=[institution.id];current.status='pending';});
          for(const task of tasks) {
            if(task.status==='done'||task.status==='attention')continue;
            const allJobs=(await storageGet(QUEUE))||[];
            const position=allJobs.findIndex(j=>j.runId===job.runId&&j.owner===job.owner);
            const superseded=allJobs.slice(position+1).some(j=>j.owner===job.owner && (j.institutionIds||[]).includes(institution.id) && (j.targets||[]).some(id=>task.scope.gradeDisciplineIds.includes(id)));
            if(superseded){task.status='done';task.message='Há uma remessa mais recente neste banco; esta tarefa não altera seus likes.';await saveTask(job,task);continue;}
            if(stopped)break;
            await authorize(expectedOwner);
            await contextClient(expectedOwner).assertCurrent(institution.id);
            if(showBanks&&!bankPageMatches(task.scope))return {navigation:await prepareBankNavigation({...job,institutionIds:[institution.id]},task)};
            try {
              if(showBanks)await assertBankPage(task.scope);
              task.status='working';task.message='Conferindo o banco inteiro.';await saveTask(job,task);
              if(task.scope.readonly)throw new Error('O AvaliA bloqueia alterações neste banco.');
              const bank=await c.scan(task.scope);
              if(!task.questionIds.length||task.questionIds.some(id=>!bank.questions.some(q=>q.id===id)))
                throw new Error('Este banco não confirmou todos os IDs enviados. Nenhum like será alterado nesta disciplina.');
              status(`Atualizando likes da última remessa: ${scopeLabel(task.scope)}.`);
              const latestPlan=Core.latestBatchPlan(bank,task.questionIds);
              if(latestPlan.blocked.length)throw new Error('O AvaliA bloqueia a atualização de uma ou mais questões desta remessa. Nenhum like foi alterado nesta tentativa.');
              const report=await c.apply(latestPlan,async event=>updateJob(job,current=>current.events.push(event)));
              if(!report.complete)throw new Error(report.failed[0]?.message||'Algumas questões estão bloqueadas pelo AvaliA.');
              const final=Core.latestBatchPlan(await c.scan(task.scope),task.questionIds);
              if(final.actions.length||final.blocked.length)throw new Error('Os likes ainda não correspondem à última remessa. Retome a atualização.');
              task.status='done';task.confirmedAt=new Date().toISOString();task.message='Somente a última remessa com like — conferido no banco.';
            } catch(error) {task.status='attention';task.message=error.message;}
            await saveTask(job,task);
          }
          return {tasks};
        };
        // A visible navigation must remain in the bank institution. Partial work
        // still restores the original form context before its next submission.
        if(showBanks)await contextClient(expectedOwner).assertCurrent(institution.id);
        const result=showBanks?await process():await contextClient(expectedOwner).run(institution.id,process);
        if(result.navigation){await renderQueue();return result;}
        const done=result.tasks.filter(b=>b.status==='done').length,complete=done===result.tasks.length;
        await updateJob(job,current=>{
          if(complete)current.doneRevision=job.revision;
          current.status=current.revision!==job.revision?'pending':complete?'done':'attention';
          current.message=`${done}/${result.tasks.length} bancos conferidos com like somente na última remessa.`+(complete?'':` ${result.tasks.filter(b=>b.status!=='done').map(b=>`Alocação ${b.scope.idGradeDisciplina}: ${b.message}`).join(' ')}`);
        });
        status(`${done}/${result.tasks.length} bancos do envio conferidos com like somente na última remessa.`,!complete);
      } catch(error) {
        await updateJob(job,target=>{target.status='attention';target.message=error.message;});
        status(`Questões enviadas preservadas. Limpeza pendente: ${error.message}`,true);break;
      }
    }
    await renderQueue();
  }
  async function driveCleanup(options) {
    const jobs=(await storageGet(QUEUE))||[];
    const visualJob=jobs.find(j=>j.owner===owner()&&j.visual&&j.revision>j.doneRevision&&(!options?.runId||j.runId===options.runId)&&(j.status==='pending'||options?.retry));
    if(visualJob) {
      const receipt=await finishRun({runId:visualJob.runId,questionIds:visualJob.questionIds,retry:Boolean(options?.retry),navigateToBank:true});
      if(receipt.navigation)navigate(receipt.navigation);
      return receipt;
    }
    const result=await work(()=>drain(options));
    if(result?.navigation)navigate(result.navigation);
    return result;
  }
  async function renderQueue() {
    if(!dialog)return;
    const jobs=((await storageGet(QUEUE))||[]).filter(j=>j.owner===owner());
    const pending=jobs.filter(j=>j.revision>j.doneRevision);
    const shown=pending.length?pending:jobs.slice(-1);
    dialog.querySelector('[data-queue]').innerHTML=shown.length?shown.map(j=>`<section class="sf-bank-job"><strong>${esc(j.message)}</strong><ol>${(j.banks||[]).map(b=>`<li data-bank-state="${esc(b.status)}"><strong>${esc(b.scope.modality)} · ${esc(b.scope.name)}</strong><small>Disciplina ${esc(b.scope.idDisciplina)} · alocação ${esc(b.scope.idGradeDisciplina)} · ${esc(b.scope.course)} · ${esc(b.scope.grade)}</small><span>${esc(b.message)}</span></li>`).join('')}</ol></section>`).join(''):'Sem limpeza pendente para este professor.';
    document.getElementById('sf-bank-launcher')?.classList.toggle('sf-bank-pending',Boolean(pending.length));
  }
  function deletionHelp() {
    // Inspect only explicit visible native controls; never confuse thumbs-down with delete.
    const controls=Array.from(document.querySelectorAll('a,button,input[type="button"]')).filter(e=>!e.closest('#sf-bank-dialog') && e.getClientRects().length && !e.disabled && /^(excluir|apagar|deletar)\s+(a\s+)?quest[aã]o\b/i.test((e.textContent||e.title||e.value||'').trim()));
    if(controls.length===1) {
      dialog.close();controls[0].scrollIntoView({block:'center',behavior:'smooth'});controls[0].focus();
      alert('O comando Excluir questão do AvaliA foi localizado e destacado. Confira o ID e o enunciado e use a confirmação do próprio sistema.');
    } else status(controls.length?'Há mais de uma ação de exclusão. Abra a questão específica antes de continuar.':'O perfil/tela atual não oferece Excluir questão. Cancelar/invalidar e desmarcar like não apagam o registro. Abra a questão no perfil que possui permissão de exclusão.',true);
  }
  function open() {
    if(!dialog) {
      dialog=document.createElement('dialog');dialog.id='sf-bank-dialog';dialog.setAttribute('aria-labelledby','sf-bank-title');
      dialog.innerHTML=`<header><div><small>SMARTFOX 11.0</small><h2 id="sf-bank-title">Likes e dislikes</h2></div><button type="button" data-close aria-label="Fechar">×</button></header>
      <div class="sf-bank-summary"><p data-current-bank></p><p data-status role="status" aria-live="polite">Nenhuma alteração realizada.</p></div>
      <div class="sf-bank-body"><details data-bank-picker open><summary>1. Escolher os bancos <span data-scope-count></span></summary>
      <div class="sf-bank-destination"><label class="sf-bank-field">Instituição<select data-institution></select></label><label class="sf-bank-field">Produto<select data-product><option value="">Todos os produtos</option></select></label></div>
      <div class="sf-bank-actions"><button data-discover>Detectar disciplinas</button><button data-access-institution>Abrir instituição na tela azul</button></div><small>A seleção mantém instituição, produto, curso, grade e código da disciplina.</small>
      <div data-scopes class="sf-bank-scopes"><p>Clique em Detectar disciplinas para listar os bancos desta instituição.</p></div><div class="sf-bank-actions"><button data-all>Selecionar bancos deste filtro</button><button data-none>Limpar seleção de bancos</button><button data-inspect>Conferir bancos selecionados</button></div></details>
      <section data-question-panel><h3>2. Selecionar questões</h3><label class="sf-bank-field">Pesquisar código, nome ou TAG<input type="search" data-question-search placeholder="Ex.: P1 ou código da questão"></label><div class="sf-bank-actions"><button data-question-page>Selecionar esta página</button><button data-question-all>Selecionar todas dos bancos</button><button data-question-none>Desmarcar seleção</button></div><p data-question-count></p><div data-questions class="sf-bank-questions"></div><div class="sf-bank-actions sf-bank-pagination"><button data-question-prev>Anterior</button><button data-question-next>Próxima</button></div></section>
      <section><h3>3. Escolher a operação</h3><label class="sf-bank-field">Operação<select data-mode><option value="all">Retirar likes das selecionadas</option><option value="keep-tag">Retirar likes, preservando uma TAG</option><option value="like-all">Dar like nas selecionadas pendentes</option><option value="like-tag">Dar like nas selecionadas de uma TAG</option><option value="dislike-all">Dar dislike nas selecionadas</option></select></label><label class="sf-bank-field" data-tag-field hidden>TAG da operação<select data-tag><option value="">Confira os bancos primeiro</option></select><small>Comparação pelo nome exato da TAG.</small></label></section>
      <details data-cleanup><summary>Limpeza automática após novos envios</summary><p>Após inserir questões oficiais, o SmartFox retira os likes das questões anteriores e dá like somente às questões da última remessa em cada banco de destino, pelos IDs confirmados. A conclusão depende da conferência no AvaliA. Se houver interrupção, retome a tarefa salva aqui.</p><div data-queue role="status" aria-live="polite"></div><button data-resume>Retomar limpeza pendente</button></details>
      <details><summary>Excluir uma questão</summary><p>Abra a questão desejada. A exclusão usa o comando Excluir e as permissões do próprio AvaliA.</p><button data-delete>Localizar Excluir questão nesta página</button></details></div>
      <div class="sf-bank-footer"><p data-preview class="sf-bank-preview">Confira os bancos para preparar a operação.</p><div class="sf-bank-actions"><button data-apply class="sf-bank-primary" disabled>Aplicar operação</button><button data-stop hidden>Pausar após a ação atual</button></div></div>`;
      document.body.append(dialog);
      const institutions=Context.snapshot(document);
      dialog.querySelector('[data-institution]').innerHTML='<option value="">Selecione a instituição</option>'+institutions.institutions.filter(i=>!i.general).map(i=>`<option value="${esc(i.id)}">${esc(i.name)}</option>`).join('');
      try {dialog.querySelector('[data-institution]').value=Context.choose(institutions).id;}catch{}
      dialog.querySelector('[data-institution]').onchange=()=>{scopes=[];scopeSelection.clear();invalidatePreview();renderScopes();};
      dialog.querySelector('[data-access-institution]').onclick=()=>work(accessInstitution);
      dialog.querySelector('[data-close]').onclick=()=>dialog.close();
      dialog.addEventListener('close',()=>previousFocus?.focus());
      dialog.querySelector('[data-discover]').onclick=()=>work(discover);
      dialog.querySelector('[data-inspect]').onclick=()=>work(inspect);
      dialog.querySelector('[data-apply]').onclick=()=>work(applyManual);
      dialog.querySelector('[data-stop]').onclick=()=>{stopped=true;status('Pausa solicitada. A ação em andamento será conferida.');};
      dialog.querySelector('[data-resume]').onclick=()=>driveCleanup({retry:true});
      dialog.querySelector('[data-delete]').onclick=deletionHelp;
      dialog.querySelector('[data-all]').onclick=()=>{dialog.querySelectorAll('[data-scope]:not(:disabled)').forEach(e=>{e.checked=true;scopeSelection.add(e.dataset.scope);});invalidatePreview();};
      dialog.querySelector('[data-none]').onclick=()=>{scopeSelection.clear();dialog.querySelectorAll('[data-scope]').forEach(e=>e.checked=false);invalidatePreview();};
      dialog.querySelector('[data-product]').onchange=()=>{renderScopes();renderPreview();};
      dialog.querySelector('[data-question-page]').onclick=()=>selectQuestionPage(false);
      dialog.querySelector('[data-question-all]').onclick=()=>selectQuestionPage(true);
      dialog.querySelector('[data-question-none]').onclick=()=>{questionSelection.clear();renderQuestions();renderPreview();};
      dialog.querySelector('[data-question-prev]').onclick=()=>{questionPage--;renderQuestions();};
      dialog.querySelector('[data-question-next]').onclick=()=>{questionPage++;renderQuestions();};
      dialog.querySelector('[data-question-search]').oninput=()=>{questionPage=0;renderQuestions();};
      dialog.querySelector('[data-mode]').onchange=renderPreview;dialog.querySelector('[data-tag]').onchange=renderPreview;
    }
    const state=Context.snapshot(document),contextKey=[owner(),state.current?.id,state.role].join('|');
    if(dialogContext!==contextKey){
      dialogContext=contextKey;scopes=[];scopeSelection.clear();invalidatePreview();
      const field=dialog.querySelector('[data-institution]');
      field.innerHTML='<option value="">Selecione a instituição</option>'+state.institutions.filter(i=>!i.general).map(i=>`<option value="${esc(i.id)}">${esc(i.name)}</option>`).join('');
      try{field.value=Context.choose(state).id;}catch{}
      renderScopes();
    }
    updateControls();previousFocus=document.activeElement;if(!dialog.open) dialog.showModal();renderQueue().catch(e=>status(e.message,true));
  }
  async function openFromPage(){
    const selection=window.SmartFoxBankSelection?.snapshot();
    if(selection){await openQuestionSelection({...selection,questionIds:selection.questionIds.length?selection.questionIds:null});return;}
    open();if(!scopes.length)await work(discover);
  }
  const launcher=document.createElement('button');launcher.id='sf-bank-launcher';launcher.type='button';launcher.textContent='Likes do banco';launcher.onclick=async()=>{try{await authorize(owner());await openFromPage();}catch(error){open();status(error.message,true);}};document.body.append(launcher);
  function matchTargets(available,targets) {
    const matched=[];
    for(const id of targets) {
      const candidates=available.filter(s=>s.gradeDisciplineIds.includes(id));
      if(!candidates.length)throw new Error(`A alocação ${id} escolhida no elaborador não aparece nos bancos do perfil Professor/Tutor desta instituição. Confira a conta, a instituição e a disciplina do envio no AvaliA.`);
      if(candidates.length!==1 || candidates[0].contextAmbiguous) throw new Error('O caminho da disciplina não é único entre os produtos. Confirme o produto, curso e grade no AvaliA.');
      if(!matched.some(s=>s.key===candidates[0].key)) matched.push(candidates[0]);
    }
    return matched;
  }
  async function resolveTargets(records) {
    if(busy)throw new Error('Aguarde a operação de likes terminar antes de confirmar o destino do envio.');
    stopped=false;
    const targets=(records||[]).map(r=>String(r.idGradeDiscipline||''));
    if(!targets.length||targets.some(id=>!(/^[1-9]\d*$/.test(id))))throw new Error('Selecione a disciplina no AvaliA. Seu identificador precisa estar disponível antes de confirmar o produto.');
    await assertContextIdle();
    const institution=selectedInstitution(records),expectedOwner=owner();
    const local=Context.snapshot(document),remote=await contextClient(expectedOwner).read();
    if(local.current?.id!==remote.current?.id||Context.normalize(local.role)!==Context.normalize(remote.role))throw new Error('O contexto do AvaliA mudou em outra aba. Recarregue esta aba antes de enviar.');
    setBusy(true);
    try {return await locked('smartfox-bank-operation-v11',()=>contextClient(expectedOwner).run(institution.id,async()=>matchTargets(await makeClient(expectedOwner,institution).discover(),[...new Set(targets)])));}
    finally {setBusy(false);}
  }
  async function recoverQueuedSession() {
    const session=await storageGet(SESSION);
    if(!session?.bankCleanupEnabled || session.bankCleanupOwner!==owner()) return;
    const ids=[...(session.results||[]).filter(r=>r.status==='official').map(r=>r.id),...(session.items||[]).filter(i=>i.submissionConfirmed).map(i=>i.draftId)];
    for(const questionId of new Set(ids)) if(questionId) {
      const item=(session.items||[]).find(i=>String(i.draftId)===String(questionId));
      await enqueue({runId:session.runId,questionId,records:item?.bankCleanupTargets||session.bankCleanupTargets,expectedOwner:session.bankCleanupOwner});
    }
  }
  async function completion(runId,questionIds=[]) {
    const expectedOwner=owner();
    const job=((await storageGet(QUEUE))||[]).find(j=>j.owner===expectedOwner&&j.runId===runId);
    const missing=questionIds.filter(id=>!job?.questionIds?.includes(String(id)));
    const complete=Boolean(job && job.status==='done' && job.doneRevision===job.revision && !missing.length
      && (!job.banks||job.targets.every(id=>job.banks.some(b=>b.status==='done'&&b.scope.gradeDisciplineIds.includes(id)))));
    return {runId,owner:expectedOwner,complete,revision:job?.revision||0,doneRevision:job?.doneRevision||0,
      questionIds:job?.questionIds||[],institutionIds:job?.institutionIds||[],targetIds:complete?job.targets:[],banks:job?.banks||[],missing,
      message:complete?`Envio e likes da última remessa confirmados em ${job.banks?.length||job.targets.length} banco(s).`:!job?'A retirada obrigatória dos likes ainda não foi registrada.':missing.length?'Faltam questões enviadas na conferência de likes.':job.message||'Retirada obrigatória dos likes pendente.'};
  }
  async function finishRun({runId,questionIds,retry=false,navigateToBank=false}) {
    if(owner())await recoverQueuedSession();
    const job=((await storageGet(QUEUE))||[]).find(j=>j.owner===owner()&&j.runId===runId);
    if(navigateToBank && job && job.revision>job.doneRevision) {
      await updateJob(job,current=>{current.visual=true;});
      const institution=selectedInstitution((job.institutionIds||[]).map(institutionId=>({institutionId})));
      const state=await contextClient(owner()).read();
      if(state.current.id!==institution.id||Context.normalize(state.role)!=='professor/tutor'||!/^\/(Professor|AssociarConteudoDisciplina)(\/|$)/i.test(location.pathname)) {
        const navigation=await navigateInstitution(institution,{runId,questionIds,retry});
        return {...await completion(runId,questionIds),navigation,message:`Questões enviadas. Abrindo Minhas Instituições → ${institution.name} para retirar os likes.`};
      }
    }
    open();if(dialog)dialog.querySelector('[data-cleanup]').open=true;
    const result=await work(()=>drain({runId,retry,visual:navigateToBank||null}));await renderQueue();return {...await completion(runId,questionIds),...(result?.navigation?{navigation:result.navigation}:{})};
  }
  async function resumeNavigation() {
    const intent=await storageGet(NAV);
    if(!intent || intent.owner!==owner() || Date.now()-intent.at>30*60*1000)return false;
    const state=await contextClient(owner()).read();
    if(state.current.id!==intent.institutionId)throw new Error('A troca em Minhas Instituições não foi confirmada. Abra a instituição do envio e retome a retirada dos likes.');
    if(Context.normalize(state.role)!=='professor/tutor') {
      const roles=state.roles.filter(r=>Context.normalize(r.name)==='professor/tutor');
      if(roles.length!==1||intent.stage==='role')throw new Error('O perfil Professor/Tutor não foi confirmado nesta instituição.');
      const next={...intent,stage:'role',href:roles[0].href};await chrome.storage.local.set({[NAV]:next});navigate(next);return true;
    }
    if(intent.stage==='bank'&&!bankPageMatches(intent.scope))throw new Error('A navegação não abriu o código de disciplina esperado. Retome pelo painel Likes do banco.');
    open();
    if(intent.runId&&dialog)dialog.querySelector('[data-cleanup]').open=true;
    const result=intent.runId?await work(()=>drain({runId:intent.runId,retry:intent.retry,visual:true})):await work(discover);
    if(result?.navigation)navigate(result.navigation);
    else await chrome.storage.local.set({[NAV]:null});
    return true;
  }
  window.SmartFoxBankManager=Object.freeze({enqueue,resolveTargets,completion,finishRun,navigate,openQuestionSelection,openFromPage,drain:async()=>{ const jobs=(await storageGet(QUEUE))||[];if(jobs.some(j=>j.owner===owner()&&j.revision>j.doneRevision)){open();await driveCleanup();} },open,owner});
  chrome.runtime?.onMessage?.addListener((message,_sender,sendResponse)=>{
    if(message?.type!=='SF_READ_PAGE_PRODUCTS')return false;
    const state=Context.snapshot(document),products=productsFromPage();
    const matches=owner()===message.owner&&state.current?.id===String(message.institutionId)
      &&Context.normalize(state.role)==='professor/tutor'&&/^\/Professor(?:\/|$)/i.test(location.pathname);
    sendResponse({ok:Boolean(matches&&products.length),data:matches?{owner:owner(),institutionId:state.current.id,products}:null});
    return false;
  });
  // Current runs alone are recoverable; historical sessions are never swept retroactively.
  setTimeout(async()=>{
    try {
      if(await resumeNavigation())return;
      await recoverQueuedSession();
      if (/^\/(Professor|AssociarConteudoDisciplina|Home)(\/|$)/i.test(location.pathname)) {
        const jobs=((await storageGet(QUEUE))||[]).filter(j=>j.owner===owner()&&j.status==='pending'&&j.revision>j.doneRevision);
        if(jobs.length) {open();await driveCleanup();}
      }
    } catch(error) {status(`Limpeza pendente: ${error.message}`,true);}
  },2500);
})();
