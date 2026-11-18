export const norm = value => String(value ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toUpperCase().replace(/\s+/g, ' ').trim();
const head = value => norm(value).replace(/[^A-Z0-9]/g, '');
export const raKey = value => String(value ?? '').trim().replace(/^(\d+)\.0+$/, '$1').toUpperCase();
export const fields = {
  ra: ['RA', 'MATRICULA', 'CODIGODOALUNO', 'CODIGOALUNO'],
  name: ['NOME', 'ALUNO', 'NOMEDOALUNO'],
  grade: ['NOTA'],
  course: ['CURSOMATRICULA', 'CURSO'],
  discipline: ['DISCIPLINA', 'NOMEDISCIPLINA'],
  code: ['CODIGODISCIPLINA', 'CODDISCIPLINA'],
  campus: ['CAMPUSPOLO', 'POLO', 'CAMPUS', 'UNIDADE'],
  period: ['PERIODO', 'PERIODOCURSO'],
  absent: ['FALTOSO', 'AUSENTE'],
  exam: ['AVALIACAO','TIPOAVALIACAO'],
  academicPeriod: ['PERIODOLETIVO','ANOSEMESTRE','SEMESTRELETIVO']
};

export function recordsFromRows(rows, source) {
  const first = rows.findIndex(row => row.some(v => String(v ?? '').trim()));
  if (first < 0) throw new Error(source + ': planilha vazia.');
  const headers = rows[first].map(head);
  const used = headers.filter(Boolean);
  if (new Set(used).size !== used.length) throw new Error(source + ': há cabeçalhos duplicados.');
  const map = {};
  for (const [key, aliases] of Object.entries(fields)) {
    const indexes = headers.map((h, i) => aliases.includes(h) ? i : -1).filter(i => i >= 0);
    if (indexes.length > 1) throw new Error(source + ': mais de uma coluna corresponde a ' + key + '.');
    map[key] = indexes[0] ?? -1;
  }
  const examColumns=headers.map((h,i)=>['AD','AI','PS','AS','AE'].includes(h)?{exam:h,index:i}:null).filter(Boolean);
  if(map.grade<0&&!examColumns.length)throw new Error(source+': falta a coluna Nota ou AD/AI/PS/AS/AE.');
  if(map.grade>=0&&examColumns.length)throw new Error(source+': use Nota com Avaliação, ou colunas de avaliações; os dois formatos juntos são ambíguos.');
  for (const key of ['ra', 'name', 'discipline']) {
    if (map[key] < 0) throw new Error(source + ': falta a coluna ' + fields[key][0] + '. Use o modelo das planilhas enviadas.');
  }
  const result = [];
  for (let i = first + 1; i < rows.length; i++) {
    const row = rows[i];
    if (!row?.some(v => v !== '' && v != null)) continue;
    if (row.slice(headers.length).some(v => v !== '' && v != null)) throw new Error(source + ': colunas extras na linha ' + (i + 1));
    const record = {source, line: i + 1};
    for (const [key, index] of Object.entries(map)) record[key] = index < 0 ? '' : String(row[index] ?? '').trim();
    record.ra = raKey(record.ra);
    record.disciplineKey = record.code + ' | ' + record.discipline;
    if(examColumns.length){for(const c of examColumns)result.push({...record,grade:String(row[c.index]??'').trim(),exam:c.exam});}
    else result.push(record);
  }
  if (!result.length) throw new Error(source + ': sem registros.');
  return result;
}

export function gradeInfo(raw, absent = '', max = 10) {
  const text = String(raw ?? '').trim();
  const missing = ['F', 'FALTOU', 'FALTOSO', 'AUSENTE'].includes(norm(text));
  const flag = ['TRUE', 'VERDADEIRO', 'SIM', '1', 'S', 'F'].includes(norm(absent));
  if (flag && text && !missing) return {kind: 'invalid', reason: 'Faltoso marcado com nota numérica/texto diferente de F'};
  if (missing || flag) return {kind: 'absent', value: 'F'};
  if (!text) return {kind: 'empty', reason: 'Nota vazia'};
  if (!/^(?:\d+(?:[.,]\d+)?|[.,]\d+)$/.test(text)) return {kind: 'invalid', reason: 'Nota inválida ou fórmula: ' + text};
  const number = Number(text.replace(',', '.'));
  if (!Number.isFinite(number) || number < 0 || number > max) return {kind: 'invalid', reason: 'Nota fora de 0 a ' + max};
  const decimal = text.replace(',', '.').split('.');
  const whole = decimal[0].replace(/^0+(?=\d)/, '') || '0';
  const fraction = (decimal[1] || '').replace(/0+$/, '');
  return {kind: 'number', number, value: whole + (fraction ? ',' + fraction : '')};
}

export function equivalent(a, b) {
  const x = gradeInfo(a, '', 100), y = gradeInfo(b, '', 100);
  if (x.kind === 'number' && y.kind === 'number') return x.number === y.number;
  return norm(a) === norm(b);
}

export function buildPlan(records, snapshot, options) {
  const sourceMap = new Map(), pageMap = new Map();
  for (const r of records) {
    if (!sourceMap.has(r.ra)) sourceMap.set(r.ra, []);
    sourceMap.get(r.ra).push(r);
  }
  for (const r of snapshot.rows) {
    if (!pageMap.has(r.ra)) pageMap.set(r.ra, []);
    pageMap.get(r.ra).push(r);
  }
  const plan = [];
  for (const p of snapshot.rows) {
    const matches = sourceMap.get(p.ra) || [];
    const r = matches[0];
    const item = {ra: p.ra, name: p.name, before: p.value, after: '', status: '', ready: false, target: p.key,
      source: r?.source || '', line: r?.line || '', raw: r?.grade || '', sourceName: r?.name || '',recordId:r?.recordId||'',campus:r?.campus||'',course:r?.course||'',discipline:r?.discipline||'',period:r?.period||''};
    const done = (status, ready = false) => {item.status = status; item.ready = ready; plan.push(item);};
    if (pageMap.get(p.ra).length !== 1) {done('RA repetido no portal'); continue;}
    if (!matches.length) {done('Sem correspondência na planilha filtrada'); continue;}
    if (matches.length !== 1) {item.recordId='';done('RA duplicado na seleção da planilha'); continue;}
    if (!/^\d{5,20}$/.test(p.ra) || !r.name || !/^\d{5,20}$/.test(r.ra)) {done('RA inválido ou identificação incompleta'); continue;}
    if (norm(p.name) !== norm(r.name)) {done('RA confere, mas nome diverge; revisar'); continue;}
    const grade = gradeInfo(r.grade, r.absent, options.sourceMax ?? options.max);
    if (grade.kind === 'empty' || grade.kind === 'invalid') {done(grade.reason); continue;}
    if (grade.kind === 'absent') {
      item.after='';item.blank=true;
      if(!p.value.trim()){done('Faltoso: campo em branco');continue;}
      done('Faltoso: nota existente preservada (campo já preenchido)');continue;
    }
    item.after = grade.value;
    if (grade.kind === 'number' && options.sourceMax === 10 && options.max === 100) {
      const [whole, fraction=''] = grade.value.split(',');
      const scaledWhole=(whole+(fraction[0]||'0')).replace(/^0+(?=\d)/,'');
      const scaledFraction=fraction.slice(1).replace(/0+$/,'');
      item.after=scaledWhole+(scaledFraction?','+scaledFraction:'');
    }
    if (equivalent(p.value, item.after)) {done('Já possui esse valor'); continue;}
    if (!p.editable) {done('Campo ausente, bloqueado ou ambíguo'); continue;}
    if (p.value.trim()) {done('Nota existente preservada'); continue;}
    done(p.value.trim() ? 'Substituir nota existente' : 'Pronto para preencher', true);
  }
  for (const r of records) {
    if (!r.ra || !pageMap.has(r.ra)) plan.push({ra:r.ra, name:r.name, before:'', after:'', raw:r.grade, source:r.source,
      sourceName:r.name, line:r.line, status:/^\d{5,20}$/.test(r.ra) ? 'Não localizado nesta página da turma' : 'RA ausente ou inválido na planilha', ready:false});
  }
  return plan;
}

export function csvText(rows) {
  return '\uFEFF' + rows.map(row => row.map(value => {
    let s = String(value ?? '');
    if (/^[\s]*[=+\-@]/.test(s)) s = "'" + s;
    return '"' + s.replace(/"/g, '""') + '"';
  }).join(';')).join('\r\n');
}
