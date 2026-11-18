(function () {
  "use strict";

  const MESSAGE_CHANNEL = "AVALIA_AUTOBATCH";
  const REQUIRED_ALTERNATIVES = 4;
  const BRIDGE_VERSION = "11.0.0";
  const SITE_ERROR_LIMIT = 40;
  const OBJECTIVE_EDITOR_IDS = Object.freeze([
    "TextoQuestao",
    "TextoAfirmativaA",
    "TextoAfirmativaB",
    "TextoAfirmativaC",
    "TextoAfirmativaD",
    "TextoFeedbackQuestao"
  ]);
  const DISCURSIVE_EDITOR_IDS = Object.freeze([
    "TextoQuestao",
    "TextoPadraoResposta",
    "TextoFeedbackQuestao"
  ]);
  const siteErrors = [];
  let jqueryErrorHooked = false;

  function safeErrorText(value) {
    return String(value == null ? "" : value)
      .replace(/([?&](?:token|senha|password|authorization|cookie|session|email|login)=)[^&#\s]+/gi, "$1[omitido]")
      .replace(/\s+/g, " ")
      .trim()
      .slice(0, 700);
  }

  function recordSiteError(entry) {
    const error = { at: new Date().toISOString(), source: entry?.source || "avalia", code: entry?.code || "AVALIA_CLIENTE", status: Number(entry?.status || 0) || null, message: safeErrorText(entry?.message || "Falha sem mensagem"), url: safeErrorText(String(entry?.url || "").split("?")[0]) };
    const previous = siteErrors[siteErrors.length - 1];
    if (!previous || previous.code !== error.code || previous.message !== error.message || Date.now() - new Date(previous.at).getTime() > 1500) siteErrors.push(error);
    if (siteErrors.length > SITE_ERROR_LIMIT) siteErrors.splice(0, siteErrors.length - SITE_ERROR_LIMIT);
    return error;
  }

  function loginDetected() {
    const loginPath = /\/(?:Login|Account|Autenticacao)(?:\/|$)/i.test(location.pathname || "");
    const loginForm = Boolean(document.querySelector('form[action*="Login" i], input[type="password"], #inputPassword, #Password'));
    return loginPath || loginForm;
  }

  function responseLooksLikeLogin(xhr) {
    const responseUrl = String(xhr?.responseURL || "");
    const contentType = String(xhr?.getResponseHeader?.("content-type") || "");
    const body = String(xhr?.responseText || "").slice(0, 12000);
    return /\/(?:Login|Account\/Login|Autenticacao)(?:[/?#]|$)/i.test(responseUrl)
      || (/text\/html/i.test(contentType) && /(?:type=["']password["']|id=["'](?:inputPassword|Password)["']|>\s*Entrar\s*<)/i.test(body));
  }

  window.addEventListener("error", (event) => recordSiteError({ source: "javascript", code: "AVALIA_JAVASCRIPT", message: event.message || event.error?.message, url: event.filename }));
  window.addEventListener("unhandledrejection", (event) => recordSiteError({ source: "promise", code: "AVALIA_PROMISE", message: event.reason?.message || event.reason }));

  function ensureSiteErrorHooks() {
    const $ = window.jQuery;
    if (!$ || jqueryErrorHooked || typeof $(document).on !== "function") return;
    jqueryErrorHooked = true;
    $(document).on("ajaxError.avaliaAutoBatchMonitor", (_event, xhr, settings, thrown) => {
      const status = Number(xhr?.status || 0);
      const code = responseLooksLikeLogin(xhr) || status === 401 ? "AVALIA_SESSAO_EXPIRADA" : status === 403 ? "AVALIA_SEM_PERMISSAO" : status === 409 ? "AVALIA_CONFLITO" : status === 422 ? "AVALIA_VALIDACAO" : status >= 500 ? "AVALIA_SERVIDOR" : status ? "AVALIA_HTTP" : "AVALIA_REDE";
      recordSiteError({ source: "ajax", code, status, url: settings?.url, message: xhr?.responseJSON?.message || xhr?.statusText || thrown || "Falha de comunicação" });
    });
    $(document).on("ajaxComplete.avaliaAutoBatchSessionMonitor", (_event, xhr, settings) => {
      if (!responseLooksLikeLogin(xhr)) return;
      recordSiteError({ source: "ajax", code: "AVALIA_SESSAO_EXPIRADA", status: xhr?.status, url: settings?.url, message: "O AvaliA devolveu a tela de login no lugar da resposta esperada." });
    });
  }

  const delay = (milliseconds) => new Promise((resolve) => window.setTimeout(resolve, milliseconds));

  async function waitFor(condition, timeoutMs, timeoutMessage) {
    const startedAt = Date.now();
    while (Date.now() - startedAt < timeoutMs) {
      const result = condition();
      if (result) return result;
      await delay(200);
    }
    throw new Error(timeoutMessage);
  }

  function isVisible(element) {
    return Boolean(element && (element.offsetWidth || element.offsetHeight || element.getClientRects().length));
  }

  function dispatchValueEvents(element) {
    element.dispatchEvent(new Event("input", { bubbles: true }));
    element.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function setField(selector, value) {
    const element = document.querySelector(selector);
    if (!element) throw new Error(`Campo não localizado: ${selector}`);
    element.value = value == null ? "" : String(value);
    dispatchValueEvents(element);
    return element;
  }

  function normalizedOption(value) {
    return String(value || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/\s+/g, " ")
      .trim()
      .toLocaleLowerCase("pt-BR");
  }

  function questionFormat(question) {
    const declared = normalizedOption(`${question?.questionFormat || ""} ${question?.typeLabel || ""} ${question?.typeDescription || ""}`);
    return /\b(?:discursiv|dissertativ|resposta aberta)\w*/.test(declared) ? "discursive" : "objective";
  }

  function currentFormFormat() {
    const type = selectSnapshot("Questao_IdTipoQuestao");
    return questionFormat({ typeLabel: type.label });
  }

  function stableHash(value) {
    let hash = 0x811c9dc5;
    const text = String(value || "");
    for (let index = 0; index < text.length; index += 1) {
      hash ^= text.charCodeAt(index);
      hash = Math.imul(hash, 0x01000193);
    }
    return (hash >>> 0).toString(16).padStart(8, "0");
  }

  function safeQueryAll(root, selector) {
    try {
      return Array.from((root || document).querySelectorAll(selector) || []);
    } catch (_error) {
      return [];
    }
  }

  function compactText(element) {
    return String(element?.innerText || element?.textContent || "").replace(/\s+/g, " ").trim();
  }

  function equivalentLabel(left, right) {
    const expected = normalizedOption(left);
    const actual = normalizedOption(right);
    if (!expected || !actual) return false;
    return expected === actual || (expected.length >= 5 && actual.length >= 5 && (expected.includes(actual) || actual.includes(expected)));
  }

  function selectOptions(selector) {
    const element = document.querySelector(selector);
    if (!element) return [];
    return Array.from(element.options || []).filter((option) => option.value && option.value !== "0").map((option) => ({
      value: String(option.value),
      label: String(option.text || option.textContent || "").trim()
    }));
  }

  function setSelect(selector, value, label) {
    const element = document.querySelector(selector);
    if (!element) throw new Error(`Lista não localizada: ${selector}`);
    const desiredValue = String(value == null ? "" : value);
    let option = Array.from(element.options).find((item) => item.value === desiredValue);
    if (!option && label) {
      const normalizedLabel = normalizedOption(label);
      option = Array.from(element.options).find((item) => normalizedOption(item.text) === normalizedLabel);
      if (!option && normalizedLabel.length >= 5) {
        option = Array.from(element.options).find((item) => {
          const candidate = normalizedOption(item.text);
          return candidate.length >= 5 && (candidate.includes(normalizedLabel) || normalizedLabel.includes(candidate));
        });
      }
    }
    if (!option) {
      const available = selectOptions(selector).map((item) => `${item.label} (${item.value})`).join(", ");
      throw new Error(`[OPCAO_NAO_DISPONIVEL] O AvaliA não oferece “${label || desiredValue}” nesta lista.${available ? ` Opções encontradas: ${available}.` : ""}`);
    }
    element.value = option.value;
    dispatchValueEvents(element);
    return option.value;
  }

  function getTinyMce() {
    return window.tinymce || window.tinyMCE || null;
  }

  function editorHealth(expectedFormat) {
    const tiny = getTinyMce();
    const format = expectedFormat || currentFormFormat();
    const requiredIds = format === "discursive" ? DISCURSIVE_EDITOR_IDS : OBJECTIVE_EDITOR_IDS;
    const fields = requiredIds.map((id) => {
      const textarea = document.getElementById(id);
      const editor = tiny && typeof tiny.get === "function" ? tiny.get(id) : null;
      const iframe = document.getElementById(`${id}_ifr`);
      const editorReady = Boolean(editor && typeof editor.setContent === "function" && typeof editor.getContent === "function" && editor.initialized !== false);
      const textareaReady = Boolean(textarea && !textarea.disabled && (isVisible(textarea) || !tiny));
      const iframeReady = Boolean(iframe?.contentDocument?.body);
      return { id, present: Boolean(textarea), ready: editorReady || textareaReady || iframeReady };
    });
    return {
      format,
      required: fields.length,
      present: fields.filter((field) => field.present).length,
      ready: fields.filter((field) => field.ready).length,
      allReady: fields.every((field) => field.ready),
      pending: fields.filter((field) => !field.ready).map((field) => field.id)
    };
  }

  function pageBusy() {
    const $ = window.jQuery;
    const activeRequests = $ && typeof $.active === "number" ? $.active : 0;
    const busyIndicator = Array.from(document.querySelectorAll(".ld-spin, .fa-spinner, .loading, #loadingQuestao")).some(isVisible);
    return Boolean(activeRequests || busyIndicator);
  }

  function setEditor(id, html) {
    const value = String(html || "");
    const textarea = document.getElementById(id);
    if (!textarea) throw new Error(`Editor não localizado: ${id}`);
    textarea.value = value;
    dispatchValueEvents(textarea);

    const tiny = getTinyMce();
    const editor = tiny && typeof tiny.get === "function" ? tiny.get(id) : null;
    if (editor && typeof editor.setContent === "function") {
      editor.setContent(value);
      if (typeof editor.save === "function") editor.save();
      if (typeof editor.fire === "function") {
        editor.fire("input");
        editor.fire("change");
      }
    } else {
      const iframe = document.getElementById(`${id}_ifr`);
      if (iframe && iframe.contentDocument && iframe.contentDocument.body) {
        iframe.contentDocument.body.innerHTML = value;
      }
    }
  }

  function setEditorIfPresent(id, html) {
    if (!document.getElementById(id)) return false;
    setEditor(id, html);
    return true;
  }

  function clearKeywords() {
    const field = document.querySelector('[name="PalavrasChave"]');
    if (!field) return;
    const $ = window.jQuery;
    if ($ && typeof $(field).importTags === "function") {
      $(field).importTags("");
    } else {
      field.value = "";
      dispatchValueEvents(field);
    }
  }

  function setKeywords(keywords) {
    clearKeywords();
    const values = Array.from(new Set((keywords || []).map((item) => String(item || "").trim()).filter(Boolean)));
    if (!values.length) return;
    const field = document.querySelector('[name="PalavrasChave"]');
    if (!field) return;
    const joined = values.join(",");
    const $ = window.jQuery;
    if ($ && typeof $(field).importTags === "function") {
      $(field).importTags(joined);
    } else {
      field.value = joined;
      dispatchValueEvents(field);
    }
  }

  function readAlternativeCount() {
    try {
      if (typeof quantidadeQuestoes === "number") return quantidadeQuestoes;
    } catch (_error) {
      // A variável pode ainda não ter sido criada pelo formulário.
    }
    if (typeof window.quantidadeQuestoes === "number") return window.quantidadeQuestoes;
    const visible = [1, 2, 3, 4, 5].filter((number) => {
      const element = document.querySelector(`.questao-${number}`);
      return isVisible(element);
    });
    return visible.length || 5;
  }

  function readVisibleAlternativeCount() {
    return [1, 2, 3, 4, 5].filter((number) => {
      const elements = Array.from(document.querySelectorAll(`.questao-${number}`));
      return elements.some(isVisible);
    }).length;
  }

  function parseAlternativePolicy(text) {
    const value = normalizedOption(text);
    if (!/(?:alternativa|afirmativa)/i.test(value)) return null;
    const minimum = value.match(/quantidade minima(?: e)?(?: de)?\s*(\d+)|minim[oa](?: e)?(?: de)?\s*(\d+)/i);
    const maximum = value.match(/quantidade maxima(?: e)?(?: de)?\s*(\d+)|maxim[oa](?: e)?(?: de)?\s*(\d+)/i);
    const exact = value.match(/exatamente\s*(\d+)/i);
    const min = Number((minimum && (minimum[1] || minimum[2])) || (exact && exact[1]) || 0);
    const max = Number((maximum && (maximum[1] || maximum[2])) || (exact && exact[1]) || 0);
    if (!min && !max) return null;
    return { min: min || null, max: max || null, evidence: String(text || "").replace(/\s+/g, " ").trim() };
  }

  function discoverAlternativePolicy(extraMessages) {
    const evidence = [];
    const messages = Array.isArray(extraMessages) ? extraMessages : [];
    messages.forEach((message) => { if (message) evidence.push(String(message)); });
    Array.from(document.querySelectorAll('input[type="hidden"], input[type="number"], [data-min], [data-max], [min], [max]')).forEach((element) => {
      const identity = `${element.id || ""} ${element.name || ""}`;
      if (!/(?:alternativa|afirmativa|quantidade)/i.test(identity)) return;
      const min = element.getAttribute && element.getAttribute("min");
      const max = element.getAttribute && element.getAttribute("max");
      const dataMin = element.getAttribute && element.getAttribute("data-min");
      const dataMax = element.getAttribute && element.getAttribute("data-max");
      if (min || max || dataMin || dataMax) evidence.push(`alternativas: mínimo ${dataMin || min || "?"}, máximo ${dataMax || max || "?"}`);
      if (element.value && /(?:min|max)/i.test(identity)) evidence.push(`${identity}: ${element.value}`);
    });
    const parsed = evidence.map(parseAlternativePolicy).filter(Boolean);
    const min = parsed.reduce((value, entry) => entry.min == null ? value : Math.max(value || 0, entry.min), null);
    const maxValues = parsed.map((entry) => entry.max).filter((value) => value != null);
    const max = maxValues.length ? Math.min(...maxValues) : null;
    return {
      explicit: parsed.length > 0,
      min,
      max,
      allowsFour: !(min != null && min > REQUIRED_ALTERNATIVES) && !(max != null && max < REQUIRED_ALTERNATIVES),
      evidence: parsed.map((entry) => entry.evidence)
    };
  }

  function validationError(messages) {
    const list = (messages || []).map((message) => String(message || "").replace(/\s+/g, " ").trim()).filter(Boolean);
    const policy = discoverAlternativePolicy(list);
    if (policy.explicit && !policy.allowsFour) {
      const range = policy.min === policy.max && policy.min != null ? `exatamente ${policy.min}` : `mínimo ${policy.min ?? "?"} e máximo ${policy.max ?? "?"}`;
      const error = new Error(`[PERFIL_EXIGE_CINCO] O perfil/configuração atual do AvaliA exige ${range} afirmativas. O arquivo possui exatamente A–D e a extensão não inventará uma alternativa E. Esta questão pode ser ignorada para o lote continuar. Mensagem do AvaliA: ${list.join(" ")}`);
      recordSiteError({ source: "validation", code: "AVALIA_REGRA_DE_ALTERNATIVAS", status: 422, message: list.join(" ") });
      return error;
    }
    recordSiteError({ source: "validation", code: "AVALIA_VALIDACAO", status: 422, message: list.join(" ") || "Campo não informado" });
    return new Error(`[VALIDACAO_AVALIA] O AvaliA recusou o salvamento: ${list.join(" ") || "não informou o campo que precisa ser corrigido."}`);
  }

  function forceAlternativeCount(value) {
    try {
      quantidadeQuestoes = value;
    } catch (_error) {
      // O fallback abaixo atende páginas que não expõem a variável como global.
    }
    window.quantidadeQuestoes = value;
  }

  async function setAlternativeCount(target) {
    if (target !== REQUIRED_ALTERNATIVES) {
      throw new Error(`O SmartFox aceita exatamente ${REQUIRED_ALTERNATIVES} alternativas.`);
    }
    const policy = discoverAlternativePolicy();
    if (policy.explicit && !policy.allowsFour) throw validationError(policy.evidence);
    let count = readAlternativeCount();
    let guard = 0;
    while (count > target && guard < 5) {
      if (readVisibleAlternativeCount() <= target) break;
      const button = document.getElementById("btnRemoverAfirmativa");
      if (!button) break;
      button.click();
      try {
        await waitFor(() => readAlternativeCount() < count || readVisibleAlternativeCount() <= target, 2500, "");
      } catch (_error) {
        // O fallback explícito abaixo corrige formulários antigos do AvaliA.
      }
      count = readAlternativeCount();
      guard += 1;
    }
    while (count < target && guard < 10) {
      if (readVisibleAlternativeCount() >= target) break;
      const button = document.getElementById("btnAdicionarAfirmativa");
      if (!button) break;
      button.click();
      try {
        await waitFor(() => readAlternativeCount() > count || readVisibleAlternativeCount() >= target, 2500, "");
      } catch (_error) {
        // O fallback explícito abaixo corrige formulários antigos do AvaliA.
      }
      count = readAlternativeCount();
      guard += 1;
    }
    if (count !== target || readVisibleAlternativeCount() !== target) {
      forceAlternativeCount(target);
      [1, 2, 3, 4, 5].forEach((number) => {
        document.querySelectorAll(`.questao-${number}`).forEach((element) => {
          element.style.display = number <= target ? "" : "none";
        });
      });
    }
    setEditor("TextoAfirmativaE", "");
    const fifthRadio = document.querySelector('input[name="Afirmativas[4].Verdadeira"]');
    if (fifthRadio) {
      fifthRadio.checked = false;
      dispatchValueEvents(fifthRadio);
    }
    forceAlternativeCount(target);
    if (readVisibleAlternativeCount() !== target) throw new Error("O AvaliA não confirmou quatro áreas de alternativa visíveis.");
    return { count: target, fifthCleared: !htmlToText(document.getElementById("TextoAfirmativaE")?.value || "") };
  }

  function setCorrectAlternative(correctIndex) {
    if (!Number.isInteger(correctIndex) || correctIndex < 0 || correctIndex >= REQUIRED_ALTERNATIVES) {
      throw new Error("O gabarito precisa indicar uma alternativa entre A e D.");
    }
    const radios = Array.from(document.querySelectorAll('input[type="radio"][name^="Afirmativas["][name$=".Verdadeira"]'));
    if (radios.length < REQUIRED_ALTERNATIVES) throw new Error("Os controles de gabarito A-D não foram localizados.");
    const $ = window.jQuery;
    if ($ && $.fn && typeof $.fn.iCheck === "function") {
      radios.forEach((radio) => $(radio).iCheck("uncheck"));
      $(radios[correctIndex]).iCheck("check");
    } else {
      radios.forEach((radio, index) => {
        radio.checked = index === correctIndex;
        dispatchValueEvents(radio);
      });
    }
  }

  function htmlToText(html) {
    const container = document.createElement("div");
    container.innerHTML = String(html || "")
      .replace(/<br\s*\/?\s*>/gi, " ")
      .replace(/<\/(?:p|div|li|tr|h[1-6])\s*>/gi, " ");
    return (container.textContent || "").replace(/\s+/g, " ").trim();
  }

  function normalizedText(value) {
    return String(value == null ? "" : value).normalize("NFC").replace(/\u00a0/g, " ").replace(/\s+/g, " ").trim();
  }

  function editorHtml(id) {
    const textarea = document.getElementById(id);
    const tiny = getTinyMce();
    const editor = tiny && typeof tiny.get === "function" ? tiny.get(id) : null;
    if (editor && typeof editor.getContent === "function") return String(editor.getContent() || "");
    const iframe = document.getElementById(`${id}_ifr`);
    if (iframe?.contentDocument?.body) return String(iframe.contentDocument.body.innerHTML || "");
    return String(textarea?.value || "");
  }

  function editorText(id) {
    return htmlToText(editorHtml(id));
  }

  function htmlAttributes(html, attribute) {
    const expression = new RegExp(`${attribute}=["']([^"']+)["']`, "gi");
    return Array.from(String(html || "").matchAll(expression)).map((entry) => entry[1]).sort();
  }

  function imageSignatures(html) {
    const values = new Set(htmlAttributes(html, "data-aab-image"));
    for (const match of String(html || "").matchAll(/\balt=["']AABIMG:([^:"']+)/gi)) values.add(match[1]);
    return Array.from(values).sort();
  }

  function fnv1a(value) {
    let hash = 0x811c9dc5;
    for (let index = 0; index < String(value || "").length; index += 1) {
      hash ^= String(value).charCodeAt(index);
      hash = Math.imul(hash, 0x01000193);
    }
    return (hash >>> 0).toString(16).padStart(8, "0");
  }

  function imageSourceSignatures(html) {
    const signatures = [];
    for (const match of String(html || "").matchAll(/<img\b([^>]*)>/gi)) {
      const attributes = match[1];
      const marker = attributes.match(/data-aab-image=["']([^"']+)/i)?.[1] || attributes.match(/alt=["']AABIMG:([^:"']+)/i)?.[1];
      if (!marker) continue;
      const source = attributes.match(/\bsrc=["']([^"']*)["']/i)?.[1] || "";
      signatures.push(`${marker}:${source ? fnv1a(source) : "SEM_FONTE"}`);
    }
    return signatures.sort();
  }

  function mathStructure(html) {
    // Ignore editor bookkeeping, but preserve operands, order, operators and semantic attributes.
    const significant = new Set(['mathvariant','linethickness','bevelled','accent','accentunder','notation','rowspan','columnspan','width','height','depth','lspace','stretchy','fence','separator']);
    return (String(html).match(/<[^>]+>|[^<]+/g)||[]).map(token=>{
      if(!token.startsWith('<'))return htmlToText(token).replace(/\s+/g,'');
      const match=token.match(/^<(\/)?([\w:]+)([^>]*)>/);if(!match)return '';
      const name=match[2].toLowerCase().split(':').at(-1);
      if(match[1])return `</${name}>`;
      const attrs=[...match[3].matchAll(/([\w:-]+)\s*=\s*["']([^"']*)["']/g)]
        .filter(a=>significant.has(a[1].toLowerCase())).map(a=>`${a[1].toLowerCase()}=${htmlToText(a[2])}`).sort();
      // Empty MathML elements are serialized either as paired tags or self-closing tags.
      return `<${name}${attrs.length?' '+attrs.join(' '):''}>${/\/\s*$/.test(match[3])?`</${name}>`:''}`;
    }).join('');
  }

  function formulaSignatures(html) {
    const structures=[];
    const remainder=String(html||'').replace(/<math\b[^>]*>[\s\S]*?<\/math\s*>/gi,math=>{structures.push('mathml:'+mathStructure(math));return '';});
    const values = new Set(htmlAttributes(remainder, "data-aab-formula"));
    for (const match of remainder.matchAll(/\btitle=["']Fórmula Word verificada:\s*([0-9a-f]+)/gi)) values.add(match[1]);
    return [...values,...structures].sort(); // duplicates matter: two formulas cannot collapse into one.
  }

  function expectedRichText(plain, html) {
    // OMML's linear description (x^(2)) and its rendered MathML (x2) differ by design.
    // Compare rendered text here; formulaSignatures separately checks the complete math tree.
    return normalizedText(/<math\b/i.test(html||'')?htmlToText(html):(plain||htmlToText(html)));
  }

  function specialCharacters(text) {
    const counts = new Map();
    for (const character of String(text || "").normalize("NFC")) {
      const point = character.codePointAt(0);
      if (point < 0x80 || /\s/.test(character)) continue;
      const key = `${character}:U+${point.toString(16).toUpperCase().padStart(4, "0")}`;
      counts.set(key, (counts.get(key) || 0) + 1);
    }
    return Array.from(counts.entries()).sort(([left], [right]) => left.localeCompare(right)).map(([key, count]) => `${key}:${count}`);
  }

  function scriptSignatures(html) {
    const signatures = [];
    const expression = /<(sup|sub)\b[^>]*>([\s\S]*?)<\/\1\s*>/gi;
    let match;
    while ((match = expression.exec(String(html || ""))) !== null) signatures.push(`${match[1].toLowerCase()}:${normalizedText(htmlToText(match[2]))}`);
    return signatures.sort();
  }

  function richIntegrity(html) {
    return {
      images: imageSignatures(html),
      imageSources: imageSourceSignatures(html),
      formulas: formulaSignatures(html),
      scripts: scriptSignatures(html),
      specialCharacters: specialCharacters(htmlToText(html))
    };
  }

  function selectedCorrectIndex() {
    const radios = Array.from(document.querySelectorAll('input[type="radio"][name^="Afirmativas["][name$=".Verdadeira"]'));
    return radios.findIndex((radio) => radio.checked || radio.closest(".iradio_square-blue")?.classList.contains("checked"));
  }

  function selectSnapshot(id) {
    const field = document.getElementById(id);
    const selected = field && field.options ? Array.from(field.options).find((option) => option.value === field.value) : null;
    return {
      present: Boolean(field),
      visible: isVisible(field),
      disabled: Boolean(field && field.disabled),
      value: String(field?.value || ""),
      label: String(selected?.text || selected?.textContent || "").trim()
    };
  }

  function formSnapshot() {
    const alternativeHtml = ["A", "B", "C", "D", "E"].map((letter) => editorHtml(`TextoAfirmativa${letter}`));
    const alternatives = alternativeHtml.map(htmlToText);
    const bodyHtml = editorHtml("TextoQuestao");
    const expectedResponseHtml = editorHtml("TextoPadraoResposta");
    const feedbackHtml = editorHtml("TextoFeedbackQuestao");
    const type = selectSnapshot("Questao_IdTipoQuestao");
    const cognitive = selectSnapshot("IdHabilidadeQuestao");
    const format = questionFormat({ typeLabel: type.label });
    return {
      questionFormat: format,
      name: normalizedText(document.getElementById("Questao_Nome")?.value || ""),
      bodyText: normalizedText(htmlToText(bodyHtml)),
      bodyHtml,
      expectedResponseText: normalizedText(htmlToText(expectedResponseHtml)),
      expectedResponseHtml,
      alternatives: alternatives.map(normalizedText),
      alternativeHtml,
      feedbackText: normalizedText(htmlToText(feedbackHtml)),
      feedbackHtml,
      correctIndex: selectedCorrectIndex(),
      typeId: type.value,
      type,
      cognitiveId: cognitive.value,
      cognitive,
      alternativeCount: format === "discursive" ? 0 : readAlternativeCount(),
      visibleAlternativeCount: format === "discursive" ? 0 : readVisibleAlternativeCount()
    };
  }

  function compareQuestion(question, options) {
    validateQuestionPayload(question);
    const actual = formSnapshot();
    const settings = options || {};
    const postSave = settings.metadataMode === "post-save" || (settings.metadataMode !== "strict" && numericStep() > 4);
    const format = questionFormat(question);
    const expectedAlternatives = question.alternatives.map((item) => expectedRichText(item.plain, item.html));
    const mismatches = [];
    const mismatchDetails = [];
    const warnings = [];
    const mismatch = (field, expected, found) => {
      mismatches.push(field);
      mismatchDetails.push({ field, expected: String(expected ?? ""), found: String(found ?? "") });
    };
    const compareRich = (label, expectedHtml, actualHtml) => {
      const expected = richIntegrity(expectedHtml);
      const found = richIntegrity(actualHtml);
      const checks = [
        ["imagens", expected.images, found.images],
        ["conteúdo binário das imagens", expected.imageSources, found.imageSources],
        ["fórmulas", expected.formulas, found.formulas],
        ["sobrescritos/subscritos", expected.scripts, found.scripts],
        ["caracteres especiais", expected.specialCharacters, found.specialCharacters]
      ];
      checks.forEach(([kind, expectedValues, foundValues]) => {
        if (JSON.stringify(expectedValues) !== JSON.stringify(foundValues)) mismatch(`${kind} em ${label}`, expectedValues.join(", ") || "nenhum", foundValues.join(", ") || "nenhum");
      });
    };
    const nameField = document.getElementById("Questao_Nome");
    const generatedGenericName = question.headerFormat === "generic" && nameField?.readOnly && Boolean(actual.name);
    if (normalizedText(question.name) !== actual.name) mismatch("identificação", normalizedText(question.name), actual.name);
    if (expectedRichText(question.bodyText, question.bodyHtml) !== actual.bodyText) mismatch("enunciado", expectedRichText(question.bodyText, question.bodyHtml), actual.bodyText);
    if (format === "discursive") {
      const expectedResponse = expectedRichText(question.expectedResponseText, question.expectedResponseHtml);
      if (expectedResponse !== actual.expectedResponseText) mismatch("padrão de resposta", expectedResponse, actual.expectedResponseText);
    } else {
      expectedAlternatives.forEach((expected, index) => {
        if (expected !== actual.alternatives[index]) mismatch(`alternativa ${"ABCD"[index]}`, expected, actual.alternatives[index]);
      });
      if (actual.alternatives[4]) mismatch("alternativa E não vazia", "vazia", actual.alternatives[4]);
    }
    if (expectedRichText(question.feedbackText, question.feedbackHtml) !== actual.feedbackText) mismatch("feedback pedagógico", expectedRichText(question.feedbackText, question.feedbackHtml), actual.feedbackText);
    compareRich("enunciado", question.bodyHtml, actual.bodyHtml);
    if (format === "discursive") compareRich("padrão de resposta", question.expectedResponseHtml, actual.expectedResponseHtml);
    else question.alternatives.forEach((alternative, index) => compareRich(`alternativa ${"ABCD"[index]}`, alternative.html, actual.alternativeHtml[index]));
    compareRich("feedback pedagógico", question.feedbackHtml, actual.feedbackHtml);
    if (format !== "discursive" && Number(question.correctIndex) !== actual.correctIndex) mismatch("gabarito", "ABCD"[Number(question.correctIndex)] || question.correctIndex, "ABCD"[actual.correctIndex] || actual.correctIndex);
    if (String(question.typeId) !== actual.typeId) {
      if (equivalentLabel(question.typeLabel, actual.type.label)) warnings.push({ field: "tipo da questão", expected: String(question.typeId), found: actual.typeId, reason: `O perfil usa outro código interno para o mesmo tipo “${actual.type.label}”.` });
      else if (postSave && format !== "discursive") warnings.push({ field: "tipo da questão", expected: String(question.typeId), found: actual.typeId, reason: "O AvaliA não mantém esse controle estável depois do salvamento; o valor já foi conferido no Passo 4." });
      else mismatch("tipo da questão", String(question.typeId), actual.typeId);
    }
    if (question.cognitiveId && String(question.cognitiveId) !== actual.cognitiveId) {
      if (equivalentLabel(question.cognitiveLabel, actual.cognitive.label)) warnings.push({ field: "nível cognitivo", expected: String(question.cognitiveId), found: actual.cognitiveId, reason: `O perfil usa outro código interno para o mesmo nível “${actual.cognitive.label}”.` });
      else if (postSave) warnings.push({ field: "nível cognitivo", expected: String(question.cognitiveId), found: actual.cognitiveId, reason: "O AvaliA não mantém esse controle estável depois do salvamento; o valor já foi conferido no Passo 4." });
      else mismatch("nível cognitivo", String(question.cognitiveId), actual.cognitiveId);
    }
    if (format !== "discursive" && (actual.alternativeCount !== REQUIRED_ALTERNATIVES
      || (currentStep() === "step-4" && actual.visibleAlternativeCount !== REQUIRED_ALTERNATIVES))) {
      if (postSave && !actual.alternatives[4]) warnings.push({ field: "quantidade de alternativas", expected: REQUIRED_ALTERNATIVES, found: actual.alternativeCount, reason: "A–D permanecem completas e E está vazia; o contador visual foi recriado pelo assistente do AvaliA." });
      else mismatch("quantidade de alternativas", REQUIRED_ALTERNATIVES, actual.alternativeCount);
    }
    return { matches: mismatches.length === 0, mismatches, mismatchDetails, warnings, actual, questionFormat: format, metadataMode: postSave ? "post-save" : "strict", richIntegrity: { body: richIntegrity(actual.bodyHtml), expectedResponse: richIntegrity(actual.expectedResponseHtml), alternatives: format === "discursive" ? [] : actual.alternativeHtml.slice(0, 4).map(richIntegrity), feedback: richIntegrity(actual.feedbackHtml) } };
  }

  function verifyCurrentQuestion(payload) {
    const question = payload && payload.question;
    const verification = compareQuestion(question, { metadataMode: payload && payload.metadataMode });
    if (!verification.matches) {
      const details = verification.mismatchDetails.map((entry) => `${entry.field} (esperado: “${entry.expected || "vazio"}”; encontrado: “${entry.found || "vazio"}”)`).join("; ");
      throw new Error(`[DIVERGENCIA_DE_CAMPO] A conferência do ${currentStep() || "formulário"} encontrou ${verification.mismatches.length} diferença(s): ${details}. Nenhum envio oficial foi feito.`);
    }
    const discursive = verification.questionFormat === "discursive";
    return {
      verified: true,
      questionFormat: verification.questionFormat,
      fields: discursive ? 6 : 9,
      richFields: discursive ? 3 : 6,
      alternativeCount: discursive ? 0 : REQUIRED_ALTERNATIVES,
      correctLetter: discursive ? "" : "ABCD"[question.correctIndex],
      warnings: verification.warnings,
      metadataMode: verification.metadataMode,
      richIntegrity: verification.richIntegrity
    };
  }

  function validateQuestionPayload(question) {
    const errors = [];
    if (!question || typeof question !== "object") errors.push("Questão inválida.");
    if (!question || typeof question !== "object") throw new Error(errors.join(" "));
    const format = questionFormat(question);
    if (question.segmentationWarnings?.length) errors.push("A separação dos campos precisa ser corrigida antes do preenchimento: " + question.segmentationWarnings.join(" "));
    if (!question.name) errors.push("Identificação ausente.");
    if (!htmlToText(question.bodyHtml || question.bodyText)) errors.push("Enunciado ausente.");
    if (format === "discursive") {
      if (!htmlToText(question.expectedResponseHtml || question.expectedResponseText)) errors.push("Padrão de resposta discursiva ausente.");
    } else {
      if (!Array.isArray(question.alternatives) || question.alternatives.length !== REQUIRED_ALTERNATIVES) {
        errors.push(`São obrigatórias exatamente ${REQUIRED_ALTERNATIVES} alternativas A–D.`);
      }
      if (!Number.isInteger(question.correctIndex) || question.correctIndex < 0 || question.correctIndex >= REQUIRED_ALTERNATIVES) {
        errors.push("Gabarito inválido.");
      }
    }
    if (!htmlToText(question.feedbackHtml || question.feedbackText)) errors.push("Feedback pedagógico ausente.");
    if (!question.typeId || String(question.typeId) === "0") errors.push("Tipo de questão ausente.");
    if (errors.length) throw new Error(errors.join(" "));
  }

  function currentStep() {
    const step = Array.from(document.querySelectorAll("#myModal2 .content")).find(isVisible);
    return step ? step.id : "";
  }

  function disciplineRecords() {
    return Array.from(new Set([
      ...document.querySelectorAll("#tableDisciplinas tbody tr"),
      ...document.querySelectorAll('table[id*="Disciplina" i] tbody tr'),
      ...document.querySelectorAll('[data-disciplina]')
    ]))
      .map((row) => {
        const cells = Array.from(row.cells || []);
        const texts = cells.map(compactText);
        const tagCell = cells[4] || null;
        const tags = safeQueryAll(tagCell, "span[value], [data-id-tag], [data-tag-id]").map((element) => ({
          id: String(element.getAttribute?.("value") || element.getAttribute?.("data-id-tag") || element.getAttribute?.("data-tag-id") || "").trim(),
          label: compactText(element),
          group: "Graduação"
        })).filter((tag) => tag.id && tag.label);
        return {
          idGradeDiscipline: String(row.getAttribute?.("value") || row.getAttribute?.("data-id-grade-disciplina") || row.getAttribute?.("data-grade-discipline-id") || row.querySelector?.(".colunaIdGradeDisciplina")?.textContent || "").trim(),
          code: texts[0] || "",
          course: texts[1] || "",
          grade: texts[2] || "",
          discipline: texts[3] || texts.find((text) => text && !/^\d+$/.test(text)) || "",
          tags,
          text: texts.filter(Boolean).join(" | ")
        };
      })
      .filter((record) => record.text && !/nenhum registro/i.test(record.text));
  }

  function disciplineRows() {
    return disciplineRecords().map((record) => record.text);
  }

  function tagCatalog() {
    const entries = safeQueryAll(document, 'input[name="disciplinaQuestaoTags"], input.flatDisciplinaQuestao').map((input) => {
      const fieldset = input.closest?.("fieldset");
      const legend = fieldset?.querySelector?.("legend");
      const wrapper = input.closest?.("label, .checkbox, li, div");
      const checkedWrapper = input.parentElement?.className || wrapper?.className || "";
      return {
        id: String(input.value || input.getAttribute?.("value") || "").trim(),
        label: String(input.getAttribute?.("text") || input.getAttribute?.("data-text") || compactText(wrapper) || "").replace(/\s+/g, " ").trim(),
        group: compactText(legend),
        selected: Boolean(input.checked || /\bchecked\b/i.test(String(checkedWrapper)))
      };
    }).filter((tag) => tag.id && tag.label && tag.group);
    const unique = [];
    const seen = new Set();
    entries.forEach((tag) => {
      const key = `${normalizedOption(tag.group)}:${tag.id}:${normalizedOption(tag.label)}`;
      if (seen.has(key)) return;
      seen.add(key);
      unique.push(tag);
    });
    const groups = {};
    unique.forEach((tag) => { groups[tag.group] = (groups[tag.group] || 0) + 1; });
    const graduation = unique.filter((tag) => normalizedOption(tag.group) === "graduacao");
    const signature = stableHash(unique.map((tag) => `${normalizedOption(tag.group)}:${tag.id}:${normalizedOption(tag.label)}`).sort().join("|"));
    return {
      mappedAt: new Date().toISOString(),
      total: unique.length,
      graduationCount: graduation.length,
      ignoredCount: unique.length - graduation.length,
      groups,
      signature,
      tags: unique,
      graduation
    };
  }

  function getTagCatalog() {
    const catalog = tagCatalog();
    if (!catalog.total) throw new Error("[CATALOGO_TAGS_NAO_VISIVEL] Abra o formulário Elaborador e deixe o Passo 3 carregado para mapear as tags atuais.");
    return catalog;
  }

  function elementDescriptor(element) {
    if (!element) return "";
    const attributes = ["title", "aria-label", "data-original-title", "data-title", "onclick", "href", "name", "id"]
      .map((name) => element.getAttribute?.(name) || "");
    return normalizedOption(`${compactText(element)} ${element.className || ""} ${attributes.join(" ")}`);
  }

  function questionIdFromRow(row) {
    const direct = ["data-id-questao", "data-question-id", "data-id", "value"]
      .map((name) => String(row.getAttribute?.(name) || "").trim())
      .find((value) => /^\d{4,12}$/.test(value));
    if (direct) return direct;
    const firstCell = Array.from(row.cells || [])[0];
    const firstMatch = compactText(firstCell).match(/\b(\d{4,12})\b/);
    if (firstMatch) return firstMatch[1];
    const attributes = safeQueryAll(row, "a, button, input, [data-id-questao], [data-question-id]")
      .flatMap((element) => ["data-id-questao", "data-question-id", "data-id", "value", "href", "onclick"].map((name) => element.getAttribute?.(name) || ""))
      .join(" ");
    const named = attributes.match(/(?:idQuestao|id_questao|questaoId|questionId)\D{0,12}(\d{4,12})/i);
    if (named) return named[1];
    const fallback = attributes.match(/\b(\d{5,12})\b/);
    return fallback ? fallback[1] : "";
  }

  function likeControlInfo(row) {
    const native=safeQueryAll(row, '.btn-Validada, .btn-Validar, .btn-Desativada').filter(isVisible);
    if(native.length) {
      const liked=native.some(e=>e.classList.contains('btn-Validada'));
      const disabled=native.some(e=>e.classList.contains('btn-Desativada'));
      const container=native.find(e=>e.classList.contains(liked?'btn-Validada':'btn-Validar'));
      const action=container?.querySelector('a[href]');
      let verified=null;
      if(action) {try {const u=new URL(action.getAttribute('href'),location.origin);if(u.origin===location.origin && u.pathname==='/DisciplinaQuestao/Validacao' && u.searchParams.get('tipo')===(liked?'voltarPadrao':'validar')) verified=action;} catch(_) {}}
      return {liked:disabled?false:liked,likeControl:!liked&&!disabled?verified:null,unlikeControl:liked?verified:null,reason:verified?'':disabled?'Questão invalidada.':'O AvaliA não permite alterar esta questão.'};
    }
    const controls = safeQueryAll(row, "button, a, input[type='button'], input[type='checkbox'], [role='button']")
      .map((element) => ({ element, descriptor: elementDescriptor(element) }))
      .filter((entry) => /thumbs[-_ ]?up|curtir|\blike\b|aprovar|validar|retirar|desmarcar/.test(entry.descriptor));
    if (!controls.length) return { liked: null, likeControl: null, unlikeControl: null, reason: "Controle de aprovação/like não reconhecido nesta linha." };
    let liked = null;
    let likeControl = null;
    let unlikeControl = null;
    controls.forEach((entry) => {
      const descriptor = entry.descriptor;
      const pressed = entry.element.getAttribute?.("aria-pressed");
      const explicitUnlike = /retirar|remover|descurtir|desmarcar/.test(descriptor);
      const explicitLike = !explicitUnlike && /curtir|\blike\b|aprovar|validar/.test(descriptor);
      const visualOn = pressed === "true" || entry.element.checked === true || /\b(active|checked|selected|btn-success|text-success|green|liked|validada|aprovada)\b/.test(descriptor);
      const visualOff = pressed === "false" || /\b(btn-default|text-muted|grey|gray|unliked|nao-validada|não-validada)\b/.test(descriptor);
      if (explicitUnlike) { liked = true; unlikeControl = unlikeControl || entry.element; }
      else if (explicitLike) { if (liked == null) liked = false; likeControl = likeControl || entry.element; }
      if (visualOn) { liked = true; unlikeControl = unlikeControl || entry.element; }
      else if (visualOff && liked == null) { liked = false; likeControl = likeControl || entry.element; }
    });
    if (liked === true && !unlikeControl && controls.length === 1) unlikeControl = controls[0].element;
    if (liked === false && !likeControl && controls.length === 1) likeControl = controls[0].element;
    return { liked, likeControl, unlikeControl, reason: liked == null ? "O controle existe, mas seu estado não é inequívoco." : "" };
  }

  function tagDataFromRow(row) {
    return safeQueryAll(row, "[data-id-tag], [data-tag-id], [data-tag], .tag, .label")
      .map((element) => ({
        id: String(element.getAttribute?.("data-id-tag") || element.getAttribute?.("data-tag-id") || element.getAttribute?.("value") || "").trim(),
        label: compactText(element),
        group: "Graduação"
      }))
      .filter((tag) => tag.id || tag.label);
  }

  function parseApprovalRow(row) {
    const id = questionIdFromRow(row);
    if (!id || /nenhum registro/i.test(compactText(row))) return null;
    const state = likeControlInfo(row);
    const cells = Array.from(row.cells || []);
    const disciplineCell = cells.find((cell) => /disciplina/i.test(String(cell.getAttribute?.("data-title") || cell.getAttribute?.("headers") || "")));
    return {
      id,
      liked: state.liked,
      discipline: compactText(disciplineCell),
      tags: tagDataFromRow(row),
      text: compactText(row).slice(0, 600),
      ambiguousReason: state.reason
    };
  }

  function selectedTagFilter(targetTag) {
    const targetId = String(targetTag?.id || "").trim();
    const targetLabel = normalizedOption(targetTag?.label || "");
    const controls = safeQueryAll(document, 'select[id*="Tag" i], select[name*="Tag" i], input[id*="Tag" i], input[name*="Tag" i], input[data-tag-id]');
    for (const control of controls) {
      let id = String(control.value || control.getAttribute?.("data-tag-id") || "").trim();
      let label = "";
      if (String(control.tagName || "").toLowerCase() === "select") label = String(control.options?.[control.selectedIndex]?.text || "").trim();
      else {
        if ((control.type === "checkbox" || control.type === "radio") && !control.checked) continue;
        label = String(control.getAttribute?.("text") || control.getAttribute?.("data-text") || compactText(control.closest?.("label")) || control.value || "").trim();
      }
      if ((targetId && id === targetId) || (targetLabel && normalizedOption(label) === targetLabel)) return { id, label, verified: true };
    }
    return { id: "", label: "", verified: false };
  }

  function selectedDiscipline(expectedDisciplines) {
    const expected = (Array.isArray(expectedDisciplines) ? expectedDisciplines : []).map((value) => String(value || "").replace(/\s+/g, " ").trim()).filter(Boolean);
    const candidates = safeQueryAll(document, 'select[id*="Disciplina" i], select[name*="Disciplina" i], [data-disciplina], .modal-title, h1, h2, h3, h4')
      .map((element) => {
        if (String(element.tagName || "").toLowerCase() === "select") return String(element.options?.[element.selectedIndex]?.text || "").trim();
        return String(element.getAttribute?.("data-disciplina") || compactText(element)).trim();
      }).filter(Boolean);
    for (const wanted of expected) {
      const normalizedWanted = normalizedOption(wanted);
      const found = candidates.find((candidate) => {
        const normalizedCandidate = normalizedOption(candidate);
        return normalizedCandidate === normalizedWanted || normalizedCandidate.includes(normalizedWanted) || normalizedWanted.includes(normalizedCandidate);
      });
      if (found) return { discipline: wanted, found, verified: true };
    }
    return { discipline: "", found: candidates[0] || "", verified: false };
  }

  function approvalTableData() {
    const tables = safeQueryAll(document, "table").filter((table) => isVisible(table));
    const candidates = tables.map((table) => {
      let rows = safeQueryAll(table, "tbody tr");
      let dataTableInfo = null;
      try {
        const $ = window.jQuery;
        if ($?.fn?.dataTable?.isDataTable?.(table)) {
          const api = $(table).DataTable();
          const appliedNodes = api.rows({ search: "applied" }).nodes();
          const allRows = typeof appliedNodes?.toArray === "function" ? appliedNodes.toArray() : Array.from(appliedNodes || []);
          const page = api.page?.info?.() || null;
          const settings = api.settings?.()[0];
          if (allRows.length) rows = allRows;
          dataTableInfo = {
            total: Number(page?.recordsDisplay ?? page?.recordsTotal ?? allRows.length) || allRows.length,
            serverSide: Boolean(settings?.oFeatures?.bServerSide),
            rowsRead: allRows.length
          };
        }
      } catch (_error) {
        dataTableInfo = null;
      }
      const parsed = rows.map(parseApprovalRow).filter(Boolean);
      return { table, rows, parsed, dataTableInfo };
    }).sort((left, right) => right.parsed.length - left.parsed.length);
    const chosen = candidates[0] || { table: null, rows: [], parsed: [] };
    let totalReported = chosen.dataTableInfo?.total || chosen.parsed.length;
    let scanComplete = Boolean(chosen.table && chosen.parsed.length && (!chosen.dataTableInfo || chosen.parsed.length >= totalReported));
    const container = chosen.table?.closest?.(".dataTables_wrapper, .modal, section, div") || document;
    const infoText = safeQueryAll(container, ".dataTables_info, [role='status']").map(compactText).find((text) => /\d/.test(text)) || "";
    const infoMatch = infoText.match(/(?:de|of)\s+([\d.]+)\s+(?:registros|entries)/i);
    if (infoMatch) {
      totalReported = Number(infoMatch[1].replace(/\D/g, "")) || chosen.parsed.length;
      scanComplete = chosen.parsed.length >= totalReported;
    }
    const next = safeQueryAll(container, ".paginate_button.next, [aria-label*='Próximo' i], [aria-label*='Next' i]").find(isVisible);
    if (next && !/disabled/.test(String(next.className || "")) && next.getAttribute?.("aria-disabled") !== "true") scanComplete = false;
    return { ...chosen, totalReported, scanComplete, infoText };
  }

  async function inspectApprovalWorkspace(payload) {
    ensureSiteErrorHooks();
    const targetTag = payload?.targetTag || {};
    const expectedDisciplines = payload?.expectedDisciplines || [];
    const table = approvalTableData();
    const tagFilter = selectedTagFilter(targetTag);
    const discipline = selectedDiscipline(expectedDisciplines);
    const pageText = normalizedOption(compactText(document.body));
    const allQuestionsView = /todas? questoes|todas? as questoes/.test(pageText);
    return {
      pageKind: loginDetected() ? "login" : /^\/(?:Professor|DisciplinaQuestao|GradeDisciplinaGerenciamento)/i.test(location.pathname) ? "professor" : "other",
      urlPath: location.pathname,
      allQuestionsView,
      activeTagFilter: tagFilter,
      tagFilterVerified: tagFilter.verified,
      discipline: discipline.discipline || discipline.found,
      disciplineVerified: discipline.verified,
      questions: table.parsed,
      totalReported: table.totalReported,
      scanComplete: table.scanComplete,
      infoText: table.infoText,
      recentSiteErrors: siteErrors.slice(-10),
      inspectedAt: new Date().toISOString()
    };
  }

  async function applyApprovalDecision(payload) {
    const questionId = String(payload?.questionId || "").trim();
    const desiredLiked = Boolean(payload?.desiredLiked);
    if (!/^\d+$/.test(questionId)) throw new Error("[LIKE_ID_INVALIDO] O ID da questão não é válido.");
    const workspace = await inspectApprovalWorkspace(payload);
    if (!workspace.allQuestionsView || !workspace.tagFilterVerified || !workspace.disciplineVerified) {
      throw new Error("[ESCOPO_LIKE_NAO_CONFIRMADO] A visão Todas questões, a disciplina e a tag precisam permanecer confirmadas.");
    }
    const table = approvalTableData();
    const matches = table.rows.filter((row) => questionIdFromRow(row) === questionId);
    if (matches.length !== 1) throw new Error(`[LIKE_LINHA_AMBIGUA] A questão ${questionId} apareceu ${matches.length} vez(es) na página atual.`);
    const before = likeControlInfo(matches[0]);
    if (before.liked === desiredLiked) return { id: questionId, desiredLiked, confirmed: true, alreadyCorrect: true };
    const control = desiredLiked ? before.likeControl : before.unlikeControl;
    if (!control) throw new Error(`[LIKE_CONTROLE_NAO_RECONHECIDO] Não há uma ação inequívoca para ${desiredLiked ? "aprovar" : "retirar o like de"} ${questionId}.`);
    control.click();
    try {
      await waitFor(() => {
        const currentTable = approvalTableData();
        const currentRow = currentTable.rows.find((row) => questionIdFromRow(row) === questionId);
        if (!currentRow) return false;
        return likeControlInfo(currentRow).liked === desiredLiked;
      }, 12000, "");
      return { id: questionId, desiredLiked, confirmed: true, alreadyCorrect: false };
    } catch (_error) {
      return { id: questionId, desiredLiked, confirmed: false, indeterminate: true, message: "O clique foi feito, mas o AvaliA não apresentou uma confirmação inequívoca. A extensão não repetirá a ação." };
    }
  }

  function getState() {
    ensureSiteErrorHooks();
    const form = document.getElementById("formSalvarQuestao");
    const activeSource = document.querySelector(".btnFonteQuestao.active");
    const sourceField = document.getElementById("Questao_IdFonte");
    const institutionField = document.getElementById("Instituicao_IdInstituicao");
    const questionIdField = document.getElementById("Questao_IdQuestao");
    const snapshot = form ? formSnapshot() : null;
    const alternativePolicy = discoverAlternativePolicy(relevantMessages());
    const editors = editorHealth(snapshot?.questionFormat);
    const isLogin = loginDetected();
    const supportedPage = location.hostname === "avalia.grupoa.com.br" && /^\/Elaborador\/?/i.test(location.pathname);
    const tags = tagCatalog();
    const disciplineDetails = disciplineRecords();
    const roleText = Array.from(document.querySelectorAll('#usuarioPerfil > a, [data-perfil], [data-role], .perfil, .user-role, a[href*="Perfil" i]'))
      .map((element) => (element.innerText || element.textContent || "").replace(/\s+/g, " ").trim())
      .find(Boolean) || "";
    return {
      supportedPage,
      loginDetected: isLogin,
      pageKind: isLogin ? "login" : supportedPage ? "elaborador" : /professor\s*\/\s*tutor/i.test(roleText) || /^\/(?:Professor|CorrecaoDiscursiva|AssociarConteudoDisciplina)(?:\/|$)/i.test(location.pathname) ? "professor" : "other",
      roleName: roleText,
      formReady: Boolean(form && document.getElementById("TextoQuestao")),
      currentStep: currentStep(),
      activeSource: activeSource ? (activeSource.innerText || "").trim() : "",
      activeSourceId: activeSource ? activeSource.getAttribute("IdFonte") || activeSource.getAttribute("idfonte") || "" : "",
      sourceId: sourceField ? sourceField.value : "",
      institutionId: institutionField ? institutionField.value : "",
      institutionName: document.getElementById("Instituicao_Nome")?.value || "",
      disciplines: disciplineRows(),
      disciplineRecords: disciplineDetails,
      tagCatalog: tags,
      alternativeCount: snapshot ? snapshot.alternativeCount : readAlternativeCount(),
      visibleAlternativeCount: snapshot ? snapshot.visibleAlternativeCount : readVisibleAlternativeCount(),
      questionId: questionIdField ? questionIdField.value : "",
      questionName: document.getElementById("Questao_Nome")?.value || "",
      questionFormat: snapshot?.questionFormat || currentFormFormat(),
      bodyText: snapshot ? snapshot.bodyText : "",
      expectedResponseText: snapshot ? snapshot.expectedResponseText : "",
      alternatives: snapshot ? snapshot.alternatives : [],
      feedbackText: snapshot ? snapshot.feedbackText : "",
      correctIndex: snapshot ? snapshot.correctIndex : -1,
      typeId: snapshot ? snapshot.typeId : "",
      cognitiveId: snapshot ? snapshot.cognitiveId : "",
      alternativePolicy,
      editors,
      editorsReady: editors.allReady,
      pageBusy: pageBusy(),
      recentSiteErrors: siteErrors.filter((entry) => Date.now() - new Date(entry.at).getTime() < 10 * 60 * 1000).slice(-10),
      modalOpen: isVisible(document.getElementById("myModal2")),
      checkedAt: new Date().toISOString()
    };
  }

  function discursiveTypeOption() {
    return selectOptions("#Questao_IdTipoQuestao").find((option) =>
      /\b(?:discursiv|dissertativ|resposta aberta)\w*/i.test(normalizedOption(option.label))
    ) || null;
  }

  function ensureQuestionTypeSupported(question) {
    if (questionFormat(question) !== "discursive") return true;
    const option = discursiveTypeOption();
    if (!option) {
      const available = selectOptions("#Questao_IdTipoQuestao").map((item) => item.label).join(", ");
      throw new Error(`[TIPO_DISCURSIVO_INDISPONIVEL] O perfil atual do AvaliA não apresentou a opção de questão discursiva.${available ? ` Tipos encontrados: ${available}.` : ""}`);
    }
    return true;
  }

  function getCatalog() {
    const types = selectOptions("#Questao_IdTipoQuestao");
    const discursive = types.find((option) => /\b(?:discursiv|dissertativ|resposta aberta)\w*/i.test(normalizedOption(option.label))) || null;
    return {
      types,
      cognitiveLevels: selectOptions("#IdHabilidadeQuestao"),
      supportsDiscursive: Boolean(discursive),
      discursiveType: discursive,
      bridgeVersion: BRIDGE_VERSION
    };
  }

  function diagnoseWorkspace(payload) {
    const state = getState();
    const expectedDraftId = String(payload && payload.expectedDraftId || "");
    const issues = [];
    const add = (code, severity, message, repairable, action, cause, impact) => issues.push({
      code,
      severity,
      message,
      repairable: Boolean(repairable),
      action: action || "",
      cause: cause || message,
      impact: impact || (severity === "blocking" ? "O lote não será iniciado enquanto este item não estiver resolvido." : "A execução pode continuar com atenção.")
    });
    if (state.loginDetected) {
      add("AVALIA_SESSAO_EXPIRADA", "blocking", "A sessão do AvaliA está na tela de acesso.", false, "Entre novamente e reabra Elaborador; depois clique em Testar perfil.", "A página atual é a tela de autenticação ou uma resposta do site redirecionou para ela.", "Nenhum arquivo será preenchido ou salvo nesta sessão.");
    } else if (!state.supportedPage) {
      add("PAGINA_INCORRETA", "blocking", state.pageKind === "professor" ? "Tela azul reconhecida. Para cadastrar questões, use Ferramentas → Elaborador." : "Abra Ferramentas e escolha Elaborador para cadastrar questões.", false, "Ferramentas → Elaborador", "O cadastro de questões utiliza o perfil Elaborador; a tela azul oferece bancos, correção e relatórios.");
    } else if (!state.modalOpen || !state.formReady) {
      add("FORMULARIO_FECHADO", "blocking", "Abra Elabore Novas Questões e avance na configuração.", false, "Abrir o formulário do AvaliA", "O formulário de criação ainda não está presente na página.");
    }
    if (state.formReady && !state.institutionId && state.institutionName) {
      add("VINCULO_INSTITUCIONAL_INCOMPLETO", "blocking", `O AvaliA mostra “${state.institutionName}”, mas não retornou o identificador institucional obrigatório.`, false, "Repita uma vez a seleção IES no Passo 1. Se continuar vazio, solicite ao suporte o vínculo Elaborador + IES deste professor.", "O nome visual da IES foi carregado, porém Instituicao_IdInstituicao permaneceu vazio.", "O AvaliA recusará ou deixará indeterminado o salvamento; a extensão não forçará um ID de outra conta.");
    } else if (state.formReady && !state.institutionId) {
      add("INSTITUICAO_AUSENTE", "blocking", "A instituição ainda não foi confirmada.", false, "Confirmar a IES no Passo 1");
    }
    if (state.formReady && !state.sourceId && (state.activeSourceId || state.activeSource)) {
      add("VINCULO_FONTE_INCOMPLETO", "blocking", `A fonte “${state.activeSource || state.activeSourceId}” aparece selecionada, mas o AvaliA não gravou o identificador da fonte.`, false, "Volte ao Passo 1 e selecione IES novamente. Se persistir, o perfil precisa ser corrigido pelo suporte.", "O botão de fonte está ativo, mas Questao_IdFonte está vazio.", "A criação da questão não tem uma origem válida e será bloqueada antes do primeiro preenchimento.");
    } else if (state.formReady && !state.sourceId) {
      add("FONTE_AUSENTE", "blocking", "A fonte da questão ainda não foi confirmada.", false, "Selecionar IES no Passo 1");
    }
    if (state.formReady && !state.disciplines.length) add("DISCIPLINA_AUSENTE", "blocking", "Nenhuma disciplina foi adicionada.", false, "Adicionar uma disciplina no Passo 3");
    if (state.formReady && state.currentStep !== "step-4" && (!expectedDraftId || !state.questionId || state.questionId === "0")) {
      add("ETAPA_INCORRETA", "blocking", `O formulário está em ${state.currentStep || "uma etapa desconhecida"}; o preenchimento começa no Passo 4.`, false, "Conclua manualmente as escolhas dos Passos 1–3 e abra o Passo 4");
    }
    if (state.formReady && !expectedDraftId && state.questionId && state.questionId !== "0") {
      add("FORMULARIO_OCUPADO", "blocking", `O formulário está vinculado à questão ${state.questionId}.`, false, "Abra uma nova questão vazia antes de iniciar outro lote");
    }
    if (state.formReady && state.questionFormat !== "discursive" && state.alternativePolicy?.explicit && !state.alternativePolicy.allowsFour) {
      add("PERFIL_EXIGE_CINCO", "blocking", `Esta configuração do AvaliA exige ${state.alternativePolicy.min === state.alternativePolicy.max ? `exatamente ${state.alternativePolicy.min}` : `mínimo ${state.alternativePolicy.min ?? "?"} e máximo ${state.alternativePolicy.max ?? "?"}`} afirmativas.`, false, "Use uma configuração que aceite A–D; a extensão não criará uma alternativa E artificial");
    }
    if (state.currentStep === "step-4" && state.questionFormat !== "discursive" && state.alternativeCount !== REQUIRED_ALTERNATIVES) add("alternative-count", "blocking", "O formulário objetivo não está com quatro alternativas.", true, "Ajustar para A–D");
    if (state.currentStep === "step-4" && !selectOptions("#Questao_IdTipoQuestao").length) add("type-catalog-missing", "blocking", "A lista de tipos não foi carregada para este perfil.", false, "Reabra manualmente o Passo 4 antes de preencher");
    if (state.currentStep === "step-4" && !selectOptions("#IdHabilidadeQuestao").length) add("cognitive-catalog-missing", "blocking", "A lista de níveis cognitivos não foi carregada para este perfil.", false, "Reabra manualmente o Passo 4 antes de preencher");
    if (state.currentStep === "step-4" && !state.editorsReady) add("EDITORES_NAO_INICIALIZADOS", "blocking", `Os editores do AvaliA ainda não terminaram de carregar (${state.editors.ready}/${state.editors.required}).`, false, "Aguarde ou reabra manualmente o Passo 4; a extensão não voltará ao Passo 3", "Um ou mais campos TinyMCE ainda não estão utilizáveis.", "Preencher agora poderia cortar texto, imagens, fórmulas ou caracteres especiais.");
    if (state.pageBusy) add("AVALIA_OCUPADO", "warning", "O AvaliA ainda está processando dados nesta tela.", true, "Aguardar o processamento terminar antes de executar");
    if (expectedDraftId && state.questionId && state.questionId !== "0" && state.questionId !== expectedDraftId) add("draft-mismatch", "blocking", `A tela mostra a questão ${state.questionId}, mas a sessão espera ${expectedDraftId}.`, false, "Conferir a questão aberta");
    const recentCritical = (state.recentSiteErrors || []).filter((entry) => ["AVALIA_SESSAO_EXPIRADA", "AVALIA_SEM_PERMISSAO"].includes(entry.code) && !(state.loginDetected && entry.code === "AVALIA_SESSAO_EXPIRADA"));
    if (recentCritical.length) {
      const latest = recentCritical[recentCritical.length - 1];
      add(latest.code, "blocking", latest.code === "AVALIA_SESSAO_EXPIRADA" ? "O próprio AvaliA informou que a sessão expirou (HTTP 401)." : "O próprio AvaliA recusou a ação para este usuário (HTTP 403).", false, latest.code === "AVALIA_SESSAO_EXPIRADA" ? "Entrar novamente no AvaliA e reabrir o formulário" : "Confirmar as permissões do perfil de professor");
    }
    const transient = (state.recentSiteErrors || []).filter((entry) => ["AVALIA_REDE", "AVALIA_SERVIDOR"].includes(entry.code));
    if (transient.length) add("avalia-transient-errors", "warning", `${transient.length} falha(s) recente(s) de rede/servidor foram registradas pelo próprio AvaliA.`, true, "Executar recuperação segura e retomar do último marco");
    const blocking = issues.filter((issue) => issue.severity === "blocking");
    const firstBlocking = blocking[0] || null;
    const checkIssue = (...codes) => issues.find((issue) => codes.includes(issue.code));
    const check = (key, label, ok, detail, issue) => ({ key, label, status: issue ? (issue.severity === "blocking" ? "error" : "warning") : ok ? "ok" : "pending", detail, code: issue?.code || "" });
    const profileChecks = [
      check("session", "Sessão", !state.loginDetected && state.supportedPage, state.loginDetected ? "Acesso expirado" : state.supportedPage ? "Acesso ativo" : "Abra Elaborador", checkIssue("AVALIA_SESSAO_EXPIRADA", "PAGINA_INCORRETA")),
      check("form", "Formulário", state.formReady && state.modalOpen, state.formReady && state.modalOpen ? `Aberto em ${state.currentStep || "etapa detectada"}` : "Abra uma nova questão", checkIssue("FORMULARIO_FECHADO")),
      check("source", "Fonte IES", Boolean(state.sourceId), state.sourceId ? `Vínculo ${state.sourceId} confirmado` : state.activeSource ? `${state.activeSource} sem vínculo interno` : "Não selecionada", checkIssue("VINCULO_FONTE_INCOMPLETO", "FONTE_AUSENTE")),
      check("institution", "Instituição", Boolean(state.institutionId), state.institutionId ? `${state.institutionName || "IES"} confirmada` : state.institutionName ? `${state.institutionName} sem ID` : "Não confirmada", checkIssue("VINCULO_INSTITUCIONAL_INCOMPLETO", "INSTITUICAO_AUSENTE")),
      check("discipline", "Disciplina", state.disciplines.length > 0, state.disciplines.length ? `${state.disciplines.length} adicionada(s)` : "Nenhuma adicionada", checkIssue("DISCIPLINA_AUSENTE")),
      check("editors", "Editores", state.currentStep !== "step-4" || state.editorsReady, state.currentStep === "step-4" ? `${state.editors.ready}/${state.editors.required} prontos` : "Verificados no Passo 4", checkIssue("EDITORES_NAO_INICIALIZADOS"))
    ];
    const ready = blocking.length === 0;
    return {
      state,
      issues,
      ready,
      repairableCount: issues.filter((issue) => issue.repairable).length,
      catalog: state.formReady ? getCatalog() : { types: [], cognitiveLevels: [], bridgeVersion: BRIDGE_VERSION },
      preflight: {
        checkedAt: state.checkedAt,
        status: ready ? "ready" : state.loginDetected ? "login" : "blocked",
        code: firstBlocking?.code || "PRONTO",
        title: ready ? "Perfil pronto para executar" : firstBlocking?.message || "Configuração incompleta",
        cause: firstBlocking?.cause || "Todos os vínculos e componentes obrigatórios foram reconhecidos.",
        impact: firstBlocking?.impact || "O arquivo pode ser interpretado e o lote poderá começar após sua confirmação.",
        action: firstBlocking?.action || "Selecione o DOCX ou prossiga com o lote revisado.",
        checks: profileChecks
      }
    };
  }

  async function diagnoseAndRepair(payload) {
    let diagnosis = diagnoseWorkspace(payload);
    const repaired = [];
    if (!diagnosis.state.supportedPage || !diagnosis.state.formReady) return { ...diagnosis, repaired };
    await waitForPageIdle(12000);
    if (diagnosis.state.currentStep !== "step-4") return { ...diagnosis, repaired, manualSetupBoundary: true };
    diagnosis = diagnoseWorkspace(payload);
    if (diagnosis.state.currentStep === "step-4" && diagnosis.state.questionFormat !== "discursive" && diagnosis.issues.some((issue) => issue.code === "alternative-count")) {
      await setAlternativeCount(REQUIRED_ALTERNATIVES);
      repaired.push("A quantidade de alternativas foi ajustada para A–D.");
    }
    await waitForPageIdle(8000);
    diagnosis = diagnoseWorkspace(payload);
    return { ...diagnosis, repaired };
  }

  async function recoverStalledWorkspace(payload) {
    const phase = String(payload?.phase || "");
    const unsafe = ["saving", "submitting", "needs_verification"].includes(phase);
    if (unsafe) throw new Error(`[RECUPERACAO_BLOQUEADA] A extensão não fará nova ação durante “${phase}”, pois um salvamento ou envio pode ter ocorrido. Confira o registro antes de continuar.`);
    const expectedDraftId = String(payload?.expectedDraftId || "");
    const actions = [];
    const before = getState();
    if (expectedDraftId && before.questionId && before.questionId !== "0" && String(before.questionId) !== expectedDraftId) {
      throw new Error(`[RASCUNHO_DIVERGENTE] A tela está na questão ${before.questionId}, mas o marco salvo espera ${expectedDraftId}. Nenhum campo foi forçado.`);
    }
    if (/^step-[1-3]$/.test(before.currentStep)) {
      const diagnosis = diagnoseWorkspace({ expectedDraftId });
      return { recovered: false, actions, diagnosis, state: diagnosis.state, checkpointPreserved: true, safeToContinue: false, manualSetupBoundary: true };
    }
    const idle = await waitForPageIdle(15000);
    if (!idle) throw new Error("[AVALIA_OCUPADO] O AvaliA continua processando uma requisição. A extensão pausou para não sobrepor ações.");
    const preview = document.getElementById("myModal3");
    if (isVisible(preview)) {
      const $ = window.jQuery;
      if ($ && typeof $(preview).modal === "function") $(preview).modal("hide");
      else preview.style.display = "none";
      actions.push("A visualização que permaneceu aberta foi fechada.");
    }
    const tiny = getTinyMce();
    if (tiny && Array.isArray(tiny.editors)) tiny.editors.forEach((editor) => { if (typeof editor.save === "function") editor.save(); });
    if (currentStep() === "step-4" && currentFormFormat() !== "discursive" && (!expectedDraftId || !getState().questionId || getState().questionId === "0")) {
      await setAlternativeCount(REQUIRED_ALTERNATIVES);
      actions.push("As quatro alternativas A–D foram resincronizadas.");
    }
    await waitForPageIdle(8000);
    const diagnosis = diagnoseWorkspace({ expectedDraftId });
    return { recovered: diagnosis.ready, actions, diagnosis, state: diagnosis.state, checkpointPreserved: true, safeToContinue: diagnosis.ready };
  }

  function getSiteErrors() {
    ensureSiteErrorHooks();
    return { errors: siteErrors.slice(), count: siteErrors.length };
  }

  async function fillQuestion(payload) {
    const question = payload && payload.question;
    validateQuestionPayload(question);
    const format = questionFormat(question);
    const state = getState();
    if (!state.supportedPage || !state.formReady) throw new Error("[FORMULARIO_FECHADO] Abra Elaborador, inicie uma nova questão e avance até o Passo 4.");
    if (state.currentStep !== "step-4") throw new Error("[ETAPA_INCORRETA] O Passo 4, Elabore questão, precisa estar aberto.");
    assertProfileLinkage(state);
    if (format === "discursive" && question.suggestedTagLabel) {
      const expected = tagCatalog().graduation.filter(tag => normalizedOption(tag.label) === normalizedOption(question.suggestedTagLabel));
      if (expected.length !== 1) throw new Error(`[TAG_DISCURSIVA_NAO_CONFIRMADA] Mapeie a tag “${question.suggestedTagLabel}” no Passo 3. O catálogo atual está ausente ou ambíguo; nenhum envio foi realizado.`);
      if (expected.length === 1 && (!state.disciplineRecords?.length || state.disciplineRecords.some(row =>
        !row.tags.some(tag => tag.id === expected[0].id) || row.tags.some(tag => /^discursiva\b/.test(normalizedOption(tag.label)) && tag.id !== expected[0].id)))) {
        throw new Error(`[TAG_DISCURSIVA_DIVERGENTE] ${question.name}: confira a alocação no Passo 3 e use a tag “${question.suggestedTagLabel}” em cada disciplina. Nenhum campo foi preenchido e nenhuma questão foi salva.`);
      }
    }
    if (state.questionId && state.questionId !== "0") throw new Error("A tela atual já corresponde a um rascunho salvo. Prepare uma nova questão antes de preencher.");

    const idle = await waitForPageIdle(12000);
    if (!idle) throw new Error("[AVALIA_OCUPADO] O AvaliA não terminou o carregamento do formulário dentro do limite seguro.");
    const nameField = document.getElementById("Questao_Nome");
    if (nameField.readOnly && nameField.value.trim() && normalizedText(nameField.value) !== normalizedText(question.name)) throw new Error("[NOME_BLOQUEADO] O AvaliA bloqueou a edição do nome. Abra um cadastro que permita acrescentar o ano e semestre antes de enviar.");
    ensureQuestionTypeSupported(question);
    setField("#Questao_Nome", question.name);
    setSelect("#Questao_IdTipoQuestao", question.typeId, question.typeLabel);
    await waitFor(
      () => currentFormFormat() === format && editorHealth(format).allReady,
      15000,
      `[EDITORES_NAO_INICIALIZADOS] O AvaliA não preparou os editores do modelo ${format === "discursive" ? "discursivo" : "objetivo"} após a seleção do tipo.`
    );
    if (question.cognitiveId) setSelect("#IdHabilidadeQuestao", question.cognitiveId, question.cognitiveLabel);
    setEditor("TextoQuestao", question.bodyHtml);
    if (format === "discursive") {
      setEditor("TextoPadraoResposta", question.expectedResponseHtml || `<p>${question.expectedResponseText || ""}</p>`);
      ["A", "B", "C", "D", "E"].forEach((letter) => setEditorIfPresent(`TextoAfirmativa${letter}`, ""));
      uncheckAllAnswers();
    } else {
      await setAlternativeCount(REQUIRED_ALTERNATIVES);
      question.alternatives.forEach((alternative, index) => {
        setEditor(`TextoAfirmativa${"ABCD"[index]}`, alternative.html || `<p>${alternative.plain || ""}</p>`);
      });
      setEditor("TextoAfirmativaE", "");
      setEditorIfPresent("TextoPadraoResposta", "");
      setCorrectAlternative(question.correctIndex);
    }
    setEditor("TextoFeedbackQuestao", question.feedbackHtml);
    if (payload.fillKeywords) setKeywords(question.keywords || []);
    else clearKeywords();

    const verification = compareQuestion(question, { metadataMode: "strict" });
    if (!verification.matches) throw new Error(`[DIVERGENCIA_DE_CAMPO] O preenchimento ficou diferente do DOCX em: ${verification.mismatches.join(", ")}.`);
    return {
      name: verification.actual.name,
      alternativeCount: verification.actual.alternativeCount,
      correctLetter: format === "discursive" ? "" : "ABCD"[question.correctIndex],
      questionFormat: format,
      type: question.typeLabel,
      cognitive: question.cognitiveLabel,
      verified: true
    };
  }

  function relevantMessages() {
    const selectors = [
      ".field-validation-error",
      ".validation-summary-errors",
      ".alert-danger",
      ".alert-warning",
      ".toast-message",
      ".ui-pnotify-text",
      ".noty_body",
      ".jconfirm-content"
    ];
    return Array.from(new Set(Array.from(document.querySelectorAll(selectors.join(",")))
      .filter(isVisible)
      .map((element) => (element.innerText || element.textContent || "").replace(/\s+/g, " ").trim())
      .filter((message) => message && !/m[ií]nimo 4 alternativas/i.test(message))));
  }

  function goToStep(stepNumber) {
    const $ = window.jQuery;
    const wizard = $ && $("#wizard");
    if (!wizard || !wizard.length || typeof wizard.smartWizard !== "function") {
      throw new Error("O assistente de etapas do AvaliA não está disponível.");
    }
    for (let index = 1; index <= stepNumber; index += 1) wizard.smartWizard("enableStep", index);
    wizard.smartWizard("goToStep", stepNumber);
  }

  function numericStep() {
    const match = currentStep().match(/step-(\d+)/);
    return match ? Number(match[1]) : 0;
  }

  async function waitForPageIdle(timeoutMs) {
    const startedAt = Date.now();
    let stableChecks = 0;
    while (Date.now() - startedAt < timeoutMs) {
      if (!pageBusy()) {
        stableChecks += 1;
        if (stableChecks >= 3) return true;
      } else {
        stableChecks = 0;
      }
      await delay(250);
    }
    return false;
  }

  function assertProfileLinkage(state) {
    const current = state || getState();
    if (current.loginDetected) throw new Error("[AVALIA_SESSAO_EXPIRADA] A sessão está na tela de acesso. Entre novamente e execute o teste de perfil.");
    if (!current.supportedPage) throw new Error("[PAGINA_INCORRETA] Abra a página Elaborador do AvaliA.");
    if (!current.institutionId && current.institutionName) {
      throw new Error(`[VINCULO_INSTITUCIONAL_INCOMPLETO] O AvaliA mostra “${current.institutionName}”, mas Instituicao_IdInstituicao está vazio. A extensão não forçará um identificador; repita o Passo 1 ou solicite a correção do vínculo Elaborador + IES.`);
    }
    if (!current.sourceId && (current.activeSourceId || current.activeSource)) {
      throw new Error(`[VINCULO_FONTE_INCOMPLETO] A fonte “${current.activeSource || current.activeSourceId}” aparece selecionada, mas Questao_IdFonte está vazio. Repita a seleção no Passo 1 ou solicite a correção do perfil.`);
    }
    if (!current.sourceId) throw new Error("[FONTE_AUSENTE] Selecione a fonte IES no Passo 1.");
    if (!current.institutionId) throw new Error("[INSTITUICAO_AUSENTE] Confirme a instituição no Passo 1.");
    if (!current.disciplines.length) throw new Error("[DISCIPLINA_AUSENTE] Nenhuma disciplina foi adicionada no Passo 3.");
    return current;
  }

  async function moveToStep(stepNumber, label) {
    if (numericStep() >= stepNumber) return currentStep();
    let lastError = null;
    for (let attempt = 1; attempt <= 3; attempt += 1) {
      try {
        await waitForPageIdle(8000);
        goToStep(stepNumber);
        await waitFor(() => numericStep() >= stepNumber, 18000, "");
        await waitForPageIdle(10000);
        return currentStep();
      } catch (error) {
        lastError = error;
        await delay(500 * attempt);
      }
    }
    const message = `O AvaliA não confirmou a etapa ${label || stepNumber} após 3 tentativas controladas.${lastError?.message ? ` ${lastError.message}` : ""}`;
    recordSiteError({ source: "wizard", code: "AVALIA_ETAPA_TRAVADA", message });
    throw new Error(`[AVALIA_ETAPA_TRAVADA] ${message}`);
  }

  async function previewQuestionForOfficialSubmission() {
    if (currentStep() !== "step-4") throw new Error("A questão precisa estar no Passo 4 para a visualização obrigatória.");
    const button = document.getElementById("btnVisualizarOnline");
    const modal = document.getElementById("myModal3");
    if (!button || !modal) throw new Error("A visualização obrigatória da questão não foi localizada.");

    button.click();
    await waitFor(
      () => isVisible(modal),
      30000,
      "O AvaliA não concluiu a visualização obrigatória da questão."
    );

    const $ = window.jQuery;
    if ($ && typeof $(modal).modal === "function") $(modal).modal("hide");
    else modal.style.display = "none";
    await waitFor(() => !isVisible(modal), 8000, "A janela de visualização não pôde ser fechada.");
    window.visualizouQuestao = true;
  }

  async function completeBibliographicStep() {
    if (numericStep() > 5) return { required: false, found: false, resumed: true };
    await moveToStep(5, "de referências bibliográficas");
    await waitFor(
      () => document.getElementById("FormularioReferenciasBibliograficas"),
      30000,
      "O AvaliA não carregou a etapa de referências bibliográficas."
    );

    const referencesRequired = window.obrigaCadastroReferenciasBibliograficas === true;
    const hasReference = Boolean(document.querySelector("#tableReferencias .idQuestaoReferencia"));
    if (referencesRequired && !hasReference) {
      throw new Error("O AvaliA exige referência bibliográfica para esta questão. Cadastre-a antes do envio oficial.");
    }
    await waitForPageIdle(12000);
    return { required: referencesRequired, found: hasReference };
  }

  function pendingCorrectionButtons() {
    return [
      ...document.querySelectorAll(".btn-ignorarCorrecaoOrtografica"),
      ...document.querySelectorAll(".btn-ignorarNormaRevisao")
    ].filter((button) => !button.disabled && isVisible(button));
  }

  async function completeCorrectionStep() {
    await moveToStep(6, "de correção obrigatória");

    if (currentStep() === "step-7") return { ignoredSuggestions: 0 };

    await waitFor(
      () => document.getElementById("formSalvarQuestaoCorrecao") || currentStep() === "step-7",
      45000,
      "O AvaliA não concluiu a verificação ortográfica."
    );
    if (currentStep() === "step-7") return { ignoredSuggestions: 0 };

    let ignoredSuggestions = 0;
    for (let guard = 0; guard < 80; guard += 1) {
      const button = pendingCorrectionButtons()[0];
      if (!button) break;
      button.click();
      ignoredSuggestions += 1;
      await delay(180);
    }
    if (pendingCorrectionButtons().length) throw new Error("O limite seguro de sugestões de correção foi atingido.");

    const pendingActions = Array.from(document.querySelectorAll('input[name="AcaoAplicada[]"]'))
      .filter((field) => !field.value || field.value === "Pendente");
    if (pendingActions.length) throw new Error("Nem todas as sugestões de correção foram analisadas automaticamente.");
    const saveButton = document.getElementById("btnSubmitCorrecaoOrtografica");
    if (!saveButton) throw new Error("O botão para concluir a correção obrigatória não foi localizado.");
    await waitFor(() => !saveButton.disabled, 10000, "O AvaliA não liberou a conclusão da correção obrigatória.");
    saveButton.click();

    await waitFor(
      () => currentStep() === "step-7",
      60000,
      "O AvaliA não confirmou a conclusão da correção obrigatória."
    );
    return { ignoredSuggestions };
  }

  async function prepareOfficialSubmission(payload) {
    const question = payload && payload.question;
    const state = getState();
    if (!state.formReady || numericStep() < 4 || numericStep() > 7) throw new Error("A questão precisa estar entre os Passos 4 e 7 para ser concluída.");
    assertProfileLinkage(state);
    if (!state.questionId || state.questionId === "0") throw new Error("Salve a questão antes de iniciar o envio oficial.");
    if (state.sourceId !== "111" && !/\bIES\b/i.test(state.activeSource || "")) throw new Error("O fluxo oficial automático está habilitado somente para questões da fonte IES.");
    const initialVerification = verifyCurrentQuestion({ question, metadataMode: "post-save" });

    if (numericStep() === 4) await previewQuestionForOfficialSubmission();
    const references = numericStep() <= 5 ? await completeBibliographicStep() : { required: false, found: false, resumed: true };
    const corrections = await completeCorrectionStep();
    if (currentStep() !== "step-7") throw new Error("O Passo 7 de envio oficial não foi alcançado.");
    const finalVerification = verifyCurrentQuestion({ question, metadataMode: "post-save" });
    return { id: state.questionId, references, corrections, ready: true, warnings: [...(initialVerification.warnings || []), ...(finalVerification.warnings || [])] };
  }

  const submissionGuards = new Map();

  function responseSucceeded(data) {
    return Boolean(data && (data.type === "success" || data.success === true || data.sucesso === true));
  }

  function nextScreenReady(originalId, nextMode) {
    const state = getState();
    if (nextMode === "same") {
      return state.formReady && state.currentStep === "step-4" && state.editorsReady
        && Boolean(state.sourceId && state.institutionId && state.disciplines.length)
        && (!state.questionId || state.questionId === "0")
        && String(state.questionId || "") !== String(originalId || "");
    }
    return state.currentStep === "step-1" || !state.modalOpen;
  }

  function observeAjaxOrTransition(urlFragment, trigger, transitionCondition, timeoutMs) {
    const $ = window.jQuery;
    if (!$) throw new Error("A comunicação interna do AvaliA não está disponível.");
    return new Promise((resolve, reject) => {
      const namespace = `.avaliaAutoBatch${Date.now()}${Math.floor(Math.random() * 10000)}`;
      let settled = false;
      const cleanup = () => {
        window.clearTimeout(timer);
        window.clearInterval(poller);
        $(document).off(`ajaxComplete${namespace}`);
      };
      const succeed = (value) => {
        if (settled) return;
        settled = true;
        cleanup();
        resolve(value);
      };
      const fail = (error) => {
        if (settled) return;
        settled = true;
        cleanup();
        reject(error);
      };
      const timer = window.setTimeout(() => {
        recordSiteError({ source: "submission", code: "AVALIA_ENVIO_SEM_CONFIRMACAO", url: urlFragment, message: "Tempo esgotado sem confirmação inequívoca" });
        fail(new Error("[ENVIO_INDETERMINADO] O AvaliA não confirmou o envio dentro do tempo seguro. A extensão não repetirá o clique até verificar o estado."));
      }, timeoutMs);
      const poller = window.setInterval(() => {
        try {
          if (transitionCondition()) succeed({ type: "success", message: "Envio confirmado pela mudança de tela.", confirmedBy: "transition" });
        } catch (_error) {
          // A tela pode estar sendo reconstruída durante alguns milissegundos.
        }
      }, 250);
      $(document).on(`ajaxComplete${namespace}`, (_event, xhr, settings) => {
        if (!String(settings && settings.url || "").includes(urlFragment)) return;
        if (responseLooksLikeLogin(xhr)) {
          recordSiteError({ source: "submission", code: "AVALIA_SESSAO_EXPIRADA", status: xhr?.status, url: settings?.url, message: "O AvaliA devolveu a tela de acesso durante o envio." });
          fail(new Error("[AVALIA_SESSAO_EXPIRADA] A sessão expirou durante o envio. Entre novamente e confira o registro antes de continuar."));
          return;
        }
        let data = xhr.responseJSON;
        if (!data && xhr.responseText) {
          try { data = JSON.parse(xhr.responseText); } catch (_error) { data = null; }
        }
        if (!data) {
          recordSiteError({ source: "submission", code: "AVALIA_RESPOSTA_INDETERMINADA", status: xhr?.status, url: settings?.url, message: "Resposta sem resultado reconhecível" });
          fail(new Error("[ENVIO_INDETERMINADO] O AvaliA respondeu sem um resultado reconhecível; nenhum novo clique será feito automaticamente."));
        } else if (!responseSucceeded(data)) {
          recordSiteError({ source: "submission", code: "AVALIA_RECUSA_ENVIO", status: xhr?.status, url: settings?.url, message: data.message || "Envio recusado" });
          fail(new Error(data.message || "O AvaliA recusou o envio oficial."));
        }
        else succeed({ ...data, confirmedBy: "response" });
      });
      try {
        trigger();
      } catch (error) {
        fail(error);
      }
    });
  }

  async function submitOfficial(payload) {
    const question = payload && payload.question;
    const state = getState();
    if (state.currentStep !== "step-7") throw new Error("A questão ainda não está pronta no Passo 7.");
    if (!state.questionId || state.questionId === "0") throw new Error("O identificador da questão não foi localizado.");
    verifyCurrentQuestion({ question, metadataMode: "post-save" });

    const nextMode = payload && payload.nextMode === "same" ? "same" : "fresh";
    const existingGuard = submissionGuards.get(String(state.questionId));
    if (existingGuard && existingGuard.started && !existingGuard.confirmed) {
      if (nextScreenReady(state.questionId, nextMode)) {
        existingGuard.confirmed = true;
        return { id: state.questionId, message: "Envio confirmado pela tela seguinte.", readyForNext: true, nextMode, reconciled: true };
      }
      throw new Error("[ENVIO_INDETERMINADO] Já houve um clique de envio para esta questão. A extensão bloqueou uma repetição automática para evitar duplicidade.");
    }
    const buttonId = nextMode === "same"
      ? "btnEnviarQuestaoCriarNovaMesmosParametros"
      : "btnEnviarQuestaoCriarNova";
    const button = document.getElementById(buttonId);
    if (!button || !isVisible(button)) throw new Error("O botão de envio oficial não está disponível para a fonte IES.");

    const guard = { started: true, confirmed: false, startedAt: Date.now(), nextMode };
    submissionGuards.set(String(state.questionId), guard);
    const response = await observeAjaxOrTransition(
      "/Questao/EnviarQuestaoPost",
      () => button.click(),
      () => nextScreenReady(state.questionId, nextMode),
      60000
    );
    guard.confirmed = true;

    let readyForNext = true;
    try {
      if (nextMode === "same") {
        await waitFor(() => {
          const next = getState();
          return next.formReady && next.currentStep === "step-4" && next.editorsReady
            && Boolean(next.sourceId && next.institutionId && next.disciplines.length)
            && (!next.questionId || next.questionId === "0");
        }, 30000, "");
      } else {
        await waitFor(
          () => currentStep() === "step-1" || !isVisible(document.getElementById("myModal2")),
          30000,
          ""
        );
      }
    } catch (_error) {
      readyForNext = false;
    }

    return {
      id: state.questionId,
      message: response.message || `Questão ${state.questionId} enviada oficialmente.`,
      readyForNext,
      nextMode,
      confirmedBy: response.confirmedBy || "response"
    };
  }

  function reconcileOfficial(payload) {
    const questionId = String(payload && payload.questionId || "");
    const nextMode = payload && payload.nextMode === "same" ? "same" : "fresh";
    const guard = submissionGuards.get(questionId);
    if (guard && guard.confirmed) return { confirmed: true, readyForNext: nextScreenReady(questionId, nextMode), evidence: "memory" };
    if (nextScreenReady(questionId, nextMode)) {
      if (guard) guard.confirmed = true;
      return { confirmed: true, readyForNext: true, evidence: "transition" };
    }
    const state = getState();
    return {
      confirmed: false,
      safeToRetry: false,
      currentStep: state.currentStep,
      currentQuestionId: state.questionId,
      message: "O envio anterior continua sem confirmação inequívoca. Verifique a lista do AvaliA; a extensão não repetiu o envio."
    };
  }

  async function saveDraft(payload) {
    const question = payload && payload.question;
    const state = getState();
    if (!state.formReady || state.currentStep !== "step-4") throw new Error("O Passo 4 não está pronto para salvar.");
    assertProfileLinkage(state);
    if (state.questionId && state.questionId !== "0") {
      verifyCurrentQuestion({ question, metadataMode: "strict" });
      return { id: state.questionId, message: `Rascunho ${state.questionId} já confirmado.`, alreadySaved: true };
    }
    if (questionFormat(question) !== "discursive" && state.alternativeCount !== REQUIRED_ALTERNATIVES) throw new Error("A questão objetiva não está configurada com quatro alternativas A–D.");
    verifyCurrentQuestion({ question, metadataMode: "strict" });

    const button = document.getElementById("submitFormQuestao");
    if (!button) throw new Error("O botão Salvar questão não foi localizado.");
    const messagesBefore = new Set(relevantMessages());
    const siteErrorCountBefore = siteErrors.length;
    button.click();

    const startedAt = Date.now();
    let buttonWasDisabled = false;
    while (Date.now() - startedAt < 30000) {
      await delay(200);
      const id = document.getElementById("Questao_IdQuestao")?.value || "";
      if (id && id !== "0") {
        verifyCurrentQuestion({ question, metadataMode: "strict" });
        return { id, message: `Rascunho ${id} criado e conferido.` };
      }
      if (button.disabled) buttonWasDisabled = true;
      const criticalSiteError = siteErrors.slice(siteErrorCountBefore).find((entry) => ["AVALIA_SESSAO_EXPIRADA", "AVALIA_SEM_PERMISSAO"].includes(entry.code));
      if (criticalSiteError) {
        const action = criticalSiteError.code === "AVALIA_SESSAO_EXPIRADA" ? "Entre novamente e reabra Elaborador." : "Confirme as permissões deste perfil de professor.";
        throw new Error(`[${criticalSiteError.code}] ${criticalSiteError.message} ${action}`);
      }
      const newMessages = relevantMessages().filter((message) => !messagesBefore.has(message));
      if (newMessages.length && !button.disabled) throw validationError(newMessages);
      if (buttonWasDisabled && !button.disabled && Date.now() - startedAt > 1200) {
        const messages = relevantMessages();
        if (messages.length) throw validationError(messages);
      }
    }
    recordSiteError({ source: "save", code: "AVALIA_SALVAMENTO_SEM_CONFIRMACAO", message: "O formulário não devolveu um ID em 30 segundos" });
    throw new Error("[SALVAMENTO_INDETERMINADO] O AvaliA não confirmou a criação do rascunho em 30 segundos. O salvamento não será repetido sem verificar o estado.");
  }

  function uncheckAllAnswers() {
    const radios = Array.from(document.querySelectorAll('input[type="radio"][name^="Afirmativas["][name$=".Verdadeira"]'));
    const $ = window.jQuery;
    if ($ && $.fn && typeof $.fn.iCheck === "function") radios.forEach((radio) => $(radio).iCheck("uncheck"));
    else radios.forEach((radio) => { radio.checked = false; dispatchValueEvents(radio); });
  }

  async function resetForNext() {
    const currentId = document.getElementById("Questao_IdQuestao")?.value || "";
    if ((!currentId || currentId === "0") && currentStep() === "step-4") return getState();
    if (!currentId || currentId === "0") throw new Error("A questão atual não possui identificador para preparar a próxima.");

    const createNext = typeof window.novaQuestaoMesmosConteudos === "function"
      ? window.novaQuestaoMesmosConteudos
      : (typeof novaQuestaoMesmosConteudos === "function" ? novaQuestaoMesmosConteudos : null);
    if (!createNext) throw new Error("O AvaliA não disponibilizou a ação segura para criar a próxima questão.");
    for (let attempt = 1; attempt <= 2; attempt += 1) {
      createNext();
      try {
        await waitFor(() => {
          const next = getState();
          return next.formReady && next.currentStep === "step-4" && next.editorsReady
            && Boolean(next.sourceId && next.institutionId && next.disciplines.length)
            && (!next.questionId || next.questionId === "0");
        }, 15000, "");
        return getState();
      } catch (_error) {
        await delay(750 * attempt);
      }
    }
    throw new Error("O AvaliA não confirmou uma nova tela vazia. A execução foi pausada sem alterar identificadores internos.");
  }

  // The native carousel has data-ride=carousel. One controller owns navigation during a batch.
  document.addEventListener?.('smartfox-grading-hold-carousel', () => {
    if (!/^\/CorrecaoDiscursiva(?:\/|$)/i.test(location.pathname) || !document.body.classList.contains('sf-autonomous-mode')) return;
    const $ = window.jQuery, element = document.getElementById('carousel-discursivas');
    if (element && $?.fn?.carousel && $(element).data('bs.carousel')) $(element).carousel('pause');
  });

  // Refresh only the native filter widgets after the isolated controller sets values.
  document.addEventListener?.('smartfox-grading-refresh-filters', () => {
    if (!/^\/CorrecaoDiscursiva(?:\/|$)/i.test(location.pathname)) return;
    const $ = window.jQuery;
    if (!$?.fn?.multiselect) return;
    for (const id of ['sltAvaliacao', 'sltStatus', 'sltAgrupamento', 'sltStatusCorrecaoIA']) {
      const element = document.getElementById(id);
      if (element && $(element).data('multiselect')) $(element).multiselect('refresh');
    }
  });

  const commands = {
    ping: () => ({ ok: true, version: BRIDGE_VERSION }),
    getState,
    getCatalog,
    getTagCatalog,
    inspectApprovalWorkspace,
    applyApprovalDecision,
    getSiteErrors,
    diagnoseWorkspace,
    diagnoseAndRepair,
    recoverStalledWorkspace,
    fillQuestion,
    verifyCurrentQuestion,
    saveDraft,
    resetForNext,
    prepareOfficialSubmission,
    submitOfficial,
    reconcileOfficial
  };

  window.addEventListener("message", async (event) => {
    if (event.source !== window || event.origin !== location.origin) return;
    const detail = event.data;
    if (!detail || detail.channel !== MESSAGE_CHANNEL || detail.direction !== "request") return;
    if (!detail || !detail.requestId || !detail.command) return;
    let response;
    try {
      const command = commands[detail.command];
      if (!command) throw new Error(`Comando não permitido: ${detail.command}`);
      const data = await command(detail.payload || {});
      response = { requestId: detail.requestId, ok: true, data };
    } catch (error) {
      response = { requestId: detail.requestId, ok: false, error: error instanceof Error ? error.message : String(error) };
    }
    window.postMessage({ channel: MESSAGE_CHANNEL, direction: "response", ...response }, location.origin);
  });
})();
