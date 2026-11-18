import test from 'node:test';
import assert from 'node:assert/strict';
import {buildAudit} from '../audit.mjs';
import {reportSheets} from '../report-sheets.mjs';
import {exportXlsx} from '../report-xlsx.mjs';
import {unzip} from '../import.mjs';
const student=(ra,name)=>({ra,name,role:'Estudante',key:ra||name});
const base=()=>({period:{text:'2026.2'},periods:[{text:'2026.2'}],complete:true,rows:[],warnings:[],ava:{complete:true,account:'Joana Professora',courses:[{id:'a',code:'036_G_AREA_20262',name:'Gestão de Projetos (Graduação EAD)',verified:true,teacher:true,role:'Professor',rosterComplete:true,students:[student('990000001','Pessoa Um'),student('990000002','Pessoa Dois')]}]},portalMap:[{periodo:{value:'p',text:'2026.2'},unidade:{value:'u',text:'Cidade Azul'},turma:{value:'t',text:'G - 2026.2.3.1P - Administração'},disciplina:{value:'d',text:'Gestão de Projetos'},roster:[{ra:'990000001',name:'Pessoa Um',status:'Ativa'}],assessmentsKnown:true,assessments:['AD','AI','PS'],columns:['AD','AI','PS'].map(exam=>({exam,editable:1,empty:1,filled:0}))}]});
const record=(ra='990000002',name='Pessoa Dois')=>({recordId:ra,ra,name,discipline:'Gestão de Projetos',code:'036',course:'Administração',campus:'Cidade Azul',period:'1',source:'AD EAD.xlsx',line:2});
test('Alunos só no AVA usa participantes reais, mesmo sem arquivo, e inclui turma e disciplina',()=>{
 const r=base(),a=buildAudit([],r);assert.equal(a.onlyAva.length,1);assert.equal(a.onlyAva[0].ra,'990000002');assert.equal(a.onlyAva[0].avaClass,'036_G_AREA_20262');assert.equal(a.onlyAva[0].discipline,'Gestão de Projetos');assert.equal(a.onlyAva[0].confirmed,true);assert.equal(a.complete,true);
 assert.equal(a.classDivergences.length,1);assert.equal(a.classDivergences[0].missing,1);assert(a.onlyAva[0].sophiaClass.includes('Turmas compatíveis consultadas: G - 2026.2.3.1P - Administração'));
 assert(!a.issues.some(i=>i.kind==='Sem base de alunos'));
});
test('Arquivo de outro aluno não fabrica um participante ausente no AVA',()=>{
 const a=buildAudit([record('990000099','Pessoa Fora do AVA')],base());assert(!a.onlyAva.some(s=>s.ra==='990000099'));assert(a.groups.some(g=>g.missing===1));
});
test('Nome único no arquivo resolve RA e turma esperada; RA não exposto fica identificado',()=>{
 const r=base();r.ava.courses[0].students=[student('','Pessoa Dois')];let a=buildAudit([record()],r);assert.equal(a.onlyAva[0].ra,'990000002');assert(a.onlyAva[0].method.includes('arquivo'));assert(a.onlyAva[0].sophiaClass.includes('1P'));
 a=buildAudit([],r);assert.equal(a.onlyAva[0].confirmed,false);assert(a.onlyAva[0].status.includes('RA indisponível'));
});
test('Consulta parcial mantém pendência e não confirma ausência global',()=>{
 const r=base();r.portalMap.push({periodo:{text:'2026.2'},unidade:{text:'Outra Cidade'},failed:true});const a=buildAudit([],r);assert.equal(a.complete,false);assert.equal(a.onlyAva[0].confirmed,false);assert(a.onlyAva[0].status.includes('incompleto'));
 r.portalMap.pop();r.ava.courses[0].rosterComplete=false;assert.equal(buildAudit([],r).complete,false);
});
test('Mesmo nome com RA diferente é divergência, não ausência confirmada',()=>{
 const r=base();r.portalMap[0].roster.push({ra:'990000009',name:'Pessoa Dois'});const a=buildAudit([],r);assert.equal(a.onlyAva[0].confirmed,false);assert(a.onlyAva[0].status.includes('RA diferente'));
});
test('Professores, disciplinas e modalidades não se misturam na comparação',()=>{
 const r=base();r.ava.courses[0].teacher=false;assert.equal(buildAudit([],r).onlyAva.length,0);
 r.ava.courses[0].teacher=true;r.portalMap[0].turma.text='S - 2026.2.1P - Administração';assert.equal(buildAudit([],r).onlyAva.length,2);
});
test('Entradas 1-3E e 2-4E ficam distintas e aluno em outra entrada é informado',()=>{
 const r=base();r.ava.courses[0].code='036_G_AREA_2-4E_20262';const a=buildAudit([],r);assert(a.onlyAva.find(s=>s.ra==='990000001').status.includes('outra entrada'));assert.equal(a.onlyAva.find(s=>s.ra==='990000001').confirmed,false);assert(a.classDivergences[0].detail.includes('não localizada'));
});
test('Relatório Excel abre com as duas abas pedidas, RA literal e sem fórmulas injetadas',async()=>{
 const r=base();r.ava.courses[0].students[1].name='=HYPERLINK("teste")';const sheets=reportSheets(r,[]);
 assert.deepEqual(sheets.slice(0,2).map(s=>s.name),['Turmas com divergências','Alunos só no AVA']);
 const blob=exportXlsx(sheets),files=await unzip(await blob.arrayBuffer());
 const workbook=await files('xl/workbook.xml');assert(workbook.includes('Alunos só no AVA'));
 const students=await files('xl/worksheets/sheet2.xml');assert(students.includes('990000002'));assert(students.includes('HYPERLINK'));assert(!students.includes('<f>'));assert(students.includes('t="inlineStr"'));
});
