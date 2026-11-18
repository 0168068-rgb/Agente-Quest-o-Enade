/* SmartFox 11.0 — Minhas Instituições, using only links exposed by AvaliA. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.SmartFoxBankContext=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const normalize=value=>String(value||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/\s+/g,' ').trim().toLowerCase();
  function snapshot(doc) {
    const rawInstitutions=Array.from(doc.querySelectorAll('a[href^="/Contexto/AlterarInstituicao/"]')).map(a=>{
      const href=a.getAttribute('href')||'',match=href.match(/^\/Contexto\/AlterarInstituicao\/([1-9]\d*)$/);
      return match?{id:match[1],name:a.textContent.trim(),href,selected:Boolean(a.parentElement?.querySelector('.fa-check')||a.getAttribute('aria-current')==='true'),general:normalize(a.textContent)==='papeis gerais'}:null;
    }).filter(Boolean);
    const byId=new Map();
    for(const item of rawInstitutions){const prior=byId.get(item.id);byId.set(item.id,prior?{...prior,selected:prior.selected||item.selected}:item);}
    const institutions=[...byId.values()];
    const selected=institutions.filter(i=>i.selected);
    const roles=Array.from(doc.querySelectorAll('#usuarioPerfil ul a[href]')).map(a=>({name:a.textContent.trim(),href:a.getAttribute('href')})).filter(r=>/^\/Contexto\/AlterarPapel\/[1-9]\d*$/.test(r.href));
    return {institutions,current:selected.length===1?selected[0]:null,roles,role:doc.querySelector('#usuarioPerfil > a')?.textContent.trim()||'',owner:normalize(doc.querySelector('a.user-profile')?.textContent)};
  }
  function choose(state,preferredId) {
    const candidates=state.institutions.filter(i=>!i.general);
    const match=preferredId?candidates.find(i=>i.id===String(preferredId)):state.current&&!state.current.general?state.current:candidates.length===1?candidates[0]:null;
    if(!match)throw new Error('Selecione a instituição de destino em Likes do banco → Instituição. Nenhuma instituição será escolhida apenas pelo nome da disciplina.');
    return match;
  }
  function create({fetch:send,parseDocument,expectedOwner,onProgress=()=>{},normalizeOwner=normalize}) {
    async function page(path) {
      const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),25000);
      try {
        const response=await send(path,{method:'GET',credentials:'same-origin',cache:'no-store',redirect:'follow',signal:controller.signal});
        if(!response.ok)throw new Error('O AvaliA não confirmou a troca em Minhas Instituições.');
        const state=snapshot(parseDocument(await response.text()));
        // AvaliA fills #usuarioPerfil with jQuery.load('/Contexto') after HTML load.
        if(!state.role) {
          const profile=await send('/Contexto',{method:'GET',credentials:'same-origin',cache:'no-store',redirect:'error',headers:{'X-Requested-With':'XMLHttpRequest'},signal:controller.signal});
          if(!profile.ok)throw new Error('O AvaliA não carregou o perfil da instituição.');
          const roleState=snapshot(parseDocument('<div id="usuarioPerfil">'+await profile.text()+'</div>'));
          state.role=roleState.role;state.roles=roleState.roles;
        }
        if(!state.current || !state.owner || normalizeOwner(state.owner)!==normalizeOwner(expectedOwner))throw new Error('O AvaliA não confirmou a instituição e o professor. Confira a sessão.');
        return state;
      } finally {clearTimeout(timer);}
    }
    const read=()=>page('/Home/Index');
    async function enter(id,role='Professor/Tutor') {
      let state=await read();
      const target=state.institutions.find(i=>i.id===String(id));
      if(!target)throw new Error('A instituição do envio não aparece em Minhas Instituições neste perfil.');
      if(state.current.id!==target.id) {
        onProgress(`Minhas Instituições → ${target.name}…`);
        state=await page(target.href);
        if(state.current.id!==target.id)throw new Error('A troca de instituição não foi confirmada. Nenhum like foi alterado.');
      }
      if(normalize(state.role)!==normalize(role)) {
        const roles=state.roles.filter(r=>normalize(r.name)===normalize(role));
        if(roles.length!==1)throw new Error(`A instituição não oferece o perfil ${role}.`);
        state=await page(roles[0].href);
      }
      if(state.current.id!==target.id || normalize(state.role)!==normalize(role))throw new Error('O contexto do AvaliA não corresponde à instituição e ao perfil solicitados.');
      return state;
    }
    async function run(id,task) {
      const previous=await read();
      try {const state=await enter(id);return await task(state);}
      finally {await enter(previous.current.id,previous.role);}
    }
    async function assertCurrent(id) {
      const state=await read();
      if(state.current.id!==String(id)||normalize(state.role)!=='professor/tutor')throw new Error('A instituição ou o perfil mudou durante a operação. Retome no contexto correto; nenhum novo like será alterado.');
      return state;
    }
    return {read,enter,run,assertCurrent};
  }
  return Object.freeze({snapshot,choose,create,normalize});
});
