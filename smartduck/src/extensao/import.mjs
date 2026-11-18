const LIMIT = 160 * 1024 * 1024;
const decoder = new TextDecoder('utf-8', {fatal:true});
const nsElements = (node, name) => Array.from(node.getElementsByTagNameNS('*', name));
const child = (node, name) => Array.from(node.children || []).find(n => n.localName === name);
const textOf = (node, name) => child(node, name)?.textContent ?? '';
function xml(text) {
  if (/<!DOCTYPE|<!ENTITY/i.test(text)) throw new Error('XML com declaração externa não suportada.');
  const doc = new DOMParser().parseFromString(text, 'application/xml');
  if (nsElements(doc,'parsererror').length) throw new Error('Arquivo XLSX com XML inválido.');
  return doc;
}
function crc32(bytes) {
  let c = 0xffffffff;
  for (const b of bytes) {
    c ^= b;
    for (let i=0;i<8;i++) c = (c >>> 1) ^ ((c & 1) ? 0xedb88320 : 0);
  }
  return (c ^ 0xffffffff) >>> 0;
}
export async function unzip(buffer) {
  const bytes = new Uint8Array(buffer), v = new DataView(buffer);
  if (bytes.length < 22) throw new Error('Arquivo XLSX incompleto.');
  let end = bytes.length - 22;
  for (; end >= Math.max(0, bytes.length - 65557); end--) {
    if (v.getUint32(end,true) === 0x06054b50 && end+22+v.getUint16(end+20,true) === bytes.length) break;
  }
  if (end < Math.max(0, bytes.length-65557)) throw new Error('O arquivo não é um XLSX/ZIP válido.');
  if (v.getUint16(end+4,true) || v.getUint16(end+6,true)) throw new Error('Arquivo dividido não suportado.');
  const count = v.getUint16(end+10,true);
  let offset = v.getUint32(end+16,true), total = 0;
  if (!count || count > 4096 || offset >= end) throw new Error('Estrutura XLSX não suportada.');
  const entries = new Map();
  for (let i=0;i<count;i++) {
    if (offset+46>end || v.getUint32(offset,true)!==0x02014b50) throw new Error('Diretório ZIP inválido.');
    const flags=v.getUint16(offset+8,true), method=v.getUint16(offset+10,true), crc=v.getUint32(offset+16,true);
    const packed=v.getUint32(offset+20,true), size=v.getUint32(offset+24,true);
    const nameLen=v.getUint16(offset+28,true), extra=v.getUint16(offset+30,true), comment=v.getUint16(offset+32,true);
    const local=v.getUint32(offset+42,true);
    const name=decoder.decode(bytes.subarray(offset+46,offset+46+nameLen));
    if (flags&1 || ![0,8].includes(method)) throw new Error('XLSX criptografado ou compressão não suportada.');
    total+=size;
    if(total>LIMIT || size>LIMIT || packed>bytes.length || local+30>end) throw new Error('XLSX excede o limite de leitura.');
    if (name.includes('..') || name.startsWith('/') || entries.has(name)) throw new Error('Caminho ZIP inválido ou duplicado.');
    if (v.getUint32(local,true)!==0x04034b50) throw new Error('Entrada ZIP inválida.');
    const start=local+30+v.getUint16(local+26,true)+v.getUint16(local+28,true);
    if (start+packed>end) throw new Error('Entrada ZIP truncada.');
    entries.set(name,{method,crc,size,start,packed});
    offset+=46+nameLen+extra+comment;
  }
  return async name => {
    const e=entries.get(name);
    if(!e) return null;
    let out;
    if(e.method===0) out=bytes.slice(e.start,e.start+e.packed);
    else {
      let stream;
      try { stream=new Blob([bytes.subarray(e.start,e.start+e.packed)]).stream().pipeThrough(new DecompressionStream('deflate-raw')); }
      catch {throw new Error('Atualize o Chrome para ler arquivos XLSX.');}
      const reader=stream.getReader(), chunks=[]; let length=0;
      while(true) {
        const {value,done}=await reader.read(); if(done) break;
        length+=value.length;
        if(length>e.size || length>LIMIT) {await reader.cancel(); throw new Error('Descompactação excedeu o tamanho declarado.');}
        chunks.push(value);
      }
      out=new Uint8Array(length); let pos=0;
      for(const c of chunks) {out.set(c,pos);pos+=c.length;}
    }
    if(out.length!==e.size || crc32(out)!==e.crc) throw new Error('XLSX corrompido: verificação de integridade falhou.');
    return decoder.decode(out);
  };
}
function richText(node) {
  return nsElements(node,'t').filter(t=>!t.closest('rPh')).map(t=>t.textContent).join('');
}
export async function readXlsx(buffer) {
  const read=await unzip(buffer);
  const wb=await read('xl/workbook.xml'), rels=await read('xl/_rels/workbook.xml.rels');
  if(!wb || !rels) throw new Error('Estrutura de planilha XLSX não encontrada.');
  const shared=await read('xl/sharedStrings.xml');
  const strings=shared ? nsElements(xml(shared),'si').map(richText) : [];
  const relation=new Map(nsElements(xml(rels),'Relationship').map(r=>[r.getAttribute('Id'),r]));
  const stylesText=await read('xl/styles.xml'); let formats=[];
  if(stylesText) {
    const styles=xml(stylesText);
    const fmt=new Map(nsElements(styles,'numFmt').map(n=>[n.getAttribute('numFmtId'),n.getAttribute('formatCode')]));
    const xfs=nsElements(styles,'cellXfs')[0];
    formats=Array.from(xfs?.children||[]).map(n=>fmt.get(n.getAttribute('numFmtId'))||'');
  }
  const sheets=[];
  for(const sheet of nsElements(xml(wb),'sheet')) {
    const id=sheet.getAttribute('r:id') || sheet.getAttributeNS('http://schemas.openxmlformats.org/officeDocument/2006/relationships','id');
    const rel=relation.get(id);
    if(!rel || rel.getAttribute('TargetMode')==='External') throw new Error('Referência de aba inválida.');
    let target=rel.getAttribute('Target')||'';
    target=target.startsWith('/') ? target.slice(1) : 'xl/'+target;
    target=target.replace(/\/\.\//g,'/');
    if(target.includes('..')) throw new Error('Caminho de aba não suportado.');
    const sheetText=await read(target);
    if(!sheetText) throw new Error('Aba ausente no arquivo.');
    const rows=[];
    for(const row of nsElements(xml(sheetText),'row')) {
      const rowNum=Number(row.getAttribute('r')) || rows.length+1;
      if(rowNum>150000) throw new Error('Aba excede 150 mil linhas.');
      const values=[];
      for(const c of Array.from(row.children).filter(n=>n.localName==='c')) {
        const ref=c.getAttribute('r')||''; const letters=ref.match(/^[A-Z]+/)?.[0];
        let col=letters ? Array.from(letters).reduce((v,l)=>v*26+l.charCodeAt(0)-64,0)-1 : values.length;
        if(col>255) throw new Error('Aba excede 256 colunas.');
        const type=c.getAttribute('t'), raw=textOf(c,'v');
        let value=raw;
        if(child(c,'f')) value='#FORMULA: '+textOf(c,'f');
        else if(type==='s') {
          if(!/^\d+$/.test(raw) || Number(raw)>=strings.length) throw new Error('Texto compartilhado inválido.');
          value=strings[Number(raw)];
        } else if(type==='inlineStr') value=richText(c);
        else if(type==='b') value=raw==='1' ? 'true' : 'false';
        else if(type!=='str' && type!=='e') {
          const fmt=formats[Number(c.getAttribute('s'))];
          if(/^0+$/.test(fmt||'') && /^\d+$/.test(raw)) value=raw.padStart(fmt.length,'0');
        }
        values[col]=value;
      }
      rows[rowNum-1]=values;
    }
    for(let i=0;i<rows.length;i++) rows[i] ||= [];
    if(rows.some(r=>r.some(v=>v!==''))) sheets.push({name:sheet.getAttribute('name'),rows});
  }
  return sheets;
}
export function readCsv(text) {
  text=text.replace(/^\uFEFF/,'');
  const first=text.split(/\r?\n/,1)[0];
  const sep=[';', '\t', ','].sort((a,b)=>first.split(b).length-first.split(a).length)[0];
  const rows=[]; let row=[],cell='',quoted=false,closed=false;
  for(let i=0;i<text.length;i++) {
    const c=text[i];
    if(quoted) {
      if(c==='"' && text[i+1]==='"') {cell+='"';i++;}
      else if(c==='"') {quoted=false;closed=true;}
      else cell+=c;
    } else if(c==='"' && !cell && !closed) quoted=true;
    else if(c===sep) {row.push(cell);cell='';closed=false;}
    else if(c==='\n' || c==='\r') {row.push(cell);rows.push(row);row=[];cell='';closed=false;if(c==='\r'&&text[i+1]==='\n')i++;}
    else {if(closed || c==='"') throw new Error('CSV com aspas inválidas. Exporte novamente usando UTF-8.');cell+=c;}
  }
  if(quoted) throw new Error('CSV com aspas não fechadas.');
  if(cell || row.length || closed) {row.push(cell);rows.push(row);}
  const nonempty=rows.filter(r=>r.some(Boolean));
  const width=nonempty[0]?.length;
  if(nonempty.some(r=>r.length!==width)) throw new Error('CSV com colunas desalinhadas. Use XLSX ou CSV separado por ponto e vírgula.');
  return rows;
}
export async function readFile(file) {
  if(file.size>50*1024*1024) throw new Error(file.name+': limite de 50 MB por arquivo.');
  const buffer=await file.arrayBuffer();
  const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',buffer))).map(x=>x.toString(16).padStart(2,'0')).join('');
  if(/\.xlsx$/i.test(file.name)) return {hash,sheets:await readXlsx(buffer)};
  if(/\.csv$/i.test(file.name)) {
    let text;
    try {text=decoder.decode(buffer);} catch {throw new Error('CSV não está em UTF-8. Salve como CSV UTF-8 no Excel.');}
    return {hash,sheets:[{name:'CSV',rows:readCsv(text)}]};
  }
  throw new Error('Escolha um arquivo XLSX ou CSV. Para XLS antigo, salve uma cópia como XLSX.');
}
