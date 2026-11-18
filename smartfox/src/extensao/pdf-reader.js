(function (root) {
  'use strict';
  let modulesPromise = null;

  async function loadModules() {
    if (!root.chrome?.runtime?.getURL) throw new Error('Abra o leitor de PDF pela extensão SmartFox instalada.');
    if (!modulesPromise) {
      modulesPromise = (async () => {
        // Preload the packaged worker in the isolated extension world. PDF.js
        // then uses its supported local handler instead of creating a blob
        // worker across the page/extension origins (blocked by Chrome CSP).
        const [pdfjs, worker] = await Promise.all([
          import(root.chrome.runtime.getURL('vendor/pdf.min.mjs')),
          import(root.chrome.runtime.getURL('vendor/pdf.worker.min.mjs'))
        ]);
        if (typeof pdfjs.getDocument !== 'function' || !worker.WorkerMessageHandler) {
          throw new Error('Os arquivos do leitor de PDF estão incompletos.');
        }
        root.pdfjsWorker = { WorkerMessageHandler: worker.WorkerMessageHandler };
        pdfjs.GlobalWorkerOptions.workerSrc = root.chrome.runtime.getURL('vendor/pdf.worker.min.mjs');
        return pdfjs;
      })().catch(() => {
        modulesPromise = null;
        const error = new Error('Não foi possível carregar o leitor local de PDF. Atualize a pasta completa do SmartFox, clique em Recarregar em chrome://extensions e atualize a aba do AvaliA.');
        error.code = 'PDF_LEITOR_INDISPONIVEL';
        throw error;
      });
    }
    return modulesPromise;
  }

  function readableError(error) {
    if (typeof error?.code === 'string' && error.code.startsWith('PDF_')) return error;
    let message;
    let code;
    if (error?.name === 'PasswordException') {
      code = 'PDF_COM_SENHA';
      message = 'Este PDF está protegido por senha. Abra-o com a senha e salve uma cópia desbloqueada para importar.';
    } else if (error?.name === 'InvalidPDFException') {
      code = 'PDF_INVALIDO';
      message = 'O arquivo não pôde ser lido como PDF. Abra-o em um leitor de PDF e salve uma nova cópia antes de importar.';
    } else if (/getOrInsert|withResolvers|Promise\.try|URL\.parse|Float16Array|toHex|toBase64|fromBase64/.test(String(error?.message))) {
      code = 'PDF_NAVEGADOR_DESATUALIZADO';
      message = 'A leitura deste PDF precisa de recursos de uma versão mais recente do Chrome. Atualize o navegador e tente novamente.';
    } else {
      code = 'PDF_LEITURA_FALHOU';
      message = 'Não foi possível concluir a leitura do PDF. Tente salvar uma nova cópia do arquivo e importá-la novamente.';
    }
    const result = new Error(message);
    result.code = code;
    return result;
  }

  async function read(arrayBuffer) {
    let task;
    try {
      const pdfjs = await loadModules();
      task = pdfjs.getDocument({
        data: new Uint8Array(arrayBuffer),
        isEvalSupported: false,
        useWasm: false,
        useWorkerFetch: false,
        // Only text is extracted. Font faces, image codecs and remote assets
        // are unnecessary for this operation.
        disableFontFace: true,
        verbosity: pdfjs.VerbosityLevel?.ERRORS ?? 0
      });
      const pdf = await task.promise;
      const pages = [];
      for (let number = 1; number <= pdf.numPages; number++) {
        const page = await pdf.getPage(number);
        try {
          const content = await page.getTextContent();
          const text = content.items.map(item => String(item.str || '')).join(' ').trim();
          if (text) pages.push(`[Página ${number}]\n${text}`);
        } finally {
          page.cleanup();
        }
      }
      if (!pages.length) {
        const error = new Error('O PDF não possui texto selecionável. Converta o material com OCR antes de adicioná-lo.');
        error.code = 'PDF_SEM_TEXTO';
        throw error;
      }
      return pages.join('\n\n');
    } catch (error) {
      throw readableError(error);
    } finally {
      // Includes password failures, invalid PDFs and errors after reading pages.
      // Cleanup must not replace the useful primary error shown to the professor.
      if (task) await task.destroy().catch(() => {});
    }
  }

  root.SmartFoxPdfReader = Object.freeze({ read });
})(typeof window !== 'undefined' ? window : globalThis);
