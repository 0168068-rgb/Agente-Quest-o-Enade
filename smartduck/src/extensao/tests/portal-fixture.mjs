// Fictional portal. No network calls or real students.
import {webcrypto} from 'node:crypto';
const {JSDOM}=await import(process.env.SMARTDUCK_JSDOM||'jsdom');
export {JSDOM};
export const sleep=ms=>new Promise(r=>setTimeout(r,ms));
export class FakePortal {
  constructor(){
    this.units=[{value:'u1',text:'Nova Iguaçu'},{value:'u2',text:'Itaperuna'}];
    this.classes={u1:[{value:'a',text:'Administração 1º período'},{value:'b',text:'Psicologia 1º período'},{value:'wrong',text:'Administração 2º período'}],u2:[{value:'c',text:'Administração 1º período'}]};
    this.subjects=[{value:'d1',text:'Gestão de Projetos'},{value:'d2',text:'Estatística'}];
    this.bank={
      'a/d1':[[{ra:'990000001',name:'Pessoa Um',value:''},{ra:'990000002',name:'Pessoa Dois',value:''}],[{ra:'990000003',name:'Pessoa Três',value:''}]],
      'a/d2':[[{ra:'990000001',name:'Pessoa Um',value:''}]],
      'b/d1':[[{ra:'990000004',name:'Pessoa Quatro',value:''}]],
      'b/d2':[[{ra:'990000004',name:'Pessoa Quatro',value:''}]],
      'wrong/d1':[[{ra:'990000001',name:'Pessoa Um',value:''}]],
      'wrong/d2':[[{ra:'990000001',name:'Pessoa Um',value:''}]],
      'c/d1':[[{ra:'990000005',name:'Pessoa Cinco',value:''},{ra:'990000006',name:'Pessoa Seis',value:'55'}]],
      'c/d2':[[{ra:'990000005',name:'Pessoa Cinco',value:''}]]
    };
    this.stageLabel='Semestre';this.exams=['ad','ai','ps'];
    this.values={periodo:'p26',unidade:'u1',turma:'a',etapa:'e-a',disciplina:'d1'};this.page=1;this.searched=false;this.saveCount=0;this.reloadCount=0;this.rejectSave=false;this.log=[];this.documentVersion=0;this.saveDelay=0;this.requestActive=false;this.scriptCalls=[];this.makeDocument();
  }
  makeDocument(){
    this.dom?.window.close();this.documentVersion++;this.dom=new JSDOM('<!doctype html><html><body><form><div id="controls"></div><button type="button" id="buscar">Buscar</button><button type="button" id="novo">Novo filtro</button><button type="button" id="salvar">Gravar</button><div id="grid"></div></form></body></html>',{url:'https://portal.sophia.com.br/SophiA_112/LancNotas.aspx',runScripts:'dangerously'});
    const w=this.dom.window;Object.defineProperty(w.document,'readyState',{value:'complete'});Object.defineProperty(w.crypto,'randomUUID',{value:()=>webcrypto.randomUUID()});
    w.Element.prototype.getClientRects=function(){return this.hidden||this.closest('[hidden]')?[]:[{width:40,height:20}];};
    const begins=new Set(),ends=new Set();
    this.manager={add_beginRequest:fn=>begins.add(fn),remove_beginRequest:fn=>begins.delete(fn),add_endRequest:fn=>ends.add(fn),remove_endRequest:fn=>ends.delete(fn),get_isInAsyncPostBack:()=>this.requestActive};
    this.beginRequest=()=>{this.requestActive=true;for(const fn of begins)fn();};
    this.endRequest=()=>{this.requestActive=false;for(const fn of [...ends])fn(null,{get_error:()=>null});};
    w.Sys={WebForms:{PageRequestManager:{getInstance:()=>this.manager}}};
    this.render();
  }
  render(){
    const w=this.dom.window,d=w.document,v=this.values;
    const classes=this.classes[v.unidade]||[];
    if(!classes.some(c=>c.value===v.turma))v.turma=classes[0]?.value||'';
    v.etapa=v.turma?'e-'+v.turma:'';
    const subjects=v.turma?(this.subjectsByClass?.[v.turma]??this.subjects):[];
    if(!subjects.some(s=>s.value===v.disciplina))v.disciplina=subjects[0]?.value||'';
    const choices={periodo:[{value:'p25',text:'2025.2'},{value:'p26',text:'2026.2'}],unidade:this.units,turma:classes,etapa:v.turma?[{value:v.etapa,text:this.stageByClass?.[v.turma]||this.stageLabel}]:[],disciplina:subjects};
    d.querySelector('#controls').replaceChildren(...Object.entries(choices).map(([kind,opts])=>{
      const e=d.createElement('select');e.id=kind;e.disabled=this.searched;for(const o of opts)e.add(new w.Option(o.text,o.value));e.value=v[kind];e.onchange=()=>{v[kind]=e.value;this.render();};return e;
    }));
    d.querySelector('#buscar').hidden=this.searched;d.querySelector('#novo').hidden=!this.searched;d.querySelector('#salvar').hidden=!this.searched;
    d.querySelector('#buscar').onclick=()=>{this.searched=true;this.page=1;this.log.push(['buscar',v.periodo,v.turma,v.disciplina]);this.render();};
    d.querySelector('#novo').onclick=()=>{this.searched=false;this.render();};
    d.querySelector('#salvar').onclick=()=>{
      this.saveCount++;this.log.push(['salvar',v.periodo,v.turma,v.disciplina,this.page]);
      this.beginRequest();
      const complete=()=>{if(!this.rejectSave){
        const rows=this.bank[v.turma+'/'+v.disciplina][this.page-1];
        rows.forEach((r,i)=>{for(const exam of this.exams){
          const input=d.querySelector('#'+exam+i);if(!input||input.disabled||input.readOnly)continue;
          if(exam==='ad')r.value=input.value;
          else{r.values??={};r.values[exam]=input.value;}
        }});
        this.render();
      }this.endRequest();};
      if(this.saveDelay)w.setTimeout(complete,this.saveDelay);else complete();
    };
    const grid=d.querySelector('#grid');grid.replaceChildren();
    if(this.searched){
      const pages=this.bank[v.turma+'/'+v.disciplina],table=d.createElement('table');
      table.innerHTML='<tr><th>RA</th><th>Nome</th>'+this.exams.map(e=>'<th>'+e.toUpperCase()+'</th>').join('')+'</tr>';
      for(const [i,r] of pages[this.page-1].entries()){
        const tr=d.createElement('tr');for(const text of [r.ra,r.name])tr.append(Object.assign(d.createElement('td'),{textContent:text}));
        for(const exam of this.exams){
          const td=d.createElement('td'),value=exam==='ad'?r.value:r.values?.[exam]||'';
          if(r.textExams?.includes(exam))td.textContent=value;
          else{const input=Object.assign(d.createElement('input'),{id:exam+i,type:'text',value,disabled:!!r.locked,readOnly:!!r.readOnly,...r.fields?.[exam]});input.defaultValue=input.value;td.append(input);}
          tr.append(td);
        }table.append(tr);
      }
      const foot=d.createElement('tr'),td=Object.assign(d.createElement('td'),{colSpan:2+this.exams.length,textContent:'Página '+this.page+' de '+pages.length+' '});
      for(let i=1;i<=pages.length;i++)if(i!==this.page){const a=Object.assign(d.createElement('a'),{href:"javascript:__doPostBack('grid','Page$"+i+"')",textContent:String(i)});a.onclick=e=>{e.preventDefault();this.page=i;this.render();};td.append(a);}
      foot.append(td);table.append(foot);grid.append(table);
    }
  }
  async execute(func,command){const value=await this.dom.window.eval('('+func.toString()+')')(command);return JSON.parse(JSON.stringify(value));}
  reload(){if(this.requestActive)throw new Error('Reload interrupted an active Save request');this.reloadCount++;this.searched=false;this.page=1;this.makeDocument();}
  close(){this.dom.window.close();}
}
export function installChrome(portal){
  globalThis.chrome={
    scripting:{executeScript:async({func,args,world})=>{portal.scriptCalls.push({action:args[0].action,world});const documentId='fixture-doc-'+portal.documentVersion;return [{frameId:0,documentId,result:await portal.execute(func,args[0])}];}},
    tabs:{get:async id=>({id,url:portal.dom.window.location.href,status:portal.tabLoading?'loading':'complete'}),reload:async()=>portal.reload(),update:async()=>({windowId:1}),query:async()=>[{id:7,url:'https://portal.sophia.com.br/SophiA_112/LancNotas.aspx',title:'Notas'}],create:async()=>{throw new Error('Não deve criar abas');}},
    windows:{update:async()=>{throw new Error('Não deve abrir ou focar janelas');}},
    storage:{session:{values:{},async set(v){Object.assign(this.values,v);},async get(k){return {[k]:this.values[k]};},async remove(k){delete this.values[k];}}},
    runtime:{id:'smartduck-test',getURL:p=>'chrome-extension://smartduck-test/'+p,onMessage:{addListener(){},removeListener(){}},sendMessage:async()=>undefined}
  };
}
export function records(){
  const base={campus:'Nova Iguaçu',course:'Administração',period:'1',discipline:'Gestão de Projetos',code:'36',absent:'false',source:'AD Exemplo.xlsx / Notas',fileId:'fictional'};
  return [
    {ra:'990000001',name:'Pessoa Um',grade:'8'},
    {ra:'990000002',name:'Pessoa Dois',grade:'F',absent:'true'},
    {ra:'990000003',name:'Pessoa Três',grade:'9'},
    {ra:'990000001',name:'Pessoa Um',grade:'7',discipline:'Estatística',code:'37'},
    {ra:'990000004',name:'Pessoa Quatro',grade:'6',course:'Psicologia'},
    {ra:'990000005',name:'Pessoa Cinco',grade:'10',campus:'Itaperuna'},
    {ra:'990000006',name:'Pessoa Seis',grade:'F',absent:'true',campus:'Itaperuna'}
  ].map((r,i)=>({...base,...r,line:i+2,recordId:'record-'+i,disciplineKey:(r.code||base.code)+' | '+(r.discipline||base.discipline)}));
}
