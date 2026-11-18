(async function(){
  'use strict';
  if(window.top!==window.self||!/^\/CorrecaoDiscursiva(?:\/|$)/i.test(location.pathname))return;
  if(!window.SmartFoxAccess||!(await window.SmartFoxAccess.requireAuthorized()))return;
  const Engine=window.SmartFoxGradingEngine;
  if(!Engine||document.getElementById('sf-grading-launcher'))return;
  const owner=()=>window.SmartFoxIdentity?.extractAvaliaIdentity(document)?.normalizedName||'';
  const expectedOwner=owner(),historyKey='smartfoxGradingReviewedV2:'+encodeURIComponent(expectedOwner);
  let history=[],journal=[],historyRevision=-1,scanTimer,scanPromise=null,filterRevision=0;
  const journalKey=historyKey+':journal',revisionKey=historyKey+':revision';
  const formScopes=new WeakMap();
  function selected(id){const e=document.getElementById(id);return {id:String(e?.value||''),name:textOf(e?.selectedOptions?.[0]||Array.from(e?.options||[]).find(o=>o.value===e.value))};}
  function filters(){return {institution:selected('sltInstituicao'),assessment:selected('sltAvaliacao'),status:selected('sltStatus'),group:selected('sltAgrupamento'),aiStatus:selected('sltStatusCorrecaoIA')};}
  function filterKey(f){return JSON.stringify([f.institution.id,f.assessment.id,f.status.id,f.group.id,f.aiStatus?.id||'']);}
  let previousFilters=filterKey(filters());
  function checkFilters(){
    const key=filterKey(filters());if(key===previousFilters)return;
    previousFilters=key;filterRevision++;
    for(const panel of document.querySelectorAll('.sf-grading-panel')){
      reviewed(panel);panel.querySelector('[data-note]').value='';panel.querySelector('[data-feedback]').value='';
      for(const field of panel.querySelectorAll('[data-attainment]'))field.value='';
      message(panel,'Instituição, avaliação ou status mudou. Pesquise novamente e abra a resposta nos novos resultados.','warning');
    }
  }
  document.addEventListener('change',e=>{if(e.target.matches?.('#sltInstituicao,#sltAvaliacao,#sltStatus,#sltAgrupamento,#sltStatusCorrecaoIA'))checkFilters();});

  const visible=e=>Boolean(e&&e.isConnected&&e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden');
  
  function textOf(node) {
    return String(node?.innerText || node?.textContent || "").replace(/\u00a0/g, " ").replace(/\s+/g, " ").trim();
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function formId(form) {
    return String(form?.id || "").replace(/^correcao_/, "") || form?.querySelector('input[name="nota"]')?.id?.replace(/^txtNota_/, "") || "desconhecido";
  }

  function activeItem(form) {
    return form?.closest("#questoesItens .item") || form?.closest(".item") || form?.parentElement;
  }

  function sectionNodes(item, startLabel, stopLabel) {
    if (!item) return [];
    const children = Array.from(item.children);
    const start = children.findIndex((node) => /^H[1-6]$/.test(node.tagName) && textOf(node).toLowerCase() === startLabel.toLowerCase());
    if (start < 0) return [];
    const nodes = [];
    for (let index = start + 1; index < children.length; index += 1) {
      const node = children[index];
      if (/^H[1-6]$/.test(node.tagName) && textOf(node).toLowerCase() === stopLabel.toLowerCase()) break;
      if (node.tagName !== "HR") nodes.push(node);
    }
    return nodes;
  }

  function combinedHtml(nodes) {
    return nodes.map((node) => node.outerHTML || node.innerHTML || "").join("\n").trim();
  }

  function readContext(form) {
    const item = activeItem(form);
    const id = formId(form);
    const noteInput = form.querySelector('input[name="nota"], input[id^="txtNota_"]');
    const expectedElement = form.querySelector(`#txtPadrao_${CSS.escape(id)}`) || form.querySelector('[id^="txtPadrao_"]');
    const justificationElement = form.querySelector(`#txtJustificativa_${CSS.escape(id)}`) || form.querySelector('.txtDivJustificativa, [contenteditable="true"]');
    const hiddenJustification = form.querySelector(`#justificativa_${CSS.escape(id)}`) || form.querySelector('input[name="justificativa"]');
    const submitButton = form.querySelector(`#btn_${CSS.escape(id)}`) || form.querySelector('button[type="submit"]');
    const questionNodes = sectionNodes(item, "Questão", "Resposta");
    const responseNodes = sectionNodes(item, "Resposta", "Correção");
    const maxFromInput = Engine.parseScore(noteInput?.max);
    const weightText = Array.from(form.querySelectorAll("span, label, strong"))
      .map(textOf)
      .find((value) => /peso\s*:/i.test(value)) || "";
    const maxFromText = Engine.parseScore(weightText.match(/peso\s*:\s*([\d.,]+)/i)?.[1]);
    const maxScore = maxFromInput ?? maxFromText;
    const header = item?.querySelector(".modal-header");
    const headings = Array.from(header?.querySelectorAll("h4, h5") || []).map(textOf).filter(Boolean);
    return {
      id,
      filters: filters(),
      institutionId: form.querySelector('input[name="idInstituicao"]')?.value || '',
      nativeAnswerId: form.querySelector('input[name="idQuestaoDiscursiva"]')?.value || '',
      sectionsFound: ['Questão','Resposta','Correção'].every(label=>Array.from(item?.children||[]).some(n=>/^H[1-6]$/.test(n.tagName)&&textOf(n).toLowerCase()===label.toLowerCase())),
      mediaAnswer: responseNodes.some(n=>n.matches?.('img,video,audio,object,iframe,embed,canvas,svg,a[href],input[type="file"]')||n.querySelector?.('img,video,audio,object,iframe,embed,canvas,svg,a[href],input[type="file"]')),
      form,
      item,
      noteInput,
      expectedElement,
      justificationElement,
      hiddenJustification,
      submitButton,
      questionHtml: combinedHtml(questionNodes),
      questionText: questionNodes.map(textOf).join(" ").trim(),
      responseHtml: combinedHtml(responseNodes),
      responseText: responseNodes.map(textOf).join(" ").trim(),
      expectedHtml: expectedElement?.innerHTML || "",
      expectedText: textOf(expectedElement),
      maxScore,
      maxFromInput,
      maxFromText,
      maxSource: maxFromInput != null ? "limite do campo" : maxFromText != null ? "texto do peso" : "não identificado",
      weightMismatch: maxFromInput != null && maxFromText != null && Math.abs(maxFromInput - maxFromText) > 1e-9,
      weightText,
      step: noteInput?.step || "0.001",
      assessment: headings[0] || "Avaliação não identificada",
      course: headings[1] || "Turma não identificada"
    };
  }


  function identity(c){return [expectedOwner,filterKey(c.filters),c.institutionId,c.id,c.maxScore,c.questionHtml,c.responseHtml,c.expectedHtml].join('|');}
  function success(c){
    const node=Array.from(c.item?.children||[]).find(e=>e.matches('.panel.panel-success'));
    if(!node?.isConnected||!textOf(node).includes('Correção realizada'))return false;
    // The same answer can be confirmed while its carousel item is off screen.
    // Ignore only the item's visibility; a hidden success placeholder is never confirmation.
    for(let e=node;e&&e!==c.item;e=e.parentElement){
      const style=getComputedStyle(e);
      if(e.hidden||e.style.display==='none'||style.display==='none'||style.visibility==='hidden')return false;
    }
    return true;
  }
  function validateContext(c){
    checkFilters();
    const scope=formScopes.get(c.form);
    if(!scope||scope.revision!==filterRevision||scope.key!==filterKey(c.filters))throw new Error('Os filtros mudaram. Pesquise novamente e reabra a resposta nos novos resultados.');
    if(!/^\d+$/.test(c.filters.institution.id)||!/^\d+$/.test(c.filters.assessment.id)||!/^\d+$/.test(c.filters.status.id))throw new Error('Selecione Instituição, Avaliação e Status antes de corrigir.');
    if(c.filters.institution.id!==c.institutionId)throw new Error('A instituição selecionada difere da instituição da resposta.');

    if(!expectedOwner||owner()!==expectedOwner)throw new Error('O professor mudou. Reabra a correção na conta correta.');
    const current=window.SmartFoxBankContext?.snapshot(document)?.current;
    if(!current||current.general||String(current.id)!==c.institutionId)throw new Error('A instituição da resposta não corresponde ao contexto atual.');
    if(!/^\d+$/.test(c.id)||c.nativeAnswerId!==c.id)throw new Error('O código da resposta não foi confirmado.');
    if(!visible(c.form)||!visible(c.noteInput)||!visible(c.submitButton)||c.submitButton.disabled||c.noteInput.disabled)throw new Error('Abra uma resposta editável pelo Corrigir ou Editar do AvaliA.');
    if(!c.sectionsFound||!c.questionText)throw new Error('Não foi possível separar enunciado, resposta e correção.');
    if(c.weightMismatch)throw new Error('O peso do texto diverge do limite do campo. Confira a configuração no AvaliA.');
    if(new URL(c.form.action,location.origin).origin!==location.origin||new URL(c.form.action,location.origin).pathname!=='/CorrecaoDiscursiva/Modal'||c.form.method.toLowerCase()!=='post')throw new Error('O formulário de correção mudou. Atualize a extensão antes de enviar.');
    if(!c.form.querySelector('input[name="__RequestVerificationToken"]')?.value)throw new Error('A sessão de correção não foi confirmada. Atualize a página.');
  }
  function message(panel,text,tone='neutral'){
    const box=panel.querySelector('[data-message]');box.className='sf-g-message sf-g-'+tone;box.textContent=text;
  }
  function reviewed(panel){panel.querySelector('[data-reviewed]').checked=false;panel._prepared=null;}
  function analyze(context){return Engine.analyzeResponse({questionText:context.questionText,responseText:context.responseText,expectedText:context.expectedText,maxScore:context.maxScore});}
  function refresh(panel){
    const c=readContext(panel._form);panel._identity=identity(c);panel._context=c;reviewed(panel);
    panel.querySelector('[data-scope]').textContent='Instituição: '+c.filters.institution.name+' ('+c.filters.institution.id+') · Avaliação: '+c.filters.assessment.name+' ('+c.filters.assessment.id+') · Status: '+c.filters.status.name+' ('+c.filters.status.id+')';
    const a=analyze(c);
    panel.querySelector('[data-weight]').textContent=c.maxScore==null?'Peso não identificado':Engine.formatScore(c.maxScore,3);
    panel.querySelector('[data-words]').textContent=String(a.metrics.wordCount);
    panel.querySelector('[data-reference]').textContent=c.expectedText||'Confira o padrão original no AvaliA. Sem padrão, a correção será pausada.';
    panel.querySelector('[data-feedback]').value=c.expectedText;
    panel.querySelector('[data-question]').textContent=c.questionText||'Enunciado não identificado.';
    panel.querySelector('[data-response]').textContent=c.responseText|| (c.mediaAnswer?'A resposta contém imagem ou anexo; confira no AvaliA.':'Nenhum texto identificado. Confira a resposta original.');
    panel.querySelector('[data-evidence]').textContent=a.metrics.matchedTerms.length?'Palavras em comum: '+a.metrics.matchedTerms.slice(0,12).join(', ')+'. Isso não determina acerto ou nota.':a.explanation;
    const note=panel.querySelector('[data-note]');note.max=c.maxScore??'';note.step=c.step;
    message(panel,c.weightMismatch?'Pesos divergentes: a correção precisa ser conferida no AvaliA.':'Leia a resposta e defina a nota. A justificativa será o padrão de resposta integral da questão.',c.weightMismatch?'warning':'neutral');
  }
  function rubricKey(c){return 'smartfoxRubricV2:'+encodeURIComponent(expectedOwner)+':'+c.institutionId+':'+Engine.fnv1a([c.questionHtml,c.expectedHtml,c.assessment,c.course].join('|'));}
  function criteria(panel){return Array.from(panel.querySelectorAll('[data-criterion]')).map(row=>({label:row.querySelector('[data-label]').value,weight:row.querySelector('[data-weight-input]').value,attainment:row.querySelector('[data-attainment]').value}));}
  function addCriterion(panel,label='',weight=''){
    const row=document.createElement('div');row.className='sf-g-criterion';row.dataset.criterion='';
    row.innerHTML='<label>Critério<input data-label type="text" maxlength="180"></label><label>Peso %<input data-weight-input type="number" min="1" max="100" step="1"></label><label>Atendimento<select data-attainment><option value="">Avaliar</option><option value="0">Não atendido</option><option value="0.25">25%</option><option value="0.5">50%</option><option value="0.75">75%</option><option value="1">Integral</option></select></label><button type="button" data-action="remove">Remover critério</button>';
    row.querySelector('[data-label]').value=label;row.querySelector('[data-weight-input]').value=weight;
    panel.querySelector('[data-criteria]').append(row);
  }
  function dispatch(element){for(const type of ['input','change','blur'])element.dispatchEvent(new Event(type,{bubbles:true}));}
  function preparedMatches(c,p){return Engine.parseScore(c.noteInput?.value)===p.score&&c.justificationElement?.innerHTML===p.html&&c.hiddenJustification?.value===c.justificationElement?.innerHTML;}
  function copyExpected(c,reference){
    if(!c.expectedElement||c.expectedElement.innerHTML!==reference.feedbackHtml)throw Error('O padrão de resposta mudou. Reanalise a questão.');
    c.justificationElement.replaceChildren(...Array.from(c.expectedElement.childNodes,node=>node.cloneNode(true)));
    dispatch(c.justificationElement);
    c.hiddenJustification.value=c.justificationElement.innerHTML;dispatch(c.hiddenJustification);
    if(c.justificationElement.innerHTML!==reference.feedbackHtml||c.hiddenJustification.value!==reference.feedbackHtml)throw Error('O AvaliA não manteve o padrão de resposta integral na justificativa.');
  }
  async function prepareFields(panel){
    const automatic=window.SmartFoxAutomaticGrading;
    if(automatic&&(automatic.supervisor?.status().mode==='enabled'||automatic.supervisor?.status().busy||['running','pausing'].includes(automatic.runner.status().state)))throw Error('Pause o modo autônomo antes de usar a revisão individual.');
    if(panel._confirmed||panel._uncertain)throw new Error('Reabra a resposta no AvaliA para iniciar outra revisão.');
    const c=readContext(panel._form);validateContext(c);
    if(identity(c)!==panel._identity){refresh(panel);throw new Error('O contexto ou a resposta mudou. Revise novamente.');}
    if(!panel.querySelector('[data-reviewed]').checked)throw new Error('Confirme que revisou a resposta, a nota e o feedback.');
    const score=Engine.validateTeacherScore(panel.querySelector('[data-note]').value,c.maxScore,c.step);
    const reference=window.SmartFoxGradingAutomation.expectedFeedback(c);
    if(!c.justificationElement||!c.hiddenJustification)throw new Error('O campo nativo da justificativa não foi localizado.');
    if(panel._prepared&&!preparedMatches(c,panel._prepared))throw new Error('Os campos nativos mudaram após o preenchimento. Reanalise antes de continuar.');
    c.noteInput.value=String(score);dispatch(c.noteInput);
    copyExpected(c,reference);
    const prepared={score,feedback:reference.feedback,html:reference.feedbackHtml,identity:identity(c)};
    if(!preparedMatches(c,prepared))throw new Error('O AvaliA não manteve os campos preenchidos. Confira a nota e a justificativa.');
    panel._prepared=prepared;
    message(panel,'Nota e feedback preenchidos e conferidos. A correção ainda não foi enviada.','success');
    return {c,prepared};
  }
  async function record(c,prepared,status){
    const audit=prepared.automatic?{automatic:true,rule:prepared.rule,metadata:prepared.metadata,lines:prepared.lines,characters:prepared.characters,outcome:prepared.outcome}:{};
    const entry={at:new Date().toISOString(),answerId:c.id,institutionId:c.institutionId,assessmentId:c.filters.assessment.id,assessmentName:c.filters.assessment.name,filterStatusId:c.filters.status.id,filterStatusName:c.filters.status.name,score:prepared.score,maxScore:c.maxScore,status,...audit,...(prepared.reason?{reason:prepared.reason}:{})};
    const nextHistory=[...history,entry].slice(-10000),nextJournal=[...journal,entry],revision=historyRevision+1;
    const checkpoint=nextJournal.length>=50;
    // Each transition is durable; compact the complete audit only once per 50 transitions.
    await chrome.storage.local.set({[revisionKey]:revision,[journalKey]:checkpoint?[]:nextJournal,...(checkpoint?{[historyKey]:nextHistory}:{})});
    history=nextHistory;journal=checkpoint?[]:nextJournal;historyRevision=revision;
    document.querySelector('#sf-grading-launcher b').textContent=String(history.filter(x=>x.status==='confirmed').length);
  }
  async function reloadHistory(){
    const revision=Number((await chrome.storage.local.get(revisionKey))[revisionKey]||0);
    if(historyRevision===revision)return;
    const stored=await chrome.storage.local.get([historyKey,journalKey,revisionKey]);
    journal=Array.isArray(stored[journalKey])?stored[journalKey]:[];
    history=[...(Array.isArray(stored[historyKey])?stored[historyKey]:[]),...journal].slice(-10000);
    historyRevision=Number(stored[revisionKey]||0);
  }
  function automaticStatus(c){
    if(success(c))return true;
    const last=history.findLast(r=>r.institutionId===c.institutionId&&r.assessmentId===c.filters.assessment.id&&r.answerId===c.id);
    if(last&&['submitting','unconfirmed','rejected'].includes(last.status))throw window.SmartFoxGradingAutomation.itemIssue('Resposta '+c.id+' reservada para conferir o envio anterior. A sequência continua sem reenviá-la.',last.status);
    return success(c)||last?.status==='confirmed';
  }
  async function recordIssue(c,error){
    const last=history.findLast(r=>r.institutionId===c.institutionId&&r.assessmentId===c.filters.assessment.id&&r.answerId===c.id);
    if(last&&(['submitting','unconfirmed','rejected'].includes(last.status)||(last.status==='pending'&&last.reason===error.kind)))return;
    await record(c,{automatic:true,score:null,reason:error.kind},'pending');
  }
  async function submitAutomatic(original,decision,assertRun){
    if(typeof assertRun!=='function'||!window.SmartFoxGradingAutomation)throw Error('Execução automática não inicializada.');
    assertRun();await window.SmartFoxAccess.assertAuthorized({force:true});assertRun();
    const contextClient=window.SmartFoxBankContext.create({fetch:(...args)=>fetch(...args),parseDocument:html=>new DOMParser().parseFromString(html,'text/html'),expectedOwner,normalizeOwner:window.SmartFoxIdentity.normalizePersonName});
    await contextClient.assertCurrent(original.institutionId);await reloadHistory();assertRun();
    const c=readContext(original.form);validateContext(c);
    if(c.filters.status.id!=='1'||identity(c)!==identity(original))throw Error('A resposta ou os filtros mudaram antes da correção automática.');
    if(automaticStatus(c))throw Error('Esta resposta já foi corrigida; não será sobrescrita.');
    const fresh=window.SmartFoxGradingAutomation.decide({...c,discipline:original.discipline},decision.policy);
    if(fresh.score!==decision.score||fresh.feedback!==decision.feedback||fresh.feedbackHtml!==decision.feedbackHtml)throw Error('O critério ou o padrão de resposta mudou antes do envio.');
    const score=Engine.validateTeacherScore(fresh.score,c.maxScore,c.step);
    if(!c.justificationElement||!c.hiddenJustification)throw Error('Campo de feedback não localizado.');
    const panel=Array.from(document.querySelectorAll('.sf-grading-panel')).find(p=>p._form===c.form);
    c.noteInput.scrollIntoView({block:'center',behavior:'instant'});
    c.noteInput.value=String(score);dispatch(c.noteInput);
    copyExpected(c,fresh);
    const prepared={score,feedback:fresh.feedback,html:fresh.feedbackHtml,identity:identity(c),automatic:true,
      lines:fresh.lines,characters:fresh.characters,outcome:fresh.outcome,metadata:fresh.metadata,
      rule:{lineWidth:fresh.policy.lineWidth,minLines:fresh.policy.minLines,shortScore:fresh.policy.shortScore,creditPercent:fresh.policy.creditPercent,feedbackMode:'expected-answer'}};
    if(!preparedMatches(c,prepared))throw Error('O AvaliA não manteve nota e feedback preenchidos.');
    assertRun();validateContext(readContext(c.form));
    // Persist before the native submit. A lost acknowledgement is never retried automatically.
    await record(c,prepared,'submitting');
    let clicked=false;
    try{
      assertRun();const current=readContext(c.form);validateContext(current);
      if(identity(current)!==prepared.identity||!preparedMatches(current,prepared))throw Error('Dados alterados antes do envio.');
      c.submitButton.scrollIntoView({block:'center',behavior:'instant'});
      if(panel)panel._pending=true;clicked=true;c.submitButton.click();
      const deadline=Date.now()+60000;
      while(Date.now()<deadline){
        if(owner()!==expectedOwner)throw Error('O professor mudou durante o envio. Reabra a correção na conta correta.');
        if(success(c)){
          await record(c,prepared,'confirmed');
          if(panel){panel._confirmed=true;message(panel,'Nota e feedback confirmados pelo AvaliA — critério automático de extensão.','success');}
          return;
        }
        const errors=Array.from(c.item.querySelectorAll('.validation-summary-errors,.field-validation-error,.alert-danger')).filter(visible).map(textOf).filter(Boolean);
        if(errors.length){await record(c,prepared,'rejected');clicked=false;throw window.SmartFoxGradingAutomation.itemIssue('O AvaliA recusou esta correção. A resposta foi reservada para conferência.','rejected');}
        if(!document.contains(c.item))break;
        await new Promise(resolve=>setTimeout(resolve,300));
      }
      throw window.SmartFoxGradingAutomation.itemIssue('Envio sem confirmação do AvaliA. Esta resposta fica para conferência; a sequência continua sem repetir o envio.','unconfirmed');
    }catch(error){
      if(clicked){if(panel)panel._uncertain=true;await record(c,prepared,'unconfirmed');}
      else if(history.at(-1)?.status==='submitting')await record(c,prepared,'cancelled');
      throw error;
    }finally{if(panel)panel._pending=false;}
  }
  async function approve(panel){
    if(panel._pending||panel._uncertain)throw new Error('Confira o resultado nativo antes de tentar outra correção.');
    await window.SmartFoxAccess.assertAuthorized({force:true});
    const initial=readContext(panel._form);
    const contextClient=window.SmartFoxBankContext.create({fetch:(...args)=>fetch(...args),parseDocument:html=>new DOMParser().parseFromString(html,'text/html'),expectedOwner,normalizeOwner:window.SmartFoxIdentity.normalizePersonName});
    await contextClient.assertCurrent(initial.institutionId);
    const {c,prepared}=await prepareFields(panel);
    if(success(c))throw new Error('A correção já aparece concluída no AvaliA.');
    if(!confirm('SmartFox 11.0 — confirmar correção\n\nResposta '+c.id+' · instituição '+c.institutionId+'\nAvaliação: '+c.filters.assessment.name+' ('+c.filters.assessment.id+') · Status: '+c.filters.status.name+'\nNota: '+Engine.formatScore(prepared.score,3)+' de '+Engine.formatScore(c.maxScore,3)+'\n\nFeedback: '+prepared.feedback+'\n\nSalvar esta correção no AvaliA?'))return;
    await contextClient.assertCurrent(initial.institutionId);
    validateContext(readContext(panel._form));
    if(identity(readContext(panel._form))!==prepared.identity||!preparedMatches(readContext(panel._form),prepared))throw new Error('Os dados mudaram antes do envio. Revise novamente.');
    panel._pending=true;message(panel,'Aguardando a confirmação do AvaliA…','running');
    try{
      c.submitButton.click();
      const deadline=Date.now()+15000;
      while(Date.now()<deadline){
        if(owner()!==expectedOwner)break;
        if(success(c)){
          await record(c,prepared,'confirmed');panel._confirmed=true;
          message(panel,'Correção confirmada pelo AvaliA.','success');return;
        }
        const errors=Array.from(c.item.querySelectorAll('.validation-summary-errors,.field-validation-error,.alert-danger')).filter(visible).map(textOf).filter(Boolean);
        if(errors.length){message(panel,'O AvaliA informou: '+errors.join(' · '),'danger');await record(c,prepared,'rejected');return;}
        if(!document.contains(c.item))break;
        await new Promise(resolve=>setTimeout(resolve,300));
      }
      panel._uncertain=true;message(panel,'Não foi possível confirmar o envio. Confira o resultado no AvaliA e reabra a resposta; o clique não será repetido.','warning');await record(c,prepared,'unconfirmed');
    }finally{panel._pending=false;}
  }
  function downloadHistory(){
    const blob=new Blob([JSON.stringify({product:'SmartFox 11.0',records:history},null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');
    a.href=url;a.download='SmartFox_Correcoes_Revisadas.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  function createPanel(c){
    const panel=document.createElement('section');panel.className='sf-grading-panel';panel._form=c.form;
    panel.innerHTML=`<header class="sf-g-header"><div class="sf-g-brand"><div><small>SMARTFOX 11.0</small><strong>Corrigir questão discursiva</strong></div></div><span class="sf-g-badge sf-g-neutral">Revisão docente</span></header>
    <div class="sf-g-actions"><button type="button" class="sf-g-primary" data-action="automatic">Retomar correção automática</button></div>
    <div class="sf-g-policy">Este painel é a revisão manual opcional. O modo automático usa os critérios já salvos na lista e dispensa confirmação por questão.</div>
    <div class="sf-g-policy" data-scope></div><div class="sf-g-metrics"><div><span>Peso máximo</span><strong data-weight></strong></div><div><span>Palavras na resposta</span><strong data-words></strong></div></div>
    <details class="sf-g-options"><summary>Enunciado, resposta e padrão</summary><div><b>Enunciado</b><p data-question></p><b>Resposta do estudante</b><p data-response></p><b>Padrão de resposta</b><p data-reference></p></div></details>
    <div class="sf-g-evidence" data-evidence></div>
    <details class="sf-g-options"><summary>Calcular nota por critérios</summary><div><p>Ajuste os critérios ao comando. Os pesos devem somar 100%.</p><div data-criteria></div><button type="button" data-action="add">Adicionar critério</button><button type="button" data-action="calculate">Calcular nota</button><button type="button" data-action="save-criteria">Salvar critérios para esta questão</button></div></details>
    <label class="sf-g-field">Nota atribuída pelo professor<input type="number" min="0" data-note></label>
    <label class="sf-g-field">Justificativa: padrão de resposta da questão<textarea rows="4" readonly data-feedback placeholder="O padrão da questão será copiado integralmente, com a formatação original."></textarea></label>
    <div class="sf-g-actions"><button type="button" data-action="analyze">Reanalisar contexto</button></div>
    <label class="sf-g-review"><input type="checkbox" data-reviewed> Revisei o enunciado, a resposta, a nota e o feedback.</label>
    <div class="sf-g-message sf-g-neutral" data-message role="status" aria-live="polite"></div>
    <div class="sf-g-actions"><button type="button" data-action="fill">Preencher sem enviar</button><button type="button" class="sf-g-primary" data-action="approve">Aprovar e corrigir</button></div>
    <footer><button type="button" data-action="history">Baixar histórico</button><span>O histórico não inclui o texto da resposta.</span></footer>`;
    addCriterion(panel,'Atendimento ao comando',40);addCriterion(panel,'Correção dos conceitos',40);addCriterion(panel,'Justificativa e aplicação',20);
    panel.addEventListener('input',e=>{if(!e.target.matches('[data-reviewed]')){panel._edited=true;reviewed(panel);}});
    panel.addEventListener('change',e=>{if(!e.target.matches('[data-reviewed]')){panel._edited=true;reviewed(panel);}});
    panel.addEventListener('click',async e=>{
      const b=e.target.closest('button[data-action]');if(!b||b.disabled||panel._busy)return;
      const action=b.dataset.action;panel._busy=true;b.disabled=true;
      try{
        if(action==='automatic'){
          const automatic=window.SmartFoxAutomaticGrading;
          if(!automatic)throw Error('O modo automático ainda está carregando. Aguarde o painel R6 na lista de correções.');
          await automatic.supervisor.resume();return;
        }
        if(action==='add'){addCriterion(panel);reviewed(panel);}
        if(action==='remove'){b.closest('[data-criterion]').remove();reviewed(panel);}
        if(action==='save-criteria'){
          const current=readContext(c.form);validateContext(current);if(identity(current)!==panel._identity)throw new Error('Reanalise o contexto antes de salvar critérios.');
          const rows=criteria(panel).map(({label,weight})=>({label,weight}));Engine.rubricScore(rows.map(row=>({...row,attainment:0})),current.maxScore,current.step);
          await chrome.storage.local.set({[rubricKey(current)]:rows});message(panel,'Critérios salvos para este enunciado e contexto. O atendimento será avaliado novamente em cada resposta.');
        }
        if(action==='calculate'){
          const current=readContext(c.form);if(identity(current)!==panel._identity)throw new Error('O contexto mudou. Reanalise a resposta.');
          panel.querySelector('[data-note]').value=String(Engine.rubricScore(criteria(panel),current.maxScore,current.step));reviewed(panel);
          message(panel,'Nota calculada pelos critérios que você avaliou. Revise o feedback antes de preencher.');
        }
        if(action==='analyze')refresh(panel);
        if(action==='fill')await prepareFields(panel);
        if(action==='approve')await approve(panel);
        if(action==='history')downloadHistory();
      }catch(error){message(panel,error.message||String(error),'danger');}
      finally{panel._busy=false;b.disabled=Boolean(panel._confirmed||panel._uncertain)&&['fill','approve'].includes(action);}
    });
    refresh(panel);return panel;
  }
  async function scan(){
    checkFilters();if(scanPromise)return scanPromise;
    scanPromise=(async()=>{for(const form of document.querySelectorAll('#questoesItens .item.active form[id^="correcao_"]')){
      if(!visible(form))continue;
      const c=readContext(form);if(!c.noteInput||!c.item)continue;
      if(!formScopes.has(form))formScopes.set(form,{revision:filterRevision,key:filterKey(c.filters)});
      const mode=window.SmartFoxAutomaticGrading?.supervisor.status();
      if(mode&&(mode.mode==='enabled'||mode.busy))continue;
      if(form.dataset.sfGradingMounted==='true')continue;
      form.dataset.sfGradingMounted='true';const panel=createPanel(c);form.before(panel);
      const key=rubricKey(c),saved=(await chrome.storage.local.get(key))[key];
      if(Array.isArray(saved)&&saved.length&&identity(readContext(form))===panel._identity&&!panel._busy&&!panel._edited){
        panel.querySelector('[data-criteria]').replaceChildren();for(const row of saved)addCriterion(panel,row.label,row.weight);
      }
    }})();
    try{await scanPromise;}finally{scanPromise=null;}
  }
  await reloadHistory();
  const launcher=document.createElement('button');launcher.type='button';launcher.id='sf-grading-launcher';launcher.innerHTML='<em>Corrigir discursivas</em><b>'+history.filter(x=>x.status==='confirmed').length+'</b>';
  launcher.onclick=()=>{const panel=Array.from(document.querySelectorAll('.sf-grading-panel')).find(visible);if(panel)panel.scrollIntoView({block:'center',behavior:'smooth'});else alert('Escolha a avaliação e clique em Pesquisar. Abra Corrigir; em respostas concluídas, use Editar para habilitar o assistente.');};document.documentElement.append(launcher);
  new MutationObserver(records=>{if(records.every(r=>r.target.closest?.('.sf-grading-panel,#sf-grading-launcher,#sf-auto-grading,#sf-auto-dock')))return;clearTimeout(scanTimer);scanTimer=setTimeout(()=>scan().catch(()=>{}),100);}).observe(document.body,{childList:true,subtree:true,attributes:true,attributeFilter:['class','style']});
  window.SmartFoxGradingAssistant=Object.freeze({version:'11.0',readContext,analyze,prepareFields,scan,filters,filterKey,owner,expectedOwner,validateContext,automaticStatus,submitAutomatic,recordIssue,reloadHistory,downloadHistory,getHistory:()=>history.slice()});
  window.dispatchEvent(new Event('smartfox-grading-ready'));
  await scan();
})();
