// Executed in Chrome's isolated extension world. No cookies, credentials or requests.
export async function portalCommand(command) {
  const norm=v=>String(v??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toUpperCase().replace(/\s+/g,' ').trim();
  const raKey=v=>String(v??'').trim().replace(/^(\d+)\.0+$/,'$1').toUpperCase();
  const visible=e=>e.isConnected && e.getClientRects().length>0 && getComputedStyle(e).visibility!=='hidden' && getComputedStyle(e).display!=='none';
  const clean=e=>(e.innerText??e.textContent??'').replace(/\s+/g,' ').trim();
  const failure=(message,code)=>({ok:false,message,...(code?{code}:{})});
  if(location.protocol!=='https:' || location.hostname!=='portal.sophia.com.br') return failure('Abra o portal SophiA em HTTPS.');
  if(!/\/LancNotas\.aspx$/i.test(location.pathname)||Array.from(document.querySelectorAll('input[type="password"]')).some(visible)) return failure('Entre novamente no SophiA na mesma aba.','SESSION_UNAVAILABLE');
  if(document.readyState==='loading') return failure('Aguarde o portal terminar de carregar.');
  const stateKey='__SOPHIA_NOTAS_ASSISTENTE_V1__';
  if(command.action==='prepareRecovery'){
    const state=globalThis[stateKey];
    if(state){state.cancelled=true;for(let i=0;i<25&&state.applying;i++)await new Promise(r=>setTimeout(r,40));}
    if(state?.applying)return failure('Aguardando o preenchimento anterior terminar.','APPLY_ACTIVE');
    const tables=Array.from(document.querySelectorAll('table')).filter(t=>visible(t)&&Array.from(t.rows).some(r=>Array.from(r.cells).some(c=>/^(RA|MATRICULA|CODIGO|CODIGO DO ALUNO)$/.test(norm(clean(c))))));
    const dirty=[...new Set(tables.flatMap(t=>Array.from(t.querySelectorAll('input[type="text"],input[type="number"],input:not([type])'))))].filter(e=>visible(e)&&e.value!==e.defaultValue);
    if(dirty.some(input=>!state?.owned?.some(c=>c.input===input&&input.value===c.after)))return failure('Há alterações manuais no SophiA que precisam ser salvas ou descartadas antes de continuar.','MANUAL_CHANGES');
    return {ok:true,discardable:dirty.length};
  }
  const dialogs=Array.from(document.querySelectorAll('.cortinaDialogo, [role="dialog"], .dialogo')).filter(visible)
    .filter(e=>!String(e.className).includes('cc-') && !/cookieconsent/i.test(e.getAttribute('aria-label')||''));
  if(dialogs.length) return failure('Há uma janela aberta no portal. Leia e feche a mensagem antes de continuar.');
  const context=()=>Array.from(document.querySelectorAll('select')).filter(e=>/periodo|unidade|turma|etapa|disciplina/i.test(e.id+' '+e.name)).map(e=>({
    id:e.id || e.name,value:e.value,text:e.options[e.selectedIndex]?.text?.trim()||'',disabled:e.disabled
  }));
  if(command.action==='catalog'){
    const found=[];
    for(const table of document.querySelectorAll('table')){
      if(!visible(table))continue;
      const rows=Array.from(table.rows).filter(r=>r.closest('table')===table);
      for(let h=0;h<rows.length;h++){
        const cells=Array.from(rows[h].cells),headers=cells.map(c=>norm(clean(c)));
        if(headers.filter(x=>['NOME','ALUNO','NOME DO ALUNO'].includes(x)).length!==1||headers.filter(x=>['RA','MATRICULA','CODIGO','CODIGO DO ALUNO'].includes(x)).length!==1)continue;
        if(cells.some(c=>c.colSpan>1||c.rowSpan>1))continue;
        const codeIndex=headers.findIndex(x=>['RA','MATRICULA','CODIGO','CODIGO DO ALUNO'].includes(x));
        const nameIndex=headers.findIndex(x=>['NOME','ALUNO','NOME DO ALUNO'].includes(x));
        const statusIndex=headers.indexOf('SITUACAO');
        // Inactive enrolments may have fewer grade cells. They still belong to
        // the roster and must not be reported as absent students.
        const data=rows.slice(h+1).filter(r=>visible(r)&&r.cells[codeIndex]&&r.cells[nameIndex]&&clean(r.cells[codeIndex])&&clean(r.cells[nameIndex])&&!Array.from(r.cells).some(c=>c.colSpan>1||c.rowSpan>1));
        const excluded=['RA','NOME','ALUNO','FOTO','CODIGO','MATRICULA','SITUACAO','DISPENSA','MEDIA','NUMERO','N'];
        const columns=headers.map((label,i)=>{
          if(!/^[A-Z][A-Z0-9]{0,7}$/.test(label)||excluded.includes(label)||!(['AD','AI','PS','AS','AE'].includes(label)||data.some(r=>r.cells[i]?.querySelector('input[type="text"],input[type="number"],input:not([type])'))))return null;
          const cells=data.map(r=>r.cells[i]).filter(Boolean);
          const editable=cells.map(c=>Array.from(c.querySelectorAll('input[type="text"],input[type="number"],input:not([type])')).filter(visible)).filter(inputs=>inputs.length===1&&!inputs[0].matches(':disabled')&&!inputs[0].readOnly&&inputs[0].getAttribute('aria-disabled')!=='true').map(inputs=>inputs[0]);
          return {exam:label,editable:editable.length,empty:editable.filter(i=>!i.value.trim()).length,filled:cells.filter(c=>{const i=c.querySelector('input[type="text"],input[type="number"],input:not([type])');return (i?i.value:clean(c)).trim();}).length};
        }).filter(Boolean);
        const roster=data.map(r=>({ra:raKey(clean(r.cells[codeIndex])),name:clean(r.cells[nameIndex]),status:statusIndex>=0&&r.cells[statusIndex]?clean(r.cells[statusIndex]):''}));
        found.push({assessments:columns.map(c=>c.exam),columns,students:data.length,roster,identity:JSON.stringify(roster.map(r=>[r.ra,r.name]))});
      }
    }
    if(found.length===1)return {ok:true,...found[0],assessmentsKnown:true,context:context()};
    const emptyShell=Array.from(document.querySelectorAll('[id$="NotasTabPanel_tbLancNotas"]')).filter(visible);
    const notesPanels=Array.from(document.querySelectorAll('[id$="LancamentoTabContainer_NotasTabPanel"]')).filter(visible);
    const filters=context();
    // SophiA also returns a successful, empty result without an empty-state
    // message: only its notes shell remains. Do not call that a missing column.
    if(!found.length&&emptyShell.length===1&&!emptyShell[0].rows.length&&notesPanels.length===1&&filters.length===5&&filters.every(c=>c.disabled))return {ok:true,assessments:[],assessmentsKnown:false,columns:[],students:0,roster:[],identity:'empty-notes-shell',emptyReason:'Tela de notas sem lista de alunos',context:filters};
    if(!found.length&&Array.from(document.querySelectorAll('td,p,span,div')).some(e=>visible(e)&&/^(?:nenhum (?:aluno|registro|resultado|dado)(?: encontrado| localizado| disponível)?[.!]?|não (?:há|existem) (?:alunos|registros)(?: para (?:esta|essa) (?:turma|disciplina))?[.!]?)$/i.test(clean(e))))return {ok:true,assessments:[],columns:[],students:0,roster:[],identity:'empty',context:context()};
    return failure(found.length?'Mais de uma tabela de alunos. O mapeamento foi interrompido.':'Tabela de alunos não reconhecida. O mapeamento foi interrompido.');
  }
  const exam=norm(command.exam);
  if(!/^[A-Z0-9]{1,8}$/.test(exam)) return failure('Informe uma avaliação como AD, AI ou PS.');
  function scan() {
    const candidates=[],baseHeaders=[];
    for(const [tableIndex,table] of Array.from(document.querySelectorAll('table')).entries()) {
      if(!visible(table)) continue;
      const rows=Array.from(table.rows).filter(r=>r.closest('table')===table);
      for(let h=0;h<rows.length;h++) {
        const headers=Array.from(rows[h].cells).map(c=>norm(clean(c)));
        const names=headers.map((s,i)=>['NOME','ALUNO','NOME DO ALUNO'].includes(s)?i:-1).filter(i=>i>=0);
        const codes=headers.map((s,i)=>['CODIGO','CODIGO DO ALUNO','RA','MATRICULA'].includes(s)?i:-1).filter(i=>i>=0);
        if(names.length!==1 || codes.length!==1) continue;
        baseHeaders.push(headers);
        const grades=headers.map((s,i)=>s.split(/[^A-Z0-9]+/).includes(exam)?i:-1).filter(i=>i>=0);
        if(grades.length!==1) continue;
        if(Array.from(rows[h].cells).some(c=>c.colSpan>1 || c.rowSpan>1)) continue;
        const result=[];
        for(let i=h+1;i<rows.length;i++) {
          const cells=Array.from(rows[i].cells);
          const nameCell=cells[names[0]],codeCell=cells[codes[0]],gradeCell=cells[grades[0]];
          if(!nameCell || !codeCell || nameCell.tagName==='TH' || !visible(rows[i])) continue;
          if(cells.some(c=>c.colSpan>1 || c.rowSpan>1)) continue;
          const name=(nameCell.getAttribute('title') || nameCell.querySelector('[title]')?.getAttribute('title') || clean(nameCell)).trim();
          const ra=raKey(clean(codeCell));
          if(!name || !ra) continue;
          const inputs=gradeCell ? Array.from(gradeCell.querySelectorAll('input[type="text"],input[type="number"],input:not([type])')).filter(visible) : [];
          const input=inputs.length===1?inputs[0]:null;
          result.push({key:tableIndex+':'+i,ra,name,value:input?input.value:gradeCell?clean(gradeCell):'',
            editable:!!input&&!input.matches(':disabled')&&!input.readOnly&&input.getAttribute('aria-disabled')!=='true', type:input?.type||'',
            inputId:input?.id||input?.name||'', maxLength:input?.maxLength??-1,min:input?.min||'',max:input?.max||'',step:input?.step||'',input});
        }
        candidates.push({rows:result,headers,tableIndex});
      }
    }
    if(!candidates.length&&baseHeaders.length===1&&!baseHeaders[0].some(s=>s.split(/[^A-Z0-9]+/).includes(exam))){const e=new Error('A avaliação '+exam+' não está disponível nesta turma.');e.code='ASSESSMENT_UNAVAILABLE';throw e;}
    if(candidates.length!==1) throw new Error(candidates.length ? 'Mais de uma tabela corresponde à avaliação. Nenhum preenchimento foi feito.' : 'Tabela de alunos/coluna '+exam+' não identificada. Busque a turma no portal e confira a avaliação.');
    const found=candidates[0], ctx=context();
    const identity=JSON.stringify({url:location.href,exam,context:ctx,headers:found.headers,
      rows:found.rows.map(r=>[r.key,r.ra,r.name,r.inputId,r.type])});
    return {...found,context:ctx,identity,url:location.origin+location.pathname};
  }
  const publicScan=s=>({...s,rows:s.rows.map(({input,...r})=>r),fingerprint:JSON.stringify([s.identity,s.rows.map(r=>[r.value,r.editable,r.maxLength,r.min,r.max,r.step])])});
  let current;
  try {current=scan();} catch(e) {return failure(e.message,e.code);}
  if(command.action==='scan') return {ok:true,snapshot:publicScan(current)};
  if(command.action==='prepareSave') {
    const filled=globalThis[stateKey];
    if(!filled||filled.token!==command.token||filled.identity!==current.identity)return failure('A turma ou a página mudou antes de gravar. A gravação não foi iniciada.');
    if(filled.saveIssued)return failure('A gravação desta turma já foi solicitada. Confira por releitura; ela não será repetida automaticamente.');
    if(!Array.isArray(command.changes)||!command.changes.length)return failure('Não há notas conferidas para gravar.');
    if(command.changes.length!==filled.changes.length)return failure('O lote de gravação não corresponde ao preenchimento conferido.');
    if(new Set(command.changes.map(c=>c.key)).size!==command.changes.length||filled.changes.some(c=>!command.changes.some(x=>x.key===c.key)))return failure('O lote de gravação contém destinos divergentes.');
    for(const c of command.changes){
      const row=current.rows.find(r=>r.key===c.key);
      const expected=row?.type==='number'?c.after.replace(',','.'):c.after;
      if(!row||row.ra!==c.ra||norm(row.name)!==norm(c.name)||row.value!==expected)return failure('Um valor mudou antes de gravar. Confira a turma; a gravação não foi iniciada.');
    }
    const candidates=Array.from(document.querySelectorAll('button,a,input[type="submit"],input[type="button"]')).filter(e=>visible(e)&&!e.matches(':disabled')&&!e.disabled&&e.getAttribute('aria-disabled')!=='true'&&['GRAVAR','SALVAR'].includes(norm(e.value||clean(e))));
    let buttons=candidates.filter(e=>norm(e.value||clean(e))==='SALVAR');if(!buttons.length)buttons=candidates;
    if(buttons.length>1&&buttons.every(e=>e.tagName==='A'&&e.getAttribute('href')&&e.getAttribute('href')===buttons[0].getAttribute('href')&&e.getAttribute('onclick')===buttons[0].getAttribute('onclick')&&e.closest('form')===buttons[0].closest('form'))){
      buttons=[...buttons].sort((a,b)=>a.getBoundingClientRect().top-b.getBoundingClientRect().top).slice(0,1);
    }
    if(buttons.length!==1)return failure('O comando Salvar não foi identificado de forma única nesta página.');
    const button=buttons[0],column=current.headers.findIndex(s=>s.split(/[^A-Z0-9]+/).includes(exam));
    const fields=command.changes.map(c=>{
      const row=current.rows.find(r=>r.key===c.key),[table,index]=row.key.split(':').map(Number);
      return {table,row:index,column,id:row.inputId,value:row.value,ra:row.ra,name:row.name,
        raColumn:current.headers.findIndex(s=>['RA','MATRICULA','CODIGO','CODIGO DO ALUNO'].includes(s)),
        nameColumn:current.headers.findIndex(s=>['NOME','ALUNO','NOME DO ALUNO'].includes(s))};
    });
    // Validation remains isolated; the click is performed separately in MAIN.
    filled.saveIssued=true;
    return {ok:true,prepared:true,nonce:filled.token,url:current.url,context:current.context,fields,
      button:{tag:button.tagName,id:button.id||'',name:button.name||'',label:norm(button.value||clean(button)),href:button.getAttribute('href')||'',onclick:button.getAttribute('onclick')||''}};
  }
  if(command.action==='undo') {
    const state=globalThis[stateKey];
    if(!state || state.token!==command.token || state.identity!==current.identity) return failure('Não há preenchimento para desfazer nesta mesma tela.');
    const map=new Map(current.rows.map(r=>[r.key,r]));
    if(state.changes.some(c=>!map.get(c.key)?.editable || map.get(c.key).value!==c.after)) return failure('A página ou uma nota mudou. Desfazer bloqueado para preservar alterações posteriores.');
    const restored=[];
    for(const change of [...state.changes].reverse()) {
      let fresh;try {fresh=scan();} catch {return failure('A página mudou durante a restauração. Confira os valores no portal.');}
      if(fresh.identity!==state.identity) return failure('A turma mudou durante a restauração. Confira os valores no portal.');
      const row=fresh.rows.find(r=>r.key===change.key);
      if(row.value!==change.after) return failure('Uma nota mudou durante a restauração. Confira os valores no portal.');
      setValue(row.input,change.before);
      await new Promise(resolve=>setTimeout(resolve,40));
      if(!row.input.isConnected || row.input.value!==change.before) return failure('O portal não confirmou a restauração. Confira os valores.');
      restored.push(change.key);
    }
    delete globalThis[stateKey];
    return {ok:true,count:restored.length,message:'Valores restaurados nos campos. Isso não confirma nem desfaz gravações no servidor.'};
  }
  if(command.action!=='apply') return failure('Comando desconhecido.');
  if(command.fingerprint!==publicScan(current).fingerprint) return failure('Os campos mudaram após a leitura. Atualizando as correspondências.','STALE_SNAPSHOT');
  const changes=command.changes;
  if(!Array.isArray(changes) || !changes.length || changes.length>2000 || new Set(changes.map(x=>x.key)).size!==changes.length) return failure('Lote vazio, repetido ou muito grande.');
  const byKey=new Map(current.rows.map(r=>[r.key,r]));
  for(const c of changes) {
    const row=byKey.get(c.key);
    if(!row || row.ra!==c.ra || norm(row.name)!==norm(c.name)) return failure('Uma correspondência deixou de ser válida. Atualize a prévia.');
    if(typeof c.after!=='string'||(!/^(?:\d+(?:,\d+)?)$/.test(c.after)&&!(c.after===''&&c.blank===true))||(c.after!==''&&Number(c.after.replace(',','.'))>Number(command.max)))return failure('Valor de nota inválido. Faltosos devem permanecer em branco.');
    if(c.blank===true&&c.after!=='')return failure('Faltosos devem permanecer em branco.');
    if(c.after==='F' && row.type==='number') return failure('Campo numérico não aceita F.');
  }
  function fieldBlock(row,c){
    if(!row?.editable)return 'Não inserido: campo bloqueado durante o preenchimento';
    if(row.value!==c.before||command.onlyEmpty&&row.value.trim())return 'Não inserido: valor alterado ou nota já existente';
    const v=row.type==='number'?c.after.replace(',','.'):c.after;
    if(v===''&&row.input.required)return 'Não inserido: campo obrigatório no SophiA';
    if(row.maxLength>=0&&v.length>row.maxLength)return 'Não inserido: valor excede o tamanho permitido pelo campo';
    if(row.type==='number'&&v!==''){
      const n=Number(v),min=row.input.min,max=row.input.max,step=row.input.step;
      if((min!==''&&n<Number(min))||(max!==''&&n>Number(max)))return 'Não inserido: nota fora do limite do campo';
      if(step&&step!=='any'&&Math.abs((n-Number(min||0))/Number(step)-Math.round((n-Number(min||0))/Number(step)))>1e-8)return 'Não inserido: precisão da nota não aceita pelo campo';
    }
    return '';
  }
  const state={token:crypto.randomUUID(),identity:current.identity,changes:[],owned:[],applying:true,cancelled:false};
  globalThis[stateKey]=state;
  const results=[];
  try{for(const c of changes) {
    if(state.cancelled)return {ok:false,message:'Preenchimento cancelado para recuperação automática.',results,token:state.token};
    let fresh;
    try {fresh=scan();} catch(e) {return {ok:false,message:e.message,results,token:state.token};}
    if(fresh.identity!==state.identity) return {ok:false,message:'A página mudou durante o preenchimento. Confira o lote antes de repetir.',results,token:state.token};
    const row=fresh.rows.find(r=>r.key===c.key);
    if(state.changes.some(done=>fresh.rows.find(r=>r.key===done.key)?.value!==done.after)) return {ok:false,message:'Um campo preenchido mudou. Confira o lote antes de repetir.',results,token:state.token};
    const blocked=fieldBlock(row,c);
    if(blocked){results.push({key:c.key,ra:c.ra,skipped:true,status:blocked});continue;}
    const after=row.type==='number'?c.after.replace(',','.'):c.after;
    state.changes.push({key:c.key,before:c.before,after});
    state.owned.push({input:row.input,before:c.before,after});
    setValue(row.input,after);
    await new Promise(resolve=>setTimeout(resolve,40));
    const accepted=row.input.isConnected && row.input.value===after && row.input.validity.valid;
    results.push({key:c.key,ra:c.ra,status:accepted?'Preenchido; gravação não confirmada':'Valor recusado ou página recarregada; conferir',value:row.input.value});
    if(!accepted&&row.input.isConnected&&[after,c.before].includes(row.input.value)){
      let unchanged;try{unchanged=scan().identity===state.identity;}catch{unchanged=false;}
      if(unchanged){
        if(row.input.value!==c.before){setValue(row.input,c.before);await new Promise(resolve=>setTimeout(resolve,40));}
        if(row.input.isConnected&&row.input.value===c.before){
          state.changes.pop();state.owned.pop();
          results[results.length-1]={key:c.key,ra:c.ra,skipped:true,status:'Não inserido: campo recusou a nota; demais alunos continuam',value:c.before};
          continue;
        }
      }
    }
    if(!accepted) return {ok:false,message:'O portal recusou ou alterou um campo. Processo interrompido; confira os valores.',results,token:state.token};
  }
  return {ok:true,message:'Campos preenchidos. O lote seguirá para gravação e releitura automática.',results,token:state.token};
  }finally{state.applying=false;}
  function setValue(input,value) {
    const setter=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value')?.set;
    if(setter) setter.call(input,value);else input.value=value;
    input.dispatchEvent(new Event('input',{bubbles:true}));
    input.dispatchEvent(new Event('change',{bubbles:true}));
    input.dispatchEvent(new Event('blur',{bubbles:true}));
  }
}
