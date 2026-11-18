// Run with Node.js: node tests/core.test.mjs
// All records here are fictitious.
import assert from 'node:assert/strict';
import {buildPlan,gradeInfo,recordsFromRows} from '../core.mjs';
const record={ra:'990000001',name:'Pessoa Exemplo',grade:'8,000',absent:'false'};
const snapshot={rows:[{key:'1',ra:'990000001',name:'Pessoa Exemplo',value:'',editable:true,type:'text'}]};
const options={sourceMax:10,max:100,absent:'blank',overwrite:false};
const plan=(r=record,s=snapshot,o=options)=>buildPlan([r],s,o)[0];
for(const [grade,want] of [['0','0'],['8,000','80'],['10,000','100'],['7,5','75'],['0,25','2,5'],['9,875','98,75']]) assert.equal(plan({...record,grade}).after,want);
assert.equal(plan(record,snapshot,{...options,max:10}).after,'8');
assert.equal(plan({...record,grade:'80'},snapshot,{...options,sourceMax:100}).after,'80');
assert.equal(gradeInfo('').kind,'empty');
assert.equal(gradeInfo('F').kind,'absent');
assert(!plan({...record,grade:'F'}).ready);
assert.equal(plan({...record,grade:'F'}).after,'');
assert.equal(plan({...record,grade:'F'}).status,'Faltoso: campo em branco');
assert(!plan({...record,grade:'F'},{rows:[{...snapshot.rows[0],value:'70'}]}).ready);
assert.equal(plan({...record,grade:'F'},{rows:[{...snapshot.rows[0],value:'70'}]},{...options,overwrite:true}).after,'');
assert(plan({...record,grade:'F'},{rows:[{...snapshot.rows[0],value:'70'}]},{...options,overwrite:true}).blank);
for(const grade of ['11','-1','NaN','=1+1','#FORMULA: A1']) assert(!plan({...record,grade}).ready);
assert(!plan({...record,absent:'true'}).ready);
assert(!buildPlan([record,record],snapshot,options)[0].ready);
assert(!plan({...record,name:'Outra Pessoa'}).ready);
assert(!plan({...record,ra:'LT'},{rows:[{...snapshot.rows[0],ra:'LT'}]}).ready);
assert(!plan(record,{rows:[{...snapshot.rows[0],value:'70'}]}).ready);
assert(!plan(record,{rows:[{...snapshot.rows[0],value:'70'}]},{...options,overwrite:true}).ready);
assert.equal(plan(record,{rows:[{...snapshot.rows[0],value:'80,0'}]}).status,'Já possui esse valor');
assert.throws(()=>recordsFromRows([['RA','RA'],['1','1']],'teste'));
console.log('OK: conversão AD, AI/PS, F, vazio, duplicidades, nomes, RA e notas existentes.');
