// Runs only in the SophiA tab. Uses its visible controls and normal page events.
export function portalNavigation(command={action:'state'}){
  const norm=v=>String(v??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toUpperCase().replace(/\s+/g,' ').trim();
  const visible=e=>e.isConnected&&e.getClientRects().length>0&&getComputedStyle(e).display!=='none'&&getComputedStyle(e).visibility!=='hidden';
  const clean=e=>(e.innerText??e.textContent??e.value??'').replace(/\s+/g,' ').trim();
  if(location.protocol!=='https:'||location.hostname!=='portal.sophia.com.br')return {ok:false,message:'Entre no SophiA da sua instituição.'};
  const onNotes=/^\/SophiA_\d+\/LancNotas\.aspx$/i.test(location.pathname);
  if(command.action==='enter'){
    if(onNotes)return {ok:true,unchanged:true};
    const school=location.pathname.match(/^\/SophiA_\d+\//i)?.[0];
    const links=Array.from(document.querySelectorAll('a[href]')).filter(visible).map(e=>{try{return new URL(e.getAttribute('href'),location.href);}catch{return null;}}).filter(u=>u&&u.origin===location.origin&&school&&u.pathname.toLowerCase()===(school+'LancNotas.aspx').toLowerCase());
    const urls=[...new Set(links.map(u=>u.href))];
    if(urls.length!==1)return {ok:false,message:'Entre na sua conta do SophiA. O menu Notas precisa estar disponível para realizar o lote.'};
    setTimeout(()=>location.assign(urls[0]),0);return {ok:true,issued:true};
  }
  if(!onNotes)return {ok:false,code:'SESSION_UNAVAILABLE',message:'Ao clicar em Realizar, o SmartDuck abrirá Notas na mesma aba. Entre na sua conta do SophiA primeiro.'};
  if(Array.from(document.querySelectorAll('input[type="password"]')).some(visible))return {ok:false,code:'SESSION_UNAVAILABLE',message:'A sessão do SophiA expirou. Entre novamente na mesma aba.'};
  const dialogs=Array.from(document.querySelectorAll('.cortinaDialogo,[role="dialog"],.dialogo')).filter(visible).filter(e=>!String(e.className).includes('cc-')&&!/cookieconsent/i.test(e.getAttribute('aria-label')||''));
  if(dialogs.length){
    const text=norm(dialogs.map(clean).join(' '));
    const success=dialogs.length===1&&/(?:NOTAS?|LANCAMENTOS?|DADOS).{0,40}(?:GRAVAD|SALV|REGISTRAD).{0,40}SUCESSO/.test(text)&&!/(?:\bNAO\b|\bERRO\b|\bFALHA\b|\bDESEJA\b|\bCONFIRMA)/.test(text);
    const buttons=Array.from(dialogs[0].querySelectorAll('a,button,input[type="button"],input[type="submit"]')).filter(e=>visible(e)&&!e.disabled);
    const cancellations=buttons.filter(e=>['CANCELAR','NÃO','NAO','VOLTAR','FECHAR'].includes(norm(e.value||clean(e))));
    const confirmations=/\b(?:DESEJA|CONFIRMA|CONFIRMAR|CERTEZA|EXCLUIR|APAGAR|REMOVER)\b/.test(text);
    const passive=dialogs.length===1&&!confirmations&&buttons.length===1&&['OK','FECHAR'].includes(norm(buttons[0].value||clean(buttons[0])));
    const dismiss=passive?buttons[0]:cancellations.length===1?cancellations[0]:null;
    if(command.action==='acknowledge'&&dismiss){setTimeout(()=>dismiss.click(),0);return {ok:true,issued:true};}
    return {ok:false,code:'PORTAL_NOTICE',dialog:true,savedNotice:success,dismissible:!!dismiss,
      message:success?'Notas gravadas com sucesso.':'Mensagem do SophiA: '+clean(dialogs[0]).slice(0,500)};
  }
  const controls={};
  for(const kind of ['periodo','unidade','turma','etapa','disciplina']){
    const matches=Array.from(document.querySelectorAll('select')).filter(e=>(e.id+' '+e.name).toLowerCase().includes(kind));
    if(matches.length!==1)return {ok:false,message:'Não foi possível identificar unicamente o filtro '+kind+'.'};
    const e=matches[0];
    controls[kind]={id:e.id||e.name,value:e.value,text:e.options[e.selectedIndex]?.text.trim()||'',disabled:e.disabled,options:Array.from(e.options).filter(o=>!o.disabled&&o.value&&!/^[-–—\s]*(selecione|fim das etapas|todos|todas)/i.test(o.text.trim())).map(o=>({value:o.value,text:o.text.trim()}))};
  }
  const allButtons=Array.from(document.querySelectorAll('button,a,input[type="button"],input[type="submit"]')).filter(e=>visible(e)&&!e.disabled);
  const findButtons=labels=>allButtons.filter(e=>labels.includes(norm(e.value||clean(e))));
  const pageLinks=allButtons.map(e=>{
    const raw=(e.getAttribute('href')||'')+' '+(e.getAttribute('onclick')||'');
    const token=raw.match(/Page\$(\d+|Next|Prev|First|Last)\b/i)?.[1];
    return token?{element:e,token,text:clean(e)}:null;
  }).filter(Boolean);
  const gradeTables=Array.from(document.querySelectorAll('table')).filter(t=>visible(t)&&Array.from(t.rows).some(r=>Array.from(r.cells).some(c=>/^(CODIGO|RA|MATRICULA|CODIGO DO ALUNO)$/.test(norm(clean(c))))));
  const pagerText=gradeTables.map(t=>clean(t)).join(' ');
  const paging=pagerText.match(/P[aá]gina\s+(\d+)\s*(?:de|\/)\s*(\d+)/i);
  const page={numbers:[...new Set(pageLinks.filter(x=>/^\d+$/.test(x.token)).map(x=>Number(x.token)))],next:pageLinks.some(x=>/^Next$/i.test(x.token)),current:paging?Number(paging[1]):null,total:paging?Number(paging[2]):null};
  const signature=JSON.stringify(Object.values(controls).map(c=>[c.id,c.value,c.text,c.disabled,c.options]));
  const busy=document.readyState!=='complete'||!!window.Sys?.WebForms?.PageRequestManager?.getInstance?.()?.get_isInAsyncPostBack?.();
  const greeting=Array.from(document.querySelectorAll('[id*="dadosUsuario"],[id*="usuario"],[id*="Usuario"]')).filter(visible).map(clean).find(t=>/^Ol[aá][,\s]/i.test(t));
  const account={name:greeting?.replace(/^Ol[aá][,\s]+/i,'').split(/Trocar senha|Sair|\|/i)[0].replace(/[.\s]+$/,'')||'',school:location.origin+location.pathname.match(/^\/SophiA_\d+\//i)?.[0]};
  if(command.account&&(command.account.school!==account.school||command.account.name&&command.account.name!==account.name))return {ok:false,code:'ACCOUNT_CHANGED',message:'A conta do SophiA mudou durante o lote.'};
  if(command.action==='state')return {ok:true,controls,page,signature,busy,account,url:location.origin+location.pathname};
  if(busy)return {ok:false,message:'Aguarde o portal terminar de carregar.'};
  if(command.signature!==signature)return {ok:false,message:'Os filtros do portal mudaram durante o lote. Processo interrompido.'};
  if(command.action==='new'&&gradeTables.some(t=>Array.from(t.querySelectorAll('input[type="text"],input[type="number"],input:not([type])')).some(e=>visible(e)&&e.value!==e.defaultValue)))return {ok:false,code:'MANUAL_CHANGES',message:'Há notas alteradas e ainda não confirmadas nesta tela. Salve ou descarte essas alterações no SophiA antes de realizar o lote.'};
  if(command.action==='select'){
    const c=controls[command.kind];
    if(!c||c.disabled||!c.options.some(o=>o.value===command.value&&o.text===command.text))return {ok:false,code:'OPTION_UNAVAILABLE',message:'A opção de '+command.kind+' não está disponível nesta turma.'};
    if(c.value===command.value)return {ok:true,unchanged:true};
    const el=Array.from(document.querySelectorAll('select')).find(e=>(e.id||e.name)===c.id);
    setTimeout(()=>{el.value=command.value;el.dispatchEvent(new Event('change',{bubbles:true}));},0);
    return {ok:true,issued:true};
  }
  let matches=[];
  if(command.action==='new')matches=findButtons(['NOVO FILTRO']);
  if(command.action==='search')matches=findButtons(['BUSCAR','LISTAR']);
  if(command.action==='page')matches=pageLinks.filter(p=>String(p.token).toUpperCase()===String(command.page).toUpperCase()).map(p=>p.element);
  if(matches.length!==1)return {ok:false,message:'Não foi possível identificar unicamente o comando '+command.action+' no SophiA.'};
  const button=matches[0];setTimeout(()=>button.click(),0);
  return {ok:true,issued:true};
}
