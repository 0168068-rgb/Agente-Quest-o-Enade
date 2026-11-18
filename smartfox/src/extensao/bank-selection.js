/* Native question checkboxes — selections are bound to bank IDs, never names. */
(function(){
  'use strict';
  if(window.top!==window.self||!window.SmartFoxBankManager||!window.SmartFoxBankContext)return;
  let currentKey='',selected=new Set(),bar=null,barTable=null,scheduled=false,openingTarget=null,lastTarget=null,selectedMode='all';
  const positive=value=>/^[1-9]\d*$/.test(String(value||''));
  function readTarget(table) {
    const context=window.SmartFoxBankContext.snapshot(document);
    const owner=window.SmartFoxBankManager.owner();
    if(!owner||!context.current?.id||context.current.general)return null;
    const candidates=Array.from(table.querySelectorAll('tbody tr[id^="questao-"] a[href]')).map(link=>{
      const url=new URL(link.getAttribute('href'),location.origin);
      if(url.origin!==location.origin||!/^\/DisciplinaQuestao\/(Validacao|Desativar)$/.test(url.pathname))return null;
      const idGrade=url.searchParams.get('idGrade'),idDisciplina=url.searchParams.get('idDisciplina');
      return positive(idGrade)&&positive(idDisciplina)?{idGrade,idDisciplina}:null;
    }).filter(Boolean);
    const unique=[...new Map(candidates.map(s=>[`${s.idGrade}:${s.idDisciplina}`,s])).values()];
    if(unique.length!==1)return null;
    const selectedProduct=Array.from(document.querySelectorAll('#filtroModalidade option')).find(o=>o.selected);
    const modalityId=selectedProduct?.value;
    const remembered=openingTarget&&openingTarget.owner===owner&&openingTarget.institutionId===context.current.id&&openingTarget.idGrade===unique[0].idGrade&&openingTarget.idDisciplina===unique[0].idDisciplina?openingTarget:null;
    const binding=remembered?.idGradeDisciplina||new URLSearchParams(location.search).get('idGradeDisciplina');
    return {...unique[0],institutionId:context.current.id,owner,...(positive(modalityId)?{modalityId,modality:String(selectedProduct.textContent||'').trim()}:{}),...(positive(binding)?{idGradeDisciplina:binding}:{})};
  }
  function refresh() {
    scheduled=false;
    const table=document.getElementById('tableDisciplinaQuestoes');
    const target=table&&(!table.closest('.modal')||table.closest('.modal').getClientRects().length)&&readTarget(table);
    if(!target){
      const state=window.SmartFoxBankContext.snapshot(document);
      const visible=table&&(!table.closest('.modal')||table.closest('.modal').getClientRects().length);
      const modality=Array.from(document.querySelectorAll('#filtroModalidade option')).find(o=>o.selected)?.value||'';
      const sameContext=lastTarget&&lastTarget.owner===window.SmartFoxBankManager.owner()&&lastTarget.institutionId===state.current?.id&&(lastTarget.modalityId||'')===modality;
      if(visible&&table===barTable&&sameContext&&currentKey&&!table.querySelector('tbody tr[id^="questao-"]')){
        if(bar){bar.querySelector('[data-native-count]').textContent=`${selected.size} selecionadas · aguardando a tabela carregar`;bar.querySelectorAll('button').forEach(b=>b.disabled=true);}return;
      }
      bar?.remove();bar=null;currentKey='';lastTarget=null;selected.clear();return;
    }
    lastTarget=target;
    const key=[target.owner,target.institutionId,target.modalityId||'',target.idGradeDisciplina||'',target.idGrade,target.idDisciplina].join(':');
    if(key!==currentKey){selected.clear();currentKey=key;bar?.remove();bar=null;}
    if(barTable!==table){bar?.remove();bar=null;barTable=table;}
    if(!bar||!bar.isConnected) {
      bar=document.createElement('div');bar.className='sf-native-bank-bar';bar.setAttribute('role','region');bar.setAttribute('aria-label','SmartFox seleção de questões');
      bar.innerHTML='<strong>SmartFox 11.0 · Selecionar questões</strong><span data-native-count></span><div><button type="button" data-native-page>Selecionar esta página</button><button type="button" data-native-clear>Limpar seleção</button><button type="button" data-native-all>Selecionar banco inteiro</button></div><div><button type="button" data-native-mode="like-all">Dar like</button><button type="button" data-native-mode="all">Retirar like</button><button type="button" data-native-mode="dislike-all">Dar dislike</button><button type="button" data-native-apply>Aplicar operação</button></div><small>Escolha a operação e clique em Aplicar operação. Selecione uma ou várias questões. O banco inteiro inclui todas as páginas.</small>';
      const wrapper=table.closest('.dataTables_wrapper')||table;wrapper.parentNode.insertBefore(bar,wrapper);
      bar.querySelector('[data-native-page]').onclick=()=>{for(const row of table.querySelectorAll('tbody tr[id^="questao-"]')){const id=row.id.replace('questao-','');if(positive(id))selected.add(id);}refresh();};
      bar.querySelector('[data-native-clear]').onclick=()=>{selected.clear();refresh();};
      bar.querySelector('[data-native-all]').onclick=()=>openSelection(null,'all');
      bar.querySelectorAll('[data-native-mode]').forEach(button=>button.onclick=()=>{selectedMode=button.dataset.nativeMode;bar.querySelectorAll('[data-native-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));});
      bar.querySelector('[data-native-apply]').onclick=()=>openSelection([...selected],selectedMode);
    }
    function openSelection(questionIds,mode) {
      const latest=readTarget(table);
      if(!latest||JSON.stringify(latest)!==JSON.stringify(target)){refresh();return;}
      if(questionIds!==null&&!questionIds.length){bar.querySelector('[data-native-count]').textContent='Selecione ao menos uma questão ou use Selecionar banco inteiro.';return;}
      window.SmartFoxBankManager.openQuestionSelection({target:latest,questionIds,mode}).catch(error=>{bar.querySelector('[data-native-count]').textContent=error.message;});
    }
    for(const row of table.querySelectorAll('tbody tr[id^="questao-"]')) {
      const id=row.id.replace('questao-','');if(!positive(id))continue;
      let check=row.querySelector('input[data-sf-question-select]');
      if(!check) {
        check=document.createElement('input');check.type='checkbox';check.dataset.sfQuestionSelect=id;check.className='sf-native-question-check';check.setAttribute('aria-label',`Selecionar questão ${id}`);
        (row.cells?.[0]||row.querySelector('td'))?.prepend(check);
      }
      check.onchange=()=>{if(check.checked)selected.add(id);else selected.delete(id);updateCount();};
      check.checked=selected.has(id);
    }
    function updateCount(){const text=`${selected.size} selecionadas · disciplina ${target.idDisciplina} · grade ${target.idGrade}`;const field=bar.querySelector('[data-native-count]');if(field.textContent!==text)field.textContent=text;}
    bar.querySelectorAll('button').forEach(b=>b.disabled=false);
    bar.querySelectorAll('[data-native-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.nativeMode===selectedMode)));
    updateCount();
  }
  document.addEventListener('click',event=>{
    const link=event.target.closest?.('a[data-load-url]');if(!link)return;
    let url;try{url=new URL(link.getAttribute('data-load-url'),location.origin);}catch{return;}
    if(url.origin!==location.origin||url.pathname!=='/DisciplinaQuestao/Index')return;
    const state=window.SmartFoxBankContext.snapshot(document),row=link.closest('tr');
    const allocation=row?.querySelector('a[href*="idGradeDisciplina="]')?.getAttribute('href');
    const binding=allocation?new URL(allocation,location.origin).searchParams.get('idGradeDisciplina'):null;
    const selectedProduct=Array.from(document.querySelectorAll('#filtroModalidade option')).find(o=>o.selected);
    openingTarget={owner:window.SmartFoxBankManager.owner(),institutionId:state.current?.id,idGrade:url.searchParams.get('idGrade'),idDisciplina:url.searchParams.get('idDisciplina'),...(positive(selectedProduct?.value)?{modalityId:selectedProduct.value,modality:String(selectedProduct.textContent||'').trim()}:{}),...(positive(binding)?{idGradeDisciplina:binding}:{})};
    selected.clear();currentKey='';
  },true);
  function snapshot(){
    refresh();const table=document.getElementById('tableDisciplinaQuestoes');
    if(!bar||!table)return null;
    const target=readTarget(table);return target?{target,questionIds:[...selected]}:null;
  }
  window.SmartFoxBankSelection=Object.freeze({snapshot,refresh});
  const observer=new MutationObserver(records=>{
    if(records.every(r=>r.target.closest?.('.sf-native-bank-bar,#sf-bank-dialog')||Array.from(r.addedNodes).every(n=>n.nodeType!==1||n.matches?.('input[data-sf-question-select],.sf-native-bank-bar'))&&r.addedNodes.length))return;
    if(!scheduled){scheduled=true;setTimeout(refresh,150);}
  });
  observer.observe(document.body,{childList:true,subtree:true});
  window.addEventListener('smartfox-bank-updated',event=>{
    const table=document.getElementById('tableDisciplinaQuestoes'),target=table&&readTarget(table);
    if(target&&event.detail?.keys?.includes(`${target.institutionId}:${target.idGrade}:${target.idDisciplina}`)) {
      const modal=table.closest('.modal');(modal||document).querySelector('#btnPesquisar')?.click();
    }
  });
  refresh();
})();
