(function (root) {
  "use strict";

  const SCHEMA_VERSION = 7;
  const EXTENSION_VERSION = "11.0.0";
  const REQUIRED_ALTERNATIVES = 4;

  const PHASES = Object.freeze({
    PENDING: "pending",
    FILLING: "filling",
    FILLED: "filled",
    SAVING: "saving",
    DRAFT_SAVED: "draft_saved",
    PREPARING: "preparing",
    READY_TO_SUBMIT: "ready_to_submit",
    SUBMITTING: "submitting",
    NEEDS_VERIFICATION: "needs_verification",
    SUBMITTED: "submitted",
    COMPLETED: "completed",
    SKIPPED: "skipped"
  });

  const PHASE_LABELS = Object.freeze({
    [PHASES.PENDING]: "Aguardando",
    [PHASES.FILLING]: "Preenchendo",
    [PHASES.FILLED]: "Preenchida e conferida",
    [PHASES.SAVING]: "Salvando",
    [PHASES.DRAFT_SAVED]: "Rascunho confirmado",
    [PHASES.PREPARING]: "Concluindo etapas obrigatórias",
    [PHASES.READY_TO_SUBMIT]: "Pronta para envio",
    [PHASES.SUBMITTING]: "Enviando oficialmente",
    [PHASES.NEEDS_VERIFICATION]: "Aguardando verificação segura",
    [PHASES.SUBMITTED]: "Envio confirmado",
    [PHASES.COMPLETED]: "Concluída",
    [PHASES.SKIPPED]: "Ignorada; lote continuou"
  });

  const ALLOWED_TRANSITIONS = Object.freeze({
    [PHASES.PENDING]: [PHASES.FILLING, PHASES.SKIPPED],
    [PHASES.FILLING]: [PHASES.FILLED, PHASES.PENDING, PHASES.SKIPPED],
    [PHASES.FILLED]: [PHASES.SAVING, PHASES.FILLING, PHASES.SKIPPED],
    [PHASES.SAVING]: [PHASES.DRAFT_SAVED, PHASES.FILLED, PHASES.SKIPPED],
    [PHASES.DRAFT_SAVED]: [PHASES.PREPARING, PHASES.COMPLETED, PHASES.SKIPPED],
    [PHASES.PREPARING]: [PHASES.READY_TO_SUBMIT, PHASES.DRAFT_SAVED, PHASES.SKIPPED],
    [PHASES.READY_TO_SUBMIT]: [PHASES.SUBMITTING, PHASES.PREPARING, PHASES.SKIPPED],
    [PHASES.SUBMITTING]: [PHASES.SUBMITTED, PHASES.NEEDS_VERIFICATION],
    [PHASES.NEEDS_VERIFICATION]: [PHASES.SUBMITTED],
    [PHASES.SUBMITTED]: [PHASES.COMPLETED],
    [PHASES.COMPLETED]: [],
    [PHASES.SKIPPED]: []
  });

  function normalize(value) {
    return String(value == null ? "" : value)
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/<[^>]*>/g, " ")
      .replace(/\s+/g, " ")
      .trim()
      .toLowerCase();
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

  function questionFingerprint(question) {
    const alternatives = Array.isArray(question && question.alternatives)
      ? question.alternatives.map((alternative) => alternative.plain || alternative.html || "")
      : [];
    return fnv1a([
      normalize(question && question.name),
      normalize(question && (question.bodyText || question.bodyHtml)),
      ...alternatives.map(normalize),
      normalize(question && question.correctLetter),
      normalize(question && (question.expectedResponseText || question.expectedResponseHtml)),
      normalize(question && (question.feedbackText || question.feedbackHtml)),
      normalize(question && question.typeId),
      normalize(question && question.cognitiveId),
      normalize(question && (question.richSignature || question.richIntegrity?.signature || ""))
    ].join("\u241f"));
  }

  function fileFingerprint(parsed) {
    return fnv1a((parsed && parsed.questions || []).map((question) =>
      question.fingerprint || questionFingerprint(question)).join("|"));
  }

  function makeRunId() {
    const random = Math.random().toString(36).slice(2, 10);
    return `aab-${Date.now().toString(36)}-${random}`;
  }

  function nowIso() {
    return new Date().toISOString();
  }

  function semesterName(name, date = new Date()) {
    const parts = new Intl.DateTimeFormat('en-US', {timeZone:'America/Sao_Paulo',year:'numeric',month:'numeric'}).formatToParts(date);
    const year=parts.find(p=>p.type==='year').value, month=Number(parts.find(p=>p.type==='month').value);
    const base=String(name||'').trim().replace(/(?:\s*[-–—|·]?\s*\(?20\d{2}\.[12]\)?)+$/,'').trim();
    return base ? `${base} — ${year}.${month<=6?1:2}` : '';
  }
  function createSession(parsed, options) {
    if (!parsed || !Array.isArray(parsed.questions) || !parsed.questions.length) {
      throw new Error("Não há questões válidas para criar a sessão.");
    }
    parsed.questions.forEach(q => { q.name = semesterName(q.name); });
    const settings = options || {};
    const createdAt = nowIso();
    return {
      schemaVersion: SCHEMA_VERSION,
      extensionVersion: EXTENSION_VERSION,
      runId: settings.runId || makeRunId(),
      fileName: settings.fileName || parsed.fileName || "avaliação.docx",
      fileFingerprint: parsed.fileFingerprint || fileFingerprint(parsed),
      outputMode: settings.outputMode === "draft" ? "draft" : "official",
      fillKeywords: settings.fillKeywords !== false,
      status: "ready",
      currentIndex: 0,
      createdAt,
      updatedAt: createdAt,
      completedAt: null,
      parsed,
      results: [],
      tagConfig: {
        catalogSummary: settings.tagCatalogSummary || null,
        target: settings.targetTag || null,
        syncLatestOnly: Boolean(settings.syncLatestOnly),
        verifiedInStep3: false,
        verifiedAt: null
      },
      approvalSync: {
        enabled: Boolean(settings.syncLatestOnly),
        status: settings.syncLatestOnly ? "waiting_for_batch" : "not_requested",
        plan: null,
        processedIds: [],
        errors: [],
        updatedAt: createdAt
      },
      items: parsed.questions.map((question, index) => ({
        index,
        instanceKey: `${question.fingerprint || questionFingerprint(question)}:${index + 1}`,
        number: question.number,
        name: question.name,
        fingerprint: question.fingerprint || questionFingerprint(question),
        originalFingerprint: question.fingerprint || questionFingerprint(question),
        phase: PHASES.PENDING,
        manualAuthorizedAt: null,
        manualAuthorizationNote: "",
        allocationAuthorizedAt: null,
        allocationAuthorizationNote: "",
        allocationAuthorizationScope: "",
        knowledgeDecision: "",
        knowledgeReviewedAt: null,
        knowledgeReviewNote: "",
        knowledgeCorrection: null,
        editCount: 0,
        draftId: "",
        submissionConfirmed: false,
        ignoredSuggestions: 0,
        lastError: "",
        lastErrorAt: null,
        lastProblem: null,
        errorHistory: [],
        skippedReason: "",
        skippedAt: null,
        attempts: { fill: 0, save: 0, prepare: 0, submit: 0, next: 0 },
        updatedAt: createdAt
      }))
    };
  }

  function migrateSessionV4(legacySession) {
    if (!legacySession || legacySession.schemaVersion !== 4 || !Array.isArray(legacySession.items) || !Array.isArray(legacySession.parsed?.questions)) {
      throw new Error("A sessão anterior não é compatível com a migração 4.x → 11.0.");
    }
    const session = JSON.parse(JSON.stringify(legacySession));
    session.schemaVersion = SCHEMA_VERSION;
    session.extensionVersion = EXTENSION_VERSION;
    session.continueOnError = true;
    session.migratedFrom = { schemaVersion: 4, extensionVersion: legacySession.extensionVersion || "4.0.0", at: nowIso() };
    session.items = session.items.map((item, index) => ({
      ...item,
      index,
      instanceKey: `${item.fingerprint || questionFingerprint(session.parsed.questions[index])}:${index + 1}`,
      lastProblem: null,
      errorHistory: Array.isArray(item.errorHistory) ? item.errorHistory : [],
      skippedReason: item.skippedReason || "",
      skippedAt: item.skippedAt || null
    }));
    session.results = (session.results || []).map((result, resultIndex) => {
      const matching = session.items.find((item) => item.fingerprint === result.fingerprint && !session.results.slice(0, resultIndex).some((previous) => previous.instanceKey === item.instanceKey));
      return { ...result, instanceKey: result.instanceKey || matching?.instanceKey || `${result.fingerprint || "legacy"}:result-${resultIndex + 1}` };
    });
    const active = currentItem(session);
    if (active && active.phase === PHASES.PREPARING && /tipo da questão|etapas obrigatórias/i.test(active.lastError || "")) {
      active.attempts.prepare = 0;
      active.lastError = "";
      active.lastErrorAt = null;
      active.lastProblem = null;
      active.migrationRepair = "Tentativas de preparação liberadas; metadados pós-salvamento serão conferidos pela regra 11.0.";
    }
    if (session.status !== "completed" && session.status !== "verification_required") session.status = "paused";
    session.updatedAt = nowIso();
    assertSession(session);
    return session;
  }

  function migrateSessionV5(legacySession) {
    if (!legacySession || legacySession.schemaVersion !== 5 || !Array.isArray(legacySession.items) || !Array.isArray(legacySession.parsed?.questions)) {
      throw new Error("A sessão anterior não é compatível com a migração 5.x → 11.0.");
    }
    const session = JSON.parse(JSON.stringify(legacySession));
    session.schemaVersion = SCHEMA_VERSION;
    session.extensionVersion = EXTENSION_VERSION;
    session.migratedFrom = { schemaVersion: 5, extensionVersion: legacySession.extensionVersion || "5.0.0", at: nowIso() };
    hydrateSession(session);
    if (session.status !== "completed" && session.status !== "verification_required") session.status = "paused";
    session.updatedAt = nowIso();
    assertSession(session);
    return session;
  }

  function migrateSessionV6(legacySession) {
    if (!legacySession || legacySession.schemaVersion !== 6 || !Array.isArray(legacySession.items) || !Array.isArray(legacySession.parsed?.questions)) {
      throw new Error("A sessão anterior não é compatível com a migração 6.x → 11.0.");
    }
    const session = JSON.parse(JSON.stringify(legacySession));
    session.schemaVersion = SCHEMA_VERSION;
    session.extensionVersion = EXTENSION_VERSION;
    session.migratedFrom = { schemaVersion: 6, extensionVersion: legacySession.extensionVersion || "6.0.0", at: nowIso() };
    hydrateSession(session);
    if (session.status !== "completed" && session.status !== "verification_required") session.status = "paused";
    session.updatedAt = nowIso();
    assertSession(session);
    return session;
  }

  function currentItem(session) {
    return session && Array.isArray(session.items) ? session.items[session.currentIndex] || null : null;
  }

  function hydrateSession(session) {
    if (!session || !Array.isArray(session.items)) return session;
    session.extensionVersion = EXTENSION_VERSION;
    session.continueOnError = session.continueOnError !== false;
    session.tagConfig = {
      catalogSummary: null,
      target: null,
      syncLatestOnly: false,
      verifiedInStep3: false,
      verifiedAt: null,
      ...(session.tagConfig || {})
    };
    session.approvalSync = {
      enabled: Boolean(session.tagConfig.syncLatestOnly),
      status: session.tagConfig.syncLatestOnly ? "waiting_for_batch" : "not_requested",
      plan: null,
      processedIds: [],
      errors: [],
      updatedAt: session.updatedAt || nowIso(),
      ...(session.approvalSync || {})
    };
    session.approvalSync.processedIds = Array.isArray(session.approvalSync.processedIds) ? session.approvalSync.processedIds : [];
    session.approvalSync.errors = Array.isArray(session.approvalSync.errors) ? session.approvalSync.errors : [];
    session.items.forEach((item, index) => {
      item.index = index;
      item.manualAuthorizedAt = item.manualAuthorizedAt || null;
      item.manualAuthorizationNote = item.manualAuthorizationNote || "";
      item.allocationAuthorizedAt = item.allocationAuthorizedAt || null;
      item.allocationAuthorizationNote = item.allocationAuthorizationNote || "";
      item.allocationAuthorizationScope = item.allocationAuthorizationScope || "";
      item.knowledgeDecision = item.knowledgeDecision || "";
      item.knowledgeReviewedAt = item.knowledgeReviewedAt || null;
      item.knowledgeReviewNote = item.knowledgeReviewNote || "";
      item.knowledgeCorrection = item.knowledgeCorrection || null;
      item.errorHistory = Array.isArray(item.errorHistory) ? item.errorHistory : [];
      item.attempts = { fill: 0, save: 0, prepare: 0, submit: 0, next: 0, ...(item.attempts || {}) };
    });
    return session;
  }

  function assertSession(session) {
    if (!session || session.schemaVersion !== SCHEMA_VERSION) throw new Error("Sessão incompatível com a versão 11.0.");
    hydrateSession(session);
    if (!Array.isArray(session.items) || !Array.isArray(session.parsed && session.parsed.questions)) {
      throw new Error("Sessão incompleta ou corrompida.");
    }
    if (session.items.length !== session.parsed.questions.length) throw new Error("A sessão não corresponde ao arquivo importado.");
    if (!Number.isInteger(session.currentIndex) || session.currentIndex < 0 || session.currentIndex > session.items.length) {
      throw new Error("Posição inválida na sessão.");
    }
    const instanceKeys = session.items.map((item) => item.instanceKey);
    if (instanceKeys.some((key) => !key) || new Set(instanceKeys).size !== instanceKeys.length) {
      throw new Error("A sessão contém ocorrências sem identificação única.");
    }
    const draftIds = session.items.map((item) => String(item.draftId || "")).filter(Boolean);
    if (new Set(draftIds).size !== draftIds.length) throw new Error("Um mesmo identificador do AvaliA foi associado a duas questões.");
    return true;
  }

  function touch(session, item) {
    const timestamp = nowIso();
    session.updatedAt = timestamp;
    if (item) item.updatedAt = timestamp;
  }

  function transition(session, nextPhase, patch) {
    assertSession(session);
    const item = currentItem(session);
    if (!item) throw new Error("Não há questão ativa na sessão.");
    const allowed = ALLOWED_TRANSITIONS[item.phase] || [];
    if (nextPhase !== item.phase && !allowed.includes(nextPhase)) {
      throw new Error(`Transição inválida: ${item.phase} → ${nextPhase}.`);
    }
    const itemBefore = JSON.parse(JSON.stringify(item));
    const sessionBefore = { status: session.status, updatedAt: session.updatedAt };
    item.phase = nextPhase;
    Object.assign(item, patch || {});
    item.lastError = "";
    item.lastErrorAt = null;
    item.lastProblem = patch && Object.prototype.hasOwnProperty.call(patch, "lastProblem") ? patch.lastProblem : null;
    session.status = "running";
    touch(session, item);
    try {
      assertSession(session);
    } catch (error) {
      Object.keys(item).forEach((key) => { delete item[key]; });
      Object.assign(item, itemBefore);
      session.status = sessionBefore.status;
      session.updatedAt = sessionBefore.updatedAt;
      throw error;
    }
    return item;
  }

  function incrementAttempt(session, action) {
    const item = currentItem(session);
    if (!item || !Object.prototype.hasOwnProperty.call(item.attempts, action)) {
      throw new Error(`Tentativa desconhecida: ${action}.`);
    }
    item.attempts[action] += 1;
    touch(session, item);
    return item.attempts[action];
  }

  function recordError(session, error, options) {
    const item = currentItem(session);
    const message = error instanceof Error ? error.message : String(error || "Falha não identificada.");
    if (item) {
      item.lastError = message;
      item.lastErrorAt = nowIso();
      item.lastProblem = options && options.problem ? { ...options.problem, message: options.problem.message || message } : { code: "EXECUTION_ERROR", message };
      item.errorHistory = Array.isArray(item.errorHistory) ? item.errorHistory : [];
      item.errorHistory.push({ at: item.lastErrorAt, phase: item.phase, ...item.lastProblem });
      if (item.errorHistory.length > 30) item.errorHistory.splice(0, item.errorHistory.length - 30);
      if (options && options.needsVerification) item.phase = PHASES.NEEDS_VERIFICATION;
    }
    session.status = options && options.needsVerification ? "verification_required" : "paused";
    touch(session, item);
    return message;
  }

  function updatePendingQuestion(session, index, question) {
    assertSession(session);
    if (!Number.isInteger(index) || index < 0 || index >= session.items.length) throw new Error("Questão inválida para edição.");
    const item = session.items[index];
    if (item.phase !== PHASES.PENDING) throw new Error("A questão só pode ser editada antes do início do preenchimento.");
    question.name = semesterName(question.name);
    const fingerprint = question.fingerprint || questionFingerprint(question);
    session.parsed.questions[index] = question;
    item.number = question.number;
    item.name = question.name;
    item.fingerprint = fingerprint;
    item.instanceKey = `${fingerprint}:${index + 1}`;
    item.manualAuthorizedAt = null;
    item.manualAuthorizationNote = "";
    item.allocationAuthorizedAt = null;
    item.allocationAuthorizationNote = "";
    item.allocationAuthorizationScope = "";
    item.knowledgeDecision = "";
    item.knowledgeReviewedAt = null;
    item.knowledgeReviewNote = "";
    item.knowledgeCorrection = null;
    item.editCount = Number(item.editCount || 0) + 1;
    session.fileFingerprint = fileFingerprint(session.parsed);
    touch(session, item);
    assertSession(session);
    return item;
  }

  function authorizeQuestion(session, index, note) {
    assertSession(session);
    if (!Number.isInteger(index) || index < 0 || index >= session.items.length) throw new Error("Questão inválida para autorização.");
    const item = session.items[index];
    const question = session.parsed.questions[index];
    if (item.phase !== PHASES.PENDING) throw new Error("A autorização só pode ser alterada antes do processamento da questão.");
    if (Array.isArray(question.hardErrors) && question.hardErrors.length) {
      throw new Error(`Corrija primeiro os campos técnicos obrigatórios: ${question.hardErrors.join(" ")}`);
    }
    item.manualAuthorizedAt = nowIso();
    item.manualAuthorizationNote = String(note || "Revisada e autorizada pelo usuário.");
    touch(session, item);
    return item;
  }

  function revokeAuthorization(session, index) {
    assertSession(session);
    if (!Number.isInteger(index) || index < 0 || index >= session.items.length) throw new Error("Questão inválida para revisão.");
    const item = session.items[index];
    if (item.phase !== PHASES.PENDING) throw new Error("A autorização não pode ser revogada após o início do processamento.");
    item.manualAuthorizedAt = null;
    item.manualAuthorizationNote = "";
    touch(session, item);
    return item;
  }

  function authorizeAllocation(session, index, note) {
    assertSession(session);
    if (!Number.isInteger(index) || index < 0 || index >= session.items.length) throw new Error("Questão inválida para aprovação da matéria.");
    const item = session.items[index];
    if (item.phase !== PHASES.PENDING) throw new Error("A alocação só pode ser aprovada antes do processamento da questão.");
    item.allocationAuthorizedAt = nowIso();
    item.allocationAuthorizationNote = String(note || "Correspondência com a disciplina conferida e aprovada pelo usuário.");
    touch(session, item);
    return item;
  }

  function revokeAllocationAuthorization(session, index) {
    assertSession(session);
    if (!Number.isInteger(index) || index < 0 || index >= session.items.length) throw new Error("Questão inválida para revisão da matéria.");
    const item = session.items[index];
    if (item.phase !== PHASES.PENDING) throw new Error("A aprovação da matéria não pode ser revogada após o início do processamento.");
    item.allocationAuthorizedAt = null;
    item.allocationAuthorizationNote = "";
    item.allocationAuthorizationScope = "";
    touch(session, item);
    return item;
  }

  function recordKnowledgeDecision(session, index, decision, note, correction) {
    assertSession(session);
    if (!Number.isInteger(index) || index < 0 || index >= session.items.length) throw new Error("Questão inválida para conferência com a base.");
    const item = session.items[index];
    if (item.phase !== PHASES.PENDING) throw new Error("A decisão sobre o material só pode ser alterada antes do processamento da questão.");
    const allowed = ["accepted", "kept", "corrected", "not_required"];
    if (!allowed.includes(decision)) throw new Error("Decisão de conferência inválida.");
    item.knowledgeDecision = decision;
    item.knowledgeReviewedAt = nowIso();
    item.knowledgeReviewNote = String(note || "Conferência com a base registrada pelo usuário.");
    item.knowledgeCorrection = correction ? JSON.parse(JSON.stringify(correction)) : null;
    touch(session, item);
    return item;
  }

  function revokeKnowledgeDecision(session, index) {
    assertSession(session);
    if (!Number.isInteger(index) || index < 0 || index >= session.items.length) throw new Error("Questão inválida para conferência com a base.");
    const item = session.items[index];
    if (item.phase !== PHASES.PENDING) throw new Error("A decisão sobre o material não pode ser revogada após o início.");
    item.knowledgeDecision = "";
    item.knowledgeReviewedAt = null;
    item.knowledgeReviewNote = "";
    item.knowledgeCorrection = null;
    touch(session, item);
    return item;
  }

  function resetAttempts(session, actions) {
    assertSession(session);
    const item = currentItem(session);
    if (!item) throw new Error("Não há questão ativa para liberar novas tentativas.");
    if ([PHASES.SUBMITTING, PHASES.NEEDS_VERIFICATION, PHASES.SUBMITTED, PHASES.COMPLETED].includes(item.phase)) {
      throw new Error("As tentativas não podem ser zeradas depois de um possível envio oficial.");
    }
    const selected = Array.isArray(actions) && actions.length ? actions : ["fill", "save", "prepare", "next"];
    selected.forEach((action) => {
      if (Object.prototype.hasOwnProperty.call(item.attempts, action)) item.attempts[action] = 0;
    });
    touch(session, item);
    return item.attempts;
  }

  function cleanupIds(session) {
    return Array.from(new Set([
      ...(session?.results||[]).filter(r=>r.status==="official").map(r=>String(r.id||"")),
      ...(session?.items||[]).filter(i=>i.submissionConfirmed).map(i=>String(i.draftId||""))
    ].filter(id=>/^[1-9]\d*$/.test(id))));
  }

  function needsBankCleanup(session) {
    if(!session?.bankCleanupEnabled) return false;
    const ids=cleanupIds(session), receipt=session.bankCleanupReceipt;
    if(!ids.length) return false;
    return !(receipt?.complete && receipt.runId===session.runId && receipt.owner===session.bankCleanupOwner
      && receipt.revision>0 && receipt.doneRevision===receipt.revision
      && ids.every(id=>receipt.questionIds?.includes(id))
      && (session.bankDestination||[]).every(scope=>(!scope.institutionId||receipt.institutionIds?.includes(scope.institutionId))
        && (scope.gradeDisciplineIds||[]).every(id=>receipt.targetIds?.includes(String(id)))));
  }

  function terminalStatus(session) {
    return session.currentIndex < session.items.length ? "running" : needsBankCleanup(session) ? "cleanup_pending" : "completed";
  }

  function setBankCleanupReceipt(session, receipt) {
    session.bankCleanupReceipt=JSON.parse(JSON.stringify(receipt||{complete:false}));
    if(session.currentIndex>=session.items.length) {
      session.status=terminalStatus(session);
      if(session.status==="completed") {session.completedAt=session.completedAt||nowIso();session.endedAt=session.endedAt||session.completedAt;}
      else {session.completedAt=null;session.endedAt=null;}
    }
    return !needsBankCleanup(session);
  }

  function skipCurrent(session, reason, details) {
    assertSession(session);
    const item = currentItem(session);
    if (!item) throw new Error("Não há questão ativa para ignorar.");
    if ([PHASES.SUBMITTING, PHASES.NEEDS_VERIFICATION, PHASES.SUBMITTED, PHASES.COMPLETED].includes(item.phase)) {
      throw new Error("Esta questão não pode ser ignorada porque pode ter sido enviada. Faça a verificação segura primeiro.");
    }
    transition(session, PHASES.SKIPPED, {
      skippedReason: String(reason || "Questão incompatível com a configuração atual do AvaliA."),
      skippedAt: nowIso(),
      lastProblem: details || item.lastProblem || null
    });
    if (!session.results.some((entry) => entry.instanceKey === item.instanceKey)) {
      session.results.push({
        number: item.number,
        name: item.name,
        fingerprint: item.fingerprint,
        instanceKey: item.instanceKey,
        id: item.draftId,
        status: "skipped",
        reason: item.skippedReason,
        skippedAt: item.skippedAt,
        ...(details || {})
      });
    }
    session.currentIndex += 1;
    session.status = terminalStatus(session);
    if (session.status === "completed") session.completedAt = nowIso();
    touch(session, item);
    assertSession(session);
    return item;
  }

  function completeCurrent(session, result) {
    assertSession(session);
    const item = currentItem(session);
    if (!item) throw new Error("Não há questão ativa para concluir.");
    if (item.phase === PHASES.DRAFT_SAVED && session.outputMode === "draft") {
      transition(session, PHASES.COMPLETED);
    } else {
      if (item.phase === PHASES.SUBMITTED) transition(session, PHASES.COMPLETED);
      else if (item.phase !== PHASES.COMPLETED) throw new Error(`A questão não pode ser concluída na fase ${item.phase}.`);
    }
    if (!session.results.some((entry) => entry.instanceKey === item.instanceKey)) {
      session.results.push({
        number: item.number,
        name: item.name,
        fingerprint: item.fingerprint,
        instanceKey: item.instanceKey,
        id: item.draftId,
        status: session.outputMode === "official" ? "official" : "draft",
        ignoredSuggestions: item.ignoredSuggestions || 0,
        completedAt: nowIso(),
        ...(result || {})
      });
    }
    session.currentIndex += 1;
    session.status = terminalStatus(session);
    if (session.status === "completed") session.completedAt = nowIso();
    touch(session, item);
    assertSession(session);
    return item;
  }

  function phaseLabel(phase) {
    return PHASE_LABELS[phase] || phase || "Desconhecida";
  }

  function officialIds(session) {
    assertSession(session);
    return Array.from(new Set((session.results || [])
      .filter((result) => result.status === "official")
      .map((result) => String(result.id || "").trim())
      .filter((id) => /^\d+$/.test(id))));
  }

  root.AvaliaBatchEngine = Object.freeze({
    schemaVersion: SCHEMA_VERSION,
    version: EXTENSION_VERSION,
    requiredAlternatives: REQUIRED_ALTERNATIVES,
    phases: PHASES,
    phaseLabel,
    normalize,
    fnv1a,
    questionFingerprint,
    fileFingerprint,
    semesterName,
    createSession,
    migrateSessionV4,
    migrateSessionV5,
    migrateSessionV6,
    hydrateSession,
    currentItem,
    assertSession,
    transition,
    incrementAttempt,
    resetAttempts,
    recordError,
    updatePendingQuestion,
    authorizeQuestion,
    revokeAuthorization,
    authorizeAllocation,
    revokeAllocationAuthorization,
    recordKnowledgeDecision,
    revokeKnowledgeDecision,
    skipCurrent,
    completeCurrent,
    officialIds,
    cleanupIds,
    needsBankCleanup,
    setBankCleanupReceipt
  });
})(typeof window !== "undefined" ? window : globalThis);
