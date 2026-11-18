(function (root) {
  "use strict";

  function escapeXml(value) {
    return String(value == null ? "" : value)
      .replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&apos;");
  }

  function safeName(value) {
    return String(value || "Avaliacao_Athus")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-zA-Z0-9_-]+/g, "_")
      .replace(/_+/g, "_")
      .replace(/^_|_$/g, "")
      .slice(0, 90) || "Avaliacao_Athus";
  }

  function isDiscursive(question) {
    return question?.questionFormat === "discursive"
      || /discursiv|dissertativ|resposta aberta/i.test(`${question?.typeLabel || ""} ${question?.typeDescription || ""}`);
  }

  function validateQuestions(questions) {
    if (!Array.isArray(questions) || !questions.length) return ["Não há questões para exportar."];
    const errors = [];
    questions.forEach((question, index) => {
      const label = question?.name || `Questão ${index + 1}`;
      const richHtml = [question?.bodyHtml, question?.feedbackHtml, question?.expectedResponseHtml,
        ...(question?.alternatives || []).map(a => a.html)].join(" ");
      if (question?.media?.length || question?.richIntegrity?.imageHashes?.length || /<(?:img|svg|table)\b/i.test(richHtml)) {
        errors.push(`${label}: esta exportação não preserva imagens ou tabelas de texto. Use o Word original para esses elementos.`);
      }
      for (const formula of richHtml.matchAll(/<math\b[^>]*>[\s\S]*?<\/math\s*>/gi)) {
        const hash=formula[0].match(/data-aab-formula=["']([^"']+)["']/)?.[1];
        const record=(question.formulas||[]).find(f=>f.hash===hash);
        if(!record?.canonical||record.conversionIssues?.length)errors.push(`${label}: a fórmula não possui uma estrutura Word íntegra para exportação.`);
      }
      if(/data-aab-formula/i.test(richHtml.replace(/<math\b[^>]*>[\s\S]*?<\/math\s*>/gi,'')))errors.push(`${label}: reimporte o Word para atualizar a fórmula do formato antigo.`);
      const discursive = isDiscursive(question);
      const alternatives = Array.isArray(question?.alternatives) ? question.alternatives : [];
      const alternativeTexts = alternatives.map((alternative) => String(alternative?.plain || alternative?.text || "").trim());
      if (!String(question?.bodyText || "").trim()) errors.push(`${label}: enunciado vazio`);
      if (!String(question?.feedbackText || "").trim()) errors.push(`${label}: feedback pedagógico vazio`);
      if (discursive) {
        if (!String(question?.expectedResponseText || "").trim()) errors.push(`${label}: padrão de resposta discursiva vazio`);
      } else {
        if (alternatives.length !== 4) errors.push(`${label}: deve ter exatamente quatro alternativas A–D`);
        if (alternativeTexts.some((text) => !text)) errors.push(`${label}: há alternativa vazia`);
        const normalized = alternativeTexts.map((text) => text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/\s+/g, " ").trim().toLocaleLowerCase("pt-BR"));
        if (normalized.length === 4 && new Set(normalized).size !== 4) errors.push(`${label}: há alternativas duplicadas`);
        const correctIndex = Number.isInteger(question?.correctIndex) ? question.correctIndex : "ABCD".indexOf(String(question?.correctLetter || "").toUpperCase());
        if (correctIndex < 0 || correctIndex > 3) errors.push(`${label}: gabarito inválido`);
        const statedLetter = String(question?.correctLetter || "").trim().toUpperCase();
        if (statedLetter && (!/^[A-D]$/.test(statedLetter) || correctIndex >= 0 && statedLetter !== "ABCD"[correctIndex])) errors.push(`${label}: letra do gabarito não corresponde ao índice correto`);
      }
    });
    return errors;
  }

  function run(text, options) {
    const value = String(text || "").split("\n").map(escapeXml).join('</w:t><w:br/><w:t xml:space="preserve">');
    const properties = [options?.bold ? "<w:b/>" : "", options?.italic ? "<w:i/>" : "", options?.size ? `<w:sz w:val="${options.size}"/><w:szCs w:val="${options.size}"/>` : ""].join("");
    return `<w:r>${properties ? `<w:rPr>${properties}</w:rPr>` : ""}<w:t xml:space="preserve">${value}</w:t></w:r>`;
  }

  function paragraph(text, options) {
    const style = options?.style ? `<w:pStyle w:val="${escapeXml(options.style)}"/>` : "";
    const spacing = options?.after != null ? `<w:spacing w:after="${Number(options.after)}"/>` : "";
    const keep = options?.keepNext ? "<w:keepNext/>" : "";
    const pageBreak = options?.pageBreakBefore ? "<w:pageBreakBefore/>" : "";
    const properties = style || spacing || keep || pageBreak ? `<w:pPr>${style}${spacing}${keep}${pageBreak}</w:pPr>` : "";
    return `<w:p>${properties}${run(text, options)}</w:p>`;
  }

  function labelParagraph(label, value) {
    return `<w:p><w:pPr><w:spacing w:after="70"/></w:pPr>${run(`${label}: `, { bold: true, size: 20 })}${run(value, { size: 20 })}</w:p>`;
  }

  function decodeHtml(value) {
    return String(value||'').replace(/&#x([0-9a-f]+);/gi,(_,n)=>String.fromCodePoint(parseInt(n,16)))
      .replace(/&#(\d+);/g,(_,n)=>String.fromCodePoint(Number(n))).replace(/&nbsp;/g,' ')
      .replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&apos;/g,"'").replace(/&amp;/g,'&');
  }
  const hasRichMath=html=>/<(?:math|sup|sub)\b/i.test(html||'');
  function richParagraphs(html, question, prefix='') {
    const formulaMap=new Map((question.formulas||[]).map(f=>[f.hash,f]));
    const fragments=[];
    const source=String(html||'').replace(/<math\b[^>]*>[\s\S]*?<\/math\s*>/gi,part=>{
      const hash=part.match(/data-aab-formula=["']([^"']+)["']/)?.[1],record=formulaMap.get(hash);
      if(!record?.canonical||record.conversionIssues?.length)throw new Error('Não foi possível exportar a fórmula do Word.');
      // Keep the original OMML; do not reconstruct a fraction from flattened text.
      const key=`@@SFMATH${fragments.length}@@`;fragments.push(record.canonical);return key;
    });
    let output='',line=prefix?run(prefix,{bold:true,size:22}):'',bold=0,italic=0,script=[];
    const flush=()=>{if(line){output+=`<w:p><w:pPr><w:spacing w:after="130"/></w:pPr>${line}</w:p>`;line='';}};
    for(const token of source.match(/@@SFMATH\d+@@|<[^>]+>|[^<@]+|@/g)||[]) {
      const formula=token.match(/^@@SFMATH(\d+)@@$/);if(formula){line+=fragments[Number(formula[1])];continue;}
      if(!token.startsWith('<')) {const value=decodeHtml(token);if(value){let r=run(value,{bold:bold>0,italic:italic>0,size:22});if(script.length)r=r.replace('<w:rPr>',`<w:rPr><w:vertAlign w:val="${script.at(-1)==='sup'?'superscript':'subscript'}"/>`);line+=r;}continue;}
      const match=token.match(/^<(\/)?([a-z0-9]+)/i);if(!match)continue;const tag=match[2].toLowerCase(),end=Boolean(match[1]);
      if(['p','div','li','h1','h2','h3'].includes(tag)){if(end)flush();}
      else if(tag==='br')line+='<w:r><w:br/></w:r>';
      else if(['b','strong'].includes(tag))bold=Math.max(0,bold+(end?-1:1));
      else if(['i','em'].includes(tag))italic=Math.max(0,italic+(end?-1:1));
      else if(['sup','sub'].includes(tag)){if(end)script.pop();else script.push(tag);}
    }
    flush();return output;
  }

  function questionXml(question, index) {
    const parts = [];
    const discursive = isDiscursive(question);
    const name = String(question.name || `Questão (${index + 1})`).replace(/_Discursiva$/i, '') + (discursive ? '_Discursiva' : '');
    parts.push(paragraph(name, { style: "QuestionHeader", keepNext: true, pageBreakBefore: true }));
    parts.push(labelParagraph("Tema Gerador", question.theme || question.subjectHint || ""));
    parts.push(labelParagraph("Objetivo associado", question.objective || ""));
    parts.push(labelParagraph("Tipo de questão", discursive ? (question.typeDescription || "Discursiva, análise aplicada") : `Múltipla escolha com resposta única, ${question.typeDescription || "identificação conceitual"}`));
    const bodyLines = String(question.bodyText || "").split(/\n+/).map((line) => line.trim()).filter(Boolean);
    const command = bodyLines.at(-1) || "";
    const context = bodyLines.slice(0, -1).join("\n");
    const layout = text => root.SmartFoxAthus ? root.SmartFoxAthus.wrapLines(text).join("\n") : text;
    if (hasRichMath(question.bodyHtml)) parts.push(richParagraphs(question.bodyHtml,question));
    else {
      if (context) parts.push(paragraph(layout(context), { after: 130, size: 22 }));
      if (command) parts.push(paragraph(command, { after: 130, size: 22 }));
    }
    if (discursive) {
      parts.push(hasRichMath(question.expectedResponseHtml)?richParagraphs(question.expectedResponseHtml,question,"Resposta esperada: "):labelParagraph("Resposta esperada", question.expectedResponseText || ""));
      (question.responseCriteria || []).forEach((criterion, i) => parts.push(labelParagraph(`Critério ${i + 1}`, criterion)));
    } else {
      (question.alternatives || []).slice(0, 4).forEach((alternative, alternativeIndex) => {
        parts.push(hasRichMath(alternative.html)?richParagraphs(alternative.html,question,`${"ABCD"[alternativeIndex]}) `):paragraph(`${"ABCD"[alternativeIndex]}) ${alternative.plain || alternative.text || ""}`, { after: 80, size: 22 }));
      });
      const correctIndex = Number.isInteger(question.correctIndex) ? question.correctIndex : "ABCD".indexOf(String(question.correctLetter || "").toUpperCase());
      parts.push(labelParagraph("Gabarito", "ABCD"[correctIndex]));
    }
    parts.push(labelParagraph("Feedback pedagógico", ""));
    parts.push(hasRichMath(question.feedbackHtml)?richParagraphs(question.feedbackHtml,question):paragraph(layout(question.feedbackText || ""), {after:100,size:22}));
    // Source excerpts and working notes remain in the professor review panel.
    return parts.join("");
  }

  function documentXml(questions, metadata) {
    const title = metadata?.title || `Avaliação ${metadata?.assessment || questions[0]?.assessment || "Athus"}`;
    const subject = metadata?.subject || questions[0]?.theme || "";
    const objectiveCount = questions.filter((question) => !isDiscursive(question)).length;
    const discursiveCount = questions.length - objectiveCount;
    const objectiveRows = [...new Map(questions.filter(q=>q.objective).map(q=>[`${q.ua}:${q.objectiveNumber}:${q.objective}`,q])).values()];
    const body = [
      paragraph("UNIVERSIDADE IGUAÇU", { style: "DocumentTitle", keepNext: true }),
      paragraph("NÚCLEO DE EDUCAÇÃO A DISTÂNCIA", { style: "DocumentSubtitle", keepNext: true }),
      paragraph(title, { style: "DocumentTitle", keepNext: true }),
      subject ? paragraph(subject, { style: "DocumentSubtitle", keepNext: true }) : "",
      paragraph(`Documento produzido para revisão docente · ${questions.length} questão(ões) · ${objectiveCount} objetiva(s) A–D · ${discursiveCount} discursiva(s)`, { style: "AuditNote", after: 220 }),
      metadata?.partial ? paragraph(`AVALIAÇÃO PARCIAL: ${questions.length} de ${metadata.requested} questões solicitadas. Complemente as UAs indicadas na extensão antes de aplicar.`, { style: "AuditNote", after: 160 }) : "",
      metadata?.draft ? paragraph("RASCUNHO PARA REVISÃO — pendências Athus precisam ser corrigidas antes da aplicação.", {style:"AuditNote",after:180}) : "",
      paragraph("Orientações", {bold:true,keepNext:true}),
      paragraph("Leia a contextualização e o comando antes de responder. Nas objetivas, assinale uma única alternativa. Relacione sua decisão aos dados da situação e confira os cálculos quando houver.", {after:160,size:22}),
      objectiveRows.length ? paragraph("Objetivos de aprendizagem", {bold:true,keepNext:true}) : "",
      ...objectiveRows.map(q=>paragraph(`UA (${q.ua || '—'}) · Obj (${q.objectiveNumber || '—'}): ${q.objective}`, {after:80,size:22})),
      ...questions.map((q,i)=>questionXml(q,i)),
      '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr>'
    ].join("");
    return `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"><w:body>${body}</w:body></w:document>`;
  }

  function stylesXml() {
    return `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="pt-BR"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="276" w:lineRule="auto"/><w:suppressAutoHyphens/></w:pPr></w:pPrDefault></w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>
  <w:style w:type="paragraph" w:styleId="DocumentTitle"><w:name w:val="Document Title"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:pPr><w:jc w:val="center"/><w:spacing w:after="80"/></w:pPr><w:rPr><w:b/><w:color w:val="174E74"/><w:sz w:val="28"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="DocumentSubtitle"><w:name w:val="Document Subtitle"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:pPr><w:jc w:val="center"/><w:spacing w:after="100"/></w:pPr><w:rPr><w:color w:val="3B5F78"/><w:sz w:val="21"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="QuestionHeader"><w:name w:val="Question Header"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="180" w:after="120"/><w:shd w:fill="EAF3F8"/></w:pPr><w:rPr><w:b/><w:color w:val="123F5D"/><w:sz w:val="23"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="AuditNote"><w:name w:val="Audit Note"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:rPr><w:i/><w:color w:val="667A89"/><w:sz w:val="17"/></w:rPr></w:style>
</w:styles>`;
  }

  function contentTypesXml() {
    return `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/><Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/><Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/></Types>`;
  }

  async function buildDocx(questions, metadata) {
    const managed = metadata?.athusRules || questions.some(q=>q.generatedFromKnowledgeBase);
    if (managed && !metadata?.draft) {
      if(!root.SmartFoxAthus) throw new Error("Módulo Athus não carregado. Recarregue a extensão.");
      root.SmartFoxAthus.assertReady(questions,metadata?.athusRules || questions[0]?.generationRules);
    }
    const validationErrors = validateQuestions(questions);
    if (validationErrors.length) throw new Error(`O Word não foi criado porque o lote possui ${validationErrors.length} inconsistência(s):\n- ${validationErrors.slice(0, 8).join("\n- ")}${validationErrors.length > 8 ? `\n- e mais ${validationErrors.length - 8}` : ""}`);
    if (typeof root.JSZip === "undefined") throw new Error("O gerador de DOCX não foi carregado.");
    const zip = new root.JSZip();
    const now = new Date().toISOString();
    zip.file("[Content_Types].xml", contentTypesXml());
    zip.folder("_rels").file(".rels", `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/></Relationships>`);
    zip.folder("word").file("document.xml", documentXml(questions, metadata));
    zip.folder("word").file("styles.xml", stylesXml());
    zip.folder("word").folder("_rels").file("document.xml.rels", `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>`);
    zip.folder("docProps").file("core.xml", `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>${escapeXml(metadata?.title || "Avaliação Athus")}</dc:title><dc:creator>SmartFox 11.0</dc:creator><cp:lastModifiedBy>SmartFox 11.0</cp:lastModifiedBy><dcterms:created xsi:type="dcterms:W3CDTF">${now}</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">${now}</dcterms:modified></cp:coreProperties>`);
    zip.folder("docProps").file("app.xml", `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>SmartFox 11.0</Application><AppVersion>11.0</AppVersion></Properties>`);
    return zip.generateAsync({ type: "blob", mimeType: "application/vnd.openxmlformats-officedocument.wordprocessingml.document", compression: "DEFLATE", compressionOptions: { level: 6 } });
  }

  async function download(questions, metadata) {
    const blob = await buildDocx(questions, metadata);
    const assessment = metadata?.assessment || questions[0]?.assessment || "ATHUS";
    const subject = metadata?.subject || questions[0]?.theme || "Avaliacao";
    const fileName = `${safeName(`${metadata?.draft ? "RASCUNHO_" : ""}${assessment}_${subject}_SmartFox`)}.docx`;
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = fileName;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 2500);
    return fileName;
  }

  root.AvaliaDocxExporter = Object.freeze({ version: "11.0.0", escapeXml, safeName, validateQuestions, documentXml, buildDocx, download });
})(typeof window !== "undefined" ? window : globalThis);
