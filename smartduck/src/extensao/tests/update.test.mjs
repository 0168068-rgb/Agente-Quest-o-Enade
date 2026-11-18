import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {JSDOM} from './portal-fixture.mjs';

test('Atualização substitui o botão antigo da própria extensão sem duplicar o painel',async()=>{
  const dom=new JSDOM('<html><body></body></html>',{url:'https://portal.sophia.com.br/SophiA_999/LancNotas.aspx',runScripts:'outside-only'});
  try{
    const w=dom.window,old=w.document.createElement('div');old.id='smartduck-widget';w.document.documentElement.append(old);w.__SMARTDUCK_WIDGET_V1__={host:old};
    w.chrome={runtime:{getManifest:()=>({version:'1.9.0'}),getURL:p=>'chrome-extension://fixture/'+p,sendMessage:async()=>({ok:true})}};
    const code=await fs.readFile(new URL('../widget.js',import.meta.url),'utf8');w.eval(code);
    assert.equal(old.isConnected,false);assert.equal(w.document.querySelectorAll('#smartduck-widget').length,1);
    const current=w.document.getElementById('smartduck-widget');assert.equal(current.dataset.smartduckVersion,'1.9.0');
    w.eval(code);assert.equal(w.document.getElementById('smartduck-widget'),current);
  }finally{dom.window.close();}
});
test('Atualização reconfigura e injeta o botão apenas nas abas já abertas do SophiA',async()=>{
  const dom=new JSDOM('',{runScripts:'outside-only'}),calls=[];let installed;
  try{
    dom.window.chrome={
      sidePanel:{getOptions:async()=>({}),setOptions:async v=>calls.push(['configure',v]),setPanelBehavior:async()=>{}},
      tabs:{query:async query=>{assert.equal(query.url,'https://portal.sophia.com.br/*');return [{id:3,url:'https://portal.sophia.com.br/SophiA_999/LancNotas.aspx'}];},onUpdated:{addListener(){}},onRemoved:{addListener(){}}},
      scripting:{executeScript:async args=>calls.push(['inject',args])},
      runtime:{onInstalled:{addListener:fn=>installed=fn},onMessage:{addListener(){}}},
      commands:{onCommand:{addListener(){}}}
    };
    dom.window.eval(await fs.readFile(new URL('../background.js',import.meta.url),'utf8'));installed();
    await new Promise(r=>setTimeout(r,10));
    assert.equal(calls.length,2);assert.equal(calls[0][0],'configure');assert.deepEqual(JSON.parse(JSON.stringify(calls[1][1])),{target:{tabId:3,frameIds:[0]},files:['widget.js']});
  }finally{dom.window.close();}
});
