(function (root) {
  "use strict";

  const VERSION = "11.0.0";
  const SCHEMA_VERSION = 4;
  const INDEX_VERSION = 3;
  const MAX_FILE_BYTES = 35 * 1024 * 1024;
  const MAX_TEXT_CHARS = 4_000_000;
  const MAX_DOCUMENTS = 250;
  const MAX_BASE_TEXT_CHARS = 50_000_000;
  const CHUNK_TARGET = 1250;
  const CHUNK_OVERLAP = 180;
  const SUPPORTED_EXTENSIONS = Object.freeze(["docx", "pdf", "pptx", "txt", "md", "html", "htm", "csv"]);
  const COLLECTION_EVALUATIONS = Object.freeze(["GENERAL", "AD", "AI", "PS", "P1", "P2", "SCH", "P3"]);
  const DEFAULT_COLLECTION_ID = "collection-general";
  const DEFAULT_ATHUS_RULES = `Projeto Athus — padrão acadêmico próximo ao ENADE, em português do Brasil.
Usar exclusivamente informações contempladas nas fontes; não inventar conteúdo externo.
AD: 10 objetivas, somente UA1 a UA5. AI e PS: 5 objetivas. P1: 16 objetivas e 2 discursivas, ou 10 objetivas e 2 discursivas quando selecionado. P2, SCH e P3: 18.
Dificuldade: 40% fáceis, 40% médias e 20% difíceis.
Identificação: Questão (x)_AVALIAÇÃO_UA (x)_Obj (x)_nível.
Cada objetiva deve ter Tema Gerador, objetivo coerente, habilidade, contextualização de no mínimo 15 linhas no Word padrão, também para discursivas, comando direto, exatamente A–D, uma correta e feedback de 1 a 6 linhas.
Distratores devem ser plausíveis, próximos ao problema e equilibrados em tamanho. Proibidos NRA, nenhuma das anteriores e todas corretas/erradas.
Evitar pegadinhas, ambiguidades, dupla negação, linguagem artificial e dificuldade por texto desnecessário.
Nunca mencionar material, PDF, arquivo, documento ou nome da fonte no texto destinado ao estudante.
Nunca antecipar no enunciado o conceito correto nem usar URL, autoria, referência bibliográfica, QR Code, DOI ou fragmento editorial como alternativa.
Conferir a relação conteúdo → objetivo → habilidade → situação → comando → resposta → feedback antes de liberar.`;
  const STOP_WORDS = new Set((
    "a o as os um uma uns umas de da do das dos em no na nos nas por para com sem sobre entre e ou que qual quais " +
    "como quando onde porque pois se sua seu suas seus este esta estes estas isso isto aquele aquela ao aos à às " +
    "ser estar ter foi são é era foram pode podem deve devem questão alternativa resposta assinale considere analise"
  ).split(/\s+/));
  const FORBIDDEN_STUDENT_REFERENCE = /\b(?:material\s+estudado|conteudo\s+estudado|conforme\s+o\s+material|de\s+acordo\s+com\s+o\s+arquivo|segundo\s+o\s+pdf|na\s+ua\s+enviada|conforme\s+o\s+documento|neste\s+material|neste\s+arquivo|neste\s+documento)\b/i;
  const corpusCache = new WeakMap();
  const statsCache = new WeakMap();
  const hydratedBases = new WeakSet();

  function normalize(value) {
    return String(value == null ? "" : value)
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[\u00ad\u200b-\u200d\ufeff]/g, "")
      .replace(/[^a-zA-Z0-9À-ÿ%+\-–—=<>²³⁰¹⁴⁵⁶⁷⁸⁹\s]/g, " ")
      .replace(/\s+/g, " ")
      .trim()
      .toLocaleLowerCase("pt-BR");
  }

  function cleanText(value) {
    return String(value == null ? "" : value)
      .replace(/\r\n?/g, "\n")
      .replace(/[\u00ad\u200b-\u200d\ufeff]/g, "")
      .replace(/[ \t]+/g, " ")
      .replace(/\n[ \t]+/g, "\n")
      .replace(/\n{3,}/g, "\n\n")
      .trim();
  }

  function decodeXml(value) {
    return String(value || "")
      .replace(/&#x([0-9a-f]+);/gi, (_, code) => String.fromCodePoint(Number.parseInt(code, 16)))
      .replace(/&#([0-9]+);/g, (_, code) => String.fromCodePoint(Number(code)))
      .replace(/&lt;/g, "<")
      .replace(/&gt;/g, ">")
      .replace(/&quot;/g, '"')
      .replace(/&apos;/g, "'")
      .replace(/&amp;/g, "&");
  }

  function stripHtml(value) {
    return cleanText(decodeXml(String(value || "")
      .replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, " ")
      .replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi, " ")
      .replace(/<(?:br|\/p|\/div|\/li|\/h[1-6]|\/tr)>/gi, "\n")
      .replace(/<[^>]+>/g, " ")));
  }

  function tokens(value) {
    const matches = normalize(value).match(/[a-z0-9%+\-=<>²³⁰¹⁴⁵⁶⁷⁸⁹]{2,}/g) || [];
    return matches.filter((term) => !STOP_WORDS.has(term) && (term.length > 2 || /\d|[%+\-=<>²³]/.test(term)));
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

  function extensionOf(name) {
    return String(name || "").toLocaleLowerCase("pt-BR").match(/\.([a-z0-9]+)$/)?.[1] || "";
  }

  function normalizeUa(value) {
    const parsed = Number(String(value == null ? "" : value).match(/\d{1,2}/)?.[0] || 0);
    return parsed >= 1 && parsed <= 30 ? parsed : null;
  }

  function normalizeEvaluation(value) {
    const normalized = String(value || "GENERAL").trim().toLocaleUpperCase("pt-BR");
    return COLLECTION_EVALUATIONS.includes(normalized) ? normalized : "GENERAL";
  }

  function collectionLabel(collection) {
    if (!collection || collection.id === DEFAULT_COLLECTION_ID) return "Acervo geral";
    const evaluation = normalizeEvaluation(collection.evaluation);
    const subject = cleanText(collection.subject || "");
    return cleanText(collection.name || `${evaluation === "GENERAL" ? "Acervo" : evaluation}${subject ? ` · ${subject}` : ""}`) || "Coleção sem nome";
  }

  function normalizeCollection(collection, fallbackId) {
    const now = new Date().toISOString();
    const source = collection && typeof collection === "object" ? collection : {};
    const evaluation = normalizeEvaluation(source.evaluation);
    const subject = cleanText(source.subject || "");
    const id = String(source.id || fallbackId || `collection-${fnv1a(`${evaluation}:${normalize(subject)}:${now}`)}`);
    return {
      id,
      name: collectionLabel({ ...source, id, evaluation, subject }),
      evaluation,
      subject,
      defaultUas: cleanText(source.defaultUas || ""),
      defaultDifficulty: ["auto", "Fácil", "Médio", "Difícil"].includes(source.defaultDifficulty) ? source.defaultDifficulty : "auto",
      defaultCount: Math.max(0, Math.min(30, Number(source.defaultCount || 0))),
      rulesText: cleanText(source.rulesText || ""),
      createdAt: source.createdAt || now,
      updatedAt: source.updatedAt || source.createdAt || now,
      lastUsedAt: source.lastUsedAt || null
    };
  }

  function defaultCollection(now) {
    const at = now || new Date().toISOString();
    return normalizeCollection({
      id: DEFAULT_COLLECTION_ID,
      name: "Acervo geral",
      evaluation: "GENERAL",
      subject: "",
      createdAt: at,
      updatedAt: at
    }, DEFAULT_COLLECTION_ID);
  }

  function inferSubjectFromName(name) {
    const stem = String(name || "")
      .replace(/\.[^.]+$/, "")
      .replace(/[_-]+/g, " ")
      .replace(/\b(?:AD|AI|PS|P1|P2|P3|SCH)\b/gi, " ")
      .replace(/\b(?:avalia[cç][aã]o|quest[oõ]es?|padr[aã]o|projeto|athus|entrada|arquivo|material)\b/gi, " ")
      .replace(/\b(?:19|20)\d{2}\b/g, " ")
      .replace(/\bUA\s*\d{1,2}\b/gi, " ")
      .replace(/\(\d+\)/g, " ")
      .replace(/\b\d{1,2}\b/g, " ")
      .replace(/\s+/g, " ")
      .trim();
    return stem.length >= 4 ? stem : "";
  }

  function splitIntoChunks(text, documentId) {
    const cleaned = cleanText(text).slice(0, MAX_TEXT_CHARS);
    if (!cleaned) return [];
    const paragraphs = cleaned.split(/\n{2,}|(?<=[.!?])\s+(?=[A-ZÀ-Ý0-9])/u).map((part) => part.trim()).filter(Boolean);
    const chunks = [];
    let buffer = "";
    let ordinal = 0;
    const push = () => {
      const value = cleanText(buffer);
      if (!value) return;
      const termList = tokens(value);
      const counts = {};
      termList.forEach((term) => { counts[term] = (counts[term] || 0) + 1; });
      chunks.push({ id: `${documentId}:c${++ordinal}`, ordinal, text: value, terms: Object.keys(counts), termCounts: counts, wordCount: value.split(/\s+/).length });
      buffer = value.slice(Math.max(0, value.length - CHUNK_OVERLAP));
    };
    paragraphs.forEach((paragraph) => {
      if (paragraph.length > CHUNK_TARGET * 1.6) {
        const sentences = paragraph.match(/[^.!?]+[.!?]+|[^.!?]+$/g) || [paragraph];
        sentences.forEach((sentence) => {
          if (buffer && buffer.length + sentence.length > CHUNK_TARGET) push();
          buffer = `${buffer} ${sentence}`.trim();
        });
        return;
      }
      if (buffer && buffer.length + paragraph.length > CHUNK_TARGET) push();
      buffer = `${buffer}${buffer ? "\n\n" : ""}${paragraph}`;
    });
    if (buffer.trim()) push();
    return chunks;
  }

  function createEmptyBase() {
    const now = new Date().toISOString();
    const base = {
      schemaVersion: SCHEMA_VERSION,
      createdAt: now,
      updatedAt: now,
      collections: [defaultCollection(now)],
      activeCollectionId: DEFAULT_COLLECTION_ID,
      documents: [],
      rules: { activeText: DEFAULT_ATHUS_RULES, sourceName: "Padrão Athus integrado", updatedAt: now },
      generationHistory: []
    };
    hydratedBases.add(base);
    return base;
  }

  function hydrateBase(base) {
    const result = base && typeof base === "object" ? base : createEmptyBase();
    if (hydratedBases.has(result)) return result;
    result.schemaVersion = SCHEMA_VERSION;
    result.createdAt = result.createdAt || new Date().toISOString();
    result.updatedAt = result.updatedAt || result.createdAt;
    const hydratedCollections = Array.isArray(result.collections)
      ? result.collections.map((collection) => normalizeCollection(collection)).filter((collection) => collection.id)
      : [];
    const collectionIds = new Set(hydratedCollections.map((collection) => collection.id));
    if (!collectionIds.has(DEFAULT_COLLECTION_ID)) hydratedCollections.unshift(defaultCollection(result.updatedAt));
    result.collections = hydratedCollections.filter((collection, index, values) => values.findIndex((candidate) => candidate.id === collection.id) === index);
    result.activeCollectionId = result.collections.some((collection) => collection.id === result.activeCollectionId)
      ? result.activeCollectionId
      : DEFAULT_COLLECTION_ID;
    result.documents = Array.isArray(result.documents) ? result.documents : [];
    result.rules = result.rules && typeof result.rules === "object" ? result.rules : { activeText: "", sourceName: "", updatedAt: null };
    if (!result.rules.activeText) result.rules = { activeText: DEFAULT_ATHUS_RULES, sourceName: "Padrão Athus integrado", updatedAt: result.updatedAt };
    result.generationHistory = Array.isArray(result.generationHistory) ? result.generationHistory.slice(-2000) : [];
    result.documents.forEach((document) => {
      const needsAnalysis = root.AvaliaPremiumCurator && (document.analysis?.version !== root.AvaliaPremiumCurator.version || document.analysis?.revision !== root.AvaliaPremiumCurator.analysisRevision || !document.role);
      document.text = cleanText(document.text || "").slice(0, MAX_TEXT_CHARS);
      document.id = document.id || `kb-${fnv1a(`${document.name}:${document.text}`)}`;
      document.fingerprint = document.fingerprint || fnv1a(document.text);
      document.collectionId = result.collections.some((collection) => collection.id === document.collectionId)
        ? document.collectionId
        : DEFAULT_COLLECTION_ID;
      document.assignedUa = normalizeUa(document.assignedUa);
      if (root.AvaliaPremiumCurator && (needsAnalysis || !document.analysis)) {
        document.analysis = root.AvaliaPremiumCurator.analyzeDocument({
          name: document.name,
          text: document.text,
          metadata: { role: document.analysis?.requestedRole || document.role || "auto", subject: document.subjectSource === "manual" ? document.subject : "", assignedUa: document.assignedUa }
        });
      }
      document.role = document.analysis?.role || document.role || "reference_material";
      document.subject = cleanText(document.analysis?.subject || document.subject || inferSubjectFromName(document.name));
      document.subjectSource = document.analysis?.subjectSource || document.subjectSource || "filename";
      const indexedText = document.analysis ? (document.analysis.evidence?.eligible ? document.analysis.evidence.cleanText : "") : document.role === "reference_material" ? document.text : "";
      const needsIndex = needsAnalysis || document.indexVersion !== INDEX_VERSION || !Array.isArray(document.chunks);
      document.chunks = needsIndex ? splitIntoChunks(indexedText, document.id) : document.chunks;
      document.indexVersion = INDEX_VERSION;
    });
    result.collections.forEach((collection) => {
      const latestDocumentUpdate = result.documents
        .filter((document) => document.collectionId === collection.id)
        .map((document) => document.updatedAt || document.addedAt)
        .filter(Boolean)
        .sort()
        .at(-1);
      if (latestDocumentUpdate && latestDocumentUpdate > collection.updatedAt) collection.updatedAt = latestDocumentUpdate;
    });
    result.generationHistory = result.generationHistory.map((entry) => {
      if (!entry || typeof entry !== "object") return entry;
      return { ...entry, collectionId: result.collections.some((collection) => collection.id === entry.collectionId) ? entry.collectionId : DEFAULT_COLLECTION_ID };
    });
    hydratedBases.add(result);
    return result;
  }

  function shallowBaseCopy(base) {
    const source = hydrateBase(base || createEmptyBase());
    const copy = {
      ...source,
      collections: source.collections.map((collection) => ({ ...collection })),
      documents: [...source.documents],
      rules: { ...source.rules },
      generationHistory: [...source.generationHistory]
    };
    hydratedBases.add(copy);
    return copy;
  }

  function activeCollection(base) {
    const hydrated = hydrateBase(base);
    return hydrated.collections.find((collection) => collection.id === hydrated.activeCollectionId) || hydrated.collections[0];
  }

  function listCollections(base) {
    return hydrateBase(base).collections
      .map((collection) => ({ ...collection, name: collectionLabel(collection) }))
      .sort((left, right) => {
        if (left.id === DEFAULT_COLLECTION_ID) return -1;
        if (right.id === DEFAULT_COLLECTION_ID) return 1;
        return left.name.localeCompare(right.name, "pt-BR", { numeric: true, sensitivity: "base" });
      });
  }

  function upsertCollection(base, values) {
    const result = shallowBaseCopy(base);
    const now = new Date().toISOString();
    const input = values && typeof values === "object" ? values : {};
    const evaluation = normalizeEvaluation(input.evaluation);
    const subject = cleanText(input.subject || "");
    if (evaluation === "GENERAL" && input.id !== DEFAULT_COLLECTION_ID) throw new Error("Escolha a avaliação da coleção.");
    if (input.id !== DEFAULT_COLLECTION_ID && subject.length < 3) throw new Error("Informe a disciplina com pelo menos 3 caracteres.");
    const existingIndex = result.collections.findIndex((collection) => collection.id === input.id);
    const sameKey = result.collections.find((collection, index) => index !== existingIndex && normalizeEvaluation(collection.evaluation) === evaluation && normalize(collection.subject) === normalize(subject));
    if (sameKey) throw new Error(`A coleção “${collectionLabel(sameKey)}” já existe.`);
    const id = existingIndex >= 0
      ? result.collections[existingIndex].id
      : String(input.id || `collection-${fnv1a(`${evaluation}:${normalize(subject)}`)}`);
    const previous = existingIndex >= 0 ? result.collections[existingIndex] : {};
    const collection = normalizeCollection({
      ...previous,
      ...input,
      id,
      evaluation,
      subject,
      name: cleanText(input.name || `${evaluation} · ${subject}`),
      createdAt: previous.createdAt || now,
      updatedAt: now,
      lastUsedAt: now
    });
    if (existingIndex >= 0) result.collections.splice(existingIndex, 1, collection);
    else result.collections.push(collection);
    result.activeCollectionId = collection.id;
    result.updatedAt = now;
    return { base: result, collection, created: existingIndex < 0 };
  }

  function selectCollection(base, id) {
    const result = shallowBaseCopy(base);
    const collection = result.collections.find((entry) => entry.id === id);
    if (!collection) return { base: result, selected: false, collection: activeCollection(result) };
    const now = new Date().toISOString();
    collection.lastUsedAt = now;
    result.activeCollectionId = collection.id;
    result.updatedAt = now;
    return { base: result, selected: true, collection };
  }

  function removeCollection(base, id) {
    const result = shallowBaseCopy(base);
    if (!id || id === DEFAULT_COLLECTION_ID) return { base: result, removed: false, removedDocuments: 0 };
    if (!result.collections.some((collection) => collection.id === id)) return { base: result, removed: false, removedDocuments: 0 };
    const before = result.documents.length;
    result.collections = result.collections.filter((collection) => collection.id !== id);
    result.documents = result.documents.filter((document) => document.collectionId !== id);
    result.generationHistory = result.generationHistory.filter((entry) => !entry || typeof entry !== "object" || entry.collectionId !== id);
    if (result.activeCollectionId === id) result.activeCollectionId = DEFAULT_COLLECTION_ID;
    result.updatedAt = new Date().toISOString();
    return { base: result, removed: true, removedDocuments: before - result.documents.length };
  }

  function updateCollectionPreferences(base, id, preferences) {
    const result = shallowBaseCopy(base);
    const index = result.collections.findIndex((collection) => collection.id === id);
    if (index < 0) return { base: result, updated: false };
    const previous = result.collections[index];
    const next = normalizeCollection({
      ...previous,
      defaultUas: preferences?.defaultUas ?? previous.defaultUas,
      defaultDifficulty: preferences?.defaultDifficulty ?? previous.defaultDifficulty,
      defaultCount: preferences?.defaultCount ?? previous.defaultCount,
      rulesText: preferences?.rulesText ?? previous.rulesText,
      updatedAt: new Date().toISOString()
    });
    result.collections[index] = next;
    result.updatedAt = next.updatedAt;
    return { base: result, updated: true, collection: next };
  }

  function scopeBase(base, collectionId) {
    const source = hydrateBase(base);
    const selected = source.collections.find((collection) => collection.id === (collectionId || source.activeCollectionId)) || activeCollection(source);
    const scoped = {
      ...source,
      activeCollectionId: selected.id,
      documents: source.documents.filter((document) => document.collectionId === selected.id),
      generationHistory: source.generationHistory.filter((entry) => entry && typeof entry === "object" ? entry.collectionId === selected.id : selected.id === DEFAULT_COLLECTION_ID),
      rules: {
        ...source.rules,
        activeText: selected.rulesText || source.rules.activeText
      }
    };
    hydratedBases.add(scoped);
    return scoped;
  }

  function mergeBases(base, incomingBase) {
    let result = shallowBaseCopy(base);
    const incoming = hydrateBase(incomingBase);
    const collectionMap = new Map([[DEFAULT_COLLECTION_ID, DEFAULT_COLLECTION_ID]]);
    let collectionsAdded = 0;
    incoming.collections.forEach((collection) => {
      if (collection.id === DEFAULT_COLLECTION_ID) return;
      const equivalent = result.collections.find((entry) => normalizeEvaluation(entry.evaluation) === normalizeEvaluation(collection.evaluation) && normalize(entry.subject) === normalize(collection.subject));
      if (equivalent) {
        collectionMap.set(collection.id, equivalent.id);
        return;
      }
      const added = upsertCollection(result, collection);
      result = added.base;
      collectionMap.set(collection.id, added.collection.id);
      collectionsAdded += 1;
    });
    let documentsAdded = 0;
    let documentsReplaced = 0;
    incoming.documents.forEach((document) => {
      const mappedCollectionId = collectionMap.get(document.collectionId) || DEFAULT_COLLECTION_ID;
      const next = {
        ...document,
        collectionId: mappedCollectionId,
        id: `kb-${document.fingerprint || fnv1a(document.text)}-${fnv1a(mappedCollectionId).slice(0, 6)}`
      };
      const merged = addOrReplace(result, next);
      result = merged.base;
      merged.replaced ? documentsReplaced += 1 : documentsAdded += 1;
    });
    const history = [...result.generationHistory, ...incoming.generationHistory.map((entry) => entry && typeof entry === "object" ? { ...entry, collectionId: collectionMap.get(entry.collectionId) || DEFAULT_COLLECTION_ID } : entry)];
    result.generationHistory = history.filter((entry, index, values) => {
      const key = entry && typeof entry === "object" ? `${entry.collectionId}:${entry.factFingerprint || entry.questionName || index}` : String(entry);
      return values.findIndex((candidate, candidateIndex) => {
        const candidateKey = candidate && typeof candidate === "object" ? `${candidate.collectionId}:${candidate.factFingerprint || candidate.questionName || candidateIndex}` : String(candidate);
        return candidateKey === key;
      }) === index;
    }).slice(-2000);
    result.updatedAt = new Date().toISOString();
    return { base: result, collectionsAdded, documentsAdded, documentsReplaced };
  }

  function xmlParagraphText(xml) {
    const paragraphs = [];
    const paragraphPattern = /<(?:w|a):p\b[^>]*>([\s\S]*?)<\/(?:w|a):p>/gi;
    let match;
    while ((match = paragraphPattern.exec(String(xml || "")))) {
      const pieces = [];
      const contentPattern = /<(?:w:t|a:t)\b[^>]*>([\s\S]*?)<\/(?:w:t|a:t)>|<(?:w:tab|w:br|a:br)\b[^>]*\/?\s*>/gi;
      let content;
      while ((content = contentPattern.exec(match[1]))) pieces.push(content[1] == null ? " " : decodeXml(content[1]));
      const line = cleanText(pieces.join(""));
      if (line) paragraphs.push(line);
    }
    return paragraphs;
  }

  function naturalSort(left, right) {
    return String(left).localeCompare(String(right), "pt-BR", { numeric: true, sensitivity: "base" });
  }

  async function extractOoxml(arrayBuffer, kind) {
    if (typeof root.JSZip === "undefined") throw new Error("O leitor de arquivos Office não foi carregado.");
    const zip = await root.JSZip.loadAsync(arrayBuffer);
    const paths = Object.keys(zip.files).filter((path) => {
      if (kind === "docx") return path === "word/document.xml" || /^word\/(?:footnotes|endnotes|comments)\.xml$/.test(path);
      return /^ppt\/slides\/slide\d+\.xml$/.test(path) || path === "ppt/notesMasters/notesMaster1.xml";
    }).sort(naturalSort);
    if (!paths.length) throw new Error(kind === "docx" ? "DOCX sem conteúdo textual reconhecível." : "PPTX sem slides reconhecíveis.");
    const sections = [];
    for (const path of paths) {
      const xml = await zip.file(path)?.async("string");
      const paragraphs = xmlParagraphText(xml || "");
      if (paragraphs.length) sections.push(paragraphs.join("\n"));
    }
    return cleanText(sections.join("\n\n"));
  }

  async function extractPdf(arrayBuffer) {
    if (typeof root.__AAB_PDF_EXTRACTOR__ === "function") return cleanText(await root.__AAB_PDF_EXTRACTOR__(arrayBuffer));
    if (!root.SmartFoxPdfReader) throw new Error("O leitor local de PDF não foi carregado. Recarregue a extensão SmartFox e atualize a aba do AvaliA.");
    return cleanText(await root.SmartFoxPdfReader.read(arrayBuffer));
  }

  async function extractFile(file) {
    if (!file) throw new Error("Selecione ao menos um material.");
    const extension = extensionOf(file.name);
    if (!SUPPORTED_EXTENSIONS.includes(extension)) throw new Error(`Formato .${extension || "?"} não suportado. Use DOCX, PDF, PPTX, TXT, MD, HTML ou CSV.`);
    if (Number(file.size || 0) > MAX_FILE_BYTES) throw new Error(`${file.name}: arquivo acima do limite de 35 MB.`);
    let text = "";
    if (extension === "docx" || extension === "pptx") text = await extractOoxml(await file.arrayBuffer(), extension);
    else if (extension === "pdf") text = await extractPdf(await file.arrayBuffer());
    else if (extension === "html" || extension === "htm") text = stripHtml(await file.text());
    else text = cleanText(await file.text());
    if (text.length < 80) throw new Error(`${file.name}: foi encontrado texto insuficiente para formar uma base confiável.`);
    if (text.length > MAX_TEXT_CHARS) text = text.slice(0, MAX_TEXT_CHARS);
    return text;
  }

  function buildDocument(fileMeta, text, metadata) {
    const cleaned = cleanText(text);
    const fingerprint = fnv1a(cleaned);
    const now = new Date().toISOString();
    const meta = metadata && typeof metadata === "object" ? metadata : {};
    const collectionId = String(meta.collectionId || DEFAULT_COLLECTION_ID);
    const id = `kb-${fingerprint}-${fnv1a(collectionId).slice(0, 6)}`;
    const analysis = root.AvaliaPremiumCurator?.analyzeDocument({ name: fileMeta?.name, text: cleaned, metadata: meta }) || null;
    const role = analysis?.role || meta.role || "reference_material";
    const subject = cleanText(meta.subject || analysis?.subject || inferSubjectFromName(fileMeta?.name));
    const indexedText = analysis ? (analysis.evidence?.eligible ? analysis.evidence.cleanText : "") : role === "reference_material" ? cleaned : "";
    return {
      id,
      collectionId,
      name: String(fileMeta?.name || "material"),
      extension: extensionOf(fileMeta?.name),
      mime: String(fileMeta?.type || ""),
      sourceSize: Number(fileMeta?.size || 0),
      subject,
      assignedUa: normalizeUa(meta.assignedUa),
      role,
      analysis,
      subjectSource: analysis?.subjectSource || (meta.subject ? "manual" : "filename"),
      text: cleaned,
      fingerprint,
      wordCount: cleaned ? cleaned.split(/\s+/).length : 0,
      characterCount: cleaned.length,
      addedAt: now,
      updatedAt: now,
      indexVersion: INDEX_VERSION,
      chunks: splitIntoChunks(indexedText, id)
    };
  }

  function addOrReplace(base, document) {
    const result = shallowBaseCopy(base);
    const targetCollectionId = result.collections.some((collection) => collection.id === document.collectionId)
      ? document.collectionId
      : result.activeCollectionId;
    document.collectionId = targetCollectionId;
    const duplicateIndex = result.documents.findIndex((entry) => entry.collectionId === targetCollectionId && (entry.fingerprint === document.fingerprint || normalize(entry.name) === normalize(document.name)));
    if (duplicateIndex < 0 && result.documents.length >= MAX_DOCUMENTS) throw new Error(`A base atingiu o limite de ${MAX_DOCUMENTS} materiais. Remova versões antigas ou divida o acervo por perfil.`);
    const retainedCharacters = result.documents.reduce((total, entry, index) => total + (index === duplicateIndex ? 0 : Number(entry.characterCount || entry.text?.length || 0)), 0);
    if (retainedCharacters + Number(document.characterCount || document.text?.length || 0) > MAX_BASE_TEXT_CHARS) throw new Error("A base atingiu o limite de 50 milhões de caracteres. Remova materiais redundantes antes de continuar.");
    if (duplicateIndex >= 0) {
      document.addedAt = result.documents[duplicateIndex].addedAt || document.addedAt;
      result.documents.splice(duplicateIndex, 1, document);
    } else result.documents.push(document);
    result.updatedAt = new Date().toISOString();
    const collection = result.collections.find((entry) => entry.id === targetCollectionId);
    if (collection) collection.updatedAt = result.updatedAt;
    return { base: result, replaced: duplicateIndex >= 0 };
  }

  function removeDocument(base, id) {
    const result = shallowBaseCopy(base);
    const removedDocument = result.documents.find((document) => document.id === id);
    const before = result.documents.length;
    result.documents = result.documents.filter((document) => document.id !== id);
    result.updatedAt = new Date().toISOString();
    const collection = result.collections.find((entry) => entry.id === removedDocument?.collectionId);
    if (collection && result.documents.length < before) collection.updatedAt = result.updatedAt;
    return { base: result, removed: result.documents.length < before };
  }

  function clearCollection(base, collectionId) {
    const result = shallowBaseCopy(base);
    const targetId = result.collections.some((collection) => collection.id === collectionId)
      ? collectionId
      : result.activeCollectionId;
    const before = result.documents.length;
    result.documents = result.documents.filter((document) => document.collectionId !== targetId);
    const removedDocuments = before - result.documents.length;
    if (removedDocuments) {
      const now = new Date().toISOString();
      result.updatedAt = now;
      const collection = result.collections.find((entry) => entry.id === targetId);
      if (collection) collection.updatedAt = now;
    }
    return { base: result, removedDocuments };
  }

  function updateDocumentMetadata(base, id, metadata) {
    const result = shallowBaseCopy(base);
    const index = result.documents.findIndex((entry) => entry.id === id);
    const document = index >= 0 ? { ...result.documents[index] } : null;
    if (!document) return { base: result, updated: false };
    if (metadata?.collectionId && result.collections.some((collection) => collection.id === metadata.collectionId)) {
      const collision = result.documents.find((entry) => entry.id !== document.id && entry.collectionId === metadata.collectionId && (entry.fingerprint === document.fingerprint || normalize(entry.name) === normalize(document.name)));
      if (collision) return { base: result, updated: false, collision };
      document.collectionId = metadata.collectionId;
    }
    const hasSubject = Boolean(metadata && Object.prototype.hasOwnProperty.call(metadata, "subject"));
    const enteredSubject = hasSubject ? cleanText(metadata.subject) : (document.subjectSource === "manual" ? document.subject : "");
    document.subject = enteredSubject || document.subject || inferSubjectFromName(document.name);
    document.assignedUa = normalizeUa(metadata?.assignedUa);
    if (root.AvaliaPremiumCurator) {
      document.analysis = root.AvaliaPremiumCurator.analyzeDocument({
        name: document.name,
        text: document.text,
        metadata: { role: metadata?.role || document.role || "auto", subject: enteredSubject, assignedUa: document.assignedUa }
      });
      document.role = document.analysis.role;
      document.subject = cleanText(document.analysis.subject || document.subject);
      document.subjectSource = document.analysis.subjectSource;
      const indexedText = document.analysis.evidence?.eligible ? document.analysis.evidence.cleanText : "";
      document.chunks = splitIntoChunks(indexedText, document.id);
      document.indexVersion = INDEX_VERSION;
    }
    document.updatedAt = new Date().toISOString();
    result.documents[index] = document;
    result.updatedAt = document.updatedAt;
    const collection = result.collections.find((entry) => entry.id === document.collectionId);
    if (collection) collection.updatedAt = document.updatedAt;
    return { base: result, updated: true };
  }

  function updateCollectionDocumentSubjects(base, collectionId, subject) {
    const result = shallowBaseCopy(base);
    const enteredSubject = cleanText(subject || "");
    const collection = result.collections.find((entry) => entry.id === collectionId);
    if (!collection || !enteredSubject) return { base: result, updatedDocuments: 0 };
    const now = new Date().toISOString();
    let updatedDocuments = 0;
    result.documents = result.documents.map((entry) => {
      if (entry.collectionId !== collectionId) return entry;
      const document = { ...entry, subject: enteredSubject, subjectSource: "manual", updatedAt: now };
      if (root.AvaliaPremiumCurator) {
        document.analysis = root.AvaliaPremiumCurator.analyzeDocument({
          name: document.name,
          text: document.text,
          metadata: { role: document.role || "auto", subject: enteredSubject, assignedUa: document.assignedUa }
        });
        document.role = document.analysis.role;
        document.subject = cleanText(document.analysis.subject || enteredSubject);
        document.subjectSource = document.analysis.subjectSource || "manual";
        const indexedText = document.analysis.evidence?.eligible ? document.analysis.evidence.cleanText : "";
        document.chunks = splitIntoChunks(indexedText, document.id);
        document.indexVersion = INDEX_VERSION;
      }
      updatedDocuments += 1;
      return document;
    });
    if (updatedDocuments) {
      collection.updatedAt = now;
      result.updatedAt = now;
    }
    return { base: result, updatedDocuments };
  }

  function reanalyzeCollectionDocuments(base, collectionId) {
    const result = shallowBaseCopy(base);
    const collection = result.collections.find((entry) => entry.id === collectionId);
    if (!collection) return { base: result, updatedDocuments: 0 };
    const now = new Date().toISOString();
    let updatedDocuments = 0;
    result.documents = result.documents.map((entry) => {
      if (entry.collectionId !== collectionId) return entry;
      const document = { ...entry, updatedAt: now };
      if (root.AvaliaPremiumCurator) {
        const manualSubject = document.subjectSource === "manual" ? document.subject : "";
        document.analysis = root.AvaliaPremiumCurator.analyzeDocument({
          name: document.name,
          text: document.text,
          metadata: { role: document.role || "auto", subject: manualSubject, assignedUa: document.assignedUa }
        });
        document.role = document.analysis.role;
        document.subject = cleanText(document.analysis.subject || document.subject || inferSubjectFromName(document.name));
        document.subjectSource = document.analysis.subjectSource || document.subjectSource;
        const indexedText = document.analysis.evidence?.eligible ? document.analysis.evidence.cleanText : "";
        document.chunks = splitIntoChunks(indexedText, document.id);
        document.indexVersion = INDEX_VERSION;
      }
      updatedDocuments += 1;
      return document;
    });
    if (updatedDocuments) {
      collection.updatedAt = now;
      result.updatedAt = now;
    }
    return { base: result, updatedDocuments };
  }

  function corpus(base) {
    const hydrated = hydrateBase(base);
    const cached = corpusCache.get(hydrated);
    if (cached?.updatedAt === hydrated.updatedAt) return cached.index;
    const documents = hydrated.documents;
    const chunks = documents.flatMap((document) => (document.chunks || []).map((chunk) => ({
      ...chunk,
      documentId: document.id,
      documentName: document.name,
      documentSubject: document.subject || "",
      documentUa: document.assignedUa || null
    })));
    const documentFrequency = {};
    chunks.forEach((chunk) => new Set(chunk.terms || tokens(chunk.text)).forEach((term) => { documentFrequency[term] = (documentFrequency[term] || 0) + 1; }));
    const index = { documents, chunks, documentFrequency, totalChunks: chunks.length };
    corpusCache.set(hydrated, { updatedAt: hydrated.updatedAt, index });
    return index;
  }

  function idf(term, index) {
    return Math.log(1 + (index.totalChunks + 1) / ((index.documentFrequency[term] || 0) + 1));
  }

  function uniqueTerms(value) {
    return [...new Set(tokens(value))];
  }

  function chunkScore(chunk, queryTerms, queryNormalized, index) {
    const counts = chunk.termCounts || Object.fromEntries(tokens(chunk.text).map((term) => [term, 1]));
    let score = 0;
    let matched = 0;
    queryTerms.forEach((term) => {
      if (!counts[term]) return;
      matched += 1;
      score += idf(term, index) * (1 + Math.log(counts[term]));
    });
    const normalizedChunk = normalize(chunk.text);
    const phraseWords = queryNormalized.split(/\s+/).filter((term) => term.length > 3).slice(0, 10);
    if (phraseWords.length >= 4 && normalizedChunk.includes(phraseWords.slice(0, 4).join(" "))) score += 4;
    const coverage = queryTerms.length ? matched / queryTerms.length : 0;
    return { score: score * (0.55 + coverage), matched, coverage };
  }

  function evidenceExcerpt(text, termsToFind) {
    const source = cleanText(text);
    const normalizedSource = normalize(source);
    const position = termsToFind.map((term) => normalizedSource.indexOf(term)).filter((index) => index >= 0).sort((a, b) => a - b)[0] || 0;
    const start = Math.max(0, position - 120);
    const end = Math.min(source.length, start + 440);
    return `${start > 0 ? "…" : ""}${source.slice(start, end).trim()}${end < source.length ? "…" : ""}`;
  }

  function supportingSentence(text, alternative) {
    const alternativeTerms = uniqueTerms(alternative);
    const candidates = cleanText(text).split(/\n+|(?<=[.!?])\s+(?=[A-ZÀ-Ý0-9])/u).map((entry) => entry.trim()).filter(Boolean);
    const ranked = candidates.map((entry) => ({ entry, matches: alternativeTerms.filter((term) => normalize(entry).includes(term)).length }))
      .sort((left, right) => right.matches - left.matches || left.entry.length - right.entry.length);
    return (ranked[0]?.entry || cleanText(text).slice(0, 420)).replace(/^[•·\-–—]\s*/, "").trim();
  }

  function alternativeSupport(alternative, evidenceText, index) {
    const plain = String(alternative?.plain || alternative?.text || alternative?.html || "");
    const normalizedAlternative = normalize(plain);
    const terms = uniqueTerms(plain);
    const evidenceNormalized = normalize(evidenceText);
    let score = 0;
    let matched = 0;
    terms.forEach((term) => {
      if (!evidenceNormalized.includes(term)) return;
      matched += 1;
      score += idf(term, index);
    });
    const phrase = normalizedAlternative.split(/\s+/).filter(Boolean).slice(0, 12).join(" ");
    const direct = phrase.length >= 8 && evidenceNormalized.includes(phrase);
    if (direct) score += 8;
    const coverage = terms.length ? matched / terms.length : 0;
    score *= 0.5 + coverage;
    return { score, matched, total: terms.length, coverage, direct };
  }

  function rankedEvidenceSegments(rankedChunks, queryTerms, body, index) {
    const segments = [];
    const seen = new Set();
    rankedChunks.forEach((chunk) => {
      cleanText(chunk.text).split(/\n+|(?<=[.!?])\s+(?=[A-ZÀ-Ý0-9])/u).map((text) => cleanText(text)).filter((text) => text.length >= 24).forEach((text) => {
        const key = normalize(text);
        if (seen.has(key)) return;
        seen.add(key);
        const rank = chunkScore({ text, termCounts: Object.fromEntries(tokens(text).map((term) => [term, 1])) }, queryTerms, normalize(body), index);
        if (rank.matched) segments.push({ ...chunk, id: `${chunk.id}:s${segments.length + 1}`, text, rank });
      });
    });
    return segments.sort((left, right) => right.rank.score - left.rank.score).slice(0, 8);
  }

  function analyzeQuestion(question, base) {
    const index = corpus(base);
    const baseSummary = { documents: index.documents.length, chunks: index.chunks.length, contentScope: "statement-and-alternatives" };
    if (!index.chunks.length) return { status: "no_base", confidence: 0, suggestedIndex: null, suggestedLetter: "", agreement: null, evidence: [], warnings: ["Adicione materiais à base para conferir esta questão."], baseSummary };
    const body = cleanText(question?.bodyText || stripHtml(question?.bodyHtml || ""));
    const queryText = [body, ...(question?.alternatives || []).map(a => cleanText(a.plain || a.text || stripHtml(a.html || "")))].join(" ");
    const queryTerms = uniqueTerms(queryText);
    // Filename, objective, discipline label, answer key and feedback never
    // participate in retrieval. The supplied answer is audited only afterwards.
    const subjectTerms = [];
    const ranked = index.chunks.map(chunk => ({...chunk, rank:chunkScore(chunk,queryTerms,normalize(queryText),index)}))
      .filter((chunk) => chunk.rank.matched > 0)
      .sort((left, right) => right.rank.score - left.rank.score)
      .slice(0, 6);
    if (!ranked.length) return { status: "insufficient", confidence: 0, suggestedIndex: null, suggestedLetter: "", agreement: null, evidence: [], warnings: ["Nenhum trecho da base correspondeu ao enunciado e às alternativas."], baseSummary, alignment: { score: 0, matchedTerms: [], missingTerms: queryTerms.slice(0, 12) } };

    const segments = rankedEvidenceSegments(ranked, queryTerms, queryText, index);
    const top = (segments.length ? segments : ranked).slice(0, 4);
    const evidenceText = top.map((chunk) => chunk.text).join("\n");
    const matchedTerms = queryTerms.filter((term) => normalize(evidenceText).includes(term));
    const alignmentRatio = queryTerms.length ? matchedTerms.length / queryTerms.length : 0;
    const alignmentScore = Math.round(Math.min(100, alignmentRatio * 115));
    const subjectScore = Math.round(Math.max(0, ...top.map((chunk) => Number(chunk.rank.subjectCoverage || 0))) * 100);
    const discursive = question?.questionFormat === "discursive" || /discursiv|dissertativ|resposta aberta/i.test(`${question?.typeLabel || ""} ${question?.typeDescription || ""}`);
    if (discursive) {
      const expectedResponse = cleanText(question?.expectedResponseText || question?.expectedResponseHtml || "");
      const responseTerms = uniqueTerms(expectedResponse);
      const normalizedEvidence = normalize(evidenceText);
      const supportedResponseTerms = responseTerms.filter((term) => normalizedEvidence.includes(term));
      const responseCoverage = responseTerms.length ? Math.round(supportedResponseTerms.length / responseTerms.length * 100) : 0;
      const confidence = Math.round(Math.min(0.99, (alignmentScore / 100) * 0.5 + (responseCoverage / 100) * 0.5) * 100) / 100;
      let status = "insufficient";
      if (alignmentScore >= 45 && responseCoverage >= 50 && confidence >= 0.55) status = "supported";
      else if (alignmentScore >= 22 || responseCoverage >= 25) status = "review";
      const warnings = [];
      if (!expectedResponse) warnings.push("A questão discursiva não possui padrão de resposta para confrontar com a base.");
      if (alignmentScore < 45) warnings.push("A correspondência temática da questão discursiva com a base é parcial.");
      if (expectedResponse && responseCoverage < 50) warnings.push("Menos da metade dos conceitos relevantes da resposta esperada foi sustentada pelos trechos recuperados; confira manualmente.");
      if (subjectTerms.length && index.documents.some((document) => document.subject) && subjectScore === 0) warnings.push("Os melhores trechos não possuem a mesma identificação de disciplina da questão; confira a classificação dos materiais.");
      const evidence = top.map((chunk) => ({
        documentId: chunk.documentId,
        documentName: chunk.documentName,
        chunkId: chunk.id,
        score: Math.round(chunk.rank.score * 100) / 100,
        coverage: Math.round(chunk.rank.coverage * 100),
        excerpt: evidenceExcerpt(chunk.text, matchedTerms)
      }));
      return {
        status,
        questionFormat: "discursive",
        confidence,
        suggestedIndex: null,
        suggestedLetter: "",
        currentIndex: -1,
        currentLetter: "",
        agreement: status === "supported" ? true : null,
        responseCoverage,
        supportedResponseTerms: supportedResponseTerms.slice(0, 18),
        alignment: { score: alignmentScore, subjectScore, matchedTerms: matchedTerms.slice(0, 18), missingTerms: queryTerms.filter((term) => !matchedTerms.includes(term)).slice(0, 12) },
        evidence,
        warnings,
        feedbackSuggestion: "",
        analyzedAt: new Date().toISOString(),
        baseUpdatedAt: base?.updatedAt || null,
        baseSummary
      };
    }
    const alternatives = Array.isArray(question?.alternatives) ? question.alternatives : [];
    const alternativeScores = alternatives.map((alternative, alternativeIndex) => {
      const supports = top.map((segment, segmentIndex) => ({ ...alternativeSupport(alternative, segment.text, index), weight: 1 / (segmentIndex + 1), relevance: segment.rank.score }));
      const termSet = new Set();
      let score = 0;
      let direct = false;
      supports.forEach((support, segmentIndex) => {
        score += support.score * support.weight * Math.min(2.2, 0.6 + support.relevance / 6);
        if (support.matched) uniqueTerms(alternative.plain || alternative.text || "").filter((term) => normalize(top[segmentIndex].text).includes(term)).forEach((term) => termSet.add(term));
        if (support.direct && segmentIndex === 0) { direct = true; score += 7; }
      });
      const alternativeTerms = uniqueTerms(alternative.plain || alternative.text || "");
      return {
        index: alternativeIndex,
        letter: alternative.letter || String.fromCharCode(65 + alternativeIndex),
        text: String(alternative.plain || alternative.text || ""),
        score,
        matched: termSet.size,
        total: alternativeTerms.length,
        coverage: alternativeTerms.length ? termSet.size / alternativeTerms.length : 0,
        direct
      };
    });
    const negativePrompt = /\b(exceto|incorreta|incorreto|nao corresponde|nao e verdadeira|falsa)\b/.test(normalize(body));
    const ordered = [...alternativeScores].sort((left, right) => negativePrompt ? left.score - right.score : right.score - left.score);
    const best = ordered[0] || null;
    const runnerUp = ordered[1] || { score: 0 };
    const bestRaw = best?.score || 0;
    const separation = bestRaw ? Math.max(0, Math.min(1, Math.abs(bestRaw - runnerUp.score) / bestRaw)) : 0;
    const evidenceStrength = Math.min(1, (top[0]?.rank.score || 0) / 9);
    const alternativeCoverage = best?.coverage || 0;
    let confidence = Math.min(0.99, 0.32 * evidenceStrength + 0.43 * separation + 0.25 * alternativeCoverage + (best?.direct ? 0.16 : 0));
    if (negativePrompt && alternativeScores.filter((entry) => entry.score > 0.6).length < Math.max(2, alternatives.length - 1)) confidence *= 0.55;
    confidence = Math.round(confidence * 100) / 100;
    const suggestedIndex = bestRaw >= 0.55 && confidence >= 0.5 ? best.index : null;
    const suggestedLetter = suggestedIndex == null ? "" : (alternatives[suggestedIndex]?.letter || String.fromCharCode(65 + suggestedIndex));
    const currentIndex = Number.isInteger(question?.correctIndex) ? question.correctIndex : Math.max(0, alternatives.findIndex((entry) => entry.letter === question?.correctLetter));
    const agreement = suggestedIndex == null ? null : suggestedIndex === currentIndex;
    let status = "review";
    if (alignmentScore < 22 || suggestedIndex == null) status = "insufficient";
    else if (confidence >= 0.78 && agreement === false) status = "mismatch";
    else if (confidence >= 0.66 && agreement === true) status = "supported";
    const warnings = [];
    if (negativePrompt) warnings.push("O enunciado pede a alternativa incorreta/exceção; a inferência exige atenção adicional.");
    if (alignmentScore < 45) warnings.push("A correspondência temática com a base é parcial.");
    if (subjectTerms.length && index.documents.some((document) => document.subject) && subjectScore === 0) warnings.push("Os melhores trechos não possuem a mesma identificação de disciplina da questão; confira a classificação dos materiais.");
    if (suggestedIndex == null) warnings.push("A base não sustentou uma única alternativa com confiança suficiente.");
    else if (!agreement) warnings.push(`A base favorece ${suggestedLetter}, mas o DOCX marca ${question.correctLetter || String.fromCharCode(65 + currentIndex)}.`);
    const evidence = top.map((chunk) => ({
      documentId: chunk.documentId,
      documentName: chunk.documentName,
      chunkId: chunk.id,
      score: Math.round(chunk.rank.score * 100) / 100,
      coverage: Math.round(chunk.rank.coverage * 100),
      excerpt: evidenceExcerpt(chunk.text, matchedTerms)
    }));
    const feedbackBasis = suggestedIndex == null ? "" : supportingSentence(top[0].text, alternatives[suggestedIndex]?.plain || "");
    let feedbackSuggestion = suggestedIndex == null ? "" : `A alternativa ${suggestedLetter} está correta porque ${feedbackBasis.replace(/^[A-ZÀ-Ý]/u, (letter) => letter.toLocaleLowerCase("pt-BR"))}`;
    if (FORBIDDEN_STUDENT_REFERENCE.test(normalize(feedbackSuggestion))) {
      feedbackSuggestion = "";
      warnings.push("A evidência contém referência ao arquivo de origem; corrija o feedback manualmente para manter o texto autônomo.");
    }
    return {
      status,
      confidence,
      suggestedIndex,
      suggestedLetter,
      currentIndex,
      currentLetter: question?.correctLetter || String.fromCharCode(65 + currentIndex),
      agreement,
      negativePrompt,
      alternativeScores: alternativeScores.map((entry) => ({ ...entry, score: Math.round(entry.score * 100) / 100 })),
      alignment: { score: alignmentScore, subjectScore, matchedTerms: matchedTerms.slice(0, 18), missingTerms: queryTerms.filter((term) => !matchedTerms.includes(term)).slice(0, 12) },
      evidence,
      warnings,
      feedbackSuggestion,
      analyzedAt: new Date().toISOString(),
      baseUpdatedAt: base?.updatedAt || null,
      baseSummary
    };
  }

  function analyzeQuestions(questions, base) {
    return (questions || []).map((question) => analyzeQuestion(question, base));
  }

  function cacheSignature(base) {
    return `${base.updatedAt || ""}:${base.documents.length}:${base.generationHistory.length}:${base.activeCollectionId || ""}`;
  }

  function cachedCalculation(base, key, calculate) {
    const signature = cacheSignature(base);
    let entry = statsCache.get(base);
    if (!entry || entry.signature !== signature) {
      entry = { signature, values: new Map() };
      statsCache.set(base, entry);
    }
    if (!entry.values.has(key)) entry.values.set(key, calculate());
    return entry.values.get(key);
  }

  function baseStats(base, collectionId) {
    const source = hydrateBase(base);
    const targetId = collectionId && source.collections.some((collection) => collection.id === collectionId) ? collectionId : "";
    return cachedCalculation(source, `base:${targetId || "all"}`, () => {
      const hydrated = targetId ? scopeBase(source, targetId) : source;
      const premiumAudit = root.AvaliaPremiumCurator?.baseAudit(hydrated) || null;
      return {
        documents: hydrated.documents.length,
        chunks: hydrated.documents.reduce((total, document) => total + (document.chunks?.length || 0), 0),
        words: hydrated.documents.reduce((total, document) => total + Number(document.wordCount || 0), 0),
        characters: hydrated.documents.reduce((total, document) => total + Number(document.characterCount || document.text?.length || 0), 0),
        generatedHistory: hydrated.generationHistory.length,
        updatedAt: hydrated.updatedAt,
        collections: source.collections.length,
        activeCollectionId: hydrated.activeCollectionId,
        roles: premiumAudit?.counts || {},
        conflicts: premiumAudit?.conflicts?.length || 0,
        quarantined: premiumAudit?.quarantineCount || 0,
        objectives: premiumAudit?.objectives || 0,
        curricularUas: premiumAudit?.uas || 0,
        modelQuestions: premiumAudit?.modelQuestions || 0,
        safeFacts: premiumAudit?.safeFacts || 0,
        premiumAudit
      };
    });
  }

  function collectionStats(base) {
    const hydrated = hydrateBase(base);
    return cachedCalculation(hydrated, "collections", () => {
      const counters = new Map(hydrated.collections.map((collection) => [collection.id, { documents: 0, safeFacts: 0, objectives: 0, quarantined: 0 }]));
      hydrated.documents.forEach((document) => {
        const count = counters.get(document.collectionId);
        if (!count) return;
        count.documents += 1;
        count.safeFacts += Number(document.analysis?.evidence?.facts?.length || 0);
        count.objectives += Number(document.analysis?.curriculum?.specificObjectives?.length || 0);
        count.quarantined += Number(document.analysis?.quarantine?.count || 0);
      });
      return listCollections(hydrated).map((collection) => ({
        id: collection.id,
        name: collection.name,
        evaluation: collection.evaluation,
        subject: collection.subject,
        ...(counters.get(collection.id) || { documents: 0, safeFacts: 0, objectives: 0, quarantined: 0 }),
        updatedAt: collection.updatedAt
      }));
    });
  }

  function baseFingerprint(value) {
    return fnv1a(JSON.stringify(value && typeof value === "object" ? value : {}));
  }

  function integrityReport(base) {
    const source = hydrateBase(base);
    const blocking = [];
    const warnings = [];
    const collectionIds = new Set(source.collections.map((collection) => collection.id));
    const documentIds = new Set();
    const documentKeys = new Set();
    let totalCharacters = 0;
    let staleIndexes = 0;
    let unclassified = 0;
    source.documents.forEach((document, index) => {
      const label = document.name || `material ${index + 1}`;
      if (!document.id || documentIds.has(document.id)) blocking.push(`ID de material ausente ou repetido: ${label}.`);
      if (document.id) documentIds.add(document.id);
      if (!collectionIds.has(document.collectionId)) blocking.push(`${label}: coleção inexistente.`);
      if (!document.text || document.text.length < 80) blocking.push(`${label}: texto insuficiente ou ausente.`);
      if (!document.fingerprint) warnings.push(`${label}: assinatura de conteúdo ausente.`);
      const duplicateKey = `${document.collectionId}:${document.fingerprint || normalize(document.name)}`;
      if (documentKeys.has(duplicateKey)) warnings.push(`${label}: conteúdo repetido dentro da mesma coleção.`);
      documentKeys.add(duplicateKey);
      if (document.indexVersion !== INDEX_VERSION || !Array.isArray(document.chunks)) staleIndexes += 1;
      if (!document.role || !document.subject) unclassified += 1;
      totalCharacters += Number(document.characterCount || document.text?.length || 0);
    });
    if (source.documents.length > MAX_DOCUMENTS) blocking.push(`O acervo ultrapassa o limite de ${MAX_DOCUMENTS} materiais.`);
    if (totalCharacters > MAX_BASE_TEXT_CHARS) blocking.push("O acervo ultrapassa o limite de 50 milhões de caracteres.");
    const orphanHistory = source.generationHistory.filter((entry) => entry && typeof entry === "object" && !collectionIds.has(entry.collectionId)).length;
    if (staleIndexes) warnings.push(`${staleIndexes} material(is) precisam ter o índice reconstruído.`);
    if (unclassified) warnings.push(`${unclassified} material(is) ainda não possuem disciplina ou função completas.`);
    if (orphanHistory) warnings.push(`${orphanHistory} registro(s) de geração apontam para coleção inexistente.`);
    const deductions = Math.min(100, blocking.length * 35 + warnings.length * 5);
    return {
      ok: blocking.length === 0,
      status: blocking.length ? "invalid" : warnings.length ? "attention" : "healthy",
      score: Math.max(0, 100 - deductions),
      blocking,
      warnings,
      counts: {
        collections: source.collections.length,
        documents: source.documents.length,
        generationHistory: source.generationHistory.length,
        totalCharacters,
        staleIndexes,
        unclassified,
        orphanHistory
      },
      fingerprint: baseFingerprint(source),
      checkedAt: new Date().toISOString()
    };
  }

  function parseUaScope(value) {
    const text = String(value || "");
    const values = [];
    for (const match of text.matchAll(/(?:UA\s*)?(\d{1,2})\s*(?:a|at[eé]|[-–—])\s*(?:UA\s*)?(\d{1,2})/gi)) {
      const start = normalizeUa(match[1]);
      const end = normalizeUa(match[2]);
      if (!start || !end) continue;
      for (let ua = Math.min(start, end); ua <= Math.max(start, end); ua += 1) values.push(ua);
    }
    const withoutRanges = text.replace(/(?:UA\s*)?\d{1,2}\s*(?:a|at[eé]|[-–—])\s*(?:UA\s*)?\d{1,2}/gi, " ");
    for (const match of withoutRanges.matchAll(/(?:\bUA\s*)?(\d{1,2})\b/gi)) {
      const ua = normalizeUa(match[1]);
      if (ua) values.push(ua);
    }
    return [...new Set(values)].sort((left, right) => left - right);
  }

  function parseGenerationRules(ruleText, options) {
    if (!root.SmartFoxAthus) throw new Error("Atualize todos os arquivos da extensão para carregar as regras Athus.");
    return root.SmartFoxAthus.resolve(ruleText, options || {});
  }

  function detectMaterialUa(name, text, explicitUa) {
    const normalizedName = String(name || "").replace(/[_-]+/g, " ");
    const pattern = /\b(?:UA|unidade(?:\s+de\s+aprendizagem)?)\s*0?(\d{1,2})\b/gi;
    const fromName = [...normalizedName.matchAll(pattern)].map((match) => Number(match[1])).filter((ua) => ua >= 1 && ua <= 30);
    const headings = [...String(text || "").matchAll(/^\s*(?:unidade(?:\s+de\s+aprendizagem)?\s*(?:UA\s*)?|UA\s*)0?(\d{1,2})\b/gim)].map((match) => Number(match[1])).filter((ua) => ua >= 1 && ua <= 30);
    const names = [...new Set(fromName)], internal = [...new Set(headings)];
    const manual = normalizeUa(explicitUa);
    if (manual && internal.some((ua) => ua !== Number(manual))) return { ua: null, conflict: true, message: "A UA informada diverge dos títulos internos. Deixe o campo vazio para respeitar cada UA." };
    if (!manual && names.length === 1 && internal.length === 1 && names[0] !== internal[0]) return { ua: null, conflict: true, message: "A UA do nome diverge da UA interna. Confira o arquivo antes de importar." };
    return { ua: manual || (internal.length > 1 ? null : internal[0] || (names.length === 1 ? names[0] : null)), conflict: false,
      source: manual ? "informada" : internal.length ? "títulos internos" : names.length === 1 ? "nome do arquivo" : "não identificada", multiple: internal.length > 1 };
  }

  async function expandMaterialBatch(files) {
    const expanded = [], failures = [], names = new Set();
    let totalBytes = 0;
    const maxTotal = 150 * 1024 * 1024;
    const append = (file) => {
      if (names.has(file.name.toLocaleLowerCase())) throw new Error("Nome repetido no lote. Renomeie o arquivo para diferenciá-lo.");
      if (expanded.length >= 100) throw new Error("Limite de 100 arquivos por lote. Divida o envio em dois lotes.");
      if (file.size > MAX_FILE_BYTES) throw new Error("O arquivo ultrapassa 35 MB.");
      if (totalBytes + file.size > maxTotal) throw new Error("O lote ultrapassa 150 MB descompactados. Divida o envio.");
      totalBytes += file.size; names.add(file.name.toLocaleLowerCase()); expanded.push(file);
    };
    for (const file of files) {
      try {
        if (!/\.zip$/i.test(file.name)) { append(file); continue; }
        if (file.size > MAX_FILE_BYTES) throw new Error("O ZIP ultrapassa 35 MB.");
        if (!root.JSZip) throw new Error("O leitor ZIP não foi carregado. Recarregue a extensão.");
        const zip = await root.JSZip.loadAsync(await file.arrayBuffer());
        const entries = Object.values(zip.files).filter((entry) => !entry.dir && !/(^|\/)__MACOSX\//.test(entry.name) && SUPPORTED_EXTENSIONS.includes(entry.name.split('.').pop().toLowerCase()));
        if (!entries.length) throw new Error("O ZIP não contém materiais em formatos compatíveis.");
        for (const entry of entries) {
          try {
            const size = entry._data?.uncompressedSize;
            if (!Number.isFinite(size) || size > MAX_FILE_BYTES || totalBytes + size > maxTotal || expanded.length >= 100) throw new Error("Limite de tamanho ou quantidade do lote excedido.");
            const data = await entry.async("uint8array");
            append(new File([data], entry.name.replace(/\//g, "__"), { type: "application/octet-stream" }));
          } catch (error) { failures.push(file.name + "/" + entry.name + ": " + error.message); }
        }
      } catch (error) { failures.push(file.name + ": " + error.message); }
    }
    return { files: expanded, failures };
  }

  function generateQuestions(base, ruleText, options) {
    const rules = parseGenerationRules(ruleText, options || {});
    if (root.SmartFoxLocalQuestionGenerator) return root.SmartFoxLocalQuestionGenerator.generate(hydrateBase(base), rules, options || {});
    const message = "O módulo de criação local não foi carregado. Atualize a extensão e recarregue a aba do AvaliA.";
    return { questions: [], requested: rules.totalCount, produced: 0, rules, status: "unavailable", manualReviewRequired: true,
      rejected: [{ source: "Gerador", reason: message, sentence: "" }], message };
  }

  root.AvaliaKnowledgeBase = Object.freeze({
    version: VERSION,
    schemaVersion: SCHEMA_VERSION,
    defaultRules: DEFAULT_ATHUS_RULES,
    supportedExtensions: SUPPORTED_EXTENSIONS,
    collectionEvaluations: COLLECTION_EVALUATIONS,
    defaultCollectionId: DEFAULT_COLLECTION_ID,
    normalize,
    cleanText,
    tokens,
    fnv1a,
    splitIntoChunks,
    createEmptyBase,
    hydrateBase,
    activeCollection,
    listCollections,
    upsertCollection,
    selectCollection,
    removeCollection,
    updateCollectionPreferences,
    scopeBase,
    mergeBases,
    collectionStats,
    extractOoxml,
    extractFile,
    buildDocument,
    addOrReplace,
    removeDocument,
    clearCollection,
    updateDocumentMetadata,
    updateCollectionDocumentSubjects,
    reanalyzeCollectionDocuments,
    analyzeQuestion,
    analyzeQuestions,
    baseStats,
    baseFingerprint,
    integrityReport,
    parseUaScope,
    parseGenerationRules,
    detectMaterialUa,
    expandMaterialBatch,
    generateQuestions
  });
})(typeof window !== "undefined" ? window : globalThis);
