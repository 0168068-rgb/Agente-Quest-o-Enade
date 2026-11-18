(function () {
  "use strict";

  const VERSION = "11.0.0";
  const SCHEMA_VERSION = 1;
  const MAX_FILES = 600;
  const MAX_SUBMISSIONS = 5000;

  function normalizeSpaces(value) {
    return String(value == null ? "" : value).replace(/\s+/g, " ").trim();
  }

  function normalizeForMatch(value) {
    return normalizeSpaces(value)
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase();
  }

  function normalizeFileName(value) {
    return normalizeForMatch(value)
      .replace(/\.docx$/i, "")
      .replace(/\s*(?:\(\s*\d+\s*\)|[-_ ](?:copia|copy)(?:[-_ ]\d+)?)\s*$/i, "")
      .replace(/[_\-.]+/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function fnv1a(value) {
    let hash = 0x811c9dc5;
    for (const character of String(value || "")) {
      hash ^= character.charCodeAt(0);
      hash = Math.imul(hash, 0x01000193);
    }
    return (hash >>> 0).toString(16).padStart(8, "0");
  }

  function questionFingerprint(question) {
    if (question?.duplicateFingerprint) return String(question.duplicateFingerprint);
    const normalized = [
      question?.bodyText,
      ...(question?.alternatives || []).map((alternative) => alternative?.plain),
      question?.correctLetter,
      question?.expectedResponseText,
      question?.questionFormat,
      question?.feedbackText
    ].map(normalizeForMatch).join("\u241f");
    return fnv1a(normalized);
  }

  function createEmptyLedger() {
    const now = new Date().toISOString();
    return { schemaVersion: SCHEMA_VERSION, version: VERSION, createdAt: now, updatedAt: now, files: [], submissions: [] };
  }

  function uniqueBy(items, identity) {
    const seen = new Set();
    return (items || []).filter((item) => {
      const key = identity(item);
      if (!key || seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }

  function hydrateLedger(raw) {
    const empty = createEmptyLedger();
    if (!raw || typeof raw !== "object") return empty;
    const files = (Array.isArray(raw.files) ? raw.files : []).filter((entry) => entry && entry.fileFingerprint && entry.fileName);
    const submissions = (Array.isArray(raw.submissions) ? raw.submissions : []).filter((entry) => entry && entry.questionFingerprint);
    return {
      ...empty,
      createdAt: raw.createdAt || empty.createdAt,
      updatedAt: raw.updatedAt || empty.updatedAt,
      files: uniqueBy(files, (entry) => entry.id || `${entry.runId}:${entry.fileFingerprint}:${entry.importedAt}`).slice(-MAX_FILES),
      submissions: uniqueBy(submissions, (entry) => entry.identity || entry.id || `${entry.status}:${entry.avaliaId || ""}:${entry.runId}:${entry.questionIndex}:${entry.questionFingerprint}`).slice(-MAX_SUBMISSIONS)
    };
  }

  function fileDescriptor(input) {
    return {
      fileName: normalizeSpaces(input?.fileName || input?.name || "arquivo.docx"),
      normalizedName: normalizeFileName(input?.fileName || input?.name || "arquivo.docx"),
      fileFingerprint: normalizeSpaces(input?.fileFingerprint),
      questionCount: Number(input?.questionCount ?? input?.questions?.length ?? 0)
    };
  }

  function scan(ledgerInput, input) {
    const ledger = hydrateLedger(ledgerInput);
    const descriptor = fileDescriptor(input);
    const files = ledger.files || [];
    const exactFileMatches = files.filter((entry) => entry.fileFingerprint === descriptor.fileFingerprint && descriptor.fileFingerprint);
    const sameNameMatches = files.filter((entry) => entry.normalizedName === descriptor.normalizedName && descriptor.normalizedName && entry.fileFingerprint !== descriptor.fileFingerprint);
    const renamedContentMatches = exactFileMatches.filter((entry) => entry.normalizedName !== descriptor.normalizedName);
    const sameNameAndContentMatches = exactFileMatches.filter((entry) => entry.normalizedName === descriptor.normalizedName);
    const submissionsByFingerprint = new Map();
    (ledger.submissions || []).forEach((entry) => {
      const matches = submissionsByFingerprint.get(entry.questionFingerprint) || [];
      matches.push(entry);
      submissionsByFingerprint.set(entry.questionFingerprint, matches);
    });
    const questionMatches = (input?.questions || []).map((question, questionIndex) => {
      const fingerprint = questionFingerprint(question);
      const matches = (submissionsByFingerprint.get(fingerprint) || []).slice().sort((left, right) => String(right.recordedAt || "").localeCompare(String(left.recordedAt || "")));
      return matches.length ? {
        questionIndex,
        questionNumber: question?.number ?? questionIndex + 1,
        questionName: question?.name || `Questão ${questionIndex + 1}`,
        questionFingerprint: fingerprint,
        matches
      } : null;
    }).filter(Boolean);
    return {
      scannedAt: new Date().toISOString(),
      scope: "Histórico local deste perfil do Chrome e registros concluídos pela extensão.",
      descriptor,
      exactFileMatches,
      sameNameMatches,
      renamedContentMatches,
      sameNameAndContentMatches,
      questionMatches,
      summary: {
        sameFileImports: sameNameAndContentMatches.length,
        sameNameDifferentContent: sameNameMatches.length,
        renamedSameContent: renamedContentMatches.length,
        previouslySubmittedQuestions: questionMatches.length
      }
    };
  }

  function recordImport(ledgerInput, input) {
    const ledger = hydrateLedger(ledgerInput);
    const descriptor = fileDescriptor(input);
    if (!descriptor.fileFingerprint) return ledger;
    const importedAt = input?.importedAt || new Date().toISOString();
    const runId = normalizeSpaces(input?.runId || "sem-lote");
    const id = fnv1a(`${runId}|${descriptor.fileFingerprint}|${importedAt}`);
    if (!ledger.files.some((entry) => entry.id === id)) ledger.files.push({ id, importedAt, runId, ...descriptor });
    ledger.files = ledger.files.slice(-MAX_FILES);
    ledger.updatedAt = new Date().toISOString();
    ledger.version = VERSION;
    return ledger;
  }

  function recordSubmission(ledgerInput, input) {
    const ledger = hydrateLedger(ledgerInput);
    const fingerprint = normalizeSpaces(input?.questionFingerprint || questionFingerprint(input?.question));
    if (!fingerprint) return ledger;
    const recordedAt = input?.recordedAt || new Date().toISOString();
    const status = input?.status === "official" ? "official" : "draft";
    const avaliaId = normalizeSpaces(input?.avaliaId || "");
    const runId = normalizeSpaces(input?.runId || "sem-lote");
    const questionIndex = Number(input?.questionIndex ?? -1);
    const identity = avaliaId
      ? `${status}|${avaliaId}|${fingerprint}`
      : `${status}|${runId}|${questionIndex}|${fingerprint}`;
    if (ledger.submissions.some((entry) => entry.identity === identity)) return ledger;
    ledger.submissions.push({
      id: fnv1a(`${identity}|${recordedAt}`), identity, recordedAt, status, avaliaId, runId,
      fileName: normalizeSpaces(input?.fileName || ""), fileFingerprint: normalizeSpaces(input?.fileFingerprint || ""),
      questionIndex, questionNumber: input?.questionNumber ?? questionIndex + 1,
      questionName: normalizeSpaces(input?.questionName || input?.question?.name || `Questão ${questionIndex + 1}`),
      questionFingerprint: fingerprint
    });
    ledger.submissions = ledger.submissions.slice(-MAX_SUBMISSIONS);
    ledger.updatedAt = new Date().toISOString();
    ledger.version = VERSION;
    return ledger;
  }

  function stats(ledgerInput) {
    const ledger = hydrateLedger(ledgerInput);
    return {
      files: ledger.files.length,
      submissions: ledger.submissions.length,
      drafts: ledger.submissions.filter((entry) => entry.status === "draft").length,
      official: ledger.submissions.filter((entry) => entry.status === "official").length,
      oldestAt: [...ledger.files, ...ledger.submissions].map((entry) => entry.importedAt || entry.recordedAt).filter(Boolean).sort()[0] || "",
      updatedAt: ledger.updatedAt
    };
  }

  function ledgerFingerprint(ledgerInput) {
    const ledger = hydrateLedger(ledgerInput);
    return fnv1a(JSON.stringify({
      files: ledger.files.map((entry) => [entry.id, entry.importedAt, entry.runId, entry.fileName, entry.fileFingerprint, entry.questionCount]),
      submissions: ledger.submissions.map((entry) => [entry.identity, entry.recordedAt, entry.status, entry.avaliaId, entry.runId, entry.fileName, entry.questionFingerprint])
    }));
  }

  function mergeLedgers(currentInput, incomingInput) {
    const current = hydrateLedger(currentInput);
    const incoming = hydrateLedger(incomingInput);
    const before = stats(current);
    const merged = hydrateLedger({
      ...current,
      createdAt: current.createdAt || incoming.createdAt,
      updatedAt: new Date().toISOString(),
      files: [...current.files, ...incoming.files],
      submissions: [...current.submissions, ...incoming.submissions]
    });
    const after = stats(merged);
    return { ledger: merged, filesAdded: Math.max(0, after.files - before.files), submissionsAdded: Math.max(0, after.submissions - before.submissions) };
  }

  window.AvaliaDuplicateLedger = Object.freeze({
    version: VERSION,
    schemaVersion: SCHEMA_VERSION,
    maxFiles: MAX_FILES,
    maxSubmissions: MAX_SUBMISSIONS,
    normalizeFileName,
    questionFingerprint,
    createEmptyLedger,
    hydrateLedger,
    scan,
    recordImport,
    recordSubmission,
    stats,
    ledgerFingerprint,
    mergeLedgers
  });
})();
