import test from 'node:test';
import assert from 'node:assert/strict';
import {JSDOM} from './portal-fixture.mjs';
import {avaCommand,AvaClient,avaPeriod} from '../ava.mjs';

function avaFixture(account='Professora Joana'){
  const dom=new JSDOM('<html><body><button aria-haspopup="true"><img alt=""></button><button aria-label="Alterar para modo de visualização: lista">Lista</button><button aria-label="Filtrar por status todos">Todos</button><input aria-label="Filtrar por nome"><div id="list"></div><div id="modals"></div></body></html>',{url:'https://avauni.grupoa.education/plataforma/my/courses',runScripts:'dangerously'});
  const w=dom.window,d=w.document;w.Element.prototype.getClientRects=function(){return this.hidden||this.closest('[hidden]')?[]:[{width:20,height:20}];};w.Element.prototype.scrollIntoView=function(){};d.querySelector('img').alt=account;
  const courses=[{id:'a',code:'036_G_GESTAO_20262',name:'Gestão de Projetos (Graduação EAD)',role:'Professor',count:2},{id:'b',code:'099_S_GESTAO_20262',name:'Estatística (Graduação Semipresencial - Cidade Azul)',role:'Estudante',count:2},{id:'old',code:'036_G_GESTAO_20252',name:'Gestão de Projetos (Graduação EAD)',role:'Professor',count:2}];
  let page=0;const opened=[];
  function render(){const box=d.getElementById('list');box.replaceChildren();const table=d.createElement('table');table.innerHTML='<tr><th></th><th>Código</th><th>Disciplina</th><th>Formato</th><th>Participantes</th></tr>';
    const c=courses[page],row=table.insertRow();row.insertCell();row.insertCell().textContent=c.code;const a=d.createElement('a');a.href='/plataforma/course/'+c.id;a.textContent=c.name;row.insertCell().append(a);row.insertCell().textContent='Normal';const b=d.createElement('button');b.dataset.testid='list-courses-table-open-participants-btn';b.textContent='('+c.count+')';b.onclick=()=>open(c);row.insertCell().append(b);box.append(table);
    const total=d.createElement('div');total.textContent='de 3 registros';box.append(total);const current=d.createElement('button');current.setAttribute('aria-label','Current Page, Page '+(page+1));box.append(current);const next=d.createElement('button');next.setAttribute('aria-label','Next page');next.disabled=page===2;next.onclick=()=>{page++;render();};box.append(next);
  }
  function open(c){opened.push(c.id);const dialog=d.createElement('div');dialog.setAttribute('role','dialog');dialog.innerHTML='<h2>Participantes</h2><p>Total de participantes ativos '+c.count+' - incluindo você Total de instrutores 1</p><span data-testid="participantsSearchInput"><input type="search"></span><table><tr><td></td><td><img alt=""></td><td></td><td></td></tr></table><button>Fechar</button>';dialog.querySelector('img').alt=account;dialog.querySelector('tr').cells[3].textContent=c.role;dialog.querySelector('button').onclick=()=>dialog.remove();d.getElementById('modals').append(dialog);}
  d.querySelector('[aria-label="Filtrar por status todos"]').onclick=e=>{e.currentTarget.setAttribute('aria-pressed','true');page=0;render();};render();
  globalThis.chrome={scripting:{executeScript:async({func,args})=>[{result:await w.eval('('+func.toString()+')')(args[0])}]}};
  return {dom,w,d,opened,close:()=>w.close()};
}
test('AVA identifica outro professor, todas as páginas e o papel real sem abrir abas',async()=>{
  for(const name of ['Professora Joana','Professor Marcos']){const f=avaFixture(name);try{const r=await new AvaClient(8,{pause:async()=>{},polls:12}).collect(['2026.2']);assert.equal(r.complete,true);assert.equal(r.account,name);assert.equal(r.pages,3);assert.deepEqual(f.opened,['a','b']);assert.equal(r.courses.find(c=>c.id==='a').teacher,true);assert.equal(r.courses.find(c=>c.id==='b').teacher,false);}finally{f.close();}}
});
test('Alteração de conta ou total divergente vira verificação incompleta',async()=>{
  const f=avaFixture();try{let r=await f.w.eval('('+avaCommand.toString()+')')({action:'state',account:'Outra Professora'});assert.equal(r.ok,false);
    const c=new AvaClient(8,{pause:async()=>{},polls:12}),call=c.call.bind(c);c.call=async command=>{const result=await call(command);if(command.action==='state')result.total=4;return result;};r=await c.collect(['2026.2']);assert.equal(r.complete,false);assert(r.warnings.some(x=>x.includes('quantidade total')));
  }finally{f.close();}
});
test('Período explícito diferencia turma atual de disciplina antiga ainda disponível',()=>{assert.equal(avaPeriod({code:'009PRESUNIG_UNIG_2026.2_PRES_I'}),'2026.2');assert.equal(avaPeriod({code:'036_G_GESTAO_20252'}),'2025.2');assert.equal(avaPeriod({code:'006-40h_S_ADM_I_202611P'}),'2026.1');assert.equal(avaPeriod({code:'831EXT_G_GP2025243P'}),'2025.2');assert.equal(avaPeriod({code:'SEM_CODIGO'}),'');});
test('Filtro de categoria ainda ativo impede declarar cobertura completa',async()=>{
  const f=avaFixture();try{const filter=f.d.createElement('div');filter.setAttribute('aria-label','filtrar por categorias');filter.textContent='Uma categoria';f.d.body.append(filter);
    const r=await new AvaClient(8,{pause:async()=>{},polls:12}).collect(['2026.2']);assert.equal(r.complete,false);assert(r.warnings.some(x=>x.includes('filtros adicionais')));
  }finally{f.close();}
});
test('Clique em Todos sem mudança de seleção não confirma cobertura do AVA',async()=>{
  const f=avaFixture();try{f.d.querySelector('[aria-label="Filtrar por status todos"]').onclick=()=>{};
    const r=await new AvaClient(8,{pause:async()=>{},polls:12}).collect(['2026.2']);assert.equal(r.complete,false);assert.equal(f.opened.length,0);
  }finally{f.close();}
});
test('Lista de alunos percorre todas as páginas do modal e exclui o professor',async()=>{
 const f=avaFixture();try{
  const c=new AvaClient(8,{pause:async()=>{},polls:12});await c.action('participants',{id:'a'});
  const dialog=f.d.querySelector('[role="dialog"]'),table=dialog.querySelector('table');dialog.querySelector('p').textContent='Total de participantes ativos 3 - incluindo você';
  const draw=data=>{table.innerHTML='<tr><th>RA</th><th>Nome</th><th>E-mail</th><th>Função</th></tr>';for(const [ra,name,role] of data){const row=table.insertRow();row.insertCell().textContent=ra;const img=f.d.createElement('img');img.alt=name;row.insertCell().append(img);row.insertCell();row.insertCell().textContent=role;}};
  draw([['','Professora Joana','Professor'],['990000010','Pessoa Dez','Estudante']]);
  const next=f.d.createElement('button');next.setAttribute('aria-label','Next page');next.onclick=()=>{draw([['990000011','Pessoa Onze','Aluno']]);next.disabled=true;};dialog.append(next);
  const r=await c.roster(await c.call({action:'state'}),()=>{});assert.equal(r.rosterComplete,true);assert.deepEqual(r.students.map(s=>s.ra),['990000010','990000011']);assert.equal(r.participantCount,3);
 }finally{f.close();}
});
test('Falha de página de participantes conserva alunos já lidos e marca cobertura incompleta',async()=>{
 const f=avaFixture();try{
  const c=new AvaClient(8,{pause:async()=>{},polls:12}),initial={dialog:true,search:'',participantTotal:3,memberNext:true,members:[{key:'a',ra:'990000010',name:'Pessoa Dez',role:'Estudante'}]};
  c.action=async()=>{throw new Error('Falha na página seguinte');};const r=await c.roster(initial,()=>{});assert.equal(r.students.length,1);assert.equal(r.rosterComplete,false);assert(r.rosterWarnings.some(s=>s.includes('Falha')));
 }finally{f.close();}
});
