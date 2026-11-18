(function(){
  "use strict";
  if(window.top!==window.self)return;
  let currentStatus=null,pending=null,dialog=null,previousFocus=null;
  function escapeHtml(value){return String(value??"").replace(/[&<>"']/g,char=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[char]));}
  function readStatus(){
    if(pending)return pending;
    pending=new Promise((resolve,reject)=>{
      const unavailable=()=>new Error("Recarregue esta aba do AvaliA para reconectar o SmartFox Autônomo.");
      if(typeof chrome==="undefined"||!chrome.runtime?.sendMessage){reject(unavailable());return;}
      const timer=setTimeout(()=>reject(new Error("O SmartFox não respondeu. Recarregue a extensão e esta aba.")),15000);
      try{
        chrome.runtime.sendMessage({type:"SF_STATUS"},response=>{
          clearTimeout(timer);
          if(chrome.runtime.lastError){reject(unavailable());return;}
          if(!response?.ok){reject(new Error(response?.error||"Não foi possível conferir os arquivos do SmartFox."));return;}
          const detected=window.SmartFoxIdentity?.extractAvaliaIdentity(document);
          currentStatus={...response.data,identity:{avaliaName:detected?.name||"",detected:Boolean(detected?.name),verified:false}};
          resolve(currentStatus);
        });
      }catch(_){clearTimeout(timer);reject(unavailable());}
    }).finally(()=>{pending=null;});
    return pending;
  }
  function ensureButton(){
    if(document.getElementById("sf-account-button"))return;
    const button=document.createElement("button");button.id="sf-account-button";button.type="button";button.title="Sobre o SmartFox Autônomo";
    button.innerHTML=`<img src="${escapeHtml(chrome.runtime.getURL("icons/icon-48.png"))}" alt=""><span>Autônomo</span>`;
    button.addEventListener("click",openAccount);document.documentElement.appendChild(button);
  }
  function showInfo(error){
    if(!dialog){
      dialog=document.createElement("dialog");dialog.id="sf-standalone-dialog";dialog.setAttribute("aria-labelledby","sf-standalone-title");
      dialog.addEventListener("close",()=>previousFocus?.focus?.());document.documentElement.appendChild(dialog);
    }
    const name=currentStatus?.identity?.avaliaName;
    dialog.innerHTML=`<header><div><small>EDIÇÃO AUTÔNOMA · 11.2</small><h2 id="sf-standalone-title">SmartFox pronto para você</h2></div><button type="button" data-close aria-label="Fechar">×</button></header>
    <div class="sf-standalone-body">
    ${error?`<p class="sf-standalone-error" role="alert">${escapeHtml(error.message)}</p>`:'<p class="sf-standalone-ready">Pronto para usar. Sem cadastro, chave de ativação ou aprovação de computador.</p>'}
    <p>Abra <b>Ferramentas</b> para preparar avaliações, acessar seu acervo ou trabalhar na correção discursiva.</p>
    <dl><dt>Acesso ao SmartFox</dt><dd>Local, sem prazo de ativação e sem administrador.</dd><dt>Perfil no AvaliA</dt><dd>${escapeHtml(name||"Entre normalmente na sua conta do AvaliA.")}</dd><dt>Seus materiais</dt><dd>Salvos neste perfil do navegador. Exporte um backup no Banco de materiais antes de trocar de computador ou remover a extensão.</dd></dl>
    <p>O AvaliA continua usando seu login habitual e precisa de internet. A criação de questões usa os materiais locais; não requer chave de IA.</p>
    <p class="sf-standalone-muted">Versão 11.2.0 · Base: correções R6 de outubro de 2026. Atualizações são feitas substituindo os arquivos da extensão e clicando em Recarregar no navegador.</p></div>`;
    dialog.querySelector("[data-close]").addEventListener("click",()=>dialog.close());
    if(!dialog.open){previousFocus=document.activeElement;dialog.showModal();}
    dialog.querySelector("[data-close]").focus();
  }
  async function assertAuthorized(){
    let status;
    try{status=await readStatus();if(!status.authorized||!status.standalone)throw new Error("O pacote está incompleto ou é de outra edição. Extraia novamente o SmartFox Autônomo e recarregue a extensão.");}
    catch(error){showInfo(error);throw error;}
    ensureButton();return status;
  }
  async function requireAuthorized(){try{await assertAuthorized();return true;}catch(_){return false;}}
  async function openAccount(){try{const status=await readStatus();if(!status.authorized)throw new Error("Confira os arquivos do pacote e recarregue a extensão.");showInfo();}catch(error){showInfo(error);}}
  window.SmartFoxAccess=Object.freeze({version:"11.2.0",requireAuthorized,assertAuthorized,openAccount,openAnnouncements:openAccount,refreshAnnouncements:async()=>({state:"available",announcements:[]}),getStatus:()=>currentStatus?JSON.parse(JSON.stringify(currentStatus)):null});
})();
