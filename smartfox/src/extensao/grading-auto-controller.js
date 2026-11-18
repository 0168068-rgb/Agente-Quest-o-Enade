(function(){
  'use strict';
  if(window.top!==window.self||!/^\/CorrecaoDiscursiva(?:\/|$)/i.test(location.pathname))return;
  let initialized=false;
  async function init(){
    const G=window.SmartFoxGradingAssistant,A=window.SmartFoxGradingAutomation;
    if(initialized||!G||!A||!/^\d+$/.test(G.filters().institution.id)||!/^\d+$/.test(G.filters().assessment.id))return;initialized=true;
    readyObserver.disconnect();
    const institution=G.filters().institution.id;
    const storageKey='smartfoxAutomaticPolicyV1:'+encodeURIComponent(G.expectedOwner)+':'+institution;
    const resumeKey=storageKey+':lastRun';
    const autonomyKey=storageKey+':autonomy';
    let restoredMode=null,loadError='',supervisor;
    const visible=e=>Boolean(e?.isConnected&&e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden');
    const text=e=>String(e?.innerText||e?.textContent||'').replace(/\s+/g,' ').trim();
    const ui=document.createElement('section');ui.id='sf-auto-grading';ui.className='sf-auto-panel';ui.dataset.build='2026.10.09.6';
    ui.innerHTML=`<header><div><small>SMARTFOX 11.0 · CORREÇÃO AUTÔNOMA · R6</small><h3>Abre, corrige e avança sozinho</h3></div><span data-state>Preparando início automático</span></header>
      <p data-scope></p><p data-rule>Sem resposta: zero. Uma linha: 0,5 ponto. Mais de uma linha: nota máxima.</p>
      <div class="sf-auto-settings">
        <label>Avaliações do lote<select data-setting="scope"><option value="all">Todas as disponíveis nesta instituição</option><option value="current">Somente a avaliação selecionada</option></select></label>
        <label>Caracteres por linha padrão<input data-setting="lineWidth" type="number" min="20" max="500" value="80"></label>
        <label>Linhas para pontuação integral<input data-setting="minLines" type="number" min="2" max="100" value="2"></label>
        <label>Pontos para resposta curta<input data-setting="shortScore" type="number" min="0" step="0.001" value="0.5"></label>
        <label>Percentual do peso da questão<input data-setting="creditPercent" type="number" min="0.001" max="100" step="0.001" value="100"></label>
      </div><p class="sf-auto-hint">A linha padrão independe da tela: cada bloco de 80 caracteres normalizados conta uma linha. Espaços repetidos, Enter e parágrafos vazios não aumentam a contagem.</p>
      <p class="sf-auto-hint"><strong>Justificativa: sempre o padrão de resposta da própria questão.</strong> O texto e a formatação são copiados integralmente para todas as notas. Se não houver padrão, a resposta fica para conferência e o lote continua.</p>
      <details><summary>Testar o critério antes de iniciar</summary><label>Exemplo de resposta<textarea data-example rows="3" placeholder="Cole uma resposta de exemplo."></textarea></label><button type="button" data-auto="test">Calcular exemplo (peso 1)</button><p data-test></p></details>
      <div class="sf-auto-actions"><button type="button" data-auto="save">Salvar meus critérios</button><button type="button" data-auto="start" class="sf-auto-primary">Retomar agora</button><button type="button" data-auto="pause">Pausar</button><button type="button" data-auto="history">Baixar histórico</button></div>
      <p class="sf-auto-run" role="status" aria-live="polite" data-progress>O modo autônomo inicia ao abrir esta tela: pesquisa pendências, clica em Corrigir, salva cada resposta e segue para a próxima turma e avaliação.</p><p data-current></p>
      <small>Mantenha a aba, o computador e a sessão do AvaliA ativos. Ao terminar, novas pendências são verificadas a cada 60 segundos. Ao recarregar, o modo ativo retoma sozinho. Uma pausa solicitada permanece até Retomar agora.</small>`;
    const anchor=document.getElementById('formPesquisaCorrecaoDiscursiva');
    if(anchor)anchor.before(ui);else document.body.prepend(ui);
    const dock=document.createElement('aside');dock.id='sf-auto-dock';
    dock.innerHTML='<strong>SmartFox · correção autônoma · R6</strong><p role="status" aria-live="polite" data-dock-status>Preparando início automático…</p><p data-dock-current></p><div><button type="button" data-auto="pause">Pausar</button><button type="button" data-auto="start">Retomar agora</button><button type="button" data-auto="review">Revisão individual</button></div>';
    document.body.append(dock);
    const fields=Array.from(ui.querySelectorAll('[data-setting]'));
    const readPolicy=()=>A.validatePolicy(Object.fromEntries(fields.map(e=>[e.dataset.setting,e.value])));
    const showPolicy=p=>fields.forEach(e=>{e.value=String(p[e.dataset.setting]);});
    function describePolicy(p){
      ui.querySelector('[data-rule]').textContent='Sem resposta: zero. De 1 a '+(p.minLines-1)+' linha(s): '+String(p.shortScore).replace('.',',')+' ponto(s). A partir de '+p.minLines+' linhas: '+p.creditPercent+'% do peso. A nota respeita o máximo da questão; este modo considera a extensão do texto.';
      ui.querySelector('.sf-auto-hint').textContent='Uma linha padrão corresponde a '+p.lineWidth+' caracteres normalizados, incluindo os espaços simples entre palavras. Enter e parágrafos vazios não aumentam a contagem.';
    }
    const say=value=>{ui.querySelector('[data-progress]').textContent=value;};
    function updateScope(){const f=G.filters();ui.querySelector('[data-scope]').textContent='Instituição: '+f.institution.name+' · Avaliação atual: '+f.assessment.name;}
    showPolicy(A.DEFAULTS);updateScope();
    try{const stored=await chrome.storage.local.get([storageKey,resumeKey,autonomyKey]);if(stored[storageKey])showPolicy(A.validatePolicy(stored[storageKey]));restoredMode=stored[autonomyKey]||null;if(stored[resumeKey])say('Última passagem: '+stored[resumeKey].confirmed+' correções confirmadas.');}
    catch(error){loadError='Não foi possível carregar os critérios salvos: '+error.message;say(loadError);}
    describePolicy(readPolicy());
    let run=null,ownedChange=false,runner;
    const modal=()=>document.getElementById('modalCarousel');
    function assertScope(){
      if(!run)return;
      if(G.owner()!==G.expectedOwner||G.filters().institution.id!==run.institution)throw Error('Professor ou instituição mudou. Reabra a página no contexto correto.');
      if(!ownedChange&&G.filterKey(G.filters())!==run.filters){
        supervisor?.restart('Filtros atualizados pelo AvaliA. Reiniciando a pesquisa automaticamente…');
        throw Error('Os filtros mudaram. A sequência será reiniciada antes de qualquer novo envio.');
      }
    }
    async function waitFor(check,label,timeout=20000){
      const deadline=Date.now()+timeout;
      while(Date.now()<deadline){
        if(['pausing','paused'].includes(runner.status().state))throw Error('Execução pausada.');
        assertScope();const result=check();if(result)return result;
        await new Promise(resolve=>setTimeout(resolve,150));
      }
      throw Error(label+' não foi confirmado pelo AvaliA. A execução foi interrompida.');
    }
    function setSelect(id,value){
      const el=document.getElementById(id);
      if(!el||!Array.from(el.options).some(o=>o.value===String(value)&&!o.disabled))throw Error('Opção indisponível no filtro '+id+'.');
      if(el.value===String(value))return;
      el.value=String(value);el.dispatchEvent(new Event('change',{bubbles:true}));
    }
    const table=()=>document.getElementById('TabelaQuestoesDiscursivas');
    const links=()=>Array.from(table()?.querySelectorAll('tbody a[data-load-url]')||[]).filter(e=>visible(e)&&text(e).includes('Corrigir'));
    const tableSignature=()=>links().map(e=>e.getAttribute('data-load-url')).join('|');
    const holdCarousel=()=>document.dispatchEvent(new Event('smartfox-grading-hold-carousel'));
    const pageState=()=>A.paginationState(document.getElementById('TabelaQuestoesDiscursivas_wrapper'));
    async function waitForResults(fresh=()=>true){
      let previous=null,signature='',stableSince=0;
      return waitFor(()=>{
        const current=table(),wrapper=document.getElementById('TabelaQuestoesDiscursivas_wrapper');
        const rows=current?.querySelectorAll('tbody tr'),page=pageState();
        const ready=fresh()&&visible(current)&&rows?.length&&page.ready&&
          !Array.from(wrapper?.querySelectorAll('.dataTables_processing')||[]).some(visible)&&
          (current.querySelector('td.dataTables_empty')||links().length);
        if(!ready){previous=null;return false;}
        const nextSignature=tableSignature()+'|'+page.token;
        if(current!==previous||nextSignature!==signature){previous=current;signature=nextSignature;stableSince=Date.now();return false;}
        return Date.now()-stableSince>=300;
      },'Carregamento completo da lista e da paginação',60000);
    }
    async function closeModal(){
      if(!visible(modal()))return;
      const close=Array.from(modal().querySelectorAll('[data-dismiss="modal"]')).find(visible);
      if(!close)throw Error('Não foi possível localizar Fechar no AvaliA.');
      close.click();await waitFor(()=>!visible(modal()),'Fechamento da resposta');
    }
    runner=A.createRunner({
      assertScope,
      async runExclusive(task){
        if(!navigator.locks?.request)throw Error('Este navegador não oferece bloqueio entre abas. Use uma versão atual do Chrome ou Edge.');
        await navigator.locks.request('smartfox-grading:'+G.expectedOwner,{ifAvailable:true},async lock=>{
          if(!lock){const error=Error('Outra aba já está executando correções.');error.code='SF_GRADING_BUSY';throw error;}
          await task();
        });
      },
      async begin(p){
        if(!/^\d+$/.test(institution)||G.filters().institution.id!==institution)throw Error('A instituição mudou. Recarregue a página para salvar os critérios no contexto correto.');
        const current=window.SmartFoxBankContext?.snapshot(document)?.current;
        if(!current||current.general||String(current.id)!==institution)throw Error('A instituição dos filtros difere de Minhas Instituições. Selecione o contexto correto antes de iniciar.');
        await window.SmartFoxAccess.assertAuthorized({force:true});await G.reloadHistory();
        run={institution,filters:G.filterKey(G.filters()),policy:p,initialAssessment:G.filters().assessment.id};
        await closeModal();await chrome.storage.local.set({[storageKey]:p});
      },
      assessments(p){
        return Array.from(document.getElementById('sltAvaliacao')?.options||[]).filter(o=>/^\d+$/.test(o.value)&&!o.disabled&&(p.scope==='all'||o.value===run.initialAssessment)).map(o=>({id:o.value,name:text(o)}));
      },
      async selectAssessment(a){
        ownedChange=true;
        try{setSelect('sltAvaliacao',a.id);setSelect('sltStatus','1');setSelect('sltAgrupamento','3');if(document.getElementById('sltStatusCorrecaoIA'))setSelect('sltStatusCorrecaoIA','0');run.filters=G.filterKey(G.filters());run.assessment=a.id;}
        finally{ownedChange=false;}
        document.dispatchEvent(new Event('smartfox-grading-refresh-filters'));
        updateScope();say('Pesquisando '+a.name+'…');
      },
      async search(){
        await closeModal();const search=document.getElementById('btnPesquisarCorrecaoDiscursiva');
        if(!search)throw Error('Botão Pesquisar não localizado.');
        await waitFor(()=>!search.disabled,'Disponibilidade da pesquisa',60000);
        const previous=table();let changed=false;
        const observer=new MutationObserver(records=>{if(records.some(r=>r.target.id==='resultadosCorrecaoDiscursiva'||r.target.closest?.('#resultadosCorrecaoDiscursiva')))changed=true;});
        observer.observe(document.body,{childList:true,subtree:true});
        try{
          search.click();
          await waitForResults(()=>!search.disabled&&((table()&&table()!==previous)||(changed&&visible(document.getElementById('resultadosCorrecaoDiscursiva')))));
          if(!table())throw Error('Tabela de resultados não encontrada. Verifique a mensagem do AvaliA.');
        }finally{observer.disconnect();}
      },
      rows(){
        const result=links().map(e=>{const cells=Array.from(e.closest('tr')?.querySelectorAll('td')||[]);return {key:A.queueTarget(e.getAttribute('data-load-url'),location.origin,{institution:run.institution,assessment:run.assessment}),group:text(cells[1]),discipline:text(cells[2])};});
        if(!result.length&&table()?.querySelector('tbody tr')&&!table().querySelector('td.dataTables_empty')&&text(table().querySelector('tbody')))throw Error('A lista tem resultados sem um botão Corrigir reconhecido.');
        return result;
      },
      async open(row){
        const found=links().find(e=>A.queueTarget(e.getAttribute('data-load-url'),location.origin,{institution:run.institution,assessment:run.assessment})===row.key);
        if(!found)throw Error('A lista mudou. Reinicie para pesquisar as pendências novamente.');
        run.group=row.group;run.discipline=row.discipline;
        dock.querySelector('[data-dock-current]').textContent='Abrindo '+(row.group||'turma')+' · '+(row.discipline||'disciplina')+'…';
        const previous=document.querySelector('#questoesItens');found.scrollIntoView({block:'center',behavior:'instant'});found.click();
        await waitFor(()=>visible(modal())&&document.querySelector('#questoesItens')!==previous&&document.querySelector('#questoesItens .item.active'),'Abertura da turma',120000);
        holdCarousel();run.items=Array.from(document.querySelectorAll('#questoesItens .item'));
        await G.scan();
      },
      async current(){
        holdCarousel();
        await waitFor(()=>{const e=document.querySelector('#questoesItens .item.active');return visible(e)&&!e.classList.contains('left')&&!e.classList.contains('right');},'Carregamento da questão');
        await G.scan();const form=document.querySelector('#questoesItens .item.active form[id^="correcao_"]');
        if(!form)throw Error('Formulário da resposta não identificado; nenhuma nota foi enviada.');
        const c=G.readContext(form);run.currentItem=c.item;c.item.scrollIntoView({block:'start',behavior:'instant'});
        return {...c,discipline:run.discipline};
      },
      alreadyDone:c=>G.automaticStatus(c),
      issue:(c,error)=>G.recordIssue(c,error),
      preview(c,d){
        const m=d.metadata;
        ui.querySelector('[data-current]').textContent='Disciplina: '+(m.discipline||'não informada no cabeçalho')+' · Prova: '+(m.exam||m.assessment)+' · Modelo: '+(m.model||'não informado')+' · Resposta '+c.id+' · '+d.lines+' linha(s) · Nota '+d.score+' / '+d.maxScore;
        const items=run.items;
        dock.querySelector('[data-dock-current]').textContent=(run.group?run.group+' · ':'')+ui.querySelector('[data-current]').textContent+' · Questão '+(items.indexOf(c.item)+1)+' de '+items.length;
      },
      submit:(c,d,check)=>G.submitAutomatic(c,d,check),
      async next(){
        holdCarousel();const items=run.items,previous=run.currentItem;
        if(items.length<2||items.indexOf(previous)===items.length-1)return false;
        const active=document.querySelector('#questoesItens .item.active');
        if(active!==previous){
          if(active!==items[items.indexOf(previous)+1])throw Error('O carrossel mudou de ordem. Reabra o grupo para conferir a navegação.');
          return true;
        }
        const next=modal()?.querySelector('[data-slide="next"]');
        if(!next||!visible(next)||next.classList.contains('disabled')||getComputedStyle(next).pointerEvents==='none')throw Error('A próxima questão está indisponível.');
        next.click();await waitFor(()=>document.querySelector('#questoesItens .item.active')!==active,'Próxima questão');return true;
      },
      close:closeModal,
      async nextPage(){
        await waitForResults();const page=pageState();
        if(page.end)return false;
        const before=tableSignature(),previousTable=table();
        page.next.scrollIntoView({block:'center',behavior:'instant'});page.next.click();
        await waitForResults(()=>table()!==previousTable||tableSignature()!==before||pageState().token!==page.token);return true;
      },
      status(s){
        const busy=['running','pausing'].includes(s.state);
        fields.forEach(e=>e.disabled=busy);ui.querySelector('[data-auto="save"]').disabled=busy;
        ui.querySelector('[data-state]').textContent=({idle:'Pronto',running:'Em execução',pausing:'Pausando',paused:'Pausado',blocked:'Requer conferência',waiting:'Aguardando outra aba',completed:'Passagem concluída'})[s.state];
        say(s.confirmed+' correções confirmadas · '+s.skipped+' já corrigidas · '+s.pending+' para conferência'+(s.lastError?' · '+s.lastError:s.state==='completed'?' · Fim das avaliações selecionadas.':' · '+(s.state==='running'?'Processando as pendências…':'Nenhum novo envio será iniciado.')));
        dock.querySelector('[data-dock-status]').textContent=ui.querySelector('[data-progress]').textContent;
      },
      async finish(s){try{await chrome.storage.local.set({[resumeKey]:{...s,at:new Date().toISOString()}});}catch(error){say('Não foi possível salvar o resumo: '+error.message);}finally{run=null;}}
    });
    supervisor=A.createSupervisor({
      now:()=>Date.now(),setTimer:(fn,ms)=>setTimeout(fn,ms),clearTimer:id=>clearTimeout(id),
      load:async()=>(await chrome.storage.local.get(autonomyKey))[autonomyKey],
      save:mode=>chrome.storage.local.set({[autonomyKey]:mode}),pause:()=>runner.pause(),
      async run(check){
        const stored=await chrome.storage.local.get(storageKey);
        if(stored[storageKey])showPolicy(A.validatePolicy(stored[storageKey]));
        const p=readPolicy();describePolicy(p);check();return runner.start(p);
      },
      status(s){
        const busy=s.busy||['running','pausing'].includes(runner.status().state);
        document.body.classList.toggle('sf-autonomous-mode',s.mode==='enabled'||busy);
        if(!busy&&s.mode!=='enabled')void G.scan().catch(console.error);
        for(const root of [ui,dock]){
          root.querySelector('[data-auto="start"]').disabled=busy;
          root.querySelector('[data-auto="pause"]').disabled=s.mode!=='enabled';
        }
        if(!busy){
          const label=s.mode==='paused'?'Pausado':s.mode==='blocked'?'Requer conferência':'Autônomo ativo';
          ui.querySelector('[data-state]').textContent=label;
          const message=s.reason||'Início automático em 3 segundos. Não é necessário aprovar cada questão.';
          dock.querySelector('[data-dock-status]').textContent=message;say(message);
        }
      }
    });
    const pause=reason=>supervisor.suspend(reason);
    document.addEventListener('change',e=>{
      if(e.target.matches?.('#sltInstituicao,#sltAvaliacao,#sltStatus,#sltAgrupamento,#sltStatusCorrecaoIA')){
        if(!ownedChange)supervisor.restart('Filtros atualizados. A correção continuará automaticamente em 3 segundos.');updateScope();
      }
    });
    document.addEventListener('keydown',e=>{if(e.key==='Escape')void pause('Pausado com Esc.');});
    document.addEventListener('click',e=>{
      if(!e.isTrusted||supervisor.status().mode!=='enabled')return;
      // Ordinary clicks, including opening Corrigir, must never persist a pause.
      const target=e.target.closest?.('button,a,input,select,textarea');
      if(target?.matches('#questoesItens form[id^="correcao_"] button[type="submit"]')){
        e.preventDefault();e.stopImmediatePropagation();
        dock.querySelector('[data-dock-status]').textContent='A correção automática já está ativa. Aguarde o envio e o avanço para a próxima questão.';
        return;
      }
      if(target?.matches('#TabelaQuestoesDiscursivas a[data-load-url],#btnPesquisarCorrecaoDiscursiva,#modalCarousel [data-slide],#modalCarousel [data-dismiss="modal"]'))supervisor.restart('Navegação atualizada. Retomando automaticamente a sequência…');
    },true);
    document.addEventListener('input',e=>{if(e.isTrusted&&e.target.closest?.('#questoesItens form[id^="correcao_"]'))void pause('Edição manual da correção iniciada. Clique em Retomar agora quando terminar.');},true);
    ui.addEventListener('input',e=>{if(e.target.matches('[data-setting]'))void pause('Critérios em edição. Salve e clique em Retomar agora.');});
    ui.addEventListener('change',e=>{if(e.target.matches('[data-setting]'))void pause('Critérios em edição. Salve e clique em Retomar agora.');});
    async function handleAction(e){
      const button=e.target.closest('[data-auto]');if(!button||button.disabled)return;
      try{
        const action=button.dataset.auto;
        if(action==='pause'){await pause('Pausado pelo professor.');return;}
        if(action==='review'){await pause('Revisão individual selecionada.');return;}
        if(action==='history'){G.downloadHistory();return;}
        const p=readPolicy();
        describePolicy(p);
        if(action==='save'){
          if(G.filters().institution.id!==institution)throw Error('A instituição mudou. Recarregue a página antes de salvar.');
          await chrome.storage.local.set({[storageKey]:p});say('Critérios salvos. A justificativa será sempre o padrão de resposta da questão.');
        }
        if(action==='test'){
          const d=A.decide({responseText:ui.querySelector('[data-example]').value,maxScore:1,step:'0.001',expectedText:'Padrão apenas para simular a nota.'},p);
          ui.querySelector('[data-test]').textContent=d.characters+' caracteres · '+d.lines+' linha(s) · nota '+d.score+' de 1. Na correção, a justificativa será o padrão da própria questão.';
        }
        if(action==='start'){await chrome.storage.local.set({[storageKey]:p});await supervisor.resume();}
      }catch(error){say(error.message||String(error));}
    }
    ui.addEventListener('click',handleAction);dock.addEventListener('click',handleAction);
    chrome.storage.onChanged?.addListener((changes,area)=>{if(area==='local'&&changes[autonomyKey])supervisor.sync(changes[autonomyKey].newValue);});
    window.addEventListener('pagehide',()=>supervisor.dispose());
    window.addEventListener('pageshow',async e=>{
      if(!e.persisted)return;
      try{await supervisor.restore((await chrome.storage.local.get(autonomyKey))[autonomyKey]);}
      catch(error){await supervisor.suspend('Não foi possível retomar a sessão: '+error.message,true);}
    });
    const launcher=document.getElementById('sf-grading-launcher');if(launcher)launcher.onclick=()=>ui.scrollIntoView({block:'start',behavior:'smooth'});
    window.SmartFoxAutomaticGrading=Object.freeze({runner,readPolicy,supervisor});
    await supervisor.restore(loadError?{mode:'blocked',reason:loadError}:restoredMode);
  }
  const readyObserver=new MutationObserver(()=>init().catch(console.error));
  readyObserver.observe(document.body,{childList:true,subtree:true});
  window.addEventListener('smartfox-grading-ready',()=>init().catch(console.error));
  document.addEventListener('change',()=>init().catch(console.error));
  init().catch(console.error);
})();
