/* SmartFox: regras explícitas de extensão de resposta; não avalia conteúdo. */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.SmartFoxGradingAutomation=api;
})(typeof window!=='undefined'?window:globalThis,function(){
  'use strict';
  const DEFAULTS=Object.freeze({version:2,lineWidth:80,minLines:2,shortScore:0.5,creditPercent:100,scope:'all',feedbackMode:'expected-answer'});
  const itemIssue=(message,kind)=>Object.assign(Error(message),{code:'SF_GRADING_ITEM',kind});
  function validatePolicy(value){
    const p={...DEFAULTS};
    for(const key of ['lineWidth','minLines','shortScore','creditPercent','scope'])if(value?.[key]!==undefined)p[key]=value[key];
    for(const [key,min,max]of [['lineWidth',20,500],['minLines',2,100]]){
      p[key]=Number(p[key]);if(!Number.isInteger(p[key])||p[key]<min||p[key]>max)throw Error('Confira a largura da linha e o mínimo de linhas.');
    }
    p.creditPercent=Number(String(p.creditPercent).replace(',','.'));
    if(!Number.isFinite(p.creditPercent)||p.creditPercent<=0||p.creditPercent>100)throw Error('O percentual deve ser maior que zero e até 100%.');
    p.shortScore=Number(String(p.shortScore).replace(',','.'));
    if(!Number.isFinite(p.shortScore)||p.shortScore<0)throw Error('A nota para resposta curta deve ser zero ou positiva.');
    if(!['all','current'].includes(p.scope))throw Error('Escolha as avaliações do lote.');
    return Object.freeze(p);
  }
  function responseText(html,plain=''){
    if(html==null||html==='')return clean(plain);
    const source=String(html).replace(/<(script|style)\b[^>]*>[\s\S]*?<\/\1>/gi,'')
      .replace(/<br\b[^>]*>|<\/(?:p|div|li|tr|h[1-6]|blockquote)>/gi,' ');
    let text;
    if(typeof DOMParser!=='undefined')text=new DOMParser().parseFromString(source,'text/html').body.textContent||'';
    else text=source.replace(/<[^>]*>/g,' ').replace(/&#(x[0-9a-f]+|\d+);/gi,(_,n)=>{
      const code=n[0].toLowerCase()==='x'?parseInt(n.slice(1),16):Number(n);
      return code>0&&code<=0x10ffff?String.fromCodePoint(code):'';
    }).replace(/&(nbsp|amp|lt|gt|quot|apos);/gi,(_,n)=>({nbsp:' ',amp:'&',lt:'<',gt:'>',quot:'"',apos:"'"})[n.toLowerCase()]);
    return clean(text);
  }
  function clean(value){return String(value??'').normalize('NFC').replace(/[\u200b-\u200f\u202a-\u202e\u2060-\u206f\ufeff]/g,'').replace(/\s+/gu,' ').trim();}
  function countLines(text,width=80){
    const normalized=clean(text),chars=Array.from(normalized).length;
    // Text flows in fixed character cells. Enter and blank paragraphs add no credit.
    return {text:normalized,characters:chars,lines:chars?Math.ceil(chars/width):0};
  }
  function metadata(assessment,course,explicit={}){
    const title=clean(assessment),header=clean(course);
    const exam=title.match(/\b(P[123]|AD|AI|PS|SCH|AV[123]|A[123])\b/i)?.[1]?.toUpperCase()||'';
    const model=title.match(/\bmodelo\s*[:#-]?\s*([\p{L}\d]+)/iu)?.[1]||'';
    const term=title.match(/\b20\d{2}[./-][12]\b/)?.[0]||'';
    const afterPeriod=header.match(/\b\d+\s*[º°o]?\s*PER[IÍ]ODO\s*-\s*(.+?)(?:\s*\||$)/i)?.[1];
    const discipline=clean(explicit.discipline||afterPeriod||'');
    return {assessment:title,exam,model,term,course:header,discipline,disciplineSource:explicit.discipline?'campo do AvaliA':afterPeriod?'cabeçalho da turma':''};
  }
  function expectedFeedback(input){
    const html=String(input.expectedHtml??''),text=responseText(html,input.expectedText);
    if(!text&&!/<(?:img|svg|math)\b/i.test(html))throw itemIssue('Padrão de resposta não disponível. Resposta reservada para conferência, sem preencher a nota.','reference');
    // The native HTML is copied unchanged: no templates, additions or truncation.
    return Object.freeze({feedback:text,feedbackHtml:html});
  }
  function decide(input,policy){
    const p=validatePolicy(policy),max=Number(input.maxScore);
    if(input.mediaAnswer)throw itemIssue('Resposta com imagem, arquivo, áudio ou link: reservada para conferência.','media');
    if(input.maxScore==null||input.maxScore===''||!Number.isFinite(max)||max<=0)throw itemIssue('Peso máximo não identificado. Nenhuma nota foi enviada.','weight');
    const metric=countLines(responseText(input.responseHtml,input.responseText),p.lineWidth);
    const outcome=metric.lines===0?'empty':metric.lines<p.minLines?'short':'credit';
    const increment=input.step==='any'?null:Number(String(input.step||'0.001').replace(',','.'));
    if(increment!==null&&(!Number.isFinite(increment)||increment<=0))throw Error('Precisão da nota não identificada.');
    let score=outcome==='credit'?max*p.creditPercent/100:outcome==='short'?Math.min(p.shortScore,max):0;
    if(increment!==null&&(outcome==='short'||p.creditPercent!==100))score=Math.min(Math.round(score/increment)*increment,Math.floor((max+1e-10)/increment)*increment);
    score=Number(score.toFixed(6));
    if(increment!==null&&Math.abs(score/increment-Math.round(score/increment))>1e-7)throw Error('O peso máximo não respeita a precisão do campo. Confira o AvaliA.');
    const meta=metadata(input.assessment,input.course,{discipline:input.discipline});
    const data={score,maxScore:max,lines:metric.lines,characters:metric.characters,minLines:p.minLines,lineWidth:p.lineWidth,metadata:meta};
    return Object.freeze({...data,outcome,...expectedFeedback(input),policy:p,contentEvaluated:false});
  }
  function queueTarget(href,origin,scope){
    const url=new URL(href,origin);
    if(url.origin!==origin||url.pathname!=='/CorrecaoDiscursiva/Modal'||url.searchParams.get('idInstituicao')!==String(scope.institution)||url.searchParams.get('idAvaliacao')!==String(scope.assessment)||url.searchParams.get('status')!=='1')throw Error('A lista não corresponde à instituição, avaliação e pendências selecionadas. Pesquise novamente.');
    url.searchParams.sort();return url.pathname+url.search;
  }
  function paginationState(wrapper){
    const pending={ready:false,end:false,next:null,token:''};
    if(!wrapper)return pending;
    const label=e=>clean(e?.textContent);
    const pager=wrapper.querySelector('#TabelaQuestoesDiscursivas_paginate,.dataTables_paginate');
    const info=label(wrapper.querySelector('.dataTables_info'));
    const token=label(pager?.querySelector('.active,.current,[aria-current="page"]'))+'|'+info;
    // Bootstrap wrappers, direct DataTables links/buttons, and the native ID.
    const control=pager?.querySelector('#TabelaQuestoesDiscursivas_next,.next,[rel="next"]')||
      Array.from(pager?.querySelectorAll('a,button')||[]).find(e=>/^(próximo|proximo|next)$/i.test(label(e)||e.getAttribute('aria-label')||''));
    if(control){
      const next=control.matches('a,button')?control:control.querySelector('a,button');
      const disabled=e=>Boolean(e&&(e.disabled||e.classList.contains('disabled')||e.getAttribute('aria-disabled')==='true'||e.closest('li.disabled,.paginate_button.disabled,[aria-disabled="true"]')));
      if(disabled(control)||disabled(next))return {ready:true,end:true,next:null,token};
      return next?{ready:true,end:false,next,token}:pending;
    }
    // A single/empty page may omit Next entirely. An unfinished pager is not an error yet.
    const range=info.match(/Mostrando de ([\d.]+) at[eé] ([\d.]+) de ([\d.]+) registros/i);
    if(range){
      const [start,end,total]=range.slice(1).map(v=>Number(v.replace(/\./g,'')));
      if(start<=end&&end===total)return {ready:true,end:true,next:null,token};
    }
    return pending;
  }
  function createRunner(adapter){
    let state='idle',stopRequested=false,counts={confirmed:0,skipped:0,pending:0},lastError='';
    const status=()=>({state,...counts,lastError});
    const emit=()=>adapter.status?.(status());
    const pause=()=>{stopRequested=true;if(state==='running'){state='pausing';emit();}};
    const check=()=>{if(stopRequested)throw Error('Execução pausada. Nenhuma nova correção será iniciada.');adapter.assertScope();};
    async function start(policy){
      if(['running','pausing'].includes(state))throw Error('Já existe uma correção automática em execução.');
      const p=validatePolicy(policy);state='running';stopRequested=false;counts={confirmed:0,skipped:0,pending:0};lastError='';emit();
      try{
        await adapter.runExclusive(async()=>{
          check();await adapter.begin(p);
          const assessments=adapter.assessments(p);
          if(!assessments.length)throw Error('Nenhuma avaliação disponível nesta instituição.');
          for(const assessment of assessments){
            check();await adapter.selectAssessment(assessment);check();
            const visitedGroups=new Set();let newGroups;
            do{
              newGroups=0;await adapter.search();check();
              let more=true;
              while(more){
                check();let rows=adapter.rows();
                for(const row of rows){
                  check();if(visitedGroups.has(row.key))continue;
                  await adapter.open(row);check();
                  const seen=new Set();
                  for(;;){
                    check();const c=await adapter.current();if(!c)throw Error('Resposta não identificada. Confira a tela do AvaliA.');
                    if(seen.has(c.id))break;seen.add(c.id);
                    try{
                      if(await adapter.alreadyDone(c)){counts.skipped++;}
                      else{
                        const d=decide(c,p);await adapter.preview(c,d);check();
                        await adapter.submit(c,d,check);counts.confirmed++;
                      }
                    }catch(error){
                      if(error.code!=='SF_GRADING_ITEM')throw error;
                      check();await adapter.issue?.(c,error);counts.pending++;
                    }
                    emit();check();if(!await adapter.next())break;
                  }
                  check();await adapter.close();visitedGroups.add(row.key);newGroups++;
                }
                check();more=await adapter.nextPage();
              }
              // Re-query pending work from page one so shrinking pagination cannot skip rows.
            }while(newGroups>0);
          }
        });
        state='completed';
      }catch(error){state=stopRequested?'paused':error.code==='SF_GRADING_BUSY'?'waiting':'blocked';lastError=error.message||String(error);}
      finally{await adapter.finish?.(status());emit();}
      return status();
    }
    return Object.freeze({start,pause,status});
  }
  function createSupervisor(adapter){
    let mode='enabled',reason='',busy=false,timer=null,nextAt=0,generation=0,disposed=false,writes=Promise.resolve();
    const status=()=>({mode,reason,busy,nextAt});
    const emit=()=>adapter.status?.(status());
    function restoredRecord(record){
      const incidental=['Interação manual detectada. Clique em Retomar agora para continuar.','Filtros alterados. Clique em Retomar agora para continuar.'];
      if(record?.mode==='paused'&&!record.version&&incidental.includes(record.reason))return {version:2,mode:'enabled',reason:'Pausa indevida da versão anterior removida. Iniciando automaticamente…'};
      if(record?.mode==='blocked'&&(!record.version||record.version===2)&&record.reason==='Paginação do AvaliA não reconhecida.')return {version:3,mode:'enabled',reason:'Bloqueio antigo de paginação corrigido. Reiniciando automaticamente…'};
      if(record?.mode==='blocked'&&(!record.version||record.version<=3)&&(
        record.reason==='Envio sem confirmação do AvaliA. A execução foi interrompida e este envio não será repetido.'||
        /^A resposta \d+ tem envio anterior sem confirmação\. Confira o registro nativo antes de retomar\.$/.test(record.reason||'')
      ))return {version:4,mode:'enabled',reason:'Retomando as demais respostas. Envios anteriores sem confirmação permanecem registrados, sem repetição.'};
      return record;
    }
    function cancel(){if(timer!==null)adapter.clearTimer(timer);timer=null;nextAt=0;}
    async function persist(){
      const record={version:4,mode,reason};
      writes=writes.catch(()=>{}).then(()=>adapter.save(record));
      try{await writes;return true;}catch(error){cancel();mode='blocked';reason='Não foi possível salvar o modo autônomo: '+error.message;adapter.pause();emit();return false;}
    }
    function schedule(delay){
      cancel();if(disposed||mode!=='enabled')return;
      nextAt=adapter.now()+delay;timer=adapter.setTimer(()=>cycle(),delay);emit();
    }
    async function suspend(message='Pausado pelo professor.',blocked=false){
      generation++;cancel();mode=blocked?'blocked':'paused';reason=message;adapter.pause();emit();await persist();
    }
    async function cycle(){
      cancel();if(disposed||busy||mode!=='enabled')return;
      busy=true;const current=generation;reason='';emit();
      try{
        // The saved mode is checked again before every autonomous pass, including other tabs.
        const saved=restoredRecord(await adapter.load());
        if(saved&&saved.mode!=='enabled'){sync(saved);return;}
        if(current!==generation||mode!=='enabled')return;
        const result=await adapter.run(()=>{if(disposed||current!==generation||mode!=='enabled')throw Error('Execução pausada antes do início.');});
        if(current!==generation||mode!=='enabled')return;
        if(result.state==='completed'||result.state==='waiting'){
          reason=result.state==='waiting'?'Outra aba está corrigindo. Aguardando a próxima verificação.':(result.confirmed||0)+' correções confirmadas · '+(result.pending||0)+' respostas para conferência. Nova pesquisa automática em 60 segundos.';
          schedule(60000);
        }else await suspend(result.lastError||'Confira o AvaliA antes de retomar.',result.state!=='paused');
      }catch(error){if(current===generation&&mode==='enabled')await suspend(error.message||String(error),true);}
      finally{busy=false;if(!disposed&&mode==='enabled'&&timer===null)schedule(3000);emit();}
    }
    function sync(record){
      record=restoredRecord(record);
      if(!record||!['enabled','paused','blocked'].includes(record.mode))return;
      if(record.mode===mode&&String(record.reason||'')===reason)return;
      generation++;cancel();mode=record.mode;reason=String(record.reason||'');
      if(mode!=='enabled')adapter.pause();else if(!busy)schedule(3000);emit();
    }
    async function restore(record){
      disposed=false;generation++;cancel();
      record=restoredRecord(record);
      mode=['enabled','paused','blocked'].includes(record?.mode)?record.mode:'enabled';reason=String(record?.reason||'');
      // Restoring a tab must not overwrite a pause just saved by another tab.
      if(mode==='enabled')schedule(3000);else emit();
    }
    async function resume(){
      if(busy||disposed)return;
      generation++;mode='enabled';reason='';if(await persist())schedule(0);
    }
    function restart(message='Atualizando a lista de pendências…'){
      if(disposed||mode!=='enabled')return;
      generation++;cancel();reason=message;adapter.pause();
      if(!busy)schedule(3000);emit();
    }
    function dispose(){disposed=true;generation++;cancel();adapter.pause();}
    return Object.freeze({restore,resume,restart,suspend,sync,dispose,status});
  }
  return Object.freeze({DEFAULTS,validatePolicy,responseText,countLines,metadata,expectedFeedback,decide,queueTarget,paginationState,itemIssue,createRunner,createSupervisor});
});
