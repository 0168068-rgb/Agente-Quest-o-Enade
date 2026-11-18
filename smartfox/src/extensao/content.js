(async function () {
  "use strict";

  if (window.top !== window.self || document.getElementById("aab-launcher")) return;
  if (/^\/CorrecaoDiscursiva(?:\/|$)/i.test(location.pathname)) return;
  if (!window.SmartFoxAccess || !(await window.SmartFoxAccess.requireAuthorized())) return;

  const PRODUCT_VERSION = "11.2.0";
  const PRODUCT_LABEL = "11.2";
  const PRODUCT_NAME = `SmartFox Autônomo ${PRODUCT_LABEL}`;
  const MESSAGE_CHANNEL = "AVALIA_AUTOBATCH";
  const STORAGE_KEY = "aabSessionV7";
  const LEGACY_STORAGE_KEYS = Object.freeze(["aabSessionV6", "aabSessionV41", "aabSessionV4"]);
  const OCCURRENCE_KEY = "aabOccurrenceStoreV7";
  const LEGACY_OCCURRENCE_KEY = "aabOccurrenceStoreV6";
  const KNOWLEDGE_KEY = "aabKnowledgeBaseV9";
  const DUPLICATE_LEDGER_KEY = "aabDuplicateLedgerV1";
  const STORAGE_HEALTH_KEY = "aabStorageHealthV9";
  const LEGACY_KNOWLEDGE_KEYS = Object.freeze(["aabKnowledgeBaseV7"]);
  const LOCK_KEY = "aabRunLockV7";
  const LOCK_TTL_MS = 20000;
  const OCCURRENCE_LIMIT = 500;
  const REQUIRED_ALTERNATIVES = 4;
  const Engine = window.AvaliaBatchEngine;
  const Curator = window.AvaliaPremiumCurator;
  const Knowledge = window.AvaliaKnowledgeBase;
  const ExternalExam = window.SmartFoxExternalExam;
  const Parser = window.AvaliaDocxParser;
  const Exporter = window.AvaliaDocxExporter;
  const StudentGuide = window.AvaliaStudentGuideExporter;
  const Athus = window.SmartFoxAthus;
  const Approval = window.AvaliaApprovalSync;
  const Duplicates = window.AvaliaDuplicateLedger;
  if (!Athus || !Engine || !Parser || !Knowledge || !ExternalExam || !Curator || !Exporter || !StudentGuide || !Approval || !Duplicates) return;
  const P = Engine.phases;
  let knowledgeWriteQueue = Promise.resolve();
  let sessionWriteQueue = Promise.resolve();
  let occurrenceWriteQueue = Promise.resolve();
  let duplicateLedgerWriteQueue = Promise.resolve();
  const actionsInFlight = new WeakSet();
  const workTasks = new Set();

  const app = {
    session: null,
    abandoning: false,
    abandonUncertain: false,
    generationController: null,
    running: false,
    approvalRunning: false,
    batchReviewBusy: false,
    stopRequested: false,
    heartbeatTimer: null,
    clockTimer: null,
    reviewIndex: 0,
    reviewFilter: "all",
    diagnosis: null,
    lastDisciplines: [],
    occurrences: [],
    occurrenceFilter: "all",
    occurrenceSearch: "",
    lastDiagnosisSignature: "",
    knownSiteErrors: new Set(),
    knowledgeBase: Knowledge.createEmptyBase(),
    duplicateLedger: Duplicates.createEmptyLedger(),
    knowledgeBusy: false,
    collectionEditorMode: "",
    editingMaterialId: "",
    fileImportFailure: null,
    fileImportBusy: false,
    fileRemovalBusy: false,
    fileDiagnosticFilter: "action",
    storageHealth: { status: "waiting", checkedAt: null, latencyMs: null, message: "Ainda não testado." },
    tagCatalog: null,
    pendingTagConfig: { target: null, syncLatestOnly: false },
    currentView: "prepare",
    externalExamReport: null
  };

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function assertWorkActive() {
    if (app.abandoning) throw Object.assign(new Error("Trabalho abandonado."), { code: "WORK_ABANDONED" });
  }

  function trackWork(task) {
    workTasks.add(task);
    task.then(() => workTasks.delete(task), () => workTasks.delete(task));
    return task;
  }

  function bridge(command, payload, timeoutMs) {
    assertWorkActive();
    const requestId = crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`;
    const timeout = timeoutMs || 40000;
    return new Promise((resolve, reject) => {
      const timer = window.setTimeout(() => {
        if (app.abandoning) app.abandonUncertain = true;
        window.removeEventListener("message", onMessage);
        reject(new Error(`[SEM_RESPOSTA] O AvaliA não respondeu ao comando ${command} em ${Math.round(timeout / 1000)} segundos.`));
      }, timeout);
      function onMessage(event) {
        const data = event.data;
        if (event.source !== window || event.origin !== location.origin) return;
        if (!data || data.channel !== MESSAGE_CHANNEL || data.direction !== "response" || data.requestId !== requestId) return;
        window.clearTimeout(timer);
        window.removeEventListener("message", onMessage);
        if (data.ok) resolve(data.data);
        else reject(new Error(data.error || "Falha não identificada no formulário."));
      }
      window.addEventListener("message", onMessage);
      window.postMessage({ channel: MESSAGE_CHANNEL, direction: "request", requestId, command, payload: payload || {} }, location.origin);
    });
  }

  function storageGet(key) {
    return new Promise((resolve, reject) => chrome.storage.local.get(key, (value) => {
      const error = chrome.runtime?.lastError;
      if (error) reject(new Error(`[ARMAZENAMENTO_LEITURA] ${error.message}`));
      else resolve(value);
    }));
  }

  function storageSet(value) {
    return new Promise((resolve, reject) => chrome.storage.local.set(value, () => {
      const error = chrome.runtime?.lastError;
      if (error) reject(new Error(`[ARMAZENAMENTO_GRAVACAO] ${error.message}`));
      else resolve();
    }));
  }

  function storageRemove(key) {
    return new Promise((resolve, reject) => chrome.storage.local.remove(key, () => {
      const error = chrome.runtime?.lastError;
      if (error) reject(new Error(`[ARMAZENAMENTO_REMOCAO] ${error.message}`));
      else resolve();
    }));
  }

  async function loadDuplicateLedger() {
    const stored = await storageGet(DUPLICATE_LEDGER_KEY);
    app.duplicateLedger = Duplicates.hydrateLedger(stored?.[DUPLICATE_LEDGER_KEY]);
    return app.duplicateLedger;
  }

  function persistDuplicateLedger() {
    const snapshot = Duplicates.hydrateLedger(app.duplicateLedger);
    app.duplicateLedger = snapshot;
    duplicateLedgerWriteQueue = duplicateLedgerWriteQueue.catch(() => {}).then(() => storageSet({ [DUPLICATE_LEDGER_KEY]: snapshot }));
    return duplicateLedgerWriteQueue;
  }

  async function registerImportedFile(file, parsed, runId) {
    app.duplicateLedger = Duplicates.recordImport(app.duplicateLedger, {
      fileName: file?.name || parsed?.fileName,
      fileFingerprint: parsed?.fileFingerprint,
      questionCount: parsed?.questions?.length,
      runId
    });
    await persistDuplicateLedger();
  }

  async function registerCompletedQuestion(question, item, completedId, questionIndex) {
    app.duplicateLedger = Duplicates.recordSubmission(app.duplicateLedger, {
      question,
      questionFingerprint: question?.duplicateFingerprint,
      questionIndex,
      questionNumber: question?.number,
      questionName: question?.name,
      avaliaId: completedId,
      status: app.session?.outputMode === "official" ? "official" : "draft",
      runId: app.session?.runId,
      fileName: app.session?.fileName,
      fileFingerprint: app.session?.fileFingerprint
    });
    await persistDuplicateLedger();
  }

  async function testLocalDatabase(options) {
    const startedAt = performance.now();
    const nonce = crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`;
    app.storageHealth = { status: "testing", checkedAt: new Date().toISOString(), latencyMs: null, message: "Testando gravação, leitura e remoção…" };
    renderSystemHealth();
    try {
      const probe = { nonce, at: new Date().toISOString(), version: PRODUCT_VERSION };
      await storageSet({ [STORAGE_HEALTH_KEY]: probe });
      const stored = await storageGet(STORAGE_HEALTH_KEY);
      if (stored?.[STORAGE_HEALTH_KEY]?.nonce !== nonce) throw new Error("A leitura não devolveu o mesmo registro gravado.");
      await storageRemove(STORAGE_HEALTH_KEY);
      const latencyMs = Math.max(1, Math.round(performance.now() - startedAt));
      app.storageHealth = { status: "healthy", checkedAt: new Date().toISOString(), latencyMs, message: `Gravação, leitura e remoção confirmadas em ${latencyMs} ms.` };
      if (!options?.silent) {
        setBaseProgress("success", `Armazenamento deste perfil aprovado em ${latencyMs} ms. O acervo e os checkpoints podem ser persistidos.`);
        log(`Teste do banco local aprovado em ${latencyMs} ms.`, "success", { code: "ARMAZENAMENTO_APROVADO" });
      }
      return { ok: true, ...app.storageHealth };
    } catch (error) {
      storageRemove(STORAGE_HEALTH_KEY).catch(() => {});
      app.storageHealth = { status: "error", checkedAt: new Date().toISOString(), latencyMs: Math.max(1, Math.round(performance.now() - startedAt)), message: error.message };
      if (!options?.silent) setBaseProgress("danger", `O armazenamento deste perfil falhou: ${error.message} Sem ele, a extensão não pode garantir retomada nem preservar o acervo.`);
      return { ok: false, error, ...app.storageHealth };
    } finally {
      renderSystemHealth();
      if (typeof renderKnowledgeBase === "function") renderKnowledgeBase();
    }
  }

  function includeStorageCheck(diagnosis, storageHealth) {
    if (!diagnosis || typeof diagnosis !== "object") return diagnosis;
    const check = {
      id: "local-storage",
      label: "Banco local",
      status: storageHealth.ok ? "ok" : "error",
      detail: storageHealth.ok ? storageHealth.message : `Falhou: ${storageHealth.message}`
    };
    diagnosis.preflight = diagnosis.preflight || { status: diagnosis.ready ? "ready" : "blocked", checks: [] };
    diagnosis.preflight.checks = [check, ...(diagnosis.preflight.checks || []).filter((entry) => entry.id !== check.id)];
    if (storageHealth.ok) return diagnosis;
    diagnosis.ready = false;
    diagnosis.issues = [{
      code: "ARMAZENAMENTO_INDISPONIVEL",
      severity: "blocking",
      repairable: false,
      message: "O banco local deste perfil não concluiu o teste de gravação, leitura e remoção.",
      action: "Verifique se a extensão tem permissão de armazenamento, recarregue-a e teste novamente neste perfil."
    }, ...(diagnosis.issues || []).filter((entry) => entry.code !== "ARMAZENAMENTO_INDISPONIVEL")];
    diagnosis.preflight = {
      ...diagnosis.preflight,
      status: "blocked",
      code: "ARMAZENAMENTO_INDISPONIVEL",
      title: "O banco local deste perfil não está disponível.",
      cause: storageHealth.message,
      impact: "Sem persistência, checkpoints, base permanente e retomada não são confiáveis.",
      action: "Recarregue a extensão neste perfil e use Testar tudo novamente."
    };
    return diagnosis;
  }

  function createUi() {
    const launcher = document.createElement("button");
    launcher.id = "aab-launcher";
    launcher.type = "button";
    launcher.title = `Abrir ${PRODUCT_NAME}`;
    launcher.setAttribute("aria-label", `Abrir ${PRODUCT_NAME}`);
    launcher.innerHTML = `<img src="${chrome.runtime.getURL("icons/icon-32.png")}" alt=""><b>${PRODUCT_LABEL}</b>`;

    const panel = document.createElement("aside");
    panel.id = "aab-panel";
    panel.setAttribute("aria-label", `Painel ${PRODUCT_NAME}`);
    panel.innerHTML = `
      <header class="aab-header">
        <div class="aab-brand-mark"><img src="${chrome.runtime.getURL("icons/icon-48.png")}" alt="Raposa SmartFox"></div>
        <div class="aab-brand-copy">
          <div class="aab-kicker">PROJETO ATHUS · CURADORIA PREMIUM</div>
          <h2>SmartFox <span class="aab-version">${PRODUCT_LABEL}</span></h2>
        </div>
        <button type="button" id="aab-close" aria-label="Fechar painel">×</button>
      </header>
      <div class="aab-safe-strip aab-neutral-strip" id="aab-mode-strip"><span></span><strong>Guia rápido.</strong> 1) Coloque o Word em Preparar  2) Use Banco de materiais  3) Revise  4) Envie.</div>
      <div class="aab-quick-guide"><div class="aab-quick-card"><strong>1. Word da prova</strong><span>Fica em <b>Preparar</b></span></div><div class="aab-quick-card"><strong>2. Banco da disciplina</strong><span>Fica em <b>Banco de materiais</b></span></div><div class="aab-quick-card"><strong>3. Revisão e envio</strong><span>Use <b>Revisar</b> e <b>Executar</b></span></div></div>
      <nav class="aab-nav" aria-label="Áreas do SmartFox">
        <button type="button" class="aab-nav-active" data-aab-nav="prepare"><span>1</span>Preparar</button>
        <button type="button" data-aab-nav="base"><span>2</span>Banco de materiais</button>
        <button type="button" data-aab-nav="review"><span>3</span>Revisar</button>
        <button type="button" data-aab-nav="run"><span>4</span>Executar</button>
        <button type="button" data-aab-nav="help"><span>?</span>Ajuda</button>
      </nav>
      <div class="aab-system-rail" aria-label="Estado geral da extensão" aria-live="polite">
        <div id="aab-health-site" data-state="waiting"><span>AvaliA</span><strong id="aab-health-site-value">A testar</strong></div>
        <div id="aab-health-storage" data-state="waiting"><span>Banco local</span><strong id="aab-health-storage-value">A testar</strong></div>
        <div id="aab-health-batch" data-state="waiting"><span>Lote</span><strong id="aab-health-batch-value">Nenhum</strong></div>
      </div>
      <div class="aab-work-actions"><span id="aab-work-status" role="status">Trabalho atual</span><button type="button" class="aab-button" id="aab-clear-questions" title="Limpar as questões e o Word do lote atual">Zerar questões</button><button type="button" class="aab-button aab-danger" id="aab-abandon-work">Abandonar trabalho</button></div>
      <div class="aab-body">
        <section class="aab-section aab-preflight-card" id="aab-preflight-section" data-aab-view="prepare" aria-live="polite">
          <div class="aab-preflight-head">
            <div><span class="aab-eyebrow">PRIMEIRO PASSO</span><strong>Testar perfil e tela</strong><small>Uma verificação reúne sessão, vínculos, disciplina e formulário.</small></div>
            <span id="aab-preflight-badge" class="aab-preflight-badge aab-preflight-waiting">Aguardando</span>
          </div>
          <div id="aab-preflight-explanation" class="aab-preflight-explanation">
            <strong>Abra Elaborador e teste o perfil.</strong>
            <span>A extensão verificará sessão, formulário, fonte, instituição, disciplina e editores.</span>
          </div>
          <div class="aab-preflight-actions">
            <button type="button" class="aab-button aab-primary" id="aab-test-profile">Testar tudo agora</button>
          </div>
          <small id="aab-preflight-time" class="aab-preflight-time">Ainda não testado nesta aba.</small>
          <details class="aab-technical-details">
            <summary>Detalhes e recuperação</summary>
            <div id="aab-preflight-checks" class="aab-preflight-checks"></div>
            <div id="aab-site-status" class="aab-status aab-neutral">Aguardando verificação.</div>
            <div id="aab-diagnosis" class="aab-diagnosis" hidden></div>
            <div class="aab-inline-actions">
              <button type="button" class="aab-button aab-secondary" id="aab-repair-site">Recuperar tela</button>
              <button type="button" class="aab-button aab-ghost" id="aab-download-diagnostic">Baixar diagnóstico</button>
            </div>
          </details>
        </section>

        <section class="aab-section aab-tag-section" id="aab-tag-section" data-aab-view="prepare">
          <div class="aab-section-title"><div><strong>Tag da avaliação</strong><small>O catálogo é lido novamente; somente Graduação fica disponível.</small></div><span id="aab-tag-badge" class="aab-count-badge">0</span></div>
          <div id="aab-tag-summary" class="aab-tag-summary"><strong>Mapeamento obrigatório</strong><span>Conclua manualmente os Passos 1–3 e use o botão abaixo. A extensão não modifica disciplina nem tag.</span></div>
          <div class="aab-inline-actions">
            <button type="button" class="aab-button aab-primary" id="aab-map-tags">Mapear tags atuais</button>
          </div>
          <div id="aab-tag-choice" class="aab-tag-choice" hidden>
            <label class="aab-field aab-full"><span>Qual tag de Graduação deve ser conferida?</span><select id="aab-target-tag"><option value="">Escolha depois do mapeamento</option></select></label>
            <input id="aab-sync-likes" type="checkbox" hidden disabled><p>Após o envio oficial, os likes das questões anteriores serão retirados e somente as questões da última remessa receberão like. Use <strong>Likes do banco</strong> para aprovar questões novamente, por TAG ou em todas as disciplinas escolhidas.</p>
          </div>
          <div class="aab-manual-boundary"><b>Controle dos gestores</b><span>Fonte, conteúdo, instituição, disciplina e tags são escolhidos por você nos Passos 1–3. A automação começa somente no Passo 4.</span></div>
        </section>

        <section class="aab-section aab-hero-section" data-aab-view="prepare">
          <div class="aab-step-title"><span>WORD</span><div><strong>Aqui você coloca o arquivo Word da prova</strong><small>Reconhece objetivas A–D e discursivas com padrão de resposta</small></div></div><div class="aab-stage-hint"><strong>Onde envio o Word?</strong><span>Use o botão logo abaixo. O arquivo é analisado primeiro e só depois segue para revisão.</span></div>
          <div class="aab-inline-actions"><button type="button" class="aab-button" id="aab-download-model">Baixar modelo Word</button><button type="button" class="aab-button" id="aab-download-prompt">Baixar prompt para elaborar prova</button></div>
          <div class="aab-upload-with-remove">
          <label class="aab-drop-zone" for="aab-file">
            <span class="aab-drop-icon">DOCX</span>
            <strong>Clique aqui para colocar o arquivo Word da prova</strong>
            <small>O arquivo é analisado localmente antes de qualquer envio.</small>
            <input id="aab-file" type="file" accept=".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document">
          </label>
          <button id="aab-remove-file" class="aab-remove-file" type="button" title="Remover arquivo" aria-label="Remover arquivo e limpar análise" hidden>×</button>
          </div>
          <div class="aab-mode-switch" role="radiogroup" aria-label="Destino das questões">
            <label><input type="radio" name="aab-output-mode" value="official" checked><span><strong>Oficial</strong><small>Conclui e envia</small></span></label>
            <label><input type="radio" name="aab-output-mode" value="draft"><span><strong>Rascunho</strong><small>Somente salva</small></span></label>
          </div>
          <details class="aab-compact-options"><summary>Opções do lote</summary><div class="aab-options-grid">
            <label class="aab-check-row"><input id="aab-auto-start" type="checkbox" checked><span><strong>Início automático</strong><small>Só inicia quando todas as revisões estiverem liberadas.</small></span></label>
            <label class="aab-check-row"><input id="aab-notify" type="checkbox" checked><span><strong>Aviso final</strong><small>Informa início, fim e duração.</small></span></label>
            <label class="aab-check-row aab-full-option"><input id="aab-continue-errors" type="checkbox" checked><span><strong>Continuar com as próximas válidas</strong><small>Isola uma falha definitiva sem repetir envios incertos.</small></span></label>
          </div></details>
          <div id="aab-file-summary" class="aab-muted">Nenhum arquivo analisado.</div>
          <div id="aab-stats" class="aab-stats" hidden></div>
          <section id="aab-file-diagnostics" class="aab-file-diagnostics" hidden aria-live="polite">
            <div class="aab-file-diagnostic-head">
              <div><strong id="aab-file-diagnostic-title">Diagnóstico do arquivo</strong><small id="aab-file-diagnostic-subtitle">Aguardando um DOCX.</small></div>
              <span id="aab-file-diagnostic-badge">—</span>
            </div>
            <div id="aab-file-diagnostic-metrics" class="aab-file-diagnostic-metrics"></div>
            <div class="aab-file-diagnostic-tools">
              <label><span>Mostrar</span><select id="aab-file-diagnostic-filter" aria-label="Filtrar diagnóstico do arquivo">
                <option value="action" selected>Erros e revisões</option>
                <option value="blocking">Somente erros</option>
                <option value="review">Somente revisões</option>
                <option value="warning">Somente avisos</option>
                <option value="all">Tudo</option>
              </select></label>
              <button type="button" class="aab-button aab-secondary" id="aab-download-file-diagnostic">Baixar laudo</button>
              <button type="button" class="aab-button aab-primary" id="aab-approve-file-rules" hidden>Aprovar exceções do lote</button>
              <button type="button" class="aab-button aab-ghost" id="aab-revoke-file-rules" hidden>Revogar aprovação</button>
            </div>
            <div id="aab-file-diagnostic-list" class="aab-file-diagnostic-list"></div>
            <small id="aab-file-diagnostic-scope" class="aab-file-diagnostic-scope"></small>
          </section>
        </section>

        <section class="aab-section aab-knowledge-section" id="aab-knowledge-section" data-aab-view="base">
          <div class="aab-section-title"><div><strong>Banco de questões e materiais</strong><small>Aqui fica o banco de dados da disciplina e também a geração de novas questões.</small></div><span id="aab-base-count" class="aab-count-badge">0</span></div>
          <div class="aab-collection-card">
            <label class="aab-field aab-full"><span>Coleção ativa</span><select id="aab-collection-select" aria-label="Coleção permanente ativa"></select></label>
            <div id="aab-collection-summary" class="aab-collection-summary">Acervo geral</div>
            <div class="aab-inline-actions aab-collection-actions">
              <button type="button" class="aab-button aab-primary" id="aab-new-collection">Nova coleção</button>
              <button type="button" class="aab-button aab-secondary" id="aab-edit-collection">Editar</button>
              <button type="button" class="aab-button aab-ghost" id="aab-delete-collection">Excluir</button>
              <button type="button" class="aab-button aab-secondary" id="aab-test-database">Testar armazenamento</button>
            </div>
            <div id="aab-database-summary" class="aab-database-summary"><strong>Banco de dados / acervo da disciplina</strong><span>É aqui que ficam salvos seus planos de ensino, materiais, modelos e regras para reutilização neste perfil do Chrome.</span></div>
            <div id="aab-collection-editor" class="aab-collection-editor" hidden>
              <strong id="aab-collection-editor-title">Nova coleção permanente</strong>
              <div class="aab-generator-grid">
                <label class="aab-field"><span>Avaliação</span><select id="aab-collection-evaluation"><option value="AD">AD</option><option value="AI">AI</option><option value="PS">PS</option><option value="P1" selected>P1</option><option value="P2">P2</option><option value="SCH">SCH</option><option value="P3">P3</option></select></label>
                <label class="aab-field aab-generator-wide"><span>Disciplina</span><input id="aab-collection-subject" type="text" placeholder="Ex.: Comportamento Organizacional"></label>
              </div>
              <small>Exemplo: P1 · Comportamento Organizacional. Os materiais ficam disponíveis nas próximas avaliações deste perfil.</small>
              <div class="aab-inline-actions"><button type="button" class="aab-button aab-primary" id="aab-save-collection">Salvar coleção</button><button type="button" class="aab-button aab-ghost" id="aab-cancel-collection">Cancelar</button></div>
            </div>
          </div>
          <label class="aab-drop-zone aab-material-drop" for="aab-material-files">
            <span class="aab-drop-icon">UAs</span><strong>Selecione várias UAs de uma vez ou um ZIP com os materiais</strong>
            <small>Use Ctrl ou Shift para selecionar vários arquivos · DOCX, PDF com texto, PPTX, TXT, MD, HTML, CSV ou ZIP · até 35 MB por arquivo</small>
            <input id="aab-material-files" type="file" multiple accept=".docx,.pdf,.pptx,.txt,.md,.html,.htm,.csv,.zip">
          </label>
          <div id="aab-material-batch-preview" class="aab-muted" aria-live="polite">Nenhum material selecionado.</div>
          <div class="aab-material-meta">
            <label class="aab-field aab-full"><span>Função dos arquivos</span><select id="aab-material-role"><option value="auto" selected>Detectar automaticamente</option><option value="teaching_plan">Plano de ensino — objetivos e UAs</option><option value="reference_material">Material de conteúdo — fatos e respostas</option><option value="assessment_model">Modelo de avaliação — estilo e estrutura</option><option value="rules">Regras institucionais — limites e padrão</option></select></label>
            <label class="aab-field"><span>Disciplina dos arquivos</span><input id="aab-material-subject" type="text" placeholder="Herdada da coleção ou detectada pelo nome"></label>
            <label class="aab-field"><span>Mesma UA para todos (opcional)</span><input id="aab-material-ua" type="text" inputmode="numeric" placeholder="Vazio = detectar a UA de cada arquivo"></label>
          </div>
          <div class="aab-inline-actions">
            <button type="button" class="aab-button aab-primary" id="aab-add-materials">Importar UAs em lote</button>
            <button type="button" class="aab-button aab-secondary" id="aab-scan-base">Conferir lote nesta coleção</button>
          </div>
          <div id="aab-base-summary" class="aab-base-summary">Nenhum material adicionado.</div>
          <div id="aab-curation-dashboard" class="aab-curation-dashboard" hidden></div>
          <div id="aab-base-progress" class="aab-status aab-neutral" hidden></div>
          <ul id="aab-base-list" class="aab-base-list"></ul>
          <div id="aab-material-editor" class="aab-material-editor" hidden>
            <strong id="aab-material-editor-title">Classificar material</strong>
            <div class="aab-material-meta">
              <label class="aab-field aab-full"><span>Função</span><select id="aab-edit-material-role"><option value="teaching_plan">Plano de ensino — objetivos e UAs</option><option value="reference_material">Material de conteúdo — fatos e respostas</option><option value="assessment_model">Modelo de avaliação — estilo e estrutura</option><option value="rules">Regras institucionais — limites e padrão</option></select></label>
              <label class="aab-field"><span>Disciplina</span><input id="aab-edit-material-subject" type="text"></label>
              <label class="aab-field"><span>UA específica</span><input id="aab-edit-material-ua" type="text" inputmode="numeric" placeholder="Vazio = títulos internos"></label>
              <label class="aab-field aab-full"><span>Coleção</span><select id="aab-edit-material-collection"></select></label>
            </div>
            <div class="aab-inline-actions"><button type="button" class="aab-button aab-primary" id="aab-save-material">Salvar classificação</button><button type="button" class="aab-button aab-ghost" id="aab-cancel-material">Cancelar</button></div>
          </div>
          <div class="aab-inline-actions">
            <button type="button" class="aab-button aab-secondary" id="aab-audit-base">Auditar coleção</button>
            <button type="button" class="aab-button aab-secondary" id="aab-export-base">Exportar backup</button>
            <button type="button" class="aab-button aab-secondary" id="aab-export-collection">Exportar coleção</button>
            <label class="aab-button aab-secondary aab-import-backup">Importar backup<input id="aab-import-base" type="file" accept="application/json,.json"></label>
            <button type="button" class="aab-button aab-ghost" id="aab-clear-base">Esvaziar coleção</button>
          </div>

          <div class="aab-stage-hint aab-stage-hint-fox"><strong>Criação local de questões</strong><span>Adicione as UAs à coleção e clique em Gerar avaliação. Você também pode abrir uma prova já pronta em Word.</span></div>
          <details class="aab-generator-card" open>
            <summary>Criar questões com os materiais</summary>
            <p>Confira a composição e a abrangência abaixo. Casos locais só são montados quando o conteúdo permite usar uma das estruturas disponíveis. Demais propostas ficam como rascunhos para edição. O documento final depende da conferência Athus e da revisão docente.</p>
            <label class="aab-field aab-full"><span>Orientações específicas desta avaliação</span><textarea id="aab-generation-rules" rows="4" placeholder="Ex.: 10 objetivas e 2 discursivas; UAs: 1-6. Objetivo: analisar decisões empreendedoras."></textarea></label>
            <label class="aab-rule-file" for="aab-rule-file"><span>Anexar regras em arquivo</span><input id="aab-rule-file" type="file" accept=".docx,.pdf,.txt,.md,.html,.htm"></label>
            <div class="aab-generator-grid">
              <label class="aab-field"><span>Avaliação</span><select id="aab-generation-evaluation"><option>AD</option><option>AI</option><option>PS</option><option>P1</option><option>P2</option><option>SCH</option><option>P3</option></select></label>
              <label class="aab-field" id="aab-p1-composition-field" hidden><span>Composição da P1</span><select id="aab-p1-composition"><option value="">Orientações / quantidade informada</option><option value="18">16 objetivas + 2 discursivas</option><option value="12">10 objetivas + 2 discursivas</option></select></label>
              <label class="aab-field"><span>Total de questões (vazio = orientações/padrão)</span><input id="aab-generation-count" type="number" min="1" max="30" placeholder="Automática"></label>
              <label class="aab-field aab-generator-wide"><span>Disciplina / Tema Gerador</span><input id="aab-generation-theme" type="text" placeholder="Ex.: Ciência Política"></label>
              <label class="aab-field"><span>UAs trabalhadas nesta etapa</span><input id="aab-generation-uas" type="text" placeholder="Ex.: 1-5 ou 3,4"></label>
              <label class="aab-field"><span>Dificuldade (inclui discursivas)</span><select id="aab-generation-difficulty"><option value="auto" selected>Distribuição das regras</option><option>Fácil</option><option>Médio</option><option>Difícil</option></select></label>
            </div>
            <div class="aab-inline-actions">
              <button type="button" class="aab-button aab-primary" id="aab-generate-questions">Gerar propostas</button>
              <button type="button" class="aab-button aab-secondary" id="aab-apply-athus-rules">Aplicar regras ao lote aberto</button>
              <button type="button" class="aab-button aab-secondary" id="aab-open-assessment-word">Abrir Word da avaliação</button>
              <button type="button" class="aab-button aab-secondary" id="aab-download-athus-draft" hidden>Rascunho para revisão (.docx)</button>
              <button type="button" class="aab-button aab-secondary" id="aab-download-generated-docx" hidden>Avaliação do professor (.docx)</button>
              <button type="button" class="aab-button aab-student-button" id="aab-download-study-guide" title="Cria um guia sem questões nem gabaritos" hidden>Guia do aluno (.docx)</button>
              <button type="button" class="aab-button aab-primary" id="aab-download-assessment-package" hidden>Baixar avaliação + guia</button>
            </div>
            <p class="aab-muted">Sem chat, chave de IA ou API paga. A criação usa regras locais e mantém os materiais neste navegador. As estruturas locais variam entre casos aplicados, verdadeiro ou falso e análise de afirmações. Toda contextualização deve ter pelo menos 15 linhas no Word padrão, sem contar alternativas. As estruturas locais são limitadas. Pendências de contexto, objetivo, linhas, feedback e composição aparecem para correção; um rascunho não é apresentado como avaliação pronta. O Word exportado usa formatação própria de texto; questões com imagens, fórmulas ou tabelas exigem o arquivo original.</p>
            <p id="aab-athus-rules-preview" class="aab-muted" role="status"></p>
            <p id="aab-athus-batch-status" class="aab-muted" role="status"></p>
            <div id="aab-generation-result" class="aab-muted"></div>
          </details>

          <details class="aab-external-exam-card">
            <summary>Responder prova externa com a base da disciplina</summary>
            <div class="aab-local-only-banner"><strong>Somente acervo local</strong><span>Nenhuma busca na internet é permitida. Planos de ensino, modelos e regras ajudam na organização, mas somente arquivos classificados como <b>Material de conteúdo</b> podem sustentar respostas.</span></div>
            <div id="aab-external-collection-summary" class="aab-external-collection-summary">Selecione uma coleção específica com disciplina definida.</div>
            <label class="aab-drop-zone aab-external-drop" for="aab-external-exam-file">
              <span class="aab-drop-icon">PROVA</span>
              <strong>Selecionar prova externa em DOCX</strong>
              <small>O arquivo é lido localmente; eventual gabarito existente não influencia a resposta sugerida.</small>
              <input id="aab-external-exam-file" type="file" accept=".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document">
            </label>
            <div class="aab-inline-actions">
              <button type="button" class="aab-button aab-primary" id="aab-analyze-external-exam">Analisar pela coleção ativa</button>
              <button type="button" class="aab-button aab-secondary" id="aab-download-external-report" hidden>Baixar gabarito fundamentado</button>
              <button type="button" class="aab-button aab-ghost" id="aab-clear-external-report" hidden>Limpar análise</button>
            </div>
            <div id="aab-external-exam-status" class="aab-muted">Nenhuma prova externa analisada.</div>
            <div id="aab-external-exam-results" class="aab-external-exam-results" hidden></div>
          </details>
        </section>

        <section class="aab-section" id="aab-question-section" data-aab-view="review" hidden>
          <div class="aab-section-title"><div><strong>Revisão das questões</strong><small>Questão, evidência, objetivo e decisão no mesmo lugar</small></div><span class="aab-review-head-actions"><button type="button" class="aab-link-button" id="aab-download-generated-docx-review" hidden>Baixar prova</button><button type="button" class="aab-link-button aab-student-link" id="aab-download-study-guide-review" title="Roteiro para compartilhar sem revelar a prova" hidden>Roteiro do aluno</button><button type="button" class="aab-link-button" id="aab-review-all-high">Aplicar correções seguras</button></span></div>
          <div class="aab-bulk-review">
            <button type="button" class="aab-button aab-warning-button" id="aab-approve-all-reviews" aria-describedby="aab-bulk-review-summary">Aprovar todas e alocar assim mesmo</button>
            <small id="aab-bulk-review-summary" role="status">Aplica sua decisão ao lote inteiro, incluindo questões fora do filtro atual.</small>
          </div>
          <div class="aab-review-toolbar">
            <button type="button" class="aab-icon-button" id="aab-prev-question" aria-label="Questão anterior">‹</button>
            <select id="aab-question-select" aria-label="Questão inspecionada"></select>
            <button type="button" class="aab-icon-button" id="aab-next-question" aria-label="Próxima questão">›</button>
          </div>
          <div class="aab-filter-row">
            <label for="aab-filter">Mostrar</label>
            <select id="aab-filter">
              <option value="all">Todas</option>
              <option value="action">Precisam de ação</option>
              <option value="blocked">Com campo obrigatório ausente</option>
              <option value="review">Aguardando autorização</option>
              <option value="authorized">Autorizadas manualmente</option>
              <option value="ready">Aprovadas automaticamente</option>
            </select>
            <button type="button" class="aab-link-button" id="aab-next-issue">Próxima pendência</button>
          </div>
          <div id="aab-question-status" class="aab-question-status"></div>
          <div id="aab-question-preview" class="aab-preview"></div>

          <div id="aab-knowledge-card" class="aab-knowledge-card">
            <div class="aab-knowledge-head">
              <div><strong>Conferência com os materiais</strong><small id="aab-knowledge-summary">Adicione uma base para verificar o conteúdo.</small></div>
              <span id="aab-knowledge-confidence">—</span>
            </div>
            <div id="aab-knowledge-answer" class="aab-knowledge-answer"></div>
            <div id="aab-knowledge-evidence" class="aab-knowledge-evidence"></div>
            <div class="aab-knowledge-actions">
              <button type="button" class="aab-button aab-primary" id="aab-apply-knowledge">Aplicar correção fundamentada</button>
              <button type="button" class="aab-button aab-secondary" id="aab-keep-knowledge">Manter após conferência</button>
              <button type="button" class="aab-button aab-ghost" id="aab-revoke-knowledge">Reabrir decisão</button>
            </div>
          </div>

          <details class="aab-review-group" id="aab-allocation-group">
            <summary>Compatibilidade com a disciplina</summary>
          <div id="aab-allocation-card" class="aab-allocation-card">
            <div class="aab-allocation-head"><div><strong>Conferência da matéria</strong><small id="aab-allocation-summary">Aguardando a disciplina do AvaliA.</small></div><span id="aab-allocation-score">—</span></div>
            <div id="aab-allocation-details" class="aab-allocation-details aab-muted"></div>
            <div class="aab-inline-actions">
              <button type="button" class="aab-button aab-secondary" id="aab-check-allocation">Conferir matéria agora</button>
              <button type="button" class="aab-button aab-warning-button" id="aab-approve-allocation">Aprovar alocação mesmo assim</button>
              <button type="button" class="aab-button aab-ghost" id="aab-revoke-allocation">Revogar aprovação</button>
            </div>
          </div>
          </details>

          <details class="aab-source-card">
            <summary><span>Trecho de origem</span><small id="aab-source-range"></small></summary>
            <pre id="aab-source-text"></pre>
          </details>

          <details class="aab-edit-card" id="aab-edit-card">
            <summary>Editar campos e corrigir a interpretação</summary>
            <div class="aab-edit-grid">
              <label class="aab-field aab-full"><span>Identificação</span><input id="aab-edit-name" type="text"></label>
              <label class="aab-field aab-full"><span>Tema Gerador</span><input id="aab-edit-theme" type="text"></label>
              <label class="aab-field aab-full"><span>Objetivo associado</span><textarea id="aab-edit-objective" rows="3"></textarea></label>
              <label class="aab-field"><span>UA</span><input id="aab-edit-ua" type="number" min="1" max="30"></label>
              <label class="aab-field"><span>Número do objetivo</span><input id="aab-edit-objective-number" type="number" min="1" max="99"></label>
              <label class="aab-field"><span>Dificuldade</span><select id="aab-edit-difficulty"><option>Fácil</option><option>Médio</option><option>Difícil</option></select></label>
              <label class="aab-field"><span>Habilidade avaliada</span><input id="aab-edit-skill" type="text"></label>
              <label class="aab-check aab-full"><input id="aab-edit-objective-confirm" type="checkbox"><span>Conferi que o objetivo corresponde à habilidade exigida nesta questão.</span></label>
              <label class="aab-field aab-full"><span>Contextualização e comando (pergunta na última linha)</span><textarea id="aab-edit-body" rows="7"></textarea></label>
              <label class="aab-field aab-full" id="aab-expected-response-field" hidden><span>Padrão de resposta discursiva</span><textarea id="aab-edit-expected-response" rows="6"></textarea></label>
              <label class="aab-field" data-aab-objective-field><span>Alternativa A</span><textarea id="aab-edit-a" rows="3"></textarea></label>
              <label class="aab-field" data-aab-objective-field><span>Alternativa B</span><textarea id="aab-edit-b" rows="3"></textarea></label>
              <label class="aab-field" data-aab-objective-field><span>Alternativa C</span><textarea id="aab-edit-c" rows="3"></textarea></label>
              <label class="aab-field" data-aab-objective-field><span>Alternativa D</span><textarea id="aab-edit-d" rows="3"></textarea></label>
              <label class="aab-field" data-aab-objective-field><span>Gabarito</span><select id="aab-edit-answer"><option>A</option><option>B</option><option>C</option><option>D</option></select></label>
              <label class="aab-field"><span>Tipo / modelo</span><select id="aab-edit-type"></select></label>
              <label class="aab-field"><span>Nível cognitivo</span><select id="aab-edit-cognitive"></select></label>
              <label class="aab-field aab-full"><span>Feedback pedagógico</span><textarea id="aab-edit-feedback" rows="6"></textarea></label>
            </div>
            <div class="aab-media-tools">
              <div><strong>Adicionar imagem</strong><small>PNG, JPEG, GIF, WebP, SVG ou BMP; até 12 MB. A assinatura será conferida no AvaliA.</small></div>
              <input id="aab-image-file" type="file" accept="image/png,image/jpeg,image/gif,image/webp,image/svg+xml,image/bmp">
              <select id="aab-image-target" aria-label="Campo que receberá a imagem">
                <option value="body">Enunciado</option><option value="expectedResponse">Padrão de resposta</option><option value="A">Alternativa A</option><option value="B">Alternativa B</option><option value="C">Alternativa C</option><option value="D">Alternativa D</option><option value="feedback">Feedback</option>
              </select>
              <button type="button" class="aab-button aab-secondary" id="aab-add-image">Inserir imagem na questão</button>
              <button type="button" class="aab-button aab-ghost" id="aab-remove-image">Remover última imagem adicionada</button>
              <span id="aab-rich-summary" class="aab-muted"></span>
            </div>
            <div class="aab-edit-actions">
              <button type="button" class="aab-button aab-primary" id="aab-apply-edit">Aplicar e conferir novamente</button>
              <button type="button" class="aab-button aab-secondary" id="aab-redetect">Autodetectar tipo novamente</button>
              <button type="button" class="aab-button aab-ghost" id="aab-restore-question">Restaurar trecho do Word</button>
            </div>
          </details>

          <div id="aab-authorization" class="aab-authorization">
            <label class="aab-check-row"><input id="aab-manual-confirm" type="checkbox"><span><strong id="aab-confirmation-copy">Li todos os campos da questão e o feedback</strong><small>Confirmo que a questão faz sentido mesmo com os alertas indicados.</small></span></label>
            <div class="aab-inline-actions">
              <button type="button" class="aab-button aab-warning-button" id="aab-authorize">Aprovar e ir à próxima</button>
              <button type="button" class="aab-button aab-ghost" id="aab-revoke">Revogar autorização</button>
            </div>
          </div>
          <label class="aab-check-row aab-keyword-row"><input id="aab-keywords" type="checkbox" checked><span>Preencher palavras-chave derivadas do tema e da UA</span></label>
        </section>

        <section class="aab-section" id="aab-readiness-section" data-aab-view="run" hidden>
          <div class="aab-section-title"><div><strong>Prontidão do lote</strong><small>Veja somente o que falta antes de iniciar</small></div></div>
          <ul id="aab-readiness-list" class="aab-readiness-list"></ul>
        </section>

        <section class="aab-section" id="aab-run-section" data-aab-view="run" hidden>
          <div class="aab-step-title"><span>▶</span><div><strong>Executar e acompanhar</strong><small>Marcos persistentes, antirrepetição e retomada segura</small></div></div>
          <div class="aab-run-card">
            <div><span>Estado</span><strong id="aab-run-state">Pronto</strong></div>
            <div><span>Início</span><strong id="aab-start-time">—</strong></div>
            <div><span>Fim</span><strong id="aab-end-time">—</strong></div>
            <div><span>Tempo</span><strong id="aab-elapsed">00:00</strong></div>
          </div>
          <div class="aab-progress" aria-label="Progresso"><div id="aab-progress-bar"></div></div>
          <div id="aab-progress-text" class="aab-muted">0 de 0 concluídas.</div>
          <div id="aab-last-problem" class="aab-last-problem" hidden></div>
          <div id="aab-cleanup-panel" class="aab-section" hidden><strong>Retirada obrigatória dos likes</strong><p id="aab-cleanup-state" role="status" aria-live="polite"></p><button type="button" class="aab-button aab-primary" id="aab-finish-cleanup">Concluir retirada dos likes</button></div>
          <div id="aab-approval-sync" class="aab-approval-sync" hidden>
            <div class="aab-approval-head"><div><strong>Likes da última remessa</strong><small id="aab-approval-status">Aguardando a conclusão do lote oficial.</small></div><span id="aab-approval-badge">Opcional</span></div>
            <div id="aab-approval-summary" class="aab-approval-summary"></div>
            <div class="aab-inline-actions">
              <button type="button" class="aab-button aab-secondary" id="aab-inspect-approvals">Conferir lista e criar prévia</button>
              <button type="button" class="aab-button aab-primary" id="aab-apply-approvals" hidden>Confirmar e ajustar likes</button>
            </div>
          </div>
          <div class="aab-actions">
            <button type="button" class="aab-button aab-primary aab-start-button" id="aab-start"><span>▶</span> Confirmar e iniciar tudo</button>
            <button type="button" class="aab-button aab-primary" id="aab-resume" hidden>Retomar do último marco</button>
            <button type="button" class="aab-button aab-secondary" id="aab-fill-current">Conferir texto, fórmulas e imagens sem salvar</button>
            <button type="button" class="aab-button aab-secondary" id="aab-smart-recover">Resolver problema e tentar continuar</button>
            <button type="button" class="aab-button aab-warning-button" id="aab-skip-current" hidden>Ignorar esta questão e continuar</button>
            <button type="button" class="aab-button aab-danger" id="aab-stop" disabled>Pausar após a ação atual</button>
            <button type="button" class="aab-button aab-warning-button" id="aab-confirm-sent" hidden>Conferi no AvaliA: foi enviada</button>
            <button type="button" class="aab-button aab-ghost" id="aab-report">Baixar relatório completo</button>
          </div>
        </section>

        <section class="aab-section" id="aab-log-section" data-aab-view="run">
          <div class="aab-section-title"><div><strong>Histórico e diagnóstico</strong><small>Erros, alertas e conclusões preservados localmente</small></div><button type="button" class="aab-link-button" id="aab-clear-session">Nova avaliação</button></div>
          <div class="aab-history-summary" id="aab-history-summary"></div>
          <div class="aab-history-tools">
            <input id="aab-history-search" type="search" placeholder="Buscar código, questão ou mensagem" aria-label="Buscar no histórico">
            <select id="aab-history-filter" aria-label="Filtrar histórico">
              <option value="all">Tudo</option>
              <option value="error">Erros</option>
              <option value="warning">Alertas</option>
              <option value="success">Conclusões</option>
              <option value="info">Informações</option>
            </select>
          </div>
          <ol id="aab-log" class="aab-log"></ol>
          <div class="aab-history-actions">
            <button type="button" class="aab-button aab-ghost" id="aab-export-history">Exportar banco</button>
            <button type="button" class="aab-button aab-ghost" id="aab-clear-history">Limpar banco</button>
          </div>
        </section>

        <section class="aab-section aab-help-section" id="aab-help-section" data-aab-view="help">
          <div class="aab-section-title"><div><strong>Ajuda SmartFox</strong><small>Pesquise uma dúvida ou use uma ação rápida</small></div><span class="aab-count-badge">11.2</span></div>
          <div id="aab-help-identity" class="aab-help-identity"><span>Identidade</span><strong>Edição autônoma, sem ativação.</strong></div>
          <div class="aab-help-actions" id="aab-help-actions">
            <button type="button" class="aab-button aab-primary" data-aab-help-action="test">Testar perfil e tela</button>
            <button type="button" class="aab-button aab-secondary" data-aab-help-action="account">Sobre esta versão</button>
            <button type="button" class="aab-button aab-secondary" data-aab-help-action="announcements">Sobre e atualizações</button>
            <button type="button" class="aab-button aab-secondary" data-aab-help-action="prepare">Importar DOCX</button>
            <button type="button" class="aab-button aab-secondary" data-aab-help-action="base">Abrir acervo</button>
            <button type="button" class="aab-button aab-secondary" data-aab-help-action="external">Prova externa</button>
            <button type="button" class="aab-button aab-secondary" data-aab-help-action="review">Revisar questões</button>
            <button type="button" class="aab-button aab-secondary" data-aab-help-action="run">Executar lote</button>
          </div>
          <label class="aab-field aab-full aab-help-search"><span>Qual é a sua dúvida?</span><input id="aab-help-search" type="search" placeholder="Ex.: questão 2, duplicidade, fórmula ou backup"></label>
          <div id="aab-help-results" class="aab-help-results" aria-live="polite"></div>
          <div id="aab-help-list" class="aab-help-list">
            <details data-help="inicio começar testar perfil passos 1 2 3 4"><summary>Como começar uma nova avaliação?</summary><p>No AvaliA, conclua manualmente os Passos 1–3. Em Preparar, teste o perfil, mapeie a tag de Graduação, importe o DOCX e revise o diagnóstico. O SmartFox intervém somente do Passo 4 em diante.</p></details>
            <details data-help="docx word arquivo erro leitura questão tipo alternativas"><summary>O DOCX não foi interpretado corretamente</summary><p>Abra o diagnóstico do arquivo: ele indica questão, trecho, campo faltante, causa provável e ação. Objetivas exigem exatamente A–D; discursivas exigem padrão de resposta. Exceções só avançam após sua aprovação explícita.</p></details>
            <details data-help="duplicidade repetida nome texto envio"><summary>Como funcionam as duplicidades?</summary><p>Nome repetido, texto interno repetido e histórico de envio são sinalizados. O aviso não bloqueia as demais questões válidas; um envio de resultado incerto nunca é repetido automaticamente.</p></details>
            <details data-help="acervo banco permanente material plano ensino gerar questão resposta correta"><summary>Como reutilizar materiais e criar questões?</summary><p>Em Acervo, crie uma coleção por avaliação e disciplina, como “P1 · Comportamento Organizacional”. Adicione plano de ensino, conteúdo, modelos e regras. A coleção permanece neste perfil e pode ser exportada em backup.</p></details>
            <details data-help="prova externa responder gabarito base disciplina sem internet web evidência"><summary>Como responder uma prova externa somente pelo acervo?</summary><p>Abra uma coleção específica da disciplina, classifique as fontes válidas como “Material de conteúdo” e selecione a prova em DOCX. O SmartFox não consulta a internet: ele mostra resposta, confiança e trechos da coleção, ou informa que a base é insuficiente. Itens amarelos exigem conferência docente.</p></details>
            <details data-help="qualidade referência url autor bibliografia resposta alternativa"><summary>Como a curadoria evita alternativas ruins?</summary><p>URLs, referências, autoria e fragmentos bibliográficos entram em quarentena e não podem virar alternativas. A revisão confere objetivo, matéria, evidência, gabarito, coerência e completude antes da liberação.</p></details>
            <details data-help="imagem fórmula caractere especial igual word"><summary>Imagens, fórmulas e caracteres especiais</summary><p>O importador preserva conteúdo rico e compara a representação com o Word. Use a conferência sem salvar; divergências ficam bloqueadas até correção ou autorização docente.</p></details>
            <details data-help="rascunho oficial salvar enviar confirmação"><summary>Qual a diferença entre rascunho e oficial?</summary><p>Rascunho apenas salva. Oficial percorre confirmações e envia depois das verificações. Escolha o destino antes de iniciar; o relatório registra início, fim, duração, IDs e falhas.</p></details>
            <details data-help="travou loop questão 2 recuperar checkpoint salvamento indeterminado"><summary>O AvaliA travou ou parou em uma questão</summary><p>Use “Resolver problema e tentar continuar”. A extensão relê o estado, restaura o último marco seguro e segue para a próxima válida quando permitido. Salvamento indeterminado exige conferência humana para impedir duplicação.</p></details>
            <details data-help="tag graduação like banco retirar aprovar"><summary>Gerenciar likes do banco</summary><p>O botão Likes do banco detecta suas disciplinas e permite desmarcar ou aprovar questões, em todas as selecionadas ou por TAG. Após novos envios oficiais, a atualização dos likes é automática: somente a última remessa fica com like. Falhas ficam pendentes para retomada.</p></details>
            <details data-help="baixar prova documento docx roteiro aluno estudo"><summary>Como baixar a prova e o roteiro de estudos?</summary><p>Após gerar ou revisar, use “Baixar avaliação em DOCX” e “Baixar roteiro do aluno”. O roteiro usa os conteúdos e objetivos avaliados sem revelar perguntas nem gabaritos.</p></details>
            <details data-help="corrigir respostas peso máximo justificativa padrão"><summary>Como funciona a correção discursiva?</summary><p>Na tela de correção, o peso máximo é lido do modelo do AvaliA. Resposta relacionada, mesmo curta ou incompleta, recebe sugestão de nota máxima; resposta vazia ou sem relação recebe zero. A justificativa replica o padrão e todo lançamento exige confirmação docente.</p></details>
            <details data-help="nome avalia divergente licença identidade usuário acesso"><summary>Preciso cadastrar meu nome no SmartFox?</summary><p>Não. Esta edição dispensa cadastro, chave de ativação e liberação de computador. Entre normalmente no AvaliA com sua conta institucional.</p></details>
            <details data-help="atualização aviso versão administrador notificação leitura"><summary>Onde vejo avisos de atualização?</summary><p>Use “Sobre e atualizações” para ver a versão instalada. Para atualizar, substitua os arquivos na mesma pasta e clique em Recarregar na página de extensões. Não há consulta a um servidor de comunicados.</p></details>
            <details data-help="integridade código propriedade intelectual cópia pacote alterado"><summary>O que significa INTEGRIDADE_DO_PACOTE_FALHOU?</summary><p>Um arquivo crítico está ausente ou diferente do catálogo SHA-256. Extraia novamente o pacote SmartFox Autônomo e recarregue a extensão. A conferência dos arquivos é feita localmente, sem servidor de autorização.</p></details>

            <details data-help="disciplinas disponíveis acesso administrador"><summary>Preciso liberar cada disciplina?</summary><p>Não. Use diretamente as disciplinas disponíveis no seu perfil do AvaliA. Selecione a disciplina correta no Passo 3 antes de enviar as questões.</p></details>
            <details data-help="onde word arquivo docx colocar enviar prova"><summary>Onde eu coloco o arquivo Word da prova?</summary><p>Abra <b>Preparar</b> e use a área grande “Clique aqui para colocar o arquivo Word da prova”. Depois confira o diagnóstico do arquivo antes de seguir.</p></details>
            <details data-help="onde banco dados acervo materiais disciplina"><summary>Onde fica o banco de dados da disciplina?</summary><p>Abra <b>Banco de materiais</b>. Nessa área ficam a coleção ativa, o banco de materiais, o upload dos arquivos da disciplina e os controles de backup.</p></details>
            <details data-help="onde gerar questoes novas banco disciplina"><summary>Onde gero novas questões?</summary><p>Em <b>Banco de materiais</b>, adicione as UAs como Material de conteúdo e use “Criar questões com os materiais”. Informe avaliação, quantidade, disciplina e UAs; clique em Gerar avaliação e revise as propostas. A elaboração funciona por regras locais, sem chat nem chave de IA.</p></details>
            <details data-help="desmarcar like tag"><summary>Como desmarcar os likes das questões?</summary><p>Abra <b>Likes do banco</b>, detecte as disciplinas, selecione os bancos e confira a prévia. Escolha desmarcar todos ou preservar os likes de uma TAG. O mesmo painel permite dar like em todas as questões pendentes ou apenas nas da TAG escolhida.</p></details>
            <details data-help="corrigir discursivas correcao respostas discursivas"><summary>Como o SmartFox ajuda na correção discursiva?</summary><p>Na tela de correção, o SmartFox sugere nota e justificativa com base no padrão de resposta e no peso máximo do item. A decisão final continua sendo do professor.</p></details>
          </div>
          <div id="aab-help-empty" class="aab-help-empty" hidden>Nenhuma resposta encontrada. Consulte o código do erro no Histórico ou baixe o diagnóstico.</div>
        </section>
      </div>`;
    document.documentElement.appendChild(launcher);
    document.documentElement.appendChild(panel);
    return { launcher, panel };
  }

  const roots = createUi();
  const byId = (id) => document.getElementById(id);
  const ui = {
    abandonWork: byId("aab-abandon-work"), clearQuestions: byId("aab-clear-questions"), workStatus: byId("aab-work-status"),
    launcher: roots.launcher, panel: roots.panel, close: byId("aab-close"), modeStrip: byId("aab-mode-strip"),
    navButtons: Array.from(document.querySelectorAll("[data-aab-nav]")), viewSections: Array.from(document.querySelectorAll("[data-aab-view]")),
    healthSite: byId("aab-health-site"), healthSiteValue: byId("aab-health-site-value"), healthStorage: byId("aab-health-storage"), healthStorageValue: byId("aab-health-storage-value"), healthBatch: byId("aab-health-batch"), healthBatchValue: byId("aab-health-batch-value"),
    downloadModel:byId("aab-download-model"),downloadPrompt:byId("aab-download-prompt"),file: byId("aab-file"), removeFile: byId("aab-remove-file"), fileSummary: byId("aab-file-summary"), stats: byId("aab-stats"),
    fileDiagnostics: byId("aab-file-diagnostics"), fileDiagnosticTitle: byId("aab-file-diagnostic-title"), fileDiagnosticSubtitle: byId("aab-file-diagnostic-subtitle"), fileDiagnosticBadge: byId("aab-file-diagnostic-badge"), fileDiagnosticMetrics: byId("aab-file-diagnostic-metrics"), fileDiagnosticFilter: byId("aab-file-diagnostic-filter"), downloadFileDiagnostic: byId("aab-download-file-diagnostic"), approveFileRules: byId("aab-approve-file-rules"), revokeFileRules: byId("aab-revoke-file-rules"), fileDiagnosticList: byId("aab-file-diagnostic-list"), fileDiagnosticScope: byId("aab-file-diagnostic-scope"),
    modeInputs: Array.from(document.querySelectorAll('input[name="aab-output-mode"]')), autoStart: byId("aab-auto-start"), notify: byId("aab-notify"), continueErrors: byId("aab-continue-errors"),
    preflightSection: byId("aab-preflight-section"), preflightBadge: byId("aab-preflight-badge"), preflightChecks: byId("aab-preflight-checks"), preflightExplanation: byId("aab-preflight-explanation"), preflightTime: byId("aab-preflight-time"), testProfile: byId("aab-test-profile"), downloadDiagnostic: byId("aab-download-diagnostic"),
    siteStatus: byId("aab-site-status"), diagnosis: byId("aab-diagnosis"), repairSite: byId("aab-repair-site"),
    tagSection: byId("aab-tag-section"), tagBadge: byId("aab-tag-badge"), tagSummary: byId("aab-tag-summary"), mapTags: byId("aab-map-tags"), tagChoice: byId("aab-tag-choice"), targetTag: byId("aab-target-tag"), syncLikes: byId("aab-sync-likes"),
    knowledgeSection: byId("aab-knowledge-section"), materialFiles: byId("aab-material-files"), materialRole: byId("aab-material-role"), materialSubject: byId("aab-material-subject"), materialUa: byId("aab-material-ua"), addMaterials: byId("aab-add-materials"), scanBase: byId("aab-scan-base"),
    collectionSelect: byId("aab-collection-select"), collectionSummary: byId("aab-collection-summary"), newCollection: byId("aab-new-collection"), editCollection: byId("aab-edit-collection"), deleteCollection: byId("aab-delete-collection"), testDatabase: byId("aab-test-database"), databaseSummary: byId("aab-database-summary"), collectionEditor: byId("aab-collection-editor"), collectionEditorTitle: byId("aab-collection-editor-title"), collectionEvaluation: byId("aab-collection-evaluation"), collectionSubject: byId("aab-collection-subject"), saveCollection: byId("aab-save-collection"), cancelCollection: byId("aab-cancel-collection"),
    baseCount: byId("aab-base-count"), baseSummary: byId("aab-base-summary"), curationDashboard: byId("aab-curation-dashboard"), baseProgress: byId("aab-base-progress"), baseList: byId("aab-base-list"), materialEditor: byId("aab-material-editor"), materialEditorTitle: byId("aab-material-editor-title"), editMaterialRole: byId("aab-edit-material-role"), editMaterialSubject: byId("aab-edit-material-subject"), editMaterialUa: byId("aab-edit-material-ua"), editMaterialCollection: byId("aab-edit-material-collection"), saveMaterial: byId("aab-save-material"), cancelMaterial: byId("aab-cancel-material"), auditBase: byId("aab-audit-base"), exportBase: byId("aab-export-base"), exportCollection: byId("aab-export-collection"), importBase: byId("aab-import-base"), clearBase: byId("aab-clear-base"),
    generationRules: byId("aab-generation-rules"), ruleFile: byId("aab-rule-file"), generationEvaluation: byId("aab-generation-evaluation"), generationCount: byId("aab-generation-count"), p1Composition: byId("aab-p1-composition"), p1CompositionField: byId("aab-p1-composition-field"), generationTheme: byId("aab-generation-theme"), generationUas: byId("aab-generation-uas"), generationDifficulty: byId("aab-generation-difficulty"), generateQuestions: byId("aab-generate-questions"), openAssessmentWord: byId("aab-open-assessment-word"), downloadGeneratedDocx: byId("aab-download-generated-docx"), downloadGeneratedDocxReview: byId("aab-download-generated-docx-review"), downloadStudyGuide: byId("aab-download-study-guide"), downloadStudyGuideReview: byId("aab-download-study-guide-review"), generationResult: byId("aab-generation-result"),
    downloadAssessmentPackage: byId("aab-download-assessment-package"), materialBatchPreview: byId("aab-material-batch-preview"),
    externalCollectionSummary: byId("aab-external-collection-summary"), externalExamFile: byId("aab-external-exam-file"), analyzeExternalExam: byId("aab-analyze-external-exam"), downloadExternalReport: byId("aab-download-external-report"), clearExternalReport: byId("aab-clear-external-report"), externalExamStatus: byId("aab-external-exam-status"), externalExamResults: byId("aab-external-exam-results"),
    questionSection: byId("aab-question-section"), questionSelect: byId("aab-question-select"), prevQuestion: byId("aab-prev-question"), nextQuestion: byId("aab-next-question"),
    filter: byId("aab-filter"), nextIssue: byId("aab-next-issue"), questionStatus: byId("aab-question-status"), preview: byId("aab-question-preview"),
    approveAllReviews: byId("aab-approve-all-reviews"), bulkReviewSummary: byId("aab-bulk-review-summary"),
    allocationCard: byId("aab-allocation-card"), allocationSummary: byId("aab-allocation-summary"), allocationScore: byId("aab-allocation-score"), allocationDetails: byId("aab-allocation-details"),
    checkAllocation: byId("aab-check-allocation"), approveAllocation: byId("aab-approve-allocation"), revokeAllocation: byId("aab-revoke-allocation"),
    allocationGroup: byId("aab-allocation-group"), knowledgeCard: byId("aab-knowledge-card"), knowledgeSummary: byId("aab-knowledge-summary"), knowledgeConfidence: byId("aab-knowledge-confidence"), knowledgeAnswer: byId("aab-knowledge-answer"), knowledgeEvidence: byId("aab-knowledge-evidence"),
    applyKnowledge: byId("aab-apply-knowledge"), keepKnowledge: byId("aab-keep-knowledge"), revokeKnowledge: byId("aab-revoke-knowledge"), reviewAllHigh: byId("aab-review-all-high"),
    sourceRange: byId("aab-source-range"), sourceText: byId("aab-source-text"), editCard: byId("aab-edit-card"),
    editTheme: byId("aab-edit-theme"), editObjective: byId("aab-edit-objective"), editUa: byId("aab-edit-ua"), editObjectiveNumber: byId("aab-edit-objective-number"), editDifficulty: byId("aab-edit-difficulty"), editSkill: byId("aab-edit-skill"), editObjectiveConfirm: byId("aab-edit-objective-confirm"),
    athusRulesPreview: byId("aab-athus-rules-preview"), athusBatchStatus: byId("aab-athus-batch-status"), downloadAthusDraft: byId("aab-download-athus-draft"), applyAthusRules: byId("aab-apply-athus-rules"),
    editName: byId("aab-edit-name"), editBody: byId("aab-edit-body"), editExpectedResponse: byId("aab-edit-expected-response"), expectedResponseField: byId("aab-expected-response-field"), objectiveFields: Array.from(document.querySelectorAll("[data-aab-objective-field]")), editAlternatives: ["a", "b", "c", "d"].map((letter) => byId(`aab-edit-${letter}`)),
    editAnswer: byId("aab-edit-answer"), editType: byId("aab-edit-type"), editCognitive: byId("aab-edit-cognitive"), editFeedback: byId("aab-edit-feedback"),
    imageFile: byId("aab-image-file"), imageTarget: byId("aab-image-target"), addImage: byId("aab-add-image"), removeImage: byId("aab-remove-image"), richSummary: byId("aab-rich-summary"),
    applyEdit: byId("aab-apply-edit"), redetect: byId("aab-redetect"), restoreQuestion: byId("aab-restore-question"),
    authorization: byId("aab-authorization"), manualConfirm: byId("aab-manual-confirm"), confirmationCopy: byId("aab-confirmation-copy"), authorize: byId("aab-authorize"), revoke: byId("aab-revoke"), keywords: byId("aab-keywords"),
    readinessSection: byId("aab-readiness-section"), readinessList: byId("aab-readiness-list"), runSection: byId("aab-run-section"),
    cleanupPanel: byId("aab-cleanup-panel"), cleanupState: byId("aab-cleanup-state"), finishCleanup: byId("aab-finish-cleanup"),
    runState: byId("aab-run-state"), startTime: byId("aab-start-time"), endTime: byId("aab-end-time"), elapsed: byId("aab-elapsed"),
    progressBar: byId("aab-progress-bar"), progressText: byId("aab-progress-text"), lastProblem: byId("aab-last-problem"),
    approvalSync: byId("aab-approval-sync"), approvalStatus: byId("aab-approval-status"), approvalBadge: byId("aab-approval-badge"), approvalSummary: byId("aab-approval-summary"), inspectApprovals: byId("aab-inspect-approvals"), applyApprovals: byId("aab-apply-approvals"),
    start: byId("aab-start"), resume: byId("aab-resume"), fillCurrent: byId("aab-fill-current"), smartRecover: byId("aab-smart-recover"), skipCurrent: byId("aab-skip-current"), stop: byId("aab-stop"),
    confirmSent: byId("aab-confirm-sent"), report: byId("aab-report"), logSection: byId("aab-log-section"), log: byId("aab-log"), clearSession: byId("aab-clear-session"),
    historySummary: byId("aab-history-summary"), historySearch: byId("aab-history-search"), historyFilter: byId("aab-history-filter"), exportHistory: byId("aab-export-history"), clearHistory: byId("aab-clear-history"),
    helpSection: byId("aab-help-section"), helpIdentity: byId("aab-help-identity"), helpActions: byId("aab-help-actions"), helpSearch: byId("aab-help-search"), helpResults: byId("aab-help-results"), helpList: byId("aab-help-list"), helpEmpty: byId("aab-help-empty")
  };

  ui.editType.innerHTML = Parser.typeCatalog.map((type) => `<option value="${escapeHtml(type.id)}">${escapeHtml(type.label)}</option>`).join("");
  ui.editCognitive.innerHTML = Parser.cognitiveCatalog.map((level) => `<option value="${escapeHtml(level.id)}">${escapeHtml(level.label)}</option>`).join("");

  function selectedMode() {
    return ui.modeInputs.find((input) => input.checked)?.value === "draft" ? "draft" : "official";
  }

  function safeUiAction(code, handler) {
    return async function (...args) {
      if (app.abandoning || app.batchReviewBusy) return;
      const control = args[0]?.currentTarget instanceof Element ? args[0].currentTarget : null;
      if (control && actionsInFlight.has(control)) return Promise.resolve();
      if (control) {
        actionsInFlight.add(control);
        control.setAttribute("aria-busy", "true");
      }
      const critical = /^(?:LOTE_|LIKES_|ENVIO_)/.test(code);
      const task = Promise.resolve()
        .then(() => window.SmartFoxAccess.assertAuthorized({ force: critical }))
        .then(() => { assertWorkActive(); return handler.apply(this, args); }).catch((error) => {
        if (app.abandoning || error?.code === "WORK_ABANDONED") return;
        const rawMessage = error?.message || String(error);
        const detectedCode = errorCode(error);
        const finalCode = detectedCode && detectedCode !== "EXECUTION_ERROR" ? detectedCode : code;
        const message = rawMessage.startsWith(`[${finalCode}]`) ? rawMessage : `[${finalCode}] ${rawMessage}`;
        setSiteStatus("danger", message);
        log(message, "error", { code: finalCode });
      }).finally(() => {
        if (control) {
          actionsInFlight.delete(control);
          control.removeAttribute("aria-busy");
        }
        renderSystemHealth();
      });
      return trackWork(task);
    };
  }

  function healthState(element, valueElement, state, value) {
    element.dataset.state = state;
    valueElement.textContent = value;
  }

  function renderSystemHealth() {
    const siteState = app.diagnosis?.ready ? "ready" : app.diagnosis?.error ? "danger" : app.diagnosis ? "warning" : "waiting";
    const siteValue = app.diagnosis?.ready ? "Pronto" : app.diagnosis?.state?.loginDetected ? "Novo acesso" : app.diagnosis ? "Ação necessária" : "A testar";
    healthState(ui.healthSite, ui.healthSiteValue, siteState, siteValue);
    const storageState = app.storageHealth.status === "healthy" ? "ready" : app.storageHealth.status === "error" ? "danger" : app.storageHealth.status === "testing" ? "running" : "waiting";
    const storageValue = app.storageHealth.status === "healthy" ? `${app.storageHealth.latencyMs} ms` : app.storageHealth.status === "error" ? "Falhou" : app.storageHealth.status === "testing" ? "Testando" : "A testar";
    healthState(ui.healthStorage, ui.healthStorageValue, storageState, storageValue);
    if (!app.session) healthState(ui.healthBatch, ui.healthBatchValue, "waiting", "Nenhum");
    else if (app.cleanupBusy) healthState(ui.healthBatch, ui.healthBatchValue, "running", "Retirando likes");
    else if (Engine.needsBankCleanup(app.session) && app.session.currentIndex>=app.session.items.length) healthState(ui.healthBatch, ui.healthBatchValue, "warning", "Likes pendentes");
    else if (app.running) healthState(ui.healthBatch, ui.healthBatchValue, "running", `${app.session.currentIndex}/${app.session.items.length}`);
    else if (app.session.status === "completed") healthState(ui.healthBatch, ui.healthBatchValue, "ready", "Concluído");
    else if (app.session.confirmedAt) healthState(ui.healthBatch, ui.healthBatchValue, "warning", "Retomar");
    else healthState(ui.healthBatch, ui.healthBatchValue, "warning", `${app.session.parsed?.validQuestionCount ?? app.session.parsed?.executableCount ?? 0} válidas`);
  }

  function activeTagConfig() {
    return app.session?.tagConfig || app.pendingTagConfig;
  }

  function selectedGraduationTag() {
    return activeTagConfig()?.target || null;
  }

  function manualTagSelectionState(target, state) {
    const records = Array.isArray(state?.disciplineRecords) ? state.disciplineRecords : [];
    if (!target) return { verified: false, disciplines: [], matches: [] };
    const matches = records.filter((record) => (record.tags || []).some((tag) => String(tag.id || "") === String(target.id || "") || Approval.normalize(tag.label) === Approval.normalize(target.label)));
    return { verified: matches.length > 0, disciplines: matches.map((record) => record.discipline || record.text).filter(Boolean), matches };
  }

  function applyManualTagVerification(state) {
    const config = activeTagConfig();
    if (!config) return;
    if (!state?.supportedPage || !state?.formReady || !Array.isArray(state.disciplineRecords)) return;
    const verification = manualTagSelectionState(config.target, state || app.diagnosis?.state);
    config.verifiedInStep3 = verification.verified;
    config.verifiedAt = verification.verified ? new Date().toISOString() : null;
    config.selectedDisciplines = verification.disciplines;
    if (app.session) app.session.tagConfig = config;
  }

  function renderTagPanel() {
    const catalog = app.tagCatalog;
    const config = activeTagConfig();
    const locked = Boolean(app.session?.confirmedAt);
    const canRemapCompletedBatch = Boolean(app.session?.status === "completed" && app.session?.approvalSync?.enabled && !app.running && !app.approvalRunning);
    if (!catalog) {
      ui.tagBadge.textContent = "0";
      ui.tagChoice.hidden = true;
      ui.tagSummary.className = "aab-tag-summary";
      ui.tagSummary.innerHTML = "<strong>Mapeamento obrigatório</strong><span>Abra o formulário Elaborador; a extensão apenas lerá as escolhas dos Passos 1–3.</span>";
      ui.mapTags.disabled = app.running || app.approvalRunning;
      return;
    }
    const groupText = Object.entries(catalog.groups || {}).map(([group, count]) => `${group}: ${count}`).join(" · ");
    ui.tagBadge.textContent = String(catalog.eligibleCount);
    ui.tagChoice.hidden = false;
    ui.tagSummary.className = `aab-tag-summary ${catalog.eligibleCount ? "aab-tag-ready" : "aab-tag-alert"}`;
    ui.tagSummary.innerHTML = `<strong>${catalog.total} tag(s) mapeada(s) agora</strong><span>${catalog.eligibleCount} de Graduação disponíveis · ${catalog.ignoredCount} de outros grupos ignoradas${groupText ? ` · ${escapeHtml(groupText)}` : ""}.</span><small>Assinatura ${escapeHtml(catalog.signature)} · ${escapeHtml(formatClock(catalog.mappedAt))}</small>`;
    const chosenId = String(config?.target?.id || "");
    ui.targetTag.innerHTML = `<option value="">Selecione uma tag de Graduação</option>${catalog.eligible.map((tag) => `<option value="${escapeHtml(tag.id)}">${escapeHtml(tag.label)}</option>`).join("")}`;
    ui.targetTag.value = catalog.eligible.some((tag) => tag.id === chosenId) ? chosenId : "";
    ui.targetTag.disabled = locked || app.running;
    ui.syncLikes.checked = false;
    ui.syncLikes.disabled = true;
    ui.mapTags.disabled = (locked && !canRemapCompletedBatch) || app.running || app.approvalRunning;
    const selection = manualTagSelectionState(config?.target, app.diagnosis?.state);
    if (config?.target) {
      const detail = selection.verified
        ? `Confirmada na escolha manual do Passo 3 para ${selection.disciplines.join(", ") || "a disciplina adicionada"}.`
        : "Ainda não encontrada nas linhas adicionadas no Passo 3; volte ao AvaliA, faça a escolha manual e teste novamente.";
      ui.tagSummary.innerHTML += `<div class="aab-tag-verification ${selection.verified ? "aab-tag-verified" : "aab-tag-unverified"}"><b>${selection.verified ? "✓" : "!"}</b><span>${escapeHtml(config.target.label)} — ${escapeHtml(detail)}</span></div>`;
    }
  }

  function acceptMappedTagCatalog(rawCatalog, options) {
    const received = rawCatalog?.tags ? rawCatalog.tags : rawCatalog;
    const summary = Approval.summarizeCatalog(received || []);
    const mapped = {
      ...summary,
      mappedAt: rawCatalog?.mappedAt || new Date().toISOString()
    };
    const previousSignature = app.tagCatalog?.signature || app.session?.tagConfig?.catalogSummary?.signature || "";
    const changed = Boolean(previousSignature && previousSignature !== mapped.signature);
    app.tagCatalog = mapped;
    const config = activeTagConfig();
    if (changed && config) {
      config.verifiedInStep3 = false;
      config.verifiedAt = null;
      config.catalogChangedAt = new Date().toISOString();
      if (app.session?.confirmedAt) {
        app.session.approvalSync.status = "catalog_changed";
        app.session.approvalSync.plan = null;
      } else {
        config.target = null;
        config.syncLatestOnly = false;
      }
      if (app.session && !app.session.confirmedAt) {
        app.session.approvalSync.enabled = false;
        app.session.approvalSync.status = "catalog_changed";
        app.session.approvalSync.plan = null;
      }
      recordOccurrence("[CATALOGO_TAGS_ALTERADO] A lista de tags mudou desde o último mapeamento. Escolha novamente uma tag de Graduação; nenhum like foi alterado.", "warning", { code: "CATALOGO_TAGS_ALTERADO" });
    }
    if (config) {
      config.catalogSummary = {
        total: mapped.total,
        eligibleCount: mapped.eligibleCount,
        ignoredCount: mapped.ignoredCount,
        groups: mapped.groups,
        signature: mapped.signature,
        mappedAt: mapped.mappedAt
      };
      config.catalogSnapshot = mapped.catalog;
      applyManualTagVerification(options?.state || app.diagnosis?.state);
    }
    renderTagPanel();
    return { mapped, changed };
  }

  async function mapTagsNow(options) {
    ui.mapTags.disabled = true;
    ui.mapTags.textContent = "Mapeando…";
    try {
      const raw = await bridge("getTagCatalog", {}, 10000);
      const result = acceptMappedTagCatalog(raw, { state: app.diagnosis?.state });
      const message = `${result.mapped.total} tag(s) lida(s): ${result.mapped.eligibleCount} de Graduação disponíveis e ${result.mapped.ignoredCount} de outros grupos ignoradas.`;
      if (app.session?.status === "completed" && app.session?.approvalSync?.enabled) {
        const targetCheck = Approval.verifyGraduationTarget(result.mapped.catalog, app.session.tagConfig?.target);
        if (targetCheck.valid) {
          app.session.approvalSync.catalogCheckedAt = new Date().toISOString();
          app.session.approvalSync.catalogSignature = result.mapped.signature;
          app.session.approvalSync.status = "awaiting_professor";
          app.session.approvalSync.plan = null;
          app.session.approvalSync.updatedAt = new Date().toISOString();
          if (!options?.silent) log(`A tag original “${targetCheck.target.label}” continua válida em Graduação. A prévia de likes foi liberada para o perfil Professor.`, "success", { code: "TAG_REMESSA_RECONFIRMADA" });
        } else {
          app.session.approvalSync.status = "catalog_changed";
          app.session.approvalSync.plan = null;
          app.session.approvalSync.updatedAt = new Date().toISOString();
          if (!options?.silent) log(`[CATALOGO_TAGS_ALTERADO] A tag original da remessa não pôde ser confirmada em Graduação: ${targetCheck.message} Nenhum like será alterado.`, "warning", { code: "CATALOGO_TAGS_ALTERADO" });
        }
      }
      if (!options?.silent) log(`Mapeamento de tags concluído. ${message}`, "success", { code: "TAGS_MAPEADAS" });
      if (app.session) await saveSession();
      return result;
    } catch (error) {
      app.tagCatalog = null;
      renderTagPanel();
      if (!options?.silent) log(error.message, "warning", { code: errorCode(error) || "CATALOGO_TAGS_NAO_VISIVEL" });
      return { mapped: null, changed: false, error };
    } finally {
      ui.mapTags.textContent = "Mapear tags atuais";
      renderTagPanel();
    }
  }

  async function chooseTargetTag() {
    const config = activeTagConfig();
    const target = app.tagCatalog?.eligible.find((tag) => tag.id === ui.targetTag.value) || null;
    if (!config) return;
    config.target = target;
    config.syncLatestOnly = false;
    applyManualTagVerification(app.diagnosis?.state);
    if (app.session) {
      app.session.tagConfig = config;
      app.session.approvalSync.enabled = Boolean(config.syncLatestOnly);
      app.session.approvalSync.status = config.syncLatestOnly ? "waiting_for_batch" : "not_requested";
      app.session.approvalSync.plan = null;
      await saveSession();
    }
    renderTagPanel();
    renderReadiness();
  }

  async function setLikeSyncOption() {
    const config = activeTagConfig();
    if (!config) return;
    config.syncLatestOnly = false;
    if (app.session) {
      app.session.approvalSync.enabled = config.syncLatestOnly;
      app.session.approvalSync.status = config.syncLatestOnly ? "waiting_for_batch" : "not_requested";
      app.session.approvalSync.plan = null;
      await saveSession();
    }
    renderTagPanel();
    renderApprovalSync();
  }

  function switchView(view) {
    const allowed = ["prepare", "base", "review", "run", "help"];
    app.currentView = allowed.includes(view) ? view : "prepare";
    ui.navButtons.forEach((button) => {
      const active = button.dataset.aabNav === app.currentView;
      button.classList.toggle("aab-nav-active", active);
      button.setAttribute("aria-current", active ? "page" : "false");
    });
    ui.viewSections.forEach((section) => section.classList.toggle("aab-view-hidden", section.dataset.aabView !== app.currentView));
    if (app.currentView === "help") renderHelpIdentity();
  }

  function renderHelpIdentity() {
    const status = window.SmartFoxAccess?.getStatus?.();
    if (!ui.helpIdentity) return;
    const name = status?.identity?.avaliaName || status?.profile?.avaliaName || "";
    ui.helpIdentity.dataset.state = status?.authorized ? "verified" : "blocked";
    ui.helpIdentity.innerHTML = `<span>SmartFox Autônomo · uso local</span><strong>${escapeHtml(name || "Sem cadastro ou ativação no SmartFox")}</strong>`;
  }

  function filterHelp() {
    const term = String(ui.helpSearch?.value || "").trim().toLowerCase();
    let visible = 0;
    Array.from(ui.helpList?.querySelectorAll("details") || []).forEach((item) => {
      item.hidden = Boolean(term) && !`${item.dataset.help || ""} ${item.textContent || ""}`.toLowerCase().includes(term);
      if (!item.hidden) visible += 1;
    });
    const total = Array.from(ui.helpList?.querySelectorAll("details") || []).length;
    ui.helpResults.textContent = term ? `${visible} resposta(s) encontrada(s)` : `${total} respostas rápidas disponíveis`;
    ui.helpEmpty.hidden = visible > 0;
  }

  async function handleHelpAction(event) {
    const button = event.target.closest("[data-aab-help-action]");
    if (!button) return;
    const action = button.dataset.aabHelpAction;
    if (action === "account") return window.SmartFoxAccess.openAccount();
    if (action === "announcements") return window.SmartFoxAccess.openAnnouncements();
    if (action === "test") {
      switchView("prepare");
      return ui.testProfile.click();
    }
    if (action === "external") {
      switchView("base");
      ui.externalExamFile.focus();
      return;
    }
    if (["review", "run"].includes(action) && !app.session) {
      switchView("prepare");
      modeStrip("warning", "Importe ou gere as questões primeiro.", "Depois, Revisar e Executar serão liberados.");
      return;
    }
    if (["prepare", "base", "review", "run"].includes(action)) switchView(action);
  }

  function renderNavigation() {
    ui.navButtons.forEach((button) => {
      const view = button.dataset.aabNav;
      const unavailable = ["review", "run"].includes(view) && !app.session;
      button.disabled = unavailable;
      button.title = unavailable ? "Importe ou produza questões primeiro." : "";
    });
    if (!app.session && ["review", "run"].includes(app.currentView)) app.currentView = "prepare";
    switchView(app.currentView);
  }

  function knowledgeRequiresDecision(question, index) {
    const audit = question?.knowledgeAudit;
    const item = reviewItem(index);
    if (!audit || audit.status === "no_base" || audit.status === "supported") return false;
    return !item?.knowledgeDecision;
  }

  function activeKnowledgeCollection() {
    return Knowledge.activeCollection(app.knowledgeBase);
  }

  function scopedKnowledgeBase() {
    return Knowledge.scopeBase(app.knowledgeBase, activeKnowledgeCollection().id);
  }

  function applyCollectionDefaults() {
    const collection = activeKnowledgeCollection();
    const specific = collection.id !== Knowledge.defaultCollectionId;
    if (specific) {
      ui.generationEvaluation.value = collection.evaluation;
      ui.generationTheme.value = collection.subject;
      ui.materialSubject.value = collection.subject;
    } else {
      ui.generationTheme.value = "";
      ui.materialSubject.value = "";
    }
    ui.generationUas.value = collection.defaultUas || "";
    ui.generationDifficulty.value = collection.defaultDifficulty || "auto";
    ui.generationCount.value = collection.defaultCount || "";
    const previousRules = collection.rulesText || app.knowledgeBase.rules?.activeText || "";
    ui.generationRules.value = Athus.masterText(previousRules) ? "" : previousRules;
    ui.materialSubject.readOnly = specific;
    ui.generationTheme.readOnly = specific;
    ui.generationEvaluation.disabled = specific || app.running || app.knowledgeBusy;
  }

  function openCollectionEditor(mode) {
    const active = activeKnowledgeCollection();
    if (mode === "edit" && active.id === Knowledge.defaultCollectionId) {
      setBaseProgress("warning", "O Acervo geral é reservado para compatibilidade. Crie uma coleção identificada para organizar a avaliação.");
      return;
    }
    app.collectionEditorMode = mode;
    ui.collectionEditor.hidden = false;
    ui.collectionEditorTitle.textContent = mode === "edit" ? "Editar coleção permanente" : "Nova coleção permanente";
    ui.collectionEvaluation.value = mode === "edit" ? active.evaluation : "P1";
    ui.collectionSubject.value = mode === "edit" ? active.subject : "";
    ui.collectionSubject.focus();
  }

  function closeCollectionEditor() {
    app.collectionEditorMode = "";
    ui.collectionEditor.hidden = true;
    ui.collectionSubject.value = "";
  }

  async function saveCollectionEditor() {
    if (app.running || app.knowledgeBusy) return;
    const active = activeKnowledgeCollection();
    try {
      const result = Knowledge.upsertCollection(app.knowledgeBase, {
        id: app.collectionEditorMode === "edit" ? active.id : undefined,
        evaluation: ui.collectionEvaluation.value,
        subject: ui.collectionSubject.value
      });
      app.knowledgeBase = result.base;
      if (!result.created && active.subject !== result.collection.subject) {
        setBaseProgress("neutral", `Reclassificando os materiais de “${result.collection.name}”…`);
        app.knowledgeBase = Knowledge.updateCollectionDocumentSubjects(app.knowledgeBase, result.collection.id, result.collection.subject).base;
      }
      closeCollectionEditor();
      applyCollectionDefaults();
      await persistKnowledgeBase();
      renderKnowledgeBase();
      setBaseProgress("success", `${result.created ? "Coleção criada" : "Coleção atualizada"}: ${result.collection.name}. Os próximos arquivos ficarão guardados nela.`);
      log(`${result.created ? "Coleção permanente criada" : "Coleção permanente atualizada"}: ${result.collection.name}.`, "success", { code: result.created ? "COLECAO_CRIADA" : "COLECAO_ATUALIZADA" });
    } catch (error) {
      setBaseProgress("warning", error.message);
    }
  }

  async function selectActiveCollection() {
    if (app.running || app.knowledgeBusy) return;
    const current = activeKnowledgeCollection();
    const target = Knowledge.listCollections(app.knowledgeBase).find((collection) => collection.id === ui.collectionSelect.value);
    if (!target) return;
    if (app.session?.parsed?.questions?.length && app.session.knowledgeCollectionId && app.session.knowledgeCollectionId !== target.id) {
      const approved = window.confirm(`O lote aberto foi conferido com “${app.session.knowledgeCollectionName || current.name}”. Trocar para “${target.name}” refará a análise de conteúdo e as decisões bibliográficas pendentes. Continuar?`);
      if (!approved) {
        renderKnowledgeBase();
        return;
      }
    }
    const result = Knowledge.selectCollection(app.knowledgeBase, ui.collectionSelect.value);
    if (!result.selected) return;
    cancelMaterialEditor();
    resetExternalExam({ clearFile: true });
    app.knowledgeBase = result.base;
    applyCollectionDefaults();
    await persistKnowledgeBase();
    renderKnowledgeBase();
    if (app.session) await scanQuestionsWithBase({ silent: false });
    setBaseProgress("success", `Coleção ativa: ${result.collection.name}.`);
  }

  async function deleteActiveCollection() {
    if (app.running || app.knowledgeBusy) return;
    const collection = activeKnowledgeCollection();
    if (collection.id === Knowledge.defaultCollectionId) {
      setBaseProgress("warning", "O Acervo geral não pode ser excluído.");
      return;
    }
    const stats = Knowledge.baseStats(app.knowledgeBase, collection.id);
    if (!window.confirm(`Excluir a coleção “${collection.name}” e seus ${stats.documents} material(is)? Avaliações já enviadas ao AvaliA não serão alteradas.`)) return;
    const result = Knowledge.removeCollection(app.knowledgeBase, collection.id);
    cancelMaterialEditor();
    resetExternalExam({ clearFile: true });
    app.knowledgeBase = result.base;
    applyCollectionDefaults();
    await persistKnowledgeBase();
    renderKnowledgeBase();
    if (app.session) await scanQuestionsWithBase({ silent: true });
    setBaseProgress("success", `Coleção excluída. ${result.removedDocuments} material(is) removido(s) do acervo local.`);
    log(`Coleção ${collection.name} excluída com ${result.removedDocuments} material(is).`, "warning", { code: "COLECAO_EXCLUIDA" });
  }

  async function persistCollectionPreferences() {
    const collection = activeKnowledgeCollection();
    const result = Knowledge.updateCollectionPreferences(app.knowledgeBase, collection.id, {
      defaultUas: ui.generationUas.value,
      defaultDifficulty: ui.generationDifficulty.value,
      defaultCount: Number(ui.generationCount.value || 0),
      rulesText: ui.generationRules.value.trim() || Knowledge.defaultRules
    });
    app.knowledgeBase = result.base;
    await persistKnowledgeBase();
  }

  async function persistKnowledgeBase() {
    const snapshot = app.knowledgeBase;
    const operation = knowledgeWriteQueue.then(
      () => storageSet({ [KNOWLEDGE_KEY]: snapshot }),
      () => storageSet({ [KNOWLEDGE_KEY]: snapshot })
    );
    knowledgeWriteQueue = operation.catch(() => {});
    await operation;
  }

  function formatSize(bytes) {
    const value = Number(bytes || 0);
    if (value < 1024) return `${value} B`;
    if (value < 1024 * 1024) return `${Math.round(value / 1024)} KB`;
    return `${(value / (1024 * 1024)).toFixed(1)} MB`;
  }

  function currentAthusRules() {
    const collection=activeKnowledgeCollection();
    return Athus.resolve(ui.generationRules.value,{evaluation:collection.evaluation === "GENERAL" ? ui.generationEvaluation.value : collection.evaluation,
      theme:collection.subject || ui.generationTheme.value.trim(),count:ui.generationCount.value,uas:ui.generationUas.value,difficulty:ui.generationDifficulty.value});
  }
  function refreshAthusPreview() {
    const evaluation=activeKnowledgeCollection().evaluation === "GENERAL" ? ui.generationEvaluation.value : activeKnowledgeCollection().evaluation;
    ui.p1CompositionField.hidden=evaluation !== "P1";
    ui.p1Composition.value=["12","18"].includes(String(ui.generationCount.value)) ? String(ui.generationCount.value) : "";
    ui.p1Composition.disabled=app.running || app.knowledgeBusy;
    try { ui.athusRulesPreview.textContent=Athus.describe(currentAthusRules()); }
    catch(error) { ui.athusRulesPreview.textContent=error.message; }
  }
  function assessmentAthusReport(requireReview) {
    if (!app.session?.generatedFromKnowledgeBase) return null;
    return Athus.batch(app.session.parsed.questions,app.session.parsed.generationRules,{requireReview});
  }
  async function applyAthusRulesToBatch() {
    if (!app.session?.generatedFromKnowledgeBase || app.running) return;
    const rules=currentAthusRules();
    app.session.parsed.generationRules=rules;
    app.session.parsed.questions.forEach((question,index)=>{
      question.generationRules=rules; delete question.athusReview;
      if(app.session.items[index]?.phase === P.PENDING) Engine.revokeAuthorization(app.session,index);
    });
    await saveSession(); renderSession(); refreshAthusPreview();
    ui.athusBatchStatus.textContent="Regras aplicadas ao lote. Confira as pendências antes de liberar.";
  }
  async function downloadAthusDraft() {
    if (!app.session?.parsed?.questions?.length || app.running) return;
    await Exporter.download(app.session.parsed.questions,{...assessmentDownloadMetadata(),draft:true,title:"Rascunho para revisão docente"});
  }

  function renderKnowledgeBase() {
    const collection = activeKnowledgeCollection();
    const scope = scopedKnowledgeBase();
    const stats = Knowledge.baseStats(app.knowledgeBase, collection.id);
    const globalStats = Knowledge.baseStats(app.knowledgeBase);
    const collectionStats = Knowledge.collectionStats(app.knowledgeBase);
    const audit = stats.premiumAudit || Curator.baseAudit(scope);
    ui.collectionSelect.innerHTML = collectionStats.map((entry) => `<option value="${escapeHtml(entry.id)}"${entry.id === collection.id ? " selected" : ""}>${escapeHtml(entry.name)} (${entry.documents})</option>`).join("");
    ui.collectionSummary.innerHTML = `<strong>${escapeHtml(collection.name)}</strong><span>${collection.id === Knowledge.defaultCollectionId ? "Compatibilidade com acervos antigos" : `${escapeHtml(collection.evaluation)} · ${escapeHtml(collection.subject)}`} · ${stats.documents} material(is) · ${stats.safeFacts} trechos disponíveis</span>`;
    const databaseState = app.storageHealth.status;
    ui.databaseSummary.className = `aab-database-summary aab-database-${escapeHtml(databaseState)}`;
    ui.databaseSummary.innerHTML = databaseState === "healthy"
      ? `<strong>Banco deste perfil aprovado</strong><span>${escapeHtml(app.storageHealth.message)} ${globalStats.documents} material(is) persistidos em ${globalStats.collections} coleção(ões).</span>`
      : databaseState === "error"
        ? `<strong>Falha no banco deste perfil</strong><span>${escapeHtml(app.storageHealth.message)} Recarregue a extensão antes de executar um lote.</span>`
        : `<strong>Banco exclusivo deste perfil</strong><span>Teste a persistência. Para levar o acervo a outro perfil, exporte e importe um backup verificado.</span>`;
    ui.baseCount.textContent = String(stats.documents);
    ui.baseSummary.innerHTML = stats.documents
      ? `<strong>${stats.documents} arquivo(s) nesta coleção</strong><span>${stats.words.toLocaleString("pt-BR")} palavras · ${stats.safeFacts} fatos seguros · ${stats.quarantined} trecho(s) em quarentena · ${globalStats.documents} arquivo(s) em ${globalStats.collections} coleção(ões)</span>`
      : `A coleção “${escapeHtml(collection.name)}” está vazia. Inclua um plano de ensino e materiais de conteúdo; eles permanecerão disponíveis neste perfil.`;
    ui.curationDashboard.hidden = !stats.documents;
    ui.curationDashboard.innerHTML = stats.documents ? `
      <div><b>${stats.roles?.teaching_plan || 0}</b><span>planos</span></div>
      <div><b>${stats.objectives}</b><span>objetivos</span></div>
      <div><b>${stats.roles?.reference_material || 0}</b><span>conteúdos</span></div>
      <div><b>${stats.safeFacts}</b><span>trechos disponíveis</span></div>
      <div><b>${stats.roles?.assessment_model || 0}</b><span>modelos</span></div>
      <div><b>${stats.modelQuestions}</b><span>questões-modelo</span></div>
      <div class="${stats.conflicts ? "aab-curation-alert" : ""}"><b>${stats.conflicts}</b><span>conflitos</span></div>
      <div><b>${stats.quarantined}</b><span>quarentena</span></div>` : "";
    ui.baseList.innerHTML = scope.documents.length ? scope.documents.map((document) => `
      <li class="${document.analysis?.blockingIssues?.length ? "aab-base-item-warning" : ""}"><div><span class="aab-role-pill aab-role-${escapeHtml(document.role || "reference_material")}">${escapeHtml(Curator.roleLabels[document.role] || document.role || "Material")}</span><strong>${escapeHtml(document.name)}</strong><small>${escapeHtml(document.subject || "Disciplina não classificada")} · ${document.assignedUa ? `UA${document.assignedUa}` : document.analysis?.curriculum?.uas?.length ? `${document.analysis.curriculum.uas.length} UAs no plano` : "UA por títulos internos"}</small><small>${document.role === Curator.roles.TEACHING_PLAN ? `${document.analysis?.curriculum?.specificObjectives?.length || 0} objetivos · ${document.analysis?.curriculum?.uas?.length || 0} UAs` : document.role === Curator.roles.ASSESSMENT_MODEL ? `${document.analysis?.blueprint?.questionCount || 0} questões-modelo · ${document.analysis?.blueprint?.fourAlternativeCompliance || 0}% com A–D` : document.role === Curator.roles.REFERENCE ? `${document.analysis?.evidence?.facts?.length || 0} fatos seguros · ${document.analysis?.quarantine?.count || 0} em quarentena` : `${document.analysis?.quarantine?.count || 0} trechos isolados`} · ${formatSize(document.sourceSize)}</small>${document.analysis?.warnings?.length ? `<small class="aab-doc-warning">${escapeHtml(document.analysis.warnings[0])}</small>` : ""}<label class="aab-document-collection"><span>Mover para</span><select data-aab-move-material="${escapeHtml(document.id)}">${collectionStats.map((entry) => `<option value="${escapeHtml(entry.id)}"${entry.id === document.collectionId ? " selected" : ""}>${escapeHtml(entry.name)}</option>`).join("")}</select></label></div><span class="aab-base-item-actions"><button type="button" class="aab-edit-material-button" data-aab-edit-material="${escapeHtml(document.id)}" aria-label="Editar classificação de ${escapeHtml(document.name)}">Classificar</button><button type="button" data-aab-remove-material="${escapeHtml(document.id)}" aria-label="Remover ${escapeHtml(document.name)}">Remover</button></span></li>`).join("") : "";
    const specific = collection.id !== Knowledge.defaultCollectionId;
    const answerSources = scope.documents.filter((document) => document.role === Curator.roles.REFERENCE && Array.isArray(document.chunks) && document.chunks.length);
    if (app.externalExamReport) {
      const reportSignature = (app.externalExamReport.sourceDocuments || []).map((document) => `${document.id}:${document.fingerprint}`).sort().join("|");
      const currentSignature = answerSources.map((document) => `${document.id}:${document.fingerprint}`).sort().join("|");
      if (app.externalExamReport.collection?.id !== collection.id || reportSignature !== currentSignature) {
        app.externalExamReport = null;
        ui.externalExamResults.hidden = true;
        ui.externalExamResults.innerHTML = "";
        ui.externalExamStatus.className = "aab-external-status aab-external-warning";
        ui.externalExamStatus.innerHTML = "<strong>O acervo mudou.</strong><span>Analise novamente a prova para impedir um gabarito baseado em fontes antigas.</span>";
      }
    }
    ui.externalCollectionSummary.className = `aab-external-collection-summary ${specific && answerSources.length ? "aab-external-ready" : "aab-external-blocked"}`;
    ui.externalCollectionSummary.innerHTML = specific
      ? answerSources.length
        ? `<strong>${escapeHtml(collection.name)}</strong><span>${answerSources.length} material(is) de conteúdo disponível(is) para responder sem internet.</span>`
        : `<strong>${escapeHtml(collection.name)}</strong><span>Nenhum arquivo classificado como Material de conteúdo. Planos, modelos e regras não serão usados como resposta.</span>`
      : `<strong>Escolha uma coleção de disciplina</strong><span>O Acervo geral é amplo demais e permanece bloqueado para evitar respostas da matéria errada.</span>`;
    ui.collectionSelect.disabled = app.running || app.knowledgeBusy;
    ui.newCollection.disabled = app.running || app.knowledgeBusy;
    ui.editCollection.disabled = app.running || app.knowledgeBusy || !specific;
    ui.deleteCollection.disabled = app.running || app.knowledgeBusy || !specific;
    ui.testDatabase.disabled = app.running || app.knowledgeBusy || app.storageHealth.status === "testing";
    ui.materialFiles.disabled = app.running || app.knowledgeBusy;
    ui.materialRole.disabled = app.running || app.knowledgeBusy;
    ui.materialSubject.disabled = app.running || app.knowledgeBusy;
    ui.materialSubject.readOnly = specific;
    ui.materialUa.disabled = app.running || app.knowledgeBusy;
    ui.addMaterials.disabled = app.running || app.knowledgeBusy;
    ui.importBase.disabled = app.running || app.knowledgeBusy;
    ui.scanBase.disabled = app.running || app.knowledgeBusy || !stats.documents || !app.session;
    ui.generateQuestions.disabled = app.running || app.knowledgeBusy || app.abandoning || !stats.documents;
    ui.openAssessmentWord.disabled = app.running || app.knowledgeBusy || app.fileImportBusy || app.abandoning;
    ui.auditBase.disabled = app.running || app.knowledgeBusy || !stats.documents;
    ui.exportBase.disabled = !globalStats.documents;
    ui.exportCollection.disabled = !stats.documents;
    ui.clearBase.disabled = app.running || app.knowledgeBusy || !stats.documents;
    ui.saveMaterial.disabled = app.running || app.knowledgeBusy;
    ui.cancelMaterial.disabled = app.running || app.knowledgeBusy;
    ui.generationEvaluation.disabled = app.running || app.knowledgeBusy || specific;
    ui.generationTheme.disabled = app.running || app.knowledgeBusy;
    ui.generationTheme.readOnly = specific;
    ui.externalExamFile.disabled = app.running || app.knowledgeBusy;
    ui.analyzeExternalExam.disabled = app.running || app.knowledgeBusy || !specific || !answerSources.length || !ui.externalExamFile.files?.length;
    ui.downloadExternalReport.hidden = !app.externalExamReport;
    ui.downloadExternalReport.disabled = app.running || app.knowledgeBusy || !app.externalExamReport;
    ui.clearExternalReport.hidden = !app.externalExamReport && !ui.externalExamFile.files?.length;
    ui.clearExternalReport.disabled = app.running || app.knowledgeBusy;
    const generatedAvailable = Boolean(app.session?.parsed?.questions?.length);
    ui.downloadAthusDraft.hidden = !generatedAvailable || !app.session?.generatedFromKnowledgeBase;
    ui.downloadAthusDraft.disabled = app.running;
    ui.applyAthusRules.disabled = app.running || !app.session?.generatedFromKnowledgeBase;
    refreshAthusPreview();
    const athusReport=assessmentAthusReport(true);
    ui.athusBatchStatus.textContent=athusReport ? (athusReport.ok ? "Regras conferidas e revisão docente registrada." : `Rascunho: ${athusReport.issues.length} pendência(s) Athus. ${athusReport.issues.slice(0,3).map(i=>i.message).join(" ")}`) : "";
    ui.downloadAssessmentPackage.hidden = !generatedAvailable;
    ui.downloadAssessmentPackage.disabled = app.running;
    ui.downloadGeneratedDocx.hidden = !generatedAvailable;
    ui.downloadGeneratedDocx.disabled = app.running;
    ui.downloadGeneratedDocxReview.hidden = !generatedAvailable;
    ui.downloadGeneratedDocxReview.disabled = app.running;
    ui.downloadStudyGuide.hidden = !generatedAvailable;
    ui.downloadStudyGuide.disabled = app.running;
    ui.downloadStudyGuideReview.hidden = !generatedAvailable;
    ui.downloadStudyGuideReview.disabled = app.running;
    renderSystemHealth();
  }

  async function loadKnowledgeBase() {
    const stored = await storageGet([KNOWLEDGE_KEY, ...LEGACY_KNOWLEDGE_KEYS]);
    const sourceKey = stored?.[KNOWLEDGE_KEY] ? KNOWLEDGE_KEY : LEGACY_KNOWLEDGE_KEYS.find((key) => stored?.[key]);
    app.knowledgeBase = Knowledge.hydrateBase(sourceKey ? stored[sourceKey] : null);
    const initialIntegrity = Knowledge.integrityReport(app.knowledgeBase);
    if (!initialIntegrity.ok) throw new Error(`[BASE_INTEGRIDADE] ${initialIntegrity.blocking[0]}`);
    if (app.knowledgeBase.rules?.sourceName === "Padrão Athus integrado" && chrome.runtime?.getURL) {
      try {
        const response = await fetch(chrome.runtime.getURL("REGRAS_PROJETO_ATHUS.md"));
        const fullRules = response.ok ? await response.text() : "";
        if (fullRules.length > app.knowledgeBase.rules.activeText.length) {
          app.knowledgeBase.rules = { activeText: fullRules, sourceName: "Regras oficiais Athus integradas", updatedAt: new Date().toISOString() };
          await persistKnowledgeBase();
        }
      } catch (_error) {
        // O resumo seguro embutido continua disponível quando o recurso não puder ser lido.
      }
    }
    applyCollectionDefaults();
    if (sourceKey && sourceKey !== KNOWLEDGE_KEY) {
      await persistKnowledgeBase();
      log("Acervo anterior migrado para coleções permanentes. Os materiais existentes foram preservados no Acervo geral.", "success", { code: "BASE_MIGRADA_V9" });
    }
    renderKnowledgeBase();
    if (initialIntegrity.warnings.length) setBaseProgress("warning", `Banco aberto com integridade ${initialIntegrity.score}%: ${initialIntegrity.warnings[0]}`);
  }

  async function persistGenerationRules(sourceName) {
    const activeText = ui.generationRules.value.trim() || Knowledge.defaultRules;
    // Empty activity instructions inherit the visible institutional summary.
    const collection = activeKnowledgeCollection();
    if (collection.id === Knowledge.defaultCollectionId) {
      const updatedAt = new Date().toISOString();
      app.knowledgeBase.rules = {
        activeText,
        sourceName: sourceName || app.knowledgeBase.rules?.sourceName || "regras digitadas",
        updatedAt
      };
      app.knowledgeBase.updatedAt = updatedAt;
    }
    await persistCollectionPreferences();
  }

  function setBaseProgress(kind, message, hidden) {
    ui.baseProgress.hidden = Boolean(hidden);
    ui.baseProgress.className = `aab-status aab-${kind}`;
    ui.baseProgress.textContent = message || "";
  }

  async function scanQuestionsWithBase(options) {
    if (!app.session?.parsed?.questions?.length) {
      setBaseProgress("warning", "Importe ou produza uma avaliação antes de conferir o lote.");
      return { analyzed: 0, issues: 0 };
    }
    const collection = activeKnowledgeCollection();
    const scope = scopedKnowledgeBase();
    const stats = Knowledge.baseStats(app.knowledgeBase, collection.id);
    if (!stats.documents) {
      app.session.parsed.questions.forEach((question) => { question.knowledgeAudit = Knowledge.analyzeQuestion(question, scope); });
      await saveSession();
      renderSession();
      return { analyzed: app.session.parsed.questions.length, issues: 0 };
    }
    const baseChanged = app.session.knowledgeBaseUpdatedAt !== collection.updatedAt || app.session.knowledgeCollectionId !== collection.id;
    let issues = 0;
    app.session.parsed.questions.forEach((question, index) => {
      question.knowledgeAudit = Knowledge.analyzeQuestion(question, scope);
      const item = app.session.items[index];
      if (baseChanged && item.phase === P.PENDING) {
        item.knowledgeDecision = "";
        item.knowledgeReviewedAt = null;
        item.knowledgeReviewNote = "";
        item.knowledgeCorrection = null;
      }
      if (question.knowledgeAudit.status === "supported" && item.phase === P.PENDING) {
        item.knowledgeDecision = "accepted";
        item.knowledgeReviewedAt = question.knowledgeAudit.analyzedAt;
        item.knowledgeReviewNote = "Gabarito sustentado automaticamente pela base consultada.";
      } else if (["mismatch", "review", "insufficient"].includes(question.knowledgeAudit.status)) issues += 1;
    });
    app.session.knowledgeBaseUpdatedAt = collection.updatedAt;
    app.session.knowledgeCollectionId = collection.id;
    app.session.knowledgeCollectionName = collection.name;
    app.session.knowledgeDocumentIds = scope.documents.map((document) => document.id);
    await saveSession();
    renderSession();
    if (!options?.silent) {
      setBaseProgress(issues ? "warning" : "success", `${app.session.parsed.questions.length} questão(ões) conferidas com “${collection.name}”; ${issues} pedem decisão.`);
      log(`Coleção ${collection.name}: ${app.session.parsed.questions.length} questão(ões) verificadas em ${stats.documents} material(is); ${issues} pedem decisão.`, issues ? "warning" : "success", { code: "BASE_CONFERENCIA_COLECAO" });
    }
    return { analyzed: app.session.parsed.questions.length, issues };
  }

  function renderMaterialBatchPreview() {
    const files = Array.from(ui.materialFiles.files || []);
    ui.materialBatchPreview.textContent = files.length ? files.length + " arquivo(s) selecionado(s): " + files.slice(0, 12).map((file) => {
      if (/\.zip$/i.test(file.name)) return file.name + " (ZIP: UAs verificadas ao importar)";
      const detected = Knowledge.detectMaterialUa(file.name, "", ui.materialUa.value);
      return file.name + (detected.ua ? " → UA" + detected.ua : " → verificar títulos internos");
    }).join("; ") + (files.length > 12 ? "; e mais " + (files.length - 12) : "") : "Nenhum material selecionado.";
  }

  async function addSelectedMaterials() {
    const selectedFiles = Array.from(ui.materialFiles.files || []);
    if (!selectedFiles.length || app.knowledgeBusy || app.running) {
      setBaseProgress("warning", "Escolha um ou mais materiais primeiro.");
      return;
    }
    const enteredUa = ui.materialUa.value.trim();
    const parsedUas = Knowledge.parseUaScope(enteredUa);
    if (enteredUa && parsedUas.length !== 1) {
      setBaseProgress("warning", "Para UAs diferentes no mesmo lote, deixe o campo de UA vazio. Preencha apenas quando todos os arquivos forem da mesma UA.");
      return;
    }
    app.knowledgeBusy = true;
    renderKnowledgeBase();
    let added = 0;
    let replaced = 0;
    const failures = [];
    let fatalError = null;
    let lastPersistedBase = app.knowledgeBase;
    const collection = activeKnowledgeCollection();
    const metadata = { collectionId: collection.id, role: ui.materialRole.value || "auto", subject: collection.subject || ui.materialSubject.value.trim(), assignedUa: parsedUas[0] || null };
    try {
      setBaseProgress("neutral", "Preparando o lote e verificando os arquivos ZIP…");
      const batch = await Knowledge.expandMaterialBatch(selectedFiles);
      assertWorkActive();
      const files = batch.files;
      failures.push(...batch.failures);
      for (let index = 0; index < files.length; index += 1) {
        const file = files[index];
        setBaseProgress("neutral", `Lendo ${index + 1} de ${files.length}: ${file.name}`);
        try {
          const text = await Knowledge.extractFile(file);
          assertWorkActive();
          const detected = Knowledge.detectMaterialUa(file.name, text, metadata.assignedUa);
          if (detected.conflict) throw new Error(detected.message);
          const document = Knowledge.buildDocument(file, text, { ...metadata, assignedUa: detected.ua });
          const result = Knowledge.addOrReplace(app.knowledgeBase, document);
          app.knowledgeBase = result.base;
          await persistKnowledgeBase();
          lastPersistedBase = app.knowledgeBase;
          result.replaced ? replaced += 1 : added += 1;
        } catch (error) {
          if (error.code === "WORK_ABANDONED" || /^\[ARMAZENAMENTO_/.test(error.message || "")) throw error;
          failures.push(`${file.name}: ${error.message}`);
          log(`Material não adicionado: ${file.name}. ${error.message}`, "error", { code: "BASE_ARQUIVO_INVALIDO" });
        }
      }
      await persistKnowledgeBase();
    } catch (error) {
      fatalError = error;
      app.knowledgeBase = lastPersistedBase;
    } finally {
      app.knowledgeBusy = false;
      ui.materialFiles.value = "";
      renderKnowledgeBase();
      ui.materialBatchPreview.textContent = failures.length ? "Arquivos pendentes: " + failures.join("; ") : "Lote processado. Confira as UAs na lista da coleção.";
    }
    if (fatalError) {
      setBaseProgress("danger", `A importação foi pausada sem perder os materiais já confirmados: ${fatalError.message}`);
      log(`Importação do acervo pausada: ${fatalError.message}`, "error", { code: errorCode(fatalError) || "BASE_PERSISTENCIA_FALHOU" });
      return;
    }
    const postAudit = Curator.baseAudit(scopedKnowledgeBase());
    const message = `${added} adicionado(s), ${replaced} atualizado(s)${failures.length ? ` e ${failures.length} recusado(s)` : ""} em “${collection.name}”. ${postAudit.quarantineCount} trecho(s) isolado(s); ${postAudit.conflicts.length} conflito(s) aguardam classificação.`;
    setBaseProgress(failures.length ? "warning" : "success", message);
    log(`Base permanente atualizada: ${message}`, failures.length ? "warning" : "success", { code: "BASE_ATUALIZADA" });
    if (app.session) await scanQuestionsWithBase({ silent: false });
  }

  async function removeMaterial(id) {
    if (app.knowledgeBusy) return;
    const document = app.knowledgeBase.documents.find((entry) => entry.id === id);
    if (!document || !window.confirm(`Remover “${document.name}” da coleção “${activeKnowledgeCollection().name}”?`)) return;
    app.knowledgeBase = Knowledge.removeDocument(app.knowledgeBase, id).base;
    await persistKnowledgeBase();
    renderKnowledgeBase();
    if (app.session) await scanQuestionsWithBase({ silent: false });
  }

  async function moveMaterialToCollection(id, targetCollectionId) {
    if (app.knowledgeBusy || app.running) return;
    const document = app.knowledgeBase.documents.find((entry) => entry.id === id);
    const target = Knowledge.listCollections(app.knowledgeBase).find((collection) => collection.id === targetCollectionId);
    if (!document || !target || document.collectionId === target.id) return;
    const result = Knowledge.updateDocumentMetadata(app.knowledgeBase, id, { collectionId: target.id, subject: target.subject || document.subject, role: document.role, assignedUa: document.assignedUa });
    if (!result.updated) {
      setBaseProgress("warning", result.collision ? `“${document.name}” já existe em “${target.name}”. Remova ou renomeie a versão existente antes de mover.` : "Não foi possível mover o material.");
      renderKnowledgeBase();
      return;
    }
    app.knowledgeBase = result.base;
    await persistKnowledgeBase();
    renderKnowledgeBase();
    if (app.session) await scanQuestionsWithBase({ silent: true });
    setBaseProgress("success", `“${document.name}” foi movido para “${target.name}”.`);
    log(`Material movido: ${document.name} → ${target.name}.`, "success", { code: "BASE_MATERIAL_MOVIDO" });
  }

  function editMaterialMetadata(id) {
    if (app.knowledgeBusy || app.running) return;
    const document = app.knowledgeBase.documents.find((entry) => entry.id === id);
    if (!document) return;
    app.editingMaterialId = id;
    ui.materialEditor.hidden = false;
    ui.materialEditorTitle.textContent = `Classificar: ${document.name}`;
    ui.editMaterialRole.value = document.role || Curator.roles.REFERENCE;
    ui.editMaterialSubject.value = document.subject || "";
    ui.editMaterialUa.value = document.assignedUa || "";
    ui.editMaterialCollection.innerHTML = Knowledge.listCollections(app.knowledgeBase).map((collection) => `<option value="${escapeHtml(collection.id)}"${collection.id === document.collectionId ? " selected" : ""}>${escapeHtml(collection.name)}</option>`).join("");
    ui.materialEditor.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function cancelMaterialEditor() {
    app.editingMaterialId = "";
    ui.materialEditor.hidden = true;
  }

  async function saveMaterialMetadata() {
    if (!app.editingMaterialId || app.knowledgeBusy || app.running) return;
    const document = app.knowledgeBase.documents.find((entry) => entry.id === app.editingMaterialId);
    if (!document) return cancelMaterialEditor();
    const role = ui.editMaterialRole.value;
    const ua = ui.editMaterialUa.value.trim();
    const parsedUas = Knowledge.parseUaScope(ua);
    if (ua && parsedUas.length !== 1) {
      setBaseProgress("warning", "UA inválida. Informe somente um número entre 1 e 30 ou deixe vazio.");
      return;
    }
    const target = Knowledge.listCollections(app.knowledgeBase).find((collection) => collection.id === ui.editMaterialCollection.value);
    const subject = target?.subject || ui.editMaterialSubject.value.trim();
    if (!subject) {
      setBaseProgress("warning", "Informe a disciplina do material ou mova-o para uma coleção identificada.");
      return;
    }
    const result = Knowledge.updateDocumentMetadata(app.knowledgeBase, document.id, { collectionId: target?.id, subject, assignedUa: parsedUas[0] || null, role });
    if (!result.updated) {
      setBaseProgress("warning", result.collision ? `Já existe um arquivo equivalente em “${target?.name || "essa coleção"}”.` : "A classificação não pôde ser atualizada.");
      return;
    }
    app.knowledgeBase = result.base;
    await persistKnowledgeBase();
    cancelMaterialEditor();
    renderKnowledgeBase();
    if (app.session) await scanQuestionsWithBase({ silent: false });
    setBaseProgress("success", `Classificação de ${document.name} atualizada.`);
    log(`Arquivo classificado: ${document.name} · ${Curator.roleLabels[role]} · ${subject} · ${ua ? `UA${parsedUas[0]}` : "UA pelos títulos internos"} · ${target?.name || "Acervo geral"}.`, "success", { code: "BASE_CLASSIFICADA" });
  }

  async function clearKnowledgeBase() {
    const collection = activeKnowledgeCollection();
    const documents = scopedKnowledgeBase().documents;
    if (app.knowledgeBusy || !documents.length || !window.confirm(`Esvaziar a coleção “${collection.name}”? Seus ${documents.length} material(is) serão removidos do acervo local; outras coleções e avaliações já salvas permanecerão intactas.`)) return;
    cancelMaterialEditor();
    app.knowledgeBase = Knowledge.clearCollection(app.knowledgeBase, collection.id).base;
    await persistKnowledgeBase();
    renderKnowledgeBase();
    if (app.session) await scanQuestionsWithBase({ silent: true });
    setBaseProgress("success", `Coleção “${collection.name}” esvaziada.`);
    log(`A coleção ${collection.name} foi esvaziada.`, "warning", { code: "COLECAO_ESVAZIADA" });
  }

  function setSiteStatus(kind, message) {
    ui.siteStatus.className = `aab-status aab-${kind}`;
    ui.siteStatus.textContent = message;
  }

  function modeStrip(kind, title, text) {
    ui.modeStrip.className = `aab-safe-strip aab-${kind}-strip`;
    ui.modeStrip.innerHTML = `<span></span><strong>${escapeHtml(title)}</strong>${text ? ` ${escapeHtml(text)}` : ""}`;
  }

  function normalizeSearch(value) {
    return String(value || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("pt-BR");
  }

  function occurrenceCode(message, explicitCode) {
    if (explicitCode) return String(explicitCode);
    const match = String(message || "").match(/\[([A-Z0-9_-]+)\]/);
    return match ? match[1] : "";
  }

  function renderOccurrenceCenter() {
    const all = app.occurrences || [];
    const counts = all.reduce((result, entry) => {
      const kind = ["error", "warning", "success"].includes(entry.kind) ? entry.kind : "info";
      result[kind] += 1;
      return result;
    }, { error: 0, warning: 0, success: 0, info: 0 });
    ui.historySummary.innerHTML = `<span class="aab-history-error"><b>${counts.error}</b> erros</span><span class="aab-history-warning"><b>${counts.warning}</b> alertas</span><span class="aab-history-success"><b>${counts.success}</b> conclusões</span><span><b>${all.length}</b> total</span>`;
    const query = normalizeSearch(app.occurrenceSearch);
    const filtered = all.filter((entry) => {
      const kindMatches = app.occurrenceFilter === "all" || entry.kind === app.occurrenceFilter;
      const haystack = normalizeSearch(`${entry.code || ""} ${entry.message || ""} ${entry.questionNumber || ""} ${entry.fileName || ""}`);
      return kindMatches && (!query || haystack.includes(query));
    }).slice(-200).reverse();
    ui.log.innerHTML = filtered.length ? filtered.map((entry) => `
      <li class="aab-log-${escapeHtml(entry.kind || "info")}">
        <div><time>${escapeHtml(formatClock(entry.at))}</time>${entry.code ? `<code>${escapeHtml(entry.code)}</code>` : ""}</div>
        <span>${escapeHtml(entry.message)}</span>
      </li>`).join("") : '<li class="aab-log-empty">Nenhuma ocorrência corresponde ao filtro.</li>';
    ui.logSection.hidden = false;
  }

  function persistOccurrenceStore() {
    const snapshot = app.occurrences.slice(-OCCURRENCE_LIMIT);
    const operation = occurrenceWriteQueue.then(
      () => storageSet({ [OCCURRENCE_KEY]: snapshot }),
      () => storageSet({ [OCCURRENCE_KEY]: snapshot })
    );
    occurrenceWriteQueue = operation.catch((error) => console.warn("SmartFox: histórico local não persistido.", error));
    return operation;
  }

  function recordOccurrence(message, kind, details) {
    const info = details || {};
    const entry = {
      at: info.at || new Date().toISOString(),
      kind: ["error", "warning", "success"].includes(kind) ? kind : "info",
      code: occurrenceCode(message, info.code),
      message: String(message || "Ocorrência sem descrição.").replace(/\s+/g, " ").trim().slice(0, 1200),
      source: info.source || "extension",
      questionNumber: info.questionNumber ?? Engine.currentItem(app.session)?.number ?? null,
      runId: app.session?.runId || "",
      fileName: app.session?.fileName || ""
    };
    const previous = app.occurrences[app.occurrences.length - 1];
    const duplicate = previous && previous.kind === entry.kind && previous.code === entry.code && previous.message === entry.message
      && Date.now() - new Date(previous.at).getTime() < 2000;
    if (!duplicate) app.occurrences.push(entry);
    if (app.occurrences.length > OCCURRENCE_LIMIT) app.occurrences.splice(0, app.occurrences.length - OCCURRENCE_LIMIT);
    persistOccurrenceStore();
    renderOccurrenceCenter();
    return entry;
  }

  async function loadOccurrenceStore() {
    const stored = await storageGet([OCCURRENCE_KEY, LEGACY_OCCURRENCE_KEY]);
    const entries = Array.isArray(stored?.[OCCURRENCE_KEY]) ? stored[OCCURRENCE_KEY] : stored?.[LEGACY_OCCURRENCE_KEY];
    app.occurrences = Array.isArray(entries) ? entries.slice(-OCCURRENCE_LIMIT) : [];
    if (!stored?.[OCCURRENCE_KEY] && app.occurrences.length) await storageSet({ [OCCURRENCE_KEY]: app.occurrences });
    app.knownSiteErrors = new Set(app.occurrences.filter((entry) => entry.source === "avalia").map((entry) => `${entry.at}:${entry.code}:${entry.message}`));
    renderOccurrenceCenter();
  }

  function addEvent(message, kind, details) {
    if (!app.session) return;
    app.session.events = Array.isArray(app.session.events) ? app.session.events : [];
    app.session.events.push({ at: details?.at || new Date().toISOString(), message, kind: kind || "info", code: occurrenceCode(message, details?.code) });
    if (app.session.events.length > 400) app.session.events.splice(0, app.session.events.length - 400);
  }

  function log(message, kind, record, details) {
    const suppliedDetails = record && typeof record === "object" && details == null ? record : details;
    const shouldRecord = record !== false;
    const info = { ...(suppliedDetails || {}), at: suppliedDetails?.at || new Date().toISOString() };
    if (shouldRecord) addEvent(message, kind, info);
    recordOccurrence(message, kind, info);
  }

  function formatClock(iso) {
    if (!iso) return "—";
    return new Date(iso).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  }

  function elapsedSeconds() {
    if (!app.session?.startedAt) return 0;
    const end = app.session.endedAt ? new Date(app.session.endedAt).getTime() : Date.now();
    return Math.max(0, Math.round((end - new Date(app.session.startedAt).getTime()) / 1000));
  }

  function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const rest = seconds % 60;
    return `${hours ? `${String(hours).padStart(2, "0")}:` : ""}${String(minutes).padStart(2, "0")}:${String(rest).padStart(2, "0")}`;
  }

  function errorCode(error) {
    const match = String(error?.message || error || "").match(/^\[([^\]]+)\]/);
    return match ? match[1] : "EXECUTION_ERROR";
  }

  function classifyExecutionError(error, item) {
    const raw = String(error?.message || error || "Falha não identificada.");
    let code = errorCode(error);
    if (code === "EXECUTION_ERROR" && /após 3 tentativas controladas/i.test(raw)) code = "ETAPAS_NAO_CONCLUIDAS";
    if (code === "EXECUTION_ERROR" && /protetor contra looping/i.test(raw)) code = "LOOP_PROTEGIDO";
    const catalog = {
      ARMAZENAMENTO_LEITURA: {
        title: "Banco local não pôde ser lido",
        cause: "O perfil do Chrome recusou ou interrompeu a leitura dos dados persistentes da extensão.",
        action: "Confira o espaço e as políticas do perfil. Não desinstale a extensão antes de recuperar ou exportar os dados disponíveis.",
        definite: true, autoSkippable: false, retryable: true
      },
      ARMAZENAMENTO_GRAVACAO: {
        title: "Banco local não pôde ser atualizado",
        cause: "O Chrome não confirmou a gravação da sessão, coleção ou material.",
        action: "Pause o lote, libere espaço no perfil e tente novamente. Não prossiga sem um checkpoint persistido.",
        definite: true, autoSkippable: false, retryable: true
      },
      ARMAZENAMENTO_REMOCAO: {
        title: "Alteração do banco local não confirmada",
        cause: "O Chrome não confirmou a remoção solicitada.",
        action: "Reabra o painel e confira o item antes de repetir a operação.",
        definite: true, autoSkippable: false, retryable: true
      },
      VINCULO_INSTITUCIONAL_INCOMPLETO: {
        title: "Vínculo institucional incompleto",
        cause: "O AvaliA exibiu o nome da IES, mas deixou vazio o identificador institucional exigido no salvamento.",
        action: "Repita uma vez a seleção IES no Passo 1. Se persistir, solicite ao suporte o vínculo Elaborador + IES para este professor.",
        definite: true, autoSkippable: false, retryable: false
      },
      VINCULO_FONTE_INCOMPLETO: {
        title: "Vínculo da fonte incompleto",
        cause: "A fonte aparece ativa na tela, mas o campo interno Questao_IdFonte não foi preenchido pelo AvaliA.",
        action: "Selecione IES novamente no Passo 1. Se o teste continuar bloqueado, o perfil precisa de correção no AvaliA.",
        definite: true, autoSkippable: false, retryable: false
      },
      EDITORES_NAO_INICIALIZADOS: {
        title: "Editores de texto ainda não estão prontos",
        cause: "O AvaliA não terminou de criar todos os editores usados por enunciado, alternativas e feedback.",
        action: "Use Aplicar recuperação segura; a extensão só recarregará o Passo 4 quando ele estiver vazio.",
        definite: true, autoSkippable: false, retryable: true
      },
      FONTE_AUSENTE: {
        title: "Fonte IES não confirmada",
        cause: "O Passo 1 ainda não registrou a fonte da questão.",
        action: "Volte ao Passo 1, selecione IES e execute o teste de perfil novamente.",
        definite: true, autoSkippable: false, retryable: false
      },
      INSTITUICAO_AUSENTE: {
        title: "Instituição não confirmada",
        cause: "O Passo 1 ainda não registrou uma instituição.",
        action: "Confirme a IES e execute o teste de perfil novamente.",
        definite: true, autoSkippable: false, retryable: false
      },
      AVALIA_VALIDACAO: {
        title: "Validação recusada pelo AvaliA",
        cause: "O servidor ou o formulário considerou um campo obrigatório inválido.",
        action: "Leia a mensagem original, revise o campo indicado e teste novamente sem repetir um envio incerto.",
        definite: true, autoSkippable: false, retryable: true
      },
      AVALIA_CONFLITO: {
        title: "Conflito de estado no AvaliA",
        cause: "O servidor recusou a ação porque a tela e o registro não estavam no mesmo estado.",
        action: "Atualize o teste do perfil e retome somente do último marco confirmado.",
        ambiguous: true, autoSkippable: false, retryable: false
      },
      AVALIA_JAVASCRIPT: {
        title: "Erro de script do próprio AvaliA",
        cause: "Um componente da página falhou durante a execução.",
        action: "Baixe o diagnóstico, atualize a aba em uma etapa segura e use Retomar do último marco.",
        ambiguous: false, autoSkippable: false, retryable: true
      },
      AVALIA_PROMISE: {
        title: "Operação interna do AvaliA falhou",
        cause: "Uma operação assíncrona da página terminou com erro.",
        action: "Execute o teste do perfil; se a tela estiver íntegra, use a recuperação segura.",
        ambiguous: false, autoSkippable: false, retryable: true
      },
      AVALIA_HTTP: {
        title: "Resposta HTTP inesperada do AvaliA",
        cause: "O servidor respondeu com um estado não previsto pelo fluxo atual.",
        action: "Exporte o diagnóstico e confira a tela antes de retomar.",
        ambiguous: true, autoSkippable: false, retryable: false
      },
      AVALIA_REGRA_DE_ALTERNATIVAS: {
        title: "Regra de alternativas incompatível",
        cause: "O próprio AvaliA informou uma quantidade diferente de A–D.",
        action: "Use uma avaliação/perfil que aceite quatro alternativas; a extensão não criará conteúdo artificial.",
        definite: true, autoSkippable: false, retryable: false
      },
      AVALIA_SALVAMENTO_SEM_CONFIRMACAO: {
        title: "Salvamento sem confirmação do AvaliA",
        cause: "Após o clique, o formulário não devolveu um ID de registro.",
        action: "Confira a lista antes de qualquer nova tentativa; o clique não será repetido automaticamente.",
        ambiguous: true, autoSkippable: false, retryable: false
      },
      AVALIA_ENVIO_SEM_CONFIRMACAO: {
        title: "Envio oficial sem confirmação do AvaliA",
        cause: "A página não mostrou prova inequívoca de conclusão.",
        action: "Localize o ID na lista e use a confirmação manual; não repita o envio.",
        ambiguous: true, autoSkippable: false, retryable: false
      },
      AVALIA_RESPOSTA_INDETERMINADA: {
        title: "Resposta do AvaliA não reconhecida",
        cause: "O servidor respondeu sem um resultado que pudesse provar sucesso ou recusa.",
        action: "Exporte o diagnóstico e confira o registro na lista antes de continuar.",
        ambiguous: true, autoSkippable: false, retryable: false
      },
      AVALIA_RECUSA_ENVIO: {
        title: "Envio oficial recusado pelo AvaliA",
        cause: "A resposta do servidor não indicou sucesso.",
        action: "Leia a mensagem original, confira o rascunho e corrija a exigência indicada antes de decidir como continuar.",
        definite: true, autoSkippable: false, retryable: false
      },
      PERFIL_EXIGE_CINCO: {
        title: "Este perfil do AvaliA exige cinco afirmativas",
        cause: "A regra recebida do próprio AvaliA é incompatível com o arquivo A–D.",
        action: "A extensão reaplicará uma vez o tipo e A–D. Se a recusa persistir, preservará as quatro alternativas e seguirá para a próxima questão.",
        definite: true, autoSkippable: true, retryable: true
      },
      VALIDACAO_AVALIA: {
        title: "O AvaliA recusou o salvamento",
        cause: "Uma validação objetiva da página impediu a criação do registro.",
        action: "A extensão fará uma resincronização completa uma vez. Se a validação persistir, esta questão poderá ser isolada.",
        definite: true, autoSkippable: true, retryable: true
      },
      OPCAO_NAO_DISPONIVEL: {
        title: "Tipo ou opção indisponível neste perfil",
        cause: "O DOCX indicou um valor que a lista desta conta não oferece.",
        action: "Revise o tipo detectado ou deixe esta questão ser isolada; as demais continuarão.",
        definite: true, autoSkippable: true, retryable: false
      },
      DIVERGENCIA_DE_CAMPO: {
        title: "A conferência encontrou conteúdo diferente",
        cause: "Um ou mais campos não ficaram iguais ao trecho revisado do Word.",
        action: "A extensão tentou sincronizar novamente. Se persistir, esta questão pode ser isolada sem bloquear o restante.",
        definite: true, autoSkippable: true, retryable: true
      },
      ETAPAS_NAO_CONCLUIDAS: {
        title: "Etapas obrigatórias não avançaram",
        cause: "O AvaliA não confirmou a mudança de etapa dentro do limite controlado.",
        action: "A extensão fará até três retomadas. Com um rascunho confirmado, poderá isolá-lo e continuar o lote.",
        definite: true, autoSkippable: Boolean(item?.draftId), retryable: true
      },
      SALVAMENTO_INDETERMINADO: {
        title: "Resultado do salvamento não confirmado",
        cause: "Houve clique de salvar, mas a página não devolveu um identificador.",
        action: "Confira a tela ou a lista do AvaliA. O clique não será repetido automaticamente.",
        ambiguous: true, autoSkippable: false, retryable: false
      },
      ENVIO_INDETERMINADO: {
        title: "Resultado do envio oficial não confirmado",
        cause: "O AvaliA não forneceu prova inequívoca de sucesso ou falha.",
        action: "Verifique a lista e confirme manualmente; repetir o envio poderia criar duplicidade.",
        ambiguous: true, autoSkippable: false, retryable: false
      },
      SEM_RESPOSTA: {
        title: "O formulário demorou além do limite",
        cause: "A página não respondeu ao comando no tempo previsto.",
        action: "A extensão tentará novamente apenas quando isso não puder repetir um salvamento ou envio.",
        ambiguous: [P.SAVING, P.SUBMITTING, P.NEEDS_VERIFICATION].includes(item?.phase),
        autoSkippable: false, retryable: ![P.SAVING, P.SUBMITTING, P.NEEDS_VERIFICATION].includes(item?.phase)
      },
      LOOP_PROTEGIDO: {
        title: "Avanço interrompido pelo protetor de looping",
        cause: "A tela permaneceu no mesmo marco após ações controladas.",
        action: "Nenhum clique adicional foi executado. Use a retomada inteligente ou isole um rascunho confirmado.",
        ambiguous: false, autoSkippable: Boolean(item?.draftId), retryable: true
      },
      AVALIA_SESSAO_EXPIRADA: {
        title: "Sessão do AvaliA expirada",
        cause: "O AvaliA respondeu com acesso expirado ou devolveu a tela de entrada no lugar dos dados esperados.",
        action: "Entre novamente, reabra Elaborador e use Retomar; o marco local foi preservado.",
        ambiguous: false, autoSkippable: false, retryable: false
      },
      AVALIA_SEM_PERMISSAO: {
        title: "Perfil sem permissão para esta ação",
        cause: "O próprio AvaliA respondeu HTTP 403 para o usuário atual.",
        action: "Confirme que a conta de professor possui acesso à disciplina e à elaboração oficial.",
        ambiguous: false, autoSkippable: false, retryable: false
      },
      AVALIA_SERVIDOR: {
        title: "Falha temporária do servidor AvaliA",
        cause: "O próprio AvaliA retornou erro HTTP 5xx.",
        action: "A extensão fará recuperação segura e retomará do último marco quando não houver risco de duplicar.",
        ambiguous: [P.SAVING, P.SUBMITTING].includes(item?.phase), autoSkippable: false, retryable: ![P.SAVING, P.SUBMITTING].includes(item?.phase)
      },
      AVALIA_REDE: {
        title: "Falha de comunicação com o AvaliA",
        cause: "A requisição do site não recebeu resposta de rede.",
        action: "A extensão preservará o marco e tentará recuperação apenas em etapa segura.",
        ambiguous: [P.SAVING, P.SUBMITTING].includes(item?.phase), autoSkippable: false, retryable: ![P.SAVING, P.SUBMITTING].includes(item?.phase)
      },
      AVALIA_OCUPADO: {
        title: "AvaliA permaneceu ocupado",
        cause: "O indicador interno de processamento não ficou ocioso dentro do limite.",
        action: "Aguarde a requisição terminar e use Retomar; nenhuma nova ação foi sobreposta.",
        ambiguous: false, autoSkippable: Boolean(item?.draftId), retryable: true
      },
      AVALIA_ETAPA_TRAVADA: {
        title: "Assistente do AvaliA travou em uma etapa",
        cause: "A tela não confirmou a mudança após três ações controladas.",
        action: "A extensão fechará janelas residuais, aguardará o site ficar ocioso e retomará do marco confirmado.",
        ambiguous: false, autoSkippable: Boolean(item?.draftId), retryable: true
      },
      RECUPERACAO_BLOQUEADA: {
        title: "Recuperação automática bloqueada por segurança",
        cause: "A etapa atual pode ter realizado salvamento ou envio.",
        action: "Confira o ID no AvaliA antes de autorizar qualquer continuação.",
        ambiguous: true, autoSkippable: false, retryable: false
      },
      RASCUNHO_DIVERGENTE: {
        title: "A tela mostra outro registro",
        cause: "O ID aberto no AvaliA não corresponde ao marco da sessão.",
        action: "Abra o registro indicado no relatório ou uma tela compatível; nada foi forçado.",
        ambiguous: false, autoSkippable: false, retryable: false
      },
      TAG_DISCURSIVA_DIVERGENTE: {
        title: "Tag discursiva diferente da alocação",
        cause: "A linha adicionada no Passo 3 não corresponde à primeira ou segunda discursiva reconhecida no arquivo.",
        action: "Não reenvie as questões já concluídas. Prepare uma remessa separada para cada tag, confira a disciplina por código e use Troca assistida de tags antes de Adicionar.",
        definite: true, ambiguous: false, autoSkippable: false, retryable: false
      },
      TAG_DISCURSIVA_NAO_CONFIRMADA: {
        title: "Catálogo de tags discursivas não confirmado",
        cause: "A tag indicada não foi encontrada de forma única no catálogo de Graduação.",
        action: "Reabra o Passo 3, carregue e confira as tags atuais antes de iniciar uma nova remessa.",
        definite: true, ambiguous: false, autoSkippable: false, retryable: false
      },
      EXECUTION_ERROR: {
        title: "Execução pausada",
        cause: "O AvaliA retornou uma condição ainda não classificada.",
        action: "Veja o detalhe técnico e use a retomada inteligente. Nenhum envio incerto será repetido.",
        ambiguous: false, autoSkippable: false, retryable: true
      }
    };
    const selected = catalog[code] || catalog.EXECUTION_ERROR;
    return {
      code,
      ...selected,
      message: raw.replace(/^\[[^\]]+\]\s*/, ""),
      questionNumber: item?.number ?? null,
      draftId: item?.draftId || "",
      phase: item?.phase || "",
      attempts: item ? { ...item.attempts } : {}
    };
  }

  function canSkipItem(item, problem) {
    if (!item || !problem || problem.ambiguous) return false;
    if ([P.SUBMITTING, P.NEEDS_VERIFICATION, P.SUBMITTED, P.COMPLETED].includes(item.phase)) return false;
    return Boolean(problem.autoSkippable || item.draftId);
  }

  function updateClock() {
    ui.elapsed.textContent = formatDuration(elapsedSeconds());
  }

  function startClock() {
    window.clearInterval(app.clockTimer);
    updateClock();
    if (app.session?.startedAt && !app.session?.endedAt) app.clockTimer = window.setInterval(updateClock, 1000);
  }

  async function saveSession() {
    if (!app.session) return;
    app.session.updatedAt = new Date().toISOString();
    const snapshot = app.session;
    const operation = sessionWriteQueue.then(
      () => storageSet({ [STORAGE_KEY]: snapshot }),
      () => storageSet({ [STORAGE_KEY]: snapshot })
    );
    sessionWriteQueue = operation.catch(() => {});
    await operation;
  }

  function executionQuestion() {
    return app.session?.parsed?.questions?.[app.session.currentIndex] || null;
  }

  function reviewQuestion() {
    return app.session?.parsed?.questions?.[app.reviewIndex] || null;
  }

  function reviewItem(index) {
    return app.session?.items?.[Number.isInteger(index) ? index : app.reviewIndex] || null;
  }

  function allocationScope(disciplines) {
    return JSON.stringify(Array.from(new Set((disciplines || []).map(value => String(value).trim().replace(/\s+/g, " ").toLowerCase()).filter(Boolean))).sort());
  }

  function allocationRequiresApproval(question, index) {
    const audit = question?.allocationAudit;
    if (!audit || audit.status === "unknown" || audit.status === "match") return false;
    return !reviewItem(index)?.allocationAuthorizedAt;
  }

  async function auditAllocations(disciplines, options) {
    if (!app.session?.parsed?.questions?.length) return { reviewed: 0, issues: 0 };
    const rows = (Array.isArray(disciplines) ? disciplines : []).filter(Boolean);
    app.lastDisciplines = rows;
    let issues = 0;
    app.session.parsed.questions.forEach((question, index) => {
      const previousDiscipline = question.allocationAudit?.selectedDiscipline || "";
      question.allocationAudit = Parser.assessAllocation(question, rows, app.session.parsed.subjectHint || question.subjectHint);
      if (["review", "inconsistent"].includes(question.allocationAudit.status)) issues += 1;
      const item = app.session.items[index];
      if (item?.phase === P.PENDING && ((previousDiscipline && previousDiscipline !== question.allocationAudit.selectedDiscipline) || (item.allocationAuthorizationScope && item.allocationAuthorizationScope !== allocationScope(rows)))) {
        item.allocationAuthorizedAt = null;
        item.allocationAuthorizationNote = "";
        item.allocationAuthorizationScope = "";
      }
    });
    app.session.allocationAuditAt = new Date().toISOString();
    app.session.disciplineSnapshot = rows;
    await saveSession();
    if (options?.render !== false) renderSession();
    if (options?.log) log(`Conferência de matéria: ${app.session.parsed.questions.length} questão(ões) comparadas com ${rows.length} disciplina(s); ${issues} pedem decisão do professor.`, issues ? "warning" : "success");
    return { reviewed: app.session.parsed.questions.length, issues };
  }

  function questionStatus(question, index) {
    const item = reviewItem(index);
    if (item && item.phase === P.COMPLETED) return { key: "completed", label: "Concluída", kind: "success" };
    if (item && item.phase === P.SKIPPED) return { key: "skipped", label: "Ignorada; lote continuou", kind: "warning" };
    if (item && item.phase !== P.PENDING) return { key: "processing", label: Engine.phaseLabel(item.phase), kind: "running" };
    if (!question.executable) return { key: "blocked", label: "Corrigir campos obrigatórios", kind: "danger" };
    if (knowledgeRequiresDecision(question, index)) return { key: "review", label: "Conferir com os materiais", kind: "warning" };
    if (question.needsReview && !item?.manualAuthorizedAt) return { key: "review", label: "Aguardando aprovação da qualidade", kind: "warning" };
    if (allocationRequiresApproval(question, index)) return { key: "review", label: "Aguardando aprovação da matéria", kind: "warning" };
    if (item?.manualAuthorizedAt || item?.allocationAuthorizedAt) return { key: "authorized", label: "Aprovada pelo professor", kind: "authorized" };
    return { key: "ready", label: "Aprovada automaticamente", kind: "success" };
  }

  function questionCleared(question, index) {
    if (!question?.executable) return false;
    const item = reviewItem(index);
    const qualityCleared = !question.needsReview || Boolean(item?.manualAuthorizedAt);
    const allocationCleared = !allocationRequiresApproval(question, index);
    const knowledgeCleared = !knowledgeRequiresDecision(question, index);
    return qualityCleared && allocationCleared && knowledgeCleared;
  }

  function filterMatches(question, index) {
    const status = questionStatus(question, index).key;
    if (app.reviewFilter === "all") return true;
    if (app.reviewFilter === "action") return status === "blocked" || status === "review";
    return status === app.reviewFilter;
  }

  function firstMatchingIndex(start) {
    const questions = app.session?.parsed?.questions || [];
    if (!questions.length) return 0;
    for (let offset = 0; offset < questions.length; offset += 1) {
      const index = (start + offset + questions.length) % questions.length;
      if (filterMatches(questions[index], index)) return index;
    }
    return Math.max(0, Math.min(start, questions.length - 1));
  }

  function startEligibility() {
    const session = app.session;
    if (!session?.parsed?.questions?.length) return { ready: false, setup: [], hard: [], review: [], messages: ["Selecione e analise um arquivo DOCX."] };
    const setup = [];
    const athusReport=assessmentAthusReport(true);
    if(athusReport && !athusReport.ok) setup.push({code:"ATHUS_PENDENTE",reason:athusReport.issues.slice(0,4).map(i=>i.message).join(" ")});
    if (app.storageHealth.status !== "healthy") setup.push({ code: "ARMAZENAMENTO_NAO_TESTADO", reason: "Execute Testar tudo para confirmar o banco local e a retomada segura neste perfil." });
    const officialMode = (session.confirmedAt ? session.outputMode : selectedMode()) === "official";
    if (officialMode) {
      const config = session.tagConfig || {};
      if (!config.catalogSummary?.signature || !Array.isArray(config.catalogSnapshot) || !config.catalogSnapshot.length) {
        setup.push({ code: "TAGS_NAO_MAPEADAS", reason: "Mapeie o catálogo atual de tags antes de iniciar." });
      } else if (!config.target) {
        setup.push({ code: "TAG_NAO_ESCOLHIDA", reason: "Escolha qual tag de Graduação deve ser conferida." });
      } else {
        const targetCheck = Approval.verifyGraduationTarget(config.catalogSnapshot, config.target);
        if (!targetCheck.valid) setup.push({ code: targetCheck.code, reason: targetCheck.message });
        if (!config.verifiedInStep3) setup.push({ code: "TAG_NAO_CONFIRMADA_PASSO_3", reason: `A tag “${config.target.label}” não foi localizada nas escolhas manuais do Passo 3.` });
      }
    }
    const hard = [];
    const review = [];
    session.parsed.questions.forEach((question, index) => {
      if (index < session.currentIndex) return;
      if (!question.executable) hard.push({ index, number: question.number, reasons: question.hardErrors });
      else {
        const reasons = [];
        if (knowledgeRequiresDecision(question, index)) reasons.push(question.knowledgeAudit?.warnings?.[0] || "O conteúdo precisa de decisão após a consulta aos materiais.");
        if (question.needsReview && !session.items[index].manualAuthorizedAt) reasons.push(...question.reviewBlocks, ...question.warnings);
        if (allocationRequiresApproval(question, index)) reasons.push(question.allocationAudit.reason || "A matéria precisa ser conferida.");
        if (reasons.length) review.push({ index, number: question.number, reasons });
      }
    });
    const diagnostic = currentFileDiagnostics();
    const fileRuleReviews = pendingFileRuleReviews(diagnostic);
    const fileRulesAuthorized = fileRuleAuthorizationValid(diagnostic);
    if (fileRuleReviews.length && !fileRulesAuthorized) review.unshift({
      index: null,
      number: "lote",
      reasons: fileRuleReviews.map((issue) => `${issue.title}: ${issue.message}`),
      fileLevel: true
    });
    const messages = [];
    if (setup.length) messages.push(...setup.map((item) => item.reason));
    if (hard.length) messages.push(`${hard.length} questão(ões) ainda têm campo obrigatório ausente ou inválido.`);
    if (review.length) messages.push(`${review.length} pendência(s) de revisão precisam ser lidas e autorizadas.`);
    return { ready: !setup.length && !hard.length && !review.length, setup, hard, review, fileRuleReviews, fileRulesAuthorized, messages };
  }

  function auditBadge(check) {
    const status = typeof check.pass === "boolean" ? (check.pass ? "pass" : "blocking") : check.status;
    const label = status === "pass" ? "OK" : status === "blocking" ? "ATENÇÃO" : "REVISAR";
    return `<li class="aab-audit-${status}"><span>${label}</span><div><strong>${escapeHtml(check.label)}</strong>${check.message ? `<small>${escapeHtml(check.message)}</small>` : ""}</div></li>`;
  }

  function renderQuestionSelect() {
    const questions = app.session?.parsed?.questions || [];
    ui.questionSelect.innerHTML = questions.map((question, index) => {
      const status = questionStatus(question, index);
      const hiddenMarker = filterMatches(question, index) ? "" : " · fora do filtro";
      return `<option value="${index}">${question.number}. ${escapeHtml(status.label)} · ${Math.round(question.confidence * 100)}%${hiddenMarker}</option>`;
    }).join("");
    ui.questionSelect.value = String(app.reviewIndex);
  }

  function renderKnowledgeAudit(question, item, editable) {
    const audit = question.knowledgeAudit || Knowledge.analyzeQuestion(question, scopedKnowledgeBase());
    question.knowledgeAudit = audit;
    const discursive = question.questionFormat === "discursive";
    const labels = {
      no_base: ["Sem base para conferir", "neutral"],
      supported: [discursive ? "Padrão de resposta sustentado pela base" : "Gabarito sustentado pela base", "success"],
      mismatch: [discursive ? "Padrão de resposta diferente do material" : "Gabarito diferente do material", "danger"],
      review: ["Evidência pede conferência", "warning"],
      insufficient: ["Material insuficiente", "warning"]
    };
    const [label, kind] = labels[audit.status] || labels.review;
    ui.knowledgeCard.className = `aab-knowledge-card aab-knowledge-${kind}`;
    ui.knowledgeSummary.textContent = item?.knowledgeDecision === "corrected" ? "Correção fundamentada aplicada e registrada." : item?.knowledgeDecision === "kept" ? "Conteúdo mantido após sua conferência." : label;
    ui.knowledgeConfidence.textContent = audit.status === "no_base" ? "—" : `${Math.round(Number(audit.confidence || 0) * 100)}%`;
    const current = audit.currentLetter || question.correctLetter || "—";
    const suggested = audit.suggestedLetter || "não conclusivo";
    ui.knowledgeAnswer.innerHTML = audit.status === "no_base"
      ? `<span>Adicione materiais na aba <b>Base</b> para validar ${discursive ? "a resposta esperada" : "o gabarito"}, o assunto e a justificativa.</span>`
      : discursive
        ? `<span><b>Cobertura da resposta esperada:</b> ${Number(audit.responseCoverage || 0)}%</span><span><b>Aderência ao assunto:</b> ${Number(audit.alignment?.score || 0)}%</span><span><b>Decisão:</b> conferência docente obrigatória</span>`
        : `<span><b>Gabarito do DOCX:</b> ${escapeHtml(current)}</span><span><b>Sugestão da base:</b> ${escapeHtml(suggested)}</span><span><b>Aderência ao assunto:</b> ${Number(audit.alignment?.score || 0)}%</span>`;
    ui.knowledgeEvidence.innerHTML = audit.evidence?.length
      ? `<details ${["mismatch", "review"].includes(audit.status) ? "open" : ""}><summary>Ver evidências (${audit.evidence.length})</summary>${audit.evidence.map((entry) => `<article><strong>${escapeHtml(entry.documentName)}</strong><small>${escapeHtml(entry.excerpt)}</small></article>`).join("")}${audit.warnings?.length ? `<ul>${audit.warnings.map((warning) => `<li>${escapeHtml(warning)}</li>`).join("")}</ul>` : ""}</details>`
      : (audit.warnings?.length ? `<small>${escapeHtml(audit.warnings.join(" "))}</small>` : "");
    const canApply = !discursive && editable && audit.suggestedIndex != null && audit.agreement === false && Number(audit.confidence || 0) >= 0.65 && Boolean(audit.feedbackSuggestion);
    ui.applyKnowledge.hidden = !canApply;
    ui.applyKnowledge.disabled = !canApply;
    ui.keepKnowledge.hidden = audit.status === "no_base" || audit.status === "supported" || Boolean(item?.knowledgeDecision);
    ui.keepKnowledge.disabled = !editable;
    ui.revokeKnowledge.hidden = !["kept", "corrected"].includes(item?.knowledgeDecision);
    ui.revokeKnowledge.disabled = !editable;
  }

  function renderQuestion(index) {
    const questions = app.session?.parsed?.questions || [];
    if (!questions.length) return;
    app.reviewIndex = Math.max(0, Math.min(Number(index) || 0, questions.length - 1));
    const question = questions[app.reviewIndex];
    const discursive = question.questionFormat === "discursive";
    const item = reviewItem(app.reviewIndex);
    const status = questionStatus(question, app.reviewIndex);
    renderQuestionSelect();
    ui.manualConfirm.checked = false;
    ui.questionStatus.className = `aab-question-status aab-question-${status.kind}`;
    ui.questionStatus.innerHTML = `<strong>${escapeHtml(status.label)}</strong><span>Questão ${escapeHtml(question.number)} de ${questions.length}</span>`;

    const alternatives = question.alternatives.map((alternative) => `
      <li class="${alternative.letter === question.correctLetter ? "aab-correct" : ""}">
        <strong>${escapeHtml(alternative.letter)})</strong><div>${alternative.html}</div>
        ${alternative.letter === question.correctLetter ? "<span>Gabarito</span>" : ""}
      </li>`).join("");
    const hard = question.hardErrors.length
      ? `<div class="aab-inline-errors"><strong>Campos que precisam ser corrigidos</strong><ul>${question.hardErrors.map((error) => `<li>${escapeHtml(error)}</li>`).join("")}</ul></div>` : "";
    const review = question.reviewBlocks.length
      ? `<div class="aab-inline-warnings"><strong>Alertas que você pode avaliar e autorizar</strong><ul>${question.reviewBlocks.map((warning) => `<li>${escapeHtml(warning)}</li>`).join("")}</ul></div>` : "";
    const warnings = question.warnings.length
      ? `<div class="aab-inline-advisories"><strong>Observações</strong><ul>${question.warnings.map((warning) => `<li>${escapeHtml(warning)}</li>`).join("")}</ul></div>` : "";
    const candidates = (question.typeCandidates || []).map((candidate, candidateIndex) => `
      <li class="${candidateIndex === 0 ? "aab-candidate-best" : ""}">
        <span>${escapeHtml(candidate.label)}</span><b>${Math.round(candidate.score * 100)}%</b>
      </li>`).join("");
    const evidence = (question.typeEvidence || []).map((entry) => `<li>${escapeHtml(entry)}</li>`).join("");
    const checks = question.audit?.checks?.map(auditBadge).join("") || "";
    const premiumAudit = question.generationAudit;
    const premiumChecks = premiumAudit?.checks?.map(auditBadge).join("") || "";
    const athusQuestion = question.generatedFromKnowledgeBase ? Athus.question(question, app.session.parsed.generationRules, {requireReview:true}) : null;
    const qualityLabel = athusQuestion ? `${athusQuestion.issues.length} pendência(s) Athus` : premiumAudit ? `${premiumAudit.passed}/${premiumAudit.total} travas` : `Estrutura ${question.audit?.score || 0}%`;
    const premiumEvidence = question.generatedFromKnowledgeBase ? `<div class="aab-premium-evidence"><span><b>Objetivo do plano:</b> ${escapeHtml(question.objective || "não vinculado")}</span><span><b>Plano:</b> ${escapeHtml(question.curriculumEvidence?.planDocumentName || "não identificado")}</span><span><b>Evidência de conteúdo:</b> ${escapeHtml(question.generationEvidence?.documentName || "não identificada")}${question.generationEvidence?.line ? ` · linha ${Number(question.generationEvidence.line)}` : ""}</span><span><b>Modelo de estilo:</b> ${question.blueprintEvidence?.documents || 0} arquivo(s), sem reutilizar respostas</span></div>` : "";

    ui.preview.innerHTML = `
      <div class="aab-preview-meta"><div><strong>${escapeHtml(question.name)}</strong><small>${question.generatedFromKnowledgeBase ? "Curada de conteúdo + plano de ensino" : `Trecho ${question.sourceStart}–${question.sourceEnd} do Word`}</small></div><span>${escapeHtml(qualityLabel)}</span></div>
      <div class="aab-chip-row"><span>${escapeHtml(question.modelLabel || question.typeLabel)}</span><span>${escapeHtml(question.cognitiveLabel)}</span><span>${discursive ? "Discursiva" : "4 alternativas A–D"}</span><span>${escapeHtml(qualityLabel)}</span>${question.richIntegrity?.imageHashes?.length ? `<span>${question.richIntegrity.imageHashes.length} imagem(ns)</span>` : ""}${question.richIntegrity?.formulaHashes?.length ? `<span>${question.richIntegrity.formulaHashes.length} fórmula(s)</span>` : ""}</div>
      ${premiumEvidence}
      ${!question.generatedFromKnowledgeBase && question.fieldMap?.length ? `<details class="aab-audit"><summary>Leitura do Word: campos identificados</summary><ul>${question.fieldMap.map(f=>`<li>${escapeHtml(f.field)} · parágrafo ${Number(f.start)}</li>`).join("")}</ul><p>Confira o enunciado e as alternativas abaixo antes do envio.</p></details>` : ""}
      ${question.contextualDesign?.newScenario ? `<details class="aab-audit"><summary>Fundamentação da situação criada</summary><p>${escapeHtml(question.contextualDesign.reasoningSummary || "")}</p><ul>${(question.contextualDesign.materialRequirements || []).map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ul>${(question.generationEvidence?.supportingEvidence || []).filter((entry, index, all) => all.findIndex(other => other.passageId === entry.passageId && other.quote === entry.quote) === index).map(entry => `<p><b>${escapeHtml(entry.documentName)} · UA ${Number(entry.ua)}</b><br>${escapeHtml(entry.quote)}<br>${escapeHtml(entry.supports)}</p>`).join("")}</details>` : ""}
      <div class="aab-question-body">${question.bodyHtml}</div>
      ${discursive ? `<div class="aab-feedback aab-expected-response"><strong>Padrão de resposta discursiva</strong>${question.suggestedTagLabel ? `<p>Tag indicada: ${escapeHtml(question.suggestedTagLabel)}. Confira o código da disciplina, curso e grade no Passo 3.</p>` : ''}${question.expectedResponseHtml || "<p>Não informado.</p>"}</div>` : `<ol class="aab-alternatives">${alternatives}</ol>`}
      <div class="aab-feedback"><strong>Feedback pedagógico</strong>${question.feedbackHtml}</div>
      ${question.referencesText ? `<details class="aab-references"><summary>Referências encontradas no Word</summary><p>${escapeHtml(question.referencesText)}</p></details>` : ""}
      ${premiumAudit ? `<details class="aab-audit aab-premium-audit"><summary>Auditoria premium (${premiumAudit.passed}/${premiumAudit.total})</summary><ul>${premiumChecks}</ul></details>` : ""}
      <details class="aab-audit"><summary>Detalhes da análise estrutural</summary><div class="aab-detection-card"><div><strong>Tipo detectado</strong><span>${escapeHtml(question.typeLabel)} · ${Math.round((question.typeConfidence || 0) * 100)}%</span></div><ul class="aab-evidence">${evidence}</ul><details><summary>Outras hipóteses</summary><ul class="aab-candidates">${candidates}</ul></details></div><ul>${checks}</ul></details>
      ${athusQuestion ? `<details class="aab-audit" open><summary>Conferência Projeto Athus</summary><p>Contextualização: ${athusQuestion.contextLines} linhas · Feedback: ${athusQuestion.feedbackLines} linhas no Word padrão.</p><ul>${athusQuestion.issues.map(i=>`<li>${escapeHtml(i.message)}</li>`).join("")}</ul></details>` : ""}
      ${hard}${review}${warnings}`;

    ui.sourceRange.title = (question.fieldMap || []).map(f => `${f.field}: parágrafo ${f.start}${f.end !== f.start ? `–${f.end}` : ""}`).join("\n");
    ui.sourceRange.textContent = question.generatedFromKnowledgeBase ? `base permanente · ${Math.round((question.segmentationConfidence || 0) * 100)}%` : `parágrafos ${question.sourceStart}–${question.sourceEnd} · ${Math.round((question.segmentationConfidence || 0) * 100)}% confiança`;
    ui.sourceText.textContent = question.sourceText || "Trecho de origem não disponível.";
    ui.editName.value = question.name || "";
    ui.editTheme.value=question.theme || "";
    ui.editObjective.value=question.objective || "";
    ui.editUa.value=question.ua || "";
    ui.editObjectiveNumber.value=question.objectiveNumber || "";
    ui.editDifficulty.value=question.difficulty || "Médio";
    ui.editSkill.value=question.typeDescription || "";
    ui.editObjectiveConfirm.checked=Boolean(question.athusObjectiveConfirmed || !question.curriculumEvidence?.inferred);
    ui.editBody.value = question.bodyText || "";
    ui.editExpectedResponse.value = question.expectedResponseText || "";
    ui.editAlternatives.forEach((field, alternativeIndex) => { field.value = question.alternatives[alternativeIndex]?.plain || ""; });
    ui.editAnswer.value = question.correctLetter || "A";
    ui.editType.value = String(question.typeId || "65");
    ui.editCognitive.value = String(question.cognitiveId || "229");
    ui.editFeedback.value = question.feedbackText || "";
    ui.expectedResponseField.hidden = !discursive;
    ui.objectiveFields.forEach((field) => { field.hidden = discursive; });
    Array.from(ui.imageTarget.options).forEach((option) => {
      const objectiveTarget = /^[A-D]$/.test(option.value);
      option.hidden = discursive ? objectiveTarget : option.value === "expectedResponse";
      option.disabled = option.hidden;
    });
    if (ui.imageTarget.selectedOptions[0]?.disabled) ui.imageTarget.value = "body";
    ui.confirmationCopy.textContent = discursive
      ? "Li o enunciado, o padrão de resposta e o feedback"
      : "Li o enunciado, as quatro alternativas A–D, o gabarito e o feedback";

    const allocation = question.allocationAudit || { status: "unknown", score: 0, reason: "Aguardando a disciplina do AvaliA.", matchedTerms: [], missingTerms: [] };
    const allocationLabels = { match: "Conteúdo compatível", review: "Compatibilidade parcial", inconsistent: "Possível matéria incorreta", unknown: "Aguardando conferência" };
    ui.allocationCard.className = `aab-allocation-card aab-allocation-${allocation.status || "unknown"}`;
    ui.allocationSummary.textContent = allocationLabels[allocation.status] || allocationLabels.unknown;
    ui.allocationScore.textContent = allocation.status === "unknown" ? "—" : `${allocation.score}%`;
    ui.allocationDetails.innerHTML = `<span><b>Disciplina:</b> ${escapeHtml(allocation.selectedDiscipline || "não disponível")}</span><span><b>Matéria esperada:</b> ${escapeHtml(allocation.subjectHint || question.subjectHint || "não inferida")}</span><span><b>Conclusão:</b> ${escapeHtml(allocation.reason || "Aguardando análise.")}</span>${allocation.matchedTerms?.length ? `<span><b>Termos compatíveis:</b> ${escapeHtml(allocation.matchedTerms.join(", "))}</span>` : ""}${allocation.missingTerms?.length ? `<span><b>Termos a conferir:</b> ${escapeHtml(allocation.missingTerms.join(", "))}</span>` : ""}`;

    const editable = item?.phase === P.PENDING && !app.running;
    renderKnowledgeAudit(question, item, editable);
    [ui.editTheme, ui.editObjective, ui.editUa, ui.editObjectiveNumber, ui.editDifficulty, ui.editSkill, ui.editObjectiveConfirm, ui.editName, ui.editBody, ui.editExpectedResponse, ...ui.editAlternatives, ui.editAnswer, ui.editType, ui.editCognitive, ui.editFeedback, ui.applyEdit, ui.redetect, ui.restoreQuestion, ui.imageFile, ui.imageTarget, ui.addImage, ui.removeImage].forEach((control) => { control.disabled = !editable; });
    ui.removeImage.disabled = !editable || !(question.media || []).some((entry) => entry.source === "manual" || String(entry.relationshipId || "").startsWith("manual-"));
    ui.richSummary.textContent = `${question.richIntegrity?.imageHashes?.length || 0} imagem(ns) · ${question.richIntegrity?.formulaHashes?.length || 0} fórmula(s) · ${question.richIntegrity?.scriptCount || 0} sobrescrito(s)/subscrito(s) · ${question.richIntegrity?.specialCharacterCount || 0} caractere(s) Unicode`;
    ui.checkAllocation.disabled = app.running;
    ui.approveAllocation.hidden = allocation.status === "match" || allocation.status === "unknown" || Boolean(item?.allocationAuthorizedAt);
    ui.revokeAllocation.hidden = !item?.allocationAuthorizedAt;
    ui.approveAllocation.disabled = !editable;
    ui.revokeAllocation.disabled = !editable;
    ui.allocationGroup.open = allocationRequiresApproval(question, app.reviewIndex);
    ui.authorization.hidden = !question.needsReview || item?.phase !== P.PENDING;
    ui.authorize.hidden = Boolean(item?.manualAuthorizedAt);
    ui.revoke.hidden = !item?.manualAuthorizedAt;
    ui.authorize.disabled = !ui.manualConfirm.checked || !question.executable || !editable;
    ui.revoke.disabled = !editable;
    if (!question.executable) ui.authorization.querySelector("small").textContent = "Corrija primeiro os campos obrigatórios; depois a autorização será liberada.";
    else if (item?.manualAuthorizedAt) ui.authorization.querySelector("small").textContent = `Autorizada às ${formatClock(item.manualAuthorizedAt)}. Você pode revogar enquanto não iniciar.`;
    else ui.authorization.querySelector("small").textContent = "Confirmo que a questão faz sentido mesmo com os alertas indicados.";
  }

  function renderStats() {
    const questions = app.session?.parsed?.questions || [];
    const parsed = app.session?.parsed || {};
    const counts = { ready: 0, review: 0, blocked: 0, authorized: 0, completed: 0, skipped: 0 };
    questions.forEach((question, index) => {
      const key = questionStatus(question, index).key;
      if (Object.prototype.hasOwnProperty.call(counts, key)) counts[key] += 1;
    });
    ui.stats.hidden = false;
    const duplicateHistory = parsed.duplicateHistory?.summary || {};
    const duplicateSignals = Number(parsed.duplicateQuestionCount || 0)
      + Number(parsed.similarQuestionCount || 0)
      + Number(duplicateHistory.previouslySubmittedQuestions || 0)
      + Number(duplicateHistory.sameFileImports || 0)
      + Number(duplicateHistory.sameNameDifferentContent || 0)
      + Number(duplicateHistory.renamedSameContent || 0);
    ui.stats.innerHTML = `
      <div><strong>${questions.length}</strong><span>questões</span></div>
      <div class="aab-stat-good"><strong>${questions.length ? (parsed.validQuestionCount ?? questions.filter((question) => question.executable).length) : 0}</strong><span>válidas</span></div>
      <div class="aab-stat-auth"><strong>${questions.length ? duplicateSignals : 0}</strong><span>duplicidades (aviso)</span></div>
      <div class="aab-stat-warn"><strong>${counts.review}</strong><span>revisar</span></div>
      <div class="aab-stat-bad"><strong>${counts.blocked}</strong><span>corrigir</span></div>
      <div class="aab-stat-good"><strong>${counts.completed}</strong><span>concluídas</span></div>
      <div class="aab-stat-warn"><strong>${counts.skipped}</strong><span>isoladas</span></div>`;
  }

  function runtimeFileDiagnosticIssues() {
    const questions = app.session?.parsed?.questions || [];
    const issues = [];
    const sourceFor = (question) => ({
      start: Number(question.sourceStart || 0), end: Number(question.sourceEnd || question.sourceStart || 0),
      method: question.segmentationMethod || "não informado", confidence: Math.round(Number(question.segmentationConfidence || 0) * 100)
    });
    const add = (question, questionIndex, details) => issues.push({
      severity: details.severity || "review", category: details.category || "content", code: details.code,
      title: details.title, field: details.field || "Conteúdo", message: details.message,
      impact: details.impact, action: details.action, overridable: true,
      questionIndex, questionNumber: question.number, questionName: question.name,
      source: sourceFor(question), excerpt: String(question.sourceExcerpt || question.bodyText || "").slice(0, 320),
      evidence: details.evidence || []
    });
    const addFile = (details) => issues.push({
      severity: details.severity || "warning", category: "duplication", code: details.code,
      title: details.title, field: details.field || "Arquivo", message: details.message,
      impact: details.impact, action: details.action, overridable: true,
      questionIndex: null, questionNumber: null, questionName: "Arquivo", source: null, excerpt: "",
      evidence: details.evidence || []
    });
    questions.forEach((question, questionIndex) => {
      const knowledge = question.knowledgeAudit;
      if (knowledge?.status === "mismatch") add(question, questionIndex, {
        code: "CONTEUDO.GABARITO_DIVERGENTE", severity: "review", category: "content", field: "Gabarito",
        title: "O gabarito diverge dos materiais da coleção ativa",
        message: `O DOCX indica ${knowledge.currentLetter || question.correctLetter || "—"}; a base sugere ${knowledge.suggestedLetter || "outra resposta"} com ${Math.round(Number(knowledge.confidence || 0) * 100)}% de confiança.`,
        impact: "A resposta pode estar incorreta em relação ao material fornecido, mas a decisão final permanece com o professor.",
        action: "Abra a questão, leia as evidências e escolha Aplicar correção fundamentada ou Manter após conferência.",
        evidence: (knowledge.evidence || []).slice(0, 3).map((entry) => ({ documentName: entry.documentName, excerpt: entry.excerpt }))
      });
      else if (["review", "insufficient"].includes(knowledge?.status)) add(question, questionIndex, {
        code: knowledge.status === "insufficient" ? "CONTEUDO.BASE_INSUFICIENTE" : "CONTEUDO.EVIDENCIA_INCONCLUSIVA",
        severity: "review", category: "content", field: question.questionFormat === "discursive" ? "Conteúdo e padrão de resposta" : "Conteúdo e gabarito",
        title: knowledge.status === "insufficient" ? "Material insuficiente para validar a resposta" : "A evidência encontrada não foi conclusiva",
        message: (knowledge.warnings || ["A coleção ativa não sustentou uma conclusão segura."])[0],
        impact: `A extensão não pode afirmar automaticamente que ${question.questionFormat === "discursive" ? "a resposta esperada está correta" : "o gabarito está correto"}.`,
        action: "Revise a questão com as evidências ou acrescente material confiável à coleção antes de aprovar.",
        evidence: (knowledge.evidence || []).slice(0, 3).map((entry) => ({ documentName: entry.documentName, excerpt: entry.excerpt }))
      });
      const allocation = question.allocationAudit;
      if (["review", "inconsistent"].includes(allocation?.status)) add(question, questionIndex, {
        code: allocation.status === "inconsistent" ? "ALOCACAO.MATERIA_DIVERGENTE" : "ALOCACAO.MATERIA_PARCIAL",
        severity: "review", category: "allocation", field: "Disciplina",
        title: allocation.status === "inconsistent" ? "O conteúdo pode pertencer a outra matéria" : "Compatibilidade parcial com a matéria",
        message: `${allocation.reason || "A correspondência precisa ser conferida"} Compatibilidade calculada: ${Number(allocation.score || 0)}%.`,
        impact: "A questão pode ser alocada na disciplina errada.",
        action: "Confira a escolha manual do Passo 3 e use Conferir matéria agora ou Aprovar alocação mesmo assim."
      });
    });
    const duplicateHistory = app.session?.parsed?.duplicateHistory;
    const formatPrevious = (entry) => {
      const date = entry.recordedAt || entry.importedAt;
      const when = date ? new Date(date).toLocaleString("pt-BR") : "data não registrada";
      return `${entry.fileName || "arquivo anterior"} · ${when}${entry.avaliaId ? ` · AvaliA ${entry.avaliaId}` : ""}${entry.status ? ` · ${entry.status === "official" ? "oficial" : "rascunho"}` : ""}`;
    };
    if (duplicateHistory?.sameNameAndContentMatches?.length) addFile({
      code: "DUPLICIDADE.ARQUIVO_REIMPORTADO", title: "Este mesmo arquivo já foi importado neste perfil",
      message: `Nome e conteúdo coincidem com ${duplicateHistory.sameNameAndContentMatches.length} importação(ões) anterior(es). Última: ${formatPrevious(duplicateHistory.sameNameAndContentMatches.at(-1))}.`,
      impact: "Reiniciar o lote pode criar registros repetidos se as questões anteriores já tiverem sido salvas.",
      action: "Confira abaixo quais questões já têm envio registrado. Continue somente se a nova remessa for intencional. Este aviso não bloqueia as questões válidas."
    });
    if (duplicateHistory?.sameNameMatches?.length) addFile({
      code: "DUPLICIDADE.NOME_REUTILIZADO", title: "O nome do arquivo já foi usado com outro conteúdo",
      message: `O nome normalizado coincide com ${duplicateHistory.sameNameMatches.length} arquivo(s), mas a assinatura interna é diferente. Último: ${formatPrevious(duplicateHistory.sameNameMatches.at(-1))}.`,
      impact: "Duas versões distintas podem ser confundidas durante a conferência do lote.",
      action: "Confirme se esta é uma revisão intencional e, de preferência, acrescente versão ou data ao nome. O envio permanece disponível."
    });
    if (duplicateHistory?.renamedContentMatches?.length) addFile({
      code: "DUPLICIDADE.CONTEUDO_RENOMEADO", title: "Conteúdo idêntico encontrado com outro nome",
      message: `A assinatura interna coincide com ${duplicateHistory.renamedContentMatches.length} arquivo(s) anterior(es). Último: ${formatPrevious(duplicateHistory.renamedContentMatches.at(-1))}.`,
      impact: "Renomear o DOCX não transforma a remessa em conteúdo novo.",
      action: "Confira os envios já registrados; prossiga apenas se a repetição for desejada. O aviso não bloqueia as questões válidas."
    });
    (duplicateHistory?.questionMatches || []).forEach((duplicate) => {
      const question = questions[duplicate.questionIndex];
      if (!question || Duplicates.questionFingerprint(question) !== duplicate.questionFingerprint) return;
      const latest = duplicate.matches?.[0];
      add(question, duplicate.questionIndex, {
        code: "DUPLICIDADE.QUESTAO_JA_ENVIADA", severity: "warning", category: "duplication", field: "Questão completa",
        title: "Questão já processada anteriormente pela extensão",
        message: `${duplicate.matches.length} registro(s) anterior(es) possuem o mesmo conteúdo. Mais recente: ${formatPrevious(latest || {})}.`,
        impact: "Um novo envio pode criar uma cópia no AvaliA, mas não impede o processamento das questões válidas da remessa.",
        action: "Abra a questão, confira o ID anterior e mantenha-a somente se o reenvio for intencional.",
        evidence: (duplicate.matches || []).slice(0, 3).map((entry) => ({ documentName: entry.fileName || "Remessa anterior", excerpt: formatPrevious(entry) }))
      });
    });
    return issues;
  }

  function currentFileDiagnostics() {
    if (app.fileImportFailure) return app.fileImportFailure;
    const parsed = app.session?.parsed;
    if (!parsed?.questions?.length) return null;
    const base = parsed.fileDiagnostics || Parser.buildFileDiagnostics(parsed);
    parsed.fileDiagnostics = base;
    const candidates = [...(base.issues || []), ...runtimeFileDiagnosticIssues()];
    const seen = new Set();
    const issues = candidates.filter((issue) => {
      const signature = `${issue.code}:${issue.questionIndex == null ? "file" : issue.questionIndex}:${issue.message}`;
      if (seen.has(signature)) return false;
      seen.add(signature);
      return true;
    });
    const counts = issues.reduce((result, issue) => {
      const key = ["blocking", "review", "warning", "info"].includes(issue.severity) ? issue.severity : "warning";
      result[key] += 1;
      return result;
    }, { blocking: 0, review: 0, warning: 0, info: 0 });
    const status = counts.blocking ? "blocked" : counts.review ? "review" : counts.warning ? "warning" : "ready";
    const duplicateHistory = parsed.duplicateHistory?.summary || {};
    return {
      ...base,
      generatedAt: new Date().toISOString(),
      status,
      scope: `${base.scope || "Diagnóstico estrutural do arquivo."} Duplicidades históricas abrangem somente este perfil do Chrome e registros concluídos pela extensão; envios manuais ou de outros perfis não podem ser presumidos.`,
      summary: { ...(base.summary || {}), ...duplicateHistory, actionable: counts.blocking + counts.review, ...counts },
      issues
    };
  }

  function pendingFileRuleReviews(diagnostic) {
    const source = diagnostic || currentFileDiagnostics();
    return (source?.issues || []).filter((issue) => issue.questionIndex == null && issue.severity === "review" && issue.category === "rules");
  }

  function fileRuleAuthorizationValid(diagnostic) {
    const authorization = app.session?.fileRuleAuthorization;
    const rules = pendingFileRuleReviews(diagnostic);
    if (!rules.length) return true;
    if (!authorization?.at || authorization.fileFingerprint !== app.session?.fileFingerprint) return false;
    const requiredCodes = Array.from(new Set(rules.map((issue) => issue.code))).sort();
    return requiredCodes.every((code) => (authorization.codes || []).includes(code));
  }

  function fileDiagnosticMatches(issue) {
    const filter = app.fileDiagnosticFilter || "action";
    if (filter === "all") return true;
    if (filter === "action") return issue.severity === "blocking" || issue.severity === "review";
    return issue.severity === filter;
  }

  function renderFileDiagnostics() {
    const diagnostic = currentFileDiagnostics();
    ui.fileDiagnostics.hidden = !diagnostic;
    if (!diagnostic) return;
    const summary = diagnostic.summary || {};
    const labels = {
      blocked: ["Erro encontrado", "Bloqueado"],
      review: ["Revisão necessária", "Revisar"],
      warning: ["Arquivo válido com avisos", "Avisos"],
      ready: ["Arquivo sem erro detectado", "Aprovado"]
    };
    const [title, badge] = labels[diagnostic.status] || labels.review;
    ui.fileDiagnostics.dataset.state = diagnostic.status;
    ui.fileDiagnosticTitle.textContent = title;
    ui.fileDiagnosticSubtitle.textContent = diagnostic.status === "ready"
      ? `${summary.questions || 0} questão(ões) lida(s); nenhum campo obrigatório ou falha textual foi encontrado.`
      : `${summary.actionable || 0} item(ns) exigem ação; cada causa e correção estão descritas abaixo.`;
    ui.fileDiagnosticBadge.textContent = badge;
    ui.fileDiagnosticMetrics.innerHTML = `
      <span class="aab-diagnostic-error"><b>${Number(summary.blocking || 0)}</b> erros</span>
      <span class="aab-diagnostic-review"><b>${Number(summary.review || 0)}</b> revisões</span>
      <span class="aab-diagnostic-warning"><b>${Number(summary.warning || 0)}</b> avisos</span>
      <span class="aab-diagnostic-valid"><b>${Number(summary.validQuestions || 0)}</b> válidas</span>`;
    const fileRuleReviews = pendingFileRuleReviews(diagnostic);
    const fileRulesApproved = fileRuleAuthorizationValid(diagnostic);
    ui.approveFileRules.hidden = !fileRuleReviews.length || fileRulesApproved || app.running;
    ui.revokeFileRules.hidden = !fileRuleReviews.length || !fileRulesApproved || app.running;
    if (fileRuleReviews.length && fileRulesApproved) {
      ui.fileDiagnosticSubtitle.textContent = `${fileRuleReviews.length} exceção(ões) geral(is) aprovada(s) conscientemente; erros por questão continuam exigindo correção ou autorização individual.`;
    }
    ui.fileDiagnosticFilter.value = app.fileDiagnosticFilter;
    const severityOrder = { blocking: 0, review: 1, warning: 2, info: 3 };
    const visible = (diagnostic.issues || []).filter(fileDiagnosticMatches).sort((left, right) =>
      (severityOrder[left.severity] ?? 4) - (severityOrder[right.severity] ?? 4) || Number(left.questionIndex ?? 9999) - Number(right.questionIndex ?? 9999)
    );
    const severityLabel = { blocking: "ERRO", review: "REVISAR", warning: "AVISO", info: "INFO" };
    ui.fileDiagnosticList.innerHTML = visible.length ? visible.map((issue) => {
      const location = issue.questionIndex == null
        ? "Arquivo inteiro"
        : `Questão ${escapeHtml(issue.questionNumber ?? issue.questionIndex + 1)}${issue.source?.start ? ` · parágrafos ${issue.source.start}–${issue.source.end}` : ""}`;
      const evidence = issue.evidence?.length ? `<details><summary>Ver evidências da base</summary>${issue.evidence.map((entry) => `<p><b>${escapeHtml(entry.documentName || "Material")}</b><br>${escapeHtml(entry.excerpt || "")}</p>`).join("")}</details>` : "";
      return `<article class="aab-file-issue aab-file-issue-${escapeHtml(issue.severity)}">
        <div class="aab-file-issue-top"><span>${severityLabel[issue.severity] || "AVISO"}</span><code>${escapeHtml(issue.code)}</code></div>
        <strong>${escapeHtml(issue.title)}</strong>
        <small>${escapeHtml(location)} · ${escapeHtml(issue.field || "Questão")}</small>
        <p>${escapeHtml(issue.message)}</p>
        <dl><div><dt>Impacto</dt><dd>${escapeHtml(issue.impact || "Requer conferência.")}</dd></div><div><dt>Como corrigir</dt><dd>${escapeHtml(issue.action || "Abra a questão e confira o Word.")}</dd></div></dl>
        ${evidence}
        ${issue.questionIndex == null ? "" : `<button type="button" class="aab-link-button" data-aab-open-file-issue="${Number(issue.questionIndex)}">Abrir esta questão</button>`}
      </article>`;
    }).join("") : `<div class="aab-file-diagnostic-empty"><strong>Nenhum item neste filtro.</strong><span>${diagnostic.issues?.length ? "O arquivo pode possuir apenas avisos; escolha Tudo para visualizá-los." : "A estrutura, os campos obrigatórios e os textos passaram na conferência automática."}</span></div>`;
    ui.fileDiagnosticScope.textContent = diagnostic.scope || "Diagnóstico estrutural do arquivo.";
    ui.downloadFileDiagnostic.disabled = false;
  }

  function openFileDiagnosticQuestion(index) {
    if (!app.session?.parsed?.questions?.[index]) return;
    app.reviewIndex = Number(index);
    app.reviewFilter = "all";
    ui.filter.value = "all";
    switchView("review");
    renderQuestion(app.reviewIndex);
    ui.questionSection.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function downloadCurrentFileDiagnostic() {
    const diagnostic = currentFileDiagnostics();
    if (!diagnostic) return;
    downloadJson({ product: PRODUCT_NAME, version: PRODUCT_VERSION, ...diagnostic }, `Laudo_do_arquivo_SmartFox_${new Date().toISOString().replace(/[:.]/g, "-")}.json`);
    recordOccurrence(`Laudo do arquivo “${diagnostic.fileName}” exportado com ${diagnostic.summary?.blocking || 0} erro(s), ${diagnostic.summary?.review || 0} revisão(ões) e ${diagnostic.summary?.warning || 0} aviso(s).`, "info", { code: "ARQUIVO_LAUDO_EXPORTADO" });
  }

  async function approveCurrentFileRules() {
    if (!app.session || app.running) return;
    const diagnostic = currentFileDiagnostics();
    const reviews = pendingFileRuleReviews(diagnostic);
    if (!reviews.length) return;
    const summary = reviews.map((issue) => `• ${issue.title}: ${issue.message}`).join("\n");
    const approved = window.confirm(`Aprovar conscientemente ${reviews.length} exceção(ões) gerais deste lote?\n\n${summary}\n\nIsto não aprova erros técnicos nem substitui a revisão individual das questões.`);
    if (!approved) return;
    app.session.fileRuleAuthorization = {
      at: new Date().toISOString(),
      fileFingerprint: app.session.fileFingerprint,
      codes: Array.from(new Set(reviews.map((issue) => issue.code))).sort(),
      note: "Exceções gerais lidas e aprovadas pelo professor."
    };
    await saveSession();
    log(`${reviews.length} exceção(ões) gerais do lote aprovadas pelo professor; erros técnicos permanecem bloqueados.`, "warning", { code: "ATHUS.EXCECOES_LOTE_APROVADAS" });
    renderSession();
  }

  async function revokeCurrentFileRules() {
    if (!app.session || app.running || !app.session.fileRuleAuthorization) return;
    app.session.fileRuleAuthorization = null;
    await saveSession();
    log("A aprovação das exceções gerais do lote foi revogada.", "info", { code: "ATHUS.EXCECOES_LOTE_REVOGADAS" });
    renderSession();
  }

  function renderReadiness() {
    if (!app.session) return;
    let eligibility = startEligibility();
    const fileOk = Boolean(app.session.parsed?.questions?.length);
    const fourOk = app.session.parsed.questions.every((question) => question.questionFormat === "discursive" || question.alternatives.length === REQUIRED_ALTERNATIVES);
    const requiredOk = !eligibility.hard.length;
    const reviewOk = !eligibility.review.length;
    const allocationPending = app.session.parsed.questions.filter((question, index) => allocationRequiresApproval(question, index)).length;
    const knowledgePending = app.session.parsed.questions.filter((question, index) => knowledgeRequiresDecision(question, index)).length;
    const baseStats = Knowledge.baseStats(app.knowledgeBase, activeKnowledgeCollection().id);
    const imageCount = app.session.parsed.questions.reduce((total, question) => total + (question.richIntegrity?.imageHashes?.length || 0), 0);
    const formulaCount = app.session.parsed.questions.reduce((total, question) => total + (question.richIntegrity?.formulaHashes?.length || 0), 0);
    const siteReady = Boolean(app.diagnosis?.ready);
    const tagConfig = app.session.tagConfig || {};
    const tagReady = selectedMode() === "draft" || Boolean(tagConfig.target && tagConfig.verifiedInStep3 && tagConfig.catalogSummary?.signature);
    const row = (ok, label, detail) => `<li class="${ok ? "aab-ready-ok" : "aab-ready-pending"}"><b>${ok ? "✓" : "!"}</b><div><strong>${escapeHtml(label)}</strong><small>${escapeHtml(detail)}</small></div></li>`;
    ui.readinessList.innerHTML = [
      row(fileOk && fourOk && requiredOk, "Estrutura da avaliação", fileOk && fourOk && requiredOk ? `${app.session.parsed.fileDiagnostics?.summary?.objectiveQuestions ?? app.session.parsed.questions.filter((question) => question.questionFormat !== "discursive").length} objetiva(s) A–D e ${app.session.parsed.fileDiagnostics?.summary?.discursiveQuestions ?? app.session.parsed.questions.filter((question) => question.questionFormat === "discursive").length} discursiva(s); ${app.session.parsed.duplicateQuestionCount || 0} repetição(ões) apenas sinalizadas.` : `${eligibility.hard.length} questão(ões) precisam de correção estrutural.`),
      row(tagReady, "Disciplina e tag manuais", tagReady ? (selectedMode() === "draft" ? "Rascunho: a conferência de likes não será executada." : `${tagConfig.target.label} confirmada nas escolhas manuais do Passo 3; automação somente do Passo 4 em diante.`) : (eligibility.setup?.[0]?.reason || "Mapeie e escolha uma tag de Graduação.")),
      row(!knowledgePending, "Conferência bibliográfica", baseStats.documents ? (knowledgePending ? `${knowledgePending} questão(ões) aguardam decisão com “${activeKnowledgeCollection().name}”.` : `${baseStats.documents} material(is) de “${activeKnowledgeCollection().name}” consultado(s); decisões concluídas.`) : `A coleção “${activeKnowledgeCollection().name}” está vazia; conferência bibliográfica opcional não executada.`),
      row(!allocationPending, "Conteúdo × matéria", allocationPending ? `${allocationPending} questão(ões) aguardam conferência ou aprovação da disciplina.` : "Correspondência conferida ou aprovada pelo professor."),
      row(requiredOk && reviewOk, "Qualidade e integridade", reviewOk ? `${imageCount} imagem(ns) e ${formulaCount} fórmula(s) serão comparadas antes do envio.` : `${eligibility.review.filter(item => !item.fileLevel).length} questão(ões) e ${eligibility.review.filter(item => item.fileLevel).length} pendência(s) geral(is) do arquivo aguardam aprovação.`),
      row(siteReady, "Tela do AvaliA", siteReady ? "Formulário e vínculos prontos para execução." : (app.diagnosis?.preflight?.title || "Use Testar tudo agora."))
    ].join("");
  }

  function renderProgress() {
    const session = app.session;
    const total = session?.items?.length || 0;
    const completed = Math.min(session?.currentIndex || 0, total);
    ui.progressBar.style.width = `${total ? Math.round((completed / total) * 100) : 0}%`;
    const official = (session?.results || []).filter((result) => result.status === "official").length;
    const drafts = (session?.results || []).filter((result) => result.status === "draft").length;
    const skipped = (session?.results || []).filter((result) => result.status === "skipped").length;
    ui.progressText.textContent = `${completed} de ${total} processada${completed === 1 ? "" : "s"} · ${official} oficiais · ${drafts} rascunhos · ${skipped} isoladas.`;
    const item = Engine.currentItem(session);
    ui.runState.textContent = app.cleanupBusy ? "Retirando likes" : session?.status === "cleanup_pending" ? "Envio salvo · likes pendentes" : session?.status === "completed" ? "Concluído" : item ? `Questão ${item.number} · ${Engine.phaseLabel(item.phase)}` : "Pronto";
    ui.startTime.textContent = formatClock(session?.startedAt);
    ui.endTime.textContent = formatClock(session?.endedAt);
    ui.confirmSent.hidden = item?.phase !== P.NEEDS_VERIFICATION;
    const lastError = item?.lastError || "";
    const problem = item?.lastProblem || (lastError ? classifyExecutionError(new Error(lastError), item) : null);
    ui.lastProblem.hidden = !problem;
    if (problem) ui.lastProblem.innerHTML = `
      <div class="aab-problem-head"><strong>${escapeHtml(problem.title || "Último problema")}</strong><code>${escapeHtml(problem.code || "EXECUTION_ERROR")}</code></div>
      <span><b>Questão:</b> ${escapeHtml(problem.questionNumber ?? item?.number ?? "—")}${problem.draftId ? ` · <b>Registro:</b> ${escapeHtml(problem.draftId)}` : ""} · <b>Etapa:</b> ${escapeHtml(Engine.phaseLabel(problem.phase || item?.phase))}</span>
      <span><b>Causa:</b> ${escapeHtml(problem.cause || problem.message || lastError)}</span>
      <span><b>Detalhe:</b> ${escapeHtml(problem.message || lastError)}</span>
      <span><b>Tentativas:</b> preencher ${Number(problem.attempts?.fill || 0)} · salvar ${Number(problem.attempts?.save || 0)} · etapas ${Number(problem.attempts?.prepare || 0)} · enviar ${Number(problem.attempts?.submit || 0)}</span>
      <span><b>Próxima ação:</b> ${escapeHtml(problem.action || "Use a retomada inteligente.")}</span>`;
  }

  function approvalExpectedDisciplines() {
    const configured = app.session?.tagConfig?.selectedDisciplines;
    if (Array.isArray(configured) && configured.length) return configured;
    const records = app.diagnosis?.state?.disciplineRecords || [];
    if (records.length) return records.map((record) => record.discipline || record.text).filter(Boolean);
    return (app.session?.disciplineSnapshot || []).map((entry) => typeof entry === "string" ? entry : entry.discipline || entry.text || "").filter(Boolean);
  }

  function renderApprovalSync() {
    const session = app.session;
    const sync = session?.approvalSync;
    const enabled = false; // Superseded by the independent full-bank manager.
    ui.approvalSync.hidden = !enabled;
    if (!enabled) return;
    const officialIds = Approval.latestOfficialIds(session.results || []);
    const labels = {
      waiting_for_batch: ["Aguardando lote", "A conferência será liberada depois que os envios oficiais terminarem."],
      awaiting_professor: ["Abra Professor", `No perfil Professor, abra a disciplina escolhida, entre em Todas questões e filtre por “${session.tagConfig.target?.label || "a tag escolhida"}”.`],
      inspecting: ["Mapeando", "Lendo IDs, paginação, tag, disciplina e estado atual dos likes."],
      preview_ready: ["Prévia pronta", "Confira as quantidades abaixo; nenhuma alteração foi feita."],
      blocked: ["Ação necessária", "A prévia encontrou um escopo incompleto ou ambíguo e não liberou alterações."],
      applying: ["Ajustando", "Cada alteração é conferida e registrada antes de avançar."],
      verification_required: ["Conferência manual", "Uma ação não retornou confirmação inequívoca; ela não será repetida."],
      completed: ["Concluído", "Somente os IDs oficiais da última remessa permanecem aprovados neste escopo."],
      catalog_changed: ["Remapear tags", "O catálogo mudou; escolha novamente uma tag de Graduação."],
      not_requested: ["Desligado", "A sincronização opcional não foi solicitada."]
    };
    const [badge, message] = labels[sync.status] || labels.awaiting_professor;
    ui.approvalBadge.textContent = badge;
    ui.approvalStatus.textContent = message;
    const plan = sync.plan;
    if (plan) {
      const issueHtml = (plan.issues || []).slice(0, 6).map((issue) => `<li><code>${escapeHtml(issue.code)}</code><span>${escapeHtml(issue.message)}</span></li>`).join("");
      ui.approvalSummary.innerHTML = `<div class="aab-approval-metrics"><span><b>${plan.totals?.keep || 0}</b> manter</span><span><b>${plan.totals?.approve || 0}</b> adicionar</span><span><b>${plan.totals?.remove || 0}</b> retirar</span><span><b>${plan.totals?.unchanged || 0}</b> já sem like</span></div><small>${escapeHtml(plan.discipline || "Disciplina não confirmada")} · ${escapeHtml(plan.targetTag?.label || "Tag não confirmada")} · ${plan.totals?.scanned || 0}/${plan.workspaceTotal || plan.totals?.scanned || 0} linha(s) lida(s)</small>${issueHtml ? `<ul class="aab-approval-issues">${issueHtml}</ul>` : ""}`;
    } else {
      ui.approvalSummary.innerHTML = `<span>${officialIds.length} ID(s) oficial(is) preservado(s) nesta remessa.</span>`;
    }
    const canInspect = session.status === "completed" && officialIds.length > 0 && !app.running && !app.approvalRunning;
    ui.inspectApprovals.disabled = !canInspect;
    ui.applyApprovals.hidden = !(sync.status === "preview_ready" && plan?.safeToApply);
    ui.applyApprovals.disabled = app.running || app.approvalRunning;
  }

  function approvalPlanFromWorkspace(workspace) {
    const session = app.session;
    const plan = Approval.buildPlan({
      catalog: session.tagConfig.catalogSnapshot || [],
      targetTag: session.tagConfig.target,
      latestIds: Approval.latestOfficialIds(session.results || []),
      discipline: workspace.discipline,
      workspace
    });
    plan.workspaceTotal = workspace.totalReported;
    plan.workspaceInspectedAt = workspace.inspectedAt;
    return plan;
  }

  async function inspectApprovals() {
    if (!app.session?.approvalSync?.enabled || app.session.status !== "completed" || app.approvalRunning) return;
    const sync = app.session.approvalSync;
    const tagConfig = app.session.tagConfig || {};
    if (sync.status === "catalog_changed" || !sync.catalogCheckedAt || !sync.catalogSignature || sync.catalogSignature !== tagConfig.catalogSummary?.signature) {
      sync.status = "catalog_changed";
      sync.plan = null;
      sync.updatedAt = new Date().toISOString();
      await saveSession();
      log("[CATALOGO_TAGS_REMAPEAMENTO_OBRIGATORIO] O catálogo de tags não possui uma conferência final válida para esta remessa. Volte ao Elaborador, mapeie novamente e escolha manualmente a tag de Graduação; nenhum like foi alterado.", "warning", { code: "CATALOGO_TAGS_REMAPEAMENTO_OBRIGATORIO" });
      renderApprovalSync();
      return;
    }
    sync.status = "inspecting";
    sync.updatedAt = new Date().toISOString();
    renderApprovalSync();
    try {
      const workspace = await bridge("inspectApprovalWorkspace", {
        targetTag: app.session.tagConfig.target,
        expectedDisciplines: approvalExpectedDisciplines()
      }, 20000);
      if (workspace.pageKind === "login") throw new Error("[AVALIA_SESSAO_EXPIRADA] Entre novamente no AvaliA e retorne ao perfil Professor.");
      if (workspace.pageKind !== "professor") throw new Error(`[PAGINA_PROFESSOR_NECESSARIA] Esta aba está em ${workspace.urlPath || "outra página"}. Abra o perfil Professor, a disciplina e Todas questões.`);
      sync.plan = approvalPlanFromWorkspace(workspace);
      sync.status = sync.plan.safeToApply ? "preview_ready" : "blocked";
      sync.updatedAt = new Date().toISOString();
      await saveSession();
      if (sync.plan.safeToApply) {
        log(`Prévia de likes pronta: ${sync.plan.totals.keep} manter, ${sync.plan.totals.approve} adicionar e ${sync.plan.totals.remove} retirar em “${sync.plan.targetTag.label}”.`, "success", { code: "LIKE_PREVIA_PRONTA" });
      } else {
        const first = sync.plan.issues[0];
        log(`Prévia de likes bloqueada: ${first?.message || "o escopo não foi confirmado"} Nenhuma alteração foi feita.`, "warning", { code: first?.code || "LIKE_PREVIA_BLOQUEADA" });
      }
    } catch (error) {
      sync.status = "blocked";
      sync.plan = { safeToApply: false, issues: [{ code: errorCode(error) || "LIKE_INSPECAO_FALHOU", message: error.message }], totals: {}, targetTag: app.session.tagConfig.target };
      sync.errors.push({ at: new Date().toISOString(), code: errorCode(error) || "LIKE_INSPECAO_FALHOU", message: error.message });
      sync.errors = sync.errors.slice(-50);
      await saveSession();
      log(error.message, "warning", { code: errorCode(error) || "LIKE_INSPECAO_FALHOU" });
    }
    renderApprovalSync();
  }

  async function applyApprovals() {
    const session = app.session;
    const sync = session?.approvalSync;
    if (!sync?.enabled || sync.status !== "preview_ready" || !sync.plan?.safeToApply || app.approvalRunning) return;
    app.approvalRunning = true;
    renderApprovalSync();
    try {
      const payload = { targetTag: session.tagConfig.target, expectedDisciplines: approvalExpectedDisciplines() };
      const freshWorkspace = await bridge("inspectApprovalWorkspace", payload, 20000);
      const freshPlan = approvalPlanFromWorkspace(freshWorkspace);
      if (!freshPlan.safeToApply || freshPlan.planSignature !== sync.plan.planSignature) {
        sync.plan = freshPlan;
        sync.status = freshPlan.safeToApply ? "preview_ready" : "blocked";
        sync.updatedAt = new Date().toISOString();
        await saveSession();
        log("[LIKE_PREVIA_ALTERADA] A lista mudou depois da prévia. Confira as novas quantidades e confirme novamente; nenhum like foi alterado.", "warning", { code: "LIKE_PREVIA_ALTERADA" });
        return;
      }
      const approved = window.confirm(`CONFIRMAÇÃO DE LIKES — ÚLTIMA REMESSA\n\nDisciplina: ${freshPlan.discipline}\nTag de Graduação: ${freshPlan.targetTag.label}\n\n${freshPlan.totals.keep} likes serão mantidos.\n${freshPlan.totals.approve} questões da última remessa receberão like.\n${freshPlan.totals.remove} likes de questões fora da última remessa serão retirados.\n${freshPlan.totals.unchanged} questões continuarão sem like.\n\nA ação se limita aos IDs, à disciplina e à tag exibidos. Deseja continuar?`);
      if (!approved) {
        log("Ajuste de likes cancelado; a prévia foi preservada e nada foi alterado.", "info", { code: "LIKE_CANCELADO" });
        return;
      }
      sync.status = "applying";
      sync.confirmedAt = new Date().toISOString();
      sync.updatedAt = sync.confirmedAt;
      await saveSession();
      renderApprovalSync();
      const actions = [
        ...freshPlan.approve.map((row) => ({ id: row.id, desiredLiked: true, action: "approve" })),
        ...freshPlan.remove.map((row) => ({ id: row.id, desiredLiked: false, action: "remove" }))
      ];
      for (const action of actions) {
        const result = await bridge("applyApprovalDecision", { ...payload, questionId: action.id, desiredLiked: action.desiredLiked }, 20000);
        if (!result.confirmed) {
          sync.status = "verification_required";
          sync.errors.push({ at: new Date().toISOString(), code: "LIKE_RESULTADO_INDETERMINADO", questionId: action.id, message: result.message || "A ação não retornou confirmação." });
          sync.updatedAt = new Date().toISOString();
          await saveSession();
          log(`[LIKE_RESULTADO_INDETERMINADO] Questão ${action.id}: o clique não foi repetido. Confira o estado no AvaliA e gere uma nova prévia.`, "error", { code: "LIKE_RESULTADO_INDETERMINADO" });
          return;
        }
        sync.processedIds.push({ id: action.id, action: action.action, at: new Date().toISOString(), alreadyCorrect: Boolean(result.alreadyCorrect) });
        sync.updatedAt = new Date().toISOString();
        await saveSession();
        log(`Questão ${action.id}: ${action.desiredLiked ? "like confirmado para a última remessa" : "like antigo retirado e confirmado"}.`, "success", { code: action.desiredLiked ? "LIKE_ADICIONADO" : "LIKE_RETIRADO" });
      }
      const finalWorkspace = await bridge("inspectApprovalWorkspace", payload, 20000);
      const finalPlan = approvalPlanFromWorkspace(finalWorkspace);
      sync.plan = finalPlan;
      if (finalPlan.safeToApply && finalPlan.totals.approve === 0 && finalPlan.totals.remove === 0) {
        sync.status = "completed";
        sync.completedAt = new Date().toISOString();
        log(`FIM DA CONFERÊNCIA: ${finalPlan.totals.keep} questão(ões) da última remessa com like; nenhuma questão externa à remessa permaneceu aprovada no escopo.`, "success", { code: "LIKES_SINCRONIZADOS" });
      } else {
        sync.status = finalPlan.safeToApply ? "preview_ready" : "blocked";
        log("A verificação final encontrou mudança na lista. Nenhuma ação será repetida; confira a nova prévia.", "warning", { code: "LIKE_VERIFICACAO_FINAL" });
      }
      sync.updatedAt = new Date().toISOString();
      await saveSession();
    } catch (error) {
      sync.status = "blocked";
      sync.errors.push({ at: new Date().toISOString(), code: errorCode(error) || "LIKE_EXECUCAO_FALHOU", message: error.message });
      sync.errors = sync.errors.slice(-50);
      sync.updatedAt = new Date().toISOString();
      await saveSession();
      log(`Ajuste de likes interrompido: ${error.message} Nenhuma ação incerta será repetida.`, "error", { code: errorCode(error) || "LIKE_EXECUCAO_FALHOU" });
    } finally {
      app.approvalRunning = false;
      renderApprovalSync();
    }
  }

  function renderControls() {
    const session = app.session;
    const pendingReviews = (session?.parsed?.questions || []).filter((q, index) => session.items[index]?.phase === P.PENDING);
    ui.approveAllReviews.disabled = app.running || app.approvalRunning || app.batchReviewBusy || app.knowledgeBusy || app.fileImportBusy || app.fileRemovalBusy || app.abandoning || !pendingReviews.length;
    ui.bulkReviewSummary.textContent = app.batchReviewBusy ? "Conferindo e registrando a aprovação do lote…" : pendingReviews.length
      ? `${pendingReviews.length} questão(ões) ainda não enviadas. A ação abrange o lote inteiro, incluindo questões fora do filtro atual.`
      : "Nenhuma questão pendente para aprovar.";
    ui.clearQuestions.disabled = app.abandoning || app.fileRemovalBusy;
    const resumable = session && session.currentIndex < session.items.length && ["paused", "verification_required", "running"].includes(session.status) && Boolean(session.confirmedAt);
    const cleanupPending=Engine.needsBankCleanup(session);
    ui.cleanupPanel.hidden=!cleanupPending;
    ui.cleanupState.textContent=app.cleanupBusy?"Conferindo os likes no banco correto. Aguarde a confirmação.":session?.bankCleanupReceipt?.message||"As questões já enviadas estão salvas. Falta confirmar a retirada dos likes.";
    ui.finishCleanup.disabled=app.running||app.cleanupBusy||app.abandoning;
    ui.start.hidden = Boolean(resumable || session?.status === "completed" || session?.status === "cleanup_pending");
    ui.resume.hidden = !resumable || app.running;
    ui.start.disabled = app.cleanupBusy || app.batchReviewBusy || app.running || app.fileRemovalBusy || app.fileImportBusy || !session;
    ui.resume.disabled = app.cleanupBusy || app.batchReviewBusy || app.running || app.fileRemovalBusy || app.fileImportBusy;
    ui.fillCurrent.disabled = app.batchReviewBusy || app.running || app.fileRemovalBusy || app.fileImportBusy || !session || reviewItem()?.phase !== P.PENDING;
    ui.smartRecover.disabled = app.running;
    const current = Engine.currentItem(session);
    const problem = current?.lastProblem || (current?.lastError ? classifyExecutionError(new Error(current.lastError), current) : null);
    ui.skipCurrent.hidden = !canSkipItem(current, problem);
    ui.skipCurrent.disabled = app.running;
    ui.stop.disabled = !app.running;
    ui.file.disabled = app.running || app.fileImportBusy || app.fileRemovalBusy;
    ui.removeFile.hidden = !(ui.file.files?.length || session || app.fileImportFailure);
    ui.removeFile.disabled = app.running || app.approvalRunning || app.fileImportBusy || app.fileRemovalBusy;
    ui.modeInputs.forEach((input) => { input.disabled = app.running || Boolean(session?.confirmedAt); });
    ui.continueErrors.disabled = app.running;
    ui.mapTags.disabled = app.running || Boolean(session?.confirmedAt);
    ui.targetTag.disabled = app.running || Boolean(session?.confirmedAt) || !app.tagCatalog;
    ui.syncLikes.disabled = true;
    ui.materialFiles.disabled = app.running || app.knowledgeBusy;
    ui.addMaterials.disabled = app.running || app.knowledgeBusy;
    ui.reviewAllHigh.disabled = app.running || !session?.parsed?.questions?.some((question, index) => session.items[index]?.phase === P.PENDING && question.knowledgeAudit?.status === "mismatch" && Number(question.knowledgeAudit.confidence || 0) >= 0.9 && Boolean(question.knowledgeAudit.feedbackSuggestion));
    renderKnowledgeBase();
    renderTagPanel();
    renderApprovalSync();
  }

  function renderSession() {
    const session = app.session;
    if (!app.abandoning) ui.workStatus.textContent = session ? "Lote aberto" : "Trabalho atual";
    if (!session) {
      ui.questionSection.hidden = true;
      ui.readinessSection.hidden = true;
      ui.runSection.hidden = true;
      renderStats();
      ui.fileSummary.textContent = "Nenhum arquivo analisado.";
      renderFileDiagnostics();
      renderControls();
      renderNavigation();
      renderKnowledgeBase();
      renderTagPanel();
      renderApprovalSync();
      return;
    }
    const parsed = session.parsed;
    const objectiveCount = parsed.questions.filter((question) => question.questionFormat !== "discursive").length;
    const discursiveCount = parsed.questions.length - objectiveCount;
    const eligibility = startEligibility();
    const remainingBlocked = eligibility.hard.length;
    const remainingReview = eligibility.review.length;
    ui.fileSummary.innerHTML = `<div class="aab-file-result ${remainingBlocked ? "aab-file-bad" : remainingReview ? "aab-file-review" : "aab-file-good"}">
      <strong>${escapeHtml(session.fileName)}</strong>
      <span>${parsed.questionCount} questões reconhecidas · ${parsed.validQuestionCount ?? parsed.executableCount} válidas · ${objectiveCount} objetiva(s) A–D · ${discursiveCount} discursiva(s) · ${parsed.duplicateQuestionCount || 0} repetidas (aviso)</span>
      ${parsed.answerDistribution ? `<span>Gabaritos: A ${parsed.answerDistribution.A || 0} · B ${parsed.answerDistribution.B || 0} · C ${parsed.answerDistribution.C || 0} · D ${parsed.answerDistribution.D || 0}${parsed.answerDistributionWarning ? ` · <b>${escapeHtml(parsed.answerDistributionWarning)}</b>` : ""}</span>` : ""}
      <span>${remainingBlocked ? `${remainingBlocked} precisam de correção` : remainingReview ? `${remainingReview} aguardam sua autorização` : "Lote interpretado e pronto"}</span>
    </div>`;
    ui.questionSection.hidden = false;
    ui.readinessSection.hidden = false;
    ui.runSection.hidden = false;
    app.reviewIndex = Math.max(0, Math.min(app.reviewIndex, parsed.questions.length - 1));
    renderStats();
    renderFileDiagnostics();
    renderQuestion(app.reviewIndex);
    renderReadiness();
    renderProgress();
    renderControls();
    renderNavigation();
    renderKnowledgeBase();
    renderTagPanel();
    renderApprovalSync();
    startClock();
  }

  function renderPreflight(diagnosis) {
    const preflight = diagnosis?.preflight;
    if (!preflight) {
      ui.preflightBadge.className = "aab-preflight-badge aab-preflight-blocked";
      ui.preflightBadge.textContent = "Sem resposta";
      ui.preflightChecks.innerHTML = "";
      ui.preflightExplanation.innerHTML = "<strong>Não foi possível concluir o teste.</strong><span>Atualize a aba e execute o teste novamente.</span>";
      ui.preflightTime.textContent = "Teste sem resposta válida.";
      return;
    }
    const badgeLabel = preflight.status === "ready" ? "Pronto" : preflight.status === "login" ? "Novo acesso" : "Ação necessária";
    ui.preflightBadge.className = `aab-preflight-badge aab-preflight-${preflight.status === "ready" ? "ready" : "blocked"}`;
    ui.preflightBadge.textContent = badgeLabel;
    ui.preflightChecks.innerHTML = (preflight.checks || []).map((check) => `
      <div class="aab-preflight-check aab-check-${escapeHtml(check.status)}" title="${escapeHtml(check.detail)}">
        <b>${check.status === "ok" ? "✓" : check.status === "error" ? "!" : "…"}</b>
        <span><strong>${escapeHtml(check.label)}</strong><small>${escapeHtml(check.detail)}</small></span>
      </div>`).join("");
    ui.preflightExplanation.className = `aab-preflight-explanation ${preflight.status === "ready" ? "aab-explanation-ready" : "aab-explanation-blocked"}`;
    ui.preflightExplanation.innerHTML = `
      <div class="aab-preflight-title"><strong>${escapeHtml(preflight.title)}</strong><code>${escapeHtml(preflight.code)}</code></div>
      <span><b>Causa:</b> ${escapeHtml(preflight.cause)}</span>
      <span><b>Impacto:</b> ${escapeHtml(preflight.impact)}</span>
      <span><b>Ação:</b> ${escapeHtml(preflight.action)}</span>`;
    ui.preflightTime.textContent = `Último teste: ${formatClock(preflight.checkedAt)}${diagnosis.state?.roleName ? ` · perfil ${diagnosis.state.roleName}` : ""}`;
  }

  function recordDiagnosisOccurrence(diagnosis) {
    const preflight = diagnosis?.preflight;
    if (!preflight) return;
    const signature = JSON.stringify({ code: preflight.code, step: diagnosis.state?.currentStep, source: Boolean(diagnosis.state?.sourceId), institution: Boolean(diagnosis.state?.institutionId), disciplines: diagnosis.state?.disciplines?.length || 0, editors: diagnosis.state?.editorsReady });
    if (signature === app.lastDiagnosisSignature) return;
    app.lastDiagnosisSignature = signature;
    const kind = preflight.status === "ready" ? "success" : ["FORMULARIO_FECHADO", "ETAPA_INCORRETA"].includes(preflight.code) ? "warning" : "error";
    recordOccurrence(`Pré-teste: ${preflight.title} Ação: ${preflight.action}`, kind, { code: preflight.code, source: "preflight" });
  }

  function renderDiagnosis(diagnosis) {
    app.diagnosis = diagnosis;
    renderPreflight(diagnosis);
    const issues = diagnosis?.issues || [];
    const siteErrors = diagnosis?.state?.recentSiteErrors || [];
    if (!issues.length && !siteErrors.length) {
      ui.diagnosis.hidden = true;
    } else {
      ui.diagnosis.hidden = false;
      ui.diagnosis.innerHTML = `${issues.length ? `<ul>${issues.map((issue) => `<li class="aab-diagnostic-${escapeHtml(issue.severity)}"><b>${issue.repairable ? "AUTO" : "AÇÃO"}</b><div><strong>${escapeHtml(issue.message)}</strong><code>${escapeHtml(issue.code)}</code><small><b>Próximo passo:</b> ${escapeHtml(issue.action)}</small></div></li>`).join("")}</ul>` : ""}${siteErrors.length ? `<details class="aab-site-errors"><summary>Erros registrados pelo próprio AvaliA (${siteErrors.length})</summary><ol>${siteErrors.slice().reverse().map((entry) => `<li><code>${escapeHtml(entry.code)}</code><span>${escapeHtml(entry.message)}${entry.status ? ` · HTTP ${entry.status}` : ""}</span><time>${escapeHtml(formatClock(entry.at))}</time></li>`).join("")}</ol></details>` : ""}`;
    }
    renderReadiness();
  }

  function readinessMessage(diagnosis) {
    if (diagnosis?.state?.loginDetected) return { kind: "danger", message: "Sessão expirada: entre novamente no AvaliA e repita o teste de perfil." };
    if (!diagnosis?.state?.supportedPage) return { kind: "danger", message: "Para cadastrar questões, abra Ferramentas → Elaborador. Na tela azul você pode usar os bancos, corrigir e consultar relatórios." };
    if (!diagnosis.state.formReady) return { kind: "warning", message: "Abra Elabore Novas Questões e configure a avaliação." };
    if (diagnosis.ready) return { kind: "success", message: `AvaliA pronto: ${diagnosis.state.institutionName || "IES confirmada"}, ${diagnosis.state.disciplines.length} disciplina(s), ${diagnosis.state.currentStep}.` };
    const first = diagnosis.issues.find((issue) => issue.severity === "blocking");
    return { kind: first?.repairable ? "warning" : "danger", message: first?.message || "A tela ainda precisa de configuração." };
  }

  async function refreshSiteStatus(silent) {
    ui.testProfile.disabled = true;
    ui.testProfile.textContent = "Testando…";
    ui.preflightBadge.className = "aab-preflight-badge aab-preflight-testing";
    ui.preflightBadge.textContent = "Testando";
    try {
      const storageHealth = await testLocalDatabase({ silent: true });
      const item = Engine.currentItem(app.session);
      const diagnosis = includeStorageCheck(await bridge("diagnoseWorkspace", { expectedDraftId: item?.draftId || "" }, 12000), storageHealth);
      if (diagnosis.state?.tagCatalog?.total) acceptMappedTagCatalog(diagnosis.state.tagCatalog, { state: diagnosis.state });
      else applyManualTagVerification(diagnosis.state);
      (diagnosis.state?.recentSiteErrors || []).forEach((entry) => {
        const signature = `${entry.at}:${entry.code}:${entry.message}`;
        if (app.knownSiteErrors.has(signature)) return;
        app.knownSiteErrors.add(signature);
        const problem = classifyExecutionError(new Error(`[${entry.code}] ${entry.message}`), Engine.currentItem(app.session));
        recordOccurrence(`${problem.title}: ${problem.message}${entry.status ? ` (HTTP ${entry.status})` : ""} Próxima ação: ${problem.action}`, "error", { at: entry.at, code: entry.code, source: "avalia" });
      });
      if (app.session && diagnosis.state?.disciplines?.length) await auditAllocations(diagnosis.state.disciplines, { render: false, log: false });
      if (app.session && diagnosis.state?.recentSiteErrors?.length) {
        const existing = new Set((app.session.avaliaErrors || []).map((entry) => `${entry.at}:${entry.code}:${entry.message}`));
        app.session.avaliaErrors = [...(app.session.avaliaErrors || []), ...diagnosis.state.recentSiteErrors.filter((entry) => !existing.has(`${entry.at}:${entry.code}:${entry.message}`))].slice(-100);
        if (storageHealth.ok) await saveSession();
      }
      if (app.session && storageHealth.ok) await saveSession();
      renderDiagnosis(diagnosis);
      recordDiagnosisOccurrence(diagnosis);
      const status = readinessMessage(diagnosis);
      setSiteStatus(status.kind, status.message);
      if (!silent) log(status.message, diagnosis.ready ? "success" : "info");
      if (app.session) renderSession();
      return diagnosis;
    } catch (error) {
      app.diagnosis = { ready: false, error, issues: [], state: null, preflight: null };
      renderPreflight(null);
      setSiteStatus("danger", `A extensão não conseguiu conversar com o formulário. Atualize a aba após instalar a versão ${PRODUCT_LABEL}.`);
      if (!silent) log(error.message, "error");
      else recordOccurrence(error.message, "error", { code: errorCode(error), source: "preflight" });
      renderReadiness();
      return app.diagnosis;
    } finally {
      ui.testProfile.disabled = false;
      ui.testProfile.textContent = "Testar tudo agora";
      renderSystemHealth();
    }
  }

  async function smartRepair(silent) {
    try {
      setSiteStatus("neutral", "Analisando a etapa atual e aplicando somente correções seguras...");
      const item = Engine.currentItem(app.session);
      const diagnosis = await bridge("diagnoseAndRepair", { expectedDraftId: item?.draftId || "" }, 50000);
      if (app.session && diagnosis.state?.disciplines?.length) await auditAllocations(diagnosis.state.disciplines, { render: false, log: false });
      renderDiagnosis(diagnosis);
      const status = readinessMessage(diagnosis);
      setSiteStatus(status.kind, status.message);
      if (diagnosis.repaired?.length) log(`Correção inteligente: ${diagnosis.repaired.join(" ")}`, "success");
      else if (!silent) log(diagnosis.ready ? "Nenhum reparo era necessário." : "Os itens restantes exigem uma escolha sua no AvaliA.", diagnosis.ready ? "success" : "warning");
      return diagnosis;
    } catch (error) {
      setSiteStatus("danger", error.message);
      if (!silent) log(`A correção inteligente foi interrompida: ${error.message}`, "error");
      return { ready: false, error, issues: [] };
    }
  }

  function sessionTagOptions() {
    const config = activeTagConfig() || {};
    return {
      tagCatalogSummary: app.tagCatalog ? {
        total: app.tagCatalog.total,
        eligibleCount: app.tagCatalog.eligibleCount,
        ignoredCount: app.tagCatalog.ignoredCount,
        groups: app.tagCatalog.groups,
        signature: app.tagCatalog.signature,
        mappedAt: app.tagCatalog.mappedAt
      } : config.catalogSummary || null,
      targetTag: config.target || null,
      syncLatestOnly: Boolean(config.syncLatestOnly)
    };
  }

  function finishSessionTagSetup(session) {
    if (!session) return;
    session.tagConfig.catalogSnapshot = app.tagCatalog?.catalog || activeTagConfig()?.catalogSnapshot || [];
    applyManualTagVerification(app.diagnosis?.state);
    app.pendingTagConfig = { target: session.tagConfig.target, syncLatestOnly: session.tagConfig.syncLatestOnly };
  }

  async function onFileSelected(event) {
    const file = event.target.files && event.target.files[0];
    if (!file || app.running || app.fileImportBusy || app.fileRemovalBusy) return;
    app.fileImportBusy = true;
    renderControls();
    try {
    app.fileImportFailure = null;
    app.fileDiagnosticFilter = "action";
    ui.fileDiagnostics.hidden = true;
    modeStrip("running", "Executando pré-teste.", "Validando o perfil antes de interpretar o Word.");
    const initialDiagnosis = await refreshSiteStatus(true);
    ui.fileSummary.textContent = "Lendo o Word, localizando limites, classificando modelos e auditando o sentido...";
    modeStrip("running", "Interpretando.", "Nenhuma informação está sendo enviada ao AvaliA.");
    try {
      const parsed = await Parser.parse(file);
      assertWorkActive();
      parsed.duplicateHistory = Duplicates.scan(app.duplicateLedger, {
        fileName: file.name,
        fileFingerprint: parsed.fileFingerprint,
        questions: parsed.questions
      });
      app.session = Engine.createSession(parsed, { fileName: file.name, outputMode: selectedMode(), fillKeywords: ui.keywords.checked, ...sessionTagOptions() });
      finishSessionTagSetup(app.session);
      app.session.fileRuleAuthorization = null;
      app.session.events = [];
      app.session.notifyWhenDone = ui.notify.checked;
      app.session.continueOnError = ui.continueErrors.checked;
      app.session.importedQuestions = JSON.parse(JSON.stringify(parsed.questions));
      app.reviewIndex = 0;
      await saveSession();
      try {
        await registerImportedFile(file, parsed, app.session.runId);
      } catch (ledgerError) {
        log(`O histórico de duplicidades não pôde ser atualizado: ${ledgerError.message}`, "warning", { code: "DUPLICIDADE.HISTORICO_NAO_GRAVADO" });
      }
      await scanQuestionsWithBase({ silent: true });
      app.currentView = "review";
      renderSession();
      const fileDiagnostic = currentFileDiagnostics();
      if (!fileDiagnostic?.summary?.actionable && fileDiagnostic?.summary?.warning) {
        app.fileDiagnosticFilter = "warning";
        renderFileDiagnostics();
      }
      const firstAction = fileDiagnostic?.issues?.find((issue) => ["blocking", "review"].includes(issue.severity));
      log(`Diagnóstico do arquivo: ${fileDiagnostic?.summary?.blocking || 0} erro(s), ${fileDiagnostic?.summary?.review || 0} revisão(ões), ${fileDiagnostic?.summary?.warning || 0} aviso(s) e ${fileDiagnostic?.summary?.validQuestions || 0} questão(ões) estruturalmente válida(s).`, fileDiagnostic?.summary?.actionable ? "warning" : "success", { code: "ARQUIVO_DIAGNOSTICADO" });
      if (firstAction) log(`${firstAction.title} — ${firstAction.message} Local: ${firstAction.questionIndex == null ? "arquivo inteiro" : `questão ${firstAction.questionNumber}, parágrafos ${firstAction.source?.start || "—"}–${firstAction.source?.end || "—"}`}. Como corrigir: ${firstAction.action}`, firstAction.severity === "blocking" ? "error" : "warning", { code: firstAction.code, questionNumber: firstAction.questionNumber, source: "file-diagnostic" });
      const duplicateSummary = parsed.duplicateHistory?.summary || {};
      const duplicateSignals = Number(parsed.duplicateQuestionCount || 0) + Number(parsed.similarQuestionCount || 0)
        + Number(duplicateSummary.sameFileImports || 0) + Number(duplicateSummary.sameNameDifferentContent || 0)
        + Number(duplicateSummary.renamedSameContent || 0) + Number(duplicateSummary.previouslySubmittedQuestions || 0);
      if (duplicateSignals) log(`Duplicidades sinalizadas sem bloqueio: ${parsed.duplicateQuestionCount || 0} idêntica(s) e ${parsed.similarQuestionCount || 0} muito semelhante(s) dentro do DOCX; ${duplicateSummary.sameFileImports || 0} reimportação(ões), ${duplicateSummary.sameNameDifferentContent || 0} nome(s) reutilizado(s), ${duplicateSummary.renamedSameContent || 0} conteúdo(s) renomeado(s) e ${duplicateSummary.previouslySubmittedQuestions || 0} questão(ões) já processada(s).`, "warning", { code: "DUPLICIDADE.RESUMO" });
      const diagnosis = initialDiagnosis?.preflight ? initialDiagnosis : await refreshSiteStatus(true);
      if (parsed.blockedCount) {
        modeStrip("danger", "Revisão necessária.", `${parsed.blockedCount} questão(ões) têm campos obrigatórios para corrigir.`);
        log(`O Word foi dividido em ${parsed.questionCount} questões; ${parsed.blockedCount} precisam de edição antes da autorização.`, "warning");
      } else if (!parsed.autoReady) {
        modeStrip("warning", "Confira os alertas.", "Você pode editar ou autorizar cada questão individualmente.");
        log(`Interpretação concluída: ${parsed.reviewCount} questão(ões) aguardam leitura e autorização.`, "warning");
      } else {
        modeStrip("success", "Arquivo aprovado.", `${parsed.questionCount} questões reconhecidas: ${parsed.fileDiagnostics?.summary?.objectiveQuestions ?? parsed.questions.filter((question) => question.questionFormat !== "discursive").length} objetiva(s) A–D e ${parsed.fileDiagnostics?.summary?.discursiveQuestions ?? parsed.questions.filter((question) => question.questionFormat === "discursive").length} discursiva(s).`);
        log(`${parsed.questionCount} questões interpretadas; limites, tipos e textos foram conferidos.`, "success");
        if (ui.autoStart.checked) {
          if (diagnosis.ready && startEligibility().ready) await runBatch({ automatic: true });
          else modeStrip("warning", "Arquivo pronto.", "Conclua a configuração indicada no AvaliA e clique em Iniciar.");
        }
      }
    } catch (error) {
      app.session = null;
      app.fileImportFailure = Parser.importFailureDiagnostic(error, file);
      const failure = app.fileImportFailure.issues[0];
      ui.fileSummary.innerHTML = `<div class="aab-file-result aab-file-bad"><strong>${escapeHtml(file.name)}</strong><span>${escapeHtml(failure.title)}</span><span>${escapeHtml(failure.message)}</span></div>`;
      modeStrip("danger", "Arquivo não interpretado.", "Confira o formato e tente novamente.");
      renderSession();
      log(`${failure.title}: ${failure.message} Como corrigir: ${failure.action}`, "error", { code: failure.code, source: "file-diagnostic" });
    }
    } finally {
      app.fileImportBusy = false;
      renderControls();
    }
  }

  async function loadRuleFile() {
    const file = ui.ruleFile.files?.[0];
    if (!file) return;
    try {
      ui.generationResult.textContent = `Lendo regras de ${file.name}…`;
      const text = await Knowledge.extractFile(file);
      assertWorkActive();
      const current = Athus.masterText(ui.generationRules.value) ? "" : ui.generationRules.value;
      ui.generationRules.value = `${current}${current ? "\n\n" : ""}${text}`;
      await persistGenerationRules(file.name);
      ui.generationResult.textContent = `Regras extraídas de ${file.name} e salvas na coleção.`;
    } catch (error) {
      ui.generationResult.textContent = error.message;
      log(`Regras não importadas: ${error.message}`, "error", { code: "REGRAS_NAO_LIDAS" });
    }
  }

  function finalizeGeneratedQuestion(draft, subjectHint) {
    const question = Parser.reevaluateQuestion({
      ...draft,
      subjectHint: subjectHint || draft.theme || "",
      bodyHtml: Parser.textToHtml(draft.bodyText),
      expectedResponseHtml: Parser.textToHtml(draft.expectedResponseText || ""),
      alternatives: (draft.alternatives || []).map((alternative) => ({ ...alternative, html: Parser.textToHtml(alternative.plain) })),
      feedbackHtml: Parser.textToHtml(draft.feedbackText),
      referencesText: "",
      allocationAudit: { status: "unknown", score: 0, selectedDiscipline: "", subjectHint: subjectHint || draft.theme || "", reason: "Aguardando comparação com a disciplina do AvaliA.", matchedTerms: [], missingTerms: [] }
    }, { regenerateHtml: true });
    question.generatedFromKnowledgeBase = true;
    question.athusAudit = Athus.question(question, draft.generationRules);
    question.generationEvidence = draft.generationEvidence;
    question.curriculumEvidence = draft.curriculumEvidence;
    question.blueprintEvidence = draft.blueprintEvidence;
    question.generationFactFingerprint = draft.generationFactFingerprint;
    question.generationRules = draft.generationRules;
    question.generationAudit = draft.generationAudit;
    question.contextualDesign = draft.contextualDesign;
    question.alternativeFeedback = draft.alternativeFeedback;
    question.responseCriteria = draft.responseCriteria;
    question.studyTopics = draft.studyTopics;
    question.generationSignature = draft.generationSignature;
    question.reviewBlocks = Array.from(new Set([...(question.reviewBlocks || []), "Questão produzida pela extensão: leia a redação, os distratores e a evidência antes de autorizar."]));
    question.needsReview = true;
    question.autoApproved = false;
    return question;
  }

  function renderGenerationResult(result, kind) {
    const coverage = result.coverage || { requestedByUa: {}, producedByUa: {}, missingUas: [] };
    const uas = Object.keys(coverage.requestedByUa || {}).map((ua) => `UA${ua}: ${coverage.producedByUa?.[ua] || 0}/${coverage.requestedByUa[ua]}`);
    const failures = (result.rejected || []).slice(0, 12);
    const pipeline = result.pipeline || {};
    const athusIssues=result.athusAudit?.issues || [];
    ui.generationResult.className = `aab-generation-result aab-generation-${kind || "neutral"}`;
    ui.generationResult.innerHTML = `
      <strong>${escapeHtml(result.message || "Geração concluída.")}</strong>
      ${athusIssues.length ? `<ul>${athusIssues.slice(0,8).map(i=>`<li>${escapeHtml(i.message)}</li>`).join("")}</ul>` : ""}
      ${uas.length ? `<span><b>Cobertura:</b> ${escapeHtml(uas.join(" · "))}</span>` : ""}
      ${pipeline.version ? `<div class="aab-pipeline-summary"><span><b>${pipeline.safeFacts || 0}</b> trechos disponíveis</span><span><b>${pipeline.candidatesConsidered || 0}</b> possibilidades auditadas</span><span><b>${pipeline.candidatesApproved || 0}</b> aprovadas</span><span><b>${pipeline.candidatesRejected || 0}</b> recusadas</span></div>${pipeline.answerDistribution ? `<span><b>Gabaritos equilibrados:</b> A ${pipeline.answerDistribution.A || 0} · B ${pipeline.answerDistribution.B || 0} · C ${pipeline.answerDistribution.C || 0} · D ${pipeline.answerDistribution.D || 0}</span>` : ""}` : ""}
      ${failures.length ? `<details><summary>Ver ${result.rejected.length} motivo(s) de descarte</summary><ul>${failures.map((entry) => `<li><b>${escapeHtml(entry.source || "Base")}</b>: ${escapeHtml(entry.reason)}</li>`).join("")}</ul>${result.rejected.length > failures.length ? `<small>Exibindo os primeiros ${failures.length}; o total fica registrado no relatório do lote.</small>` : ""}</details>` : ""}`;
  }

  async function auditKnowledgeBase() {
    const collection = activeKnowledgeCollection();
    const scoped = scopedKnowledgeBase();
    if (app.running || app.knowledgeBusy || !scoped.documents.length) return;
    app.knowledgeBusy = true;
    setBaseProgress("neutral", `Reanalisando “${collection.name}”: funções, disciplina, bibliografias, objetivos, UAs e fatos seguros…`);
    renderKnowledgeBase();
    try {
      app.knowledgeBase = Knowledge.reanalyzeCollectionDocuments(app.knowledgeBase, collection.id).base;
      await persistKnowledgeBase();
      const audit = Curator.baseAudit(scopedKnowledgeBase());
      const integrity = Knowledge.integrityReport(app.knowledgeBase);
      const conflictNames = audit.conflicts.map((entry) => entry.name).slice(0, 3);
      const kind = audit.conflicts.length || !integrity.ok || integrity.warnings.length ? "warning" : "success";
      setBaseProgress(kind, `${audit.documents} arquivo(s) auditado(s): ${audit.safeFacts} fatos seguros, ${audit.objectives} objetivos, ${audit.modelQuestions} questões-modelo e ${audit.quarantineCount} trecho(s) em quarentena. Integridade do banco: ${integrity.score}%.${conflictNames.length ? ` Confirme a disciplina de: ${conflictNames.join("; ")}.` : integrity.warnings.length ? ` Atenção: ${integrity.warnings[0]}` : " Nenhum conflito impeditivo."}`);
      log(`Auditoria de ${collection.name} concluída: ${audit.safeFacts} fatos seguros; ${audit.quarantineCount} trechos isolados; ${audit.conflicts.length} conflitos; integridade ${integrity.score}%.`, kind, { code: "CURADORIA_CONCLUIDA" });
    } catch (error) {
      setBaseProgress("danger", `A auditoria não foi concluída: ${error.message}`);
      log(`Auditoria da biblioteca falhou: ${error.message}`, "error", { code: "CURADORIA_FALHOU" });
    } finally {
      app.knowledgeBusy = false;
      renderKnowledgeBase();
    }
  }

  function assessmentDownloadMetadata() {
    const questions = app.session?.parsed?.questions || [];
    const completion = app.session?.generationCompletion;
    return { athusRules: app.session?.generatedFromKnowledgeBase ? app.session.parsed.generationRules : null, assessment: questions[0]?.assessment || ui.generationEvaluation.value,
      subject: questions[0]?.theme || app.session?.parsed?.subjectHint,
      title: `Avaliação ${questions[0]?.assessment || "Athus"} — professor`,
      partial: completion?.status === "partial", requested: completion?.requested || questions.length };
  }

  async function downloadTeacherResource(kind) {
    const file=kind==="model"?"Modelo_Prova_SmartFox_11.0.docx":"Prompt_Prova_SmartFox_11.0.txt";
    const response=await fetch(chrome.runtime.getURL(`templates/${file}`));
    if(!response.ok)throw new Error("O material não pôde ser aberto. Recarregue a extensão e tente novamente.");
    const url=URL.createObjectURL(await response.blob()),anchor=document.createElement("a");
    anchor.href=url;anchor.download=file;document.body.appendChild(anchor);anchor.click();anchor.remove();
    window.setTimeout(()=>URL.revokeObjectURL(url),60000);
    modeStrip("success","Material pronto para download.",kind==="model"?"Substitua os exemplos pela sua avaliação antes de importar.":"Preencha os campos e use o prompt com os materiais da disciplina.");
  }

  async function downloadAssessmentPackage() {
    if (!app.session?.parsed?.questions?.length || app.running) return;
    const result = await StudentGuide.buildAssessmentPackage(app.session.parsed.questions, assessmentDownloadMetadata());
    const url = URL.createObjectURL(result.blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = result.fileName;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 60000);
    modeStrip("success", "Avaliação e guia prontos.", "O ZIP contém dois arquivos Word separados: professor e aluno.");
    log(`Pacote baixado: ${result.teacherFile} e ${result.studentFile}.`, "success", { code: "AVALIACAO_GUIA_EXPORTADOS" });
  }

  async function downloadGeneratedAssessment() {
    if (!app.session?.parsed?.questions?.length || app.running) {
      ui.generationResult.textContent = "Importe uma avaliação em Word antes de baixar o DOCX.";
      return;
    }
    try {
      const questions = app.session.parsed.questions;
      const fileName = await Exporter.download(questions, assessmentDownloadMetadata());
      log(`DOCX gerado e baixado: ${fileName}.`, "success", { code: "DOCX_GERADO" });
      modeStrip("success", "DOCX pronto.", `${questions.length} questão(ões) exportadas para revisão.`);
    } catch (error) {
      log(`Não foi possível gerar o DOCX: ${error.message}`, "error", { code: "DOCX_GERACAO_FALHOU" });
      window.alert(`Não foi possível criar o DOCX.\n\n${error.message}`);
    }
  }

  async function downloadStudentStudyGuide() {
    if (!app.session?.parsed?.questions?.length || app.running) {
      ui.generationResult.textContent = "Importe uma avaliação em Word com tema ou tópicos de estudo antes de baixar o roteiro dos alunos.";
      return;
    }
    try {
      const questions = app.session.parsed.questions;
      const result = await StudentGuide.download(questions, {
        assessment: questions[0]?.assessment || ui.generationEvaluation.value,
        subject: questions[0]?.theme || app.session.parsed.subjectHint
      });
      log(`Roteiro de estudos baixado: ${result.fileName}. Nenhuma questão ou resposta foi incluída.`, "success", { code: "ROTEIRO_ALUNO_GERADO" });
      modeStrip("success", "Roteiro do aluno pronto.", `${result.model.groups.length} unidade(s) organizadas em um DOCX seguro para compartilhamento.`);
    } catch (error) {
      log(`Não foi possível gerar o roteiro dos alunos: ${error.message}`, "error", { code: "ROTEIRO_ALUNO_FALHOU" });
      window.alert(`Não foi possível criar o roteiro de estudos.\n\n${error.message}`);
    }
  }

  function externalStatusLabel(status) {
    if (status === ExternalExam.status.ANSWERABLE) return "Respondível pela base";
    if (status === ExternalExam.status.REVIEW) return "Possível, requer conferência";
    if (status === ExternalExam.status.INVALID) return "Estrutura inválida";
    return "Não respondível com a base";
  }

  function resetExternalExam(options = {}) {
    app.externalExamReport = null;
    if (options.clearFile !== false && ui.externalExamFile) ui.externalExamFile.value = "";
    if (ui.externalExamStatus) ui.externalExamStatus.textContent = "Nenhuma prova externa analisada.";
    if (ui.externalExamResults) {
      ui.externalExamResults.hidden = true;
      ui.externalExamResults.innerHTML = "";
    }
    if (ui.downloadExternalReport) ui.downloadExternalReport.hidden = true;
    if (ui.clearExternalReport) ui.clearExternalReport.hidden = !(ui.externalExamFile?.files?.length);
  }

  function renderExternalExamReport() {
    const report = app.externalExamReport;
    if (!report) {
      ui.externalExamResults.hidden = true;
      ui.externalExamResults.innerHTML = "";
      ui.downloadExternalReport.hidden = true;
      return;
    }
    const summary = report.summary;
    const tone = report.complete ? "success" : report.possible ? "warning" : "danger";
    ui.externalExamStatus.className = `aab-external-status aab-external-${tone}`;
    ui.externalExamStatus.innerHTML = `<strong>${summary.answerable} respondível(is) · ${summary.review} para conferência · ${summary.insufficient} sem base · ${summary.invalid} inválida(s)</strong><span>${escapeHtml(report.notice)}</span>`;
    ui.externalExamResults.hidden = false;
    ui.externalExamResults.innerHTML = report.results.map((item) => {
      const answer = item.suggestedLetter
        ? `<div class="aab-external-answer"><span>Resposta sugerida</span><strong>${escapeHtml(item.suggestedLetter)}) ${escapeHtml(item.suggestedText)}</strong></div>`
        : item.suggestedText
          ? `<div class="aab-external-answer"><span>Resposta fundamentada para revisar</span><strong>${escapeHtml(item.suggestedText)}</strong></div>`
          : `<div class="aab-external-answer aab-external-no-answer"><span>Resposta</span><strong>Não foi possível determinar somente com esta coleção.</strong></div>`;
      const evidence = (item.evidence || []).slice(0, 3).map((entry) => `<li><strong>${escapeHtml(entry.documentName || "Material da coleção")}</strong><span>${escapeHtml(entry.excerpt || "")}</span></li>`).join("");
      const warnings = (item.warnings || []).slice(0, 4).map((warning) => `<li>${escapeHtml(warning)}</li>`).join("");
      return `<article class="aab-external-result" data-status="${escapeHtml(item.status)}">
        <header><div><span>Questão ${escapeHtml(item.number || item.ordinal)}</span><strong>${escapeHtml(externalStatusLabel(item.status))}</strong></div><b>${Math.round(Number(item.confidence || 0) * 100)}%</b></header>
        <p>${escapeHtml(item.bodyText || "Enunciado não reconhecido")}</p>
        ${answer}
        ${evidence ? `<details><summary>Ver evidências da disciplina</summary><ul class="aab-external-evidence">${evidence}</ul></details>` : ""}
        ${warnings ? `<details><summary>Alertas da análise</summary><ul class="aab-external-warnings">${warnings}</ul></details>` : ""}
      </article>`;
    }).join("");
    ui.downloadExternalReport.hidden = false;
    ui.clearExternalReport.hidden = false;
  }

  async function analyzeExternalExam() {
    if (app.running || app.knowledgeBusy) return;
    const file = ui.externalExamFile.files?.[0];
    if (!file) throw new Error("Selecione a prova externa em DOCX.");
    const collection = activeKnowledgeCollection();
    if (collection.id === Knowledge.defaultCollectionId || !collection.subject) {
      throw new Error("Escolha uma coleção específica com disciplina definida antes da análise.");
    }
    app.knowledgeBusy = true;
    ui.externalExamStatus.className = "aab-status aab-neutral";
    ui.externalExamStatus.textContent = `Lendo ${file.name} e consultando somente “${collection.name}”…`;
    renderKnowledgeBase();
    try {
      const parsed = await Parser.parse(file);
      assertWorkActive();
      const report = ExternalExam.analyze(parsed, scopedKnowledgeBase(), collection, Knowledge);
      app.externalExamReport = report;
      renderExternalExamReport();
      const summary = report.summary;
      const kind = report.complete ? "success" : report.possible ? "warning" : "error";
      log(`Prova externa analisada sem internet: ${summary.answerable} respondível(is), ${summary.review} para conferência, ${summary.insufficient} sem base e ${summary.invalid} inválida(s).`, kind, { code: "PROVA_EXTERNA_ANALISADA", collectionId: collection.id });
      modeStrip(report.complete ? "success" : "warning", "Análise local concluída.", `${summary.answerable + summary.review} de ${summary.total} questão(ões) possuem alguma sustentação na coleção ${collection.name}.`);
    } finally {
      app.knowledgeBusy = false;
      renderKnowledgeBase();
    }
  }

  async function downloadExternalExamReport() {
    if (!app.externalExamReport) throw new Error("Analise uma prova externa antes de baixar o relatório.");
    const fileName = await ExternalExam.download(app.externalExamReport);
    log(`Gabarito fundamentado da prova externa baixado: ${fileName}.`, "success", { code: "PROVA_EXTERNA_DOCX_GERADO" });
    modeStrip("success", "Relatório DOCX pronto.", "O arquivo registra respostas, confiança, evidências e itens sem base suficiente.");
  }

  async function generateQuestionsFromBase() {
    if (app.abandoning || app.knowledgeBusy || app.running) return;
    const collection = activeKnowledgeCollection();
    const stats = Knowledge.baseStats(app.knowledgeBase, collection.id);
    if (!stats.documents) {
      ui.generationResult.textContent = `Adicione materiais à coleção “${collection.name}” antes de produzir questões.`;
      return;
    }
    const controller = new AbortController();
    app.generationController = controller;
    app.knowledgeBusy = true;
    renderKnowledgeBase();
    try {
    await persistGenerationRules();
    assertWorkActive();
    const scope = scopedKnowledgeBase();
    const result = await Knowledge.generateQuestions(scope, ui.generationRules.value, {
      count: Number(ui.generationCount.value || 0),
      evaluation: collection.evaluation === "GENERAL" ? ui.generationEvaluation.value : collection.evaluation,
      theme: collection.subject || ui.generationTheme.value.trim(),
      uas: ui.generationUas.value.trim(),
      signal: controller.signal,
      onProgress: (message) => { if (!app.abandoning) ui.generationResult.textContent = message; },
      difficulty: ui.generationDifficulty.value
    });
    assertWorkActive();
    if (!result.questions.length) {
      renderGenerationResult(result, "warning");
      log(`Geração interrompida: ${result.message}`, "warning", { code: "BASE_SEM_FATOS_GERAVEIS" });
      return;
    }
    const approved = window.confirm(`${result.message}\n\nAs propostas substituirão o lote local atualmente aberto, mas nada no AvaliA será apagado ou enviado. Continuar?`);
    if (!approved) return;
    const subjectHint = result.rules.theme || collection.subject || scope.documents.map((document) => document.name.replace(/\.[^.]+$/, "")).slice(0, 3).join(" · ");
    const questions = result.questions.map((question) => finalizeGeneratedQuestion(question, subjectHint));
    app.knowledgeBase.generationHistory = [...(app.knowledgeBase.generationHistory || []), ...result.questions.map((question) => ({
      factFingerprint: question.generationFactFingerprint,
      questionSignature: question.generationSignature,
      contextSummary: question.bodyText.slice(0, 1800),
      at: new Date().toISOString(),
      evaluation: result.rules.evaluation,
      questionName: question.name,
      sourceDocumentId: question.generationEvidence.documentId,
      collectionId: collection.id
    }))].slice(-2000);
    app.knowledgeBase.updatedAt = new Date().toISOString();
    await persistKnowledgeBase();
    assertWorkActive();
    const parsed = Parser.summarizeParsed({
      parserVersion: `${PRODUCT_LABEL}-premium-generator`,
      fileName: `Questoes_geradas_${new Date().toISOString().slice(0, 10)}.docx`,
      subjectHint,
      questions,
      requiredAlternatives: REQUIRED_ALTERNATIVES,
      reviewThreshold: Parser.reviewThreshold,
      generatedFromKnowledgeBase: true,
      generationRules: result.rules,
      generationRejected: result.rejected
    });
    parsed.duplicateHistory = Duplicates.scan(app.duplicateLedger, {
      fileName: parsed.fileName,
      fileFingerprint: parsed.fileFingerprint,
      questions: parsed.questions
    });
    app.session = Engine.createSession(parsed, { fileName: parsed.fileName, outputMode: selectedMode(), fillKeywords: ui.keywords.checked, ...sessionTagOptions() });
    finishSessionTagSetup(app.session);
    app.session.fileRuleAuthorization = null;
    app.session.events = [];
    app.session.notifyWhenDone = ui.notify.checked;
    app.session.continueOnError = ui.continueErrors.checked;
    app.session.importedQuestions = JSON.parse(JSON.stringify(questions));
    app.session.generatedFromKnowledgeBase = true;
    app.session.generationCompletion = { status: result.status, requested: result.requested, produced: result.produced };
    app.session.knowledgeCollectionId = collection.id;
    app.session.knowledgeCollectionName = collection.name;
    app.session.knowledgeDocumentIds = scope.documents.map((document) => document.id);
    app.reviewIndex = 0;
    await saveSession();
    try {
      await registerImportedFile({ name: parsed.fileName }, parsed, app.session.runId);
    } catch (ledgerError) {
      log(`O histórico de duplicidades não pôde ser atualizado: ${ledgerError.message}`, "warning", { code: "DUPLICIDADE.HISTORICO_NAO_GRAVADO" });
    }
    await scanQuestionsWithBase({ silent: true });
    renderGenerationResult({ ...result, message: `${result.message} ${result.rejected.length} registro(s) de descarte ficaram disponíveis para auditoria.` }, result.status === "complete" ? "success" : "warning");
    app.currentView = "review";
    renderSession();
    modeStrip("warning", `${result.produced} propostas criadas.`, "Revise e aprove antes de executar.");
    log(`Geração fundamentada: ${result.produced} questão(ões) criadas e ${result.rejected.length} candidato(s) descartado(s).`, "success", { code: "QUESTOES_GERADAS" });
    } catch (error) {
      if (app.abandoning || error?.code === "WORK_ABANDONED") return;
      ui.generationResult.textContent = error.message || "A geração não foi concluída.";
      log(`Elaboração interrompida: ${error.message}`, "warning", { code: "GERACAO_LOCAL_INTERROMPIDA" });
    } finally {
      if (app.generationController === controller) app.generationController = null;
      app.knowledgeBusy = false;
      renderKnowledgeBase();
    }
  }

  function exportKnowledgeBackup() {
    const integrity = Knowledge.integrityReport(app.knowledgeBase);
    const payload = {
      product: PRODUCT_NAME,
      version: PRODUCT_VERSION,
      backupType: "complete-database",
      generatedAt: new Date().toISOString(),
      stats: Knowledge.baseStats(app.knowledgeBase),
      collectionStats: Knowledge.collectionStats(app.knowledgeBase),
      integrity,
      backupFingerprint: Knowledge.baseFingerprint(app.knowledgeBase),
      knowledgeBase: app.knowledgeBase,
      duplicateLedgerStats: Duplicates.stats(app.duplicateLedger),
      duplicateLedgerFingerprint: Duplicates.ledgerFingerprint(app.duplicateLedger),
      duplicateLedger: app.duplicateLedger
    };
    downloadJson(payload, `Backup_Banco_SmartFox_11_0_${new Date().toISOString().replace(/[:.]/g, "-")}.json`);
  }

  function exportActiveCollection() {
    const collection = activeKnowledgeCollection();
    const scope = scopedKnowledgeBase();
    const integrity = Knowledge.integrityReport(scope);
    const payload = {
      product: PRODUCT_NAME,
      version: PRODUCT_VERSION,
      backupType: "single-collection",
      generatedAt: new Date().toISOString(),
      collection: { ...collection },
      stats: Knowledge.baseStats(app.knowledgeBase, collection.id),
      integrity,
      backupFingerprint: Knowledge.baseFingerprint({ ...scope, collections: [{ ...collection }], activeCollectionId: collection.id }),
      knowledgeBase: {
        ...scope,
        collections: [{ ...collection }],
        activeCollectionId: collection.id
      }
    };
    downloadJson(payload, `Colecao_${collection.name.replace(/[^a-z0-9áàâãéèêíïóôõöúç_-]+/gi, "_")}_${new Date().toISOString().slice(0, 10)}.json`);
  }

  async function importKnowledgeBackup() {
    const file = ui.importBase.files?.[0];
    if (!file || app.running || app.knowledgeBusy) return;
    try {
      const payload = JSON.parse(await file.text());
      assertWorkActive();
      const rawBase = payload.knowledgeBase || payload;
      if (payload.backupFingerprint && Knowledge.baseFingerprint(rawBase) !== payload.backupFingerprint) throw new Error("A assinatura do backup não confere. O arquivo pode estar incompleto ou ter sido alterado.");
      const incomingLedger = payload.duplicateLedger ? Duplicates.hydrateLedger(payload.duplicateLedger) : null;
      if (incomingLedger && payload.duplicateLedgerFingerprint && Duplicates.ledgerFingerprint(incomingLedger) !== payload.duplicateLedgerFingerprint) throw new Error("A assinatura do histórico de duplicidades não confere.");
      const incoming = Knowledge.hydrateBase(rawBase);
      const integrity = Knowledge.integrityReport(incoming);
      if (!integrity.ok) throw new Error(`O banco contém falha estrutural: ${integrity.blocking[0]}`);
      const namedCollections = incoming.collections.filter((collection) => collection.id !== Knowledge.defaultCollectionId).length;
      const duplicateStats = incomingLedger ? Duplicates.stats(incomingLedger) : { files: 0, submissions: 0 };
      if (!incoming.documents.length && !namedCollections) throw new Error("O backup não contém coleções nem materiais reconhecíveis.");
      if (!window.confirm(`Importar ${namedCollections || 1} coleção(ões), ${incoming.documents.length} material(is) e ${duplicateStats.submissions} registro(s) antirrepetição?\n\nIntegridade do backup: ${integrity.score}%. Conteúdos equivalentes serão atualizados dentro da mesma avaliação e disciplina.`)) return;
      const merged = Knowledge.mergeBases(app.knowledgeBase, incoming);
      app.knowledgeBase = merged.base;
      await persistKnowledgeBase();
      const duplicateMerge = incomingLedger ? Duplicates.mergeLedgers(app.duplicateLedger, incomingLedger) : { ledger: app.duplicateLedger, filesAdded: 0, submissionsAdded: 0 };
      app.duplicateLedger = duplicateMerge.ledger;
      if (incomingLedger) await persistDuplicateLedger();
      applyCollectionDefaults();
      ui.importBase.value = "";
      renderKnowledgeBase();
      if (app.session) await scanQuestionsWithBase({ silent: false });
      setBaseProgress("success", `Backup importado: ${merged.collectionsAdded} coleção(ões) nova(s), ${merged.documentsAdded} material(is) novo(s), ${merged.documentsReplaced} atualizado(s) e ${duplicateMerge.submissionsAdded} envio(s) acrescentado(s) ao histórico antirrepetição.`);
      log(`Backup do acervo importado: ${merged.collectionsAdded} coleção(ões), ${merged.documentsAdded} material(is) e ${duplicateMerge.submissionsAdded} envio(s) antirrepetição acrescentados.`, "success", { code: "BASE_BACKUP_IMPORTADO" });
    } catch (error) {
      ui.importBase.value = "";
      setBaseProgress("danger", `Backup inválido: ${error.message}`);
      log(`Backup da base recusado: ${error.message}`, "error", { code: "BASE_BACKUP_INVALIDO" });
    }
  }

  function comparableText(value) {
    return String(value == null ? "" : value).normalize("NFC").replace(/\u00a0/g, " ").replace(/\s+/g, " ").trim();
  }

  function editedFieldHtml(originalHtml, originalText, editedText, fieldLabel) {
    if (comparableText(originalText) === comparableText(editedText)) return originalHtml || Parser.textToHtml(editedText);
    if (/<img\b|data-aab-formula=|<(?:sup|sub)\b/i.test(String(originalHtml || ""))) {
      throw new Error(`O campo “${fieldLabel}” contém imagem, fórmula ou sobrescrito. Para manter a construção exatamente igual, edite esse conteúdo no Word e importe novamente; alterações apenas nos outros campos continuam permitidas.`);
    }
    return Parser.textToHtml(editedText);
  }

  function editedQuestion(redetect) {
    const original = reviewQuestion();
    if (!original) throw new Error("Nenhuma questão selecionada.");
    const typeId = ui.editType.value;
    const selectedType = Parser.typeCatalog.find((type) => type.id === typeId);
    const discursive = selectedType?.key === "discursive" || typeId === "158";
    const cognitiveId = ui.editCognitive.value;
    const selectedCognitive = Parser.cognitiveCatalog.find((level) => level.id === cognitiveId);
    const updated = {
      ...original,
      name: original.generatedFromKnowledgeBase ? `Questão (${original.number})_${original.assessment}_UA (${ui.editUa.value})_Obj (${ui.editObjectiveNumber.value})_${ui.editDifficulty.value}${discursive ? '_Discursiva' : ''}` : ui.editName.value.replace(/_Discursiva$/i, '') + (discursive ? '_Discursiva' : ''),
      theme: ui.editTheme.value.trim(), objective: ui.editObjective.value.trim(), ua: ui.editUa.value,
      objectiveNumber: ui.editObjectiveNumber.value, difficulty: ui.editDifficulty.value,
      athusObjectiveConfirmed: ui.editObjectiveConfirm.checked, athusReview: null,
      bodyText: ui.editBody.value,
      questionFormat: discursive ? "discursive" : "objective",
      expectedResponseText: discursive ? ui.editExpectedResponse.value : "",
      expectedResponseHtml: discursive
        ? editedFieldHtml(original.expectedResponseHtml, original.expectedResponseText, ui.editExpectedResponse.value, "Padrão de resposta discursiva")
        : "",
      alternatives: discursive ? [] : ui.editAlternatives.map((field, index) => ({
        ...original.alternatives[index],
        letter: "ABCD"[index],
        plain: field.value,
        html: editedFieldHtml(original.alternatives[index]?.html, original.alternatives[index]?.plain, field.value, `Alternativa ${"ABCD"[index]}`)
      })),
      correctLetter: discursive ? "" : ui.editAnswer.value,
      correctIndex: discursive ? -1 : "ABCD".indexOf(ui.editAnswer.value),
      feedbackText: ui.editFeedback.value,
      typeId,
      typeLabel: selectedType?.label || original.typeLabel,
      typeDescription: ui.editSkill.value.trim() || (redetect ? "" : (selectedType?.label || original.typeDescription)),
      cognitiveId,
      cognitiveLabel: selectedCognitive?.label || original.cognitiveLabel,
      bodyHtml: editedFieldHtml(original.bodyHtml, original.bodyText, ui.editBody.value, "Enunciado"),
      feedbackHtml: editedFieldHtml(original.feedbackHtml, original.feedbackText, ui.editFeedback.value, "Feedback")
    };
    return Parser.reevaluateQuestion(updated, { regenerateHtml: false, preserveType: !redetect, preserveCognitive: true });
  }

  async function insertSelectedImage() {
    const question = reviewQuestion();
    const item = reviewItem();
    const file = ui.imageFile.files?.[0];
    if (!question || !item || item.phase !== P.PENDING || app.running) return;
    if (!file) {
      setSiteStatus("warning", "Escolha uma imagem antes de clicar em Inserir.");
      return;
    }
    const allowed = /^(?:image\/(?:png|jpeg|gif|webp|svg\+xml|bmp))$/i;
    if (!allowed.test(file.type || "") || file.size > 12 * 1024 * 1024) {
      setSiteStatus("danger", "Use PNG, JPEG, GIF, WebP, SVG ou BMP com no máximo 12 MB.");
      return;
    }
    try {
      const dataUrl = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(String(reader.result || ""));
        reader.onerror = () => reject(new Error("A imagem não pôde ser lida."));
        reader.readAsDataURL(file);
      });
      const hash = Engine.fnv1a(dataUrl.split(",")[1] || dataUrl);
      const alt = `AABIMG:${hash}:${file.name || "Imagem adicionada"}`;
      const imageHtml = `<p><img src="${dataUrl}" alt="${escapeHtml(alt)}" data-aab-image="${hash}" data-aab-source="manual" style="max-width:100%;height:auto"></p>`;
      const updated = JSON.parse(JSON.stringify(question));
      const target = ui.imageTarget.value;
      if (target === "body") updated.bodyHtml = `${updated.bodyHtml || Parser.textToHtml(updated.bodyText)}${imageHtml}`;
      else if (target === "expectedResponse") {
        if (updated.questionFormat !== "discursive") throw new Error("O padrão de resposta só existe em questões discursivas.");
        updated.expectedResponseHtml = `${updated.expectedResponseHtml || Parser.textToHtml(updated.expectedResponseText)}${imageHtml}`;
      }
      else if (target === "feedback") updated.feedbackHtml = `${updated.feedbackHtml || Parser.textToHtml(updated.feedbackText)}${imageHtml}`;
      else {
        const index = "ABCD".indexOf(target);
        if (index < 0 || !updated.alternatives[index]) throw new Error("Destino da imagem inválido.");
        updated.alternatives[index].html = `${updated.alternatives[index].html || Parser.textToHtml(updated.alternatives[index].plain)}${imageHtml}`;
      }
      updated.media = [...(updated.media || []), { relationshipId: `manual-${hash}`, name: file.name, mime: file.type, size: file.size, hash, resolved: true, supported: true, source: "manual", dataUrl }];
      const reviewed = Parser.reevaluateQuestion(updated, { preserveType: true, preserveCognitive: true });
      Engine.updatePendingQuestion(app.session, app.reviewIndex, reviewed);
      if (app.lastDisciplines.length) reviewed.allocationAudit = Parser.assessAllocation(reviewed, app.lastDisciplines, app.session.parsed.subjectHint || reviewed.subjectHint);
      Parser.summarizeParsed(app.session.parsed);
      await saveSession();
      ui.imageFile.value = "";
      renderSession();
      log(`Questão ${reviewed.number}: imagem “${file.name}” inserida em ${target === "body" ? "enunciado" : target === "expectedResponse" ? "padrão de resposta" : target === "feedback" ? "feedback" : `alternativa ${target}`}; assinatura ${hash} registrada.`, "success");
    } catch (error) {
      setSiteStatus("danger", error.message);
      log(`Imagem não inserida: ${error.message}`, "error");
    }
  }

  async function removeLastInsertedImage() {
    const question = reviewQuestion();
    const item = reviewItem();
    if (!question || !item || item.phase !== P.PENDING || app.running) return;
    const manual = (question.media || []).filter((entry) => entry.source === "manual" || String(entry.relationshipId || "").startsWith("manual-"));
    const selected = manual[manual.length - 1];
    if (!selected?.hash) return;
    try {
      const updated = JSON.parse(JSON.stringify(question));
      const expression = new RegExp(`<img\\b(?=[^>]*data-aab-image=["']${selected.hash}["'])[^>]*>`, "gi");
      const clean = (html) => String(html || "").replace(expression, "").replace(/<p\b[^>]*>\s*<\/p>/gi, "");
      updated.bodyHtml = clean(updated.bodyHtml);
      updated.expectedResponseHtml = clean(updated.expectedResponseHtml);
      updated.feedbackHtml = clean(updated.feedbackHtml);
      updated.alternatives.forEach((alternative) => { alternative.html = clean(alternative.html); });
      updated.media = (updated.media || []).filter((entry) => entry.hash !== selected.hash || !(entry.source === "manual" || String(entry.relationshipId || "").startsWith("manual-")));
      const reviewed = Parser.reevaluateQuestion(updated, { preserveType: true, preserveCognitive: true });
      Engine.updatePendingQuestion(app.session, app.reviewIndex, reviewed);
      if (app.lastDisciplines.length) reviewed.allocationAudit = Parser.assessAllocation(reviewed, app.lastDisciplines, app.session.parsed.subjectHint || reviewed.subjectHint);
      Parser.summarizeParsed(app.session.parsed);
      await saveSession();
      renderSession();
      log(`Questão ${reviewed.number}: última imagem adicionada (${selected.name || selected.hash}) removida.`, "info");
    } catch (error) {
      setSiteStatus("danger", error.message);
    }
  }

  async function checkAllocationNow() {
    const diagnosis = await refreshSiteStatus(true);
    if (!diagnosis.state?.disciplines?.length) {
      setSiteStatus("warning", "Adicione a disciplina no Passo 3 e tente novamente.");
      return;
    }
    const issues = app.session.parsed.questions.filter((question, index) => allocationRequiresApproval(question, index)).length;
    renderSession();
    log(`Conferência de matéria atualizada: ${app.session.parsed.questions.length} questão(ões) comparadas com ${diagnosis.state.disciplines.length} disciplina(s); ${issues} aguardam decisão do professor.`, issues ? "warning" : "success");
  }

  function planBatchReview(session, disciplines) {
    const candidates = [], blocked = [];
    const scope = allocationScope(disciplines);
    session.parsed.questions.forEach((question, index) => {
      const item = session.items[index];
      if (item?.phase !== P.PENDING) return;
      if (!question.executable || question.hardErrors?.length) {
        blocked.push({ index, number: question.number, reason: question.hardErrors?.join(" ") || "Campos obrigatórios incompletos." });
        return;
      }
      if (question.generatedFromKnowledgeBase) {
        const report = Athus.question(question, session.parsed.generationRules);
        if (!report.ok) {
          blocked.push({ index, number: question.number, reason: report.issues.map(issue => issue.message).join(" ") });
          return;
        }
      }
      const audit = Parser.assessAllocation(question, disciplines, session.parsed.subjectHint || question.subjectHint);
      const quality = !item.manualAuthorizedAt || (question.generatedFromKnowledgeBase && question.athusReview?.fingerprint !== Athus.fingerprint(question));
      const allocation = !item.allocationAuthorizedAt || question.allocationAudit?.selectedDiscipline !== audit.selectedDiscipline || (item.allocationAuthorizationScope && item.allocationAuthorizationScope !== scope);
      const knowledge = question.knowledgeAudit && !["no_base", "supported"].includes(question.knowledgeAudit.status) && !item.knowledgeDecision;
      if (quality || allocation || knowledge) candidates.push({ index, audit, quality, allocation, knowledge });
    });
    return { candidates, blocked, scope };
  }

  async function approveAllReviews() {
    const session = app.session;
    if (!session?.parsed?.questions?.length || app.running || app.approvalRunning || app.batchReviewBusy || app.abandoning || app.fileImportBusy || app.fileRemovalBusy || app.knowledgeBusy) return;
    // This action is tracked by safeUiAction; let any earlier edit/import settle first.
    if (workTasks.size > 1) throw new Error("Aguarde a operação em andamento e tente aprovar o lote novamente.");
    app.batchReviewBusy = true;
    renderControls();
    let updated = null, persisted = false;
    try {
      const state = await bridge("getState", {}, 10000);
      assertWorkActive();
      if (app.session !== session || app.running) throw new Error("O lote mudou. Confira o lote atual antes de aprovar.");
      if (!state?.supportedPage || !state.formReady || state.loginDetected) throw new Error("Abra o formulário do AvaliA com sua sessão ativa antes de aprovar a alocação.");
      const disciplines = (state.disciplines || []).map(value => String(value).trim()).filter(Boolean);
      if (!disciplines.length) throw new Error("Selecione a disciplina no Passo 3 do AvaliA antes de aprovar o lote.");
      const plan = planBatchReview(session, disciplines);
      const fileReviews = fileRuleAuthorizationValid() ? [] : pendingFileRuleReviews();
      if (!plan.candidates.length && !fileReviews.length) {
        modeStrip(plan.blocked.length ? "warning" : "success", plan.blocked.length ? "Há questões que precisam de correção." : "Lote já aprovado.",
          plan.blocked.length ? plan.blocked.map(item => `Questão ${item.number}: ${item.reason}`).join("\n") : "As decisões de revisão e alocação já estão registradas.");
        return;
      }
      const fileSummary = fileReviews.length ? `\n\nTambém serão aprovadas ${fileReviews.length} regra(s) geral(is) do arquivo:\n${fileReviews.map(issue => `• ${issue.title}: ${issue.message}`).join("\n")}` : "";
      const omitted = plan.blocked.length ? `\n\n${plan.blocked.length} questão(ões) continuarão pendentes: ${plan.blocked.map(item => item.number).join(", ")}. Precisam de correção dos campos obrigatórios ou das regras Athus.` : "";
      if (!window.confirm(`Aprovar ${plan.candidates.length} questão(ões) do lote e manter a alocação nas disciplinas abaixo?\n\n${disciplines.join("\n")}\n\nSua decisão abrange as questões fora do filtro atual, aprova a revisão de qualidade e mantém o conteúdo e o gabarito apesar dos alertas de compatibilidade ou da conferência com os materiais. A decisão ficará registrada em cada questão.${fileSummary}${omitted}\n\nApós aprovar, use Iniciar para enviar o lote.`)) return;
      assertWorkActive();
      // Prepare all decisions on a copy; persist once and restore on storage failure.
      updated = JSON.parse(JSON.stringify(session));
      for (const candidate of plan.candidates) {
        const { index, audit } = candidate;
        const question = updated.parsed.questions[index];
        question.allocationAudit = audit;
        if (candidate.quality) {
          if (question.generatedFromKnowledgeBase) question.athusReview = { fingerprint: Athus.fingerprint(question), at: new Date().toISOString() };
          Engine.authorizeQuestion(updated, index, "Professor aprovou a revisão de qualidade em lote, mantendo enunciado, alternativas, gabarito e feedback.");
        }
        if (candidate.allocation) {
          Engine.authorizeAllocation(updated, index, `Professor aprovou em lote a alocação nas disciplinas “${disciplines.join("; ")}”. Comparação textual: ${audit.score}% com “${audit.selectedDiscipline}”. ${audit.reason}`);
          updated.items[index].allocationAuthorizationScope = plan.scope;
        }
        if (candidate.knowledge) Engine.recordKnowledgeDecision(updated, index, "kept", `Conteúdo e gabarito mantidos pelo professor na aprovação em lote: ${question.knowledgeAudit.warnings?.join(" ") || question.knowledgeAudit.status}.`);
      }
      if (fileReviews.length) updated.fileRuleAuthorization = {
        at: new Date().toISOString(),
        fileFingerprint: updated.fileFingerprint,
        codes: Array.from(new Set(fileReviews.map(issue => issue.code))).sort(),
        note: "Exceções gerais lidas e aprovadas pelo professor na aprovação do lote."
      };
      updated.disciplineSnapshot = disciplines;
      updated.allocationAuditAt = new Date().toISOString();
      app.session = updated;
      await saveSession();
      persisted = true;
      assertWorkActive();
      app.lastDisciplines = disciplines;
      renderSession();
      const pending = plan.blocked.length ? ` ${plan.blocked.length} questão(ões) ainda precisam de correção.` : " Use Iniciar para prosseguir com o envio.";
      modeStrip(plan.blocked.length ? "warning" : "success", `${plan.candidates.length} questão(ões) aprovadas; ${fileReviews.length} regra(s) geral(is) aprovadas.`, `A decisão foi salva no lote.${pending}`);
      log(`${plan.candidates.length} questão(ões) aprovadas em lote; alocação mantida em “${disciplines.join("; ")}”.${pending}`, plan.blocked.length ? "warning" : "success", { code: "REVISAO_LOTE_APROVADA" });
    } catch (error) {
      if (!persisted && updated && app.session === updated) app.session = session;
      throw error;
    } finally {
      app.batchReviewBusy = false;
      if (!app.abandoning) renderSession();
    }
  }

  async function approveSelectedAllocation() {
    const question = reviewQuestion();
    const audit = question?.allocationAudit;
    if (!question || !audit || !["review", "inconsistent"].includes(audit.status)) return;
    const approved = window.confirm(`A extensão encontrou ${audit.score}% de compatibilidade com:\n\n${audit.selectedDiscipline}\n\n${audit.reason}\n\nAprovar conscientemente esta alocação? A decisão ficará no relatório.`);
    if (!approved) return;
    try {
      Engine.authorizeAllocation(app.session, app.reviewIndex, `Professor aprovou a alocação em “${audit.selectedDiscipline}” apesar do alerta de ${audit.score}%: ${audit.reason}`);
      reviewItem().allocationAuthorizationScope = allocationScope(app.lastDisciplines);
      await saveSession();
      renderSession();
      log(`Questão ${question.number}: correspondência com “${audit.selectedDiscipline}” aprovada pelo professor (${audit.score}%).`, "success");
    } catch (error) {
      setSiteStatus("danger", error.message);
    }
  }

  async function revokeSelectedAllocation() {
    const question = reviewQuestion();
    try {
      Engine.revokeAllocationAuthorization(app.session, app.reviewIndex);
      await saveSession();
      renderSession();
      log(`Questão ${question?.number || "—"}: aprovação da matéria revogada.`, "warning");
    } catch (error) {
      setSiteStatus("danger", error.message);
    }
  }

  function refreshKnowledgeForQuestion(question, index) {
    question.knowledgeAudit = Knowledge.analyzeQuestion(question, scopedKnowledgeBase());
    const item = app.session.items[index];
    if (question.knowledgeAudit.status === "supported" && item?.phase === P.PENDING) {
      item.knowledgeDecision = "accepted";
      item.knowledgeReviewedAt = question.knowledgeAudit.analyzedAt;
      item.knowledgeReviewNote = "Gabarito sustentado automaticamente pela base consultada.";
    }
    return question.knowledgeAudit;
  }

  async function applyKnowledgeCorrectionAt(index, options) {
    const question = app.session?.parsed?.questions?.[index];
    const item = app.session?.items?.[index];
    const audit = question?.knowledgeAudit;
    if (!question || !item || item.phase !== P.PENDING || audit?.suggestedIndex == null || audit.agreement !== false || Number(audit.confidence || 0) < 0.65 || !audit.feedbackSuggestion) return false;
    if (!options?.batch) {
      const approved = window.confirm(`Aplicar a sugestão fundamentada na questão ${question.number}?\n\nGabarito: ${question.correctLetter} → ${audit.suggestedLetter}\nConfiança: ${Math.round(audit.confidence * 100)}%\n\nO gabarito e o feedback serão atualizados; enunciado e alternativas serão preservados.`);
      if (!approved) return false;
    }
    const original = { correctLetter: question.correctLetter, correctIndex: question.correctIndex, feedbackText: question.feedbackText, feedbackHtml: question.feedbackHtml };
    let updated = JSON.parse(JSON.stringify(question));
    updated.correctIndex = audit.suggestedIndex;
    updated.correctLetter = audit.suggestedLetter;
    if (audit.feedbackSuggestion) {
      updated.feedbackText = audit.feedbackSuggestion;
      updated.feedbackHtml = Parser.textToHtml(audit.feedbackSuggestion);
    }
    updated = Parser.reevaluateQuestion(updated, { preserveType: true, preserveCognitive: true });
    updated.knowledgeAudit = Knowledge.analyzeQuestion(updated, scopedKnowledgeBase());
    Engine.updatePendingQuestion(app.session, index, updated);
    Engine.recordKnowledgeDecision(app.session, index, "corrected", `Gabarito alterado de ${original.correctLetter} para ${updated.correctLetter} com ${Math.round(audit.confidence * 100)}% de confiança.`, {
      original,
      applied: { correctLetter: updated.correctLetter, correctIndex: updated.correctIndex, feedbackText: updated.feedbackText },
      confidence: audit.confidence,
      evidence: audit.evidence,
      baseUpdatedAt: app.knowledgeBase.updatedAt
    });
    Parser.summarizeParsed(app.session.parsed);
    if (!options?.deferSave) {
      await saveSession();
      renderSession();
    }
    if (!options?.silent) log(`Questão ${updated.number}: gabarito ${original.correctLetter} → ${updated.correctLetter} e feedback corrigidos com evidência da base.`, "success", { code: "CORRECAO_FUNDAMENTADA" });
    return true;
  }

  async function applySelectedKnowledgeCorrection() {
    await applyKnowledgeCorrectionAt(app.reviewIndex, {});
  }

  async function keepSelectedKnowledge() {
    const question = reviewQuestion();
    const audit = question?.knowledgeAudit;
    if (!question || !audit || app.running) return;
    const approved = window.confirm(`Manter a questão ${question.number} como está, apesar da conferência com a base? A decisão e as evidências ficarão no relatório.`);
    if (!approved) return;
    try {
      Engine.recordKnowledgeDecision(app.session, app.reviewIndex, "kept", `Conteúdo mantido pelo professor após conferência: ${audit.warnings?.join(" ") || audit.status}.`);
      await saveSession();
      renderSession();
      log(`Questão ${question.number}: conteúdo mantido após conferência com a base.`, "warning", { code: "BASE_DECISAO_MANTER" });
      goToNextIssue();
    } catch (error) {
      setSiteStatus("danger", error.message);
    }
  }

  async function revokeSelectedKnowledge() {
    const question = reviewQuestion();
    try {
      Engine.revokeKnowledgeDecision(app.session, app.reviewIndex);
      await saveSession();
      renderSession();
      log(`Questão ${question?.number || "—"}: decisão bibliográfica reaberta.`, "info", { code: "BASE_DECISAO_REABERTA" });
    } catch (error) {
      setSiteStatus("danger", error.message);
    }
  }

  async function applyAllHighConfidenceCorrections() {
    if (!app.session || app.running) return;
    const candidates = app.session.parsed.questions.map((question, index) => ({ question, index, item: app.session.items[index] }))
      .filter(({ question, item }) => item.phase === P.PENDING && question.knowledgeAudit?.status === "mismatch" && Number(question.knowledgeAudit.confidence || 0) >= 0.9 && Boolean(question.knowledgeAudit.feedbackSuggestion));
    if (!candidates.length) {
      modeStrip("neutral", "Nenhuma correção automática segura.", "As demais decisões precisam de leitura individual.");
      return;
    }
    if (!window.confirm(`Aplicar ${candidates.length} correção(ões) de gabarito com confiança de pelo menos 90%? Cada alteração ficará registrada e poderá ser revisada antes do envio.`)) return;
    let applied = 0;
    for (const candidate of candidates) if (await applyKnowledgeCorrectionAt(candidate.index, { batch: true, deferSave: true, silent: true })) applied += 1;
    await saveSession();
    renderSession();
    log(`${applied} correção(ões) bibliográfica(s) de alta confiança aplicadas e registradas.`, "success", { code: "CORRECOES_SEGURAS_EM_LOTE" });
    modeStrip("success", `${applied} correção(ões) aplicadas.`, "Confira as questões antes de executar.");
  }

  async function applyQuestionEdit(redetect) {
    if (!app.session || app.running) return;
    try {
      const updated = editedQuestion(Boolean(redetect));
      Engine.updatePendingQuestion(app.session, app.reviewIndex, updated);
      if (app.lastDisciplines.length) updated.allocationAudit = Parser.assessAllocation(updated, app.lastDisciplines, app.session.parsed.subjectHint || updated.subjectHint);
      refreshKnowledgeForQuestion(updated, app.reviewIndex);
      Parser.summarizeParsed(app.session.parsed);
      await saveSession();
      renderSession();
      modeStrip(updated.executable ? (updated.needsReview ? "warning" : "success") : "danger", "Questão reanalisada.", updated.executable ? "Confira os novos resultados." : "Ainda existem campos obrigatórios.");
      log(`Questão ${updated.number}: alterações aplicadas e auditoria refeita${redetect ? " com nova autodetecção" : ""}.`, updated.executable ? "success" : "warning");
    } catch (error) {
      setSiteStatus("danger", error.message);
      log(`Edição não aplicada: ${error.message}`, "error");
    }
  }

  async function restoreImportedQuestion() {
    if (!app.session || app.running) return;
    const imported = app.session.importedQuestions?.[app.reviewIndex];
    if (!imported) return;
    const approved = window.confirm("Restaurar esta questão exatamente como foi interpretada na importação inicial? As edições atuais serão substituídas.");
    if (!approved) return;
    try {
      const restored = Parser.reevaluateQuestion(imported, {});
      Engine.updatePendingQuestion(app.session, app.reviewIndex, restored);
      if (app.lastDisciplines.length) restored.allocationAudit = Parser.assessAllocation(restored, app.lastDisciplines, app.session.parsed.subjectHint || restored.subjectHint);
      refreshKnowledgeForQuestion(restored, app.reviewIndex);
      Parser.summarizeParsed(app.session.parsed);
      await saveSession();
      renderSession();
      log(`Questão ${restored.number}: interpretação original restaurada.`, "success");
    } catch (error) {
      setSiteStatus("danger", error.message);
    }
  }

  async function authorizeSelected() {
    const question = reviewQuestion();
    if (!question || !ui.manualConfirm.checked) return;
    try {
      if (question.generatedFromKnowledgeBase) {
        const report=Athus.question(question,app.session.parsed.generationRules);
        if(!report.ok) throw new Error(report.issues.map(i=>i.message).join("\n"));
        question.athusReview={fingerprint:Athus.fingerprint(question),at:new Date().toISOString()};
      }
      Engine.authorizeQuestion(app.session, app.reviewIndex, `Revisada e autorizada manualmente com ${question.reviewBlocks.length} alerta(s) e ${question.warnings.length} observação(ões).`);
      await saveSession();
      renderSession();
      modeStrip("success", `Questão ${question.number} autorizada.`, "A decisão ficou registrada no relatório.");
      log(`Questão ${question.number}: autorizada manualmente após leitura.`, "success");
      if (startEligibility().ready) modeStrip("success", "Lote liberado.", "Todas as questões estão prontas para iniciar.");
      else goToNextIssue();
    } catch (error) {
      setSiteStatus("danger", error.message);
      log(error.message, "error");
    }
  }

  async function revokeSelected() {
    try {
      const question = reviewQuestion();
      if(question) delete question.athusReview;
      Engine.revokeAuthorization(app.session, app.reviewIndex);
      await saveSession();
      renderSession();
      log(`Questão ${question.number}: autorização manual revogada.`, "warning");
    } catch (error) {
      setSiteStatus("danger", error.message);
    }
  }

  function goToNextIssue() {
    const questions = app.session?.parsed?.questions || [];
    if (!questions.length) return;
    const previousFilter = app.reviewFilter;
    app.reviewFilter = "action";
    ui.filter.value = "action";
    const next = firstMatchingIndex(app.reviewIndex + 1);
    const status = questionStatus(questions[next], next).key;
    if (status !== "blocked" && status !== "review") {
      app.reviewFilter = previousFilter;
      ui.filter.value = previousFilter;
      modeStrip("success", "Revisão concluída.", "Não há outras pendências no arquivo.");
      return;
    }
    renderQuestion(next);
  }

  function moveReview(direction) {
    const questions = app.session?.parsed?.questions || [];
    if (!questions.length) return;
    app.reviewIndex = firstMatchingIndex(app.reviewIndex + direction);
    renderQuestion(app.reviewIndex);
  }

  function pageStatusMessage(state, item) {
    if (state.loginDetected) return "[AVALIA_SESSAO_EXPIRADA] Entre novamente no AvaliA e repita o teste de perfil.";
    if (!state.supportedPage) return "Para cadastrar questões, abra Ferramentas → Elaborador. Na tela azul você pode usar os bancos, corrigir e consultar relatórios.";
    if (!state.formReady) return "Abra Elabore Novas Questões e configure a avaliação.";
    if (!state.institutionId && state.institutionName) return `[VINCULO_INSTITUCIONAL_INCOMPLETO] O AvaliA mostra “${state.institutionName}”, mas não registrou o identificador da instituição. Repita o Passo 1 ou solicite a correção do vínculo do perfil.`;
    if (!state.sourceId && (state.activeSource || state.activeSourceId)) return "[VINCULO_FONTE_INCOMPLETO] A fonte aparece selecionada, mas o identificador interno está vazio. Repita o Passo 1 ou solicite a correção do perfil.";
    if (!state.sourceId || !state.institutionId) return "Confirme a fonte IES e a instituição no Passo 1.";
    if (!state.disciplines.length) return "Adicione pelo menos uma disciplina no Passo 3.";
    if (state.currentStep === "step-4" && !state.editorsReady) return "[EDITORES_NAO_INICIALIZADOS] Os editores do AvaliA ainda não terminaram de carregar.";
    const saved = item && [P.SAVING, P.DRAFT_SAVED, P.PREPARING, P.READY_TO_SUBMIT, P.SUBMITTING, P.NEEDS_VERIFICATION, P.SUBMITTED].includes(item.phase);
    if (saved && item.draftId && String(item.draftId) !== String(state.questionId || "")) return `A tela mostra a questão ${state.questionId || "sem ID"}, mas a sessão espera ${item.draftId}.`;
    if (!saved && state.currentStep !== "step-4") return `O preenchimento começa no Passo 4; a tela está em ${state.currentStep || "outra etapa"}.`;
    return "O formulário ainda não está pronto para esta fase.";
  }

  async function ensureBlankForm() {
    let state = await bridge("getState", {}, 10000);
    const item = Engine.currentItem(app.session);
    const saved = item && [P.SAVING, P.DRAFT_SAVED, P.PREPARING, P.READY_TO_SUBMIT, P.SUBMITTING, P.NEEDS_VERIFICATION, P.SUBMITTED].includes(item.phase);
    if (saved && item.draftId && String(item.draftId) === String(state.questionId || "")) return state;
    if (state.formReady && state.currentStep === "step-4" && state.editorsReady && state.sourceId && state.institutionId && state.disciplines.length && (!state.questionId || state.questionId === "0")) return state;
    if (state.formReady && /^step-[1-3]$/.test(state.currentStep)) throw new Error(pageStatusMessage(state, item));
    const previous = app.session.results[app.session.results.length - 1];
    if (state.questionId && previous && String(previous.id) === String(state.questionId)) {
      log(`Preparando a próxima tela após a questão ${previous.id}...`, "info");
      state = await bridge("resetForNext", {}, 40000);
      if (state.currentStep === "step-4" && state.editorsReady && state.sourceId && state.institutionId && state.disciplines.length && (!state.questionId || state.questionId === "0")) return state;
    }
    throw new Error(pageStatusMessage(state, item));
  }

  async function checkpoint(phase, patch) {
    Engine.transition(app.session, phase, patch);
    await saveSession();
    if (phase === P.SUBMITTED && app.session.bankCleanupEnabled) {
      try {
        const item=Engine.currentItem(app.session);
        await window.SmartFoxBankManager.enqueue({runId:app.session.runId,questionId:item.draftId,records:item.bankCleanupTargets||app.session.bankCleanupTargets,expectedOwner:app.session.bankCleanupOwner});
      } catch(error) { log(`Envio confirmado. Não foi possível agendar a limpeza de likes: ${error.message}`, "warning"); }
    }
    renderProgress();
  }

  function safeRepairable(error) {
    return /\[(?:DIVERGENCIA_DE_CAMPO|EDITORES_NAO_INICIALIZADOS|SEM_RESPOSTA|AVALIA_SERVIDOR|AVALIA_REDE|AVALIA_OCUPADO)\]|quatro alternativas/i.test(error?.message || "");
  }

  async function recoverWorkspaceForItem(item, silent) {
    if (!item) return { recovered: false, actions: [] };
    const result = await bridge("recoverStalledWorkspace", { phase: item.phase, expectedDraftId: item.draftId || "" }, 65000);
    if (result.actions?.length && !silent) result.actions.forEach((action) => log(`Recuperação da questão ${item.number}: ${action}`, "info"));
    if (result.diagnosis) renderDiagnosis(result.diagnosis);
    return result;
  }

  async function fillAndVerify(question, allowRepair) {
    try {
      await bridge("fillQuestion", { question, fillKeywords: app.session.fillKeywords }, 50000);
      return await bridge("verifyCurrentQuestion", { question }, 15000);
    } catch (error) {
      if (!allowRepair || !safeRepairable(error)) throw error;
      log(`Questão ${question.number}: divergência segura detectada; sincronizando a tela e tentando novamente.`, "warning");
      await smartRepair(true);
      await bridge("fillQuestion", { question, fillKeywords: app.session.fillKeywords }, 50000);
      return bridge("verifyCurrentQuestion", { question }, 15000);
    }
  }

  function destinationRecordsForCurrentState() {
    const state=app.diagnosis?.state||{};
    if(state.disciplineRecords?.length) return state.disciplineRecords;
    const item=Engine.currentItem(app.session);
    return item?.draftId && String(item.draftId)===String(state.questionId) ? item.bankCleanupTargets||[] : [];
  }

  function destinationText(scopes) {
    return (scopes||[]).map(scope=>`${scope.institutionName||"Instituição confirmada"} → ${scope.modality} → ${scope.course} → ${scope.grade} → ${scope.name} (vínculo ${scope.idGradeDisciplina})`).join("\n");
  }

  function bankRecords(records) {
    return (records||[]).map(record=>{
      const scope=(app.session.bankDestination||[]).find(s=>s.gradeDisciplineIds?.includes(String(record.idGradeDiscipline)));
      return {...record,institutionId:scope?.institutionId,institutionName:scope?.institutionName,bankScopeKey:scope?.key};
    });
  }

  function confirmSameDestination(state) {
    const expected=(app.session.bankDestination||[]).flatMap(s=>s.gradeDisciplineIds||[]).sort().join("|");
    const actual=[...new Set((state.disciplineRecords||[]).map(r=>String(r.idGradeDiscipline||"")))].sort().join("|");
    if(!expected || actual!==expected) throw new Error("O destino da questão mudou ou não pôde ser lido. Retome o lote e confirme o produto, curso, grade e disciplina antes de enviar.");
  }

  async function processPending(question) {
    question.name = Engine.semesterName(question.name);
    Engine.currentItem(app.session).name = question.name;
    const state=await ensureBlankForm();
    confirmSameDestination(state);
    await checkpoint(P.FILLING,{bankCleanupTargets:bankRecords(state.disciplineRecords)});
    Engine.incrementAttempt(app.session, "fill");
    await saveSession();
    setSiteStatus("neutral", `Questão ${question.number}: preenchendo e comparando todos os campos...`);
    await fillAndVerify(question, true);
    await checkpoint(P.FILLED);
    log(`Questão ${question.number}: preenchimento completo e idêntico ao trecho revisado.`, "success");
  }

  async function recoverFilling(question, item) {
    try {
      await bridge("verifyCurrentQuestion", { question }, 15000);
      await checkpoint(P.FILLED);
      log(`Questão ${question.number}: preenchimento anterior recuperado e conferido.`, "success");
      return;
    } catch (error) {
      if (item.attempts.fill >= 2) throw error;
    }
    Engine.incrementAttempt(app.session, "fill");
    await saveSession();
    await fillAndVerify(question, true);
    await checkpoint(P.FILLED);
  }

  async function saveFilled(question) {
    confirmSameDestination(await bridge("getState",{},10000));
    await checkpoint(P.SAVING);
    Engine.incrementAttempt(app.session, "save");
    await saveSession();
    setSiteStatus("neutral", `Questão ${question.number}: salvando uma única vez...`);
    try {
      const saved = await bridge("saveDraft", { question }, 50000);
      await checkpoint(P.DRAFT_SAVED, { draftId: String(saved.id) });
      log(`Questão ${question.number}: registro ${saved.id} salvo e conferido campo a campo.`, "success");
    } catch (error) {
      const problem = classifyExecutionError(error, Engine.currentItem(app.session));
      if (problem.definite) await checkpoint(P.FILLED, { saveRejected: true });
      throw error;
    }
  }

  async function recoverSaving(question) {
    const state = await bridge("getState", {}, 10000);
    if (state.questionId && state.questionId !== "0") {
      await bridge("verifyCurrentQuestion", { question }, 15000);
      await checkpoint(P.DRAFT_SAVED, { draftId: String(state.questionId) });
      log(`Questão ${question.number}: salvamento ${state.questionId} recuperado sem novo clique.`, "success");
      return;
    }
    if (question.questionFormat !== "discursive" && state.alternativePolicy?.explicit && !state.alternativePolicy.allowsFour) {
      await checkpoint(P.FILLED, { saveRejected: true });
      throw new Error(`[PERFIL_EXIGE_CINCO] O perfil/configuração atual do AvaliA exige ${state.alternativePolicy.min === state.alternativePolicy.max ? `exatamente ${state.alternativePolicy.min}` : `mínimo ${state.alternativePolicy.min ?? "?"} e máximo ${state.alternativePolicy.max ?? "?"}`} afirmativas. A questão A–D foi preservada e pode ser isolada para o lote continuar.`);
    }
    throw new Error("[SALVAMENTO_INDETERMINADO] O salvamento anterior não retornou um ID. A extensão não repetirá o clique automaticamente.");
  }

  async function prepareOfficial(question, item) {
    if (item.phase === P.DRAFT_SAVED) await checkpoint(P.PREPARING);
    if (item.attempts.prepare >= 3) throw new Error("[ETAPAS_NAO_CONCLUIDAS] O AvaliA não concluiu as etapas obrigatórias após 3 tentativas controladas.");
    Engine.incrementAttempt(app.session, "prepare");
    await saveSession();
    setSiteStatus("neutral", `Questão ${question.number}: visualização, referências e correção...`);
    const prepared = await bridge("prepareOfficialSubmission", { question }, 180000);
    await checkpoint(P.READY_TO_SUBMIT, { ignoredSuggestions: prepared.corrections?.ignoredSuggestions || 0 });
    if (prepared.warnings?.length) log(`Questão ${question.number}: ${prepared.warnings.length} metadado(s) já conferido(s) no Passo 4 não estavam expostos nas etapas finais; ${question.questionFormat === "discursive" ? "enunciado, padrão de resposta e feedback permaneceram idênticos" : "conteúdo A–D permaneceu idêntico"}.`, "info");
    log(`Questão ${question.number}: conferência final concluída; pronta para envio oficial.`, "success");
  }

  async function submitOfficial(question, item) {
    if (question.name !== Engine.semesterName(question.name)) throw new Error("[SEMESTRE_PENDENTE] Este rascunho foi salvo antes da atualização do nome. Acrescente o ano e semestre vigente ao nome no AvaliA e confira novamente antes do envio.");
    const destinationState=await bridge("getState",{},10000);
    if(destinationState.disciplineRecords?.length) confirmSameDestination(destinationState);
    else {
      if(String(destinationState.questionId)!==String(item.draftId)) throw new Error("O ID da questão não corresponde ao destino conferido no salvamento.");
      confirmSameDestination({disciplineRecords:item.bankCleanupTargets||[]});
    }
    const isLast = app.session.currentIndex === app.session.items.length - 1;
    const nextMode = isLast ? "fresh" : "same";
    await checkpoint(P.SUBMITTING, { nextMode });
    Engine.incrementAttempt(app.session, "submit");
    await saveSession();
    setSiteStatus("neutral", `Questão ${question.number}: enviando oficialmente uma única vez...`);
    try {
      const submitted = await bridge("submitOfficial", { question, nextMode }, 100000);
      await checkpoint(P.SUBMITTED, { submissionConfirmed: true, nextMode, confirmedBy: submitted.confirmedBy || "response" });
      log(`Questão ${question.number}: envio oficial ${item.draftId} confirmado pelo AvaliA.`, "success");
    } catch (error) {
      Engine.recordError(app.session, error, { needsVerification: true });
      await saveSession();
      throw error;
    }
  }

  async function reconcileSubmission(question, item) {
    const result = await bridge("reconcileOfficial", { questionId: item.draftId, nextMode: item.nextMode || "same" }, 15000);
    if (!result.confirmed) throw new Error(result.message || "O envio precisa ser verificado na lista do AvaliA.");
    await checkpoint(P.SUBMITTED, { submissionConfirmed: true, confirmedBy: result.evidence || "reconciliation" });
    log(`Questão ${question.number}: envio reconciliado sem repetir o clique.`, "success");
  }

  async function completeItem(question, item) {
    const completedId = item.draftId;
    const ignoredSuggestions = item.ignoredSuggestions || 0;
    const completedIndex = app.session.currentIndex;
    Engine.completeCurrent(app.session, { id: completedId, ignoredSuggestions, manuallyAuthorized: Boolean(item.manualAuthorizedAt), allocationAuthorized: Boolean(item.allocationAuthorizedAt), richSignature: question.richSignature || "" });
    await saveSession();
    try {
      await registerCompletedQuestion(question, item, completedId, completedIndex);
    } catch (ledgerError) {
      log(`Questão ${question.number}: concluída, mas o histórico antirrepetição não pôde ser atualizado (${ledgerError.message}).`, "warning", { code: "DUPLICIDADE.HISTORICO_NAO_GRAVADO", questionNumber: question.number });
    }
    app.reviewIndex = Math.min(app.session.currentIndex, app.session.items.length - 1);
    renderSession();
    log(`Questão ${question.number}: concluída (${completedId}).`, "success");
    if (app.session.currentIndex < app.session.items.length && !app.stopRequested) {
      const state = await bridge("getState", {}, 10000);
      if (!(state.currentStep === "step-4" && (!state.questionId || state.questionId === "0"))) {
        Engine.incrementAttempt(app.session, "next");
        await saveSession();
        await bridge("resetForNext", {}, 40000);
      }
    }
  }

  async function isolateCurrent(problem, automatic) {
    const item = Engine.currentItem(app.session);
    if (!canSkipItem(item, problem)) throw new Error("Esta questão não pode ser isolada com segurança nesta fase.");
    if (!automatic) {
      const approved = window.confirm(`Ignorar a questão ${item.number} e continuar com as próximas?\n\n${problem.title}\n${problem.message}\n\n${item.draftId ? `O registro ${item.draftId} permanecerá como rascunho no AvaliA.` : "Nenhum registro confirmado foi criado para esta questão."}`);
      if (!approved) return false;
    }
    if (item.draftId) {
      setSiteStatus("neutral", `Questão ${item.number}: preparando uma tela nova antes de continuar...`);
      await bridge("resetForNext", {}, 40000);
    }
    const number = item.number;
    const id = item.draftId;
    Engine.skipCurrent(app.session, `${problem.title}: ${problem.message}`, {
      errorCode: problem.code,
      problem,
      automatic: Boolean(automatic)
    });
    await saveSession();
    app.reviewIndex = Math.min(app.session.currentIndex, app.session.items.length - 1);
    log(`Questão ${number}${id ? ` (registro ${id})` : ""}: isolada por ${problem.code}; o lote continuará com as demais.`, "warning");
    renderSession();
    return true;
  }

  async function processCurrent() {
    const item = Engine.currentItem(app.session);
    const question = executionQuestion();
    if (!item || !question) return;
    app.reviewIndex = app.session.currentIndex;
    renderQuestion(app.reviewIndex);
    renderProgress();
    if (item.phase === P.PENDING) return processPending(question);
    if (item.phase === P.FILLING) return recoverFilling(question, item);
    if (item.phase === P.FILLED) return saveFilled(question);
    if (item.phase === P.SAVING) return recoverSaving(question);
    if (item.phase === P.DRAFT_SAVED && app.session.outputMode === "draft") return completeItem(question, item);
    if (item.phase === P.DRAFT_SAVED || item.phase === P.PREPARING) return prepareOfficial(question, item);
    if (item.phase === P.READY_TO_SUBMIT) return submitOfficial(question, item);
    if (item.phase === P.SUBMITTING || item.phase === P.NEEDS_VERIFICATION) return reconcileSubmission(question, item);
    if (item.phase === P.SUBMITTED) return completeItem(question, item);
    throw new Error(`Fase não reconhecida: ${item.phase}.`);
  }

  async function setRunLock() {
    const value = { runId: app.session.runId, heartbeatAt: Date.now(), fileFingerprint: app.session.fileFingerprint };
    await storageSet({ [LOCK_KEY]: value });
    window.clearInterval(app.heartbeatTimer);
    app.heartbeatTimer = window.setInterval(() => {
      storageSet({ [LOCK_KEY]: { ...value, heartbeatAt: Date.now() } }).catch((error) => {
        app.stopRequested = true;
        setSiteStatus("danger", `O checkpoint deixou de responder: ${error.message}. A extensão pausará após a ação atual.`);
      });
    }, 5000);
  }

  async function releaseRunLock() {
    window.clearInterval(app.heartbeatTimer);
    const stored = await storageGet(LOCK_KEY);
    if (stored?.[LOCK_KEY]?.runId === app.session?.runId) await storageRemove(LOCK_KEY);
  }

  async function withExclusiveLock(task) {
    if (navigator.locks?.request) {
      return navigator.locks.request("avalia-autobatch-v4", { ifAvailable: true }, async (lock) => {
        if (!lock) throw new Error("Outro lote já está em execução em uma aba do AvaliA.");
        await setRunLock();
        try { return await task(); } finally { await releaseRunLock(); }
      });
    }
    const stored = await storageGet(LOCK_KEY);
    const active = stored?.[LOCK_KEY];
    if (active && Date.now() - Number(active.heartbeatAt || 0) < LOCK_TTL_MS) throw new Error("Outro lote já está em execução.");
    await setRunLock();
    try { return await task(); } finally { await releaseRunLock(); }
  }

  function announceCleanupState() {
    if(!app.session) return;
    if(Engine.needsBankCleanup(app.session)) {
      modeStrip("warning","Retirada dos likes pendente.",app.session.bankCleanupReceipt?.message||"As questões enviadas estão salvas. Conclua a retirada dos likes para finalizar.");
      setSiteStatus("warning","Envio preservado. O trabalho só será concluído após a conferência dos likes.");
    } else if(app.session.status==="completed") {
      modeStrip("success","Trabalho concluído.","Envio e retirada dos likes confirmados no banco correto.");
      setSiteStatus("success","Envio e retirada dos likes confirmados.");
    }
  }

  async function syncCleanupReceipt() {
    const session=app.session;
    if(!session?.bankCleanupEnabled || !Engine.cleanupIds(session).length) return true;
    let receipt;
    try {receipt=await window.SmartFoxBankManager.completion(session.runId,Engine.cleanupIds(session));}
    catch(error) {receipt={complete:false,message:error.message};}
    if(app.session!==session) return false;
    const complete=Engine.setBankCleanupReceipt(session,receipt);
    await saveSession();renderSession();return complete;
  }

  async function finishRequiredLikes(retry=false) {
    const session=app.session;
    if(!session?.bankCleanupEnabled || !Engine.cleanupIds(session).length) return true;
    if(app.cleanupBusy) return false;
    app.cleanupBusy=true;
    renderSession();
    modeStrip("running","Retirando likes do banco.","As questões enviadas estão salvas; aguardando a conferência da retirada.");
    try {
      let receipt;
      try {receipt=await window.SmartFoxBankManager.finishRun({runId:session.runId,questionIds:Engine.cleanupIds(session),retry,navigateToBank:session.currentIndex>=session.items.length});}
      catch(error) {receipt={complete:false,message:error.message};}
      if(app.session!==session) return false;
      const complete=Engine.setBankCleanupReceipt(session,receipt);
      await saveSession();
      if(receipt.navigation) {window.SmartFoxBankManager.navigate(receipt.navigation);return false;}
      log(complete?"Retirada dos likes confirmada no banco completo do destino.":`Retirada obrigatória dos likes pendente: ${receipt.message}`,complete?"success":"warning");
      return complete;
    } finally {app.cleanupBusy=false;renderSession();announceCleanupState();}
  }

  async function executeLoop() {
    let watchdog = 0;
    const watchdogLimit = app.session.items.length * 14 + 14;
    while (app.session.currentIndex < app.session.items.length) {
      if (app.stopRequested) break;
      watchdog += 1;
      if (watchdog > watchdogLimit) throw new Error("O protetor contra looping interrompeu a execução. Nenhuma ação adicional foi realizada.");
      const beforeItem = Engine.currentItem(app.session);
      const before = `${app.session.currentIndex}:${beforeItem?.phase || "none"}`;
      try {
        await processCurrent();
      } catch (error) {
        if (app.abandoning) break;
        const failedItem = Engine.currentItem(app.session);
        const problem = classifyExecutionError(error, failedItem);
        Engine.recordError(app.session, error, { problem, needsVerification: [P.SUBMITTING, P.NEEDS_VERIFICATION].includes(failedItem?.phase) && problem.ambiguous });
        await saveSession();

        const saveRepair = failedItem?.phase === P.FILLED && problem.definite && problem.retryable && failedItem.attempts.save < 2;
        if (saveRepair) {
          try {
            setSiteStatus("neutral", `Questão ${failedItem.number}: reaplicando o modelo e todos os campos antes da segunda tentativa...`);
            await fillAndVerify(executionQuestion(), true);
            app.session.status = "running";
            log(`Questão ${failedItem.number}: recusa confirmada sem criação de ID; o modelo e seus campos foram resincronizados. Será feita a tentativa segura 2 de 2.`, "warning");
            await saveSession();
            continue;
          } catch (repairError) {
            const repairProblem = classifyExecutionError(repairError, failedItem);
            Engine.recordError(app.session, repairError, { problem: repairProblem });
            await saveSession();
            if (app.session.continueOnError !== false && canSkipItem(failedItem, repairProblem)) {
              await isolateCurrent(repairProblem, true);
              continue;
            }
            throw repairError;
          }
        }

        const prepareRetry = failedItem?.phase === P.PREPARING && problem.retryable && failedItem.attempts.prepare < 3;
        const fillRetry = failedItem?.phase === P.FILLING && problem.retryable && failedItem.attempts.fill < 2;
        if (prepareRetry || fillRetry) {
          const attempt = prepareRetry ? failedItem.attempts.prepare : failedItem.attempts.fill;
          const limit = prepareRetry ? 3 : 2;
          try {
            const recovered = await recoverWorkspaceForItem(failedItem, false);
            if (recovered.safeToContinue) log(`Questão ${failedItem.number}: tela destravada e marco ${Engine.phaseLabel(failedItem.phase)} preservado.`, "success");
          } catch (recoveryError) {
            log(`Questão ${failedItem.number}: a recuperação segura ainda não concluiu (${recoveryError.message}).`, "warning");
          }
          app.session.status = "running";
          log(`Questão ${failedItem.number}: ${problem.title}. Retomada automática ${attempt + 1} de ${limit} será feita a partir do marco ${Engine.phaseLabel(failedItem.phase)}.`, "warning");
          await saveSession();
          await new Promise((resolve) => window.setTimeout(resolve, 700 * Math.max(1, attempt)));
          continue;
        }

        if (app.session.continueOnError !== false && canSkipItem(failedItem, problem)) {
          await isolateCurrent(problem, true);
          continue;
        }
        throw error;
      }
      const afterItem = Engine.currentItem(app.session);
      const after = `${app.session.currentIndex}:${afterItem?.phase || "none"}`;
      if (before === after) throw new Error(`O protetor contra looping detectou ausência de avanço em ${before}.`);
    }
    if (app.abandoning) return;
    if (app.session.currentIndex >= app.session.items.length) {
      app.session.submissionEndedAt=app.session.submissionEndedAt||new Date().toISOString();
      app.session.status=Engine.needsBankCleanup(app.session)?"cleanup_pending":"completed";
      if(app.session.status==="cleanup_pending") {app.session.completedAt=null;app.session.endedAt=null;}
      else app.session.endedAt=app.session.endedAt||app.session.submissionEndedAt;
      const officialCount=app.session.results.filter(r=>r.status==="official").length;
      const draftCount=app.session.results.filter(r=>r.status==="draft").length;
      const skippedCount=app.session.results.filter(r=>r.status==="skipped").length;
      await saveSession();renderSession();
      const finishingSession=app.session;
      const cleaned=await finishRequiredLikes(false);
      if(app.session!==finishingSession || app.abandoning) return;
      const duration=formatDuration(elapsedSeconds());
      if(cleaned) {
        modeStrip(skippedCount?"warning":"success","Trabalho concluído.",`${officialCount} oficiais, ${draftCount} rascunhos e ${skippedCount} isoladas em ${duration}.${officialCount?" Retirada dos likes confirmada.":""}`);
        setSiteStatus(skippedCount?"warning":"success",`Concluído: ${officialCount} oficiais, ${draftCount} rascunhos e ${skippedCount} isoladas.${officialCount?" Likes retirados e conferidos.":""}`);
      } else announceCleanupState();
      log(cleaned?(officialCount?"FIM: trabalho e retirada obrigatória dos likes concluídos.":"FIM: trabalho concluído."):"Envio finalizado; o trabalho permanece pendente da retirada dos likes.",cleaned?"success":"warning");
      await saveSession();
      if(app.session.notifyWhenDone && !app.session.bankCleanupReceipt?.navigation) window.alert(`${PRODUCT_NAME}\n\n${cleaned?"Trabalho concluído.":"Questões enviadas. Retirada dos likes pendente."}\n${officialCount} oficiais · ${draftCount} rascunhos · ${skippedCount} isoladas.\n${cleaned&&officialCount?"Likes confirmados: somente a última remessa no banco correto.":cleaned?"":"Use Concluir retirada dos likes. As questões não serão reenviadas."}`);
    } else if (app.stopRequested) {
      app.session.status = "paused";
      await saveSession();
      modeStrip("warning", "Execução pausada.", "Use Retomar do último marco.");
      setSiteStatus("warning", `Pausado após ${app.session.currentIndex} questão(ões).`);
      log("Execução pausada após concluir a operação em andamento.", "warning");
    }
  }

  async function focusFirstBlocker(eligibility) {
    if (eligibility.setup?.length) {
      app.currentView = "prepare";
      renderNavigation();
      renderTagPanel();
      ui.tagSection.scrollIntoView({ behavior: "smooth", block: "start" });
      modeStrip("warning", "Configuração manual pendente.", eligibility.setup[0].reason);
      setSiteStatus("warning", eligibility.setup[0].reason);
      return;
    }
    const first = eligibility.hard[0] || eligibility.review[0];
    if (!first) return;
    app.reviewIndex = first.index;
    app.currentView = "review";
    renderSession();
    ui.questionSection.scrollIntoView({ behavior: "smooth", block: "start" });
    modeStrip("warning", "O início precisa de uma ação.", first.reasons[0] || `Revise a questão ${first.number}.`);
    setSiteStatus("warning", `Questão ${first.number}: ${first.reasons[0] || "aguarda sua autorização."}`);
  }

  async function runBatch(options) {
    if(app.startPreparing || app.cleanupBusy) return;
    app.startPreparing=true;
    ui.start.disabled=true;ui.resume.disabled=true;
    try { return await runBatchPrepared(options); }
    catch(error) {
      if(app.session&&!app.abandoning)modeStrip("warning", "Não foi possível iniciar ou retomar o lote.", error.message);
      throw error;
    }
    finally {app.startPreparing=false;renderControls();}
  }

  async function runBatchPrepared(options) {
    if (app.batchReviewBusy) return;
    if (app.running || !app.session || app.session.currentIndex >= app.session.items.length) return;
    let currentDestination;
    await window.SmartFoxAccess.assertAuthorized({
      force: true,
      disciplines: Array.isArray(app.diagnosis?.state?.disciplines) ? app.diagnosis.state.disciplines : []
    });
    let eligibility = startEligibility();
    if (app.session.confirmedAt && !eligibility.ready) {
      await focusFirstBlocker(eligibility);
      log(`O lote não iniciou: ${eligibility.messages.join(" ")}`, "warning");
      return;
    }
    if (!app.session.confirmedAt) {
      let diagnosis = await refreshSiteStatus(true);
      if (!diagnosis.ready && diagnosis.repairableCount) diagnosis = await smartRepair(true);
      if (!diagnosis.ready) {
        const message = readinessMessage(diagnosis).message;
        setSiteStatus("danger", message);
        modeStrip("warning", "AvaliA ainda não está pronto.", message);
        log(`O lote não iniciou: ${message}`, "warning");
        return;
      }
      eligibility = startEligibility();
      if (!eligibility.ready) {
        await focusFirstBlocker(eligibility);
        log(`O lote não iniciou após conferir a disciplina: ${eligibility.messages.join(" ")}`, "warning");
        return;
      }
      try {
        await ensureBlankForm();
      } catch (error) {
        setSiteStatus("danger", error.message);
        log(`O lote não foi iniciado: ${error.message}`, "error");
        return;
      }
      const remaining = app.session.items.length - app.session.currentIndex;
      const official = selectedMode() === "official";
      const manuallyAuthorized = app.session.items.filter((item) => item.manualAuthorizedAt).length;
      const allocationAuthorized = app.session.items.filter((item) => item.allocationAuthorizedAt).length;
      const knowledgeReviewed = app.session.items.filter((item) => item.knowledgeReviewedAt).length;
      const duplicateCount = app.session.parsed.duplicateQuestionCount || 0;
      const richCount = app.session.parsed.questions.reduce((total, question) => total + (question.richIntegrity?.imageHashes?.length || 0) + (question.richIntegrity?.formulaHashes?.length || 0), 0);
      const targetTag = app.session.tagConfig?.target;
      modeStrip("running", "Conferindo o destino da prova.", "Aguarde a leitura dos produtos e disciplinas do AvaliA.");
      setSiteStatus("warning", "Conferindo instituição, produto e disciplina antes do envio…");
      currentDestination = await window.SmartFoxBankManager.resolveTargets(destinationRecordsForCurrentState());
      app.session.bankDestination = currentDestination;
      const destinationSummary = destinationText(app.session.bankDestination);
      const likeSummary = "Após o envio, o SmartFox trocará em Minhas Instituições para o destino confirmado e abrirá a tela azul. Os likes das questões anteriores serão retirados e somente as questões desta remessa receberão like em cada banco confirmado. Se houver bloqueio no AvaliA, a limpeza ficará pendente em Likes do banco.";
      const approved = window.confirm(official
        ? `CONFIRMAÇÃO ÚNICA — ENVIO OFICIAL\n\n${remaining} questões serão preenchidas, comparadas, salvas, revisadas nas etapas do AvaliA e enviadas oficialmente.\n\nCONFIRME O DESTINO:\n${destinationSummary}\nÉ esse o produto e a disciplina corretos?\n\nDisciplina escolhida manualmente no Passo 3 · tag de Graduação: ${targetTag?.label || "não confirmada"}. A extensão só atuará do Passo 4 em diante.\n\n${manuallyAuthorized} aprovação(ões) de qualidade · ${allocationAuthorized} aprovação(ões) de matéria · ${knowledgeReviewed} conferência(s) bibliográfica(s) · ${richCount} imagem(ns)/fórmula(s) com assinatura · ${duplicateCount} repetição(ões) apenas sinalizadas.\n\n${likeSummary}\n\nFalhas definitivas poderão ser isoladas para o restante continuar. Salvamentos, envios ou likes sem confirmação inequívoca nunca serão repetidos. Deseja iniciar?`
        : `CONFIRMAÇÃO ÚNICA — RASCUNHOS\n\n${remaining} questões serão preenchidas, comparadas e salvas como rascunho.\n\n${destinationSummary}\n\nÉ esse o produto e a disciplina corretos? Deseja iniciar?`);
      if (!approved) {
        modeStrip("warning", "Início cancelado.", "A prova permanece disponível para revisão.");
        setSiteStatus("warning", "Início cancelado. Nenhuma questão foi enviada.");
        log("Início cancelado; o arquivo permanece disponível para revisão.", "info");
        return;
      }
      app.session.confirmedAt = new Date().toISOString();
      app.session.startedAt = app.session.startedAt || app.session.confirmedAt;
      app.session.status = "running";
      app.session.outputMode = selectedMode();
      app.session.fillKeywords = ui.keywords.checked;
      app.session.notifyWhenDone = ui.notify.checked;
      app.session.continueOnError = ui.continueErrors.checked;
      app.session.tagConfig.lockedAt = app.session.confirmedAt;
      app.session.approvalSync.enabled = false;
      app.session.approvalSync.status = app.session.approvalSync.enabled ? "waiting_for_batch" : "not_requested";
      log(`INÍCIO: lote ${official ? "oficial" : "de rascunhos"} iniciado às ${formatClock(app.session.startedAt)}.`, "success");
      await saveSession();
    } else {
      const resumedItem = Engine.currentItem(app.session);
      let diagnosis = await refreshSiteStatus(true);
      const unsafePhase = [P.SAVING, P.SUBMITTING, P.NEEDS_VERIFICATION].includes(resumedItem?.phase);
      if (!diagnosis.ready && diagnosis.repairableCount && !unsafePhase) diagnosis = await smartRepair(true);
      if (!diagnosis.ready) {
        const message = readinessMessage(diagnosis).message;
        setSiteStatus("danger", message);
        modeStrip("warning", "Retomada aguardando o AvaliA.", message);
        log(`A retomada não iniciou: ${message}`, "warning");
        return;
      }
      eligibility = startEligibility();
      if (!eligibility.ready) {
        await focusFirstBlocker(eligibility);
        log(`A retomada aguardou nova conferência da disciplina: ${eligibility.messages.join(" ")}`, "warning");
        return;
      }
    }

    // A fresh start has already resolved and confirmed this exact destination.
    // Resume still re-reads it; never cache a destination across attempts.
    currentDestination ||= await window.SmartFoxBankManager.resolveTargets(destinationRecordsForCurrentState());
    const destinationKeys=value=>(value||[]).map(s=>s.key).sort().join("|");
    if(destinationKeys(currentDestination)!==destinationKeys(app.session.bankDestination)) {
      if(!window.confirm(`CONFIRME O DESTINO DA RETOMADA\n\n${destinationText(currentDestination)}\n\nÉ esse o produto e a disciplina corretos para as questões restantes?`)) return;
      app.session.bankDestination=currentDestination;
      await saveSession();
    }
    if (app.session.outputMode === "official" && window.SmartFoxBankManager) {
      if (app.session.bankCleanupOwner && app.session.bankCleanupOwner !== window.SmartFoxBankManager.owner()) throw new Error("O professor deste lote não corresponde ao perfil atual. Abra o lote com a conta original.");
      app.session.bankCleanupEnabled = true;
      app.session.bankCleanupOwner = window.SmartFoxBankManager.owner();
      app.session.bankCleanupTargets = bankRecords(destinationRecordsForCurrentState());
      app.session.approvalSync.enabled = false;
      await saveSession();
    }
    assertWorkActive();
    app.running = true;
    app.stopRequested = false;
    app.currentView = "run";
    modeStrip("running", "Execução em andamento.", "Mantenha esta aba aberta.");
    renderNavigation();
    renderControls();
    startClock();
    try {
      await withExclusiveLock(executeLoop);
    } catch (error) {
      const item = Engine.currentItem(app.session);
      const problem = classifyExecutionError(error, item);
      if (app.session.status !== "verification_required") Engine.recordError(app.session, error, { problem });
      await saveSession();
      renderSession();
      const needsVerification = Engine.currentItem(app.session)?.phase === P.NEEDS_VERIFICATION;
      modeStrip(needsVerification ? "warning" : "danger", needsVerification ? "Envio precisa de conferência." : "Execução pausada com segurança.", needsVerification ? "Nenhum clique foi repetido." : "Use Resolver problema e tentar continuar.");
      setSiteStatus(needsVerification ? "warning" : "danger", `${problem.title}: ${problem.message}`);
      log(`Execução interrompida [${problem.code}] na questão ${problem.questionNumber || "—"}, etapa ${Engine.phaseLabel(problem.phase)}: ${problem.message} Próxima ação: ${problem.action}`, "error");
    } finally {
      app.running = false;
      renderSession();
      if (app.session?.bankCleanupEnabled && app.session.currentIndex < app.session.items.length) {
        try { await finishRequiredLikes(false); }
        catch(error) { log(`As questões enviadas foram preservadas. Limpeza de likes pendente: ${error.message}`, "warning"); }
      }
    }
  }

  async function fillSelected() {
    const question = reviewQuestion();
    if (!question || app.running) return;
    if (!question.executable) {
      setSiteStatus("danger", "Corrija os campos obrigatórios desta questão antes do teste.");
      return;
    }
    try {
      await ensureBlankForm();
      await bridge("fillQuestion", { question, fillKeywords: ui.keywords.checked }, 50000);
      await bridge("verifyCurrentQuestion", { question }, 15000);
      setSiteStatus("success", `Questão ${question.number} preenchida e conferida, sem salvar.`);
      log(`Teste da questão ${question.number}: todos os campos conferem; nada foi salvo.`, "success");
    } catch (error) {
      setSiteStatus("danger", error.message);
      log(error.message, "error");
    }
  }

  async function recoverAndResume() {
    if (!app.session || app.running) return;
    const item = Engine.currentItem(app.session);
    if (!item) return;
    if (item?.phase === P.NEEDS_VERIFICATION) {
      setSiteStatus("warning", "Este envio precisa ser conferido na lista; não é seguro tentar novamente.");
      return;
    }
    const problem = item?.lastProblem || (item?.lastError ? classifyExecutionError(new Error(item.lastError), item) : null);
    if (problem?.ambiguous) {
      setSiteStatus("warning", problem.action);
      return;
    }
    let diagnosis;
    try {
      const recovered = await recoverWorkspaceForItem(item, false);
      diagnosis = recovered.diagnosis;
      if (recovered.safeToContinue) log(`Questão ${item.number}: recuperação concluída; retomando exatamente do último marco.`, "success");
    } catch (error) {
      const recoveryProblem = classifyExecutionError(error, item);
      setSiteStatus(recoveryProblem.ambiguous ? "warning" : "danger", `${recoveryProblem.title}: ${recoveryProblem.message}`);
      log(`Recuperação [${recoveryProblem.code}]: ${recoveryProblem.message}`, "error");
      if (recoveryProblem.ambiguous) return;
    }
    if (!diagnosis?.ready) diagnosis = await smartRepair(false);
    if (diagnosis.ready && app.session.confirmedAt) {
      if (problem?.retryable) {
        Engine.resetAttempts(app.session, item.phase === P.PREPARING ? ["prepare"] : ["fill", "prepare", "next"]);
        log(`Questão ${item.number}: contador da retomada liberado após nova verificação da tela.`, "info");
        await saveSession();
      }
      await runBatch({ resume: true });
    }
  }

  async function skipCurrentManually() {
    const item = Engine.currentItem(app.session);
    if (!item || app.running) return;
    const problem = item.lastProblem || classifyExecutionError(new Error(item.lastError || "Falha atual"), item);
    try {
      const skipped = await isolateCurrent(problem, false);
      if (skipped && app.session.confirmedAt && app.session.currentIndex < app.session.items.length) await runBatch({ resume: true });
    } catch (error) {
      const failed = classifyExecutionError(error, Engine.currentItem(app.session));
      setSiteStatus("danger", `${failed.title}: ${failed.message}`);
      log(`Não foi possível continuar após isolar: ${failed.message}`, "error");
    }
  }

  async function confirmSentManually() {
    const item = Engine.currentItem(app.session);
    if (!item || item.phase !== P.NEEDS_VERIFICATION) return;
    const approved = window.confirm(`Confirme somente se você localizou a questão ${item.draftId} na lista do AvaliA com situação oficial/aprovada.\n\nA extensão não fará outro clique de envio. Marcar como enviada e continuar?`);
    if (!approved) return;
    await checkpoint(P.SUBMITTED, { submissionConfirmed: true, confirmedBy: "manual-list-check" });
    log(`Questão ${item.number}: envio confirmado manualmente na lista, sem repetição.`, "success");
    await runBatch({ resume: true });
  }

  function downloadJson(payload, fileName) {
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = fileName;
    link.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  function diagnosticSnapshot() {
    return {
      product: PRODUCT_NAME,
      version: PRODUCT_VERSION,
      generatedAt: new Date().toISOString(),
      preflight: app.diagnosis?.preflight || null,
      pageState: app.diagnosis?.state ? {
        pageKind: app.diagnosis.state.pageKind,
        supportedPage: app.diagnosis.state.supportedPage,
        formReady: app.diagnosis.state.formReady,
        currentStep: app.diagnosis.state.currentStep,
        activeSource: app.diagnosis.state.activeSource,
        hasSourceId: Boolean(app.diagnosis.state.sourceId),
        institutionName: app.diagnosis.state.institutionName,
        hasInstitutionId: Boolean(app.diagnosis.state.institutionId),
        disciplines: app.diagnosis.state.disciplines,
        disciplineRecords: app.diagnosis.state.disciplineRecords,
        tagCatalog: app.diagnosis.state.tagCatalog,
        editors: app.diagnosis.state.editors,
        pageBusy: app.diagnosis.state.pageBusy
      } : null,
      issues: app.diagnosis?.issues || [],
      recentAvaliaErrors: app.diagnosis?.state?.recentSiteErrors || [],
      storageHealth: app.storageHealth,
      duplicateHistory: {
        stats: Duplicates.stats(app.duplicateLedger),
        currentScan: app.session?.parsed?.duplicateHistory || null,
        scope: "Somente este perfil do Chrome e registros concluídos pela extensão."
      },
      knowledgeBase: {
        ...Knowledge.baseStats(app.knowledgeBase),
        activeCollection: activeKnowledgeCollection(),
        activeCollectionStats: Knowledge.baseStats(app.knowledgeBase, activeKnowledgeCollection().id),
        integrity: Knowledge.integrityReport(app.knowledgeBase)
      },
      tagConfiguration: app.session?.tagConfig || app.pendingTagConfig,
      approvalSync: app.session?.approvalSync || null,
      fileDiagnostic: currentFileDiagnostics(),
      currentRun: app.session ? { runId: app.session.runId, fileName: app.session.fileName, status: app.session.status, currentIndex: app.session.currentIndex, total: app.session.items.length } : null,
      occurrences: app.occurrences.slice(-200)
    };
  }

  function downloadDiagnostic() {
    downloadJson(diagnosticSnapshot(), `Diagnostico_SmartFox_11_0_${new Date().toISOString().replace(/[:.]/g, "-")}.json`);
    recordOccurrence("Diagnóstico técnico exportado.", "info", { code: "DIAGNOSTICO_EXPORTADO" });
  }

  function exportOccurrenceStore() {
    downloadJson({ product: PRODUCT_NAME, version: PRODUCT_VERSION, generatedAt: new Date().toISOString(), count: app.occurrences.length, occurrences: app.occurrences }, `Ocorrencias_SmartFox_11_0_${new Date().toISOString().replace(/[:.]/g, "-")}.json`);
  }

  async function clearOccurrenceStore() {
    const approved = window.confirm("Limpar o banco local de ocorrências? Isso não altera questões ou registros no AvaliA.");
    if (!approved || app.running) return;
    app.occurrences = [];
    app.knownSiteErrors = new Set();
    await storageRemove(OCCURRENCE_KEY);
    renderOccurrenceCenter();
  }

  function downloadReport() {
    if (!app.session) return;
    const report = {
      product: PRODUCT_NAME,
      version: PRODUCT_VERSION,
      fileName: app.session.fileName,
      fileFingerprint: app.session.fileFingerprint,
      mode: app.session.outputMode,
      status: app.session.status,
      startedAt: app.session.startedAt || null,
      endedAt: app.session.endedAt || null,
      durationSeconds: elapsedSeconds(),
      totalQuestions: app.session.items.length,
      completedQuestions: app.session.currentIndex,
      validQuestions: app.session.parsed.validQuestionCount ?? app.session.parsed.executableCount,
      duplicateQuestions: app.session.parsed.duplicateQuestionCount || 0,
      answerDistribution: app.session.parsed.answerDistribution || null,
      answerDistributionWarning: app.session.parsed.answerDistributionWarning || "",
      fileDiagnostic: currentFileDiagnostics(),
      duplicateHistory: {
        stats: Duplicates.stats(app.duplicateLedger),
        currentScan: app.session.parsed.duplicateHistory || null,
        scope: "Somente este perfil do Chrome e registros concluídos pela extensão."
      },
      officialQuestions: app.session.results.filter((result) => result.status === "official").length,
      draftQuestions: app.session.results.filter((result) => result.status === "draft").length,
      skippedQuestions: app.session.results.filter((result) => result.status === "skipped").length,
      allocationAuditAt: app.session.allocationAuditAt || null,
      disciplineSnapshot: app.session.disciplineSnapshot || [],
      tagConfiguration: app.session.tagConfig || null,
      approvalSync: app.session.approvalSync || null,
      avaliaErrors: app.session.avaliaErrors || app.diagnosis?.state?.recentSiteErrors || [],
      preflight: app.diagnosis?.preflight || null,
      storageHealth: app.storageHealth,
      knowledgeBase: {
        ...Knowledge.baseStats(app.knowledgeBase, activeKnowledgeCollection().id),
        collection: activeKnowledgeCollection(),
        documentNames: scopedKnowledgeBase().documents.map((document) => document.name),
        integrity: Knowledge.integrityReport(app.knowledgeBase)
      },
      generatedFromKnowledgeBase: Boolean(app.session.generatedFromKnowledgeBase),
      generationRules: app.session.parsed.generationRules || null,
      results: app.session.results,
      questions: app.session.parsed.questions.map((question, index) => ({
        number: question.number,
        name: question.name,
        sourceRange: [question.sourceStart, question.sourceEnd],
        segmentationMethod: question.segmentationMethod,
        segmentationConfidence: question.segmentationConfidence,
        type: { id: question.typeId, label: question.typeLabel, confidence: question.typeConfidence, evidence: question.typeEvidence, candidates: question.typeCandidates },
        cognitive: { id: question.cognitiveId, label: question.cognitiveLabel, confidence: question.cognitiveConfidence, evidence: question.cognitiveEvidence },
        referencesText: question.referencesText || "",
        fingerprint: question.fingerprint,
        confidence: question.confidence,
        qualityScore: question.audit?.score,
        audit: question.audit?.checks,
        allocationAudit: question.allocationAudit || null,
        knowledgeAudit: question.knowledgeAudit || null,
        generationEvidence: question.generationEvidence || null,
        curriculumEvidence: question.curriculumEvidence || null,
        blueprintEvidence: question.blueprintEvidence || null,
        generationAudit: question.generationAudit || null,
        richIntegrity: question.richIntegrity || null,
        media: (question.media || []).map(({ dataUrl, ...entry }) => entry),
        formulas: (question.formulas || []).map(({ canonical, ...entry }) => entry),
        hardErrors: question.hardErrors,
        reviewBlocks: question.reviewBlocks,
        warnings: question.warnings,
        manualAuthorization: app.session.items[index].manualAuthorizedAt ? { at: app.session.items[index].manualAuthorizedAt, note: app.session.items[index].manualAuthorizationNote } : null,
        allocationAuthorization: app.session.items[index].allocationAuthorizedAt ? { at: app.session.items[index].allocationAuthorizedAt, note: app.session.items[index].allocationAuthorizationNote } : null,
        knowledgeDecision: app.session.items[index].knowledgeReviewedAt ? { decision: app.session.items[index].knowledgeDecision, at: app.session.items[index].knowledgeReviewedAt, note: app.session.items[index].knowledgeReviewNote, correction: app.session.items[index].knowledgeCorrection } : null,
        execution: app.session.items[index]
      })),
      events: app.session.events || []
    };
    downloadJson(report, `Relatorio_SmartFox_11_0_${new Date().toISOString().replace(/[:.]/g, "-")}.json`);
  }

  async function restoreSession() {
    try {
      const stored = await storageGet(STORAGE_KEY);
      let session = stored?.[STORAGE_KEY];
      let migrated = false;
      let migratedFrom = "";
      if (!session) {
        const legacyStored = await storageGet(LEGACY_STORAGE_KEYS);
        const legacy = LEGACY_STORAGE_KEYS.map((key) => legacyStored?.[key]).find((candidate) => [4, 5, 6].includes(candidate?.schemaVersion));
        if ([4, 5, 6].includes(legacy?.schemaVersion)) {
          migratedFrom = `${legacy.schemaVersion}.0`;
          session = legacy.schemaVersion === 6 ? Engine.migrateSessionV6(legacy) : legacy.schemaVersion === 5 ? Engine.migrateSessionV5(legacy) : Engine.migrateSessionV4(legacy);
          Parser.summarizeParsed(session.parsed);
          session.events = Array.isArray(session.events) ? session.events : [];
          session.events.push({ at: new Date().toISOString(), message: `Sessão ${migratedFrom} migrada para ${PRODUCT_LABEL}; questões já concluídas foram preservadas e a retomada continuará do último marco.`, kind: "success", code: "SESSAO_MIGRADA" });
          await storageSet({ [STORAGE_KEY]: session });
          migrated = true;
        }
      }
      if (!session || session.schemaVersion !== Engine.schemaVersion) return;
      Engine.hydrateSession(session);
      session.parsed.subjectHint = session.parsed.subjectHint || Parser.subjectHintFromFileName(session.fileName);
      session.parsed.questions.forEach((question) => {
        question.subjectHint = question.subjectHint || session.parsed.subjectHint;
        question.richIntegrity = question.richIntegrity || Parser.computeRichIntegrity(question);
        question.richSignature = question.richSignature || question.richIntegrity.signature;
        question.allocationAudit = question.allocationAudit || { status: "unknown", score: 0, selectedDiscipline: "", subjectHint: question.subjectHint, reason: "Aguardando nova conferência com a disciplina do AvaliA.", matchedTerms: [], missingTerms: [] };
      });
      Parser.summarizeParsed(session.parsed);
      Engine.assertSession(session);
      app.session = session;
      await syncCleanupReceipt();
      app.fileImportFailure = null;
      app.pendingTagConfig = { target: session.tagConfig.target || null, syncLatestOnly: Boolean(session.tagConfig.syncLatestOnly) };
      if (session.status === "completed" && session.approvalSync?.enabled && session.approvalSync.status === "waiting_for_batch") session.approvalSync.status = "awaiting_professor";
      app.lastDisciplines = Array.isArray(session.disciplineSnapshot) ? session.disciplineSnapshot : [];
      app.session.events = Array.isArray(app.session.events) ? app.session.events : [];
      const mode = ui.modeInputs.find((input) => input.value === session.outputMode);
      if (mode) mode.checked = true;
      ui.keywords.checked = session.fillKeywords !== false;
      ui.notify.checked = session.notifyWhenDone !== false;
      ui.continueErrors.checked = session.continueOnError !== false;
      app.reviewIndex = Math.min(session.currentIndex, session.items.length - 1);
      app.currentView = session.confirmedAt && (session.status !== "completed" || session.approvalSync?.enabled) ? "run" : "review";
      await scanQuestionsWithBase({ silent: true });
      renderSession();
      const occurrenceKeys = new Set(app.occurrences.map((entry) => `${entry.at}:${entry.message}`));
      (session.events || []).slice(-100).forEach((event) => {
        if (occurrenceKeys.has(`${event.at}:${event.message}`)) return;
        app.occurrences.push({ at: event.at, message: event.message, kind: event.kind || "info", code: event.code || occurrenceCode(event.message), source: "session-history", questionNumber: null, runId: session.runId, fileName: session.fileName });
      });
      if (app.occurrences.length > OCCURRENCE_LIMIT) app.occurrences.splice(0, app.occurrences.length - OCCURRENCE_LIMIT);
      persistOccurrenceStore();
      renderOccurrenceCenter();
      if(session.status === "cleanup_pending") announceCleanupState();
      else if (session.status === "completed") modeStrip("success", "Sessão anterior concluída.", "Pronta para uma nova avaliação.");
      else if (migrated) modeStrip("success", `Sessão ${migratedFrom} recuperada.`, "As concluídas foram preservadas; use Retomar do último marco.");
      else if (session.confirmedAt) modeStrip("warning", "Sessão interrompida encontrada.", "Use Retomar do último marco.");
      else modeStrip("success", "Arquivo anterior restaurado.", "Continue a revisão ou inicie.");
      await saveSession();
      await refreshSiteStatus(true);
    } catch (error) {
      log(`Não foi possível restaurar a sessão ${PRODUCT_LABEL}: ${error.message}`, "error");
    }
  }

  async function removeSelectedFile() {
    if (app.running || app.approvalRunning || app.fileImportBusy || app.fileRemovalBusy) return;
    app.fileRemovalBusy = true;
    renderControls();
    try {
      // Finish pending saves before deleting so the file cannot reappear on reload.
      await sessionWriteQueue;
      await storageRemove([STORAGE_KEY, ...LEGACY_STORAGE_KEYS]);
      app.session = null;
      app.fileImportFailure = null;
      app.fileDiagnosticFilter = "action";
      app.reviewIndex = 0;
      app.reviewFilter = "all";
      app.currentView = "prepare";
      ui.file.value = "";
      ui.fileSummary.textContent = "Nenhum arquivo analisado.";
      modeStrip("neutral", "Arquivo removido.", "Selecione outro DOCX quando desejar. Nada já enviado ao AvaliA foi apagado.");
      renderSession();
    } finally {
      app.fileRemovalBusy = false;
      renderControls();
      ui.file.focus();
    }
  }

  async function clearSession() {
    return abandonWork();
  }

  async function clearQuestions() {
    return abandonWork({ questionsOnly: true });
  }

  async function abandonWork(options = {}) {
    if (app.abandoning) return;
    const questionsOnly = options.questionsOnly === true;
    const approved = window.confirm(questionsOnly
      ? "Zerar as questões deste trabalho?\n\nO lote, suas edições e o Word selecionado serão removidos. Os contadores voltarão a zero e o lote não será restaurado ao reabrir.\n\nAs UAs, coleções, configurações e histórico serão mantidos. Questões já cadastradas no AvaliA permanecem lá. Se houver uma operação em andamento, a limpeza aguardará sua conclusão; nenhum novo comando será enviado."
      : "Abandonar o trabalho atual?\n\nSerão descartados os arquivos selecionados, as questões e edições do lote, as análises e os resultados exibidos. O lote não será restaurado ao reabrir.\n\nAs coleções e materiais já salvos, as configurações e o histórico serão mantidos. Registros já salvos no AvaliA permanecem lá. Se houver uma ação em andamento, ela será encerrada antes da limpeza; nenhum novo comando será enviado.");
    if (!approved) return;
    app.abandoning = true;
    app.abandonUncertain = false;
    app.stopRequested = true;
    app.generationController?.abort();
    ui.abandonWork.disabled = true;
    ui.clearQuestions.disabled = true;
    ui.abandonWork.textContent = "Encerrando…";
    ui.workStatus.textContent = "Encerrando operações e limpando…";
    const surfaces = Array.from(ui.panel.querySelectorAll(".aab-body, .aab-nav"));
    surfaces.forEach((element) => { element.inert = true; });
    try {
      // All UI tasks (including boot) are tracked. Let the current bridge response
      // settle; bridge() rejects every subsequent command while abandoning.
      // Draining saves BEFORE removal prevents a late checkpoint from restoring it.
      await Promise.allSettled(Array.from(workTasks));
      await sessionWriteQueue;
      await storageRemove([STORAGE_KEY, ...LEGACY_STORAGE_KEYS]);
      await releaseRunLock();
      window.clearInterval(app.clockTimer);
      app.clockTimer = null;
      app.heartbeatTimer = null;
      app.session = null;
      app.fileImportFailure = null;
      app.fileDiagnosticFilter = "action";
      if (!questionsOnly) {
        app.diagnosis = null;
        app.tagCatalog = null;
        app.pendingTagConfig = { target: null, syncLatestOnly: false };
        app.lastDisciplines = [];
        app.lastDiagnosisSignature = "";
      }
      app.reviewIndex = 0;
      app.reviewFilter = "all";
      app.currentView = "prepare";
      app.fileImportBusy = false;
      app.fileRemovalBusy = false;
      app.knowledgeBusy = false;
      app.running = false;
      app.approvalRunning = false;
      if (questionsOnly) ui.file.value = "";
      else ui.panel.querySelectorAll('input[type="file"]').forEach((input) => { input.value = ""; });
      ui.questionSection.querySelectorAll("input, textarea, select").forEach((input) => {
        if (input.type === "checkbox" || input.type === "radio") input.checked = false;
        else input.value = "";
      });
      ui.preview.innerHTML = "";
      ui.sourceText.textContent = "";
      ui.questionSelect.innerHTML = "";
      ui.fileSummary.textContent = "Nenhum arquivo analisado.";
      ui.filter.value = "all";
      ui.fileDiagnosticFilter.value = "action";
      ui.generationResult.textContent = "Nenhuma questão gerada neste trabalho.";
      ui.editCard.open = false;
      ui.progressBar.style.width = "0%";
      ui.progressText.textContent = "Nenhum lote em andamento.";
      ui.elapsed.textContent = "00:00";
      ui.lastProblem.innerHTML = "";
      if (!questionsOnly) {
        ui.materialUa.value = "";
        ui.diagnosis.innerHTML = "";
        ui.diagnosis.hidden = true;
        closeCollectionEditor();
        cancelMaterialEditor();
        resetExternalExam({ clearFile: true });
        ui.externalExamStatus.className = "aab-muted";
        applyCollectionDefaults();
        setBaseProgress("neutral", "Selecione materiais ou prepare uma nova avaliação.");
        renderMaterialBatchPreview();
        ui.preflightBadge.className = "aab-preflight-badge aab-preflight-waiting";
        ui.preflightBadge.textContent = "Aguardando";
        ui.preflightChecks.innerHTML = "";
        ui.preflightExplanation.className = "aab-preflight-explanation";
        ui.preflightExplanation.innerHTML = "<strong>Abra Elaborador e teste o perfil.</strong><span>Prepare uma nova avaliação quando desejar.</span>";
        ui.preflightTime.textContent = "Nenhum teste neste trabalho.";
        setSiteStatus("neutral", "Aguardando verificação.");
      }
      renderSession();
      renderSystemHealth();
      modeStrip(app.abandonUncertain ? "warning" : "neutral", questionsOnly ? "Questões zeradas." : "Trabalho abandonado.", app.abandonUncertain ? "A ação em andamento não respondeu. Confira o resultado no AvaliA antes de iniciar outro envio." : "A tela está pronta para uma nova avaliação.");
      ui.workStatus.textContent = "Nenhum trabalho aberto";
      ui.panel.querySelector(".aab-body").scrollTop = 0;
    } catch (error) {
      ui.workStatus.textContent = "Limpeza não concluída. Tente novamente.";
      setSiteStatus("danger", `Não foi possível concluir a limpeza: ${error.message}`);
    } finally {
      app.abandoning = false;
      app.stopRequested = false;
      surfaces.forEach((element) => { element.inert = false; });
      ui.abandonWork.disabled = false;
      ui.clearQuestions.disabled = false;
      ui.abandonWork.textContent = "Abandonar trabalho";
      renderControls();
      if (!app.session) ui.file.focus();
    }
  }

  ui.launcher.addEventListener("click", safeUiAction("PAINEL_ABERTURA", async () => { ui.panel.classList.add("aab-open"); renderNavigation(); await refreshSiteStatus(true); }));
  ui.close.addEventListener("click", () => ui.panel.classList.remove("aab-open"));
  ui.navButtons.forEach((button) => button.addEventListener("click", () => switchView(button.dataset.aabNav)));
  ui.helpSearch.addEventListener("input", filterHelp);
  ui.helpActions.addEventListener("click", safeUiAction("AJUDA_ACAO", handleHelpAction));
  document.addEventListener("keydown", (event) => {
    const editing = /^(?:INPUT|TEXTAREA|SELECT)$/.test(event.target?.tagName || "") || event.target?.isContentEditable;
    if (event.key === "Escape" && ui.panel.classList.contains("aab-open") && !editing) ui.panel.classList.remove("aab-open");
    if (event.key === "?" && event.altKey && !editing) {
      event.preventDefault();
      ui.panel.classList.add("aab-open");
      switchView("help");
      ui.helpSearch.focus();
    }
  });
  ui.file.addEventListener("change", safeUiAction("DOCX_IMPORTACAO", onFileSelected));
  ui.removeFile.addEventListener("click", safeUiAction("DOCX_REMOCAO", removeSelectedFile));
  ui.fileDiagnosticFilter.addEventListener("change", () => { app.fileDiagnosticFilter = ui.fileDiagnosticFilter.value; renderFileDiagnostics(); });
  ui.downloadFileDiagnostic.addEventListener("click", downloadCurrentFileDiagnostic);
  ui.approveFileRules.addEventListener("click", safeUiAction("ATHUS_EXCECOES_APROVACAO", approveCurrentFileRules));
  ui.revokeFileRules.addEventListener("click", safeUiAction("ATHUS_EXCECOES_REVOGACAO", revokeCurrentFileRules));
  ui.fileDiagnosticList.addEventListener("click", (event) => {
    const button = event.target.closest("[data-aab-open-file-issue]");
    if (button) openFileDiagnosticQuestion(Number(button.dataset.aabOpenFileIssue));
  });
  ui.mapTags.addEventListener("click", safeUiAction("TAGS_MAPEAMENTO", () => mapTagsNow({ silent: false })));
  ui.targetTag.addEventListener("change", safeUiAction("TAG_ESCOLHA", chooseTargetTag));
  ui.syncLikes.addEventListener("change", safeUiAction("LIKES_CONFIGURACAO", setLikeSyncOption));
  ui.testProfile.addEventListener("click", safeUiAction("PRE_TESTE", () => refreshSiteStatus(false)));
  ui.downloadDiagnostic.addEventListener("click", downloadDiagnostic);
  ui.repairSite.addEventListener("click", safeUiAction("RECUPERACAO_TELA", () => smartRepair(false)));
  ui.collectionSelect.addEventListener("change", safeUiAction("COLECAO_SELECAO", selectActiveCollection));
  ui.newCollection.addEventListener("click", () => openCollectionEditor("new"));
  ui.editCollection.addEventListener("click", () => openCollectionEditor("edit"));
  ui.deleteCollection.addEventListener("click", safeUiAction("COLECAO_EXCLUSAO", deleteActiveCollection));
  ui.testDatabase.addEventListener("click", safeUiAction("ARMAZENAMENTO_TESTE", () => testLocalDatabase({ silent: false })));
  ui.saveCollection.addEventListener("click", safeUiAction("COLECAO_SALVAMENTO", saveCollectionEditor));
  ui.cancelCollection.addEventListener("click", closeCollectionEditor);
  ui.collectionSubject.addEventListener("keydown", safeUiAction("COLECAO_SALVAMENTO", async (event) => { if (event.key === "Enter") await saveCollectionEditor(); }));
  ui.addMaterials.addEventListener("click", safeUiAction("BASE_IMPORTACAO", addSelectedMaterials));
  ui.scanBase.addEventListener("click", safeUiAction("BASE_CONFERENCIA", () => scanQuestionsWithBase({ silent: false })));
  ui.baseList.addEventListener("click", safeUiAction("BASE_ITEM_ACAO", async (event) => {
    const removeButton = event.target.closest("[data-aab-remove-material]");
    const editButton = event.target.closest("[data-aab-edit-material]");
    if (removeButton) await removeMaterial(removeButton.dataset.aabRemoveMaterial);
    else if (editButton) editMaterialMetadata(editButton.dataset.aabEditMaterial);
  }));
  ui.baseList.addEventListener("change", safeUiAction("BASE_ITEM_MOVIMENTO", async (event) => {
    const selector = event.target.closest("[data-aab-move-material]");
    if (selector) await moveMaterialToCollection(selector.dataset.aabMoveMaterial, selector.value);
  }));
  ui.saveMaterial.addEventListener("click", safeUiAction("BASE_CLASSIFICACAO", saveMaterialMetadata));
  ui.cancelMaterial.addEventListener("click", cancelMaterialEditor);
  ui.editMaterialCollection.addEventListener("change", () => {
    const collection = Knowledge.listCollections(app.knowledgeBase).find((entry) => entry.id === ui.editMaterialCollection.value);
    if (collection?.subject) ui.editMaterialSubject.value = collection.subject;
  });
  ui.exportBase.addEventListener("click", exportKnowledgeBackup);
  ui.exportCollection.addEventListener("click", exportActiveCollection);
  ui.auditBase.addEventListener("click", safeUiAction("BASE_AUDITORIA", auditKnowledgeBase));
  ui.importBase.addEventListener("change", safeUiAction("BASE_BACKUP_IMPORTACAO", importKnowledgeBackup));
  ui.clearBase.addEventListener("click", safeUiAction("BASE_ESVAZIAMENTO", clearKnowledgeBase));
  ui.ruleFile.addEventListener("change", safeUiAction("REGRAS_IMPORTACAO", loadRuleFile));
  ui.generationRules.addEventListener("change", safeUiAction("REGRAS_SALVAMENTO", () => persistGenerationRules()));
  ui.p1Composition.addEventListener("change", safeUiAction("PREFERENCIAS_SALVAMENTO", async () => {
    ui.generationCount.value=ui.p1Composition.value;
    refreshAthusPreview();
    await persistCollectionPreferences();
  }));
  [ui.generationCount, ui.generationUas, ui.generationDifficulty].forEach((control) => control.addEventListener("change", safeUiAction("PREFERENCIAS_SALVAMENTO", persistCollectionPreferences)));
  ui.applyAthusRules.addEventListener("click", safeUiAction("ATHUS_REGRAS_LOTE",applyAthusRulesToBatch));
  ui.downloadAthusDraft.addEventListener("click",safeUiAction("ATHUS_RASCUNHO",downloadAthusDraft));
  [ui.generationRules,ui.generationCount,ui.generationUas,ui.generationDifficulty,ui.generationEvaluation,ui.generationTheme].forEach(control=>control.addEventListener("input",refreshAthusPreview));
  ui.generateQuestions.addEventListener("click", safeUiAction("QUESTOES_GERACAO", generateQuestionsFromBase));
  ui.openAssessmentWord.addEventListener("click", () => {
    if (app.abandoning || app.running || app.knowledgeBusy || app.fileImportBusy) return;
    switchView("prepare");
    ui.file.click();
  });
  ui.downloadGeneratedDocx.addEventListener("click", safeUiAction("DOCX_EXPORTACAO", downloadGeneratedAssessment));
  ui.downloadGeneratedDocxReview.addEventListener("click", safeUiAction("DOCX_EXPORTACAO", downloadGeneratedAssessment));
  ui.downloadStudyGuide.addEventListener("click", safeUiAction("ROTEIRO_EXPORTACAO", downloadStudentStudyGuide));
  ui.downloadStudyGuideReview.addEventListener("click", safeUiAction("ROTEIRO_EXPORTACAO", downloadStudentStudyGuide));
  ui.downloadAssessmentPackage.addEventListener("click", safeUiAction("AVALIACAO_GUIA_EXPORTACAO", downloadAssessmentPackage));
  ui.materialFiles.addEventListener("change", renderMaterialBatchPreview);
  ui.materialUa.addEventListener("input", renderMaterialBatchPreview);
  ui.externalExamFile.addEventListener("change", () => {
    app.externalExamReport = null;
    ui.externalExamResults.hidden = true;
    ui.externalExamResults.innerHTML = "";
    ui.downloadExternalReport.hidden = true;
    const file = ui.externalExamFile.files?.[0];
    ui.externalExamStatus.className = "aab-muted";
    ui.externalExamStatus.textContent = file ? `${file.name} selecionado. Clique em Analisar pela coleção ativa.` : "Nenhuma prova externa analisada.";
    renderKnowledgeBase();
  });
  ui.analyzeExternalExam.addEventListener("click", safeUiAction("PROVA_EXTERNA_ANALISE", analyzeExternalExam));
  ui.downloadExternalReport.addEventListener("click", safeUiAction("PROVA_EXTERNA_EXPORTACAO", downloadExternalExamReport));
  ui.clearExternalReport.addEventListener("click", () => { resetExternalExam({ clearFile: true }); renderKnowledgeBase(); });
  ui.questionSelect.addEventListener("change", () => renderQuestion(Number(ui.questionSelect.value)));
  ui.prevQuestion.addEventListener("click", () => moveReview(-1));
  ui.nextQuestion.addEventListener("click", () => moveReview(1));
  ui.filter.addEventListener("change", () => {
    app.reviewFilter = ui.filter.value;
    app.reviewIndex = firstMatchingIndex(app.reviewIndex);
    renderQuestion(app.reviewIndex);
  });
  ui.nextIssue.addEventListener("click", goToNextIssue);
  ui.modeInputs.forEach((input) => input.addEventListener("change", safeUiAction("MODO_ALTERACAO", async () => {
    if (selectedMode() === "draft") ui.syncLikes.checked = false;
    await setLikeSyncOption();
    if (app.session && !app.session.confirmedAt) { app.session.outputMode = selectedMode(); await saveSession(); }
    renderTagPanel();
    renderReadiness();
  })));
  ui.continueErrors.addEventListener("change", safeUiAction("LOTE_PREFERENCIA", async () => {
    if (app.session) {
      app.session.continueOnError = ui.continueErrors.checked;
      await saveSession();
    }
  }));
  ui.manualConfirm.addEventListener("change", () => {
    const question = reviewQuestion();
    ui.authorize.disabled = !ui.manualConfirm.checked || !question?.executable || app.running;
  });
  ui.editType.addEventListener("change", () => {
    const selected = Parser.typeCatalog.find((type) => type.id === ui.editType.value);
    const discursive = selected?.key === "discursive" || ui.editType.value === "158";
    ui.expectedResponseField.hidden = !discursive;
    ui.objectiveFields.forEach((field) => { field.hidden = discursive; });
    Array.from(ui.imageTarget.options).forEach((option) => {
      const objectiveTarget = /^[A-D]$/.test(option.value);
      option.hidden = discursive ? objectiveTarget : option.value === "expectedResponse";
      option.disabled = option.hidden;
    });
    if (ui.imageTarget.selectedOptions[0]?.disabled) ui.imageTarget.value = "body";
    ui.confirmationCopy.textContent = discursive
      ? "Li o enunciado, o padrão de resposta e o feedback"
      : "Li o enunciado, as quatro alternativas A–D, o gabarito e o feedback";
  });
  ui.applyEdit.addEventListener("click", safeUiAction("QUESTAO_EDICAO", () => applyQuestionEdit(false)));
  ui.redetect.addEventListener("click", safeUiAction("QUESTAO_REDETECCAO", () => applyQuestionEdit(true)));
  ui.restoreQuestion.addEventListener("click", safeUiAction("QUESTAO_RESTAURACAO", restoreImportedQuestion));
  ui.addImage.addEventListener("click", safeUiAction("IMAGEM_INSERCAO", insertSelectedImage));
  ui.removeImage.addEventListener("click", safeUiAction("IMAGEM_REMOCAO", removeLastInsertedImage));
  ui.checkAllocation.addEventListener("click", safeUiAction("MATERIA_CONFERENCIA", checkAllocationNow));
  ui.approveAllReviews.addEventListener("click", safeUiAction("REVISAO_LOTE_APROVACAO", approveAllReviews));
  ui.approveAllocation.addEventListener("click", safeUiAction("MATERIA_APROVACAO", approveSelectedAllocation));
  ui.revokeAllocation.addEventListener("click", safeUiAction("MATERIA_REVOGACAO", revokeSelectedAllocation));
  ui.applyKnowledge.addEventListener("click", safeUiAction("BASE_CORRECAO", applySelectedKnowledgeCorrection));
  ui.keepKnowledge.addEventListener("click", safeUiAction("BASE_DECISAO", keepSelectedKnowledge));
  ui.revokeKnowledge.addEventListener("click", safeUiAction("BASE_DECISAO", revokeSelectedKnowledge));
  ui.reviewAllHigh.addEventListener("click", safeUiAction("BASE_CORRECOES_LOTE", applyAllHighConfidenceCorrections));
  ui.authorize.addEventListener("click", safeUiAction("QUESTAO_APROVACAO", authorizeSelected));
  ui.revoke.addEventListener("click", safeUiAction("QUESTAO_REVOGACAO", revokeSelected));
  ui.downloadModel.addEventListener("click",safeUiAction("MODELO_DOWNLOAD",()=>downloadTeacherResource("model")));
  ui.downloadPrompt.addEventListener("click",safeUiAction("PROMPT_DOWNLOAD",()=>downloadTeacherResource("prompt")));
  ui.finishCleanup.addEventListener("click",safeUiAction("LIKES_CONCLUIR",()=>finishRequiredLikes(true)));
  chrome.storage.onChanged?.addListener((changes,area)=>{
    if(area!=="local" || !changes.smartfoxBankCleanupV11 || !app.session?.bankCleanupEnabled || app.running || app.cleanupBusy) return;
    const summarize=value=>{const j=(value||[]).find(j=>j.runId===app.session.runId&&j.owner===app.session.bankCleanupOwner);return j?`${j.status}:${j.revision}:${j.doneRevision}`:"";};
    if(summarize(changes.smartfoxBankCleanupV11.newValue)===summarize(changes.smartfoxBankCleanupV11.oldValue)) return;
    syncCleanupReceipt().then(announceCleanupState).catch(error=>log(`Conferência de likes pendente: ${error.message}`,"warning"));
  });
  ui.start.addEventListener("click", safeUiAction("LOTE_INICIO", () => runBatch({ automatic: false })));
  ui.resume.addEventListener("click", safeUiAction("LOTE_RETOMADA", () => runBatch({ resume: true })));
  ui.fillCurrent.addEventListener("click", safeUiAction("QUESTAO_CONFERENCIA", fillSelected));
  ui.smartRecover.addEventListener("click", safeUiAction("LOTE_RECUPERACAO", recoverAndResume));
  ui.skipCurrent.addEventListener("click", safeUiAction("QUESTAO_ISOLAMENTO", skipCurrentManually));
  ui.stop.addEventListener("click", () => {
    app.stopRequested = true;
    ui.stop.disabled = true;
    log("Pausa solicitada; a operação atual será terminada antes da parada.", "info");
  });
  ui.confirmSent.addEventListener("click", safeUiAction("ENVIO_CONFIRMACAO_MANUAL", confirmSentManually));
  ui.inspectApprovals.addEventListener("click", safeUiAction("LIKES_PREVIA", inspectApprovals));
  ui.applyApprovals.addEventListener("click", safeUiAction("LIKES_APLICACAO", applyApprovals));
  ui.report.addEventListener("click", downloadReport);
  ui.clearSession.addEventListener("click", clearSession);
  ui.abandonWork.addEventListener("click", abandonWork);
  ui.clearQuestions.addEventListener("click", clearQuestions);
  ui.historySearch.addEventListener("input", () => { app.occurrenceSearch = ui.historySearch.value; renderOccurrenceCenter(); });
  ui.historyFilter.addEventListener("change", () => { app.occurrenceFilter = ui.historyFilter.value; renderOccurrenceCenter(); });
  ui.exportHistory.addEventListener("click", exportOccurrenceStore);
  ui.clearHistory.addEventListener("click", safeUiAction("HISTORICO_LIMPEZA", clearOccurrenceStore));
  filterHelp();

  async function boot() {
    try {
      await loadOccurrenceStore();
    } catch (error) {
      app.occurrences = [];
      console.warn("SmartFox: histórico local indisponível.", error);
    }
    try {
      await loadDuplicateLedger();
    } catch (error) {
      app.duplicateLedger = Duplicates.createEmptyLedger();
      console.warn("SmartFox: histórico de duplicidades indisponível.", error);
    }
    try {
      await loadKnowledgeBase();
    } catch (error) {
      app.knowledgeBase = Knowledge.createEmptyBase();
      applyCollectionDefaults();
      renderKnowledgeBase();
      setBaseProgress("danger", `O banco local não pôde ser aberto: ${error.message}. Exporte um diagnóstico e verifique o armazenamento do perfil.`);
      console.error("SmartFox: banco local indisponível.", error);
    }
    renderSession();
    try {
      await restoreSession();
    } catch (error) {
      log(`A sessão anterior não pôde ser restaurada: ${error.message}`, "error", { code: "SESSAO_RESTAURACAO_FALHOU" });
    }
    if (!app.session) await refreshSiteStatus(true);
  }

  trackWork(boot());
})();
