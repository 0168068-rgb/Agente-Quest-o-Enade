import test from 'node:test';
import assert from 'node:assert/strict';
import {PortalClient} from '../batch-engine.mjs';
import {FakePortal,installChrome,sleep} from './portal-fixture.mjs';
const pause=()=>sleep(1);
test('Filtros encadeados reduzem consultas redundantes e mantêm o mesmo destino',async()=>{
 const measure=async fast=>{const p=new FakePortal();installChrome(p);const c=new PortalClient(7,{pause});try{
  const values={periodo:{value:'p26',text:'2026.2'},unidade:{value:'u2',text:'Itaperuna'},turma:{value:'c',text:'Administração 1º período'},etapa:{value:'e-c',text:'Semestre'},disciplina:{value:'d2',text:'Estatística'}};
  if(fast)await c.filters(values);else{await c.reset();for(const [kind,option] of Object.entries(values)){const s=await c.ready();if(s.controls[kind].value!==option.value)await c.command('select',{kind,value:option.value,text:option.text});}await c.ready();}
  return {calls:p.scriptCalls.length,values:{...p.values}};
 }finally{p.close();}};
 const old=await measure(false),fast=await measure(true);assert.deepEqual(fast.values,old.values);assert(fast.calls<old.calls*.8,JSON.stringify({old,fast}));
 console.log('Consultas de filtros: '+old.calls+' → '+fast.calls);
});
test('Tela exata já aberta é reutilizada; mudança de turma ainda exige nova busca',async()=>{
 const p=new FakePortal();installChrome(p);const c=new PortalClient(7,{pause});try{
  const s=await c.ready(),task=Object.fromEntries(Object.entries(s.controls).map(([k,v])=>[k,{value:v.value,text:v.text}]));await c.open(task);const count=p.log.length;await c.open(task);assert.equal(p.log.length,count);
  await c.open({...task,disciplina:{value:'d2',text:'Estatística'}});assert(p.log.length>count);assert.equal(p.values.disciplina,'d2');
 }finally{p.close();}
});
