(async function(){
  'use strict';
  if(window.top!==window.self||document.getElementById('sf-tools-launcher'))return;
  if(!window.SmartFoxAccess||!(await window.SmartFoxAccess.requireAuthorized()))return;
  const Context=window.SmartFoxBankContext;if(!Context)return;
  const owner=()=>window.SmartFoxIdentity?.extractAvaliaIdentity(document)?.normalizedName||'';
  const routes=[
    ['/AssociarConteudoDisciplina/Index','Associar conteúdos e questões'],
    ['/AcompanhamentoAvaliacao/Index','Dashboard de aplicações'],
    ['/CorrecaoDiscursiva/Index','Corrigir questões discursivas'],
    ['/AnalisarRecurso/Index','Análise de recursos'],
    ['/AvaliacaoRelatorio/Index/2','Exportação de notas por disciplina'],
    ['/ResultadoRespostasAlunos/Index','Análise de desempenho'],
    ['/AvaliacaoRelatorio/Index/3','Mapeamento de resultados'],
    ['/AcompanhamentoAdesao/Index','Adesão em avaliação'],
    ['/AcompanhamentoNota/PesquisaAluno','Acompanhamento individual'],
    ['/VisualizarQuestoesAluno/Index','Visualizar avaliações'],
    ['/Documentacao/Index','Arquivos e manuais'],
    ['/Elaborador/FonteExterna','Questões IES']
  ];
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const navigationKey='smartfox-navigation-v11';
  let busy=false,previousFocus;
  function pageMode(){
    const state=Context.snapshot(document),role=Context.normalize(state.role);
    if(role==='professor/tutor')return 'Tela azul · Professor/Tutor';
    if(role==='elaborador')return 'Elaborador';
    return 'Perfil ainda não identificado';
  }
  function nativeLinks(){
    const unique=new Map();
    for(const a of document.querySelectorAll('a[href]')){
      if(a.closest('#sf-tools-dialog'))continue;
      const raw=a.getAttribute('href')||'';
      const known=routes.find(r=>r[0]===raw);
      // Additional native menu pages only; never create action URLs or infer permissions.
      const extra=/^\/(?:Contrato\/Index\/\d+|Pessoa\/CadastroCompleto\/\d+|Elaborador\/Tema\/\d+|Dirf\/Index|Documentacao\/Index)\/?$/.test(raw);
      if(!known&&!extra)continue;
      unique.set(raw,known?.[1]||a.textContent.replace(/[\uE000-\uF8FF]/g,'').trim());
    }
    return [...unique];
  }

  const filterCatalog=[['sltInstituicao','Instituição'],['filtroModalidade','Produto'],['filtroCurso','Curso'],['filtroGrade','Grade'],['filtroPeriodo','Período'],['filtroDisciplina','Disciplina'],['idCurso','Curso da alocação'],['idGrade','Grade da alocação'],['idDisciplina','Disciplina da alocação'],['sltAvaliacao','Avaliação'],['sltStatus','Status'],['sltAgrupamento','Agrupamento'],['Questao_IdTipoQuestao','Tipo de questão'],['IdHabilidadeQuestao','Nível cognitivo']];
  let latestScan;
  function nativeProducts(){
    const products=new Map();
    for(const option of document.querySelectorAll('#filtroModalidade option')){
      const value=String(option.value||'').trim(),label=String(option.textContent||'').replace(/\s+/g,' ').trim();
      if(value&&label)products.set(value,{value,label,selected:Boolean(option.selected)});
    }
    for(const input of document.querySelectorAll('#comboModalidade input[data-name="selectItem"]')){
      const value=String(input.value||'').trim(),label=String(input.closest('li')?.textContent||'').replace(/\s+/g,' ').trim();
      if(value&&label&&!products.has(value))products.set(value,{value,label,selected:Boolean(input.checked)});
    }
    return [...products.values()];
  }
  function visibleDisciplineRows(){
    const rows=[];
    for(const row of document.querySelectorAll('table tbody tr')){
      const bankLink=Array.from(row.querySelectorAll('a[data-load-url]')).find(a=>/^\/DisciplinaQuestao\/Index/.test(a.getAttribute('data-load-url')||''));
      const allocation=Array.from(row.querySelectorAll('a[href]')).find(a=>/^\/AssociarConteudoDisciplina\/Index\?idGradeDisciplina=/.test(a.getAttribute('href')||''));
      if(!bankLink&&!allocation)continue;
      const queryValue=(value,name)=>{const match=String(value||'').match(new RegExp(`[?&]${name}=([^&#]+)`,'i'));try{return match?decodeURIComponent(match[1]):'';}catch{return '';}};
      const bankPath=bankLink?.getAttribute('data-load-url')||'',allocationPath=allocation?.getAttribute('href')||'';
      const cells=Array.from(row.cells||[]).map(cell=>String(cell.textContent||'').replace(/\s+/g,' ').trim());
      const record={idGrade:queryValue(bankPath,'idGrade'),idDisciplina:queryValue(bankPath,'idDisciplina'),idGradeDisciplina:queryValue(allocationPath,'idGradeDisciplina'),name:String(allocation?.textContent||'').replace(/\s+/g,' ').trim(),cells};
      const key=[record.idGrade,record.idDisciplina,record.idGradeDisciplina].join(':');if(!rows.some(item=>item.key===key))rows.push({...record,key});
    }
    return rows;
  }
  function scanPage(){
    const state=Context.snapshot(document);
    const filters=filterCatalog.flatMap(([id,label])=>{
      const field=document.getElementById(id);if(!field)return [];
      const options=Array.from(field.options||[]).map(o=>({value:String(o.value||''),label:String(o.textContent||o.text||'').trim(),disabled:Boolean(o.disabled)}));
      const selectedValues=Array.from(field.options||[]).filter(o=>o.selected).map(o=>String(o.value));
      const selected=options.filter(o=>selectedValues.includes(o.value));
      return [{id,label,value:String(field.value||''),selected:selected.map(o=>o.label).join(', '),selectedValues,disabled:Boolean(field.disabled),loading:options.length===0||options.every(o=>/carregando|aguarde/i.test(o.label)),options}];
    });
    const bank=window.SmartFoxBankSelection?.snapshot()?.target||null;
    const math=Array.from(document.querySelectorAll('button,[role="button"]')).some(b=>(b.getAttribute('aria-label')||b.getAttribute('title')||b.textContent||'').includes('Inserir fórmula matemática'));
    const products=nativeProducts(),disciplines=visibleDisciplineRows();
    latestScan={at:Date.now(),path:location.pathname,role:state.role,institution:state.current,filters,products,disciplines,links:nativeLinks(),mathEditor:math,bank,
      editors:['TextoQuestao','TextoAfirmativaA','TextoAfirmativaB','TextoAfirmativaC','TextoAfirmativaD','TextoPadraoResposta','TextoFeedbackQuestao'].filter(id=>document.getElementById(id+'_ifr'))};
    return latestScan;
  }
  function renderScan(){
    const report=scanPage(),container=dialog.querySelector('[data-scan]');
    const rows=report.filters.map(f=>`<div><b>${esc(f.label)}</b><span>${esc(f.loading?'Carregando opções':f.selected||'Selecione no AvaliA')}${f.value?' · código '+esc(f.value):''}${f.disabled?' · bloqueado pelo AvaliA':''}</span><small>${f.options.filter(o=>o.value&&!o.disabled).length} opção(ões) carregada(s)</small></div>`).join('');
    const productSummary=report.products.length?`${report.products.length} produto(s): ${report.products.map(p=>`${p.selected?'✓ ':''}${p.label} (${p.value})`).join(' · ')}`:'Nenhum produto carregado nesta tela';
    const disciplineSummary=report.disciplines.length?`${report.disciplines.length} disciplina(s) visível(is) identificada(s) por código`:'Nenhuma linha de disciplina visível nesta página';
    container.innerHTML=`<p>Identificação automática ao abrir e ao mudar a página. Os filtros dependentes são atualizados depois da seleção no AvaliA.</p><div class="sf-scan-filters">${rows||'<p>Esta tela não apresenta filtros de produto ou avaliação.</p>'}</div><p><b>Produtos:</b> ${esc(productSummary)}</p><p><b>Disciplinas:</b> ${esc(disciplineSummary)}${report.disciplines.length?' · '+esc(report.disciplines.slice(0,5).map(d=>`${d.name||'disciplina'} [${d.idDisciplina||'?'}]`).join(' · ')):''}</p><p>${report.bank?'Banco aberto: disciplina '+esc(report.bank.idDisciplina)+' · grade '+esc(report.bank.idGrade)+'. ':''}<b>${report.links.length}</b> área(s) encontrada(s) no menu · <b>${report.editors.length}</b> editor(es) carregado(s).</p><p>${report.mathEditor?'Editor nativo de fórmulas identificado · MathML e importação LaTeX.':'Abra uma questão no Elaborador para verificar o editor de fórmulas.'}</p><small>A varredura é somente de leitura. Produto, instituição, grade e disciplina são mantidos pelos códigos do AvaliA; nomes iguais não são mesclados.</small>`;
  }

  const dialog=document.createElement('dialog');dialog.id='sf-tools-dialog';
  dialog.innerHTML='<header><div><small>SMARTFOX AUTÔNOMO</small><h2>Ferramentas do professor</h2></div><button type="button" data-close aria-label="Fechar ferramentas">×</button></header><div class="sf-tools-body"><div class="sf-tools-context"><b data-mode></b><p data-context></p></div><div class="sf-tools-switch"><button type="button" data-action="blue">Tela azul</button><button type="button" data-action="editor">Elaborador</button></div><label class="sf-tools-field">Instituição para a tela azul<select data-institution></select></label><div class="sf-tools-grid"><button type="button" data-action="prepare"><b>Preparar avaliação</b><span>Importar Word, criar questões e baixar avaliação e guia</span></button><button type="button" data-action="grading"><b>Corrigir discursivas</b><span>Abrir a correção autônoma: percorrer turmas, questões e modelos sozinho</span></button><button type="button" data-action="likes"><b>Likes e dislikes</b><span>Selecionar questões, operar por TAG e conferir bancos</span></button><button type="button" data-action="messages"><b>Sobre o SmartFox</b><span>Ver a edição autônoma, orientações e backup</span></button></div><details open><summary>Outras áreas disponíveis neste perfil</summary><nav data-native></nav></details><details class="sf-tools-tabs"><summary>Abas abertas do AvaliA</summary><div data-tabs></div><button type="button" data-action="tabs">Atualizar abas</button></details><details class="sf-tools-scan"><summary>Verificação automática da tela</summary><div data-scan></div><button type="button" data-action="scan">Verificar novamente</button></details><div role="status" aria-live="polite" data-status>Escolha uma ferramenta.</div></div>';
  document.body.append(dialog);
  const tagsButton=document.createElement('button');tagsButton.type='button';tagsButton.dataset.action='tags';
  tagsButton.innerHTML='<b>Troca assistida de tags</b><span>Preparar a seleção do Passo 3, sem alterar questões salvas</span>';
  dialog.querySelector('.sf-tools-grid').append(tagsButton);
  const launcher=document.createElement('button');launcher.type='button';launcher.id='sf-tools-launcher';launcher.innerHTML='<img alt="" width="28" height="28"><span>Ferramentas</span>';
  const logo=launcher.querySelector('img');if(chrome.runtime?.getURL)logo.src=chrome.runtime.getURL('icons/icon-48.png');else logo.hidden=true;launcher.setAttribute('aria-haspopup','dialog');document.body.append(launcher);
  function render(){
    const state=Context.snapshot(document),field=dialog.querySelector('[data-institution]'),prior=field.value;
    dialog.querySelector('[data-mode]').textContent=pageMode();
    launcher.title=pageMode()+' · abrir ferramentas';
    dialog.querySelector('[data-context]').textContent=[state.current?.name||'Instituição não identificada',state.role||'Perfil carregando'].join(' · ');
    field.innerHTML='<option value="">Escolha a instituição</option>'+state.institutions.filter(i=>!i.general).map(i=>`<option value="${esc(i.id)}">${esc(i.name)}</option>`).join('');
    const candidates=state.institutions.filter(i=>!i.general);
    field.value=candidates.some(i=>i.id===prior)?prior:state.current&&!state.current.general?state.current.id:candidates.length===1?candidates[0].id:'';
    dialog.querySelector('[data-native]').innerHTML=nativeLinks().map(([path,label])=>`<button type="button" data-path="${esc(path)}">${esc(label)}</button>`).join('')||'<p>O menu do AvaliA ainda está carregando. Feche e reabra as ferramentas após o carregamento.</p>';
    renderScan();
  }
  function extensionMessage(message){
    return new Promise((resolve,reject)=>{
      if(!chrome.runtime?.sendMessage){reject(new Error('Recarregue a extensão e esta aba para restabelecer a conexão.'));return;}
      const timer=setTimeout(()=>reject(new Error('A consulta de abas demorou. Tente atualizar a lista.')),10000);
      try{chrome.runtime.sendMessage(message,response=>{clearTimeout(timer);const error=chrome.runtime.lastError;if(error||!response?.ok)reject(new Error(response?.error||error?.message||'A extensão não respondeu. Recarregue esta aba.'));else resolve(response.data);});}catch(error){clearTimeout(timer);reject(error);}
    });
  }
  async function renderTabs(){
    const holder=dialog.querySelector('[data-tabs]');holder.textContent='Consultando abas do AvaliA…';
    try{const data=await extensionMessage({type:'SF_AVALIA_TABS'});holder.innerHTML=data.tabs.map(t=>`<button type="button" data-tab="${t.id}" ${t.id===data.currentTabId?'disabled':''}><b>${esc(t.path.startsWith('/Elaborador')?'Elaborador':t.path.startsWith('/CorrecaoDiscursiva')?'Correção discursiva':'AvaliA · tela azul')}</b><small>${esc(t.path)}${t.id===data.currentTabId?' · esta aba':''}</small></button>`).join('')||'<p>Nenhuma aba do AvaliA encontrada.</p>';}
    catch(error){holder.textContent=error.message;}
  }
  function open(){previousFocus=document.activeElement;render();if(!dialog.open)dialog.showModal();renderTabs();}
  function close(){dialog.close();previousFocus?.focus?.();}
  launcher.onclick=open;dialog.querySelector('[data-close]').onclick=close;
  dialog.addEventListener('close',()=>previousFocus?.focus?.());
  async function go(path,role,openAction){
    const currentOwner=owner();if(!currentOwner)throw new Error('O professor não foi identificado.');
    const activeResponse=Array.from(document.querySelectorAll('form[id^="correcao_"]')).some(f=>f.getClientRects().length);
    if(activeResponse&&!confirm('Sair da resposta aberta? Confira se a correção foi salva no AvaliA antes de continuar.'))return;
    const status=dialog.querySelector('[data-status]');status.textContent='Conferindo a instituição e o perfil de destino…';
    await navigator.locks.request('smartfox-bank-operation-v11',async()=>{
      const data=await chrome.storage.local.get(['aabRunLockV7','aabSessionV7']);
      if(data.aabRunLockV7&&Date.now()-Number(data.aabRunLockV7.heartbeatAt||0)<20000)throw new Error('Aguarde o envio atual terminar antes de trocar de tela.');
      await window.SmartFoxAccess.assertAuthorized({force:false});
      if(owner()!==currentOwner)throw new Error('A conta mudou. Reabra as ferramentas.');
      if(role){
        const state=Context.snapshot(document),target=role==='Elaborador'?state.institutions.filter(i=>i.general):state.institutions.filter(i=>i.id===dialog.querySelector('[data-institution]').value&&!i.general);
        if(target.length!==1)throw new Error('Escolha a instituição de destino.');
        const context=Context.create({fetch:(...args)=>fetch(...args),parseDocument:html=>new DOMParser().parseFromString(html,'text/html'),expectedOwner:currentOwner,normalizeOwner:window.SmartFoxIdentity.normalizePersonName});
        await context.enter(target[0].id,role);
      }
      if(openAction)await chrome.storage.local.set({[navigationKey]:{owner:currentOwner,action:openAction,path,at:Date.now()}});
      status.textContent='Destino confirmado. Abrindo a tela…';
      location.assign(path);
    });
  }
  dialog.addEventListener('click',async e=>{
    const button=e.target.closest('[data-action],[data-path],[data-tab]');if(!button||busy)return;
    busy=true;button.disabled=true;const status=dialog.querySelector('[data-status]');status.dataset.tone='working';status.textContent='Abrindo a ferramenta…';
    try{
      const action=button.dataset.action;
      if(button.dataset.tab){await extensionMessage({type:'SF_FOCUS_AVALIA_TAB',tabId:Number(button.dataset.tab)});close();return;}
      if(action==='tabs'){await renderTabs();status.textContent='Lista de abas atualizada.';return;}
      if(action==='tags'){if(!window.SmartFoxTagTools)throw Error('A ferramenta de tags não carregou. Recarregue a extensão.');close();window.SmartFoxTagTools.open();return;}
      if(action==='scan'){renderScan();status.dataset.tone='success';status.textContent='Verificação concluída para a tela atual. Confira os filtros e recursos encontrados.';return;}
      if(button.dataset.path){
        const path=button.dataset.path;
        if(!nativeLinks().some(r=>r[0]===path))throw new Error('Esta área não está disponível no menu atual.');
        await go(path);return;
      }
      if(action==='blue'){await go('/Professor','Professor/Tutor');return;}
      if(action==='prepare'&&Context.normalize(Context.snapshot(document).role)==='professor/tutor'){await go('/Elaborador','Elaborador','prepare');return;}
      if(action==='messages'){close();await window.SmartFoxAccess.openAnnouncements();return;}
      if(action==='grading'&&/^\/CorrecaoDiscursiva(?:\/|$)/.test(location.pathname)&&document.getElementById('sf-grading-launcher')){close();document.getElementById('sf-grading-launcher').click();return;}
      if(action==='grading'){await go('/CorrecaoDiscursiva/Index','Professor/Tutor');return;}
      if(action==='editor'){await go('/Elaborador','Elaborador');return;}
      const target=document.getElementById(action==='likes'?'sf-bank-launcher':'aab-launcher');
      if(!target&&action==='prepare'){await go('/Elaborador','Elaborador','prepare');return;}
      if(!target)throw new Error('A ferramenta não terminou de carregar. Recarregue a página e tente novamente.');
      close();target.click();
    }catch(error){status.dataset.tone='error';status.textContent=error.message||String(error);}
    finally{busy=false;button.disabled=false;}
  });
  document.documentElement.classList.add('sf-tools-ready');
  render();
  let updateTimer;
  new MutationObserver(records=>{
    if(records.every(r=>r.target.closest?.('#sf-tools-dialog,#sf-tools-launcher')))return;
    clearTimeout(updateTimer);updateTimer=setTimeout(()=>{if(!busy)render();},300);
  }).observe(document.body,{childList:true,subtree:true,attributes:true,attributeFilter:['disabled','selected','aria-disabled']});
  window.addEventListener('pageshow',()=>{if(!busy)render();});
  document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible'&&!busy){render();if(dialog.open)renderTabs();}});
  document.addEventListener('change',e=>{if(!e.target.closest?.('#sf-tools-dialog'))render();});
  const pending=(await chrome.storage.local.get(navigationKey))[navigationKey];
  if(pending&&pending.owner===owner()&&pending.path===location.pathname&&Date.now()-pending.at<120000){
    await chrome.storage.local.remove(navigationKey);
    if(pending.action==='prepare'){
      let attempts=0;
      const resume=()=>{const target=document.getElementById('aab-launcher');if(target)target.click();else if(++attempts<20)setTimeout(resume,250);else{open();dialog.querySelector('[data-status]').textContent='A tela abriu. Clique em Preparar avaliação quando o carregamento terminar.';}};
      resume();
    }
  }

  window.SmartFoxTools=Object.freeze({open,refresh:render,scan:scanPage});
})();
