// Small, local-only XLSX exporter for the extension. Text is written as literal
// inline strings, never as executable formulas. No external library or server.
const enc=new TextEncoder();
const xml=v=>String(v??'').replace(/[\x00-\x08\x0B\x0C\x0E-\x1F]/g,'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
const col=n=>{let s='';for(n++;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
const declaration='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>';
const ns='http://schemas.openxmlformats.org/spreadsheetml/2006/main';
const rel='http://schemas.openxmlformats.org/officeDocument/2006/relationships';
const crcTable=Array.from({length:256},(_,n)=>{for(let i=0;i<8;i++)n=n&1?0xedb88320^(n>>>1):n>>>1;return n>>>0;});
const crc32=bytes=>{let crc=0xffffffff;for(const b of bytes)crc=crcTable[(crc^b)&255]^(crc>>>8);return (crc^0xffffffff)>>>0;};
function header(size,values){const a=new Uint8Array(size),v=new DataView(a.buffer);for(const [offset,value,bytes=4] of values)bytes===2?v.setUint16(offset,value,true):v.setUint32(offset,value,true);return a;}
export function zipFiles(files){
  const parts=[],central=[];let offset=0,size=0;
  for(const [path,text] of files){
    const name=enc.encode(path),bytes=typeof text==='string'?enc.encode(text):text,crc=crc32(bytes);
    if(offset+bytes.length>0xffffffff)throw new Error('Relatório excede o limite de tamanho do formato.');
    const local=header(30,[[0,0x04034b50],[4,20,2],[6,0x800,2],[10,0,2],[12,33,2],[14,crc],[18,bytes.length],[22,bytes.length],[26,name.length,2]]);
    const entry=header(46,[[0,0x02014b50],[4,20,2],[6,20,2],[8,0x800,2],[12,0,2],[14,33,2],[16,crc],[20,bytes.length],[24,bytes.length],[28,name.length,2],[42,offset]]);
    parts.push(local,name,bytes);central.push(entry,name);offset+=local.length+name.length+bytes.length;size+=entry.length+name.length;
  }
  const end=header(22,[[0,0x06054b50],[8,files.length,2],[10,files.length,2],[12,size],[16,offset]]);
  return new Blob([...parts,...central,end],{type:'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'});
}
function sheetXml(s){
  const count=s.headers.length,end=col(count-1),rows=[
    '<row r="1" ht="27" customHeight="1"><c r="A1" s="2" t="inlineStr"><is><t>'+xml(s.title)+'</t></is></c></row>',
    '<row r="2" ht="48" customHeight="1"><c r="A2" s="3" t="inlineStr"><is><t>'+xml(s.note)+'</t></is></c></row>'
  ];
  const values=[s.headers,...(s.rows.length?s.rows:[['Nenhuma ocorrência registrada. Consulte a cobertura acima.']])];
  for(let r=0;r<values.length;r++){
    const cells=values[r].map((v,i)=>{
      if(v===null||v===undefined||v==='')return '';
      if(String(v).length>32767)throw new Error('Um detalhe do relatório ultrapassa o limite de uma célula do Excel.');
      const ref=col(i)+(r+4),style=r===0?1:0;
      return typeof v==='number'&&Number.isFinite(v)?'<c r="'+ref+'" s="'+style+'"><v>'+v+'</v></c>':'<c r="'+ref+'" s="'+style+'" t="inlineStr"><is><t xml:space="preserve">'+xml(v)+'</t></is></c>';
    }).join('');
    const max=Math.max(...values[r].map(v=>String(v??'').length),0),height=r===0?35:Math.min(409,Math.max(30,Math.ceil(max/38)*14));
    rows.push('<row r="'+(r+4)+'" ht="'+height+'" customHeight="1">'+cells+'</row>');
  }
  const widths=s.headers.map((h,i)=>'<col min="'+(i+1)+'" max="'+(i+1)+'" width="'+(/RA|Período|Página|Linha|Editáveis|Preenchidos|Encontrados|Esperados|Alunos AVA lidos/.test(h)?17:/Disciplina|Turma|Detalhe|Divergência|Resultado|Critério|Destino|Arquivo|Aluno/.test(h)?42:25)+'" customWidth="1"/>').join('');
  return declaration+'<worksheet xmlns="'+ns+'"><dimension ref="A1:'+end+(values.length+3)+'"/><sheetViews><sheetView showGridLines="0" workbookViewId="0"><pane ySplit="4" topLeftCell="A5" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews><sheetFormatPr defaultRowHeight="30"/><cols>'+widths+'</cols><sheetData>'+rows.join('')+'</sheetData><autoFilter ref="A4:'+end+(values.length+3)+'"/><mergeCells count="2"><mergeCell ref="A1:'+end+'1"/><mergeCell ref="A2:'+end+'2"/></mergeCells></worksheet>';
}
const styles=declaration+'<styleSheet xmlns="'+ns+'"><fonts count="3"><font><sz val="10"/><name val="Arial"/><color rgb="FF17345A"/></font><font><b/><sz val="10"/><name val="Arial"/><color rgb="FFFFFFFF"/></font><font><b/><sz val="14"/><name val="Arial"/><color rgb="FF17345A"/></font></fonts><fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF17345A"/><bgColor indexed="64"/></patternFill></fill></fills><borders count="1"><border/></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="4"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf><xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyAlignment="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf><xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>';
export function exportXlsx(sheets){
  if(!sheets.length||new Set(sheets.map(s=>s.name)).size!==sheets.length)throw new Error('Abas do relatório ausentes ou repetidas.');
  for(const s of sheets)if(s.name.length>31||/[\\/?*\[\]:]/.test(s.name)||s.rows.length>1048572)throw new Error('Aba do relatório excede os limites do Excel.');
  const files=[['[Content_Types].xml',declaration+'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'+sheets.map((s,i)=>'<Override PartName="/xl/worksheets/sheet'+(i+1)+'.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>').join('')+'</Types>'],
    ['_rels/.rels',declaration+'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="'+rel+'/officeDocument" Target="xl/workbook.xml"/></Relationships>'],
    ['xl/workbook.xml',declaration+'<workbook xmlns="'+ns+'" xmlns:r="'+rel+'"><sheets>'+sheets.map((s,i)=>'<sheet name="'+xml(s.name)+'" sheetId="'+(i+1)+'" r:id="rId'+(i+1)+'"/>').join('')+'</sheets></workbook>'],
    ['xl/_rels/workbook.xml.rels',declaration+'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+sheets.map((s,i)=>'<Relationship Id="rId'+(i+1)+'" Type="'+rel+'/worksheet" Target="worksheets/sheet'+(i+1)+'.xml"/>').join('')+'<Relationship Id="styles" Type="'+rel+'/styles" Target="styles.xml"/></Relationships>'],['xl/styles.xml',styles]];
  sheets.forEach((s,i)=>files.push(['xl/worksheets/sheet'+(i+1)+'.xml',sheetXml(s)]));
  return zipFiles(files);
}
