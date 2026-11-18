// Read-only AVA audit. Reuses an authenticated tab; never opens tabs or sends
// messages, changes enrolments, reads credentials, or calls private APIs.
export function avaCommand(command={action:'state'}){
  const norm=v=>String(v??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toUpperCase().replace(/\s+/g,' ').trim();
  const visible=e=>!!e?.isConnected&&e.getClientRects().length>0&&getComputedStyle(e).display!=='none'&&getComputedStyle(e).visibility!=='hidden';
  const text=e=>(e?.innerText??e?.textContent??'').replace(/\s+/g,' ').trim();
  const fail=message=>({ok:false,message});
  if(location.origin!=='https://avauni.grupoa.education')return fail('A aba não corresponde ao AVA configurado.');
  if(Array.from(document.querySelectorAll('input[type="password"]')).some(visible))return fail('Entre no AVA para verificar o vínculo de professor.');
  const profiles=Array.from(document.querySelectorAll('button[aria-haspopup] img[alt]')).filter(visible).filter(e=>!e.closest('[role="dialog"]')).map(e=>e.alt.trim()).filter(Boolean);
  const names=[...new Set(profiles)];
  if(names.length!==1)return fail('Não foi possível identificar unicamente o professor conectado no AVA.');
  const account=names[0];
  if(command.account&&norm(command.account)!==norm(account))return fail('A conta do AVA mudou durante a verificação.');
  if(command.action==='enter'){
    if(location.pathname==='/plataforma/my/courses')return {ok:true,account,unchanged:true};
    const links=Array.from(document.querySelectorAll('a[href]')).filter(visible).filter(e=>{try{const u=new URL(e.href);return u.origin===location.origin&&u.pathname==='/plataforma/my/courses';}catch{return false;}});
    const urls=[...new Set(links.map(e=>e.href))];
    if(urls.length!==1)return fail('Abra Disciplinas no AVA para conferir o vínculo docente.');
    setTimeout(()=>location.assign(urls[0]),0);return {ok:true,account,issued:true};
  }
  if(location.pathname!=='/plataforma/my/courses')return fail('A lista de disciplinas do AVA não está aberta.');
  const buttons=Array.from(document.querySelectorAll('button')).filter(visible);
  const labelled=(label,root=document)=>Array.from(root.querySelectorAll('button')).filter(visible).filter(e=>norm(e.getAttribute('aria-label')||text(e))===norm(label));
  const dialog=Array.from(document.querySelectorAll('[role="dialog"]')).filter(visible).find(e=>e.querySelector('[data-testid="participantsSearchInput"]'));
  const table=Array.from(document.querySelectorAll('table')).filter(visible).find(t=>t.querySelector('a[href*="/plataforma/course/"]'));
  const courses=table?Array.from(table.rows).filter(r=>r.querySelector('a[href*="/plataforma/course/"]')).map(r=>{
    const cells=Array.from(r.cells),link=r.querySelector('a[href*="/plataforma/course/"]'),p=r.querySelector('[data-testid="list-courses-table-open-participants-btn"]');
    return {id:new URL(link.href).pathname.split('/').pop(),url:link.href,code:text(cells[1]),name:text(link),participants:Number(text(p).replace(/\D/g,'')),element:r};
  }):[];
  const next=labelled('Next page').filter(e=>!e.closest('[role="dialog"]'));
  const current=buttons.find(e=>/^Current Page, Page \d+$/i.test(e.getAttribute('aria-label')||''));
  const totals=[...new Set(Array.from(document.querySelectorAll('span,div')).filter(e=>visible(e)&&!e.closest('[role="dialog"]')).map(e=>text(e).match(/^de\s+([\d.]+)\s+registros$/i)?.[1]).filter(Boolean).map(s=>Number(s.replace(/\./g,''))))];
  const nameSearch=document.querySelector('input[aria-label="Filtrar por nome"]');
  const extraFilters=Array.from(new URL(location.href).searchParams).filter(([k,v])=>v&&/category|format|period|start|end|search/i.test(k));
  const filterDefaults=[['[aria-label="filtrar por categorias"]','Selecione a categoria'],['[aria-label="Filtrar por formato"]','Selecione o formato'],['[data-testid="filter-academic-sync-type"] .vue-treeselect','Todos']];
  const dropdownFilters=filterDefaults.some(([selector,placeholder])=>{const e=document.querySelector(selector);if(!e||!visible(e))return false;const value=norm(text(e));return placeholder==='Todos'?!/^(?:TODOS)+$/.test(value.replace(/\s/g,'')):value!==norm(placeholder);});
  const dateFilters=Array.from(document.querySelectorAll('input[aria-label="Filtrar por data inicial"],input[aria-label="Filtrar por data final"]')).some(e=>e.value);
  const allButton=labelled('Filtrar por status todos')[0];
  const allSelected=!!allButton&&(allButton.classList.contains('course-status__button--active')||allButton.getAttribute('aria-pressed')==='true'||allButton.getAttribute('aria-selected')==='true');
  const busy=Array.from(document.querySelectorAll('[aria-busy="true"],[role="progressbar"]')).some(e=>visible(e)&&!e.closest('tr'));
  const publicCourses=courses.map(({element,...c})=>c);
  const roleRows=dialog?Array.from(dialog.querySelectorAll('tr')).filter(r=>Array.from(r.querySelectorAll('img[alt]')).some(i=>norm(i.alt)===norm(account))).map(r=>({name:account,role:text(r.cells[3])})):[];
  const search=dialog?.querySelector('[data-testid="participantsSearchInput"] input');
  const total=dialog?text(dialog).match(/Total de participantes ativos\s*([\d.]+)/i):null;
  const members=[];
  if(dialog)for(const table of dialog.querySelectorAll('table')){
    const header=Array.from(table.querySelectorAll('th')).map(e=>norm(text(e)));
    const raIndex=header.findIndex(x=>/^(RA|MATRICULA|CODIGO DO ALUNO)$/.test(x));
    const nameIndex=header.findIndex(x=>/^(NOME|ALUNO|PARTICIPANTE|USUARIO|NOME COMPLETO)$/.test(x));
    const roleIndex=header.findIndex(x=>/^(PAPEL|FUNCAO|PERFIL|VINCULO|TIPO DE USUARIO)$/.test(x));
    for(const row of table.rows){
      if(!visible(row)||!row.querySelector('td'))continue;
      const name=row.querySelector('img[alt]')?.alt?.trim()||text(row.cells[nameIndex]);
      const role=text(row.cells[roleIndex>=0?roleIndex:3]);
      if(!name||!role)continue;
      const ra=raIndex>=0?text(row.cells[raIndex]).replace(/\.0+$/,''):text(row).match(/\b(?:RA|Matr[ií]cula)\s*[:#]\s*(\d{5,20})\b/i)?.[1]||'';
      const profile=row.querySelector('a[href*="/profile/"],a[href*="/user/"]')?.getAttribute('href')||'';
      members.push({name,ra:/^\d{5,20}$/.test(ra)?ra:'',role,key:profile||JSON.stringify([ra,norm(name),norm(role)])});
    }
  }
  const memberNext=dialog?Array.from(dialog.querySelectorAll('button')).filter(visible).filter(e=>/^(Next page|Pr[oó]xima p[aá]gina)$/i.test(e.getAttribute('aria-label')||text(e))):[];
  const memberPage=dialog?Array.from(dialog.querySelectorAll('button')).find(e=>/^Current Page, Page \d+$/i.test(e.getAttribute('aria-label')||''))?.getAttribute('aria-label')||'':'';
  const membersSignature=JSON.stringify([members,memberPage,total?.[1],search?.value]);
  const filtersClear=!nameSearch?.value&&!extraFilters.length&&!dropdownFilters&&!dateFilters;
  const state={ok:true,account,courses:publicCourses,page:current?.getAttribute('aria-label')||'',next:next.length===1&&!next[0].disabled,total:totals.length===1?totals[0]:null,filtersClear,allSelected,busy,
    dialog:!!dialog,participantTotal:total?Number(total[1].replace(/\./g,'')):null,roleRows,search:search?.value||'',members,membersSignature,memberNext:memberNext.length===1&&!memberNext[0].disabled,
    signature:JSON.stringify([location.href,publicCourses,current?.getAttribute('aria-label'),!!dialog,membersSignature,roleRows,totals,filtersClear,allSelected,busy])};
  if(command.action==='state')return state;
  if(command.signature&&command.signature!==state.signature)return fail('A tela do AVA mudou durante a conferência.');
  let targets=[];
  if(command.action==='list')targets=labelled('Alterar para modo de visualização: lista');
  if(command.action==='all')targets=labelled('Filtrar por status todos');
  if(command.action==='next')targets=next.filter(e=>!e.disabled);
  if(command.action==='memberNext')targets=memberNext.filter(e=>!e.disabled);
  if(command.action==='close')targets=dialog?labelled('Fechar',dialog):[];
  if(command.action==='participants'){
    if(dialog)return fail('Há uma consulta de participantes ainda aberta.');
    targets=courses.filter(c=>c.id===command.id).map(c=>c.element.querySelector('[data-testid="list-courses-table-open-participants-btn"]')).filter(Boolean);
  }
  if(command.action==='search'||command.action==='clearSearch'){
    if(!search)return fail('Busca de participantes não reconhecida.');
    const setter=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;
    setter.call(search,command.action==='search'?account:'');search.dispatchEvent(new Event('input',{bubbles:true}));return {ok:true,issued:true};
  }
  if(command.action==='clearName'){
    if(!nameSearch)return {ok:true,unchanged:true};
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(nameSearch,'');nameSearch.dispatchEvent(new Event('input',{bubbles:true}));return {ok:true,issued:true};
  }
  if(targets.length!==1)return fail('Comando do AVA não identificado de forma única: '+command.action+'.');
  targets[0].scrollIntoView({block:'center',inline:'center'});targets[0].click();return {ok:true,issued:true};
}

export function avaPeriod(course){
  const code=String(course.code||'');
  const found=code.match(/(?:^|_)(20\d{2})[._\/-]?([12])(?:_|$)/)||code.match(/(?:^|_)(?:[A-Z]+)?(20\d{2})([12])\d{1,2}P(?:_|$)/i);
  return found?found[1]+'.'+found[2]:'';
}
export function avaScope(course){
  const code=(course.code||'').toUpperCase(),name=course.name||'';
  const modality=/_S_/.test(code)?'S':/_G_/.test(code)?'G':/PRES/.test(code)?'P':'';
  const entries=code.match(/_([1-4])-([1-4])E(?:_|$)/);
  const campus=name.match(/Graduação Semipresencial\s*[-–]\s*([^()]+)/i)?.[1]?.trim()||'';
  return {...course,period:avaPeriod(course),modality,campus,offerings:entries?[entries[1],entries[2]]:[],discipline:name.replace(/\s*\([^()]*\)\s*$/,'').replace(/\s*\|\s*Online\s*$/i,'').trim(),disciplineCode:code.split('_')[0]};
}

export class AvaClient{
  constructor(tabId,{pause=ms=>new Promise(r=>setTimeout(r,ms)),polls=80}={}){this.tabId=tabId;this.pause=pause;this.polls=polls;this.account='';}
  async call(command){
    let timer;let result;
    try{result=await Promise.race([chrome.scripting.executeScript({target:{tabId:this.tabId,frameIds:[0]},func:avaCommand,args:[{...command,account:this.account}]}),new Promise((_,reject)=>{timer=setTimeout(()=>reject(new Error('O AVA não respondeu no prazo; verificação incompleta.')),15000);})]);}
    finally{clearTimeout(timer);}
    if(result.length!==1||!result[0]?.result?.ok)throw new Error(result[0]?.result?.message||'O AVA não respondeu.');
    const s=result[0].result;if(s.account)this.account=s.account;return s;
  }
  async stable(predicate=()=>true){
    let previous='',same=0;
    for(let n=0;n<this.polls;n++){
      await this.pause(250);const s=await this.call({action:'state'});
      same=s.signature===previous?same+1:0;previous=s.signature;
      if(same>=5&&!s.busy&&predicate(s))return s;
    }
    throw new Error('A consulta do AVA não terminou de carregar; verificação incompleta.');
  }
  async action(action,extra={},predicate=()=>true){const s=await this.call({action:'state'});await this.call({action,signature:s.signature,...extra});return this.stable(predicate);}
  async roster(initial,check){
    let s=initial;if(s.search)s=await this.action('clearSearch',{},x=>x.dialog&&!x.search);
    const pages=new Set(),people=[],warnings=[];
    try{while(true){
      check();if(!s.dialog||s.search)throw new Error('A lista de participantes foi fechada ou filtrada durante a leitura.');
      const signature=JSON.stringify(s.members);if(pages.has(signature))throw new Error('A paginação de participantes repetiu os mesmos registros.');pages.add(signature);
      people.push(...s.members);if(!s.memberNext)break;
      if(pages.size>=1000)throw new Error('Limite de páginas de participantes atingido.');
      s=await this.action('memberNext',{},x=>x.dialog&&JSON.stringify(x.members)!==signature);
    }}catch(e){if(e.code==='CANCELLED')throw e;warnings.push(e.message);}
    const unique=new Set(people.map(p=>p.key));
    if(unique.size!==people.length)warnings.push('Participantes com identificação repetida; conferir a lista do AVA.');
    if(s.participantTotal===null||people.length!==s.participantTotal)warnings.push('Nem todos os participantes do AVA foram confirmados ('+people.length+' de '+(s.participantTotal??'?')+').');
    const student=p=>/^(ALUN[OA]|ESTUDANTE|STUDENT)(?: VIGENTE)?$/i.test(p.role);
    const known=p=>student(p)||/^(PROFESSOR(?:A)?(?: VIGENTE)?|DOCENTE|INSTRUTOR(?:A)?|TUTOR(?:A)?|ADMINISTRADOR(?:A)?|COORDENADOR(?:A)?|GESTOR(?:A)?)$/i.test(p.role);
    if(people.some(p=>!known(p)))warnings.push('Há funções de participantes não reconhecidas; a lista de alunos pode estar incompleta.');
    return {students:people.filter(student),rosterComplete:!warnings.length,rosterWarnings:warnings,participantCount:people.length};
  }
  async collect(periods,{onProgress=()=>{},cancelled=()=>false}={}){
    const report={status:'partial',complete:false,account:'',courses:[],warnings:[],pages:0,periods};
    const check=()=>{if(cancelled())throw Object.assign(new Error('Verificação do AVA pausada.'),{code:'CANCELLED'});};
    try{
      await this.call({action:'enter'});await this.stable();report.account=this.account;
      let s=await this.call({action:'state'});
      if(s.dialog)await this.action('close',{},x=>!x.dialog);
      await this.action('list');await this.action('clearName');s=await this.action('all',{},x=>x.allSelected);
      const pages=new Set(),seenCourses=new Set(),allCourses=new Set();
      const filtersClear=s.filtersClear,total=s.total;
      while(true){
        check();const identity=JSON.stringify(s.courses.map(c=>c.id));
        if(pages.has(identity))throw new Error('O AVA repetiu uma página; não é possível afirmar que todas as disciplinas foram verificadas.');
        pages.add(identity);report.pages++;
        for(const c of s.courses)allCourses.add(c.id);
        if(!s.courses.length){if(s.total===0&&s.allSelected)break;throw new Error('Lista vazia ou formato do AVA não reconhecido.');}
        for(const raw of s.courses){
          const c=avaScope(raw);if(seenCourses.has(c.id))continue;seenCourses.add(c.id);
          if(!c.period){report.courses.push({...c,verified:false,teacher:false,error:'Período letivo não identificado no código da disciplina.'});report.warnings.push(c.name+': período não identificado; vínculo vigente não confirmado.');continue;}
          if(!periods.includes(c.period))continue;check();
          onProgress('Verificando vínculo de professor no AVA: '+c.name);
          let result={...c,role:'',verified:false};
          try{
            let p=await this.action('participants',{id:c.id},x=>x.dialog&&x.participantTotal===c.participants);
            if(!p.roleRows.length)p=await this.action('search',{},x=>x.search===this.account&&x.roleRows.length>0);
            if(p.roleRows.length!==1)throw new Error('O vínculo da conta conectada não é único nos participantes.');
            result.role=p.roleRows[0].role;result.verified=true;
            result.teacher=/^(PROFESSOR(?:A)?(?: VIGENTE)?|DOCENTE|INSTRUTOR(?:A)?)$/i.test(result.role.normalize('NFD').replace(/[\u0300-\u036f]/g,''));
            if(result.teacher){
              onProgress('Lendo alunos no AVA: '+c.name);
              try{Object.assign(result,await this.roster(p,check));for(const w of result.rosterWarnings)report.warnings.push(c.name+': '+w);}
              catch(e){if(e.code==='CANCELLED')throw e;result.rosterComplete=false;result.rosterWarnings=[e.message];report.warnings.push(c.name+': '+e.message);}
            }
          }catch(e){result.error=e.message;report.warnings.push(c.name+': '+e.message);}
          report.courses.push(result);
          const after=await this.call({action:'state'});if(after.dialog)await this.action('close',{},x=>!x.dialog);
        }
        check();s=await this.call({action:'state'});
        if(!s.allSelected||s.total!==total||s.filtersClear!==filtersClear)throw new Error('Os filtros ou o total de disciplinas mudaram durante a consulta do AVA.');
        if(!s.next)break;
        const prior=JSON.stringify(s.courses.map(c=>c.id));s=await this.action('next',{},x=>JSON.stringify(x.courses.map(c=>c.id))!==prior);
      }
      if(!filtersClear)report.warnings.push('Há filtros adicionais no AVA; o conjunto completo de disciplinas não foi confirmado.');
      if(total===null||allCourses.size!==total)report.warnings.push('A quantidade total de disciplinas do AVA não foi confirmada em todas as páginas.');
      report.complete=filtersClear&&total!==null&&allCourses.size===total&&report.courses.every(c=>c.verified);report.status=report.complete?'verified':'partial';
      report.rostersComplete=report.complete&&report.courses.filter(c=>c.teacher).every(c=>c.rosterComplete);
    }catch(e){if(e.code==='CANCELLED')throw e;report.warnings.push(e.message);}
    report.checkedAt=new Date().toISOString();return report;
  }
}

export async function collectAva(periods,options={}){
  const tabs=(await chrome.tabs.query({url:'https://avauni.grupoa.education/*'})).filter(t=>/^https:\/\/avauni\.grupoa\.education\//.test(t.url||''));
  if(tabs.length!==1)return {status:'unavailable',complete:false,courses:[],warnings:[tabs.length?'Há mais de uma aba do AVA. Deixe uma única aba da conta que será conferida.':'AVA não aberto: o vínculo docente não foi verificado. Entre no AVA em uma aba existente e realize novamente.']};
  return new AvaClient(tabs[0].id).collect(periods,options);
}
