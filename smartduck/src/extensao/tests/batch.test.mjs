import assert from 'node:assert/strict';
import test from 'node:test';
import {FakePortal,installChrome,records,sleep} from './portal-fixture.mjs';
import {PortalClient,discover,fillTask} from '../batch-engine.mjs';
import {portalCommand} from '../portal.mjs';
import {portalNavigation} from '../navigation.mjs';
import {finishInventory,courseMatches,classPeriod,disciplineMatches} from '../batch-core.mjs';
import {filterRecords,addFiles} from '../uploads.mjs';

const options={max:100,sourceMax:10,overwrite:false,absent:'blank'};
const settings={period:{value:'p26',text:'2026.2'},stage:{value:'e-a',text:'Semestre'},exam:'AD',options};
const client=()=>new PortalClient(7,{pause:()=>sleep(1)});
test('Todos inclui cursos, campi e disciplinas; um filtro específico restringe a seleção',()=>{
  const data=records();assert.equal(filterRecords(data).length,7);assert.equal(filterRecords(data,{campus:'Itaperuna'}).length,2);assert.equal(filterRecords(data,{disciplineKey:'37 | Estatística'}).length,1);
  assert(courseMatches('Administração','Administração 1º período'));assert(!courseMatches('Psicologia','Administração 1º período'));assert.equal(classPeriod('Administração 2º período'),'2');
  assert(!courseMatches('Administração','Administração Pública 1º período'));
  assert(disciplineMatches({discipline:'Gestão de Projetos',code:'036'},{text:'36 - Gestão de Projetos'}));
  assert(!disciplineMatches({discipline:'Gestão de Projetos',code:'036'},{text:'37 - Gestão de Projetos'}));
});
test('Limite de quatro arquivos é cumulativo e não descarta silenciosamente arquivos excedentes',async()=>{
  const existing={files:[{hash:'a'},{hash:'b'}],records:[]};let read=false;
  const file={name:'teste.xlsx',arrayBuffer:async()=>{read=true;return new ArrayBuffer(0);}};
  await assert.rejects(()=>addFiles([file,file,file],existing),/4 arquivos/);assert.equal(read,false);assert.equal(existing.files.length,2);
});
test('Duplicidade de destino bloqueia o mesmo registro em duas turmas',()=>{
  const r=records()[0];const rows=[{recordId:r.recordId,ready:true,status:'Pronto'},{recordId:r.recordId,ready:true,status:'Pronto'}];finishInventory([r],[],rows);assert(rows.every(r=>!r.ready&&r.status.includes('mais de uma turma')));
});
test('Inventário completo: várias unidades, cursos, disciplinas e páginas; faltosos em branco',async()=>{
  const portal=new FakePortal();installChrome(portal);const c=client();
  try{
    const report=await discover({client:c,records:records(),...settings});
    assert.equal(report.complete,true);assert.equal(report.tasks.length,5);assert.equal(report.rows.length,7);assert.equal(report.rows.filter(r=>r.ready).length,5);
    assert.equal(report.rows.find(r=>r.recordId==='record-1').status,'Faltoso: campo em branco');
    assert.equal(report.rows.find(r=>r.recordId==='record-6').after,'');assert(!report.rows.find(r=>r.recordId==='record-6').ready);
    assert(!report.rows.some(r=>r.status.includes('mais de uma turma')),'curricular period prevents wrong class');
    assert.equal(portal.saveCount,0,'inventory must never save');assert(portal.log.every(x=>x[1]==='p26'));
    for(const t of report.tasks){
      const rows=report.rows.filter(r=>r.taskId===t.id&&r.ready);if(!rows.length)continue;
      const filled=await fillTask(c,t,rows,{exam:'AD',max:100});
      assert(filled.changes.length);await c.save('AD',filled.changes,filled.token);await c.verify(t,'AD',filled.rows);
    }
    assert.equal(portal.bank['a/d1'][0][0].value,'80');assert.equal(portal.bank['a/d1'][0][1].value,'');assert.equal(portal.bank['a/d1'][1][0].value,'90');assert.equal(portal.bank['a/d2'][0][0].value,'70');assert.equal(portal.bank['b/d1'][0][0].value,'60');assert.equal(portal.bank['c/d1'][0][0].value,'100');assert.equal(portal.bank['c/d1'][0][1].value,'55');assert.equal(portal.bank['wrong/d1'][0][0].value,'');
    assert.equal(portal.saveCount,5);assert.equal(portal.reloadCount,5);
  }finally{portal.close();}
});
test('Falha de gravação não é confundida com valores preenchidos na tela nem é repetida',async()=>{
  const portal=new FakePortal();installChrome(portal);const c=client();
  try{
    const report=await discover({client:c,records:[records()[0]],...settings});const t=report.tasks[0],rows=report.rows.filter(r=>r.ready);
    const filled=await fillTask(c,t,rows,{exam:'AD',max:100});portal.rejectSave=true;
    await c.save('AD',filled.changes,filled.token);
    await assert.rejects(()=>c.save('AD',filled.changes,filled.token),/já foi solicitada/);
    assert.equal(portal.dom.window.document.querySelector('#ad0').value,'80','local value is filled');
    await assert.rejects(()=>c.verify(t,'AD',filled.rows),/não confirmou/);assert.equal(portal.saveCount,1);assert.equal(portal.bank['a/d1'][0][0].value,'');
  }finally{portal.close();}
});
test('Perda da resposta de preenchimento marca resultado desconhecido e não salva',async()=>{
  const portal=new FakePortal();installChrome(portal);const c=client();
  try{
    const report=await discover({client:c,records:[records()[0]],...settings});
    const execute=chrome.scripting.executeScript;
    chrome.scripting.executeScript=async args=>{const r=await execute(args);if(args.args[0].action==='apply')throw new Error('Lost response');return r;};
    await assert.rejects(()=>fillTask(c,report.tasks[0],report.rows,{exam:'AD',max:100}),/resultado pode ser parcial/);
    assert.equal(report.rows[0].ready,false);assert(report.rows[0].status.includes('desconhecido'));assert.equal(portal.saveCount,0);
  }finally{portal.close();}
});
test('Mudança de turma ou de nota antes de gravar bloqueia o botão Salvar',async()=>{
  for(const kind of ['grade','context']){
    const portal=new FakePortal();installChrome(portal);const c=client();
    try{
      const report=await discover({client:c,records:[records()[0]],...settings});const t=report.tasks[0];const filled=await fillTask(c,t,report.rows.filter(r=>r.ready),{exam:'AD',max:100});
      if(kind==='grade')portal.dom.window.document.querySelector('#ad0').value='45';else portal.dom.window.document.querySelector('#turma').options[0].text='Outra turma';
      await assert.rejects(()=>c.save('AD',filled.changes,filled.token),/mudou/);assert.equal(portal.saveCount,0);
    }finally{portal.close();}
  }
});
test('Cancelamento da consulta e mensagem do portal interrompem sem preencher',async()=>{
  const portal=new FakePortal();installChrome(portal);
  try{
    await assert.rejects(()=>discover({client:client(),records:records(),...settings,cancelled:()=>true}),/interrompida/);assert.equal(portal.saveCount,0);
    const modal=portal.dom.window.document.createElement('div');modal.setAttribute('role','dialog');modal.textContent='Confira a mensagem';portal.dom.window.document.body.append(modal);
    await assert.rejects(()=>client().state(),/mensagem/);assert.equal(portal.saveCount,0);
  }finally{portal.close();}
});
test('A extensão não aceita F, zero para faltoso ou limpeza não explicitamente sinalizada',async()=>{
  const portal=new FakePortal();installChrome(portal);const c=client();
  try{
    await c.command('search');const s=await c.scan('AD');const p=s.rows[0];
    for(const after of ['F','']){const r=await c.apply('AD',100,s,[{key:p.key,ra:p.ra,name:p.name,before:'',after}]);assert.equal(r.ok,false);}
    assert.equal((await c.apply('AD',100,s,[{key:p.key,ra:p.ra,name:p.name,before:'',after:'0',blank:true}])).ok,false);
    assert.equal(portal.dom.window.document.querySelector('#ad0').value,'');
  }finally{portal.close();}
});
