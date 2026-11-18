(function (root) {
  'use strict';
  const VERSION = '11.0.0', REVISION = 'athus-local-20260915-4';
  const clean = value => String(value || '').replace(/\s+/g, ' ').trim();
  const normalize = value => clean(value).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const subjectKey = value => normalize(value).replace(/[^a-z0-9 ]/g, ' ').split(/\s+/).filter(w => w && !['de','da','do','das','dos','e','em'].includes(w)).sort().join(' ');
  const hash = value => root.AvaliaKnowledgeBase.fnv1a(value);
  const VERB = /(?<![\p{L}])(não\s+)?(é|são|deve|devem|permite|permitem|exige|exigem|depende|dependem|representa|representam|favorece|favorecem|visa|visam|reduz|reduzem|constitui|constituem|contribui|contribuem|possibilita|possibilitam|impede|impedem|promove|promovem|deriva|derivam|resulta|resultam|mantém|mantêm)(?![\p{L}])/iu;
  const EXCLUDED = /https?:|www\.|\b(?:ISBN|DOI|gabarito|alternativa|assinale|referências bibliográficas)\b|\.{3}|…|[«»“”"]|\b(?:ou|talvez|eventualmente)\b/i;
  const INCOMPLETE_START = /^(?:se|quando|embora|caso|segundo|conforme|isso|isto|esse|essa|esses|essas|este|esta|estes|estas|ele|ela|eles|elas|portanto|assim|além disso|por exemplo)\b/i;
  const canceled = () => Object.assign(new Error('Trabalho abandonado.'), {code:'WORK_ABANDONED'});

  // Only invert a complete, direct declarative clause. Never negate a quoted
  // speaker, a condition or one side of a disjunction and call it a contradiction.
  function claimFromSentence(value) {
    const sentence = clean(value);
    if (sentence.length < 45 || sentence.length > 480 || sentence.split(' ').length < 8
        || !/[.!]$/.test(sentence) || EXCLUDED.test(sentence) || INCOMPLETE_START.test(sentence)
        || /[\[\]()?:;]|\bnão\s+(?:só|somente|apenas)\b/i.test(sentence)) return null;
    const verb = VERB.exec(sentence);
    if (!verb || verb.index > 140 || /\b(?:que|se|como|pois)\b/i.test(sentence.slice(0, verb.index))) return null;
    const predicate = sentence.slice(verb.index + verb[0].length);
    if (clean(predicate).length < 15) return null;
    const opposite = sentence.slice(0, verb.index) + (verb[1] ? verb[2] : 'não ' + verb[2].toLocaleLowerCase('pt-BR')) + predicate;
    return {text:sentence, opposite:opposite[0].toUpperCase() + opposite.slice(1),
      topic:clean(sentence.slice(0,verb.index)).replace(/^(?:O|A|Os|As|Um|Uma)\s+/,'')};
  }

  function sentences(text) {
    if (typeof Intl !== 'undefined' && Intl.Segmenter) return Array.from(new Intl.Segmenter('pt-BR',{granularity:'sentence'}).segment(text), s => s.segment);
    return String(text).split(/(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-Þ])/);
  }

  const documentCache=new WeakMap(),tokenCache=new WeakMap();
  function claimsForDocument(doc) {
    const cached=documentCache.get(doc);
    if(cached&&cached.text===doc.text&&cached.name===doc.name&&cached.ua===doc.assignedUa)return cached.claims;

    const entries = root.AvaliaPremiumCurator.curateLines(doc.text || '').accepted;
    let ua = Number(doc.assignedUa) || root.AvaliaKnowledgeBase.detectMaterialUa(doc.name, doc.text, '').ua || 0;
    let buffer = [], start = 0, previous = 0;
    const claims = [];
    const flush = () => {
      if (ua) for (const sentence of sentences(buffer.join(' '))) {
        const claim = claimFromSentence(sentence);
        if (claim) claims.push({...claim, ua, line:start, documentId:doc.id, documentName:doc.name,
          id:hash(normalize(claim.text)), passageId:doc.id + ':' + ua + ':' + start});
      }
      buffer = [];
    };
    for (const entry of entries) {
      const heading = entry.text.match(/^(?:unidade(?:\s+de\s+aprendizagem)?\s*(?:UA\s*)?|UA\s*)0?(\d{1,2})\b/i);
      if (heading) { flush(); ua = Number(heading[1]); previous = entry.line; continue; }
      if (/^(?:disciplina|objetivo|ementa)\s*:/i.test(entry.text)) { flush(); previous = entry.line; continue; }
      if (previous && entry.line > previous + 1) flush();
      previous = entry.line;
      if (!buffer.length) start = entry.line;
      buffer.push(entry.text);
      if (/[.!?]$/.test(entry.text)) flush();
    }
    flush();
    documentCache.set(doc,{text:doc.text,name:doc.name,ua:doc.assignedUa,claims});
    return claims;
  }

  function related(a, b) {
    if (a.documentId !== b.documentId || a.ua !== b.ua || a.id === b.id) return false;
    const K = root.AvaliaKnowledgeBase;
    const cachedTokens=c=>{if(!tokenCache.has(c))tokenCache.set(c,new Set(K.tokens(c.text)));return tokenCache.get(c);};
    const left=cachedTokens(a),right=cachedTokens(b);
    return [...left].some(word => right.has(word)) && Math.abs(a.line - b.line) <= 24;
  }

  function optionsForMask(length, mask, target) {
    const all = Array.from({length:2 ** length}, (_,i) => i);
    const wrong = all.filter(i => i !== mask).sort((a,b) => {
      const count = n => n.toString(2).replace(/0/g,'').length;
      return count(a ^ mask) - count(b ^ mask) || a-b;
    }).slice(0,3);
    wrong.splice(target,0,mask);
    const roman = ['I','II','III'];
    return wrong.map(value => Array.from({length}, (_,i) => `${roman[i]}: ${value & (1<<i) ? 'Falso' : 'Verdadeiro'}`).join('; ') + '.');
  }

  function buildQuestion(claims, rules, difficulty, format, index, counts, base, contextPool = claims) {
    const C = root.AvaliaPremiumCurator;
    const roman = ['I','II','III'];
    const mask = format === 'discursive' ? 1 : index % (2 ** claims.length);
    const statements = claims.map((claim,i) => mask & (1<<i) ? claim.opposite : claim.text);
    const topic = claims.map(c => c.topic).filter(t => t.length >= 3 && t.length <= 90)[0] || rules.theme;
    const alignment = C.curriculumAlignment(base, rules.theme, claims[0].ua, {concept:topic, definition:claims.map(c=>c.text).join(' ')});
    const objective = alignment?.objective || `Avaliar afirmações sobre ${topic} e justificar correções com os critérios apresentados.`;
    const style = format === 'discursive' ? 'discursive' : index % 3 === 1 ? 'comparison' : index % 3 === 2 ? 'synthesis' : 'true-false';
    const situations = [
      `Uma equipe precisa elaborar um parecer sobre ${topic}, no âmbito de ${rules.theme}. Duas pessoas chegaram a conclusões diferentes a partir das mesmas informações. A coordenação solicitou uma análise que confronte cada conclusão com os critérios apresentados, pois aceitar uma afirmação sem verificar suas condições pode comprometer a decisão. Considere o seguinte conjunto de informações para examinar o parecer.`,
      `Uma organização está comparando propostas relacionadas a ${topic}. A decisão envolve interpretar as relações entre os conceitos de ${rules.theme} e verificar se as justificativas propostas são compatíveis com essas relações. O grupo responsável deve distinguir uma conclusão sustentada de uma conclusão que inverte o sentido de um critério. Para orientar a comparação, o caso apresenta as seguintes informações.`,
      `Ao avaliar uma proposta relacionada a ${topic}, uma equipe identificou interpretações divergentes sobre os critérios da decisão. Antes de aprová-la, precisa produzir uma síntese coerente que considere conjuntamente as relações envolvidas em ${rules.theme}. Uma justificativa que acerta um conceito e contradiz outro não é suficiente para fundamentar o parecer. As informações relevantes para a análise são apresentadas a seguir.`
    ];
    // Complete, related sentences from the SAME UA supplement the case. They
    // are never truncated to reach a word quota or borrowed from another subject.
    const support = contextPool.filter(c => c.documentId === claims[0].documentId && c.ua === claims[0].ua && !claims.some(x=>x.id===c.id) && claims.some(x=>related(x,c)));
    const background = [], contextEvidence=[];
    const assertions = statements.map((text,i)=>`${roman[i]}. ${text}`).join('\n');
    const introduction = situations[index % situations.length];
    for (const c of support) {
      background.push(c.text); contextEvidence.push(c);
      if (root.SmartFoxAthus.wrapLines(introduction+'\n'+background.join(' ')+'\n'+assertions).length >= 15) break;
    }
    const command = format === 'discursive' ? 'Avalie a conclusão apresentada, explique sua relação com os critérios do caso e justifique a decisão que a equipe deve tomar.' : style === 'synthesis' ?
      'Qual síntese das relações conceituais sustenta uma interpretação coerente das informações apresentadas?' : style === 'comparison' ?
      'Comparando as conclusões apresentadas, qual alternativa classifica corretamente cada uma como verdadeira ou falsa?' :
      'Julgue cada afirmação como verdadeira ou falsa e assinale a sequência correta, na ordem apresentada.';
    const context = introduction + (background.length ? '\n\n'+background.join(' ') : '') + '\n\n'+assertions;
    const bodyText = context+'\n\n'+command;
    const reasons = claims.map((claim,i) => `${roman[i]}: ${mask & (1<<i) ? 'Falso' : 'Verdadeiro'}. ${claim.text}`);
    const correctIndex = format === 'discursive' ? -1 : counts.indexOf(Math.min(...counts));
    const labels = format === 'discursive' ? [] : optionsForMask(claims.length, mask, correctIndex);
    const alternatives = labels.map((text,i) => ({letter:'ABCD'[i],plain:style === 'synthesis' ?
      text.split(';').map((part,n) => /Falso/.test(part) ? statements[n] === claims[n].text ? claims[n].opposite : claims[n].text : statements[n]).join(' ') : text}));
    const evidence = [...claims,...contextEvidence].map(claim => ({passageId:claim.passageId, documentId:claim.documentId, documentName:claim.documentName, ua:claim.ua, quote:claim.text, supports:'Critério conceitual ou informação de contextualização.'}));
    const signature = hash(normalize(bodyText)), fingerprint = hash(REVISION + ':' + format + ':' + claims.map(c=>c.id).sort().join(':'));
    return {number:index+1, name:`Questão (${index+1})_${rules.evaluation}_UA (${claims[0].ua})_Obj (${alignment?.objectiveNumber || 1})_${difficulty}${format === 'discursive' ? '_Discursiva' : ''}`,
      assessment:rules.evaluation, theme:rules.theme, ua:String(claims[0].ua), difficulty,
      objective, objectiveNumber:String(alignment?.objectiveNumber || 1), questionFormat:format,
      typeDescription:format === 'discursive' ? 'Discursiva: análise e justificativa de decisão' : style === 'synthesis' ? 'Síntese e aplicação de conceitos' : style === 'comparison' ? 'Comparação de conclusões — verdadeiro ou falso' : 'Verdadeiro ou falso — análise de afirmações',
      bodyText, alternatives, correctIndex, correctLetter:correctIndex < 0 ? '' : 'ABCD'[correctIndex],
      feedbackText:reasons.join('\n'),
      alternativeFeedback:alternatives.map((a,i) => ({letter:a.letter, correct:i === correctIndex,
        text:(i === correctIndex ? 'Este parecer classifica corretamente as afirmações. ' : 'Este parecer classifica incorretamente pelo menos uma afirmação. ') + reasons.join(' ')})),
      expectedResponseText:format === 'discursive' ? reasons.join('\n') : '',
      responseCriteria:format === 'discursive' ? ['Identificar a afirmação que foi invertida.', 'Reescrever a afirmação de acordo com o conteúdo.', 'Relacionar a justificativa à decisão e aos critérios do caso.'] : [],
      studyTopics:[...new Set(claims.map(c=>c.topic).filter(t=>t.length >= 3 && t.length <= 90))].length ? [...new Set(claims.map(c=>c.topic).filter(t=>t.length >= 3 && t.length <= 90))] : [rules.theme],
      sourceText:claims.map(c=>c.text).join('\n'), sourceStart:claims[0].line, sourceEnd:claims.at(-1).line,
      segmentationMethod:'Afirmações completas da mesma UA; estrutura local de revisão', segmentationConfidence:1,
      generatedFromKnowledgeBase:true, generationSignature:signature, generationFactFingerprint:fingerprint, generationRules:rules,
      generationEvidence:{documentId:claims[0].documentId, documentName:claims[0].documentName, documentRole:'reference_material', excerpt:claims.map(c=>c.text).join('\n'), supportingEvidence:evidence},
      curriculumEvidence:alignment || {objective, objectiveNumber:1, inferred:true, planDocumentName:'Objetivo de revisão proposto localmente; conferir com o plano'},
      blueprintEvidence:C.aggregateBlueprint(base,rules.theme,rules.evaluation),
      contextualDesign:{version:VERSION,revision:REVISION,mode:style,newScenario:false,localRules:true,materialRequirements:claims.map(c=>c.text)},
      generationAudit:{ready:false,passed:3,total:3,score:100,manualReviewRequired:true,confidenceBand:'Revisão docente necessária',
        method:'Verificações estruturais locais; a qualidade pedagógica exige revisão docente',
        checks:[{id:'source',pass:true,label:'Afirmações completas vinculadas à fonte'}, {id:'scope',pass:true,label:'Mesma disciplina e UA'}, {id:'structure',pass:true,label:'Pareceres distintos e gabarito calculado pela regra'}],blockers:['Revisão pedagógica do professor pendente.']},
      media:[],formulas:[],warnings:['Proposta por regras locais. Confira redação, nível de dificuldade e pertinência antes de aplicar.']};
  }

  async function generate(base, rules, options = {}) {
    const check = () => { if (options.signal?.aborted) throw canceled(); };
    check();
    if (rules.scopeError) throw new Error(rules.scopeError);
    if (!rules.theme) throw new Error('Informe a disciplina da coleção antes de criar questões.');
    const C = root.AvaliaPremiumCurator;
    if (rules.stageScopeRequired) throw new Error('Informe as UAs trabalhadas na etapa desta avaliação (P1, P2, P3 ou SCH).');
    const refs = (base.documents || []).filter(d => C.isEvidenceDocument(d) && d.analysis?.usable && subjectKey(d.subject || d.analysis.subject) === subjectKey(rules.theme));
    if (!refs.length) throw new Error('Adicione as UAs como Material de conteúdo na coleção da disciplina. Modelos e planos orientam a revisão, mas não substituem o conteúdo estudado.');
    const all = [], seen = new Set();
    const startedAt=Date.now();
    for (const doc of refs) {
      options.onProgress?.(`Lendo afirmações completas de ${doc.name} neste navegador…`);
      for (const claim of claimsForDocument(doc)) if (!seen.has(claim.id)) { seen.add(claim.id); all.push(claim); }
      await new Promise(resolve => setTimeout(resolve,0)); check();
    }
    // Exact opposing statements cannot both serve as an unquestioned answer key.
    const texts = new Set(all.map(c=>normalize(c.text)));
    const conflicts = all.filter(c=>texts.has(normalize(c.opposite)));
    const conflictIds = new Set(conflicts.map(c=>c.id));
    for (let i=all.length-1;i>=0;i--) if (conflictIds.has(all[i].id)) all.splice(i,1);
    const allowed = rules.allowedUas || [];
    const available = [...new Set(all.map(c=>c.ua))].filter(ua=>!allowed.length || allowed.includes(ua)).sort((a,b)=>a-b);
    const uas = rules.explicitUaScope ? allowed : available;
    const levels = Object.entries(rules.distribution || {}).flatMap(([level,count])=>Array.from({length:count},()=>level));
    const requested = rules.totalCount || rules.count + (rules.discursiveCount || 0);
    const slots = Array.from({length:requested},(_,i)=>({ua:uas[i % uas.length], difficulty:levels[i] || 'Médio', format:i < rules.count ? 'objective' : 'discursive'}));
    const questions = [], rejected = [], used = new Set(), counts = [0,0,0,0], usedPatterns = new Set();
    for (const conflict of conflicts) rejected.push({source:conflict.documentName, sentence:conflict.text, reason:'O conteúdo inclui uma afirmação oposta. Resolva a divergência antes de usar este trecho como gabarito.'});
    const history = new Set((base.generationHistory || []).map(h=>h.factFingerprint));
    const requestedByUa = {}, producedByUa = {};
    for (const slot of slots) {
      check(); requestedByUa[slot.ua || 'não identificada'] = (requestedByUa[slot.ua || 'não identificada'] || 0) + 1;
      const pool = all.filter(c=>c.ua === slot.ua && !used.has(c.id));
      const required = slot.format === 'discursive' ? 1 : slot.difficulty === 'Difícil' ? 3 : 2;
      let draft, selected, shortContext = false;
      const caseDraft = root.SmartFoxAthusCases?.candidates(pool, rules, questions.length, usedPatterns).find(c=>c.ua===slot.ua && c.difficulty===slot.difficulty);
      if (caseDraft) {
        selected=caseDraft.evidence;
        draft=buildQuestion(selected,rules,slot.difficulty,slot.format,questions.length,counts,base,all);
        draft.bodyText=caseDraft.context+'\n\n'+caseDraft.command;
        draft.typeDescription=caseDraft.typeDescription;
        draft.alternatives=caseDraft.alternatives.map((plain,i)=>({letter:'ABCD'[i],plain}));
        draft.correctIndex=0;draft.correctLetter='A';draft.feedbackText=caseDraft.feedback;
        if(slot.format==='discursive'){
          draft.bodyText=caseDraft.context+'\n\nAnalise a situação, proponha um encaminhamento e justifique como sua decisão atende às condições e limitações apresentadas. Relacione os conceitos envolvidos às evidências do caso.';
          draft.alternatives=[];draft.correctIndex=-1;draft.correctLetter='';
          draft.typeDescription='Discursiva: análise de caso e decisão fundamentada';
          draft.expectedResponseText=caseDraft.alternatives[0]+' '+caseDraft.feedback;
          draft.responseCriteria=['Identificar o problema e as condições relevantes do caso.','Propor uma decisão compatível com as restrições apresentadas.','Relacionar os conceitos à justificativa e explicar as consequências da escolha.'];
        }
        draft.studyTopics=caseDraft.studyTopics;draft.alternativeFeedback=[];
        if(draft.curriculumEvidence?.inferred){draft.objective=caseDraft.objective;draft.curriculumEvidence.objective=caseDraft.objective;}
        draft.contextualDesign={...draft.contextualDesign,newScenario:true,pattern:caseDraft.pattern,reasoningSummary:'Caso didático por estrutura local. Confira a pertinência das fontes, a decisão exigida e a dificuldade antes de liberar.'};
        draft.generationFactFingerprint=hash(REVISION+':'+caseDraft.pattern+':'+selected.map(c=>c.id).sort().join(':'));
        draft.generationSignature=hash(normalize(draft.bodyText));
        if(history.has(draft.generationFactFingerprint)) draft=null;
        else usedPatterns.add(caseDraft.pattern+':'+slot.ua);
      }
      for (const first of draft ? [] : pool) {
        const peers = pool.filter(c=>related(first,c));
        if (peers.length + 1 < required) continue;
        selected = [first,...peers.slice(0,required-1)];
        draft = buildQuestion(selected,rules,slot.difficulty,slot.format,questions.length,counts,base,all);
        if (!history.has(draft.generationFactFingerprint) && root.SmartFoxAthus.wrapLines(root.SmartFoxAthus.bodyParts(draft).context).length >= 15) break;
        if (root.SmartFoxAthus.wrapLines(root.SmartFoxAthus.bodyParts(draft).context).length < 15) shortContext=true;
        draft = null;
      }
      if (draft && root.SmartFoxAthus.wrapLines(root.SmartFoxAthus.bodyParts(draft).context).length < 15) {
        shortContext=true;
        draft=null;
      }
      if (draft) {
        questions.push(draft);selected.forEach(c=>used.add(c.id));history.add(draft.generationFactFingerprint);
        if (draft.correctIndex >= 0) counts[draft.correctIndex]++;
        producedByUa[slot.ua] = (producedByUa[slot.ua] || 0) + 1;
      } else rejected.push({source:`UA ${slot.ua || 'não identificada'}`, sentence:'', reason:shortContext ? 'O conteúdo relacionado disponível não sustenta uma contextualização de pelo menos 15 linhas. Acrescente material relevante para este tema.' : `Não foram encontradas ${required} afirmação(ões) completas e relacionadas ainda disponíveis para este formato. Confira a UA, acrescente conteúdo ou reduza a quantidade.`});
      options.onProgress?.(`${questions.length} proposta(s) montada(s) localmente; preparando ${Object.values(requestedByUa).reduce((a,b)=>a+b,0)} de ${requested}.`);
      await new Promise(resolve=>setTimeout(resolve,0)); check();
    }
    // Balance answer positions without the former repeating A-B-C-D cycle.
    const objectives=questions.filter(q=>q.questionFormat==='objective');
    let positions=objectives.map((q,i)=>i%4);
    for(let attempt=0;attempt<60;attempt++) {
      for(let i=positions.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[positions[i],positions[j]]=[positions[j],positions[i]];}
      if(positions.length<8 || !positions.slice(4).every((n,i)=>n===positions[i%4]))break;
    }
    counts.fill(0);
    objectives.forEach((q,index)=>{
      const correct=q.alternatives[q.correctIndex],others=q.alternatives.filter((a,i)=>i!==q.correctIndex);
      others.splice(positions[index],0,correct);q.alternatives=others.map((a,i)=>({...a,letter:'ABCD'[i]}));
      q.correctIndex=positions[index];q.correctLetter='ABCD'[q.correctIndex];counts[q.correctIndex]++;
      // Per-option notes are private working notes; the final feedback stays concise.
      q.alternativeFeedback=[];
    });
    for(const q of questions) {
      const format=root.AvaliaDocxParser?.formatArithmeticText;
      if(!format)continue;
      const formulas=[];
      for(const [textKey,htmlKey] of [['bodyText','bodyHtml'],['feedbackText','feedbackHtml'],['expectedResponseText','expectedResponseHtml']]) {
        const rich=format(q[textKey]||'');q[htmlKey]=rich.html;formulas.push(...rich.formulas);
      }
      for(const a of q.alternatives){const rich=format(a.plain);a.html=rich.html;formulas.push(...rich.formulas);}
      q.formulas=[...new Map(formulas.map(f=>[f.hash,f])).values()];
    }
    for(const q of questions) q.athusAudit=root.SmartFoxAthus.question(q,rules);
    const athusAudit=root.SmartFoxAthus.batch(questions,rules);
    const status = questions.length === requested ? 'complete' : questions.length ? 'partial' : 'insufficient';
    return {questions, requested, produced:questions.length, rules, rejected, status, athusAudit, manualReviewRequired:true,
      coverage:{requestedByUa,producedByUa,missingUas:uas.filter(ua=>(producedByUa[ua]||0)<(requestedByUa[ua]||0))},
      pipeline:{version:VERSION,revision:REVISION,method:'Casos aplicados, verdadeiro ou falso e síntese conceitual por regras locais',elapsedMs:Date.now()-startedAt,safeFacts:all.length,candidatesConsidered:slots.length,candidatesApproved:questions.length,candidatesRejected:rejected.length,answerDistribution:Object.fromEntries([... 'ABCD'].map((letter,i)=>[letter,counts[i]]))},
      message:`${questions.length} de ${requested} propostas criadas por regras locais, sem serviço de IA. ${athusAudit.ok ? 'Conferência automática sem pendências formais; falta revisão pedagógica.' : `${athusAudit.issues.length} pendência(s) Athus: o resultado é um rascunho para edição.`} Revise antes de aplicar.`};
  }
  root.SmartFoxLocalQuestionGenerator = Object.freeze({version:VERSION,revision:REVISION,generate,claimFromSentence,claimsForDocument,optionsForMask});
})(typeof window !== 'undefined' ? window : globalThis);
