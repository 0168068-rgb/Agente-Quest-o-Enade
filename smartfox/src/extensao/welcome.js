"use strict";
const statusElement = document.getElementById("package-status");
const openButton = document.getElementById("open-avalia");
function showError(message) { statusElement.dataset.state = "error"; statusElement.textContent = message; openButton.disabled = true; }
const timer = setTimeout(() => showError("Recarregue a extensão para conferir a instalação."), 15000);
chrome.runtime.sendMessage({ type: "SF_STATUS" }, response => {
  clearTimeout(timer);
  if (chrome.runtime.lastError || !response?.ok || !response.data?.authorized || !response.data?.standalone) {
    showError("Não foi possível validar os arquivos. Extraia novamente o pacote e recarregue a extensão."); return;
  }
  statusElement.dataset.state = "ready";
  statusElement.textContent = "Pronto para usar. Nenhuma ativação necessária.";
  openButton.disabled = false;
});
openButton.addEventListener("click", async () => {
  try { await chrome.tabs.create({ url: "https://avalia.grupoa.com.br/" }); }
  catch (_) { showError("Abra https://avalia.grupoa.com.br/ em uma nova aba."); }
});
