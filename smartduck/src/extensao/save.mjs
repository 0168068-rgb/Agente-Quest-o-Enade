// Runs in MAIN so the actual SophiA Salvar link keeps its onclick and ASP.NET
// javascript: postback behavior. It never submits a form by an invented route.
export function portalSave(command){
  const norm=v=>String(v??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toUpperCase().replace(/\s+/g,' ').trim();
  const visible=e=>e?.isConnected&&e.getClientRects().length>0&&getComputedStyle(e).display!=='none'&&getComputedStyle(e).visibility!=='hidden';
  const clean=e=>(e?.innerText??e?.textContent??'').replace(/\s+/g,' ').trim();
  const label=e=>norm(e.value||e.innerText||e.textContent);
  const fail=message=>({ok:false,message});
  const key='__SMARTDUCK_SAVE_V1__',state=window[key];
  if(command.action==='saveStatus'){
    if(!state||(command.nonce&&state.nonce!==command.nonce))return {ok:true,missing:true};
    return {ok:true,nonce:state.nonce,issued:state.issued,started:state.started,finished:state.finished,error:state.error||'',validation:state.validation||''};
  }
  if(command.action==='saveNotStarted'){
    if(!state||state.nonce!==command.nonce||state.started||!state.issued)return {ok:true,abandoned:false};
    state.finished=true;state.cleanup?.();return {ok:true,abandoned:true};
  }
  if(command.action==='saveNotice'){
    if(!state||state.nonce!==command.nonce)return {ok:true,completed:false};
    if(window.Sys?.WebForms?.PageRequestManager?.getInstance?.()?.get_isInAsyncPostBack?.())return {ok:true,completed:false};
    state.finished=true;state.cleanup?.();return {ok:true,completed:true};
  }
  if(command.action!=='saveClick')return fail('Comando de gravação inválido.');
  if(location.origin+location.pathname!==command.url)return fail('A página mudou antes do clique em Salvar.');
  if(state?.nonce===command.nonce)return fail('O clique em Salvar desta tentativa já foi solicitado.');
  if(state?.started&&!state.finished)return {...fail('A gravação anterior ainda está em andamento.'),code:'SAVE_IN_FLIGHT'};
  state?.cleanup?.();
  for(const c of command.context){
    const matches=Array.from(document.querySelectorAll('select')).filter(e=>(e.id||e.name)===c.id);
    if(matches.length!==1||matches[0].value!==c.value||norm(matches[0].options[matches[0].selectedIndex]?.text)!==norm(c.text))return fail('Os filtros mudaram antes do clique em Salvar.');
  }
  const tables=Array.from(document.querySelectorAll('table'));
  const inputs=[];
  for(const f of command.fields){
    const table=tables[f.table],rows=table?Array.from(table.rows).filter(r=>r.closest('table')===table):[];
    const cell=rows[f.row]?.cells[f.column];
    const found=cell?Array.from(cell.querySelectorAll('input[type="text"],input[type="number"],input:not([type])')).filter(visible):[];
    if(found.length!==1||found[0].value!==f.value||(found[0].id||found[0].name||'')!==f.id||found[0].matches(':disabled')||found[0].readOnly||found[0].getAttribute('aria-disabled')==='true')return fail('Uma nota mudou antes do clique em Salvar.');
    const nameCell=rows[f.row].cells[f.nameColumn],name=nameCell?.getAttribute('title')||nameCell?.querySelector('[title]')?.getAttribute('title')||clean(nameCell);
    const ra=clean(rows[f.row].cells[f.raColumn]).replace(/^(\d+)\.0+$/,'$1').toUpperCase();
    if(ra!==f.ra||norm(name)!==norm(f.name))return fail('O aluno mudou antes do clique em Salvar.');
    inputs.push(found[0]);
  }
  const b=command.button;
  const buttons=Array.from(document.querySelectorAll('button,a,input[type="submit"],input[type="button"]')).filter(e=>visible(e)&&!e.matches(':disabled')&&!e.disabled&&e.getAttribute('aria-disabled')!=='true'&&
    e.tagName===b.tag&&(e.id||'')===b.id&&(e.name||'')===b.name&&label(e)===b.label&&(e.getAttribute('href')||'')===b.href&&(e.getAttribute('onclick')||'')===b.onclick);
  if(buttons.length!==1)return fail('O comando Salvar mudou depois da conferência.');
  const button=buttons[0],form=button.form||button.closest('form');
  const next={nonce:command.nonce,issued:false,started:false,finished:false,error:'',validation:''};
  window[key]=next;
  let manager;
  try{manager=window.Sys?.WebForms?.PageRequestManager?.getInstance?.();}catch{}
  const begin=()=>{next.started=true;};
  const end=(_sender,args)=>{next.started=true;next.finished=true;const error=args?.get_error?.();if(error)next.error=error.message||String(error);cleanup();};
  const unload=()=>{next.started=true;};
  function cleanup(){
    manager?.remove_beginRequest?.(begin);manager?.remove_endRequest?.(end);
    form?.removeEventListener('submit',begin,true);window.removeEventListener('beforeunload',unload);
  }
  next.cleanup=cleanup;
  manager?.add_beginRequest?.(begin);manager?.add_endRequest?.(end);
  form?.addEventListener('submit',begin,true);window.addEventListener('beforeunload',unload);
  // Capture synchronous validation, but let the portal's normal handler decide
  // which values are valid. Never bypass its validation or call form.submit().
  setTimeout(()=>{
    try{
      next.issued=true;button.click();
      const invalid=inputs.find(e=>e.isConnected&&!e.validity.valid);
      if(invalid){next.validation='O SophiA recusou um campo ao salvar.';next.finished=true;cleanup();}
    }catch(e){next.error=e.message||String(e);next.finished=true;cleanup();}
  },0);
  return {ok:true,issued:true};
}
