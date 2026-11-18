(async function(root){
 'use strict';
 const KEY='smartfoxWindowLayoutV1',SIZE=60;
 function clampPosition(x,y,width,height){
  const bound=(v,max)=>Math.max(0,Math.min(Number.isFinite(v)?v:0,Math.max(0,max-SIZE)));
  return {x:bound(x,width),y:bound(y,height)};
 }
 root.SmartFoxWindowGeometry={clampPosition};
 const doc=root.document;if(!doc||root.top!==root.self)return;
 async function waitFor(id){const found=doc.getElementById(id);if(found)return found;return new Promise(resolve=>{const observer=new MutationObserver(()=>{const el=doc.getElementById(id);if(el){observer.disconnect();resolve(el);}});observer.observe(doc.documentElement,{childList:true,subtree:true});});}
 const launcher=doc.getElementById('sf-tools-launcher')||await waitFor('sf-tools-launcher');
 let panel=doc.getElementById('aab-panel');
 if(!launcher)return;
 doc.documentElement.classList.add('sf-unified-launcher');
 let position=null,fullscreen=true,touched=false,drag=null,suppressClick=false,returnToPanel=false;
 const store=root.chrome?.storage?.local;
 function persist(){touched=true;try{Promise.resolve(store?.set({[KEY]:{position,fullscreen}})).catch(()=>{});}catch{}}
 function place(p){position=clampPosition(p.x,p.y,root.innerWidth,root.innerHeight);launcher.style.left=position.x+'px';launcher.style.top=position.y+'px';launcher.style.right='auto';launcher.style.bottom='auto';}
 place({x:root.innerWidth-76,y:16});
 function hideInterface(){panel?.classList.remove('aab-open');doc.getElementById('sf-tools-dialog')?.close();doc.documentElement.classList.add('sf-interface-hidden');}
 root.addEventListener('keydown',e=>{if(e.altKey&&e.shiftKey&&e.code==='KeyF'){e.preventDefault();doc.documentElement.classList.toggle('sf-interface-hidden',!doc.documentElement.classList.contains('sf-interface-hidden'));}});
 const hub=doc.getElementById('sf-tools-dialog');
 if(hub){const actions=doc.createElement('div');actions.className='sf-display-actions';for(const [label,action] of [['Sobre esta versão',()=>root.SmartFoxAccess?.openAccount()],['Ocultar · Alt+Shift+F para voltar',hideInterface]]){const b=doc.createElement('button');b.type='button';b.textContent=label;b.onclick=()=>{hub.close();action();};actions.append(b);}hub.append(actions);}
 launcher.classList.add('sf-fox-only');
 launcher.setAttribute('aria-label','Abrir SmartFox. Arraste a raposa para mover. Use Alt e as setas para mover pelo teclado.');
 const img=launcher.querySelector('img');if(img){img.draggable=false;img.src=chrome.runtime.getURL('icons/icon-128.png');}
 let toggle;
 function mode(){if(!panel)return;panel.classList.toggle('sf-fullscreen',fullscreen);toggle?.setAttribute('aria-pressed',String(fullscreen));if(toggle){toggle.textContent=fullscreen?'Restaurar janela':'Tela cheia';toggle.title=fullscreen?'Voltar à janela menor':'Ocupar toda a área da página';}}
 function setupPanel(){
  const header=panel.querySelector('.aab-header'),close=doc.getElementById('aab-close');
  const controls=doc.createElement('div');controls.className='sf-window-actions';
  const tools=doc.createElement('button');tools.type='button';tools.textContent='Ferramentas';tools.onclick=()=>{panel.classList.remove('aab-open');root.SmartFoxTools?.open();};controls.append(tools);
  toggle=doc.createElement('button');toggle.type='button';toggle.id='sf-window-maximize';toggle.onclick=()=>{fullscreen=!fullscreen;mode();persist();};controls.append(toggle);
  const hide=doc.createElement('button');hide.type='button';hide.textContent='Ocultar';hide.title='Ocultar SmartFox. Alt+Shift+F para mostrar novamente.';hide.onclick=hideInterface;controls.append(hide);
  if(close){close.title='Recolher para a raposa sem interromper o trabalho';close.setAttribute('aria-label','Recolher SmartFox para a raposa');controls.append(close);close.addEventListener('click',()=>{returnToPanel=true;queueMicrotask(()=>launcher.focus());});}
  header?.append(controls);mode();
  function visibility(){const opened=panel.classList.contains('aab-open');launcher.classList.toggle('sf-panel-visible',opened);panel.inert=!opened;launcher.setAttribute('aria-expanded',String(opened));if(opened)returnToPanel=true;}
  new MutationObserver(visibility).observe(panel,{attributes:true,attributeFilter:['class']});visibility();
 }
 if(panel)setupPanel();else waitFor('aab-panel').then(el=>{panel=el;setupPanel();});
 launcher.addEventListener('pointerdown',e=>{if(e.button!==0)return;const rect=launcher.getBoundingClientRect();drag={id:e.pointerId,startX:e.clientX,startY:e.clientY,x:rect.left,y:rect.top,moved:false};suppressClick=false;launcher.setPointerCapture?.(e.pointerId);});
 launcher.addEventListener('pointermove',e=>{if(!drag||drag.id!==e.pointerId)return;const dx=e.clientX-drag.startX,dy=e.clientY-drag.startY;if(Math.hypot(dx,dy)>5)drag.moved=true;if(!drag.moved)return;e.preventDefault();launcher.classList.add('sf-dragging');place({x:drag.x+dx,y:drag.y+dy});});
 function finish(e){if(!drag||drag.id!==e.pointerId)return;suppressClick=drag.moved;if(drag.moved)persist();drag=null;launcher.classList.remove('sf-dragging');if(launcher.hasPointerCapture?.(e.pointerId))launcher.releasePointerCapture(e.pointerId);}
 launcher.addEventListener('pointerup',finish);launcher.addEventListener('pointercancel',finish);launcher.addEventListener('lostpointercapture',finish);
 launcher.addEventListener('click',e=>{
  if(suppressClick&&e.detail!==0){suppressClick=false;e.preventDefault();e.stopImmediatePropagation();return;}
  if(returnToPanel&&panel&&launcher.id!=='aab-launcher'){
   e.preventDefault();e.stopImmediatePropagation();doc.getElementById('aab-launcher')?.click();
  }
 },true);
 launcher.addEventListener('keydown',e=>{if(!e.altKey||!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key))return;e.preventDefault();const r=launcher.getBoundingClientRect(),step=e.shiftKey?40:10;place({x:r.left+(e.key==='ArrowRight'?step:e.key==='ArrowLeft'?-step:0),y:r.top+(e.key==='ArrowDown'?step:e.key==='ArrowUp'?-step:0)});persist();});
 root.addEventListener('resize',()=>{if(position)place(position);});
 try{Promise.resolve(store?.get(KEY)).then(data=>{if(touched||drag)return;const saved=data?.[KEY];if(typeof saved?.fullscreen==='boolean')fullscreen=saved.fullscreen;if(saved?.position)place(saved.position);mode();}).catch(()=>{});}catch{}
})(typeof window==='undefined'?globalThis:window);
