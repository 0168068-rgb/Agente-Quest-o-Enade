import test from 'node:test';
import assert from 'node:assert/strict';
import {buildAudit,auditCsv} from '../audit.mjs';
import {avaScope} from '../ava.mjs';
import {FakePortal,installChrome} from './portal-fixture.mjs';
import {PortalClient} from '../batch-engine.mjs';

const record=(extra={})=>({recordId:'r1',ra:'990000001',name:'Pessoa Um',code:'36',discipline:'Gestão de Projetos',course:'Administração',campus:'Cidade Azul',period:'1',source:'AD EAD.xlsx / Notas',grade:'8',line:2,...extra});
const destination=(extra={})=>({periodo:{value:'p',text:'2026.2'},unidade:{value:'u',text:'Cidade Azul'},turma:{value:'t',text:'G - 2026.2.3.1P - Administração'},disciplina:{value:'d',text:'Gestão de Projetos'},etapa:{value:'e',text:'Semestre'},page:1,students:1,assessments:['AD','AI','AS'],columns:[{exam:'AD',editable:0,empty:0,filled:1},{exam:'AI',editable:1,empty:1,filled:0},{exam:'AS',editable:1,empty:1,filled:0}],roster:[{ra:'990000001',name:'Pessoa Um',status:'Ativa'}],...extra});
const report=(extra={})=>({complete:true,period:{text:'2026.2'},periods:[{value:'p',text:'2026.2'}],rows:[],warnings:[],portalMap:[destination()],ava:{status:'verified',complete:true,account:'Joana Professora',warnings:[],courses:[{...avaScope({id:'c1',code:'036_G_AREA_20262',name:'Gestão de Projetos (Graduação EAD)'}),verified:true,teacher:true,role:'Professor'}]},...extra});

test('Conferência deduplica avaliações e lista faltantes por RA sem confundir PS com AS',()=>{
  const data=[record(),record({recordId:'ai',exam:'AI'}),record({recordId:'r2',ra:'990000002',name:'Pessoa Dois'})];
  const a=buildAudit(data,report());assert.equal(a.groups[0].expected,2);assert.equal(a.groups[0].found,1);assert.equal(a.groups[0].missing,1);
  assert.equal(a.issues.find(i=>i.kind==='Aluno ausente').ra,'990000002');
  assert.equal(a.fields.find(f=>f.exam==='PS').status,'Ausente');assert.equal(a.fields.find(f=>f.exam==='AD').status,'Presente, sem edição');assert.equal(a.fields.find(f=>f.exam==='AI').empty,1);
});
test('Aluno inativo aparece na lista; nome divergente e aluno fora da base têm motivos próprios',()=>{
  const r=report({portalMap:[destination({roster:[{ra:'990000001',name:'Outra Pessoa',status:'Transferida'},{ra:'990000003',name:'Pessoa Três',status:'Ativa'}]})]});
  const a=buildAudit([record()],r);assert.equal(a.groups[0].missing,0);
  for(const kind of ['Nome divergente','Matrícula sem situação ativa','Aluno fora da base enviada'])assert(a.issues.some(i=>i.kind===kind));
});
test('Falha de consulta e AVA indisponível nunca viram confirmação de aluno ausente',()=>{
  let a=buildAudit([record()],report({portalMap:[destination({failed:true,roster:[]})]}));assert.equal(a.groups[0].missing,null);assert.equal(a.complete,false);assert(!a.issues.some(i=>i.kind==='Aluno ausente'));
  a=buildAudit([record()],report({ava:{complete:false,courses:[],warnings:['AVA fechado']},portalMap:[]}));assert.equal(a.groups[0].missing,null);assert.equal(a.complete,false);assert(a.issues.some(i=>i.kind==='Verificação AVA incompleta'));
  a=buildAudit([record()],report({portalMap:[{periodo:{text:'2026.2'},unidade:{text:'Cidade Azul'},failed:true,status:'Falha'}]}));assert.equal(a.complete,false);assert.equal(a.groups[0].missing,null);
});
test('Dois professores, códigos e unidades diferentes recebem apenas seu vínculo confirmado',()=>{
  const r=report();let a=buildAudit([record(),record({discipline:'Estatística',code:'99',ra:'990000004'})],r);
  assert.equal(a.groups[1].status,'Fora do vínculo docente confirmado');assert.equal(a.groups[1].missing,null);
  r.ava.account='Marcos Docente';r.ava.courses=[{...avaScope({id:'xyz',code:'099_G_OUTRA_20262',name:'Estatística (Graduação EAD)'}),verified:true,teacher:true,role:'Professor'}];
  a=buildAudit([record(),record({discipline:'Estatística',code:'99',ra:'990000004'})],r);assert.equal(a.groups[0].missing,null);assert.equal(a.groups[1].missing,1);assert.equal(a.ava.account,'Marcos Docente');
});
test('RA em outro período do mesmo curso é divergência de turma, não aluno ausente',()=>{
  const a=buildAudit([record({period:'3'})],report());assert.equal(a.groups[0].missing,0);assert.equal(a.groups[0].found,1);assert(a.issues.some(i=>i.kind==='Turma/período divergente'));
});
test('Matrículas em páginas distintas são unidas e faltantes só aparecem depois do ciclo',()=>{
  const d=destination(),r=report({portalMap:[d,{...d,page:2,roster:[{ra:'990000002',name:'Pessoa Dois'}]}]});
  const records=[record(),record({ra:'990000002',name:'Pessoa Dois'})];let a=buildAudit(records,r);assert.equal(a.groups[0].found,2);assert.equal(a.groups[0].missing,0);
  r.complete=false;r.portalMap.pop();a=buildAudit(records,r);assert.equal(a.groups[0].missing,null);
});
test('Lote com dois semestres usa o período resolvido de cada arquivo',()=>{
  const r=report();r.periods.push({value:'p2',text:'2026.1'});r.cycle={groups:[{period:r.periods[0],recordIds:['atual']},{period:r.periods[1],recordIds:['anterior']}]};
  r.ava.courses.push({...r.ava.courses[0],id:'old',code:'036_G_AREA_20261'});
  const a=buildAudit([record({recordId:'atual'}),record({recordId:'anterior'})],r);
  assert.equal(a.groups.find(g=>g.period==='2026.2').found,1);assert.equal(a.groups.find(g=>g.period==='2026.1').missing,1);
});
test('Relatório completo contém vínculos, campos, lançamento, divergência de nota e CSV seguro',()=>{
  const r=report({rows:[{...record({name:'=HYPERLINK("x")'}),before:'60',after:'80',raw:'8',status:'Nota existente preservada',exam:'AD'}]});
  const csv=auditCsv(r,[record()]);for(const title of ['RESUMO POR DISCIPLINA','DIVERGÊNCIAS E PENDÊNCIAS','CAMPOS AD / AI / PS','VÍNCULOS AVA','LANÇAMENTOS','MAPEAMENTO COMPLETO DO SOPHIA','Nota divergente'])assert(csv.includes(title));assert(csv.includes("'=HYPERLINK"));
});
test('Catálogo inclui matrícula sem células de notas e lista alunos sem depender da avaliação enviada',async()=>{
  const p=new FakePortal();installChrome(p);const c=new PortalClient(7,{pause:async()=>{}});
  try{p.searched=true;p.render();const table=p.dom.window.document.querySelector('table'),header=table.rows[0];
    header.insertCell().textContent='Situação';for(const row of Array.from(table.rows).slice(1,-1))row.insertCell().textContent='Ativa';
    const row=table.insertRow(1);for(const value of ['990000099','Pessoa Inativa'])row.insertCell().textContent=value;
    const catalog=await c.catalog();assert(catalog.roster.some(r=>r.ra==='990000099'));assert.equal(catalog.students,3);assert.equal(catalog.columns.find(c=>c.exam==='AD').editable,2);
  }finally{p.close();}
});
test('Troca da conta visível do SophiA interrompe a retomada de um lote anterior',async()=>{
  const p=new FakePortal();installChrome(p);const c=new PortalClient(7,{pause:async()=>{}});
  try{const e=p.dom.window.document.createElement('div');e.id='dadosUsuarioDiv';e.textContent='Olá Joana. Trocar senha | Sair';p.dom.window.document.body.append(e);c.account=(await c.state()).account;e.textContent='Olá Marcos. Trocar senha | Sair';await assert.rejects(()=>c.state(),e=>e.code==='ACCOUNT_CHANGED');assert.equal(p.saveCount,0);}finally{p.close();}
});
test('Resultado SophiA sem quadro de alunos registra turma vazia e não inventa campos ausentes',async()=>{
  const p=new FakePortal();installChrome(p);const c=new PortalClient(7,{pause:async()=>{}});
  try{p.searched=true;p.render();const d=p.dom.window.document;d.querySelector('#grid').innerHTML='<div id="ctl00_ContentPlaceHolder1_LancamentoTabContainer_NotasTabPanel"><table id="ctl00_ContentPlaceHolder1_LancamentoTabContainer_NotasTabPanel_tbLancNotas"></table></div>';
    const catalog=await c.catalog();assert.equal(catalog.students,0);assert.equal(catalog.assessmentsKnown,false);assert.deepEqual(catalog.roster,[]);
    const a=buildAudit([record()],report({portalMap:[destination({...catalog})]}));assert.equal(a.groups[0].missing,1);assert(a.fields.every(f=>f.status==='Não verificado'&&f.editable===null&&f.empty===null&&f.filled===null));assert(!a.issues.some(i=>i.kind==='Campo PS'));
  }finally{p.close();}
});
test('Lista com alunos e apenas Média confirma ausência de AD, AI e PS',async()=>{
  const p=new FakePortal();installChrome(p);const c=new PortalClient(7,{pause:async()=>{}});
  try{p.searched=true;p.render();const table=p.dom.window.document.querySelector('table');
    for(const row of table.rows)while(row.cells.length>2)row.deleteCell(-1);
    table.rows[0].insertCell().textContent='Média';
    const catalog=await c.catalog();assert.equal(catalog.assessmentsKnown,true);assert(catalog.students>0);assert.deepEqual(catalog.assessments,[]);
    const a=buildAudit([record()],report({portalMap:[destination({...catalog})]}));assert(a.fields.every(f=>f.status==='Ausente'));
  }finally{p.close();}
});
