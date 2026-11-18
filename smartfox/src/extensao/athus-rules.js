(function (root) {
  'use strict';
  const REVISION = 'athus-20260913-3';
  const COUNTS = Object.freeze({AD:10,AI:5,PS:5,P1:18,P2:18,SCH:18,P3:18});
  const LEVELS = ['Fácil','Médio','Difícil'];
  const clean = s => String(s || '').replace(/\s+/g,' ').trim();
  const norm = s => clean(s).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  const plain = s => String(s || '').replace(/<[^>]*>/g,' ').replace(/&nbsp;/g,' ');
  const SOURCE_REFERENCE = /\b(?:material estudado|conteudo estudado|conforme (?:o|esse|este) material|de acordo com o arquivo|segundo o pdf|(?:na|a) ua enviada|conforme o documento|o material registra|o texto registra|(?:arquivo|livro|documento)[ -]fonte|neste (?:arquivo|material|documento))\b|\b\S+\.(?:pdf|docx|pptx)\b/i;
  const FORBIDDEN_OPTION = /\b(?:nra|nenhuma (?:das|de todas as) (?:anteriores|alternativas|respostas)|todas (?:as (?:alternativas|respostas) )?(?:estao |sao )?(?:corretas|erradas))\b/i;
  function masterText(text) { return /PROMPT MESTRE|RESUMO EXECUTIVO DO ATHUS|AD: 10 objetivas.*AI e PS: 5 objetivas/s.test(text); }
  function distribution(total, selected) {
    if (LEVELS.includes(selected)) return Object.fromEntries(LEVELS.map(l=>[l,l===selected?total:0]));
    const raw = [total*0.4,total*0.4,total*0.2], values = raw.map(Math.floor);
    const order = [0,1,2].sort((a,b)=>(raw[b]-values[b])-(raw[a]-values[a]) || a-b);
    const deficit=total-values.reduce((a,b)=>a+b,0);
    for(let i=0;i<deficit;i++)values[order[i]]++;
    return Object.fromEntries(LEVELS.map((l,i)=>[l,values[i]]));
  }
  function uaScope(value) {
    const values=[];const text=String(value || '');
    for(const m of text.matchAll(/(?:UA\s*)?(\d{1,2})\s*(?:a|até|ate|[-–—])\s*(?:UA\s*)?(\d{1,2})/gi)) {
      const a=Number(m[1]),b=Number(m[2]);if(a>b||a<1||b>30) throw Error('Intervalo de UAs inválido.');
      for(let n=a;n<=b;n++)values.push(n);
    }
    const rest=text.replace(/(?:UA\s*)?\d{1,2}\s*(?:a|até|ate|[-–—])\s*(?:UA\s*)?\d{1,2}/gi,' ');
    for(const m of rest.matchAll(/\d+/g)) {const n=Number(m[0]);if(n<1||n>30)throw Error('As UAs devem estar entre 1 e 30.');values.push(n);}
    return [...new Set(values)].sort((a,b)=>a-b);
  }
  function resolve(text='', options={}) {
    // Institutional examples never override the controls. Activity instructions
    // are separate and remain attached to this assessment, not to all disciplines.
    const specific=masterText(text)?'':String(text), t=norm(specific);
    const evaluation=String(options.evaluation || specific.match(/\b(AD|AI|PS|P1|P2|SCH|P3)\b/i)?.[1] || 'AD').toUpperCase();
    if(!COUNTS[evaluation])throw Error('Avaliação não reconhecida.');
    const objectiveMatch=t.match(/\b(\d+)\s*(?:questoes?\s*)?objetivas?\b/);
    const discursiveMatch=t.match(/\b(\d+)\s*(?:questoes?\s*)?discursivas?\b/);
    const totalMatch=t.match(/(?:total\s*[:=]?\s*|\bfaca\s+|\bcrie\s+|\bgerar\s+)(\d+)\s*(?:questoes?)?/);
    const objectiveCount=objectiveMatch?Number(objectiveMatch[1]):null;
    const discursiveCount=discursiveMatch?Number(discursiveMatch[1]):evaluation==='P1'?2:0;
    const explicit=options.count!==undefined&&options.count!==''&&Number(options.count)!==0?Number(options.count):null;
    const textTotal=objectiveCount!==null?objectiveCount+discursiveCount:totalMatch?Number(totalMatch[1]):null;
    const total=explicit ?? textTotal ?? COUNTS[evaluation];
    if(!Number.isInteger(total)||total<1||total>30)throw Error('Informe uma quantidade inteira entre 1 e 30.');
    if(explicit!==null&&textTotal!==null&&explicit!==textTotal)throw Error(`As orientações pedem ${textTotal} questões e o campo Quantidade informa ${explicit}. Corrija a divergência.`);
    if(!Number.isInteger(discursiveCount)||discursiveCount<0||discursiveCount>total)throw Error('Composição objetiva/discursiva incompatível com o total.');
    if(evaluation==='P1'&&discursiveCount!==2)throw Error('A P1 deve manter duas discursivas. Ajuste a composição.');
    if(evaluation==='P1'&&total<3)throw Error('A P1 exige duas discursivas e ao menos uma objetiva.');
    const textUas=specific.match(/(?:UAs?(?:\s+(?:permitidas|da etapa))?|abrang[eê]ncia)\s*[:=]\s*([^\n.;]+)/i)?.[1] || '';
    const requestedUas=uaScope(options.uas || textUas);
    const allowedUas=requestedUas.length?requestedUas:evaluation==='AD'?[1,2,3,4,5]:[];
    if(evaluation==='AD'&&allowedUas.some(n=>n>5))throw Error('AD aceita somente UAs de 1 a 5.');
    const selected=options.difficulty || 'auto';
    let levels=distribution(total,selected);
    if(!LEVELS.includes(selected)) {
      const named=[t.match(/\b(\d+)\s*(?:questoes?\s*)?faceis/),t.match(/\b(\d+)\s*(?:questoes?\s*)?medias/),t.match(/\b(\d+)\s*(?:questoes?\s*)?dificeis/)];
      if(named.every(Boolean)) {levels=Object.fromEntries(LEVELS.map((l,i)=>[l,Number(named[i][1])]));if(Object.values(levels).reduce((a,b)=>a+b,0)!==total)throw Error('A distribuição de dificuldade deve incluir todas as questões, inclusive discursivas.');}
      else if(named.some(Boolean))throw Error('Informe as três quantidades de dificuldade para substituir o padrão 40/40/20.');
    }
    const theme=clean(options.theme || specific.match(/(?:tema|disciplina)\s*[:=]\s*([^\n.;]+)/i)?.[1]);
    const objective=clean(options.objective || specific.match(/objetivo\s*[:=]\s*([^\n]+)/i)?.[1]);
    return {revision:REVISION,evaluation,totalCount:total,count:total-discursiveCount,discursiveCount,distribution:levels,
      allowedUas,explicitUaScope:requestedUas.length>0,scopeError:'',theme,objective,raw:String(text),
      stageScopeRequired:['P1','P2','P3','SCH'].includes(evaluation)&&!requestedUas.length,
      override:explicit!==null||textTotal!==null||Boolean(discursiveMatch)||LEVELS.includes(selected),
      contextMinLines:15,contextMaxLines:null,discursiveMaxLines:null,feedbackMaxLines:6};
  }
  function describe(r) {
    return `${r.evaluation}: ${r.count} objetivas + ${r.discursiveCount} discursivas = ${r.totalCount}. Dificuldade: ${r.distribution['Fácil']} fáceis, ${r.distribution['Médio']} médias, ${r.distribution['Difícil']} difíceis (inclui discursivas). Contextualização: mínimo de 15 linhas no Word padrão. ${r.allowedUas.length?'UAs: '+r.allowedUas.join(', ')+'.':'Informe as UAs trabalhadas nesta etapa.'}`;
  }
  // Matching Arial/Helvetica metrics, in thousandths of an em. Used to lay out
  // the actual Word text, not to inflate a short paragraph with line breaks.
  const WIDTHS = {" ": 278, "!": 278, "\"": 355, "#": 556, "$": 556, "%": 889, "&": 667, "'": 191, "(": 333, ")": 333, "*": 389, "+": 584, ",": 278, "-": 333, ".": 278, "/": 278, "0": 556, "1": 556, "2": 556, "3": 556, "4": 556, "5": 556, "6": 556, "7": 556, "8": 556, "9": 556, ":": 278, ";": 278, "<": 584, "=": 584, ">": 584, "?": 556, "@": 1015, "A": 667, "B": 667, "C": 722, "D": 722, "E": 667, "F": 611, "G": 778, "H": 722, "I": 278, "J": 500, "K": 667, "L": 556, "M": 833, "N": 722, "O": 778, "P": 667, "Q": 778, "R": 722, "S": 667, "T": 611, "U": 722, "V": 667, "W": 944, "X": 667, "Y": 667, "Z": 611, "[": 278, "\\": 278, "]": 278, "^": 469, "_": 556, "`": 333, "a": 556, "b": 556, "c": 500, "d": 556, "e": 556, "f": 278, "g": 556, "h": 556, "i": 222, "j": 222, "k": 500, "l": 222, "m": 833, "n": 556, "o": 556, "p": 556, "q": 556, "r": 333, "s": 500, "t": 278, "u": 556, "v": 500, "w": 722, "x": 500, "y": 500, "z": 500, "{": 334, "|": 260, "}": 334, "~": 584, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, "": 761, " ": 278, "¡": 333, "¢": 556, "£": 556, "¤": 556, "¥": 556, "¦": 260, "§": 556, "¨": 333, "©": 737, "ª": 370, "«": 556, "¬": 584, "­": 333, "®": 737, "¯": 333, "°": 400, "±": 584, "²": 333, "³": 333, "´": 333, "µ": 556, "¶": 537, "·": 278, "¸": 333, "¹": 333, "º": 365, "»": 556, "¼": 834, "½": 834, "¾": 834, "¿": 611, "À": 667, "Á": 667, "Â": 667, "Ã": 667, "Ä": 667, "Å": 667, "Æ": 1000, "Ç": 722, "È": 667, "É": 667, "Ê": 667, "Ë": 667, "Ì": 278, "Í": 278, "Î": 278, "Ï": 278, "Ð": 722, "Ñ": 722, "Ò": 778, "Ó": 778, "Ô": 778, "Õ": 778, "Ö": 778, "×": 584, "Ø": 778, "Ù": 722, "Ú": 722, "Û": 722, "Ü": 722, "Ý": 667, "Þ": 667, "ß": 611, "à": 556, "á": 556, "â": 556, "ã": 556, "ä": 556, "å": 556, "æ": 889, "ç": 500, "è": 556, "é": 556, "ê": 556, "ë": 556, "ì": 278, "í": 278, "î": 278, "ï": 278, "ð": 556, "ñ": 556, "ò": 556, "ó": 556, "ô": 556, "õ": 556, "ö": 556, "÷": 584, "ø": 611, "ù": 556, "ú": 556, "û": 556, "ü": 556, "ý": 500, "þ": 556, "ÿ": 500, "€": 556, "–": 556, "—": 1000};
  const PAGE_WIDTH_PT=481.9, BODY_SIZE_PT=11;
  function textWidth(s) {return [...s].reduce((n,c)=>n+(WIDTHS[c]??WIDTHS[c.normalize('NFD')[0]]??556),0)*BODY_SIZE_PT/1000;}
  function wrapLines(text) {
    const lines=[];
    for(const paragraph of String(text||'').split(/\n+/).map(clean).filter(Boolean)) {
      let line='';
      for(const word of paragraph.split(' ')) {
        const trial=line?line+' '+word:word;
        if(line&&textWidth(trial)>PAGE_WIDTH_PT-5) {lines.push(line);line=word;}else line=trial;
      }
      if(line)lines.push(line);
    }
    return lines;
  }
  function bodyParts(q) {
    const rows=String(q.bodyText||'').split(/\n+/).map(clean).filter(Boolean);
    return {context:rows.slice(0,-1).join('\n'),command:rows.at(-1)||''};
  }
  function fingerprint(q) {
    const payload=JSON.stringify([q.name,q.theme,q.objective,q.difficulty,q.typeDescription,q.bodyText,q.questionFormat,q.expectedResponseText,q.alternatives?.map(a=>a.plain||a.text),q.correctLetter,q.feedbackText]);
    let h=2166136261;for(let i=0;i<payload.length;i++)h=Math.imul(h^payload.charCodeAt(i),16777619);
    return (h>>>0).toString(16);
  }
  function question(q, rules, options={}) {
    const issues=[],add=(code,message)=>issues.push({code,message});
    const discursive=q.questionFormat==='discursive';
    const parts=bodyParts(q),contextLines=wrapLines(parts.context).length,feedbackLines=wrapLines(q.feedbackText).length;
    if(!clean(q.theme))add('ATHUS.TEMA','Informe o Tema Gerador.');
    if(!clean(q.objective))add('ATHUS.OBJETIVO','Vincule um objetivo efetivamente avaliado.');
    if(q.curriculumEvidence?.inferred&&!q.athusObjectiveConfirmed)add('ATHUS.OBJETIVO_PROPOSTO','Confira e confirme o objetivo proposto localmente; ele não foi extraído de um plano.');
    if(!clean(q.typeDescription))add('ATHUS.TIPO','Informe a habilidade efetivamente avaliada.');
    if(!LEVELS.includes(q.difficulty))add('ATHUS.DIFICULDADE','Informe Fácil, Médio ou Difícil.');
    const name=clean(q.name).match(/^Quest[aã]o\s*\((\d+)\)_(AD|AI|PS|P1|P2|SCH|P3)_UA\s*\((\d+)\)_Obj\s*\((\d+)\)_(Fácil|Médio|Difícil)(_Discursiva)?$/i);
    if(!name)add('ATHUS.IDENTIFICACAO','Use Questão (x)_AVALIAÇÃO_UA (x)_Obj (x)_nível.');
    else if(name[2].toUpperCase()!==(q.assessment||rules?.evaluation)||Number(name[3])!==Number(q.ua)||Number(name[4])!==Number(q.objectiveNumber)||norm(name[5])!==norm(q.difficulty))add('ATHUS.IDENTIFICACAO_DIVERGENTE','A identificação diverge dos campos avaliação, UA, objetivo ou dificuldade.');
    if(discursive && !/_Discursiva$/i.test(clean(q.name)))add('ATHUS.NOME_DISCURSIVA','Acrescente _Discursiva ao final do nome da questão discursiva.');
    if(!discursive && /_Discursiva$/i.test(clean(q.name)))add('ATHUS.NOME_FORMATO','Retire _Discursiva do nome da questão objetiva.');
    if(rules?.allowedUas?.length&&!rules.allowedUas.includes(Number(q.ua)))add('ATHUS.UA','A UA da questão está fora da abrangência selecionada.');
    if((q.assessment||rules?.evaluation)==='AD'&&(Number(q.ua)<1||Number(q.ua)>5))add('ATHUS.UA_AD','A AD utiliza somente UAs de 1 a 5.');
    if(contextLines<15)add('ATHUS.CONTEXTO',`Contextualização com ${contextLines} linhas no Word padrão; use no mínimo 15 linhas com informações relevantes, tanto em objetivas quanto em discursivas.`);
    if(!parts.command||!/[?!.]$/.test(parts.command))add('ATHUS.COMANDO','Escreva um comando direto, separado da contextualização.');
    if(discursive&&parts.command.split(/\s+/).length>30)add('ATHUS.COMANDO_DISC','Encurte a pergunta discursiva; prefira uma única frase direta.');
    if(/(?:assinale|marque|selecione|qual).{0,70}\bincorret[ao]/i.test(parts.command))add('ATHUS.COMANDO_NEGATIVO','Peça uma decisão ou resposta correta, sem comandar a escolha da incorreta.');
    if(feedbackLines<1||feedbackLines>6)add('ATHUS.FEEDBACK',`Feedback com ${feedbackLines} linhas; use de 1 a 6 no Word padrão.`);
    const studentFields=[q.theme,q.objective,q.typeDescription,q.bodyText,q.feedbackText,q.expectedResponseText,...(q.alternatives||[]).flatMap(a=>[a.plain||a.text,plain(a.html)]),plain(q.bodyHtml),plain(q.feedbackHtml)];
    if(studentFields.some(s=>SOURCE_REFERENCE.test(norm(s))))add('ATHUS.FONTE_NO_TEXTO','Retire referências ao material, arquivo ou UA enviada do texto da questão e do feedback.');
    const sourceNames=[q.generationEvidence?.documentName,...(q.generationEvidence?.supportingEvidence||[]).map(e=>e.documentName)].filter(Boolean);
    if(sourceNames.some(name=>studentFields.some(s=>norm(s).includes(norm(name)))))add('ATHUS.NOME_DA_FONTE','O nome do arquivo deve ficar apenas na conferência docente.');
    if(/(?:guia de revis[aã]o|quadro de estudo|revisar o texto antes da entrega)/i.test(parts.context)&&/I[:.]|manter|corrigir/.test(q.bodyText))add('ATHUS.CASO_GENERICO','Substitua o exercício genérico de revisar afirmações por uma situação aplicada com problema e dados necessários à decisão.');
    if(discursive) {if(!clean(q.expectedResponseText))add('ATHUS.RESPOSTA_ESPERADA','Informe a resposta esperada da discursiva.');}
    else {
      const a=q.alternatives||[];if(a.length!==4)add('ATHUS.ALTERNATIVAS','A objetiva deve ter exatamente quatro alternativas A–D.');
      const texts=a.map(x=>clean(x.plain||x.text));
      if(texts.some(s=>!s)||new Set(texts.map(norm)).size!==4)add('ATHUS.OPCOES_DISTINTAS','Preencha quatro alternativas distintas.');
      if(texts.some(s=>/\b(?:manter|corrigir)\b/i.test(s)) && /afirma[cç][oõ]es|parecer/i.test(q.bodyText))add('ATHUS.VERDADEIRO_FALSO','Use verdadeiro ou falso para julgar afirmações, em vez de manter ou corrigir.');
      if(texts.some(s=>FORBIDDEN_OPTION.test(norm(s))))add('ATHUS.OPCAO_PROIBIDA','Substitua opções genéricas como NRA, todas ou nenhuma.');
      if(!/^[A-D]$/.test(q.correctLetter||''))add('ATHUS.GABARITO','Indique uma única alternativa correta A–D.');
      if(Number.isInteger(q.correctIndex)&&q.correctIndex!=='ABCD'.indexOf(q.correctLetter))add('ATHUS.GABARITO_DIVERGENTE','A letra do gabarito diverge da alternativa marcada.');
      const sizes=texts.map(s=>s.length);if(Math.min(...sizes)>0&&Math.max(...sizes)>Math.min(...sizes)*2.2)add('ATHUS.TAMANHO_ALTERNATIVAS','Equilibre a extensão das alternativas para não destacar o gabarito.');
    }
    if(options.requireReview&&q.athusReview?.fingerprint!==fingerprint(q))add('ATHUS.REVISAO_DOCENTE','Confirme contexto, objetivo, distratores, gabarito e dificuldade após a última edição.');
    return {revision:REVISION,ok:!issues.length,issues,contextLines,feedbackLines,manualReviewRequired:true};
  }
  function batch(questions,rules,options={}) {
    const issues=[];const add=(code,message)=>issues.push({code,message});
    if(!rules) {add('ATHUS.REGRAS_AUSENTES','Confira as regras desta avaliação antes de liberar.');return {ok:false,issues,questions:[]};}
    if(rules.stageScopeRequired)add('ATHUS.ETAPA','Informe as UAs trabalhadas na etapa desta avaliação.');
    if(questions.some(q=>q.assessment !== rules.evaluation))add('ATHUS.AVALIACAO','Há questão identificada com uma avaliação diferente das regras do lote.');
    const discursive=questions.filter(q=>q.questionFormat==='discursive').length;
    if(questions.length!==rules.totalCount)add('ATHUS.QUANTIDADE',`Lote com ${questions.length} de ${rules.totalCount} questões previstas.`);
    if(discursive!==rules.discursiveCount||questions.length-discursive!==rules.count)add('ATHUS.COMPOSICAO',`Composição prevista: ${rules.count} objetivas e ${rules.discursiveCount} discursivas.`);
    for(const level of LEVELS) {const n=questions.filter(q=>q.difficulty===level).length;if(n!==(rules.distribution[level]||0))add('ATHUS.DISTRIBUICAO',`${level}: ${n} questão(ões); previsto ${rules.distribution[level]||0}, incluindo discursivas.`);}
    const reports=questions.map(q=>question(q,rules,options));
    reports.forEach((report,index)=>report.issues.forEach(i=>issues.push({...i,number:questions[index].number,index,message:`Questão ${questions[index].number}: ${i.message}`})));
    const keys=questions.filter(q=>q.questionFormat!=='discursive').map(q=>q.correctLetter);
    const counts=[...'ABCD'].map(l=>keys.filter(k=>k===l).length);
    if(keys.length>=4&&Math.max(...counts)-Math.min(...counts)>1)add('ATHUS.EQUILIBRIO_GABARITO','Distribua os gabaritos A–D de forma equilibrada no conjunto.');
    if(keys.length>=8&&keys.slice(4).every((k,i)=>k===keys[i%4]))add('ATHUS.PADRAO_GABARITO','Evite repetir uma sequência previsível de quatro letras no gabarito.');
    const signatures=new Set();for(const q of questions){const s=norm(q.bodyText);if(signatures.has(s))add('ATHUS.REPETICAO','Há enunciados idênticos no lote.');signatures.add(s);}
    return {revision:REVISION,ok:!issues.length,issues,questions:reports,manualReviewRequired:true};
  }
  function assertReady(questions,rules) {
    const report=batch(questions,rules,{requireReview:true});
    if(!report.ok)throw new Error('A avaliação ainda possui pendências Athus:\n'+report.issues.slice(0,8).map(i=>'- '+i.message).join('\n')+'\nCorrija na revisão ou baixe o rascunho para edição.');
    return report;
  }
  root.SmartFoxAthus=Object.freeze({revision:REVISION,counts:COUNTS,levels:LEVELS,resolve,distribution,describe,masterText,wrapLines,bodyParts,fingerprint,question,batch,assertReady,sourceReference:SOURCE_REFERENCE});
})(typeof window!=='undefined'?window:globalThis);
