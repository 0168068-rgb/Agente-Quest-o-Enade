(() => {
  if(window.top!==window||location.hostname!=='portal.sophia.com.br')return;
  const version=chrome.runtime.getManifest().version,previous=globalThis.__SMARTDUCK_WIDGET_V1__;
  if(previous?.host?.isConnected&&previous.version===version)return;
  previous?.host?.remove();
  const host=document.createElement('div');host.id='smartduck-widget';host.dataset.smartduckVersion=version;const root=host.attachShadow({mode:'closed'});
  const style=document.createElement('style');style.textContent=':host{all:initial;position:fixed;inset:0;pointer-events:none;z-index:2147483600}.duck{position:fixed;right:22px;top:110px;width:64px;height:64px;border:0;padding:4px;background:transparent;pointer-events:auto;touch-action:none;cursor:pointer;filter:drop-shadow(0 5px 8px #17345a55)}.duck img{width:100%;height:100%;pointer-events:none}.duck:focus-visible{outline:3px solid #ed6108;border-radius:50%}.notice{position:fixed;right:20px;top:185px;max-width:260px;background:#17345a;color:white;padding:12px;border-radius:8px;font:13px system-ui;pointer-events:auto}.notice[hidden]{display:none}@media print{:host{display:none}}';
  const button=document.createElement('button');button.className='duck';button.type='button';button.setAttribute('aria-label','Abrir SmartDuck no painel lateral');button.title='SmartDuck · clique para abrir ou arraste para mover';
  const img=document.createElement('img');img.src=chrome.runtime.getURL('assets/duck-head.svg');img.alt='Pato SmartDuck';img.draggable=false;button.append(img);
  const notice=document.createElement('div');notice.className='notice';notice.hidden=true;notice.setAttribute('role','status');root.append(style,button,notice);document.documentElement.append(host);globalThis.__SMARTDUCK_WIDGET_V1__={host,version};
  void chrome.runtime.sendMessage({type:'smartduck.prepare'}).catch(()=>{});
  let drag=null,suppress=false;
  button.onclick=()=>{if(suppress){suppress=false;return;}chrome.runtime.sendMessage({type:'smartduck.openPanel'}).then(r=>{notice.hidden=!!r?.ok;if(!r?.ok)notice.textContent=r?.message||'Clique no ícone SmartDuck da barra do Chrome.';}).catch(()=>{notice.hidden=false;notice.textContent='Atualize o SophiA após recarregar a extensão.';});};
  function position(x,y){button.style.left=Math.max(4,Math.min(innerWidth-68,x))+'px';button.style.top=Math.max(4,Math.min(innerHeight-68,y))+'px';button.style.right='auto';}
  button.addEventListener('pointerdown',e=>{if(e.button!==0)return;const r=button.getBoundingClientRect();drag={id:e.pointerId,x:e.clientX,y:e.clientY,left:r.left,top:r.top,moved:false};button.setPointerCapture(e.pointerId);});
  button.addEventListener('pointermove',e=>{if(!drag||drag.id!==e.pointerId)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;if(Math.hypot(dx,dy)>5)drag.moved=true;if(drag.moved){e.preventDefault();position(drag.left+dx,drag.top+dy);}});
  const finish=e=>{if(!drag||drag.id!==e.pointerId)return;suppress=drag.moved;drag=null;try{button.releasePointerCapture(e.pointerId);}catch{}setTimeout(()=>{suppress=false;},0);};button.addEventListener('pointerup',finish);button.addEventListener('pointercancel',finish);
})();
