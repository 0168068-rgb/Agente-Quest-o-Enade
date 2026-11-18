(function(root){
 'use strict';
 const norm=v=>String(v||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').trim().toLowerCase();
 function plan(catalog,from,to){
  const eligible=catalog.filter(t=>norm(t.group)==='graduacao');
  const target=eligible.filter(t=>t.id===String(to));
  const source=from?eligible.filter(t=>t.id===String(from)):[];
  if(target.length!==1 || (from && source.length!==1))throw Error('Tag ausente ou ambígua. Mapeie novamente.');
  if(from===to)throw Error('Escolha uma tag de destino diferente.');
  return {source:source[0]||null,target:target[0],changes:eligible.filter(t=>t.id===String(from)||t.id===String(to)).map(t=>({id:t.id,before:t.selected,after:t.id===String(to)}))};
 }
 root.SmartFoxTagPlan={plan};
 if(!root.document||root.top!==root.self)return;
 const doc=root.document;
 const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 function fields(){return Array.from(doc.querySelectorAll('input[name="disciplinaQuestaoTags"]')).map(el=>({
  id:String(el.value),label:el.getAttribute('text')||el.getAttribute('data-text')||'',group:el.closest('fieldset')?.querySelector('legend')?.textContent||'',selected:el.checked,el
 })).filter(t=>t.label&&norm(t.group)==='graduacao');}
 let dialog, snapshot='';
 const signature=items=>JSON.stringify(items.map(({id,label,group,selected})=>({id,label,group,selected})));
 function scan(){
  const items=fields();snapshot=signature(items);
  const options=items.map(t=>`<option value="${esc(t.id)}">${esc(t.label)} (${esc(t.id)})${t.selected?' ✓':''}</option>`).join('');
  dialog.querySelector('[data-from]').innerHTML='<option value="">Somente marcar destino</option>'+options;
  dialog.querySelector('[data-to]').innerHTML='<option value="">Escolha o destino</option>'+options;
  dialog.querySelector('[data-status]').textContent=items.length?`${items.length} tags de Graduação encontradas. A alteração vale somente para a seleção antes de Adicionar. As linhas já adicionadas não são modificadas.`:'Abra Elabore Novas Questões → IES → Passo 3 para carregar as tags.';
 }
 async function apply(){
  try{
   await root.SmartFoxAccess.assertAuthorized({force:false});
   const state=await chrome.storage.local.get(['aabRunLockV7','aabSessionV7']);
   if(state.aabRunLockV7&&Date.now()-Number(state.aabRunLockV7.heartbeatAt||0)<20000)throw Error('Aguarde o lote terminar antes de trocar tags.');
   if(state.aabSessionV7?.confirmedAt && state.aabSessionV7.status!=='completed')throw Error('A remessa está confirmada. Finalize ou abandone o lote antes de reconfigurar as tags.');
   const step=doc.getElementById('step-3'),questionId=doc.getElementById('Questao_IdQuestao')?.value;
   if(!step||!step.getClientRects().length||questionId&&questionId!=='0')throw Error('Use somente o Passo 3 de uma questão nova, ainda não salva.');
   const items=fields();if(signature(items)!==snapshot)throw Error('O catálogo ou a seleção mudou. Clique em Mapear novamente.');
   const p=plan(items,dialog.querySelector('[data-from]').value,dialog.querySelector('[data-to]').value);
   if(p.changes.some(c=>items.find(t=>t.id===c.id).el.disabled))throw Error('O AvaliA bloqueou uma das tags.');
   if(!root.confirm(`Trocar a seleção de tag: ${p.source?.label||'(nenhuma)'} → ${p.target.label}?\nSomente a seleção para a próxima inclusão de disciplina será alterada. Linhas existentes, questões salvas e likes não serão modificados.`))return;
   if(signature(fields())!==snapshot)throw Error('Seleção alterada durante a confirmação. Mapeie novamente.');
   for(const change of p.changes){
    const field=items.find(t=>t.id===change.id).el;
    if(field.checked!==change.after){
     // Use the native iCheck click target when present; never rewrite row spans or hidden IDs.
     const helper=field.parentElement?.querySelector('ins.iCheck-helper');
     (helper||field).click();
    }
   }
   if(p.changes.some(c=>items.find(t=>t.id===c.id).el.checked!==c.after))throw Error('A seleção não foi confirmada pelo AvaliA. Confira manualmente antes de Adicionar.');
   scan();dialog.querySelector('[data-status]').textContent='Seleção conferida. Feche este painel e use Adicionar no AvaliA. Se a disciplina já estiver na tabela, refaça a associação manualmente e remapeie a tag no SmartFox antes do envio.';
  }catch(error){dialog.querySelector('[data-status]').textContent=error.message;}
 }
 function open(){
  if(!dialog){
   dialog=doc.createElement('dialog');dialog.id='sf-tag-dialog';
   dialog.style.cssText='max-width:650px;width:90%;padding:24px;border:1px solid #ddd;border-radius:12px;color:#182437;background:white;';
   dialog.innerHTML='<h2>Troca assistida de tags</h2><p>Somente seleção do Passo 3. Não altera questões já cadastradas.</p><p>Discursiva 1 corresponde à primeira questão aberta da prova, e Discursiva 2 à segunda, independentemente da numeração.</p><label>Tag de origem <select data-from></select></label><br><br><label>Tag de destino <select data-to></select></label><p data-status role="status" aria-live="polite"></p><button type="button" data-scan>Mapear novamente</button> <button type="button" data-apply>Aplicar operação</button> <button type="button" data-close>Fechar</button>';
   doc.body.append(dialog);dialog.querySelector('[data-scan]').onclick=scan;dialog.querySelector('[data-close]').onclick=()=>dialog.close();
   dialog.querySelector('[data-apply]').onclick=async()=>{const b=dialog.querySelector('[data-apply]');b.disabled=true;try{await apply();}finally{b.disabled=false;}};
  }
  scan();if(!dialog.open)dialog.showModal();
 }
 root.SmartFoxTagTools={open};
})(typeof window==='undefined'?globalThis:window);
