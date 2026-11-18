import assert from 'node:assert/strict';
import test from 'node:test';
import {FakePortal,installChrome,sleep} from './portal-fixture.mjs';
import {PortalClient} from '../batch-engine.mjs';
import {portalCommand} from '../portal.mjs';
import {portalSave} from '../save.mjs';

const task={periodo:{value:'p26',text:'2026.2'},unidade:{value:'u1',text:'Nova Iguaçu'},turma:{value:'a',text:'Administração 1º período'},etapa:{value:'e-a',text:'Semestre'},disciplina:{value:'d1',text:'Gestão de Projetos'},page:1};
async function fixture(){
  const portal=new FakePortal();installChrome(portal);
  const client=new PortalClient(7,{pause:()=>sleep(1)});
  await client.command('search');const snapshot=await client.scan('AD'),row=snapshot.rows[0];
  const changes=[{key:row.key,ra:row.ra,name:row.name,before:'',after:'80',recordId:'one'}];
  const applied=await client.apply('AD',100,snapshot,changes);assert.equal(applied.ok,true);
  return {portal,client,changes,token:applied.token,rows:changes};
}
function saveAnchor(portal){
  const w=portal.dom.window,d=w.document,original=d.querySelector('#salvar'),handler=original.onclick;
  const a=d.createElement('a');a.id='salvar';a.textContent='Salvar';
  a.href='javascript:WebForm_DoPostBackWithOptions(new WebForm_PostBackOptions("dynamic$saveLink", "", true, "Avaliacao", "", false, true))';
  a.setAttribute('onclick','return SubmitForm();');original.replaceWith(a);
  let submitted=0,postbacks=0;
  w.SubmitForm=()=>{submitted++;};
  w.WebForm_PostBackOptions=function(target){this.target=target;};
  w.WebForm_DoPostBackWithOptions=options=>{assert.equal(options.target,'dynamic$saveLink');postbacks++;handler();};
  return {a,counts:()=>({submitted,postbacks})};
}

test('Salvar do canto: link javascript ASP.NET executado em MAIN e confirmado no servidor',async()=>{
  const {portal:p,client:c,changes,token,rows}=await fixture();
  try{
    const anchor=saveAnchor(p);p.saveDelay=35;
    assert.equal(p.bank['a/d1'][0][0].value,'');assert.equal(p.dom.window.document.querySelector('#ad0').value,'80');
    await c.save('AD',changes,token);
    assert.deepEqual(anchor.counts(),{submitted:1,postbacks:1});assert.equal(p.saveCount,1);assert.equal(p.requestActive,false);assert.equal(p.reloadCount,0);
    assert.deepEqual(p.scriptCalls.filter(x=>['prepareSave','saveClick'].includes(x.action)),[{action:'prepareSave',world:'ISOLATED'},{action:'saveClick',world:'MAIN'}]);
    assert.equal(await c.verify(task,'AD',rows),true);assert.equal(p.reloadCount,1);assert.equal(p.bank['a/d1'][0][0].value,'80');
  }finally{p.close();}
});
test('Postback demorado termina antes da releitura, mesmo com filtros já estáveis',async()=>{
  const {portal:p,client:c,changes,token,rows}=await fixture();
  try{
    p.saveDelay=70;await c.save('AD',changes,token);await c.verify(task,'AD',rows);
    assert.equal(p.requestActive,false);assert.equal(p.saveCount,1);assert.equal(p.reloadCount,1);assert.equal(p.bank['a/d1'][0][0].value,'80');
    assert(p.scriptCalls.filter(x=>x.action==='saveStatus').length>4);
  }finally{p.close();}
});
test('Postback de página inteira é aguardado até carregar o novo documento',async()=>{
  const {portal:p,client:c,changes,token,rows}=await fixture();
  try{
    const w=p.dom.window,d=w.document;delete w.Sys;
    d.querySelector('#salvar').onclick=()=>{
      p.saveCount++;p.tabLoading=true;w.dispatchEvent(new w.Event('beforeunload'));
      w.setTimeout(()=>{p.bank['a/d1'][0][0].value=d.querySelector('#ad0').value;p.makeDocument();p.tabLoading=false;},35);
    };
    const version=p.documentVersion;await c.save('AD',changes,token);
    assert.equal(p.documentVersion,version+1);assert.equal(p.tabLoading,false);assert.equal(p.reloadCount,0);
    await c.verify(task,'AD',rows);assert.equal(p.saveCount,1);assert.equal(p.bank['a/d1'][0][0].value,'80');
  }finally{p.close();}
});
test('Painel reaberto aguarda Salvar pendente antes de recarregar e conferir',async()=>{
  const {portal:p,client:c,changes,token,rows}=await fixture();
  try{
    p.saveDelay=65;
    const prepared=await c.call(portalCommand,{action:'prepareSave',exam:'AD',changes,token});
    assert.equal((await c.call(portalSave,{...prepared,action:'saveClick'},'MAIN')).ok,true);
    const reopened=new PortalClient(7,{pause:()=>sleep(1)});await reopened.verify(task,'AD',rows);
    assert.equal(p.saveCount,1);assert.equal(p.reloadCount,1);assert.equal(p.bank['a/d1'][0][0].value,'80');
  }finally{p.close();}
});
test('Mudança de aluno, valor ou filtro entre preparação e clique impede Salvar',async()=>{
  for(const kind of ['name','grade','context','locked']){
    const {portal:p,client:c,changes,token}=await fixture();
    try{
      const prepared=await c.call(portalCommand,{action:'prepareSave',exam:'AD',changes,token}),d=p.dom.window.document;
      if(kind==='name')d.querySelectorAll('table tr')[1].cells[1].textContent='Outro Aluno';
      if(kind==='grade')d.querySelector('#ad0').value='45';
      if(kind==='context')d.querySelector('#turma').value='b';
      if(kind==='locked')d.querySelector('#ad0').disabled=true;
      const result=await c.call(portalSave,{...prepared,action:'saveClick'},'MAIN');assert.equal(result.ok,false);assert.match(result.message,/mud/);await sleep(5);assert.equal(p.saveCount,0);
    }finally{p.close();}
  }
});
test('Barras duplicadas equivalentes usam o Salvar superior uma única vez',async()=>{
  const {portal:p,client:c,changes,token}=await fixture();
  try{
    const anchor=saveAnchor(p),copy=anchor.a.cloneNode(true);copy.id='salvarRodape';anchor.a.closest('form').append(copy);
    await c.save('AD',changes,token);assert.equal(p.saveCount,1);assert.deepEqual(anchor.counts(),{submitted:1,postbacks:1});
  }finally{p.close();}
});
test('Salvar ausente ou ambíguo não clica outro comando nem informa sucesso',async()=>{
  for(const kind of ['missing','ambiguous']){
    const {portal:p,client:c,changes,token}=await fixture();
    try{
      const d=p.dom.window.document;
      if(kind==='missing')d.querySelector('#salvar').remove();
      else{const b=d.querySelector('#salvar').cloneNode(true);b.id='otherSave';d.querySelector('form').append(b);}
      await assert.rejects(()=>c.save('AD',changes,token),/não foi identificado/);assert.equal(p.saveCount,0);assert.equal(p.bank['a/d1'][0][0].value,'');
    }finally{p.close();}
  }
});
test('Validação impede postback: registra falha local e permite continuar por releitura',async()=>{
  const {portal:p,client:c,changes,token,rows}=await fixture();
  try{
    const d=p.dom.window.document;d.querySelector('#salvar').onclick=()=>{p.saveCount++;};
    await assert.rejects(()=>c.save('AD',changes,token),/não iniciou a gravação/);
    await assert.rejects(()=>c.verify(task,'AD',rows),/não confirmou/);assert.equal(p.reloadCount,1);assert.equal(p.saveCount,1);assert.equal(p.bank['a/d1'][0][0].value,'');
  }finally{p.close();}
});
test('Não recarrega nem repete Salvar enquanto há postback ainda em processamento',async()=>{
  const {portal:p,client:c,changes,token}=await fixture();
  try{
    c.savePolls=5;p.dom.window.document.querySelector('#salvar').onclick=()=>{p.saveCount++;p.beginRequest();};
    await assert.rejects(()=>c.save('AD',changes,token),e=>e.code==='SAVE_IN_FLIGHT');
    await assert.rejects(()=>c.recover(),e=>e.code==='SAVE_IN_FLIGHT');assert.equal(p.reloadCount,0);assert.equal(p.saveCount,1);
    p.endRequest();await c.recover();assert.equal(p.reloadCount,1);
  }finally{p.close();}
});
