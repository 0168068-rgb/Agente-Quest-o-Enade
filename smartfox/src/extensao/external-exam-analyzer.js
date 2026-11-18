(function (root) {
  "use strict";

  const VERSION = "11.0.0";
  const REQUIRED_ALTERNATIVES = 4;
  const CONTENT_ROLE = "reference_material";
  const STATUS = Object.freeze({
    ANSWERABLE: "answerable",
    REVIEW: "review",
    INSUFFICIENT: "insufficient",
    INVALID: "invalid"
  });

  function clean(value) {
    return String(value == null ? "" : value)
      .replace(/\r\n?/g, "\n")
      .replace(/[\u00ad\u200b-\u200d\ufeff]/g, "")
      .replace(/[ \t]+/g, " ")
      .replace(/\n{3,}/g, "\n\n")
      .trim();
  }

  function normalize(value) {
    return clean(value)
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLocaleLowerCase("pt-BR")
      .replace(/[^a-z0-9%+\-=<>²³⁰¹⁴⁵⁶⁷⁸⁹\s]/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function xml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&apos;");
  }

  function safeFileName(value) {
    const stem = String(value || "prova_externa")
      .replace(/\.[^.]+$/, "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-zA-Z0-9._-]+/g, "_")
      .replace(/^_+|_+$/g, "")
      .slice(0, 120);
    return `${stem || "prova_externa"}_gabarito_fundamentado_SmartFox.docx`;
  }

  function contentDocuments(base) {
    return (Array.isArray(base?.documents) ? base.documents : []).filter((document) => (
      document?.role === CONTENT_ROLE
      && Array.isArray(document.chunks)
      && document.chunks.length > 0
      && clean(document.text).length >= 80
    ));
  }

  function evidenceBase(base, collectionSubject) {
    const documents = contentDocuments(base).map((document) => ({ ...document, subject: clean(collectionSubject) || document.subject }));
    return {
      ...(base || {}),
      documents,
      updatedAt: base?.updatedAt || new Date(0).toISOString()
    };
  }

  function objectiveResult(question, base, ordinal, knowledge) {
    const alternatives = Array.isArray(question?.alternatives) ? question.alternatives : [];
    if (alternatives.length !== REQUIRED_ALTERNATIVES) {
      return {
        ordinal,
        number: question?.number || ordinal,
        name: question?.name || `Questão ${ordinal}`,
        format: "objective",
        bodyText: clean(question?.bodyText),
        alternatives,
        status: STATUS.INVALID,
        possible: false,
        confidence: 0,
        suggestedIndex: null,
        suggestedLetter: "",
        suggestedText: "",
        evidence: [],
        warnings: [`A questão possui ${alternatives.length} alternativa(s); são necessárias exatamente A–D.`],
        code: "PROVA_EXTERNA_ALTERNATIVAS_INVALIDAS"
      };
    }

    const providedLetter = /^[A-D]$/i.test(String(question?.correctLetter || ""))
      ? String(question.correctLetter).toUpperCase()
      : "";
    const neutralQuestion = {
      ...question,
      subjectHint: base.collectionSubject,
      correctIndex: undefined,
      correctLetter: ""
    };
    const audit = knowledge.analyzeQuestion(neutralQuestion, base);
    const suggestedIndex = Number.isInteger(audit.suggestedIndex) ? audit.suggestedIndex : null;
    const alignment = Number(audit.alignment?.score || 0);
    const confidence = Number(audit.confidence || 0);
    const hasEvidence = Array.isArray(audit.evidence) && audit.evidence.length > 0;
    let status = STATUS.INSUFFICIENT;
    if (suggestedIndex != null && hasEvidence && confidence >= 0.72 && alignment >= 35) status = STATUS.ANSWERABLE;
    else if (suggestedIndex != null && hasEvidence && confidence >= 0.5 && alignment >= 22) status = STATUS.REVIEW;
    const suggestedLetter = suggestedIndex == null ? "" : String(alternatives[suggestedIndex]?.letter || "ABCD"[suggestedIndex]);
    const warnings = [...(audit.warnings || [])];
    if (status === STATUS.REVIEW) warnings.unshift("A base encontrou uma possibilidade, mas a separação entre as alternativas ainda exige conferência docente.");
    if (status === STATUS.INSUFFICIENT) warnings.unshift("A coleção selecionada não sustenta uma resposta única com a confiança mínima.");
    if (providedLetter && suggestedLetter && providedLetter !== suggestedLetter) {
      warnings.push(`O arquivo informa ${providedLetter}, enquanto a base favorece ${suggestedLetter}. O gabarito do arquivo não foi usado para escolher a resposta.`);
    }
    return {
      ordinal,
      number: question?.number || ordinal,
      name: question?.name || `Questão ${ordinal}`,
      format: "objective",
      bodyText: clean(question?.bodyText),
      alternatives,
      status,
      possible: status !== STATUS.INSUFFICIENT,
      confidence,
      alignment,
      suggestedIndex,
      suggestedLetter,
      suggestedText: suggestedIndex == null ? "" : clean(alternatives[suggestedIndex]?.plain || alternatives[suggestedIndex]?.text),
      providedLetter,
      agreesWithProvidedKey: providedLetter && suggestedLetter ? providedLetter === suggestedLetter : null,
      evidence: audit.evidence || [],
      alternativeScores: audit.alternativeScores || [],
      warnings,
      code: status === STATUS.ANSWERABLE
        ? "PROVA_EXTERNA_RESPONDIVEL"
        : status === STATUS.REVIEW
          ? "PROVA_EXTERNA_CONFERENCIA"
          : "PROVA_EXTERNA_BASE_INSUFICIENTE"
    };
  }

  function discursiveResult(question, base, ordinal, knowledge) {
    const neutralQuestion = {
      ...question,
      subjectHint: base.collectionSubject,
      questionFormat: "discursive",
      expectedResponseText: "",
      expectedResponseHtml: ""
    };
    const audit = knowledge.analyzeQuestion(neutralQuestion, base);
    const alignment = Number(audit.alignment?.score || 0);
    const evidence = Array.isArray(audit.evidence) ? audit.evidence : [];
    const possible = alignment >= 35 && evidence.length > 0;
    const answer = possible
      ? clean(evidence.slice(0, 2).map((entry) => entry.excerpt).join(" ")).slice(0, 1200)
      : "";
    return {
      ordinal,
      number: question?.number || ordinal,
      name: question?.name || `Questão ${ordinal}`,
      format: "discursive",
      bodyText: clean(question?.bodyText),
      alternatives: [],
      status: possible ? STATUS.REVIEW : STATUS.INSUFFICIENT,
      possible,
      confidence: possible ? Math.round(Math.min(0.84, 0.18 + alignment / 125) * 100) / 100 : 0,
      alignment,
      suggestedIndex: null,
      suggestedLetter: "",
      suggestedText: answer,
      evidence,
      warnings: possible
        ? ["Resposta extrativa montada somente com trechos da base; revise a redação antes de utilizá-la.", ...(audit.warnings || [])]
        : ["A coleção selecionada não contém evidência suficiente para formular uma resposta discursiva.", ...(audit.warnings || [])],
      code: possible ? "PROVA_EXTERNA_DISCURSIVA_CONFERENCIA" : "PROVA_EXTERNA_BASE_INSUFICIENTE"
    };
  }

  function analyze(parsed, scopedBase, collection, knowledgeApi) {
    const knowledge = knowledgeApi || root.AvaliaKnowledgeBase;
    if (!knowledge?.analyzeQuestion) throw new Error("O motor do acervo permanente não está disponível.");
    const subject = clean(collection?.subject);
    if (!collection?.id || collection.id === knowledge.defaultCollectionId || !subject) {
      throw new Error("Selecione uma coleção específica com disciplina definida. O Acervo geral não pode responder uma prova externa.");
    }
    const sourceBase = evidenceBase(scopedBase, subject);
    if (!sourceBase.documents.length) {
      throw new Error(`A coleção “${collection.name || subject}” não possui material classificado como conteúdo. Planos, modelos e regras não são usados como resposta.`);
    }
    sourceBase.collectionSubject = subject;
    const questions = Array.isArray(parsed?.questions) ? parsed.questions : [];
    if (!questions.length) throw new Error("Nenhuma questão foi reconhecida na prova externa.");
    const results = questions.map((question, index) => {
      const discursive = question?.questionFormat === "discursive"
        || /discursiv|dissertativ|resposta aberta/i.test(`${question?.typeLabel || ""} ${question?.typeDescription || ""}`);
      return discursive
        ? discursiveResult(question, sourceBase, index + 1, knowledge)
        : objectiveResult(question, sourceBase, index + 1, knowledge);
    });
    const summary = {
      total: results.length,
      answerable: results.filter((item) => item.status === STATUS.ANSWERABLE).length,
      review: results.filter((item) => item.status === STATUS.REVIEW).length,
      insufficient: results.filter((item) => item.status === STATUS.INSUFFICIENT).length,
      invalid: results.filter((item) => item.status === STATUS.INVALID).length
    };
    return {
      version: VERSION,
      mode: "discipline_local_knowledge_only",
      networkUsed: false,
      fileName: parsed.fileName || "prova_externa.docx",
      analyzedAt: new Date().toISOString(),
      collection: { id: collection.id, name: collection.name, subject },
      sourceDocuments: sourceBase.documents.map((document) => ({
        id: document.id,
        name: document.name,
        fingerprint: document.fingerprint,
        role: document.role
      })),
      excludedDocuments: (scopedBase?.documents || []).filter((document) => !sourceBase.documents.some((candidate) => candidate.id === document.id)).map((document) => ({ id: document.id, name: document.name, role: document.role || "não classificado" })),
      summary,
      results,
      possible: summary.answerable + summary.review > 0,
      complete: summary.answerable === summary.total,
      notice: "Análise feita exclusivamente com materiais de conteúdo da coleção selecionada. Nenhuma consulta à internet foi realizada."
    };
  }

  function paragraph(text, style) {
    const styleXml = style ? `<w:pPr><w:pStyle w:val="${xml(style)}"/></w:pPr>` : "";
    const lines = clean(text).split("\n");
    const runs = lines.map((line, index) => `${index ? "<w:br/>" : ""}<w:t xml:space="preserve">${xml(line)}</w:t>`).join("");
    return `<w:p>${styleXml}<w:r>${runs || "<w:t></w:t>"}</w:r></w:p>`;
  }

  async function buildDocx(report, zipApi) {
    const Zip = zipApi || root.JSZip;
    if (!Zip) throw new Error("O gerador DOCX não está disponível.");
    const zip = new Zip();
    const contentTypes = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>`;
    const rels = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>`;
    const documentRels = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>`;
    const styles = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="pt-BR"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:rPr><w:b/><w:color w:val="B45309"/><w:sz w:val="34"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:rPr><w:b/><w:color w:val="1E293B"/><w:sz w:val="27"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:rPr><w:b/><w:color w:val="C2410C"/><w:sz w:val="24"/></w:rPr></w:style></w:styles>`;
    const summary = report.summary || {};
    const body = [
      paragraph("SmartFox — gabarito fundamentado da prova externa", "Title"),
      paragraph(`Arquivo: ${report.fileName}`),
      paragraph(`Disciplina/coleção: ${report.collection?.name || report.collection?.subject || "—"}`),
      paragraph(`Resultado: ${summary.answerable || 0} respondível(is), ${summary.review || 0} para conferência, ${summary.insufficient || 0} sem base suficiente e ${summary.invalid || 0} inválida(s).`),
      paragraph(report.notice),
      paragraph("Gabarito e evidências", "Heading1")
    ];
    (report.results || []).forEach((item) => {
      const statusLabel = item.status === STATUS.ANSWERABLE ? "Respondível pela base" : item.status === STATUS.REVIEW ? "Requer conferência" : item.status === STATUS.INVALID ? "Estrutura inválida" : "Base insuficiente";
      body.push(paragraph(`${item.number || item.ordinal}. ${item.name || "Questão"}`, "Heading2"));
      body.push(paragraph(`Situação: ${statusLabel} · confiança ${Math.round(Number(item.confidence || 0) * 100)}%`));
      body.push(paragraph(`Enunciado: ${item.bodyText || "não reconhecido"}`));
      if (item.suggestedLetter) body.push(paragraph(`Resposta sugerida: ${item.suggestedLetter}) ${item.suggestedText}`));
      else if (item.suggestedText) body.push(paragraph(`Resposta fundamentada sugerida: ${item.suggestedText}`));
      else body.push(paragraph("Resposta: não foi possível determinar somente com a base selecionada."));
      (item.evidence || []).slice(0, 3).forEach((entry, index) => body.push(paragraph(`Evidência ${index + 1} — ${entry.documentName}: ${entry.excerpt}`)));
      (item.warnings || []).slice(0, 4).forEach((warning) => body.push(paragraph(`Atenção: ${warning}`)));
    });
    body.push(paragraph("Registro de método", "Heading1"));
    body.push(paragraph(`Modo: ${report.mode}. Internet utilizada: não. Materiais de conteúdo consultados: ${(report.sourceDocuments || []).map((item) => item.name).join("; ") || "nenhum"}.`));
    const documentXml = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:body>${body.join("")}<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"/></w:sectPr></w:body></w:document>`;
    zip.file("[Content_Types].xml", contentTypes);
    zip.folder("_rels").file(".rels", rels);
    zip.folder("word").file("document.xml", documentXml).file("styles.xml", styles).folder("_rels").file("document.xml.rels", documentRels);
    return zip.generateAsync({ type: "uint8array", compression: "DEFLATE", compressionOptions: { level: 6 } });
  }

  async function download(report) {
    const bytes = await buildDocx(report);
    const blob = new Blob([bytes], { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = safeFileName(report.fileName);
    anchor.style.display = "none";
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    return anchor.download;
  }

  root.SmartFoxExternalExam = Object.freeze({
    version: VERSION,
    status: STATUS,
    requiredAlternatives: REQUIRED_ALTERNATIVES,
    contentRole: CONTENT_ROLE,
    analyze,
    buildDocx,
    download,
    safeFileName
  });
})(typeof window !== "undefined" ? window : globalThis);
