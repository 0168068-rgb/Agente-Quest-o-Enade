(function (root, factory) {
  "use strict";
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.SmartFoxIdentity = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const VERSION = "11.0.0";
  const PROFILE_SELECTORS = Object.freeze([
    "a.user-profile.dropdown-toggle",
    "a.user-profile",
    ".navbar a.user-profile",
    "header a.user-profile",
    "nav a.user-profile"
  ]);
  const BLOCKED_LABELS = /^(?:professor(?:\s*\/\s*tutor)?|elaborador|administrador|sair|conta|minha conta|perfil)$/i;

  function cleanDisplayName(value) {
    return String(value == null ? "" : value)
      .replace(/[\u200B-\u200D\uFEFF]/g, "")
      .replace(/[\s\u00A0]+/g, " ")
      .trim()
      .slice(0, 180);
  }

  function normalizePersonName(value) {
    return cleanDisplayName(value)
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/^(?:prof(?:essor|essora)?|dr(?:a)?)[.\s]+/i, "")
      .replace(/[^a-z0-9]+/g, " ")
      .trim()
      .replace(/\s+/g, " ");
  }

  function looksLikePersonName(value) {
    const display = cleanDisplayName(value);
    const normalized = normalizePersonName(display);
    if (!display || BLOCKED_LABELS.test(display) || normalized.length < 5) return false;
    const words = normalized.split(" ").filter(Boolean);
    return words.length >= 2 && words.every((word) => /[a-z]/.test(word));
  }

  function extractAvaliaIdentity(doc) {
    if (!doc || typeof doc.querySelectorAll !== "function") return { name: "", normalizedName: "", selector: "" };
    for (const selector of PROFILE_SELECTORS) {
      let nodes = [];
      try { nodes = Array.from(doc.querySelectorAll(selector)); } catch (_) { nodes = []; }
      for (const node of nodes) {
        const name = cleanDisplayName(node?.textContent || node?.innerText || node?.getAttribute?.("title") || "");
        if (!looksLikePersonName(name)) continue;
        return { name, normalizedName: normalizePersonName(name), selector };
      }
    }
    return { name: "", normalizedName: "", selector: "" };
  }

  function namesMatch(licensedName, detectedName) {
    const licensed = normalizePersonName(licensedName);
    const detected = normalizePersonName(detectedName);
    return Boolean(licensed && detected && licensed === detected);
  }

  function fingerprint(value) {
    const input = normalizePersonName(value);
    let hash = 2166136261;
    for (let index = 0; index < input.length; index += 1) {
      hash ^= input.charCodeAt(index);
      hash = Math.imul(hash, 16777619);
    }
    return (hash >>> 0).toString(16).padStart(8, "0");
  }

  return Object.freeze({
    version: VERSION,
    profileSelectors: PROFILE_SELECTORS,
    cleanDisplayName,
    normalizePersonName,
    looksLikePersonName,
    extractAvaliaIdentity,
    namesMatch,
    fingerprint
  });
});
