(function (root) {
  "use strict";

  const VERSION = "11.0.0";
  const GRADUATION_GROUP = "graduacao";

  function normalize(value) {
    return String(value == null ? "" : value)
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/\s+/g, " ")
      .trim()
      .toLocaleLowerCase("pt-BR");
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

  function normalizeTag(entry) {
    const tag = entry || {};
    return {
      id: String(tag.id ?? tag.value ?? "").trim(),
      label: String(tag.label ?? tag.text ?? tag.name ?? "").replace(/\s+/g, " ").trim(),
      group: String(tag.group ?? tag.groupLabel ?? "").replace(/\s+/g, " ").trim(),
      selected: Boolean(tag.selected)
    };
  }

  function uniqueCatalog(entries) {
    const seen = new Set();
    return (Array.isArray(entries) ? entries : [])
      .map(normalizeTag)
      .filter((tag) => tag.id && tag.label && tag.group)
      .filter((tag) => {
        const key = `${tag.group}\u241f${tag.id}\u241f${tag.label}`;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      });
  }

  function summarizeCatalog(entries) {
    const catalog = uniqueCatalog(entries);
    const groups = {};
    catalog.forEach((tag) => {
      groups[tag.group] = (groups[tag.group] || 0) + 1;
    });
    const eligible = catalog.filter((tag) => normalize(tag.group) === GRADUATION_GROUP);
    const signatureSource = catalog
      .map((tag) => `${normalize(tag.group)}:${tag.id}:${normalize(tag.label)}`)
      .sort()
      .join("|");
    return {
      total: catalog.length,
      eligibleCount: eligible.length,
      ignoredCount: catalog.length - eligible.length,
      groups,
      signature: fnv1a(signatureSource),
      catalog,
      eligible
    };
  }

  function verifyGraduationTarget(entries, target) {
    const summary = summarizeCatalog(entries);
    const desired = normalizeTag(target);
    const found = summary.catalog.find((tag) => tag.id === desired.id)
      || summary.catalog.find((tag) => normalize(tag.label) === normalize(desired.label));
    if (!found) return { valid: false, code: "TAG_NAO_ENCONTRADA", message: "A tag escolhida não existe no catálogo atual do AvaliA.", summary, target: null };
    if (normalize(found.group) !== GRADUATION_GROUP) {
      return { valid: false, code: "TAG_FORA_GRADUACAO", message: `A tag “${found.label}” pertence ao grupo ${found.group}, não a Graduação.`, summary, target: found };
    }
    if (desired.id && desired.label && normalize(found.label) !== normalize(desired.label)) {
      return { valid: false, code: "TAG_IDENTIDADE_ALTERADA", message: "O mesmo identificador de tag passou a exibir outro nome; remapeie e escolha novamente.", summary, target: found };
    }
    return { valid: true, code: "TAG_GRADUACAO_CONFIRMADA", message: `Tag de Graduação confirmada: ${found.label}.`, summary, target: found };
  }

  function normalizeIds(values) {
    const found = new Set();
    (Array.isArray(values) ? values : []).forEach((value) => {
      const id = String(value == null ? "" : value).trim();
      if (/^\d+$/.test(id)) found.add(id);
    });
    return Array.from(found);
  }

  function latestOfficialIds(results) {
    return normalizeIds((Array.isArray(results) ? results : [])
      .filter((result) => result && result.status === "official")
      .map((result) => result.id));
  }

  function tagMatches(row, target, workspace) {
    const tags = uniqueCatalog((row && row.tags || []).map((tag) => ({ ...tag, group: tag.group || "Graduação" })));
    if (tags.some((tag) => tag.id === target.id || normalize(tag.label) === normalize(target.label))) return true;
    const filter = workspace && workspace.activeTagFilter;
    return Boolean(workspace?.tagFilterVerified && filter
      && (String(filter.id || "") === target.id || normalize(filter.label) === normalize(target.label)));
  }

  function disciplineMatches(row, expectedDiscipline, workspace) {
    const expected = normalize(expectedDiscipline);
    if (!expected) return Boolean(workspace?.disciplineVerified);
    const rowDiscipline = normalize(row && row.discipline);
    const workspaceDiscipline = normalize(workspace && workspace.discipline);
    if (rowDiscipline) return rowDiscipline === expected || rowDiscipline.includes(expected) || expected.includes(rowDiscipline);
    return Boolean(workspace?.disciplineVerified && workspaceDiscipline
      && (workspaceDiscipline === expected || workspaceDiscipline.includes(expected) || expected.includes(workspaceDiscipline)));
  }

  function buildPlan(options) {
    const settings = options || {};
    const workspace = settings.workspace || {};
    const targetCheck = verifyGraduationTarget(settings.catalog || [], settings.targetTag || {});
    const latestIds = normalizeIds(settings.latestIds || []);
    const questions = Array.isArray(workspace.questions) ? workspace.questions : [];
    const issues = [];
    if (!targetCheck.valid) issues.push({ code: targetCheck.code, message: targetCheck.message });
    if (!latestIds.length) issues.push({ code: "REMESSA_SEM_IDS", message: "A última remessa não possui IDs oficiais confirmados." });
    if (!workspace.allQuestionsView) issues.push({ code: "LISTA_INCOMPLETA", message: "Abra a visão Todas questões antes da conferência de likes." });
    if (!workspace.scanComplete) issues.push({ code: "PAGINACAO_INCOMPLETA", message: "A extensão ainda não leu todas as páginas da lista." });
    if (!workspace.disciplineVerified) issues.push({ code: "DISCIPLINA_NAO_CONFIRMADA", message: "A disciplina da tela não foi confirmada como uma das escolhidas manualmente no Passo 3." });
    if (!workspace.tagFilterVerified) issues.push({ code: "FILTRO_TAG_NAO_CONFIRMADO", message: "A lista ainda não está filtrada pela tag escolhida." });

    const target = targetCheck.target || normalizeTag(settings.targetTag);
    const scoped = [];
    const ambiguous = [];
    const seenIds = new Set();
    questions.forEach((row) => {
      const id = String(row?.id || "").trim();
      if (!/^\d+$/.test(id)) {
        ambiguous.push({ id: "", reason: row?.ambiguousReason || "Linha sem ID inequívoco." });
        return;
      }
      if (seenIds.has(id)) {
        ambiguous.push({ id, reason: "O mesmo ID apareceu mais de uma vez na leitura." });
        return;
      }
      seenIds.add(id);
      if (!tagMatches(row, target, workspace) || !disciplineMatches(row, settings.discipline, workspace)) return;
      if (typeof row.liked !== "boolean") {
        ambiguous.push({ id, reason: row.ambiguousReason || "O estado do like não pôde ser determinado." });
        return;
      }
      scoped.push({ ...row, id });
    });
    ambiguous.forEach((entry) => issues.push({ code: "LINHA_AMBIGUA", message: `Questão ${entry.id || "sem ID"}: ${entry.reason}` }));

    const latestSet = new Set(latestIds);
    const scopedIds = new Set(scoped.map((row) => row.id));
    const missingLatest = latestIds.filter((id) => !scopedIds.has(id));
    if (missingLatest.length) issues.push({ code: "REMESSA_NAO_LOCALIZADA", message: `${missingLatest.length} questão(ões) oficiais da última remessa não apareceram na lista completa filtrada.` });

    const approve = scoped.filter((row) => latestSet.has(row.id) && !row.liked);
    const keep = scoped.filter((row) => latestSet.has(row.id) && row.liked);
    const remove = scoped.filter((row) => !latestSet.has(row.id) && row.liked);
    const unchanged = scoped.filter((row) => !latestSet.has(row.id) && !row.liked);
    const planSignature = fnv1a(JSON.stringify({
      catalog: targetCheck.summary.signature,
      target: target.id,
      discipline: normalize(settings.discipline || workspace.discipline),
      latestIds: [...latestIds].sort(),
      approve: approve.map((row) => row.id).sort(),
      remove: remove.map((row) => row.id).sort()
    }));
    return {
      version: VERSION,
      createdAt: new Date().toISOString(),
      safeToApply: issues.length === 0,
      issues,
      catalogSignature: targetCheck.summary.signature,
      planSignature,
      targetTag: target,
      discipline: settings.discipline || workspace.discipline || "",
      latestIds,
      totals: { scanned: questions.length, scoped: scoped.length, approve: approve.length, keep: keep.length, remove: remove.length, unchanged: unchanged.length, missing: missingLatest.length, ambiguous: ambiguous.length },
      approve,
      keep,
      remove,
      unchanged,
      missingLatest,
      ambiguous
    };
  }

  root.AvaliaApprovalSync = Object.freeze({
    version: VERSION,
    normalize,
    normalizeTag,
    summarizeCatalog,
    verifyGraduationTarget,
    normalizeIds,
    latestOfficialIds,
    buildPlan
  });
})(typeof window !== "undefined" ? window : globalThis);
