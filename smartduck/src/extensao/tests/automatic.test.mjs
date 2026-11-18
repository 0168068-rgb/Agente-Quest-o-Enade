import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {detectExam,detectPeriod} from '../automatic.mjs';
import {recordsFromRows,buildPlan} from '../core.mjs';
import {unitKey,courseMatches,classPeriod} from '../batch-core.mjs';
import {discoverAutomatic,PortalClient,fillTask} from '../batch-engine.mjs';
import {FakePortal,installChrome,records,sleep} from './portal-fixture.mjs';
const client=()=>new PortalClient(7,{pause:()=>sleep(1)});
test('Formato real de campus, modalidade, curso e período, sem IDs pessoais',()=>{
  assert.equal(unitKey('Campus Nova Iguaçu – RJ'),'NOVA IGUACU');
  assert(courseMatches('Semipresencial - Administração','S - 2026.2.1P - Administração - T1 (Noite)'));
  assert(!courseMatches('Semipresencial - Administração','G - 2026.2.3.1P - Administração'));
  assert(courseMatches('Superior de Tecnologia em Gestão da Tecnologia da Informação','G - 2026.2.3.4P - Gestão da Tec. da Informação'));
  assert(courseMatches('Semipresencial - Superior de Tecnologia em Análise e Des. de Sistemas','S - 2026.2.3P - Análise e Desenvolvimento de Sistemas'));
  assert(!courseMatches('Administração','G - 2026.2.3.4P - Administração Pública'));
  assert.equal(classPeriod('G - 2026.2.3.6P - Administração'),'6');assert.equal(classPeriod('S - 2026.2.1P - Administração - T1 (Noite)'),'1');
});
test('Avaliação e período detectados por dados explícitos, sem inventar destinos',()=>{
  assert.equal(detectExam({source:'ad_ead_notas.xlsx / Notas'}),'AD');assert.equal(detectExam({source:'notas.xlsx / AI'}),'AI');assert.equal(detectExam({source:'AD AI.xlsx'}),'');assert.equal(detectExam({source:'notas.xlsx'}),'');assert.equal(detectExam({exam:'PS',source:'AD.xlsx'}),'PS');
  const control={value:'',options:[{value:'historic',text:'2025.2'},{value:'current',text:'2026.2'}]};
  assert.equal(detectPeriod([],control,new Date(2026,9,28)).value,'current');
  assert.equal(detectPeriod([{academicPeriod:'2025/2'}],control).value,'historic');
  assert.throws(()=>detectPeriod([{academicPeriod:'2024.2'}],control),/não está disponível/);
  assert.throws(()=>detectPeriod([{academicPeriod:'2025.2'},{academicPeriod:'2026.2'}],control),/misturam/);
  const source=recordsFromRows([['RA','Nome','Curso','Disciplina','Campus','AD','AI'],['990000001','Pessoa','Curso','Disciplina','Campus','8','7']],'Notas.xlsx');
  assert.deepEqual(source.map(r=>[r.exam,r.grade]),[['AD','8'],['AI','7']]);
});
test('Outro usuário: mapeia campus, curso, disciplina e IDs diferentes apenas a partir do portal',async()=>{
  const p=new FakePortal();installChrome(p);
  try{
    p.units=[{value:'u1',text:'Polo Vale Azul'}];p.classes={u1:[{value:'novo123',text:'Gestão de Serviços 3º período'}]};p.subjects=[{value:'tema901',text:'Planejamento Local'}];p.bank={'novo123/tema901':[[{ra:'880000001',name:'Pessoa de Outra Conta',value:''}]]};p.values={periodo:'p26',unidade:'u1',turma:'novo123',etapa:'e-novo123',disciplina:'tema901'};p.render();
    const data=[{...records()[0],campus:'Polo Vale Azul',course:'Gestão de Serviços',period:'3',discipline:'Planejamento Local',code:'',ra:'880000001',name:'Pessoa de Outra Conta'}];
    const c=client(),report=await discoverAutomatic({client:c,records:data});assert.equal(report.tasks.length,1);assert.equal(report.tasks[0].etapa.value,'e-novo123');assert.equal(report.tasks[0].etapa.text,'Semestre');assert.equal(report.rows.filter(r=>r.ready).length,1);
    const filled=await fillTask(c,report.tasks[0],report.rows,{exam:'AD',max:100});await c.save('AD',filled.changes,filled.token);await c.verify(report.tasks[0],'AD',filled.rows);assert.equal(p.bank['novo123/tema901'][0][0].value,'80');
  }finally{p.close();}
});
test('Conta sem etapa Semestre ou sem coluna PS só gera pendências',async()=>{
  for(const kind of ['stage','assessment']){const p=new FakePortal();installChrome(p);try{
    const data=[records()[0]];
    if(kind==='stage')p.stageLabel='Etapa 1';else{p.exams=['ad','ai','as'];data[0].exam='PS';}
    p.render();const report=await discoverAutomatic({client:client(),records:data});assert.equal(report.tasks.length,0);assert.equal(report.rows.filter(r=>r.ready).length,0);assert(report.warnings.length);assert.equal(p.saveCount,0);
  }finally{p.close();}}
});
test('Somente campos vazios, existentes e editáveis; aluno externo fica pendente',async()=>{
  const p=new FakePortal();installChrome(p);
  try{
    p.bank['a/d1'][0][0].locked=true;p.bank['b/d1'][0][0].readOnly=true;p.bank['a/d2'][0][0].value='30';
    const report=await discoverAutomatic({client:client(),records:[...records(),{...records()[0],recordId:'external',ra:'770000001',name:'Pessoa Não Cadastrada'}]});
    assert.equal(report.rows.filter(r=>r.ready).length,2);assert(!report.rows.find(r=>r.recordId==='external').ready);assert.equal(p.saveCount,0);
    assert(!buildPlan([{...records()[0],grade:'6'}],{rows:[{key:'one',ra:'990000001',name:'Pessoa Um',value:'50',editable:true}]},{sourceMax:10,max:100,overwrite:true})[0].ready);
  }finally{p.close();}
});
test('Produção não cria abas/janelas nem inclui conta, senha ou escola fixa',async()=>{
  const root=new URL('../',import.meta.url),names=await fs.readdir(root);
  for(const name of names.filter(n=>/\.(?:js|mjs|html)$/.test(n))){const text=await fs.readFile(new URL(name,root),'utf8');assert(!/(?:tabs|windows)\.create\s*\(|window\.open\s*\(|target\s*=\s*["']_blank/i.test(text),name);if(/\.(?:js|mjs)$/.test(name))assert(!/SophiA_[0-9]+\/|[?&]escola=[0-9]+|txtSenha/.test(text),name);}
  const m=JSON.parse(await fs.readFile(new URL('manifest.json',root),'utf8'));assert.equal(m.side_panel.default_path,'painel.html');assert(m.permissions.includes('sidePanel'));
});

test('Varre todos os destinos, mesmo sem nomes de curso/campus coincidentes e sem registros para algumas turmas',async()=>{
  const p=new FakePortal();installChrome(p);
  try{
    const data=[{...records()[4],campus:'Outra forma de escrever o polo',course:'Nome local do curso'}];
    const report=await discoverAutomatic({client:client(),records:data});
    assert.equal(report.portalMap.length,9);
    assert.equal(new Set(report.portalMap.map(d=>d.unidade.value)).size,2);
    assert.equal(new Set(report.portalMap.map(d=>d.turma.value)).size,4);
    assert.equal(report.rows.filter(r=>r.ready).length,1);
    assert.equal(report.tasks[0].turma.value,'b');
    assert.equal(p.saveCount,0);
  }finally{p.close();}
});
test('Planilha mínima usa RA, nome e disciplina; avaliação só é inferida quando única no portal',async()=>{
  for(const exams of [['as'],['ad','ai']]){
    const p=new FakePortal();installChrome(p);p.exams=exams;p.render();
    try{
      const data=recordsFromRows([['RA','Nome','Disciplina','Nota'],['990000004','Pessoa Quatro','Gestão de Projetos','6']],'Notas.xlsx').map((r,i)=>({...r,recordId:'minimal-'+i}));
      const report=await discoverAutomatic({client:client(),records:data});
      if(exams.length===1){assert.equal(report.rows.filter(r=>r.ready).length,1);assert.equal(report.tasks[0].exam,'AS');assert.equal(report.rows[0].after,'6');}
      else{assert.equal(report.rows.filter(r=>r.ready).length,0);assert(report.rows[0].status.includes('ambíguo'));}
    }finally{p.close();}
  }
});
test('Todos os períodos explícitos dos arquivos são mapeados no mesmo lote',async()=>{
  const p=new FakePortal();installChrome(p);
  try{
    const report=await discoverAutomatic({client:client(),records:[{...records()[0],academicPeriod:'2025/2'},{...records()[4],academicPeriod:'2026.2'}]});
    assert.deepEqual(report.periods.map(p=>p.text),['2025.2','2026.2']);
    assert.equal(report.portalMap.length,18);
    assert.equal(report.tasks.length,2);
    assert.equal(report.tasks.find(t=>t.turma.value==='a').periodo.value,'p25');
    assert.equal(report.tasks.find(t=>t.turma.value==='b').periodo.value,'p26');
  }finally{p.close();}
});
test('AD, AS e AE são mapeadas, salvas e relidas nas suas próprias colunas',async()=>{
  const p=new FakePortal();installChrome(p);p.exams=['ad','as','ae'];p.render();const c=client();
  try{
    const data=['AD','AS','AE'].map((exam,i)=>({...records()[4],exam,grade:String(6+i),recordId:'exam-'+exam}));
    const report=await discoverAutomatic({client:c,records:data});
    assert.equal(report.rows.filter(r=>r.ready).length,3);
    for(const t of report.tasks){const filled=await fillTask(c,t,report.rows.filter(r=>r.taskId===t.id&&r.ready),{exam:t.exam,max:t.max});await c.save(t.exam,filled.changes,filled.token);await c.verify(t,t.exam,filled.rows);}
    assert.equal(p.bank['b/d1'][0][0].value,'60');
    assert.deepEqual(p.bank['b/d1'][0][0].values,{as:'7',ae:'8'});
    assert.equal(p.saveCount,3);
  }finally{p.close();}
});
test('Turmas vazias são catalogadas e não impedem o restante do lote',async()=>{
  const p=new FakePortal();installChrome(p);p.bank['a/d1']=[[]];p.render();
  try{
    const report=await discoverAutomatic({client:client(),records:records()});
    assert.equal(report.portalMap.find(d=>d.turma.value==='a'&&d.disciplina.value==='d1').students,0);
    assert.equal(report.rows.filter(r=>r.ready).length,3);
  }finally{p.close();}
});
test('Arquivos conflitantes para o mesmo campo e alunos em duas turmas ficam pendentes',async()=>{
  for(const duplicate of ['source','destination']){
    const p=new FakePortal();installChrome(p);
    try{
      let data;
      if(duplicate==='source')data=[records()[4],{...records()[4],recordId:'other-file',grade:'9'}];
      else data=[{...records()[0],period:''}];
      const report=await discoverAutomatic({client:client(),records:data});
      assert.equal(report.rows.filter(r=>r.ready).length,0);
      assert(report.rows.every(r=>/mais de uma|Mais de um/.test(r.status)));
    }finally{p.close();}
  }
});
test('Aviso de sucesso é fechado automaticamente; falhas e confirmações desconhecidas interrompem',async()=>{
  const p=new FakePortal();installChrome(p);
  try{
    const d=p.dom.window.document,modal=d.createElement('div');modal.setAttribute('role','dialog');modal.textContent='Notas gravadas com sucesso.';const ok=d.createElement('button');ok.textContent='OK';ok.onclick=()=>modal.remove();modal.append(ok);d.body.append(modal);
    const c=client();assert((await c.state()).ok);assert(!modal.isConnected);
    modal.textContent='Não foi possível salvar as notas.';d.body.append(modal);
    await assert.rejects(()=>c.state(),/[Mm]ensagem/);assert(modal.isConnected);assert.equal(p.saveCount,0);
  }finally{p.close();}
});
test('Alterações manuais ainda não salvas impedem navegar para outra turma',async()=>{
  const p=new FakePortal();installChrome(p);const c=client();
  try{
    await c.command('search');p.dom.window.document.querySelector('#ad0').value='42';
    await assert.rejects(()=>discoverAutomatic({client:c,records:records()}),/ainda não confirmadas/);
    assert.equal(p.dom.window.document.querySelector('#ad0').value,'42');assert.equal(p.saveCount,0);
  }finally{p.close();}
});

test('Bloqueio após mapear é registrado; outras notas da mesma página continuam',async()=>{
  const p=new FakePortal();installChrome(p);const c=client();
  try{
    const data=[records()[0],{...records()[1],grade:'6',absent:'false'}];
    const report=await discoverAutomatic({client:c,records:data}),task=report.tasks[0];
    p.bank['a/d1'][0][0].locked=true;
    const filled=await fillTask(c,task,report.rows.filter(r=>r.ready),{exam:'AD',max:100});
    assert.equal(filled.changes.length,1);assert(report.rows.find(r=>r.ra===data[0].ra).status.includes('bloqueado'));
    await c.save('AD',filled.changes,filled.token);await c.verify(task,'AD',filled.rows);
    assert.equal(p.bank['a/d1'][0][0].value,'');assert.equal(p.bank['a/d1'][0][1].value,'60');
  }finally{p.close();}
});
test('Campo que bloqueia durante o preenchimento é pulado e o próximo aluno é salvo',async()=>{
  const p=new FakePortal();installChrome(p);const c=client();
  try{
    const extra={...records()[0],recordId:'extra',ra:'990009999',name:'Pessoa Extra',grade:'7'};
    p.bank['a/d1'][0].push({ra:extra.ra,name:extra.name,value:''});
    const data=[records()[0],{...records()[1],grade:'6',absent:'false'},extra];
    const report=await discoverAutomatic({client:c,records:data}),task=report.tasks[0];
    const execute=p.execute.bind(p);
    p.execute=async(func,cmd)=>{
      if(cmd.action==='apply')p.dom.window.document.querySelector('#ad0').addEventListener('change',()=>{p.dom.window.document.querySelector('#ad1').disabled=true;},{once:true});
      return execute(func,cmd);
    };
    const filled=await fillTask(c,task,report.rows.filter(r=>r.ready),{exam:'AD',max:100});
    assert.equal(filled.changes.length,2);assert(report.rows.find(r=>r.ra===data[1].ra).status.includes('bloqueado durante'));
    await c.save('AD',filled.changes,filled.token);await c.verify(task,'AD',filled.rows);
    assert.deepEqual(p.bank['a/d1'][0].map(r=>r.value),['80','','70']);assert.equal(p.saveCount,1);
  }finally{p.close();}
});
test('Limite de um campo não impede salvar outro aluno da mesma página',async()=>{
  const p=new FakePortal();installChrome(p);const c=client();
  try{
    p.bank['a/d1'][0][0].fields={ad:{maxLength:1}};
    const data=[records()[0],{...records()[1],grade:'6',absent:'false'}],report=await discoverAutomatic({client:c,records:data}),task=report.tasks[0];
    const filled=await fillTask(c,task,report.rows.filter(r=>r.ready),{exam:'AD',max:100});
    assert.equal(filled.changes.length,1);assert(report.rows.find(r=>r.ra===data[0].ra).status.includes('tamanho permitido'));
    await c.save('AD',filled.changes,filled.token);await c.verify(task,'AD',filled.rows);assert.equal(p.bank['a/d1'][0][1].value,'60');
  }finally{p.close();}
});

test('Avaliação retirada após consulta é registrada e a avaliação seguinte pode ser salva',async()=>{
  const p=new FakePortal();installChrome(p);const c=client();
  try{
    const data=[{...records()[4],exam:'AD'},{...records()[4],exam:'AI',recordId:'ai-after',grade:'9'}];
    const report=await discoverAutomatic({client:c,records:data});
    p.exams=['ai'];p.render();
    const ad=report.tasks.find(t=>t.exam==='AD'),ai=report.tasks.find(t=>t.exam==='AI');
    const skipped=await fillTask(c,ad,report.rows.filter(r=>r.exam==='AD'),{exam:'AD',max:100});
    assert.equal(skipped.changes.length,0);assert(report.rows.find(r=>r.exam==='AD').status.includes('indisponível na releitura'));
    const filled=await fillTask(c,ai,report.rows.filter(r=>r.exam==='AI'),{exam:'AI',max:10});
    await c.save('AI',filled.changes,filled.token);await c.verify(ai,'AI',filled.rows);
    assert.equal(p.saveCount,1);assert.equal(p.bank['b/d1'][0][0].values.ai,'9');
  }finally{p.close();}
});

test('Validação de um campo recusa a nota; restaura só esse campo e salva o outro aluno',async()=>{
  const p=new FakePortal();installChrome(p);const c=client();
  try{
    const data=[records()[0],{...records()[1],grade:'6',absent:'false'}];
    const report=await discoverAutomatic({client:c,records:data}),task=report.tasks[0],execute=p.execute.bind(p);
    p.execute=async(func,command)=>{
      if(command.action==='apply'){
        const input=p.dom.window.document.querySelector('#ad0');input.addEventListener('change',()=>input.setCustomValidity(input.value?'Nota não aceita':''));
      }
      return execute(func,command);
    };
    const filled=await fillTask(c,task,report.rows.filter(r=>r.ready),{exam:'AD',max:100});
    assert.equal(filled.changes.length,1);assert(report.rows.find(r=>r.recordId==='record-0').status.includes('campo recusou'));
    await c.save('AD',filled.changes,filled.token);await c.verify(task,'AD',filled.rows);
    assert.deepEqual(p.bank['a/d1'][0].map(r=>r.value),['','60']);assert.equal(p.saveCount,1);
  }finally{p.close();}
});

test('Formulário de senha oculto não bloqueia o lote; login visível exige acesso à conta',async()=>{
  const p=new FakePortal();installChrome(p);const c=client();
  try{
    const input=p.dom.window.document.createElement('input');input.type='password';input.hidden=true;p.dom.window.document.body.append(input);
    assert((await c.ready()).ok);input.hidden=false;
    await assert.rejects(()=>c.ready(),e=>e.code==='SESSION_UNAVAILABLE');assert.equal(p.saveCount,0);
  }finally{p.close();}
});
