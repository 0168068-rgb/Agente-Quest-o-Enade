(function (root) {
  "use strict";

  const VERSION = "11.0.0";
  // Revision of the local analysis, independent of the public product name.
  const ANALYSIS_REVISION = "conteudo-confirmado-20260913";
  const PEDAGOGICAL_PROFILE = Object.freeze({
    referenceDocuments: 48,
    purpose: "Estrutura pedagógica extraída de exemplos de AD, AI, PS, P1, P2, P3 e SCH",
    minimumCaseWords: 60,
    maximumCaseWords: 260,
    principles: ["situação autônoma", "objetivo verificável", "comando ligado ao caso", "alternativas justificadas", "gabarito rastreável"],
    method: "Regras locais; os modelos orientam a estrutura e não fornecem respostas para outras disciplinas."
  });
  const ROLES = Object.freeze({
    AUTO: "auto",
    TEACHING_PLAN: "teaching_plan",
    REFERENCE: "reference_material",
    ASSESSMENT_MODEL: "assessment_model",
    RULES: "rules"
  });
  const ROLE_LABELS = Object.freeze({
    auto: "Detecção automática",
    teaching_plan: "Plano de ensino",
    reference_material: "Material de conteúdo",
    assessment_model: "Modelo de avaliação",
    rules: "Regras institucionais"
  });
  const STOP_WORDS = new Set((
    "a o as os um uma uns umas de da do das dos em no na nos nas por para com sem sobre entre e ou que qual quais " +
    "como quando onde porque pois se sua seu suas seus este esta estes estas isso isto aquele aquela ao aos à às " +
    "ser estar ter foi são é era foram pode podem deve devem também mais menos cada uma mesmo mesma ensino aluno " +
    "estudante unidade curricular disciplina conteúdo objetivo geral específicos específica específicas"
  ).split(/\s+/));
  const SECTION_HEADINGS = /^(?:ementa|objetivo\s+geral|objetivos?\s+espec[ií]ficos?|compet[eê]ncias?(?:\s+e\s+habilidades?)?|conte[uú]do\s+program[aá]tico|interdisciplinaridade|metodologia|sistema\s+de\s+avalia[cç][aã]o|bibliografia|refer[eê]ncias?)\b/i;
  const BIBLIOGRAPHY_HEADING = /^(?:\d+[.\s-]*)?(?:bibliografia|refer[eê]ncias?)(?:\s+(?:b[aá]sica|complementar|bibliogr[aá]ficas?))?\s*:?[\s-]*$/i;
  const URL_PATTERN = /(?:https?:\/\/|www\.|(?:^|\s)\/\/[a-z0-9]|\b(?:doi|url)\s*:|\b[a-z0-9-]+\.(?:com|com\.br|org|org\.br|edu|edu\.br|gov|gov\.br|net)(?:\/|\b))/i;
  const QR_PATTERN = /\b(?:qr\s*-?\s*code|qrcode|qrgo|qr\.page|page\.link)\b/i;
  const SOURCE_NOTE_PATTERN = /^\s*(?:fonte|adaptad[oa]\s+de|extra[ií]do\s+de|dispon[ií]vel\s+em|acesso\s+em)\s*:/i;
  const BIBLIOGRAPHIC_PATTERN = /(?:\beditora\b|\brecurso\s+eletr[oô]nico\b|\b(?:isbn|issn)\b|\b(?:v\.|vol\.|n\.|pp?\.)\s*\d+|\b(?:19|20)\d{2}\b.{0,45}\b(?:ed\.|edi[cç][aã]o|porto alegre|s[aã]o paulo|rio de janeiro)\b)/i;
  const AUTHOR_RECORD_PATTERN = /^[A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇ][A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇ' -]{2,},\s*[A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇ]/;
  const INLINE_CITATION_PATTERN = /\s*\((?:[A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇ][\p{L}'’-]+(?:\s+(?:e|&|et\s+al\.?|[A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇ][\p{L}'’-]+))*[,]?\s*)?(?:19|20)\d{2}[a-z]?(?:,\s*p\.?\s*\d+(?:[-–]\d+)?)?\)/giu;
  const FORBIDDEN_OUTPUT = /(?:https?:\/\/|www\.|(?:^|\s)\/\/[a-z0-9]|\b(?:doi|isbn|issn)\b|\b(?:fonte|adaptad[oa]\s+de|dispon[ií]vel\s+em|acesso\s+em)\s*:|\b(?:bibliografia|refer[eê]ncias?\s+bibliogr[aá]ficas?)\b|\beditora\b|\bqr\s*-?\s*code\b|\bqrcode\b|\[\s*\.\.\.\s*\]|\.{3,}|_{3,})/i;
  const FORBIDDEN_SOURCE_REFERENCE = /\b(?:material\s+estudado|conte[uú]do\s+estudado|conforme\s+o\s+material|de\s+acordo\s+com\s+o\s+arquivo|segundo\s+o\s+pdf|na\s+ua\s+enviada|conforme\s+o\s+documento|neste\s+material|neste\s+arquivo|neste\s+documento|arquivo-fonte|texto-base)\b/i;
  const DANGLING_START = /^(?:enquanto|quando|onde|embora|porque|pois|conforme|segundo|assim\s+como|de\s+acordo|cujo|cuja|que\b|e\b|ou\b|mas\b|por[eé]m\b|ele\b|ela\b|eles\b|elas\b|isso\b|isto\b)/i;
  const DANGLING_END = /(?:\b(?:de|da|do|das|dos|em|no|na|nos|nas|com|sem|para|por|e|ou|que|como|quando|porque|pois|cujo|cuja|ao|aos)\s*|[-–—,:;])$/i;

  function normalize(value) {
    return String(value == null ? "" : value)
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[\u00ad\u200b-\u200d\ufeff]/g, "")
      .toLocaleLowerCase("pt-BR")
      .replace(/[^a-z0-9%+\-=<>²³⁰¹⁴⁵⁶⁷⁸⁹\s]/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function clean(value) {
    return String(value == null ? "" : value)
      .replace(/\r\n?/g, "\n")
      .replace(/[\u00ad\u200b-\u200d\ufeff]/g, "")
      .replace(/[ \t]+/g, " ")
      .replace(/\n[ \t]+/g, "\n")
      .replace(/\n{3,}/g, "\n\n")
      .trim();
  }

  function repairWordBreaks(value) {
    return clean(String(value || "")
      .replace(/([A-Za-zÀ-ÿ]{4,})-\s*\n\s*([a-zà-ÿ]{2,})/g, "$1$2")
      .replace(/([A-Za-zÀ-ÿ]{4,})-\s+([a-zà-ÿ]{2,})/g, "$1$2"));
  }

  function tokens(value) {
    return (normalize(value).match(/[a-z0-9%+\-=<>²³⁰¹⁴⁵⁶⁷⁸⁹]{3,}/g) || []).filter((term) => !STOP_WORDS.has(term));
  }

  function unique(values) {
    return [...new Set((values || []).filter(Boolean))];
  }

  function similarity(left, right) {
    const a = new Set(tokens(left));
    const b = new Set(tokens(right));
    if (!a.size || !b.size) return 0;
    let intersection = 0;
    a.forEach((term) => { if (b.has(term)) intersection += 1; });
    return intersection / Math.max(1, Math.min(a.size, b.size));
  }

  function fnv1a(value) {
    let hash = 0x811c9dc5;
    const text = String(value || "");
    for (let index = 0; index < text.length; index += 1) {
      hash ^= text.charCodeAt(index);
      hash = Math.imul(hash, 0x01000193);
    }
    return (hash >>> 0).toString(16).padStart(8, "0");
  }

  function inferSubjectFromName(name) {
    return clean(String(name || "")
      .replace(/\.[^.]+$/, "")
      .replace(/[_-]+/g, " ")
      .replace(/\b(?:AD|AI|PS|P1|P2|P3|SCH)\b/gi, " ")
      .replace(/\b(?:avalia[cç][aã]o|diagn[oó]stica|quest[oõ]es?|padr[aã]o|projeto|athus|plano\s+de\s+ensino|modelo|revisada|entrada|arquivo|material)\b/gi, " ")
      .replace(/\b(?:19|20)\d{2}(?:[._-]\d)?\b/g, " ")
      .replace(/\bUA\s*\d{1,2}\b/gi, " ")
      .replace(/\(\d+\)/g, " ")
      .replace(/\s+/g, " "));
  }

  function subjectFromText(lines) {
    for (const line of lines) {
      const match = line.match(/^(?:unidade\s+curricular|disciplina)\s*:\s*(.{3,160})$/i);
      if (match && !/^\(?alinhamento|^\(?3\s+objetivos/i.test(match[1])) return clean(match[1]);
    }
    for (const line of lines) {
      const match = line.match(/^avalia[cç][aã]o\s+(?:diagn[oó]stica\s+)?de\s+(.{3,160})$/i);
      if (match) return clean(match[1]);
    }
    return "";
  }

  function classifyRole(text, name, requestedRole) {
    const source = clean(text);
    const normalized = normalize(`${name}\n${source}`);
    const counts = {
      teaching_plan: [ /plano de ensino/i, /\bementa\b/i, /objetivo geral/i, /objetivos especificos/i, /conteudo programatico/i ].reduce((score, pattern) => score + (pattern.test(normalized) ? 2 : 0), 0),
      assessment_model: Math.min(12, (source.match(/(?:^|\n)\s*Quest[aã]o\s*(?:n[º°o.]\s*)?\(?\d+/gi) || []).length * 2) + Math.min(12, (source.match(/\bGabarito\s*:?\s*(?:[A-E]\b|a resposta|esperado)/gi) || []).length * 2),
      rules: [ /regras? (?:da|de|do)/i, /prompt mestre/i, /quantidade padrao/i, /distribuicao (?:oficial|pratica) de dificuldade/i, /(?:proibid[oa]s?|obrigat[oó]ri[oa]s?)\s+(?:nas? questoes|na avaliacao|no enunciado|alternativas)/i ].reduce((score, pattern) => score + (pattern.test(normalized) ? 3 : 0), 0),
      reference_material: /(?:^|[ _-])UA[ _-]*0?\d{1,2}\b|unidade de aprendizagem/i.test(name) ? 7 : 1
    };
    const sorted = Object.entries(counts).sort((left, right) => right[1] - left[1]);
    const detected = sorted[0][0];
    const confidence = Math.max(0.35, Math.min(0.99, sorted[0][1] / Math.max(6, sorted[0][1] + sorted[1][1])));
    const requested = Object.values(ROLES).includes(requestedRole) ? requestedRole : ROLES.AUTO;
    const role = requested !== ROLES.AUTO ? requested : detected;
    const warnings = [];
    if (requested !== ROLES.AUTO && requested !== detected && sorted[0][1] >= 5) warnings.push(requested === ROLES.REFERENCE ? "Material de conteúdo confirmado pelo professor. Regras, normas e procedimentos presentes na UA podem fundamentar questões; a sugestão automática de classificação não bloqueia o uso." : `Classificação do professor mantida: ${ROLE_LABELS[requested]}. Sugestão automática: ${ROLE_LABELS[detected]}.`);
    return { role, detectedRole: detected, requestedRole: requested, confidence, scores: counts, warnings };
  }

  function junkReason(line, section) {
    const value = clean(line);
    if (!value) return "linha vazia";
    if (section === "bibliography") return "seção bibliográfica";
    if (URL_PATTERN.test(value)) return "URL ou endereço eletrônico";
    if (QR_PATTERN.test(value)) return "QR code ou redirecionador";
    if (SOURCE_NOTE_PATTERN.test(value)) return "nota de fonte/adaptação";
    if (BIBLIOGRAPHIC_PATTERN.test(value) || AUTHOR_RECORD_PATTERN.test(value)) return "registro bibliográfico";
    if (/\[\s*\.\.\.\s*\]|\.{3,}/.test(value)) return "trecho truncado ou elipse editorial";
    if (/_{3,}/.test(value)) return "lacuna ou campo de formulário";
    if (/\b(?:matr[ií]cula|nome\s+do\s+estudante|data\s+_{2,}|cada\s+quest[aã]o\s+vale)\b/i.test(value)) return "campo administrativo";
    if (/^(?:p[aá]gina\s+)?\d+\s*(?:de\s+\d+)?$/i.test(value)) return "numeração de página";
    return "";
  }

  function stripInlineCitations(value) {
    return clean(String(value || "")
      .replace(INLINE_CITATION_PATTERN, "")
      .replace(/\s+([,.;:!?])/g, "$1"));
  }

  function curateLines(text) {
    const repaired = repairWordBreaks(text);
    const lines = repaired.split(/\n+/).map((line) => clean(line)).filter(Boolean);
    const accepted = [];
    const quarantined = [];
    const sections = [];
    let section = "content";
    let sectionStart = 1;
    const closeSection = (end) => {
      if (end >= sectionStart) sections.push({ kind: section, startLine: sectionStart, endLine: end });
    };
    lines.forEach((line, index) => {
      if (BIBLIOGRAPHY_HEADING.test(line) || /^(?:bibliografia|refer[eê]ncias?)\s+(?:b[aá]sica|complementar)\s*:/i.test(line)) {
        closeSection(index);
        section = "bibliography";
        sectionStart = index + 1;
      }
      if (section === "bibliography" && /^(?:UA\s*\d+|Unidade(?:\s+de\s+Aprendizagem)?\s*\d+|Cap[ií]tulo\s*\d+|(?:Introdu[cç][aã]o|Desenvolvimento|Considera[cç][oõ]es finais)\s*:)/i.test(line)) {
        closeSection(index); section="content"; sectionStart=index+1;
      }
      const reason = junkReason(line, section);
      if (reason) quarantined.push({ line: index + 1, text: line.slice(0, 280), reason });
      else accepted.push({ line: index + 1, text: stripInlineCitations(line), section });
    });
    closeSection(lines.length);
    const reasonCounts = quarantined.reduce((counts, item) => ({ ...counts, [item.reason]: (counts[item.reason] || 0) + 1 }), {});
    return { repaired, lines, accepted, quarantined, reasonCounts, sections };
  }

  function sectionValue(lines, startPattern, endPatterns) {
    const start = lines.findIndex((line) => startPattern.test(line));
    if (start < 0) return "";
    const first = clean(lines[start].replace(startPattern, ""));
    const parts = first ? [first] : [];
    for (let index = start + 1; index < lines.length; index += 1) {
      if (endPatterns.some((pattern) => pattern.test(lines[index]))) break;
      if (BIBLIOGRAPHY_HEADING.test(lines[index])) break;
      parts.push(lines[index]);
    }
    return clean(parts.join(" "));
  }

  function splitObjectives(value) {
    const source = clean(value).replace(/^[:\s-]+/, "");
    if (!source || /^(?:\(?\s*3\s+objetivos?|alinhamento\s+com)/i.test(source)) return [];
    const raw = source.includes("•")
      ? source.split(/\s*•\s*/)
      : source.split(/(?<=[.!?;])\s+(?=[A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇ])/u);
    return unique(raw.map((item) => clean(item.replace(/^[\d.)\s-]+/, "").replace(/[.;]+$/, ""))).filter((item) => item.length >= 28 && item.length <= 520));
  }

  function extractCurriculum(lines, subject) {
    const syllabus = sectionValue(lines, /^ementa\s*:\s*/i, [/^objetivo\s+geral\s*:/i]);
    const generalObjective = sectionValue(lines, /^objetivo\s+geral\s*:\s*/i, [/^objetivos?\s+espec[ií]ficos?\s*:/i, /^compet[eê]ncias?/i]);
    const specificText = sectionValue(lines, /^objetivos?\s+espec[ií]ficos?\s*:\s*/i, [/^\*?compet[eê]ncias?/i, /^conte[uú]do\s+program[aá]tico/i]);
    const specificObjectives = splitObjectives(specificText).map((text, index) => ({ id: index + 1, text }));
    const uas = [];
    let withinProgram = false;
    for (let index = 0; index < lines.length; index += 1) {
      const line = lines[index];
      if (/^conte[uú]do\s+program[aá]tico/i.test(line)) withinProgram = true;
      if (withinProgram && /^(?:interdisciplinaridade|metodologia|sistema\s+de\s+avalia[cç][aã]o|bibliografia|refer[eê]ncias?)/i.test(line)) withinProgram = false;
      if (!withinProgram) continue;
      const match = line.match(/^UA\s*(\d{1,2})(?:\s*[:\-–]\s*|\s+)?(.*)$/i);
      if (!match) continue;
      const number = Number(match[1]);
      const following = [];
      for (let cursor = index + 1; cursor < lines.length && following.length < 3; cursor += 1) {
        if (/^UA\s*\d{1,2}\b/i.test(lines[cursor]) || SECTION_HEADINGS.test(lines[cursor])) break;
        if (!/^(?:unidades?\s+de\s+aprendizagem|conte[uú]do\s+espec[ií]fico|habilidades?\s+aplicadas?)$/i.test(lines[cursor])) following.push(lines[cursor]);
      }
      const inlineTitle = clean(match[2]);
      const title = inlineTitle || clean(following[0] || "");
      const content = inlineTitle ? clean(following[0] || "") : title;
      const skills = inlineTitle ? clean(following[1] || following[0] || "") : clean(following[1] || "");
      if (title && !/^(?:t[ií]tulo|conte[uú]do|preencher|x+)$/i.test(title) && !uas.some((entry) => entry.number === number)) uas.push({ number, title, content, skills });
    }
    const completenessParts = [Boolean(subject), syllabus.length >= 40, generalObjective.length >= 35, specificObjectives.length >= 2, uas.length >= 1];
    const completeness = Math.round(completenessParts.filter(Boolean).length / completenessParts.length * 100);
    return { subject, syllabus, generalObjective, specificObjectives, uas, completeness };
  }

  function extractAssessmentBlueprint(text) {
    const source = clean(text);
    const headers = [...source.matchAll(/(?:^|\n)\s*(?:\d+[.)]\s*)?Quest[aã]o\s*(?:n[º°o.]\s*)?\(?\d+[^\n]*/gi)];
    // Older models can have unnumbered questions, inline alternatives and inline feedback.
    const blocks = headers.length ? headers.map((h, i) => source.slice(h.index, headers[i + 1]?.index ?? source.length))
      : source.split(/\bGabarito\s*:/i).slice(0, -1);
    const questions = blocks.map((block) => {
      const canonical = block.match(/Quest[aã]o\s*\((\d+)\)_([A-Z0-9]+)_(?:UA\s*\(([^)]+)\)_)?Obj\s*\(([^)]+)\)_([^\n]+)/i);
      const meta = (pattern) => clean(block.match(pattern)?.[1] || "");
      const type = meta(/(?:Tipo\s+de\s+quest[aã]o|Modelo(?:\s+de\s+quest[aã]o)?)\s*:?\s*([^\n]+?)(?=\s+(?:Tema|N[ií]vel|Multidisciplinaridade)\b|\n|$)/i);
      const objective = meta(/Objetivo(?:\s+associado|\s+do\s+plano\s+de\s+ensino|\s+de\s+aprendizagem|\s+espec[ií]fico)?\s*:?\s*([^\n]+?)(?=\s+N[ií]vel\b|\n|$)/i);
      const alternatives = [...block.matchAll(/(?:^|[\s(])([A-E])\)\s+/gi)];
      const body = block.slice(0, alternatives[0]?.index ?? block.search(/Gabarito|Feedback/i) >>> 0)
        .split(/\n+/).filter(line => !/^\s*(?:Quest[aã]o|Objetivo|Tema|Tipo|Modelo|N[ií]vel|Multidisciplinaridade|UA\b|•|\[)/i.test(line)).join("\n");
      const command = body.match(/(?:^|[.!]\s+|\n)((?:Qual|Quais|Que|Como|Assinale|Identifique|Explique|Analise|Calcule|Compare|Justifique|Proponha|Determine)\b[^\n]+)$/i)?.[1] || "";
      const context = command ? body.slice(0, body.lastIndexOf(command)) : body;
      const content = normalize(`${type} ${command}`);
      const family = /calcul|quantitativ|valor|quantidade/.test(content) ? "cálculo com dados suficientes"
        : /sequencia|orden|etapas/.test(content) ? "sequência de procedimentos"
        : /decis|proponha|medida|estrategia|acao|mais apropriad/.test(content) ? "decisão fundamentada"
        : /compar|diferenc|distin/.test(content) ? "comparação por critérios"
        : /porque|razao|justifique|causa/.test(content) ? "relação e justificativa" : "interpretação aplicada";
      return { assessment: canonical?.[2] || source.match(/\b(AD|AI|PS|P1|P2|P3|SCH)\b/)?.[1] || "Não informado",
        difficulty: clean(canonical?.[5] || block.match(/N[ií]vel(?:\s+de\s+complexidade)?\s*:?\s*(F[aá]cil|M[eé]di[oa]|Dif[ií]cil)/i)?.[1]),
        type, objective, alternativeCount: new Set(alternatives.map(m => m[1].toUpperCase())).size,
        contextWords: wordCount(context), commandFamily: family };
    });
    const countBy = key => questions.reduce((a, q) => { const k = q[key] || "Não informado"; a[k] = (a[k] || 0) + 1; return a; }, {});
    const contexts = questions.map(q => q.contextWords).filter(Boolean);
    return { questionCount: questions.length, assessments: countBy("assessment"), difficulties: countBy("difficulty"), types: countBy("type"), commandFamilies: countBy("commandFamily"),
      averageContextWords: contexts.length ? Math.round(contexts.reduce((a,b) => a+b, 0) / contexts.length) : 0,
      contextRange: contexts.length ? [Math.min(...contexts), Math.max(...contexts)] : [0, 0],
      contextualModels: contexts.filter(n => n >= PEDAGOGICAL_PROFILE.minimumCaseWords).length,
      fourAlternativeCompliance: questions.length ? Math.round(100 * questions.filter(q => q.alternativeCount === 4).length / questions.length) : 0,
      objectiveLinkCompliance: questions.length ? Math.round(100 * questions.filter(q => q.objective.length >= 20).length / questions.length) : 0 };
  }

  function wordCount(text) { return clean(text).split(/\s+/).filter(Boolean).length; }
  function sentences(text) { return clean(text).split(/(?<=[.!?])\s+(?=[A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇ0-9])/u).map(clean).filter(Boolean); }
  function definitionParts(text) {
    return text.match(/^(.{3,105}?)\s+(?:é|são|constitui(?:-se)?|representa|corresponde\s+a|refere-se\s+a|caracteriza-se\s+por|consiste\s+em)\s+(.{20,360}?)[.!]?$/i)
      || text.match(/^([^:]{3,80}):\s*(.{28,360})[.!]?$/);
  }

  function safeConcept(value) {
    const concept = clean(String(value || "").replace(/^(?:o|a|os|as|um|uma)\s+/i, "").replace(/[.:;]+$/, ""));
    const words = concept.split(/\s+/).filter(Boolean);
    if (concept.length < 3 || concept.length > 85 || words.length > 9) return "";
    if (DANGLING_START.test(concept) || DANGLING_END.test(concept)) return "";
    if (FORBIDDEN_OUTPUT.test(concept) || BIBLIOGRAPHIC_PATTERN.test(concept) || AUTHOR_RECORD_PATTERN.test(concept) || /\d{4}/.test(concept)) return "";
    if (/[,;]$/.test(concept) || /\b(?:ele|ela|eles|elas|isso|isto|aquele|aquela)\b/i.test(concept)) return "";
    return concept.charAt(0).toLocaleUpperCase("pt-BR") + concept.slice(1);
  }

  function safeDefinition(value) {
    const definition = stripInlineCitations(clean(value).replace(/[.;:]+$/, ""));
    const words = definition.split(/\s+/).filter(Boolean);
    if (definition.length < 28 || definition.length > 360 || words.length < 6 || words.length > 58) return "";
    if (FORBIDDEN_OUTPUT.test(definition) || SOURCE_NOTE_PATTERN.test(definition) || BIBLIOGRAPHIC_PATTERN.test(definition) || AUTHOR_RECORD_PATTERN.test(definition)) return "";
    if (DANGLING_START.test(definition) || DANGLING_END.test(definition)) return "";
    if (/\b(?:figura|quadro|tabela|cap[ií]tulo|p[aá]gina)\s+\d+/i.test(definition)) return "";
    if (/\[[^\]]*$|^[^\[]*\]/.test(definition)) return "";
    return definition;
  }

  function extractFacts(acceptedLines, assignedUa) {
    const facts = [], rejected = [];
    let activeUa = Number(assignedUa || 0) || null, lastFact = null, currentExample = null, previousLine = 0;
    const exampleMarker = /(?:^|(?<=[.!?])\s+)(?:por exemplo|exemplo(?:\s+de\s+aplica[cç][aã]o)?|na pr[aá]tica|estudo de caso|situa[cç][aã]o-problema)\s*[:,–-]?\s*/i;
    const addDefinitions = (text, line) => {
      for (const sentence of sentences(text)) {
        const parts = definitionParts(sentence);
        if (!parts) continue;
        const concept = safeConcept(parts[1]), definition = safeDefinition(parts[2]);
        if (!concept || !definition || auditStudentText(sentence).length) continue;
        lastFact = { id: `fact-${fnv1a(`${concept}:${definition}:${activeUa || 0}`)}`, concept, definition,
          sentence, sourceText: sentence, sourceLine: line, ua: activeUa, kind: "definition", quality: 94, examples: [] };
        facts.push(lastFact);
      }
    };
    for (const entry of acceptedLines) {
      const gap = previousLine && entry.line > previousLine + 1;
      previousLine = entry.line;
      if (gap) { if (currentExample) currentExample.incomplete = true; currentExample = null; lastFact = null; }
      const heading = entry.text.match(/^(?:unidade(?:\s+de\s+aprendizagem)?\s*(?:UA\s*)?|UA\s*)0?(\d{1,2})\b/i);
      if (heading) { activeUa = Number(heading[1]); lastFact = null; currentExample = null; continue; }
      // Resolutions remain teacher evidence, separate from the student-facing case.
      const solution = entry.text.match(/^(Solu[cç][aã]o(?:\s+fundamentada)?|Decis[aã]o(?:\s+fundamentada)?|Conclus[aã]o|Justificativa|Crit[eé]rios?\s+de\s+decis[aã]o|Op[cç][aã]o\s+descartada\s*[1-3])\s*:\s*(.+)$/i);
      if (currentExample && solution) {
        const key = normalize(solution[1]);
        if (key.startsWith("opcao")) {
          const pair = solution[2].split(/\s+\|\s+/);
          if (pair.length === 2) currentExample.rejectedOptions.push({ text: clean(pair[0]), reason: clean(pair[1]), line: entry.line });
          else currentExample.incomplete = true;
        } else if (key.startsWith("justificativa")) currentExample.rationale = clean(solution[2]);
        else if (key.startsWith("criterio")) currentExample.criteria = solution[2].split(/\s*;\s*/).map(clean).filter(Boolean);
        else currentExample.resolution = clean(solution[2]);
        currentExample.endLine = entry.line;
        continue;
      }
      const marker = entry.text.match(exampleMarker);
      if (marker) {
        currentExample = null;
        if (marker.index) addDefinitions(entry.text.slice(0, marker.index), entry.line);
        if (lastFact && entry.line - (lastFact.examples.at(-1)?.endLine || lastFact.sourceLine) <= 2) {
          currentExample = { text: clean(entry.text.slice(marker.index + marker[0].length)), line: entry.line, endLine: entry.line, rejectedOptions: [], criteria: [] };
          lastFact.examples.push(currentExample);
        }
        continue;
      }
      const startsDefinition = definitionParts(sentences(entry.text)[0] || "");
      if (currentExample && !startsDefinition && !SECTION_HEADINGS.test(entry.text) && !/^(?:disciplina|objetivo|atividade|exerc[ií]cio|resumo)\b/i.test(entry.text)) {
        if (currentExample.resolution) { currentExample = null; lastFact = null; }
        else { currentExample.text = clean(currentExample.text + "\n" + entry.text); currentExample.endLine = entry.line; continue; }
      }
      currentExample = null;
      lastFact = null;
      addDefinitions(entry.text, entry.line);
    }
    const byKey = new Map();
    for (const fact of facts) {
      for (const example of fact.examples) {
        const issues = caseIssues(example);
        example.issues = issues;
        if (issues.length) rejected.push({ line: example.line, reason: issues.join("; "), text: example.text.slice(0, 240) });
      }
      const key = normalize(`${fact.ua}:${fact.concept}:${fact.definition}`);
      if (byKey.has(key)) byKey.get(key).examples.push(...fact.examples);
      else byKey.set(key, fact);
    }
    return { facts: [...byKey.values()], rejected };
  }

  function caseIssues(example) {
    const text = clean(example?.text), issues = auditStudentText(text), n = wordCount(text);
    if (example?.incomplete) issues.push("há trecho omitido ou resolução incompleta no caso");
    if (n < PEDAGOGICAL_PROFILE.minimumCaseWords) issues.push("o exemplo não apresenta contexto desenvolvido (mínimo de 60 palavras)");
    if (n > PEDAGOGICAL_PROFILE.maximumCaseWords) issues.push("o caso excede 260 palavras; delimite o caso sem cortar suas condições");
    if (sentences(text).length < 3 || !/[.!]$/.test(text) || DANGLING_END.test(text.replace(/[.!]$/, ""))) issues.push("o caso precisa de frases completas e conclusão textual");
    if (DANGLING_START.test(text) || /^(?:esse|essa|esses|essas|nesse|nessa|tal|tais)\b/i.test(text)) issues.push("a abertura depende de informação externa");
    if (/\b(?:figura|quadro|tabela|p[aá]gina|caso|exemplo)\s+(?:\d+|anterior|acima|abaixo)|\b(?:como vimos|j[aá] mencionado|anteriormente citado)\b/i.test(text)) issues.push("o caso depende de elemento que não acompanha a questão");
    if (/\b(?:gabarito|alternativa correta|resposta correta)\b/i.test(text)) issues.push("o caso contém a resposta da atividade");
    return unique(issues);
  }

  function analyzeDocument(input) {
    const name = String(input?.name || "material");
    const text = repairWordBreaks(input?.text || "");
    const metadata = input?.metadata && typeof input.metadata === "object" ? input.metadata : {};
    const curated = curateLines(text);
    const roleInfo = classifyRole(text, name, metadata.role || ROLES.AUTO);
    const internalSubject = subjectFromText(curated.lines);
    const filenameSubject = inferSubjectFromName(name);
    const syllabus = sectionValue(curated.lines, /^ementa\s*:\s*/i, [/^objetivo\s+geral\s*:/i]);
    const manualSubject = clean(metadata.subject || "");
    const nameInternal = similarity(filenameSubject, internalSubject);
    const nameSyllabus = similarity(filenameSubject, syllabus);
    const internalSyllabus = similarity(internalSubject, syllabus);
    const metadataConflict = Boolean(filenameSubject && internalSubject && nameInternal < 0.25 && Math.max(nameSyllabus, internalSyllabus) >= 0.16);
    const subject = manualSubject || internalSubject || filenameSubject;
    const subjectSource = manualSubject ? "manual" : internalSubject ? "internal" : "filename";
    const subjectStatus = metadataConflict && !manualSubject ? "conflict" : subject ? (manualSubject ? "confirmed" : "detected") : "missing";
    const curriculum = roleInfo.role === ROLES.TEACHING_PLAN ? extractCurriculum(curated.lines, subject) : { subject, syllabus: "", generalObjective: "", specificObjectives: [], uas: [], completeness: 0 };
    const blueprint = roleInfo.role === ROLES.ASSESSMENT_MODEL ? extractAssessmentBlueprint(text) : { questionCount: 0, assessments: {}, difficulties: {}, types: {}, commandFamilies: {}, averageContextWords: 0, contextRange: [0, 0], fourAlternativeCompliance: 0, objectiveLinkCompliance: 0 };
    const evidenceAccepted = roleInfo.role === ROLES.REFERENCE ? curated.accepted : [];
    const factResult = roleInfo.role === ROLES.REFERENCE ? extractFacts(evidenceAccepted, metadata.assignedUa) : { facts: [], rejected: [] };
    const warnings = [...roleInfo.warnings];
    if (metadataConflict) warnings.push(`Conflito de disciplina: o nome sugere “${filenameSubject}”, mas o documento identifica “${internalSubject}”. Confirme a classificação antes de usar.`);
    if (roleInfo.role === ROLES.TEACHING_PLAN && curriculum.specificObjectives.length < 1) warnings.push("O plano não contém objetivos específicos utilizáveis.");
    if (roleInfo.role === ROLES.TEACHING_PLAN && !curriculum.uas.length) warnings.push("O plano não contém uma matriz de UAs reconhecível.");
    if (roleInfo.role === ROLES.ASSESSMENT_MODEL && blueprint.questionCount < 1) warnings.push("Nenhuma questão-modelo estruturada foi reconhecida.");
    if (roleInfo.role === ROLES.REFERENCE && !evidenceAccepted.length) warnings.push("O material não contém conteúdo textual extraível. Confira o arquivo.");
    const blockingIssues = [];
    if (subjectStatus === "conflict") blockingIssues.push("disciplina interna divergente do nome do arquivo");
    if (subjectStatus === "missing") blockingIssues.push("disciplina não identificada");
    if (roleInfo.role === ROLES.TEACHING_PLAN && (!curriculum.generalObjective || !curriculum.specificObjectives.length)) blockingIssues.push("plano sem objetivos suficientes");
    const totalLines = curated.lines.length;
    const quality = Math.max(0, Math.min(100, 100 - blockingIssues.length * 28 - Math.min(28, Math.round((curated.quarantined.length / Math.max(1, totalLines)) * 55))));
    return {
      version: VERSION,
      revision: ANALYSIS_REVISION,
      role: roleInfo.role,
      roleLabel: ROLE_LABELS[roleInfo.role],
      roleConfidence: Math.round(roleInfo.confidence * 100),
      roleSource: roleInfo.requestedRole === ROLES.AUTO ? "detected" : "manual",
      detectedRole: roleInfo.detectedRole,
      requestedRole: roleInfo.requestedRole,
      roleScores: roleInfo.scores,
      subject,
      internalSubject,
      filenameSubject,
      subjectSource,
      subjectStatus,
      metadataConflict,
      curriculum,
      blueprint,
      evidence: {
        eligible: roleInfo.role === ROLES.REFERENCE && subjectStatus !== "conflict",
        cleanText: evidenceAccepted.map((entry) => entry.text).join("\n"),
        acceptedLines: evidenceAccepted.length,
        facts: factResult.facts,
        rejectedFacts: factResult.rejected.slice(0, 250)
      },
      quarantine: {
        count: curated.quarantined.length,
        reasonCounts: curated.reasonCounts,
        examples: curated.quarantined.slice(0, 18)
      },
      sections: curated.sections,
      warnings,
      blockingIssues,
      quality,
      usable: !blockingIssues.length
    };
  }

  function subjectMatch(value, theme) {
    if (!clean(theme)) return 1;
    return similarity(value, theme);
  }

  function compatibleDocuments(base, role, theme) {
    return (base?.documents || []).filter((document) => {
      const analysis = document.analysis || analyzeDocument({ name: document.name, text: document.text, metadata: { role: document.role, subject: document.subject, assignedUa: document.assignedUa } });
      return analysis.role === role && analysis.usable && subjectMatch(document.subject || analysis.subject, theme) >= 0.25;
    });
  }

  function curriculumAlignment(base, theme, ua, fact) {
    const plans = compatibleDocuments(base, ROLES.TEACHING_PLAN, theme);
    const ranked = plans.map((document) => {
      const curriculum = document.analysis.curriculum;
      const uaEntry = curriculum.uas.find((entry) => Number(entry.number) === Number(ua)) || null;
      const context = `${fact?.concept || ""} ${fact?.definition || ""}`;
      const objectives = curriculum.specificObjectives.map((objective) => ({ ...objective, score: semanticSimilarity(objective.text, context) }));
      objectives.sort((left, right) => right.score - left.score || left.id - right.id);
      const objective = objectives.find((entry) => entry.score >= 0.09) || null;
      const score = subjectMatch(document.subject, theme) * 0.55 + Math.min(1, (objective?.score || 0) * 2) * 0.3 + (uaEntry ? 0.15 : 0);
      return { document, curriculum, uaEntry, objective, score };
    }).sort((left, right) => right.score - left.score);
    const best = ranked.find((entry) => entry.objective) || null;
    if (!best?.objective) return null;
    return {
      planDocumentId: best.document.id,
      planDocumentName: best.document.name,
      objectiveNumber: best.objective.id,
      objective: best.objective.text,
      objectiveSimilarity: Math.round(best.objective.score * 100),
      ua: best.uaEntry,
      score: Math.round(best.score * 100)
    };
  }

  function aggregateBlueprint(base, theme, evaluation) {
    const models = compatibleDocuments(base, ROLES.ASSESSMENT_MODEL, theme);
    const matching = models.filter((document) => {
      const assessments = document.analysis.blueprint.assessments || {};
      return !evaluation || assessments[evaluation] || !Object.keys(assessments).length;
    });
    const all = matching.length ? matching : models;
    if (!all.length) return { available: false, documents: 0, questionCount: 0, averageContextWords: 0, commandFamilies: {}, types: {} };
    const mergeCounts = (key) => all.reduce((result, document) => {
      Object.entries(document.analysis.blueprint[key] || {}).forEach(([label, count]) => { result[label] = (result[label] || 0) + count; });
      return result;
    }, {});
    const totalQuestions = all.reduce((sum, document) => sum + Number(document.analysis.blueprint.questionCount || 0), 0);
    return {
      available: true,
      documents: all.length,
      documentNames: all.map((document) => document.name),
      questionCount: totalQuestions,
      averageContextWords: totalQuestions ? Math.round(all.reduce((sum, document) => sum + Number(document.analysis.blueprint.averageContextWords || 0) * Number(document.analysis.blueprint.questionCount || 0), 0) / totalQuestions) : 0,
      commandFamilies: mergeCounts("commandFamilies"),
      types: mergeCounts("types")
    };
  }

  // Conservative lexical affinity. This is a local rule engine, not a language model.
  function semanticTerms(value) {
    return new Set(tokens(value).filter((word) => !/^(identificar|analisar|compreender|aplicar|comparar|reconhecer|conceito|conceitos|elementos|situacao|situacoes|processo|processos)$/.test(word))
      .map((word) => word.replace(/coes$/, "cao").replace(/ais$/, "al").replace(/(?:os|as)$/, "o").replace(/s$/, "").replace(/([a-z]{5,})[ao]$/, "$1")));
  }

  function semanticSimilarity(left, right) {
    const a = semanticTerms(left);
    const b = semanticTerms(right);
    if (!a.size || !b.size) return 0;
    return [...a].filter((term) => b.has(term)).length / Math.min(a.size, b.size);
  }

  function auditStudentText(text) {
    const value = clean(text);
    const issues = [];
    if (FORBIDDEN_OUTPUT.test(value)) issues.push("contém URL, referência, lacuna ou truncamento");
    if (FORBIDDEN_SOURCE_REFERENCE.test(value)) issues.push("menciona o arquivo ou material de origem");
    if (BIBLIOGRAPHIC_PATTERN.test(value) || AUTHOR_RECORD_PATTERN.test(value)) issues.push("contém padrão bibliográfico ou nome de autoria");
    if (/([A-Za-zÀ-ÿ]{3,})-\s+([a-zà-ÿ]{2,})/.test(value)) issues.push("contém palavra quebrada por hifenização");
    if (/\[[^\]]*$|^[^\[]*\]/.test(value) || /\([^)]*$|^[^(]*\)/.test(value)) issues.push("contém delimitador incompleto");
    return unique(issues);
  }

  function auditDraft() {
    return {ready:false, manualReviewRequired:true, score:0, checks:[], blockers:["A qualidade pedagógica exige revisão do professor."]};
  }

  function failure(message, rules, extra) {
    return {
      questions: [], requested: rules.totalCount || rules.count, produced: 0, rejected: [{ source: "Curadoria premium", reason: message, sentence: "" }],
      rules, status: "insufficient", manualReviewRequired: true, coverage: { requestedByUa: {}, producedByUa: {}, missingUas: rules.allowedUas || [] },
      pipeline: { version: VERSION, candidatesConsidered: 0, candidatesApproved: 0, candidatesRejected: 0, ...extra }, message
    };
  }

  function generateQuestionSet(base, rules, options) {
    if (root.SmartFoxLocalQuestionGenerator) return root.SmartFoxLocalQuestionGenerator.generate(base, rules, options || {});
    return { ...failure("O módulo de criação local não foi carregado. Atualize a extensão e recarregue a aba do AvaliA.", rules), status: "unavailable" };
  }

  function baseAudit(base) {
    const documents = base?.documents || [];
    const counts = Object.fromEntries(Object.values(ROLES).filter((role) => role !== ROLES.AUTO).map((role) => [role, documents.filter((document) => (document.role || document.analysis?.role) === role).length]));
    const conflicts = documents.filter((document) => document.analysis?.subjectStatus === "conflict");
    const quarantineCount = documents.reduce((sum, document) => sum + Number(document.analysis?.quarantine?.count || 0), 0);
    const objectives = documents.reduce((sum, document) => sum + Number(document.analysis?.curriculum?.specificObjectives?.length || 0), 0);
    const uas = documents.reduce((sum, document) => sum + Number(document.analysis?.curriculum?.uas?.length || 0), 0);
    const modelQuestions = documents.reduce((sum, document) => sum + Number(document.analysis?.blueprint?.questionCount || 0), 0);
    const safeFacts = documents.reduce((sum, document) => sum + Number(document.analysis?.evidence?.facts?.length || 0), 0);
    return { documents: documents.length, counts, conflicts: conflicts.map((document) => ({ id: document.id, name: document.name, warning: document.analysis.warnings.find((warning) => /Conflito de disciplina/i.test(warning)) || "Conflito de disciplina" })), quarantineCount, objectives, uas, modelQuestions, safeFacts };
  }

  root.AvaliaPremiumCurator = Object.freeze({
    version: VERSION,
    analysisRevision: ANALYSIS_REVISION,
    pedagogicalProfile: PEDAGOGICAL_PROFILE,
    caseIssues,
    roles: ROLES,
    roleLabels: ROLE_LABELS,
    normalize,
    clean,
    repairWordBreaks,
    inferSubjectFromName,
    classifyRole,
    curateLines,
    extractCurriculum,
    extractAssessmentBlueprint,
    extractFacts,
    analyzeDocument,
    auditStudentText,
    auditDraft,
    curriculumAlignment,
    aggregateBlueprint,
    generateQuestionSet,
    baseAudit,
    isEvidenceDocument(document) { return (document?.role || document?.analysis?.role) === ROLES.REFERENCE && document?.analysis?.evidence?.eligible !== false; }
  });
})(typeof window !== "undefined" ? window : globalThis);
