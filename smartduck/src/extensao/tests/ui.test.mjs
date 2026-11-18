import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {JSDOM,FakePortal,installChrome,records} from './portal-fixture.mjs';
import {saveSession,loadSession} from '../session-store.mjs';
const originalTimer=globalThis.setTimeout;
const wait=async predicate=>{for(let i=0;i<1800;i++){if(predicate())return;await new Promise(r=>originalTimer(r,5));}throw new Error('UI timeout: '+globalThis.document.getElementById('message').textContent);};
let sequence=0;
async function fixture({reuse=false,portal:existing}={}){
  const portal=existing||new FakePortal();if(!reuse)installChrome(portal);
  const html=await fs.readFile(new URL('../painel.html',import.meta.url),'utf8');const d=new JSDOM(html,{url:'https://extension.test/painel.html?tab=7'});
  for(const k of ['window','document','location','Option','Event','DOMParser'])globalThis[k]=d.window[k];
  globalThis.setTimeout=(fn,ms,...args)=>originalTimer(fn,ms===250||ms===40?1:ms,...args);
  if(!reuse)await saveSession(7,{version:1,files:[{name:'AD Exemplo.xlsx',hash:'fictional',count:7,sheets:1}],records:records(),report:null,selected:[],phase:'idle',pending:null,queue:[],cursor:0,filters:{},fallbackExam:''});
  await import('../painel.mjs?test='+(++sequence));const $=id=>d.window.document.getElementById(id);
  await wait(()=>$('portalContext').textContent.includes('2026.2'));
  // Completion text appears before the final compressed checkpoint resolves.
  // Keep each DOM alive until the operation is idle so its finally callback
  // cannot touch the next test's document through globalThis.document.
  return {portal,d,$,async close(){await wait(()=>$('stop').disabled);globalThis.setTimeout=originalTimer;d.window.close();if(!reuse)portal.close();}};
}
test('Um clique em Realizar mapeia tudo, salva todas as turmas e preserva faltosos e notas existentes',async()=>{
  const f=await fixture(),{$,portal}=f;
  try{
    for(const id of ['source','campus','course','period','disciplineKey','confirmed','run','preview'])assert.equal($(id),null);
    assert.equal($('direct').textContent,'Realizar');
    assert($('mapping').textContent.includes('AD'));assert.equal($('direct').disabled,false);
    $('direct').click();await wait(()=>$('message').textContent.startsWith('Processamento concluído'));
    assert.equal(portal.saveCount,5);assert.equal(portal.reloadCount,5);assert.equal($('countSaved').textContent,'5');assert.equal($('countBlank').textContent,'1');
    assert.equal(portal.bank['a/d1'][0][1].value,'');assert.equal(portal.bank['c/d1'][0][1].value,'55');assert.equal(portal.values.etapa,'e-c');
    assert.equal($('countMapped').textContent,'9');
  }finally{await f.close();}
});
test('Conferir sem lançar percorre o ciclo, gera relatório e não preenche nem salva notas',async()=>{
  const f=await fixture(),{$,portal}=f;let downloads=0;const click=f.d.window.HTMLAnchorElement.prototype.click;
  f.d.window.HTMLAnchorElement.prototype.click=function(){if(this.download)downloads++;else click.call(this);};
  try{
    $('auditOnly').click();await wait(()=>$('message').textContent.startsWith('Conferência concluída'));await wait(()=>!$('settings').disabled);
    assert.equal(portal.saveCount,0);assert(!portal.scriptCalls.some(c=>c.action==='apply'));
    const saved=await loadSession(7);assert.equal(saved.report.complete,true);assert.equal(saved.report.mode,'audit');assert.equal(saved.report.audit.complete,false);
    assert.equal(saved.report.audit.ava.status,'unavailable');assert(saved.report.audit.fields.some(f=>f.exam==='PS'));
    assert.equal($('auditResult').hidden,false);assert.equal(downloads,1);assert.equal(saved.report.downloadAttempted,true);
    $('export').click();assert.equal(downloads,2);
  }finally{f.d.window.HTMLAnchorElement.prototype.click=click;await f.close();}
});
test('Conferência separada funciona sem arquivos e permite alternar as abas de resultados',async()=>{
 const f=await fixture(),{$,portal}=f;try{
  $('clear').click();await wait(()=>!$('settings').disabled&&$('fileCount').textContent==='0 / 4 arquivos carregados');assert.equal($('direct').disabled,true);assert.equal($('auditOnly').disabled,false);
  $('auditOnly').click();await wait(()=>$('message').textContent.startsWith('Conferência concluída'));await wait(()=>!$('settings').disabled);
  const saved=await loadSession(7);assert.equal(saved.report.complete,true);assert.equal(saved.report.portalMap.length,9);assert.equal(portal.saveCount,0);
  $('auditStudents').click();assert.equal($('auditStudents').getAttribute('aria-selected'),'true');assert($('auditIssues').textContent.includes('incompleta'));
  $('auditOther').click();assert.equal($('auditOther').getAttribute('aria-selected'),'true');assert($('auditIssues').textContent.includes('AVA'));
 }finally{await f.close();}
});
test('Consulta de participantes AVA começa depois de salvar as notas liberadas',async()=>{
 const f=await fixture(),{$,portal}=f;const query=chrome.tabs.query;let savedWhenAva=null;
 chrome.tabs.query=async args=>{if(args?.url){savedWhenAva=portal.saveCount;return [];}return query(args);};
 try{$('direct').click();await wait(()=>$('message').textContent.startsWith('Processamento concluído'));assert.equal(portal.saveCount,5);assert.equal(savedWhenAva,5);}
 finally{await f.close();}
});
test('Execução com um clique pode ser pausada pelo usuário e continuar do restante',async()=>{
  const f=await fixture(),{$,portal}=f;
  try{
    $('direct').click();await wait(()=>$('progress').textContent.startsWith('Turma/página 1'));
    $('stop').click();await wait(()=>$('message').textContent.startsWith('Lote pausado'));assert.equal(portal.saveCount,1);await wait(()=>$('resume').disabled===false);
    $('resume').click();await wait(()=>$('message').textContent.startsWith('Processamento concluído'));assert.equal(portal.saveCount,5);
  }finally{await f.close();}
});
test('Falhas de gravação são relatadas e todas as turmas são tentadas sem Continuar',async()=>{
  const f=await fixture(),{$,portal}=f;
  try{
    portal.rejectSave=true;$('direct').click();await wait(()=>$('message').textContent.includes('nenhuma nota pôde ser lançada'));await wait(()=>!$('settings').disabled);
    assert.equal(portal.saveCount,5);assert.equal($('resume').hidden,true);
    const saved=await loadSession(7);assert.equal(saved.report.complete,true);assert.equal(saved.pending,null);
    assert.equal(saved.report.rows.filter(r=>r.saved).length,0);assert(saved.report.rows.some(r=>r.status.includes('não confirmada')));
    assert(portal.log.some(x=>x[0]==='buscar'&&x[2]==='c'&&x[3]==='d2'));
  }finally{await f.close();}
});

test('Reabrir durante preenchimento não retoma alterações e permite encerrar após conferência',async()=>{
  const f=await fixture();let reopened;
  try{
    const saved=await loadSession(7);saved.phase='applying';saved.report={tasks:[],rows:[],period:{text:'2026.2'},warnings:[]};await saveSession(7,saved);
    reopened=await fixture({reuse:true,portal:f.portal});
    assert.equal(reopened.$('direct').disabled,true);assert.equal(reopened.$('resume').hidden,true);assert.equal(f.portal.saveCount,0);
    reopened.$('end').click();await wait(()=>!reopened.$('direct').disabled);assert.equal(f.portal.saveCount,0);
  }finally{await reopened?.close();await f.close();}
});
test('Seletor importa um arquivo diretamente no painel e detecta AD pelo nome',async()=>{
  const f=await fixture();
  try{
    f.$('clear').click();await wait(()=>f.$('fileCount').textContent==='0 / 4 arquivos carregados'&&!f.$('settings').disabled);
    const file=new File(['RA;Nome;Curso;Disciplina;Campus;Período;Nota\n990000001;Pessoa Um;Administração;Gestão de Projetos;Nova Iguaçu;1;8\n'],'AD Importacao.csv');
    Object.defineProperty(f.$('files'),'files',{configurable:true,value:[file]});f.$('files').dispatchEvent(new Event('change'));
    await wait(()=>f.$('fileCount').textContent==='1 / 4 arquivos carregados'&&!f.$('settings').disabled);
    assert(f.$('mapping').textContent.includes('Avaliações: AD'));assert.equal(f.$('direct').disabled,false);assert.equal(f.portal.saveCount,0);
  }finally{await f.close();}
});

test('Quatro arquivos selecionados juntos e um único Realizar lançam o lote sem outras ações',async()=>{
  const f=await fixture();
  try{
    f.$('clear').click();await wait(()=>f.$('fileCount').textContent==='0 / 4 arquivos carregados'&&!f.$('settings').disabled);
    const data=records(),files=[0,3,4,5].map((index,i)=>{
      const r=data[index];return new File(['RA;Nome;Curso;Disciplina;Campus;Período;Nota\n'+[r.ra,r.name,r.course,r.discipline,r.campus,r.period,r.grade].join(';')+'\n'],'AD Arquivo '+i+'.csv');
    });
    Object.defineProperty(f.$('files'),'files',{configurable:true,value:files});f.$('files').dispatchEvent(new Event('change'));
    await wait(()=>f.$('fileCount').textContent==='4 / 4 arquivos carregados'&&!f.$('settings').disabled);
    assert.equal(f.portal.saveCount,0);
    f.$('direct').click();await wait(()=>f.$('message').textContent.startsWith('Processamento concluído'));
    assert.equal(f.portal.saveCount,4);assert.equal(f.portal.reloadCount,4);assert.equal(f.$('countSaved').textContent,'4');assert.equal(f.$('countMapped').textContent,'9');
  }finally{await f.close();}
});

test('Realizar entra em Notas pelo menu da conta e continua na mesma aba',async()=>{
  const f=await fixture();
  try{
    const p=f.portal;p.dom.reconfigure({url:'https://portal.sophia.com.br/SophiA_112/Arquivo.aspx'});
    const link=p.dom.window.document.createElement('a');link.href='LancNotas.aspx';link.textContent='Notas';link.target='_blank';p.dom.window.document.body.append(link);
    const execute=p.execute.bind(p);let entries=0;
    p.execute=async(func,command)=>{
      if(command.action==='enter'&&p.dom.window.location.pathname.endsWith('/Arquivo.aspx')){
        // JSDOM has no page navigation: capture only the redirect scheduling.
        const schedule=p.dom.window.setTimeout;p.dom.window.setTimeout=()=>0;
        const result=await execute(func,command);p.dom.window.setTimeout=schedule;
        assert.equal(result.issued,true);entries++;p.makeDocument();return result;
      }
      return execute(func,command);
    };
    f.$('direct').click();await wait(()=>f.$('message').textContent.startsWith('Processamento concluído'));
    assert.equal(entries,1);assert.equal(p.saveCount,5);assert.equal(p.reloadCount,5);
  }finally{await f.close();}
});

test('AD bloqueada entra no relatório e as notas AI liberadas são salvas sem confirmação',async()=>{
  const p=new FakePortal();p.exams=['ad','as','ai','ae'];
  for(const pages of Object.values(p.bank))for(const page of pages)for(const r of page)r.textExams=['ad'];
  p.render();installChrome(p);
  await saveSession(7,{version:2,files:[{name:'notas.xlsx',hash:'fictional',count:2}],records:[{...records()[4],exam:'AD'},{...records()[4],exam:'AI',recordId:'ai-note',grade:'9'}],report:null,phase:'idle',pending:null,queue:[],cursor:0});
  const f=await fixture({reuse:true,portal:p});
  try{
    assert.equal(f.$('tracking').hidden,true);
    f.$('direct').click();await wait(()=>f.$('message').textContent.startsWith('Processamento concluído'));
    assert.equal(p.saveCount,1);assert.equal(p.bank['b/d1'][0][0].value,'');assert.equal(p.bank['b/d1'][0][0].values.ai,'9');
    const stored=await loadSession(7);assert(stored.report.rows.find(r=>r.exam==='AD').status.includes('bloqueado'));
    assert.equal(stored.report.rows.find(r=>r.exam==='AI').saved,true);
    assert(stored.report.portalMap.every(m=>m.columns.find(c=>c.exam==='AD').editable===0));
  }finally{await f.close();p.close();}
});
test('Sem campos liberados, a tela informa a causa e não exibe sucesso de gravação',async()=>{
  const p=new FakePortal();for(const pages of Object.values(p.bank))for(const page of pages)for(const r of page)r.textExams=['ad'];p.render();
  const f=await fixture({portal:p});
  try{
    f.$('direct').click();await wait(()=>f.$('message').textContent.includes('não liberou campos de AD'));
    assert.equal(p.saveCount,0);assert.equal(f.$('countSaved').textContent,'0');assert.equal(f.$('reportDetails').open,true);
  }finally{await f.close();}
});

test('Conclui e salva uma unidade antes da próxima; não finaliza quando acaba a primeira fila',async()=>{
  const f=await fixture(),{$,portal:p}=f;
  try{
    p.units.push({value:'u3',text:'Polo Final'});p.classes.u3=[{value:'last',text:'Curso Final 1º período'}];
    p.bank['last/d1']=[[]];p.bank['last/d2']=[[{ra:'990009990',name:'Pessoa Final',value:''}]];p.render();
    $('direct').click();await wait(()=>$('message').textContent.startsWith('Processamento concluído'));
    const firstSave=p.log.findIndex(x=>x[0]==='salvar');
    const nextUnit=p.log.findIndex(x=>x[0]==='buscar'&&x[2]==='c');
    assert(firstSave>=0&&firstSave<nextUnit,'deve salvar a primeira unidade antes de consultar os alunos da segunda');
    for(const classroom of ['a','b','wrong','c','last'])for(const subject of ['d1','d2'])assert(p.log.some(x=>x[0]==='buscar'&&x[2]===classroom&&x[3]===subject),classroom+'/'+subject);
    const saved=await loadSession(7);assert.equal(saved.report.complete,true);assert.equal(saved.report.cycle.unitsAttempted,3);
    assert.equal(saved.report.portalMap.length,11);assert.equal(p.saveCount,5);
    assert($('progress').textContent.includes('3 / 3 unidades'));assert($('progress').textContent.includes('10 disciplinas'));
    assert(p.log.slice(firstSave+1).some(x=>x[0]==='buscar'&&x[2]==='last'&&x[3]==='d2'));
  }finally{await f.close();}
});

test('Unidade vazia, turma sem Semestre e turma sem disciplinas são registradas e o ciclo continua',async()=>{
  const f=await fixture(),{$,portal:p}=f;
  try{
    p.units.unshift({value:'empty',text:'Unidade Vazia'});p.classes.empty=[];
    p.units.push({value:'u3',text:'Unidade Sem Oferta'});p.classes.u3=[{value:'noStage',text:'Curso sem semestre'},{value:'noSubject',text:'Curso sem disciplinas'}];
    p.stageByClass={noStage:'Etapa 1'};p.subjectsByClass={noSubject:[]};p.render();
    $('direct').click();await wait(()=>$('message').textContent.startsWith('Processamento concluído'));
    const saved=await loadSession(7),map=saved.report.portalMap;
    assert.equal(saved.report.cycle.unitsAttempted,4);assert.equal(saved.report.complete,true);assert.equal(p.saveCount,5);
    assert(map.find(x=>x.unidade.value==='empty').status.includes('Sem turmas'));
    assert(map.find(x=>x.turma?.value==='noStage').status.includes('Semestre ausente'));
    assert(map.find(x=>x.turma?.value==='noSubject').status.includes('Sem disciplinas'));
  }finally{await f.close();}
});

test('Arquivo sem campus aguarda todas as unidades e resolve o destino único sem confirmação',async()=>{
  const p=new FakePortal();installChrome(p);
  await saveSession(7,{version:3,files:[{name:'AD.xlsx',hash:'fictional',count:1}],records:[{...records()[4],campus:'',course:''}],report:null,phase:'idle',pending:null,queue:[],cursor:0});
  const f=await fixture({reuse:true,portal:p});
  try{
    f.$('direct').click();await wait(()=>f.$('message').textContent.startsWith('Processamento concluído'));
    assert.equal(p.saveCount,1);assert.equal(p.bank['b/d1'][0][0].value,'60');
    assert(p.log.findIndex(x=>x[0]==='buscar'&&x[2]==='c'&&x[3]==='d2')<p.log.findIndex(x=>x[0]==='salvar'));
    const saved=await loadSession(7);assert.equal(saved.report.complete,true);assert.equal(saved.report.portalMap.length,9);
  }finally{await f.close();p.close();}
});

test('Conflito entre arquivo com campus e sem campus não permite gravação antecipada',async()=>{
  const p=new FakePortal();installChrome(p);
  await saveSession(7,{version:3,files:[{name:'AD.xlsx',hash:'fictional',count:2}],records:[records()[4],{...records()[4],campus:'',recordId:'conflict',grade:'9'}],report:null,phase:'idle',pending:null,queue:[],cursor:0});
  const f=await fixture({reuse:true,portal:p});
  try{
    f.$('direct').click();await wait(()=>f.$('message').textContent.includes('nenhuma nota pôde ser lançada'));
    assert.equal(p.saveCount,0);const saved=await loadSession(7);
    assert.equal(saved.report.complete,true);assert.equal(saved.report.portalMap.length,9);
    assert(saved.report.rows.every(r=>r.status.includes('Mais de um registro')));
  }finally{await f.close();p.close();}
});

test('Remover arquivo individual mantém os demais, libera uma vaga e persiste ao reabrir',async()=>{
  const f=await fixture();let reopened;
  try{
    f.$('clear').click();await wait(()=>f.$('fileCount').textContent.startsWith('0 /')&&!f.$('settings').disabled);
    const files=[0,3,4,5].map((index,i)=>{const r=records()[index];return new File(['RA;Nome;Disciplina;Nota\n'+[r.ra,r.name,r.discipline,r.grade].join(';')+'\n'],'AD Arquivo '+i+'.csv');});
    Object.defineProperty(f.$('files'),'files',{configurable:true,value:files});f.$('files').dispatchEvent(new Event('change'));
    await wait(()=>f.$('fileCount').textContent.startsWith('4 /')&&!f.$('settings').disabled);
    assert.equal(f.$('clear').closest('details'),null);assert.equal(f.$('clear').hidden,false);
    const buttons=[...f.$('fileList').querySelectorAll('button')];assert.equal(buttons.length,4);assert.equal(buttons[1].textContent,'Remover arquivo');
    buttons[1].click();await wait(()=>f.$('fileCount').textContent.startsWith('3 /')&&!f.$('settings').disabled);
    assert(!f.$('fileList').textContent.includes(files[1].name));
    let saved=await loadSession(7);assert.equal(saved.records.length,3);assert.equal(saved.report,null);
    Object.defineProperty(f.$('files'),'files',{configurable:true,value:[files[1]]});f.$('files').dispatchEvent(new Event('change'));
    await wait(()=>f.$('fileCount').textContent.startsWith('4 /')&&!f.$('settings').disabled);
    reopened=await fixture({reuse:true,portal:f.portal});assert(reopened.$('fileCount').textContent.startsWith('4 /'));
    reopened.$('clear').click();await wait(()=>reopened.$('fileCount').textContent.startsWith('0 /')&&!reopened.$('settings').disabled);
    assert.equal(reopened.$('fileList').childElementCount,0);assert.equal(reopened.$('direct').disabled,true);
    saved=await loadSession(7);assert.equal(saved.records.length,0);assert.equal(saved.files.length,0);assert.equal(f.portal.saveCount,0);
  }finally{await reopened?.close();await f.close();}
});

test('Consulta temporariamente indisponível é repetida automaticamente e o ciclo termina',async()=>{
  const f=await fixture(),{$,portal:p}=f;
  try{
    const execute=p.execute.bind(p);let fail=true;
    p.execute=async(func,command)=>{
      if(fail&&command.action==='catalog'&&p.values.unidade==='u2'){fail=false;return {ok:false,message:'Consulta temporariamente indisponível'};}
      return execute(func,command);
    };
    $('direct').click();await wait(()=>$('message').textContent.startsWith('Processamento concluído'));
    const saved=await loadSession(7);assert.equal(saved.report.complete,true);assert.equal(saved.report.cycle.unitsAttempted,2);
    assert.equal(p.saveCount,5);assert.equal(saved.report.rows.filter(r=>r.saved).length,5);
    assert(saved.report.warnings.some(x=>x.includes('Consulta temporariamente indisponível')));assert.equal($('resume').hidden,true);
  }finally{await f.close();}
});

test('Erro persistente em uma disciplina não impede outras disciplinas nem a última unidade',async()=>{
  const f=await fixture(),{$,portal:p}=f;
  try{
    const execute=p.execute.bind(p);let failures=0;
    p.execute=async(func,command)=>{
      if(command.action==='catalog'&&p.values.turma==='a'&&p.values.disciplina==='d1'){failures++;return {ok:false,message:'Tabela indisponível nesta disciplina'};}
      return execute(func,command);
    };
    $('direct').click();await wait(()=>$('message').textContent.startsWith('Processamento concluído'));
    const saved=await loadSession(7);assert.equal(saved.report.complete,true);assert.equal(p.saveCount,3);assert(failures>=4);
    assert.equal(p.bank['a/d2'][0][0].value,'70');assert.equal(p.bank['b/d1'][0][0].value,'60');assert.equal(p.bank['c/d1'][0][0].value,'100');
    assert(saved.report.portalMap.some(m=>m.failed&&m.turma.value==='a'&&m.disciplina.value==='d1'));
    assert(saved.report.rows.find(r=>r.recordId==='record-0').status.includes('consulta incompleta'));
    assert(p.log.some(x=>x[0]==='buscar'&&x[2]==='c'&&x[3]==='d2'));assert.equal($('resume').hidden,true);
  }finally{await f.close();}
});

test('Todas as consultas falham: registra cada opção e encerra o ciclo sem prender na primeira',async()=>{
  const f=await fixture(),{$,portal:p}=f;
  try{
    const execute=p.execute.bind(p);let failures=0;
    p.execute=async(func,command)=>command.action==='catalog'?(failures++,{ok:false,message:'Falha de leitura simulada'}):execute(func,command);
    $('direct').click();await wait(()=>$('message').textContent.includes('nenhuma nota pôde ser lançada'));
    const saved=await loadSession(7);assert.equal(saved.report.complete,true);assert.equal(saved.report.cycle.unitsAttempted,2);assert.equal(p.saveCount,0);
    assert.equal(saved.report.portalMap.filter(m=>m.failed).length,9);assert.equal(failures,18);
    assert.equal($('resume').hidden,true);assert(saved.report.warnings.length>=9);
  }finally{await f.close();}
});

test('Resposta perdida no preenchimento descarta somente seus campos e segue para as demais páginas',async()=>{
  const f=await fixture(),{$,portal:p}=f;
  try{
    const execute=p.execute.bind(p);let fail=true;
    p.execute=async(func,command)=>{
      const result=await execute(func,command);
      if(fail&&command.action==='apply'){fail=false;throw new Error('Resposta do preenchimento perdida');}
      return result;
    };
    $('direct').click();await wait(()=>$('message').textContent.startsWith('Processamento concluído'));
    const saved=await loadSession(7);assert.equal(saved.report.complete,true);assert.equal(p.saveCount,4);
    assert.equal(p.bank['a/d1'][0][0].value,'');assert.equal(p.bank['a/d1'][1][0].value,'90');assert.equal(p.bank['c/d1'][0][0].value,'100');
    assert(!saved.report.rows.find(r=>r.recordId==='record-0').saved);assert.equal($('resume').hidden,true);
    assert(saved.report.warnings.some(w=>w.includes('preenchimento')));
  }finally{await f.close();}
});

test('Aviso de falha ao salvar é fechado e o restante do lote é salvo sem nova confirmação',async()=>{
  const f=await fixture(),{$,portal:p}=f;
  try{
    const execute=p.execute.bind(p);let closed=0;
    p.execute=async(func,command)=>{
      if(command.action==='saveClick'){
        const reject=p.values.turma==='a'&&p.values.disciplina==='d1'&&p.page===1;
        p.rejectSave=reject;
        if(reject){const d=p.dom.window.document,b=d.querySelector('#salvar'),original=b.onclick;
          b.onclick=()=>{original();const modal=d.createElement('div');modal.setAttribute('role','dialog');modal.textContent='Não foi possível salvar as notas desta turma.';const ok=d.createElement('button');ok.textContent='OK';ok.onclick=()=>{closed++;modal.remove();};modal.append(ok);d.body.append(modal);};
        }
      }
      return execute(func,command);
    };
    $('direct').click();await wait(()=>$('message').textContent.startsWith('Processamento concluído'));
    const saved=await loadSession(7);assert.equal(saved.report.complete,true);assert.equal(p.saveCount,5);assert.equal(closed,1);
    assert.equal(saved.report.rows.filter(r=>r.saved).length,4);assert.equal(p.bank['a/d1'][0][0].value,'');assert.equal(p.bank['c/d1'][0][0].value,'100');
    assert(saved.report.warnings.some(w=>w.includes('Não foi possível salvar')));assert.equal($('resume').hidden,true);
  }finally{await f.close();}
});

test('Gravação aceita com resposta perdida é confirmada por releitura sem clicar Salvar novamente',async()=>{
  const f=await fixture(),{$,portal:p}=f;
  try{
    const execute=p.execute.bind(p);let fail=true;
    p.execute=async(func,command)=>{
      const result=await execute(func,command);
      if(fail&&command.action==='saveClick'){fail=false;await new Promise(r=>originalTimer(r,5));throw new Error('Resposta de gravação perdida');}
      return result;
    };
    $('direct').click();await wait(()=>$('message').textContent.startsWith('Processamento concluído'));
    const saved=await loadSession(7);assert.equal(saved.report.complete,true);assert.equal(saved.report.rows.filter(r=>r.saved).length,5);assert.equal(p.saveCount,5);
    assert.equal(p.log.filter(x=>x[0]==='salvar'&&x[2]==='a'&&x[3]==='d1'&&x[4]===1).length,1);
  }finally{await f.close();}
});

test('Erro ao selecionar uma unidade não impede tentar a unidade seguinte',async()=>{
  const f=await fixture(),{$,portal:p}=f;
  try{
    p.units.push({value:'u3',text:'Última Unidade'});p.classes.u3=[{value:'last',text:'Curso Final 1º período'}];p.bank['last/d1']=[[]];p.bank['last/d2']=[[]];p.render();
    const execute=p.execute.bind(p);let failures=0;
    p.execute=async(func,command)=>{
      if(command.action==='select'&&command.kind==='unidade'&&command.value==='u2'){failures++;return {ok:false,message:'Unidade temporariamente bloqueada'};}
      return execute(func,command);
    };
    $('direct').click();await wait(()=>$('message').textContent.startsWith('Processamento concluído'));
    const saved=await loadSession(7);assert.equal(saved.report.complete,true);assert.equal(saved.report.cycle.unitsAttempted,3);assert.equal(p.saveCount,4);assert.equal(failures,2);
    assert(saved.report.portalMap.some(m=>m.unidade.value==='u2'&&m.failed));
    assert(p.log.some(x=>x[0]==='buscar'&&x[2]==='last'&&x[3]==='d2'));assert.equal($('resume').hidden,true);
  }finally{await f.close();}
});

test('Gravação parcial confirma cada aluno separadamente e continua até a última disciplina',async()=>{
  const p=new FakePortal();installChrome(p);
  const data=records();data[1]={...data[1],grade:'6',absent:'false'};
  await saveSession(7,{version:4,files:[{name:'AD.xlsx',hash:'fictional',count:7}],records:data,report:null,phase:'idle',pending:null,queue:[],cursor:0});
  const f=await fixture({reuse:true,portal:p});
  try{
    const execute=p.execute.bind(p);
    p.execute=async(func,command)=>{
      if(command.action==='saveClick'&&p.values.turma==='a'&&p.values.disciplina==='d1'&&p.page===1){
        const button=p.dom.window.document.querySelector('#salvar'),original=button.onclick;
        button.onclick=()=>{original();p.bank['a/d1'][0][1].value='';p.render();};
      }
      return execute(func,command);
    };
    f.$('direct').click();await wait(()=>f.$('message').textContent.startsWith('Processamento concluído'));
    const saved=await loadSession(7);assert.equal(saved.report.complete,true);assert.equal(p.saveCount,5);
    assert.equal(saved.report.rows.find(r=>r.recordId==='record-0').saved,true);
    assert(!saved.report.rows.find(r=>r.recordId==='record-1').saved);assert(saved.report.rows.find(r=>r.recordId==='record-1').status.includes('não confirmada'));
    assert.equal(p.bank['c/d1'][0][0].value,'100');assert.equal(saved.report.rows.filter(r=>r.saved).length,5);assert.equal(f.$('resume').hidden,true);
  }finally{await f.close();p.close();}
});
