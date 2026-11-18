import {norm} from './core.mjs';
export const FIXED_STAGE={text:'Semestre'};
export const EXAMS=['AD','AI','PS','AS','AE'];
export function detectExam(record,fallback=''){
  if(record.exam){const value=norm(record.exam);return /^[A-Z][A-Z0-9]{0,7}$/.test(value)?value:'';}
  const tokens=norm(record.source||'').replace(/[^A-Z0-9]+/g,' ').split(' ');
  const matches=[...new Set(tokens.filter(t=>EXAMS.includes(t)))];
  return matches.length===1?matches[0]:matches.length===0&&EXAMS.includes(fallback)?fallback:'';
}
export function detectPeriod(records,control,now=new Date()){
  const normalize=value=>norm(value).replace(/^(\d{4})[\/-]([12])$/,'$1.$2');
  const supplied=[...new Set(records.map(r=>normalize(r.academicPeriod)).filter(Boolean))];
  if(supplied.length>1)throw new Error('As planilhas misturam períodos letivos. Importe um período letivo por lote.');
  const exact=text=>control.options.filter(o=>normalize(o.text)===text);
  if(supplied.length){const found=exact(supplied[0]);if(found.length!==1)throw new Error('O período letivo da planilha não está disponível de forma única no SophiA.');return {...found[0],detectedFrom:'planilha'};}
  const selected=control.options.filter(o=>o.value===control.value);
  if(selected.length===1)return {...selected[0],detectedFrom:'selecionado no SophiA'};
  const current=now.getFullYear()+'.'+(now.getMonth()<6?'1':'2'),found=exact(current);
  if(found.length!==1)throw new Error('Selecione o período letivo no SophiA. Não foi possível detectá-lo com segurança.');
  return {...found[0],detectedFrom:'semestre atual disponível no SophiA'};
}
export function classify(records,fallback=''){
  return records.map(r=>({...r,exam:detectExam(r,fallback)}));
}
export function periodGroups(records,control,now=new Date()){
  const normalize=value=>norm(value).replace(/^(\d{4})[\/-]([12])$/,'$1.$2');
  const groups=new Map();
  for(const r of records){const key=normalize(r.academicPeriod);if(!groups.has(key))groups.set(key,[]);groups.get(key).push(r);}
  const result=new Map();
  for(const group of groups.values()){
    const period=detectPeriod(group,control,now);
    if(!result.has(period.value))result.set(period.value,{period,records:[]});
    result.get(period.value).records.push(...group);
  }
  return [...result.values()];
}
