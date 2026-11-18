(function (root) {
  "use strict";

  const VERSION = "11.0.0";
  const FORBIDDEN_CONCEPT = /(?:https?:\/\/|www\.|\bdoi\b|\bqr\s*code\b|\bqrgo\b|\bfonte\s*:|\badaptad[oa]\s+de\b|\bdispon[ií]vel\s+em\b|\bacesso\s+em\b|\b(?:isbn|issn|editora|ediç[aã]o|et\s+al\.)\b|\b(?:19|20)\d{2}\b|\b[A-ZÁÀÂÃÉÈÊÍÓÔÕÚÜÇ]{3,},\s*[A-ZÁÀÂÃÉÈÊÍÓÔÕÚÜÇ][A-Za-zÀ-ÿ]+)/i;

  function clean(value) {
    return String(value == null ? "" : value)
      .replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u00AD\u200B-\u200D\uFEFF]/g, "")
      .replace(/\s+/g, " ")
      .trim();
  }

  function normalize(value) {
    return clean(value)
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLocaleLowerCase("pt-BR");
  }

  function unique(values) {
    const seen = new Set();
    return values.filter((value) => {
      const key = normalize(value);
      if (!key || seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }

  function safeConcept(value) {
    const text = clean(value);
    if (text.length < 2 || text.length > 180 || FORBIDDEN_CONCEPT.test(text)) return "";
    if (/^(?:[A-D]\)|alternativa\s+[A-D]|resposta\s*:|gabarito\s*:)/i.test(text)) return "";
    return text;
  }

  function questionUa(question) {
    const direct = clean(question?.ua);
    if (/^\d{1,2}$/.test(direct)) return String(Number(direct));
    const named = clean(question?.name).match(/\bUA\s*\(?\s*(\d{1,2})/i)?.[1];
    return named ? String(Number(named)) : "Geral";
  }

  function skillSet(difficulties) {
    const normalized = difficulties.map(normalize);
    const skills = ["Explicar os conceitos centrais com vocabulário próprio e precisão terminológica."];
    if (normalized.some((value) => /facil/.test(value))) skills.push("Reconhecer definições, características e finalidades essenciais.");
    if (normalized.some((value) => /medio|media/.test(value))) skills.push("Comparar conceitos próximos e aplicá-los a situações diferentes.");
    if (normalized.some((value) => /dificil/.test(value))) skills.push("Analisar relações, justificar critérios e integrar mais de uma informação.");
    return unique(skills);
  }

  function buildStudyGuideModel(questions, metadata) {
    if (!Array.isArray(questions) || !questions.length) throw new Error("Não há questões disponíveis para criar o roteiro de estudos.");
    const subject = clean(metadata?.subject || questions.find((question) => clean(question?.theme || question?.subjectHint))?.theme || questions.find((question) => clean(question?.subjectHint))?.subjectHint || "Disciplina");
    const assessment = clean(metadata?.assessment || questions.find((question) => clean(question?.assessment))?.assessment || "Avaliação");
    const groups = new Map();

    questions.forEach((question) => {
      const ua = questionUa(question);
      if (!groups.has(ua)) groups.set(ua, { ua, objectives: [], concepts: [], difficulties: [], types: [] });
      const group = groups.get(ua);
      const objective = clean(question?.objective || question?.curriculumEvidence?.objective);
      if (objective) group.objectives.push(objective);
      const topics = question.studyTopics?.length ? question.studyTopics : [question?.theme || question?.subjectHint || metadata?.subject];
      topics.forEach((topic) => {
        const concept = safeConcept(topic);
        if (concept) group.concepts.push(concept);
      });
      if (clean(question?.difficulty)) group.difficulties.push(clean(question.difficulty));
      if (clean(question?.typeDescription)) group.types.push(clean(question.typeDescription));
    });

    const orderedGroups = Array.from(groups.values())
      .sort((left, right) => left.ua === "Geral" ? 1 : right.ua === "Geral" ? -1 : Number(left.ua) - Number(right.ua))
      .map((group) => {
        const objectives = unique(group.objectives);
        const concepts = unique(group.concepts).sort((left, right) => left.localeCompare(right, "pt-BR")).slice(0, 18);
        const uaLabel = group.ua === "Geral" ? "Conteúdos gerais" : `UA ${group.ua}`;
        const effectiveObjectives = objectives.length ? objectives : [`Revisar os conteúdos de ${subject} associados a ${uaLabel}.`];
        const skills = skillSet(group.difficulties);
        return {
          ua: group.ua,
          label: uaLabel,
          objectives: effectiveObjectives,
          concepts,
          skills,
          studyActions: [
            `Leia os materiais de ${uaLabel} e produza um resumo curto para cada objetivo.`,
            concepts.length >= 2 ? `Monte um quadro comparativo entre ${concepts.slice(0, 4).join(", ")}.` : "Organize um mapa conceitual com definições, características e exemplos.",
            "Crie um exemplo aplicado e explique por que o conceito escolhido é adequado ao caso."
          ],
          selfCheck: [
            `Consigo explicar os objetivos de ${uaLabel} sem consultar minhas anotações?`,
            concepts.length >= 2 ? "Consigo diferenciar os conceitos listados sem depender apenas de palavras-chave?" : "Consigo definir o conteúdo central e reconhecer um exemplo correto?",
            "Consigo justificar uma decisão usando critérios do conteúdo, em vez de apenas memorizar uma frase?"
          ]
        };
      });

    if (!orderedGroups.length) throw new Error("As questões não possuem informações suficientes para organizar o roteiro.");
    if (orderedGroups.every((group) => !group.concepts.length)) throw new Error("Nenhum tema de estudo foi identificado. Informe o tema das questões ou os tópicos de estudo antes de gerar o guia.");

    return {
      version: VERSION,
      title: "Roteiro de estudos",
      subject,
      assessment,
      generatedAt: new Date().toISOString(),
      groups: orderedGroups,
      questionCount: questions.length,
      objectives: unique(orderedGroups.flatMap((group) => group.objectives)),
      integrity: {
        studentSafe: true,
        includesQuestionText: false,
        includesAnswerKey: false,
        includesFeedback: false
      }
    };
  }

  function validateStudyGuideModel(model) {
    const errors = [];
    if (!clean(model?.subject)) errors.push("disciplina ausente");
    if (!clean(model?.assessment)) errors.push("avaliação ausente");
    if (!Array.isArray(model?.groups) || !model.groups.length) errors.push("nenhuma UA ou grupo de conteúdo foi reconhecido");
    (model?.groups || []).forEach((group) => {
      if (!group.objectives?.length) errors.push(`${group.label}: objetivo ausente`);
      if (!group.concepts?.length) errors.push(`${group.label}: nenhum conceito seguro`);
      if ((group.concepts || []).some((concept) => FORBIDDEN_CONCEPT.test(concept))) errors.push(`${group.label}: referência externa indevida`);
    });
    return errors;
  }

  function escapeXml(value) {
    return clean(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&apos;");
  }

  function safeName(value) {
    return clean(value || "Roteiro_de_Estudos")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-zA-Z0-9_-]+/g, "_")
      .replace(/_+/g, "_")
      .replace(/^_|_$/g, "")
      .slice(0, 95) || "Roteiro_de_Estudos";
  }

  function run(text, options) {
    const properties = [
      options?.bold ? "<w:b/>" : "",
      options?.italic ? "<w:i/>" : "",
      options?.color ? `<w:color w:val="${escapeXml(options.color)}"/>` : "",
      options?.size ? `<w:sz w:val="${Number(options.size)}"/><w:szCs w:val="${Number(options.size)}"/>` : ""
    ].join("");
    return `<w:r>${properties ? `<w:rPr>${properties}</w:rPr>` : ""}<w:t xml:space="preserve">${escapeXml(text)}</w:t></w:r>`;
  }

  function paragraph(text, options) {
    const style = options?.style ? `<w:pStyle w:val="${escapeXml(options.style)}"/>` : "";
    const spacing = `<w:spacing w:before="${Number(options?.before || 0)}" w:after="${Number(options?.after ?? 120)}" w:line="${Number(options?.line || 276)}" w:lineRule="auto"/>`;
    const align = options?.align ? `<w:jc w:val="${escapeXml(options.align)}"/>` : "";
    const keep = options?.keepNext ? "<w:keepNext/>" : "";
    const pageBreak = options?.pageBreakBefore ? "<w:pageBreakBefore/>" : "";
    const indent = options?.indent ? `<w:ind w:left="${Number(options.indent)}" w:hanging="${Number(options.hanging || 0)}"/>` : "";
    const prefix = options?.bullet ? "•   " : options?.checkbox ? "☐  " : "";
    return `<w:p><w:pPr>${style}${spacing}${align}${keep}${pageBreak}${indent}</w:pPr>${run(`${prefix}${text}`, options)}</w:p>`;
  }

  function labelParagraph(label, value) {
    return `<w:p><w:pPr><w:spacing w:after="80" w:line="276" w:lineRule="auto"/></w:pPr>${run(`${label} —`, { bold: true, size: 21 })}${run(` ${value}`, { size: 21 })}</w:p>`;
  }

  function tableCell(text, width, options) {
    const fill = options?.header ? "1F4E78" : options?.shade ? "F1F6FA" : "FFFFFF";
    const color = options?.header ? "FFFFFF" : "000000";
    return `<w:tc><w:tcPr><w:tcW w:w="${width}" w:type="dxa"/><w:shd w:fill="${fill}"/><w:tcMar><w:top w:w="90" w:type="dxa"/><w:left w:w="110" w:type="dxa"/><w:bottom w:w="90" w:type="dxa"/><w:right w:w="110" w:type="dxa"/></w:tcMar><w:vAlign w:val="center"/></w:tcPr><w:p><w:pPr><w:spacing w:after="0" w:line="250" w:lineRule="auto"/>${options?.center ? '<w:jc w:val="center"/>' : ""}</w:pPr>${run(text, { bold: options?.header, color, size: options?.header ? 19 : 18 })}</w:p></w:tc>`;
  }

  function overviewTable(groups) {
    const rows = [
      `<w:tr><w:trPr><w:tblHeader/></w:trPr>${tableCell("Unidade", 1050, { header: true, center: true })}${tableCell("Objetivos de aprendizagem", 4300, { header: true })}${tableCell("Conteúdos prioritários", 4300, { header: true })}</w:tr>`,
      ...groups.map((group, index) => `<w:tr>${tableCell(group.label, 1050, { center: true, shade: index % 2 === 1 })}${tableCell(group.objectives.join(" "), 4300, { shade: index % 2 === 1 })}${tableCell(group.concepts.slice(0, 10).join(", "), 4300, { shade: index % 2 === 1 })}</w:tr>`)
    ].join("");
    return `<w:tbl><w:tblPr><w:tblW w:w="9650" w:type="dxa"/><w:tblLayout w:type="fixed"/><w:tblBorders><w:top w:val="single" w:sz="4" w:color="D9D9D9"/><w:left w:val="single" w:sz="4" w:color="D9D9D9"/><w:bottom w:val="single" w:sz="4" w:color="D9D9D9"/><w:right w:val="single" w:sz="4" w:color="D9D9D9"/><w:insideH w:val="single" w:sz="4" w:color="D9D9D9"/><w:insideV w:val="single" w:sz="4" w:color="D9D9D9"/></w:tblBorders><w:tblCellMar><w:top w:w="80" w:type="dxa"/><w:left w:w="100" w:type="dxa"/><w:bottom w:w="80" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid><w:gridCol w:w="1050"/><w:gridCol w:w="4300"/><w:gridCol w:w="4300"/></w:tblGrid>${rows}</w:tbl>`;
  }

  function studyGuideDocumentXml(model) {
    const parts = [
      paragraph("UNIVERSIDADE IGUAÇU", { style: "Institution", align: "center", keepNext: true, after: 55 }),
      paragraph("NÚCLEO DE EDUCAÇÃO A DISTÂNCIA", { style: "InstitutionSub", align: "center", keepNext: true, after: 190 }),
      paragraph("Roteiro de estudos", { style: "Title", align: "center", keepNext: true, after: 80 }),
      paragraph(model.subject, { style: "Subtitle", align: "center", keepNext: true, after: 45 }),
      paragraph(model.assessment, { style: "Subtitle", align: "center", after: 220 }),
      paragraph("Como utilizar este roteiro", { style: "Heading1", keepNext: true }),
      paragraph("Este roteiro organiza os objetivos e os conteúdos relacionados à avaliação. Use-o para planejar a revisão, comparar conceitos e verificar o que ainda precisa ser retomado. As atividades propostas não reproduzem as perguntas da prova e não apresentam respostas prontas.", { after: 110 }),
      paragraph("Estude cada unidade com os materiais indicados pelo professor antes de responder às atividades de autoavaliação.", { bullet: true, indent: 360, hanging: 180, after: 55 }),
      paragraph("Explique os conceitos com suas próprias palavras e confirme definições no material da disciplina.", { bullet: true, indent: 360, hanging: 180, after: 55 }),
      paragraph("Registre dúvidas específicas para discutir com o professor ou com a turma.", { bullet: true, indent: 360, hanging: 180, after: 140 }),
      paragraph("Mapa dos conteúdos", { style: "Heading1", keepNext: true, after: 100 }),
      overviewTable(model.groups),
      paragraph("Plano de revisão em três etapas", { style: "Heading1", keepNext: true, before: 220 }),
      labelParagraph("Etapa 1 Compreender", "Leia os materiais e produza um resumo curto para cada objetivo de aprendizagem."),
      labelParagraph("Etapa 2 Relacionar", "Compare conceitos próximos, construa exemplos e identifique os critérios que diferenciam cada um."),
      labelParagraph("Etapa 3 Verificar", "Responda às perguntas de autoavaliação sem consultar anotações e retome somente os pontos em que houver insegurança."),
    ];

    model.groups.forEach((group) => {
      parts.push(paragraph(group.label, { style: "Heading1", keepNext: true, pageBreakBefore: true, before: 0, after: 95 }));
      parts.push(paragraph("Objetivos de aprendizagem", { style: "Heading2", keepNext: true, after: 65 }));
      group.objectives.forEach((objective) => parts.push(paragraph(objective, { bullet: true, indent: 360, hanging: 180, after: 55 })));
      parts.push(paragraph("Conteúdos para revisar", { style: "Heading2", keepNext: true, before: 100, after: 65 }));
      parts.push(paragraph(group.concepts.join(", "), { after: 105 }));
      parts.push(paragraph("Habilidades a desenvolver", { style: "Heading2", keepNext: true, after: 65 }));
      group.skills.forEach((skill) => parts.push(paragraph(skill, { bullet: true, indent: 360, hanging: 180, after: 55 })));
      parts.push(paragraph("Ações de estudo", { style: "Heading2", keepNext: true, before: 100, after: 65 }));
      group.studyActions.forEach((action, index) => parts.push(paragraph(`${index + 1}. ${action}`, { indent: 260, hanging: 220, after: 55 })));
      parts.push(paragraph("Autoavaliação", { style: "Heading2", keepNext: true, before: 100, after: 65 }));
      group.selfCheck.forEach((prompt) => parts.push(paragraph(prompt, { checkbox: true, indent: 360, hanging: 180, after: 55 })));
    });

    parts.push(paragraph("Checklist final", { style: "Heading1", keepNext: true, pageBreakBefore: true, before: 0, after: 90 }));
    [
      "Revisei todos os objetivos apresentados neste roteiro.",
      "Consigo definir e diferenciar os conceitos sem consultar o resumo.",
      "Consigo aplicar os conteúdos em exemplos novos.",
      "Registrei os pontos que ainda precisam de esclarecimento.",
      "Retomei os materiais da disciplina nos itens em que tive dificuldade."
    ].forEach((item) => parts.push(paragraph(item, { checkbox: true, indent: 360, hanging: 180, after: 65 })));
    parts.push(paragraph("Bom estudo", { style: "Closing", align: "center", before: 220, after: 120 }));
    parts.push('<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1080" w:right="1080" w:bottom="1080" w:left="1080" w:header="600" w:footer="600" w:gutter="0"/></w:sectPr>');
    return `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>${parts.join("")}</w:body></w:document>`;
  }

  function stylesXml() {
    return `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/><w:color w:val="000000"/><w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="pt-BR"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="276" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:color w:val="000000"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:pPr><w:jc w:val="center"/><w:spacing w:after="80"/></w:pPr><w:rPr><w:b/><w:color w:val="000000"/><w:sz w:val="34"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:pPr><w:jc w:val="center"/><w:spacing w:after="70"/></w:pPr><w:rPr><w:color w:val="000000"/><w:sz w:val="23"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Institution"><w:name w:val="Institution"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:rPr><w:b/><w:color w:val="000000"/><w:sz w:val="24"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="InstitutionSub"><w:name w:val="Institution Sub"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:rPr><w:color w:val="000000"/><w:sz w:val="20"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="220" w:after="100"/></w:pPr><w:rPr><w:b/><w:color w:val="000000"/><w:sz w:val="26"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="120" w:after="70"/></w:pPr><w:rPr><w:b/><w:color w:val="000000"/><w:sz w:val="22"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Closing"><w:name w:val="Closing"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:rPr><w:b/><w:color w:val="000000"/><w:sz w:val="23"/></w:rPr></w:style>
</w:styles>`;
  }

  function contentTypesXml() {
    return `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/><Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/><Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/></Types>`;
  }

  async function buildStudyGuideDocx(questions, metadata) {
    if (typeof root.JSZip === "undefined") throw new Error("O gerador de DOCX não foi carregado.");
    const model = buildStudyGuideModel(questions, metadata);
    const validationErrors = validateStudyGuideModel(model);
    if (validationErrors.length) throw new Error(`O roteiro não foi criado: ${validationErrors.join("; ")}.`);
    const zip = new root.JSZip();
    const now = new Date().toISOString();
    zip.file("[Content_Types].xml", contentTypesXml());
    zip.folder("_rels").file(".rels", `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/></Relationships>`);
    zip.folder("word").file("document.xml", studyGuideDocumentXml(model));
    zip.folder("word").file("styles.xml", stylesXml());
    zip.folder("word").folder("_rels").file("document.xml.rels", `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>`);
    zip.folder("docProps").file("core.xml", `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>${escapeXml(`Roteiro de estudos ${model.subject}`)}</dc:title><dc:subject>${escapeXml(model.assessment)}</dc:subject><dc:creator>SmartFox 11.0</dc:creator><cp:lastModifiedBy>SmartFox 11.0</cp:lastModifiedBy><dcterms:created xsi:type="dcterms:W3CDTF">${now}</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">${now}</dcterms:modified></cp:coreProperties>`);
    zip.folder("docProps").file("app.xml", `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>SmartFox 11.0</Application><AppVersion>11.0</AppVersion></Properties>`);
    const blob = await zip.generateAsync({ type: "blob", mimeType: "application/vnd.openxmlformats-officedocument.wordprocessingml.document", compression: "DEFLATE", compressionOptions: { level: 6 } });
    return { blob, model };
  }

  async function buildAssessmentPackage(questions, metadata) {
    if (!root.AvaliaDocxExporter || !root.JSZip) throw new Error("Recarregue a extensão para carregar os exportadores.");
    const [assessment, guide] = await Promise.all([
      root.AvaliaDocxExporter.buildDocx(questions, metadata),
      buildStudyGuideDocx(questions, metadata)
    ]);
    const zip = new root.JSZip();
    const stem = safeName((metadata?.assessment || "Avaliacao") + "_" + (metadata?.subject || "Disciplina"));
    const teacherFile = "Professor_" + stem + (metadata?.partial ? "_PARCIAL" : "") + ".docx";
    const studentFile = "Guia_Aluno_" + stem + ".docx";
    zip.file(teacherFile, await assessment.arrayBuffer());
    zip.file(studentFile, await guide.blob.arrayBuffer());
    return { blob: await zip.generateAsync({ type: "blob", mimeType: "application/zip", compression: "DEFLATE" }), fileName: "Avaliacao_e_Guia_" + stem + ".zip", teacherFile, studentFile };
  }

  async function download(questions, metadata) {
    const { blob, model } = await buildStudyGuideDocx(questions, metadata);
    const fileName = `${safeName(`Roteiro_de_Estudos_${model.assessment}_${model.subject}`)}.docx`;
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = fileName;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 2500);
    return { fileName, model };
  }

  root.AvaliaStudentGuideExporter = Object.freeze({
    version: VERSION,
    clean,
    safeConcept,
    buildStudyGuideModel,
    validateStudyGuideModel,
    studyGuideDocumentXml,
    buildStudyGuideDocx,
    download,
    buildAssessmentPackage
  });
})(typeof window !== "undefined" ? window : globalThis);
