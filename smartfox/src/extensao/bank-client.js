/* SmartFox 11.0 — contrato do banco conferido na interface Professor do AvaliA.
 * O dislike usa o formulário nativo de cancelamento. Não exclui questões.
 */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.SmartFoxBankClient = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const PAGE_SIZE = 100;
  const normalize = value => String(value ?? '').normalize('NFC').replace(/\s+/g, ' ').trim().toLocaleLowerCase('pt-BR');
  const id = value => { const result = String(value ?? ''); if (!/^[1-9]\d*$/.test(result)) throw new Error('Identificador do AvaliA ausente ou inválido.'); return result; };
  const bankKey = scope => `${id(scope.idGrade)}:${id(scope.idDisciplina)}`;
  const scopeKey = scope => `${scope.institutionId?id(scope.institutionId)+":" : ""}${id(scope.modalityId)}:${id(scope.idCurso)}:${bankKey(scope)}:${id(scope.idGradeDisciplina)}`;
  const questionKey = (scope,questionId) => `${scope.key||scopeKey(scope)}/${id(questionId)}`;
  const DISLIKE_DESCRIPTION = 'não gostei da questão';
  const flag = value => value === true || value === 1 || value === 'true';
  const falseFlag = value => value === false || value === 0 || value === 'false';
  const summaryColumns = ['nomeCurso','nomeGrade','periodo','nomeDisciplina','cargaHoraria','numeroMatriculas','quantidadeDisciplinaEquivalente','minimoAssociadoRecomendado','quantidadeConteudosAssociados','quantidadeQuestaoValidada','quantidadeQuestaoInvalidada','quantidadeQuestaoAAvaliar','quantidadeQuestaoTotal'];
  const questionColumns = ['idQuestao','nome','tipoQuestao','palavrasChave','tags','dificuldade','fonte','complementoFonte','situacao','idDisciplinaQuestao'];
  function cleanProducts(list) {
    const found=new Map();
    for(const item of Array.isArray(list)?list:[]) {
      const productId=String(item?.value||item?.id||'').trim(),label=String(item?.label||item?.textContent||item?.text||'').replace(/\s+/g,' ').trim();
      if(/^[1-9]\d*$/.test(productId)&&label&&!found.has(productId))found.set(productId,{id:productId,label});
    }
    return [...found.values()];
  }
  function productsFromDocument(doc) {
    const options=Array.from(doc.querySelectorAll?.('#filtroModalidade option')||[]);
    // HTMLOptionElement.id is normally an empty string, not undefined. The
    // product code is value; using id ?? value silently discards every option.
    const products=cleanProducts(options.map(option=>({id:option.value,label:option.textContent})));
    if(products.length)return products;
    return cleanProducts(Array.from(doc.querySelectorAll?.('#comboModalidade input[data-name="selectItem"]')||[]).map(input=>({
      value:input.value,label:input.closest?.('li')?.textContent||input.getAttribute?.('data-label')||''
    })));
  }
  async function readRenderedProducts({document:doc,origin,institutionId,expectedOwner,snapshot,normalizeOwner,shouldStop=()=>false,timeoutMs=20000,intervalMs=150}) {
    // This is an ordinary same-origin page load, never an injected script or
    // a write to AvaliA. Extension scripts run only in the top frame.
    const frame=doc.createElement('iframe');
    frame.hidden=true;frame.tabIndex=-1;frame.setAttribute('aria-hidden','true');
    frame.setAttribute('title','Conferência dos produtos do AvaliA');
    frame.setAttribute('sandbox','allow-scripts allow-same-origin');
    frame.src=new URL('/Professor',origin).href;
    let timer,deadline;
    try {
      return await new Promise((resolve,reject)=>{
        let settled=false;
        const finish=(error,value)=>{if(settled)return;settled=true;clearTimeout(timer);clearTimeout(deadline);error?reject(error):resolve(value);};
        const inspect=()=>{
          if(settled)return;
          try {
            if(shouldStop())throw new Error('Conferência dos produtos interrompida. O lote permanece salvo.');
            const href=frame.contentWindow?.location?.href;
            if(href&&href!=='about:blank') {
              const url=new URL(href);
              if(url.origin!==origin||!/^\/Professor(?:\/Index)?\/?$/i.test(url.pathname))throw new Error('A consulta dos produtos abriu outra página. Confira a sessão e o perfil Professor/Tutor no AvaliA.');
              const page=frame.contentDocument,state=page&&snapshot(page);
              if(state?.owner&&normalizeOwner(state.owner)!==normalizeOwner(expectedOwner))throw new Error('O professor mudou durante a conferência dos produtos.');
              if(state?.current&&String(state.current.id)!==String(institutionId))throw new Error('A instituição mudou durante a conferência dos produtos.');
              if(state?.role&&String(state.role).normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/\s+/g,'').toLowerCase()!=='professor/tutor')throw new Error('O perfil Professor/Tutor não foi confirmado na leitura dos produtos.');
              const products=page?productsFromDocument(page):[];
              if(products.length&&state?.current&&state?.owner&&state?.role) {finish(null,products);return;}
            }
          } catch(error) {finish(error);return;}
          timer=setTimeout(inspect,intervalMs);
        };
        deadline=setTimeout(()=>finish(new Error('A página de produtos não terminou de carregar. Abra a tela azul na instituição escolhida e tente iniciar novamente; o lote continua salvo.')),timeoutMs);
        frame.onerror=()=>finish(new Error('O AvaliA não permitiu carregar a página de produtos em segundo plano. Abra a tela azul na mesma instituição e tente iniciar novamente.'));
        doc.body.append(frame);inspect();
      });
    } finally {clearTimeout(timer);clearTimeout(deadline);frame.remove();}
  }
  function tableParams(columns, start) {
    const p = new URLSearchParams({draw:'1',start:String(start),length:String(PAGE_SIZE),'search[value]':'','search[regex]':'false','order[0][column]':'0','order[0][dir]':'asc'});
    columns.forEach((name,i) => { p.set(`columns[${i}][data]`,name); p.set(`columns[${i}][name]`,name[0].toUpperCase()+name.slice(1)); p.set(`columns[${i}][searchable]`,'true'); p.set(`columns[${i}][orderable]`,'true'); p.set(`columns[${i}][search][value]`,''); p.set(`columns[${i}][search][regex]`,'false'); });
    return p;
  }
  function pageData(payload) {
    if (!payload || !Array.isArray(payload.data) || payload.error) throw new Error('O AvaliA não devolveu a listagem esperada. Confira o perfil e a sessão.');
    const total = Number(payload.recordsFiltered);
    if (!Number.isSafeInteger(total) || total < 0) throw new Error('A contagem total do banco não foi confirmada.');
    return { rows:payload.data, total };
  }
  async function allPages(readPage, keyOf, onPage) {
    const rows = [], keys = new Set(); let total = null;
    for (let start=0; ; ) {
      const page = pageData(await readPage(start));
      if (total !== null && total !== page.total) throw new Error('A listagem mudou durante a leitura. Atualize a prévia antes de continuar.');
      total = page.total;
      if (total > 100000) throw new Error('Banco excede o limite de leitura desta operação. Divida a seleção de disciplinas.');
      if (rows.length + page.rows.length > total || (!page.rows.length && rows.length < total)) throw new Error('Listagem incompleta: uma página não foi recebida.');
      for (const row of page.rows) {
        const key = keyOf(row);
        if (keys.has(key)) throw new Error('A paginação repetiu um registro. Nenhuma limpeza deve começar com esta leitura.');
        keys.add(key); rows.push(row);
      }
      onPage?.(rows.length,total);
      if (rows.length === total) return rows;
      start += page.rows.length;
    }
  }
  function question(row, parseTags) {
    const state = normalize(row.situacao);
    if (!['validada','pendente','desativada'].includes(state)) throw new Error(`Estado não reconhecido na questão ${row.idQuestao}.`);
    return { id:id(row.idQuestao), name:String(row.nome || ''), state,
      readonly:flag(row.somenteLeitura) || flag(row.SomenteLeitura), tags:parseTags(row.tags), raw:row };
  }
  function buildPlan(banks, mode='all', tag='', selectedKeys=null) {
    if (!['all','keep-tag','like-all','like-tag','dislike-all'].includes(mode)) throw new Error('Escolha uma operação de likes válida.');
    const selected=normalize(tag), adding=mode.startsWith('like-'), disliking=mode==='dislike-all';
    const selection=selectedKeys===null?null:new Set(selectedKeys);
    if (['keep-tag','like-tag'].includes(mode) && !selected) throw new Error('Escolha a TAG da operação.');
    const actions=[],preserved=[],blocked=[];let total=0,unliked=0;
    for (const bank of banks) {
      if (!bank.complete || bank.unavailable) throw new Error('Conclua a leitura dos bancos selecionados e confira as permissões.');
      for (let index=0;index<bank.questions.length;index++) {
        const q=bank.questions[index];
        if(selection&&!selection.has(questionKey(bank.scope,q.id)))continue;
        total++;
        const matches=q.tags.some(t=>normalize(t)===selected);
        if ((mode==='keep-tag' && matches) || (mode==='like-tag' && !matches)) { if(q.state==='validada') preserved.push(q.id);else unliked++;continue; }
        if (adding && q.state==='validada') {preserved.push(q.id);continue;}
        if (disliking && q.state==='desativada') {unliked++;continue;}
        if (!adding && !disliking && q.state!=='validada') {unliked++;continue;}
        if (bank.scope.readonly || q.readonly || (adding && q.state==='desativada')) {blocked.push({scope:bank.scope,id:q.id});continue;}
        actions.push({scope:bank.scope,id:q.id,name:q.name,index,total:bank.questions.length,desired:disliking?'desativada':adding?'validada':'pendente',type:disliking?'desativar':adding?'validar':'voltarPadrao',wasLiked:q.state==='validada'});
      }
    }
    return {mode,tag:String(tag),adding,disliking,actions,preserved,blocked,total,unliked,createdAt:Date.now()};
  }
  function latestBatchPlan(bank, ids) {
    const latest = new Set(ids.map(String));
    if (!latest.size || [...latest].some(id => !bank.questions.some(q => q.id === id)))
      throw new Error('O banco não confirmou todos os IDs da última remessa.');
    const older = bank.questions.filter(q => !latest.has(q.id)).map(q => questionKey(bank.scope,q.id));
    const recent = bank.questions.filter(q => latest.has(q.id)).map(q => questionKey(bank.scope,q.id));
    const remove = buildPlan([bank], 'all', '', older);
    const add = buildPlan([bank], 'like-all', '', recent);
    return {...remove, mode:'latest-batch', actions:[...remove.actions,...add.actions], blocked:[...remove.blocked,...add.blocked]};
  }
  function createClient({fetch:send,parseDocument,parseTags,authorize,onProgress=()=>{},shouldStop=()=>false,institution=null,initialProducts=[],loadProducts=null}) {
    let verifying=false, products=[];
    function checkStop() { if(shouldStop() && !verifying) throw new Error('Operação pausada. As alterações já confirmadas foram preservadas.'); }
    async function request(path, params, method='POST', kind='json') {
      checkStop();
      const controller=new AbortController(), timer=setTimeout(()=>controller.abort(),25000);
      const suffix=method==='GET' && params ? '?'+params.toString() : '';
      try {
        const response=await send(path+suffix,{method,credentials:'same-origin',cache:'no-store',redirect:'error',headers:{...(kind==='page'?{}:{'X-Requested-With':'XMLHttpRequest'}),...(method==='POST'?{'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'}:{})},...(method==='POST'?{body:params.toString()}:{}),signal:controller.signal});
        if (!response.ok) throw new Error(`AvaliA HTTP ${response.status}. A operação ficou pendente; verifique a sessão e as permissões.`);
        if (kind==='text'||kind==='page') return response.text();
        return await response.json();
      } catch (error) {
        if (error.name==='AbortError') throw new Error('O AvaliA demorou a responder. A ação não será repetida automaticamente.');
        throw error;
      } finally { clearTimeout(timer); }
    }
    async function discover() {
      await authorize();
      let remoteProducts=[],productError='';
      try {
        const html=await request('/Professor',null,'GET','page');
        const doc=parseDocument(html);
        remoteProducts=productsFromDocument(doc);
      } catch(error) {
        productError=error.message;
        onProgress(`A lista geral do AvaliA não respondeu; usando os produtos já carregados nesta tela. ${error.message}`);
      }
      // The live Professor page is authoritative. In some AvaliA sessions a
      // background GET /Professor returns a fragment without #filtroModalidade,
      // even though the native selector is visible and fully populated.
      let modalities=cleanProducts([...cleanProducts(initialProducts),...remoteProducts]);
      if(!modalities.length&&loadProducts) {
        onProgress('Consultando os produtos na página carregada do AvaliA…');
        modalities=cleanProducts(await loadProducts());
      }
      if (!modalities.length) throw new Error(`O AvaliA não carregou os produtos da instituição. O lote permanece salvo.${productError?' Consulta: '+productError:' A resposta não contém o seletor de produtos.'}`);
      await authorize();
      products=modalities.map(m=>({...m,count:0}));
      const scopes=new Map();
      for (const modality of modalities) {
        onProgress(`Detectando disciplinas: ${modality.label}…`);
        const rows=await allPages(start=>{
          const p=tableParams(summaryColumns,start);
          p.set('modalidade',modality.id); p.set('idGestao','0'); p.set('apenasDisciplinasComMatriculas','false');
          return request('/GradeDisciplinaGerenciamento/TabelaResumoData',p);
        },r=>`${bankKey(r)}:${id(r.idGradeDisciplina)}`);
        products.find(p=>p.id===modality.id).count=rows.length;
        for(const row of rows) {
          const key=scopeKey({...row,modalityId:modality.id,institutionId:institution?.id});
          const readonly=falseFlag(row.liberadoAlteracao) || (flag(row.disciplinaInstitucional) && ![15,57].includes(Number(row.idPapel)));
          const scope={key,...(institution?{institutionId:institution.id,institutionName:institution.name}:{}),modalityId:modality.id,idCurso:id(row.idCurso),idGradeDisciplina:id(row.idGradeDisciplina),idGrade:id(row.idGrade),idDisciplina:id(row.idDisciplina),gradeDisciplineIds:[id(row.idGradeDisciplina)],name:String(row.nomeDisciplina||''),course:String(row.nomeCurso||''),grade:String(row.nomeGrade||''),modality:modality.label,readonly};
          if (!scope.name || !scope.grade) throw new Error('Disciplina sem identificação completa. Atualize a listagem.');
          if (scopes.has(key)) {
            const old=scopes.get(key); old.gradeDisciplineIds=Array.from(new Set([...old.gradeDisciplineIds,...scope.gradeDisciplineIds])); old.readonly ||= readonly;
          } else scopes.set(key,scope);
        }
      }
      const values=[...scopes.values()];
      // Native like routes accept Grade + Discipline only. Never pretend an
      // operation can isolate products if the server exposes the same bank key.
      for(const scope of values) {
        scope.contextAmbiguous=values.some(other=>other.key!==scope.key && bankKey(other)===bankKey(scope));
        if(scope.contextAmbiguous) scope.readonly=true;
      }
      return values;
    }
    function readPage(scope,start) {
      scopeKey(scope);
      const p=tableParams(questionColumns,start);
      p.set('idGrade',scope.idGrade);p.set('idDisciplina',scope.idDisciplina);
      // The native form uses a scalar search and absent arrays to mean no filter.
      p.delete('search[value]');p.delete('search[regex]');p.set('search','');
      return request('/DisciplinaQuestao/Tabela',p);
    }
    async function scan(scope) {
      await authorize();
      if (scope.readonly) return {scope,complete:true,questions:[],unavailable:true};
      const rows=await allPages(start=>readPage(scope,start),r=>id(r.idQuestao),(read,total)=>onProgress(`${scope.name}: ${read} de ${total} questões lidas.`));
      return {scope,complete:true,questions:rows.map(row=>question(row,parseTags))};
    }
    async function findCurrent(action) {
      const start=Math.floor(action.index/PAGE_SIZE)*PAGE_SIZE;
      const page=pageData(await readPage(action.scope,start));
      let row=page.rows.find(r=>String(r.idQuestao)===action.id);
      if (!row) {
        const bank=await scan(action.scope);
        return bank.questions.find(q=>q.id===action.id) || null;
      }
      return question(row,parseTags);
    }
    async function dislikeForm(action) {
      const query=new URLSearchParams({idQuestao:id(action.id),idGrade:id(action.scope.idGrade),idDisciplina:id(action.scope.idDisciplina)});
      const doc=parseDocument(await request('/DisciplinaQuestao/Desativar',query,'GET','text'));
      const form=doc.querySelector('form[action="/DisciplinaQuestao/DesativarQuestaoDisciplina"]');
      if(!form||String(form.getAttribute('method')).toLowerCase()!=='post')throw new Error('O formulário de dislike do AvaliA não foi reconhecido. Nenhuma justificativa foi enviada.');
      const options=Array.from(form.querySelectorAll('select[name="idTipo"] option'));
      const reasons=options.filter(o=>['questão com erro','problema na questão'].includes(normalize(o.textContent)));
      if(reasons.length!==1||!(/^[1-9]\d*$/.test(reasons[0].value)))throw new Error('O AvaliA não oferece um motivo único equivalente a Questão com erro.');
      const token=form.querySelector('input[name="__RequestVerificationToken"]')?.value;
      if(!token||!form.querySelector('textarea[name="descricao"]'))throw new Error('A confirmação do formulário de dislike está incompleta. Atualize a página.');
      const p=new URLSearchParams();
      for(const [name,value] of Object.entries({IdQuestao:action.id,IdGrade:action.scope.idGrade,IdDisciplina:action.scope.idDisciplina})) {
        const field=form.querySelector(`input[name="${name}"]`);
        // The inspected native form leaves these fields empty. Fill them only
        // from the bank and question already verified, never from the name.
        if(!field||(field.value&&String(field.value)!==String(value)))throw new Error('O formulário de dislike corresponde a outro banco ou questão.');
        p.set(name,id(value));
      }
      p.set('idTipo',reasons[0].value);p.set('descricao',DISLIKE_DESCRIPTION);p.set('__RequestVerificationToken',token);
      return p;
    }
    async function transition(action,path,params,method,desired) {
      let response,transportError;
      try{response=await request(path,params,method);}catch(error){transportError=error;}
      let after;verifying=true;
      try{after=await findCurrent(action);}finally{verifying=false;}
      if(after?.state!==desired)throw new Error(transportError?.message||'O AvaliA não confirmou a alteração desta questão no banco.');
      return response;
    }
    async function apply(plan,onResult=async()=>{}) {
      await authorize();
      const report={confirmed:[],alreadyDesired:[],preserved:[],blocked:[],failed:[],intermediate:[],complete:false};
      for(const action of plan.actions) {
        try {
          await authorize();
          const current=await findCurrent(action);
          if (!current) throw new Error(`Questão ${action.id} não consta mais no banco. Refaça a prévia.`);
          if (current.state===action.desired || (action.desired==='pendente' && current.state==='desativada')) { report.alreadyDesired.push(action.id); continue; }
          if (current.readonly || action.scope.readonly || current.state==='desativada') { report.blocked.push(action.id); continue; }
          if((plan.mode==='keep-tag' && current.tags.some(t=>normalize(t)===normalize(plan.tag))) || (plan.mode==='like-tag' && !current.tags.some(t=>normalize(t)===normalize(plan.tag)))) { report.preserved.push(action.id); continue; }
          checkStop();
          if(plan.disliking) {
            const payload=await dislikeForm(action);
            await authorize();
            const fresh=await findCurrent(action);
            if(!fresh)throw new Error('A questão deixou de constar no banco.');
            if(fresh.state==='desativada'){report.alreadyDesired.push(action.id);continue;}
            if(fresh.readonly){report.blocked.push(action.id);continue;}
            if(fresh.state==='validada') {
              await transition(action,'/DisciplinaQuestao/Validacao',new URLSearchParams({idQuestao:action.id,tipo:'voltarPadrao',idGrade:action.scope.idGrade,idDisciplina:action.scope.idDisciplina}),'GET','pendente');
              report.intermediate.push(action.id);
              await onResult({id:action.id,scope:action.scope,state:'pendente',kind:'preparação-do-dislike',at:new Date().toISOString()});
            }
            await authorize();checkStop();onProgress(`${action.scope.name}: dando dislike na questão ${action.id}…`);
            await transition(action,'/DisciplinaQuestao/DesativarQuestaoDisciplina',payload,'POST','desativada');
          } else {
            onProgress(`${action.scope.name}: ${action.desired==='validada'?'aprovando':'desmarcando'} a questão ${action.id}…`);
            const params=new URLSearchParams({idQuestao:action.id,tipo:action.type,idGrade:action.scope.idGrade,idDisciplina:action.scope.idDisciplina});
            await transition(action,'/DisciplinaQuestao/Validacao',params,'GET',action.desired);
          }
          report.confirmed.push(action.id);
          await onResult({id:action.id,scope:action.scope,state:action.desired,...(plan.disliking?{reason:'Questão com erro',description:DISLIKE_DESCRIPTION}:{}),at:new Date().toISOString()});

        } catch(error) { report.failed.push({id:action.id,scope:action.scope.key,message:error.message}); break; }
      }
      report.complete=!report.failed.length && !report.blocked.length && !plan.blocked.length;
      return report;
    }
    return {discover,scan,apply,findCurrent,products:()=>products.map(p=>({...p}))};
  }
  return Object.freeze({latestBatchPlan,normalize,scopeKey,questionKey,pageData,allPages,buildPlan,createClient,productsFromDocument,readRenderedProducts,PAGE_SIZE,DISLIKE_DESCRIPTION});
});
