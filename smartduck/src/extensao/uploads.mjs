import {recordsFromRows} from './core.mjs';
import {readFile} from './import.mjs';

export const MAX_FILES=4;
export const FILTERS=['source','campus','course','period','disciplineKey'];
export const ALL_LABELS={source:'Todos os arquivos',campus:'Todos os campi / polos',course:'Todos os cursos',period:'Todos os períodos',disciplineKey:'Todas as disciplinas'};
export const filterRecords=(records,filters={})=>records.filter(r=>FILTERS.every(k=>!filters[k]||r[k]===filters[k]));

export async function addFiles(incoming,current={files:[],records:[]},onProgress=()=>{}) {
  const chosen=Array.from(incoming);
  if(!chosen.length)return {...current,notices:[]};
  if(chosen.length+current.files.length>MAX_FILES)throw new Error('O limite é de 4 arquivos por lote. Você já carregou '+current.files.length+'. Remova um arquivo ou selecione menos arquivos; nada desta seleção foi importado.');
  const files=[...current.files],records=[...current.records],hashes=new Set(files.map(f=>f.hash));
  const notices=[];
  for(const file of chosen){
    onProgress('Lendo '+file.name+'…');
    try{
      const parsed=await readFile(file);
      if(hashes.has(parsed.hash)){notices.push(file.name+': arquivo idêntico ignorado.');continue;}
      const added=parsed.sheets.flatMap((sheet,index)=>recordsFromRows(sheet.rows,file.name+' / '+sheet.name).map(r=>({...r,fileId:parsed.hash,recordId:parsed.hash+':'+index+':'+r.line+':'+(r.exam||'nota')})));
      if(records.length+added.length>150000)throw new Error('Limite de 150 mil registros por lote.');
      records.push(...added);hashes.add(parsed.hash);files.push({hash:parsed.hash,name:file.name,count:added.length,sheets:parsed.sheets.length});
      notices.push(file.name+': '+added.length.toLocaleString('pt-BR')+' registros em '+parsed.sheets.length+' aba(s).');
    }catch(e){notices.push(file.name+': '+e.message);}
  }
  return {files,records,notices};
}
