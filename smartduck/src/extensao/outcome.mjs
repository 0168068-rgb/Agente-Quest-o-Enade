export function outcome(report){
  const rows=report.rows||[],saved=rows.filter(r=>r.saved).length;
  const pending=rows.filter(r=>!r.saved&&!/^(Já possui|Nota existente|Faltoso:)/.test(r.status)).length;
  if(saved)return {phase:'done',type:pending?'warning':'success',message:'Processamento concluído. '+saved+' notas gravadas e verificadas.'+(pending?' '+pending+' registro(s) com pendência no relatório.':report.warnings?.length?' Ocorrências registradas no relatório.':'')};
  const preserved=rows.filter(r=>/^(Já possui|Nota existente|Faltoso:)/.test(r.status));
  if(rows.length&&preserved.length===rows.length)return {phase:'done',type:'success',message:'Nenhuma alteração necessária. As notas já lançadas foram mantidas e os faltosos continuam em branco.'};
  const columns=(report.portalMap||[]).flatMap(p=>p.columns||[]);
  const requested=(report.catalog||[]).map(c=>c.exam),available=[...new Set(columns.filter(c=>c.editable>0).map(c=>c.exam))];
  const closed=requested.filter(exam=>columns.some(c=>c.exam===exam)&&columns.filter(c=>c.exam===exam).every(c=>c.editable===0));
  if(closed.length)return {phase:'blocked',type:'warning',message:'O arquivo foi lido, mas o SophiA não liberou campos de '+closed.join(', ')+' para edição nas turmas consultadas. '+(available.length?'As avaliações com campos editáveis são: '+available.join(', ')+'. ':'')+'Nenhuma nota foi lançada.'};
  const reasons=[...new Set(rows.filter(r=>!preserved.includes(r)).map(r=>r.status))].slice(0,2);
  return {phase:'blocked',type:'warning',message:'O arquivo foi lido, mas nenhuma nota pôde ser lançada. '+(reasons.join('. ')||'Não foram encontrados campos correspondentes disponíveis no SophiA.')+'. Veja os detalhes abaixo.'};
}
