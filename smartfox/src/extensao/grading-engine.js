(function (root, factory) {
  "use strict";

  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.SmartFoxGradingEngine = api;
})(typeof window !== "undefined" ? window : globalThis, function () {
  "use strict";

  const ENGINE_VERSION = "2.0.0";
  const DEFAULT_POLICY = Object.freeze({
    id: "teacher-rubric", label: "Correção por critérios definidos pelo professor",
    requireTeacherApproval: true, automaticGrades: false
  });

  const STOPWORDS = new Set([
    "a", "ao", "aos", "aquela", "aquelas", "aquele", "aqueles", "aquilo", "as", "ate",
    "com", "como", "da", "das", "de", "dela", "dele", "deles", "do", "dos", "e", "ela",
    "elas", "ele", "eles", "em", "entre", "era", "essa", "essas", "esse", "esses", "esta",
    "estas", "este", "estes", "foi", "for", "ha", "isso", "isto", "ja", "lhe", "lhes", "mais",
    "mas", "me", "mesmo", "na", "nas", "nao", "nem", "no", "nos", "nossa", "nosso", "num",
    "numa", "o", "os", "ou", "para", "pela", "pelas", "pelo", "pelos", "por", "porque", "qual",
    "quais", "que", "quem", "se", "sem", "ser", "seu", "seus", "sua", "suas", "tambem", "tem",
    "ter", "um", "uma", "umas", "uns", "sao", "sobre", "quando", "onde", "deve", "podem", "pode",
    "texto", "questao", "resposta", "acordo", "base", "partir"
  ]);

  const DIRECT_NON_ANSWERS = [
    /^n[ãa]o\s+sei(?:\s+responder)?$/,
    /^n[ãa]o\s+lembro$/,
    /^n[ãa]o\s+respondi(?:do)?$/,
    /^sem\s+resposta$/,
    /^resposta\s+em\s+branco$/,
    /^n[ãa]o\s+tenho\s+resposta$/,
    /^n[ãa]o\s+consegui(?:\s+responder)?$/,
    /^n[ãa]o\s+entendi(?:\s+a\s+quest[ãa]o)?$/,
    /^n[\/.]?a$/,
    /^s[\/.]?r$/,
    /^sei\s+l[áa]$/,
    /^teste$/,
    /^oi$/,
    /^bom\s+dia$/,
    /^boa\s+(?:tarde|noite)$/
  ];

  function htmlToText(value) {
    const source = String(value == null ? "" : value);
    if (!source) return "";
    if (typeof DOMParser !== "undefined") {
      try {
        const parsed = new DOMParser().parseFromString(source, "text/html");
        return (parsed.body?.textContent || "").replace(/\u00a0/g, " ").replace(/\s+/g, " ").trim();
      } catch (_) {}
    }
    return source
      .replace(/<br\s*\/?\s*>/gi, " ")
      .replace(/<[^>]+>/g, " ")
      .replace(/&nbsp;|&#160;/gi, " ")
      .replace(/&amp;/gi, "&")
      .replace(/&lt;/gi, "<")
      .replace(/&gt;/gi, ">")
      .replace(/&quot;/gi, '"')
      .replace(/&#39;|&apos;/gi, "'")
      .replace(/\s+/g, " ")
      .trim();
  }

  function normalize(value) {
    return htmlToText(value)
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[–—]/g, "-")
      .replace(/[^a-zA-Z0-9%+\-/\s]/g, " ")
      .replace(/\s+/g, " ")
      .trim()
      .toLowerCase();
  }

  function parseScore(value) {
    if (typeof value === "number") return Number.isFinite(value) && value >= 0 ? value : null;
    const cleaned = String(value == null ? "" : value).trim();
    if (!/^(?:\d+(?:[.,]\d+)?|[.,]\d+)$/.test(cleaned)) return null;
    if (!cleaned) return null;
    let normalized = cleaned;
    if (cleaned.includes(",") && cleaned.includes(".")) {
      normalized = cleaned.lastIndexOf(",") > cleaned.lastIndexOf(".")
        ? cleaned.replace(/\./g, "").replace(",", ".")
        : cleaned.replace(/,/g, "");
    } else if (cleaned.includes(",")) {
      normalized = cleaned.replace(",", ".");
    }
    const number = Number(normalized);
    return Number.isFinite(number) && number >= 0 ? number : null;
  }

  function decimalPlaces(value) {
    const source = String(value == null ? "" : value);
    const separator = Math.max(source.lastIndexOf("."), source.lastIndexOf(","));
    return separator < 0 ? 0 : Math.min(6, source.length - separator - 1);
  }

  function scoreForInput(value, step) {
    const number = parseScore(value);
    if (number == null) return "";
    const places = Math.max(decimalPlaces(step), 0);
    return places ? number.toFixed(places) : String(number);
  }

  function formatScore(value, decimals) {
    const number = parseScore(value);
    if (number == null) return "—";
    const places = Number.isInteger(decimals) ? decimals : Math.max(3, decimalPlaces(value));
    return number.toLocaleString("pt-BR", { minimumFractionDigits: places, maximumFractionDigits: places });
  }

  function tokens(value, options) {
    const opts = options || {};
    return normalize(value)
      .split(/\s+/)
      .map((token) => token.replace(/^[-/+]+|[-/+]+$/g, ""))
      .filter((token) => token && /[a-z0-9]/.test(token))
      .filter((token) => opts.keepStopwords || !STOPWORDS.has(token))
      .filter((token) => opts.keepShort || token.length >= 3 || /^\d+$/.test(token));
  }

  function stemKey(token) {
    const word = String(token || "");
    if (word.length <= 5) return word;
    return word
      .replace(/(?:amentos|imentos|adoras|adores|acoes|mente)$/i, "")
      .replace(/(?:amento|imento|adora|ador|acao|idades|idade)$/i, "")
      .replace(/(?:ando|endo|indo|ados|adas|idos|idas)$/i, "")
      .replace(/(?:oes|aes|ais|eis|res|ses|s)$/i, "")
      .slice(0, 9);
  }

  function tokensMatch(left, right) {
    if (!left || !right) return false;
    if (left === right) return true;
    const a = stemKey(left);
    const b = stemKey(right);
    if (a.length >= 4 && b.length >= 4 && a === b) return true;
    const prefix = Math.min(a.length, b.length, 6);
    return prefix >= 5 && a.slice(0, prefix) === b.slice(0, prefix);
  }

  function unique(values) {
    return Array.from(new Set(values));
  }

  function directNonAnswer(text) {
    const value = htmlToText(text).replace(/[.!?…]+$/g, "").trim();
    return DIRECT_NON_ANSWERS.some((pattern) => pattern.test(value.toLowerCase()));
  }

  function gibberishSignals(text) {
    const raw = htmlToText(text);
    const normalized = normalize(raw);
    const allTokens = tokens(normalized, { keepStopwords: true, keepShort: true });
    const letters = (normalized.match(/[a-z]/g) || []).length;
    const digits = (normalized.match(/[0-9]/g) || []).length;
    const meaningful = allTokens.filter((token) => /[aeiou]/.test(token) || /^\d+$/.test(token));
    const repeated = /([a-z])\1{4,}/i.test(normalized);
    const keyboard = /\b(?:asdfg?|qwerty?|zxcv|hjkl|abcde|12345)\b/i.test(normalized);
    const uniqueRatio = allTokens.length ? unique(allTokens).length / allTokens.length : 0;
    const symbolOnly = raw.trim() !== "" && letters + digits === 0;
    const oneNoiseToken = allTokens.length === 1 && allTokens[0].length <= 2;
    const vowelPoor = letters >= 5 && meaningful.length === 0;
    const repeatedNoise = allTokens.length >= 4 && uniqueRatio <= 0.25;
    return {
      isGibberish: symbolOnly || oneNoiseToken || repeated || keyboard || vowelPoor || repeatedNoise,
      symbolOnly,
      oneNoiseToken,
      repeated,
      keyboard,
      vowelPoor,
      repeatedNoise,
      uniqueRatio
    };
  }

  function overlapMetrics(responseText, referenceText) {
    const responseTokens = unique(tokens(responseText));
    const referenceTokens = unique(tokens(referenceText));
    const matches = responseTokens.filter((candidate) => referenceTokens.some((reference) => tokensMatch(candidate, reference)));
    return {
      responseTokens,
      referenceTokens,
      matches,
      matchedCount: matches.length,
      responseCoverage: responseTokens.length ? matches.length / responseTokens.length : 0,
      referenceCoverage: referenceTokens.length ? matches.length / referenceTokens.length : 0
    };
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

  function analyzeResponse(input) {
    const data = input || {};
    const policy = { ...DEFAULT_POLICY, ...(data.policy || {}) };
    const questionText = htmlToText(data.questionText || data.questionHtml);
    const responseText = htmlToText(data.responseText || data.responseHtml);
    const expectedText = htmlToText(data.expectedText || data.expectedHtml);
    const maxScore = parseScore(data.maxScore);
    const rawResponse = responseText.trim();
    const normalizedResponse = normalize(rawResponse);
    const wordList = tokens(rawResponse, { keepStopwords: true, keepShort: true });
    const contentWords = tokens(rawResponse);
    const referenceText = `${questionText} ${expectedText}`.trim();
    const overlap = overlapMetrics(rawResponse, referenceText);
    const noise = gibberishSignals(rawResponse);
    const hasAnswer = Boolean(normalizedResponse);
    const isDirectNonAnswer = hasAnswer && directNonAnswer(rawResponse);
    const exactExpected = Boolean(expectedText && normalize(expectedText) === normalizedResponse);

    const reasonCode=!rawResponse?'TEXTO_AUSENTE':exactExpected?'TEXTO_IGUAL_AO_PADRAO':overlap.matchedCount?'TERMOS_EM_COMUM':'REVISAO_DOCENTE';
    const reason=!rawResponse?'Confira se existe resposta visual ou anexo.':'Avalie os conceitos, a justificativa e o atendimento ao comando.';
    return {
      engineVersion: ENGINE_VERSION, policy: DEFAULT_POLICY,
      decision: "review", reasonCode, reason,
      hasAnswer: Boolean(rawResponse), contextualRelation: null,
      isDirectNonAnswer, isGibberish: noise.isGibberish, exactExpected, maxScore,
      suggestedScore: null, fullCreditByPolicy: false,
      requiresTeacherReview: true, canApplyAutomatically: false,
      metrics: {characterCount:rawResponse.length,wordCount:wordList.length,
        matchedTerms:overlap.matches,matchedCount:overlap.matchedCount},
      responseFingerprint: fnv1a(normalizedResponse),
      referenceFingerprint: fnv1a(normalize(referenceText)),
      explanation: !rawResponse ? "Nenhum texto de resposta identificado. Confira se há imagem ou anexo antes de atribuir a nota."
        : "A comparação identifica palavras em comum; a correção e a pontuação dependem da revisão docente."
    };
  }

  function rubricScore(criteria,maxScore,step='0.001') {
    const maximum=parseScore(maxScore),increment=step==='any'?0.001:parseScore(step);
    if(maximum==null||maximum<=0||increment==null||increment<=0)throw new Error('Peso máximo ou precisão da nota inválidos.');
    if(!Array.isArray(criteria)||!criteria.length)throw new Error('Defina os critérios de correção.');
    let total=0,earned=0;
    for(const c of criteria){
      const weight=parseScore(c.weight),attainment=parseScore(c.attainment);
      if(!String(c.label||'').trim()||weight==null||weight<=0||attainment==null||attainment>1)throw new Error('Preencha o nome, peso e atendimento de todos os critérios.');
      total+=weight;earned+=weight*attainment;
    }
    if(Math.abs(total-100)>1e-7)throw new Error('Os pesos dos critérios precisam somar 100%.');
    const raw=maximum*earned/100;
    const units=Math.min(Math.round(raw/increment),Math.floor((maximum+1e-10)/increment));
    return Number((units*increment).toFixed(Math.min(6,Math.max(decimalPlaces(step),3))));
  }

  function validateTeacherScore(value,maximum,step='0.001') {
    const score=parseScore(value),max=parseScore(maximum),increment=step==='any'?null:parseScore(step);
    if(score==null||max==null||max<=0||score>max)throw new Error('Informe uma nota válida entre zero e o peso máximo.');
    if(step!=='any'&&(increment==null||increment<=0||Math.abs(score/increment-Math.round(score/increment))>1e-7))throw new Error('A nota não respeita a precisão permitida pelo AvaliA.');
    return score;
  }

  return Object.freeze({
    rubricScore, validateTeacherScore,
    ENGINE_VERSION,
    DEFAULT_POLICY,
    htmlToText,
    normalize,
    parseScore,
    scoreForInput,
    formatScore,
    tokens,
    overlapMetrics,
    gibberishSignals,
    analyzeResponse,
    fnv1a
  });
});
