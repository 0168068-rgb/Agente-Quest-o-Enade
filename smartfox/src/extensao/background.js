"use strict";
// Autonomous edition: no account, activation service or device registry.
importScripts("integrity-check.js", "smartfox-config.js");
const CONFIG = globalThis.SMARTFOX_CONFIG;
const AVALIA_ORIGIN = "https://avalia.grupoa.com.br";
let integrityPromise = null;
async function packageIntegrity() {
  if (!globalThis.SmartFoxIntegrity?.verify) return {ok:false,failures:[{file:"integrity-check.js",reason:"unavailable"}]};
  integrityPromise ||= globalThis.SmartFoxIntegrity.verify();
  return integrityPromise;
}
function localStatus(integrity) {
  return {state:integrity.ok?"standalone_ready":"package_integrity_failed",authorized:Boolean(integrity.ok),configured:true,standalone:true,version:CONFIG.version,requiresActivation:false,requiresAdministrator:false,integrity};
}
function trustedSender(sender) {
  if(sender.id!==chrome.runtime.id)return false;
  const url=sender.url||sender.tab?.url||"";
  if(url.startsWith(chrome.runtime.getURL("")))return true;
  try{return new URL(url).origin===AVALIA_ORIGIN&&sender.frameId===0;}catch(_){return false;}
}
async function avaliaTabs() {
  const tabs=await chrome.tabs.query({url:`${AVALIA_ORIGIN}/*`});
  return tabs.filter(t=>Number.isInteger(t.id)&&t.url?.startsWith(`${AVALIA_ORIGIN}/`)).map(t=>({id:t.id,windowId:t.windowId,active:Boolean(t.active),path:new URL(t.url).pathname,title:t.title||"AvaliA"}));
}
chrome.runtime.onInstalled.addListener(details=>{
  packageIntegrity().catch(()=>null);
  if(details.reason==="install")chrome.tabs.create({url:chrome.runtime.getURL("welcome.html")}).catch(()=>null);
});
chrome.runtime.onMessage.addListener((message,sender,sendResponse)=>{
  if(!message||!String(message.type||"").startsWith("SF_")||!trustedSender(sender))return false;
  (async()=>{
    const integrity=await packageIntegrity();
    if(message.type==="SF_STATUS")return localStatus(integrity);
    if(!integrity.ok)throw Object.assign(new Error("O pacote está incompleto ou foi alterado. Extraia novamente o SmartFox Autônomo e recarregue a extensão."),{code:"PACKAGE_INTEGRITY_FAILED"});
    switch(message.type){
      case "SF_REQUEST_DISCIPLINES":return localStatus(integrity);
      case "SF_GENERATE_QUESTIONS":throw Object.assign(new Error("Use a criação local no Banco de materiais ou importe uma avaliação em Word. Esta edição não utiliza um serviço de IA."),{code:"AI_DISABLED"});
      case "SF_CANCEL_GENERATION":return {canceled:false};
      case "SF_ANNOUNCEMENTS":return {state:"available",standalone:true,announcements:[]};
      case "SF_AVALIA_TABS":return {tabs:await avaliaTabs(),currentTabId:sender.tab?.id};
      case "SF_FOCUS_AVALIA_TAB":{
        const tab=(await avaliaTabs()).find(t=>t.id===Number(message.tabId));
        if(!tab)throw new Error("Esta aba do AvaliA foi fechada. Atualize a lista de abas.");
        await chrome.tabs.update(tab.id,{active:true});
        if(Number.isInteger(tab.windowId))await chrome.windows.update(tab.windowId,{focused:true});
        return {focused:true};
      }
      case "SF_AVALIA_PRODUCTS":{
        if(!Number.isInteger(sender.tab?.id)||!message.owner||!(/^[1-9]\d*$/.test(String(message.institutionId||""))))throw new Error("O pedido de produtos não identifica o professor e a instituição.");
        const tabs=(await avaliaTabs()).filter(t=>/^\/Professor(?:\/|$)/i.test(t.path));
        for(const tab of tabs){
          let timer;
          try{
            const response=await Promise.race([
              chrome.tabs.sendMessage(tab.id,{type:"SF_READ_PAGE_PRODUCTS",owner:message.owner,institutionId:String(message.institutionId)}),
              new Promise((_,reject)=>{timer=setTimeout(()=>reject(new Error("A aba não respondeu.")),1500);})
            ]);
            const data=response?.data;
            if(response?.ok&&data?.owner===message.owner&&data?.institutionId===String(message.institutionId)&&Array.isArray(data.products)&&data.products.length)return data;
          }catch(_){/* Closed or outdated tabs cannot supply a snapshot. */}
          finally{clearTimeout(timer);}
        }
        return {products:[]};
      }
      default:throw Object.assign(new Error("Comando indisponível nesta edição autônoma."),{code:"UNKNOWN_ACTION"});
    }
  })().then(data=>sendResponse({ok:true,data})).catch(error=>sendResponse({ok:false,error:error?.message||String(error),code:error?.code||"SMARTFOX_ERROR"}));
  return true;
});
