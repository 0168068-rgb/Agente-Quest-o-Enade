const portal=url=>/^https:\/\/portal\.sophia\.com\.br\//.test(url||'');
const configure=async tab=>{const path='painel.html?tab='+tab.id,enabled=portal(tab.url),current=await chrome.sidePanel.getOptions({tabId:tab.id});if(current.path!==path||current.enabled!==enabled)await chrome.sidePanel.setOptions({tabId:tab.id,path,enabled});};
chrome.sidePanel.setPanelBehavior({openPanelOnActionClick:true}).catch(()=>{});
chrome.tabs.onUpdated.addListener((id,change,tab)=>{if(change.url||change.status==='complete')void configure(tab).catch(()=>{});});
chrome.runtime.onInstalled.addListener(()=>{void chrome.tabs.query({url:'https://portal.sophia.com.br/*'}).then(tabs=>Promise.all(tabs.map(async tab=>{await configure(tab);await chrome.scripting.executeScript({target:{tabId:tab.id,frameIds:[0]},files:['widget.js']});}))).catch(()=>{});});
chrome.runtime.onMessage.addListener((message,sender,respond)=>{
  if(sender.id!==chrome.runtime.id||!Number.isInteger(sender.tab?.id)||!portal(sender.url))return;
  if(message?.type==='smartduck.prepare'){configure(sender.tab).then(()=>respond({ok:true})).catch(()=>respond({ok:false}));return true;}
  if(message?.type==='smartduck.openPanel'){
    chrome.sidePanel.open({tabId:sender.tab.id}).then(()=>respond({ok:true})).catch(()=>respond({ok:false,message:'Clique no ícone SmartDuck da barra do Chrome para abrir o painel lateral.'}));return true;
  }
});
chrome.commands.onCommand.addListener(command=>{if(command==='toggle-smartduck')void chrome.tabs.query({active:true,currentWindow:true}).then(([tab])=>{if(tab&&portal(tab.url))return chrome.sidePanel.open({tabId:tab.id});}).catch(()=>{});});

chrome.tabs.onRemoved.addListener(tabId=>{void chrome.storage.session.remove('smartduck.session.'+tabId);});
