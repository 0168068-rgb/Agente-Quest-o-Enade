const key=tabId=>'smartduck.session.'+tabId;
export async function saveSession(tabId,value){
  const input=new TextEncoder().encode(JSON.stringify(value));
  const bytes=new Uint8Array(await new Response(new Blob([input]).stream().pipeThrough(new CompressionStream('gzip'))).arrayBuffer());
  let binary='';for(let i=0;i<bytes.length;i+=16384)binary+=String.fromCharCode(...bytes.subarray(i,i+16384));
  const packed=btoa(binary);
  if(packed.length>9*1024*1024)throw new Error('O lote excede a memória de sessão disponível. Use menos arquivos neste lote.');
  await chrome.storage.session.set({[key(tabId)]:packed});
}
export async function loadSession(tabId){
  const value=(await chrome.storage.session.get(key(tabId)))[key(tabId)];if(!value)return null;
  const bytes=Uint8Array.from(atob(value),c=>c.charCodeAt(0));
  return JSON.parse(await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text());
}
export const clearSession=tabId=>chrome.storage.session.remove(key(tabId));
