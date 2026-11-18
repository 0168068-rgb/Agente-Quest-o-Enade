(function (root) {
  "use strict";

  let verification = null;

  async function sha256(bytes) {
    const digest = await crypto.subtle.digest("SHA-256", bytes);
    return Array.from(new Uint8Array(digest), (value) => value.toString(16).padStart(2, "0")).join("");
  }

  async function verify() {
    if (verification) return verification;
    verification = (async () => {
      try {
        const response = await fetch(chrome.runtime.getURL("SMARTFOX_INTEGRITY.json"), { cache: "no-store" });
        if (!response.ok) throw new Error(`catálogo HTTP ${response.status}`);
        const catalog = await response.json();
        if (catalog?.algorithm !== "SHA-256" || !catalog.files || typeof catalog.files !== "object") {
          throw new Error("catálogo de integridade inválido");
        }
        const failures = [];
        for (const [file, expected] of Object.entries(catalog.files)) {
          try {
            const fileResponse = await fetch(chrome.runtime.getURL(file), { cache: "no-store" });
            if (!fileResponse.ok) throw new Error(`HTTP ${fileResponse.status}`);
            const actual = await sha256(await fileResponse.arrayBuffer());
            if (actual !== expected) failures.push({ file, reason: "hash_mismatch" });
          } catch (error) {
            failures.push({ file, reason: error?.message || "unreadable" });
          }
        }
        return { ok: failures.length === 0, checkedAt: new Date().toISOString(), version: catalog.version || "", failures };
      } catch (error) {
        return { ok: false, checkedAt: new Date().toISOString(), version: "", failures: [{ file: "SMARTFOX_INTEGRITY.json", reason: error?.message || "catalog_unavailable" }] };
      }
    })();
    return verification;
  }

  root.SmartFoxIntegrity = Object.freeze({ verify });
})(globalThis);
