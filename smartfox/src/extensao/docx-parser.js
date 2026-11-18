(function () {
  "use strict";

  const REQUIRED_ALTERNATIVES = 4;
  const REVIEW_THRESHOLD = 0.84;
  const FILE_DIAGNOSTIC_VERSION = "1.0";
  const LETTERS = "ABCDE";
  const SUPPORTED_IMAGE_TYPES = Object.freeze(new Set(["png", "jpg", "jpeg", "gif", "webp", "svg", "bmp"]));
  const SUBJECT_STOPWORDS = Object.freeze(new Set([
    "a", "ao", "aos", "as", "da", "das", "de", "do", "dos", "e", "em", "entre", "na", "nas", "no", "nos", "o", "os", "ou", "para", "por",
    "projeto", "athus", "avaliacao", "questao", "questoes", "arquivo", "disciplina", "materia", "professor", "turma", "semestre", "unidade"
  ]));

  const TYPE_CATALOG = Object.freeze([
    { id: "60", key: "completion", label: "Questão de Complementação Simples", shortLabel: "Complementação simples" },
    { id: "62", key: "multiple-response", label: "Questão de Resposta Múltipla", shortLabel: "Resposta múltipla" },
    { id: "63", key: "assertion-reason", label: "Questão de Asserção e Razão", shortLabel: "Asserção e razão" },
    { id: "64", key: "interpretation", label: "Questão de Interpretação", shortLabel: "Interpretação" },
    { id: "65", key: "single-choice", label: "Outro Tipo", shortLabel: "Escolha única / outro tipo" },
    { id: "158", key: "discursive", label: "Questão Discursiva", shortLabel: "Discursiva" }
  ]);

  const COGNITIVE_CATALOG = Object.freeze([
    { id: "221", label: "Julgamento", verbs: ["avaliar", "julgar", "decidir", "criticar", "validar", "justificar"] },
    { id: "222", label: "Síntese", verbs: ["sintetizar", "planejar", "elaborar", "criar", "propor", "formular"] },
    { id: "223", label: "Análise", verbs: ["analisar", "distinguir", "comparar", "examinar", "relacionar", "diferenciar", "investigar"] },
    { id: "224", label: "Aplicação", verbs: ["aplicar", "calcular", "executar", "demonstrar", "utilizar", "resolver", "determinar"] },
    { id: "229", label: "Compreensão", verbs: ["compreender", "interpretar", "explicar", "descrever", "resumir"] },
    { id: "230", label: "(Re)conhecimento", verbs: ["reconhecer", "identificar", "definir", "listar", "nomear", "indicar"] }
  ]);

  function normalizeSpaces(value) {
    return String(value || "")
      .replace(/\u00a0/g, " ")
      .replace(/\u00ad/g, "")
      .replace(/[ \t]+/g, " ")
      .replace(/\s+([,.;:!?])/g, "$1")
      .replace(/\n{3,}/g, "\n\n")
      .trim();
  }

  function normalizeForMatch(value) {
    return normalizeSpaces(value)
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase();
  }

  function escapeHtml(value) {
    return String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function textToHtml(value) {
    return String(value || "").split(/\r?\n/).map((line) => `<p>${escapeHtml(line) || "<br>"}</p>`).join("");
  }

  function hashValue(value) {
    const engine = window.AvaliaBatchEngine;
    if (engine && typeof engine.fnv1a === "function") return engine.fnv1a(value);
    let hash = 0x811c9dc5;
    for (const character of String(value || "")) {
      hash ^= character.charCodeAt(0);
      hash = Math.imul(hash, 0x01000193);
    }
    return (hash >>> 0).toString(16).padStart(8, "0");
  }

  function decodeXml(value) {
    return String(value || "")
      .replace(/&#x([0-9a-f]+);/gi, (_match, number) => String.fromCodePoint(parseInt(number, 16)))
      .replace(/&#(\d+);/g, (_match, number) => String.fromCodePoint(parseInt(number, 10)))
      .replace(/&lt;/g, "<")
      .replace(/&gt;/g, ">")
      .replace(/&quot;/g, "\"")
      .replace(/&apos;/g, "'")
      .replace(/&amp;/g, "&");
  }

  function propertyValue(properties, localName) {
    if (!properties) return null;
    const expression = new RegExp(`<w:${localName}\\b([^>]*)\\/?>(?:[\\s\\S]*?<\\/w:${localName}>)?`, "i");
    const match = properties.match(expression);
    if (!match) return null;
    const valueMatch = match[1].match(/(?:w:)?val\s*=\s*["']([^"']+)["']/i);
    return valueMatch ? valueMatch[1] : "true";
  }

  function propertyEnabled(properties, localName) {
    const value = propertyValue(properties, localName);
    return value != null && !["0", "false", "none", "off"].includes(String(value).toLowerCase());
  }

  function symbolCharacter(xml, hex) {
    const point=parseInt(hex,16),font=xml.match(/(?:w:)?font=["']([^"']+)["']/i)?.[1]||'';
    // Mapping reference: https://www.unicode.org/Public/MAPPINGS/VENDORS/ADOBE/symbol.txt
    // Known Symbol font encodings only. Unknown private glyphs stay flagged for review.
    if (/^Symbol$/i.test(font)) {
      const code=point>=0xF000&&point<=0xF0FF?point-0xF000:point;
      const greek={J:'ϑ',V:'ς',j:'ϕ',v:'ϖ',A:'Α',B:'Β',G:'Γ',D:'Δ',E:'Ε',Z:'Ζ',H:'Η',Q:'Θ',I:'Ι',K:'Κ',L:'Λ',M:'Μ',N:'Ν',X:'Ξ',O:'Ο',P:'Π',R:'Ρ',S:'Σ',T:'Τ',U:'Υ',F:'Φ',C:'Χ',Y:'Ψ',W:'Ω',a:'α',b:'β',g:'γ',d:'δ',e:'ε',z:'ζ',h:'η',q:'θ',i:'ι',k:'κ',l:'λ',m:'μ',n:'ν',x:'ξ',o:'ο',p:'π',r:'ρ',s:'σ',t:'τ',u:'υ',f:'φ',c:'χ',y:'ψ',w:'ω'};
      const symbols={0x22:'∀',0x24:'∃',0x27:'∋',0x2A:'∗',0x2D:'−',0x40:'≅',0x5C:'∴',0x5E:'⊥',0x7E:'∼',0xA3:'≤',0xA5:'∞',0xB1:'±',0xB3:'≥',0xB4:'×',0xB8:'÷',0xB9:'≠',0xBA:'≡',0xBB:'≈',0xD6:'√',0xE5:'∑',0xF2:'∫',0xAB:'↔',0xAC:'←',0xAD:'↑',0xAE:'→',0xAF:'↓',0xB0:'°',0xB5:'∝',0xB6:'∂',0xC6:'∅',0xC7:'∩',0xC8:'∪',0xCC:'⊂',0xCD:'⊆',0xCE:'∈',0xCF:'∉',0xD1:'∇'};
      if(greek[String.fromCodePoint(code)])return greek[String.fromCodePoint(code)];
      if(symbols[code])return symbols[code];
      if(code>=0x30&&code<=0x39||[0x20,0x21,0x23,0x25,0x26,0x5F,0x28,0x29,0x2B,0x2C,0x2E,0x2F,0x3A,0x3B,0x3C,0x3D,0x3E,0x3F,0x5B,0x5D,0x7B,0x7C,0x7D].includes(code))return String.fromCodePoint(code);
      if(code>=0&&code<=0xFF)return String.fromCodePoint(0xF000+code);
    }
    return point<=0x10FFFF?String.fromCodePoint(point):'\uFFFD';
  }

  function textFromFragment(xmlFragment) {
    let text = "";
    const tokens = /<(w:(?:t|instrText)|m:t)\b[^>]*>([\s\S]*?)<\/\1\s*>|<w:(tab|br|cr|noBreakHyphen|softHyphen)\b[^>]*\/?\s*>|<w:sym\b[^>]*(?:w:)?char=["']([0-9a-f]{4,6})["'][^>]*\/?\s*>/gi;
    let token;
    while ((token = tokens.exec(xmlFragment)) !== null) {
      if (token[1]) text += decodeXml(token[2].replace(/<[^>]+>/g, ""));
      else if (token[3] === "tab") text += "\t";
      else if (token[3] === "br" || token[3] === "cr") text += "\n";
      else if (token[3] === "noBreakHyphen") text += "-";
      else if (token[3] === "softHyphen") text += "\u00ad";
      else if (token[4]) text += symbolCharacter(token[0], token[4]);
    }
    return text;
  }

  function canonicalFormulaXml(xml) {
    return String(xml || "")
      .replace(/\s+(?:w:rsid\w*|w14:paraId|w14:textId|mc:Ignorable)=["'][^"']*["']/gi, "")
      .replace(/>\s+</g, "><")
      .replace(/\s+/g, " ")
      .trim();
  }

  // Parse OMML as a tree: a nested fraction must never consume its parent's closing tag.
  // MathML is the format observed in the AvaliA native equation editor (15/09/2026).
  function convertOfficeMath(xml) {
    const root = {name: 'root', children: []}, stack = [root], issues = new Set();
    for (const token of String(xml || '').match(/<[^>]*>|[^<]+/g) || []) {
      if (/^<\//.test(token)) {
        const name = token.match(/^<\/([^\s>]+)/)?.[1];
        if (stack.length < 2 || stack.at(-1).name !== name) { issues.add('XML matemático incompleto'); continue; }
        stack.pop();
      } else if (/^<[!?]/.test(token)) continue;
      else if (token.startsWith('<')) {
        const name = token.match(/^<([^\s/>]+)/)?.[1];
        if (!name) continue;
        const attrs = {};
        for (const attr of token.matchAll(/([\w:]+)\s*=\s*["']([^"']*)["']/g)) attrs[attr[1].split(':').at(-1)] = decodeXml(attr[2]);
        const node = {name, attrs, children: []}; stack.at(-1).children.push(node);
        if (!/\/\s*>$/.test(token)) stack.push(node);
      } else stack.at(-1).children.push({name:'#text',text:decodeXml(token),children:[]});
    }
    if (stack.length !== 1) issues.add('XML matemático incompleto');
    const local = n => n?.name.split(':').at(-1);
    const child = (n, key) => n.children.find(c => local(c) === key);
    const property = (n, group, key, fallback) => child(child(n,group)||{children:[]},key)?.attrs?.val ?? fallback;
    const pair = (plain='', math='') => ({plain, math});
    const join = list => pair(list.map(x=>x.plain).join(''),list.map(x=>x.math).join(''));
    const row = x => `<mrow>${x.math}</mrow>`;
    function render(n) {
      if (!n) return pair();
      const k = local(n);
      const part = key => render(child(n,key));
      const contents = () => join(n.children.map(render));
      if (k === '#text') return pair(); // Whitespace outside m:t has no mathematical meaning.
      if (/Pr$/.test(k) || n.name.startsWith('w:') && k !== 't') return pair();
      if (k === 't') {
        const value = n.children.map(c=>c.text||'').join('');
        const tokens = value.match(/[\p{L}]+|[0-9]+(?:[.,][0-9]+)?|\s+|[^\p{L}\d\s]/gu)||[];
        return pair(value,tokens.map(v=>/^\s+$/.test(v)?'<mspace width="0.25em"/>':`<${/^\p{L}/u.test(v)?'mi':/^\d/.test(v)?'mn':'mo'}>${escapeHtml(v)}</${/^\p{L}/u.test(v)?'mi':/^\d/.test(v)?'mn':'mo'}>`).join(''));
      }
      if (['root','oMath','oMathPara','e','num','den','sub','sup','deg','fName','lim','mr'].includes(k)) return contents();
      if(k === 'r') {
        const value=contents(),style=property(n,'rPr','sty',''),script=property(n,'rPr','scr','');
        const scripts={roman:'normal',script:'script',fraktur:'fraktur','double-struck':'double-struck','sans-serif':'sans-serif',monospace:'monospace'};
        const variant=script?scripts[script]:({b:'bold',bi:'bold-italic',p:'normal',i:'italic'}[style]);
        if(script&&!variant)issues.add(`Estilo matemático ${script}`);
        return variant?pair(value.plain,`<mstyle mathvariant="${variant}">${value.math}</mstyle>`):value;
      }
      if(k === 'f') {
        const a=part('num'),b=part('den'),type=property(n,'fPr','type','bar');
        if(!a.math||!b.math)issues.add('Fração sem numerador ou denominador');
        const attr=type==='noBar'?' linethickness="0"':type==='skw'?' bevelled="true"':'';
        if(!['bar','noBar','skw','lin'].includes(type))issues.add(`Tipo de fração ${type}`);
        return pair(type==='noBar'?`binomial(${a.plain}; ${b.plain})`:`(${a.plain})/(${b.plain})`,type==='lin'?`${row(a)}<mo>/</mo>${row(b)}`:`<mfrac${attr}>${row(a)}${row(b)}</mfrac>`);
      }
      if(['sSup','sSub','sSubSup','sPre'].includes(k)) {
        const e=part('e'),sub=part('sub'),sup=part('sup');
        if(!e.math)issues.add('Expoente ou índice sem base');
        if(k==='sPre')return pair(`_(${sub.plain})^(${sup.plain})${e.plain}`,`<mmultiscripts>${row(e)}<mprescripts/>${row(sub)}${row(sup)}</mmultiscripts>`);
        const tag={sSup:'msup',sSub:'msub',sSubSup:'msubsup'}[k];
        return pair(`${e.plain}${k!=='sSup'?`_(${sub.plain})`:''}${k!=='sSub'?`^(${sup.plain})`:''}`,`<${tag}>${row(e)}${k!=='sSup'?row(sub):''}${k!=='sSub'?row(sup):''}</${tag}>`);
      }
      if(k==='rad') {
        const e=part('e'),deg=part('deg'),hidden=property(n,'radPr','degHide','0');
        return !deg.math||['1','true','on'].includes(hidden)?pair(`√(${e.plain})`,`<msqrt>${row(e)}</msqrt>`):pair(`${deg.plain}√(${e.plain})`,`<mroot>${row(e)}${row(deg)}</mroot>`);
      }
      if(k==='d') {
        const begin=property(n,'dPr','begChr','('),end=property(n,'dPr','endChr',')'),sep=property(n,'dPr','sepChr','|');
        const list=n.children.filter(c=>local(c)==='e').map(render);
        return pair(begin+list.map(x=>x.plain).join(sep)+end,`<mrow><mo fence="true">${escapeHtml(begin)}</mo>${list.map(row).join(`<mo separator="true">${escapeHtml(sep)}</mo>`)}<mo fence="true">${escapeHtml(end)}</mo></mrow>`);
      }
      if(k==='nary') {
        const e=part('e'),sub=part('sub'),sup=part('sup'),op=property(n,'naryPr','chr','∫');
        const showSub=sub.math&&!['1','true','on'].includes(property(n,'naryPr','subHide','0'));
        const showSup=sup.math&&!['1','true','on'].includes(property(n,'naryPr','supHide','0'));
        const side=property(n,'naryPr','limLoc','undOvr')==='subSup';
        const tag=showSub&&showSup?(side?'msubsup':'munderover'):showSub?(side?'msub':'munder'):(side?'msup':'mover');
        const operator=`<mo>${escapeHtml(op)}</mo>`;
        return pair(`${op}${showSub?`_(${sub.plain})`:''}${showSup?`^(${sup.plain})`:''}(${e.plain})`,(showSub||showSup?`<${tag}>${operator}${showSub?row(sub):''}${showSup?row(sup):''}</${tag}>`:operator)+row(e));
      }
      if(k==='func') {const f=part('fName'),e=part('e');return pair(`${f.plain} ${e.plain}`,`${row(f)}<mo>⁡</mo>${row(e)}`);}
      if(k==='limLow'||k==='limUpp') {const e=part('e'),lim=part('lim'),tag=k==='limLow'?'munder':'mover';return pair(`${e.plain}${k==='limLow'?'_':'^'}(${lim.plain})`,`<${tag}>${row(e)}${row(lim)}</${tag}>`);}
      if(k==='m'||k==='eqArr') {
        const rows=n.children.filter(c=>local(c)===(k==='m'?'mr':'e')).map(n=>k==='m'?n.children.filter(c=>local(c)==='e').map(render):[render(n)]);
        return pair(`[${rows.map(r=>r.map(x=>x.plain).join('; ')).join(' | ')}]`,`<mtable>${rows.map(r=>`<mtr>${r.map(c=>`<mtd>${c.math}</mtd>`).join('')}</mtr>`).join('')}</mtable>`);
      }
      if(k==='acc'||k==='bar'||k==='groupChr') {
        const e=part('e'),mark=property(n,k+'Pr','chr',k==='acc'?'̂':k==='bar'?'¯':'⏟'),below=property(n,k+'Pr','pos',k==='groupChr'?'bot':'top')==='bot',tag=below?'munder':'mover';
        return pair(`${mark}(${e.plain})`,`<${tag} ${below?'accentunder':'accent'}="true">${row(e)}<mo>${escapeHtml(mark)}</mo></${tag}>`);
      }
      issues.add(`Estrutura OMML ${k}`);
      return contents();
    }
    const result=render(root);
    return {...result,plain:normalizeSpaces(result.plain),issues:[...issues]};
  }

  function formulaRecord(xml) {
    const canonical=canonicalFormulaXml(xml),hash=hashValue(canonical),converted=convertOfficeMath(xml);
    return {hash,canonical,plain:converted.plain||'[fórmula]',conversionIssues:converted.issues,
      html:`<math xmlns="http://www.w3.org/1998/Math/MathML" data-aab-formula="${hash}" title="Fórmula Word verificada: ${hash}"><mrow>${converted.math}</mrow></math>`};
  }

  function latexFormulaRecord(source) {
    const input=String(source||'').trim(),issues=new Set();let index=0;
    const commands={alpha:'α',beta:'β',gamma:'γ',delta:'δ',theta:'θ',lambda:'λ',mu:'μ',pi:'π',sigma:'σ',phi:'φ',omega:'ω',Delta:'Δ',Sigma:'Σ',Omega:'Ω',times:'×',cdot:'·',div:'÷',pm:'±',le:'≤',leq:'≤',ge:'≥',geq:'≥',ne:'≠',neq:'≠',in:'∈',notin:'∉',cup:'∪',cap:'∩',infty:'∞',to:'→',rightarrow:'→',leftarrow:'←',sum:'∑',prod:'∏',int:'∫'};
    const tag=value=>/^\d+(?:[.,]\d+)?$/.test(value)?'mn':/^\p{L}+$/u.test(value)?'mi':'mo';
    const node=value=>`<${tag(value)}>${escapeHtml(value)}</${tag(value)}>`;
    const skip=()=>{while(/\s/.test(input[index]||''))index++;};
    function argument(){skip();if(input[index]==='{'){index++;const value=sequence('}');if(input[index]==='}')index++;else issues.add('Chave LaTeX não fechada');return value;}return atom();}
    function atom(){
      skip();if(index>=input.length)return '';
      let value='';
      if(input[index]==='{'){index++;value=sequence('}');if(input[index]==='}')index++;else issues.add('Chave LaTeX não fechada');}
      else if(input[index]==='\\'){
        const match=input.slice(index+1).match(/^([A-Za-z]+|.)/),command=match?.[1]||'';index+=1+command.length;
        if(command==='frac'){const top=argument(),bottom=argument();if(!top||!bottom)issues.add('Fração LaTeX incompleta');value=`<mfrac><mrow>${top}</mrow><mrow>${bottom}</mrow></mfrac>`;}
        else if(command==='sqrt'){const body=argument();if(!body)issues.add('Raiz LaTeX incompleta');value=`<msqrt><mrow>${body}</mrow></msqrt>`;}
        else if(command==='text'||command==='mathrm'||command==='mathbf'||command==='mathit'){const body=argument();value=command==='text'?`<mtext>${body.replace(/<[^>]+>/g,'')}</mtext>`:`<mstyle mathvariant="${command==='mathbf'?'bold':command==='mathit'?'italic':'normal'}">${body}</mstyle>`;}
        else if(commands[command])value=node(commands[command]);
        else {issues.add(`Comando LaTeX \\${command} não suportado`);value=node(`\\${command}`);}
      } else {
        const match=input.slice(index).match(/^(?:\d+(?:[.,]\d+)?|[\p{L}]+|.)/u),token=match?.[0]||input[index];index+=token.length;value=node(token);
      }
      skip();let sub='',sup='';
      while(input[index]==='_'||input[index]==='^'){const marker=input[index++],part=argument();if(marker==='_')sub=part;else sup=part;skip();}
      if(sub&&sup)value=`<msubsup><mrow>${value}</mrow><mrow>${sub}</mrow><mrow>${sup}</mrow></msubsup>`;
      else if(sub)value=`<msub><mrow>${value}</mrow><mrow>${sub}</mrow></msub>`;
      else if(sup)value=`<msup><mrow>${value}</mrow><mrow>${sup}</mrow></msup>`;
      return value;
    }
    function sequence(stop=''){let result='';while(index<input.length&&(!stop||input[index]!==stop)){if(input[index]==='}') {issues.add('Chave LaTeX inesperada');index++;continue;}result+=atom();}return result;}
    const math=sequence();
    const canonical=`latex:${input.replace(/\s+/g,' ')}`,hash=hashValue(canonical);
    return {hash,canonical,plain:input,conversionIssues:[...issues],latex:input,html:`<math xmlns="http://www.w3.org/1998/Math/MathML" data-aab-formula="${hash}" data-aab-latex="${escapeHtml(input)}" title="LaTeX convertido e verificado: ${hash}"><mrow>${math}</mrow></math>`};
  }

  function latexFormulaBlocks(text) {
    const formulas=[],expression=/\\\[([\s\S]*?)\\\]|\\\(([\s\S]*?)\\\)|\$\$([^$\n]+?)\$\$|(?<![\p{L}\d])\$([^$\n]+?)\$(?!\d)/gu;
    for(const match of String(text||'').matchAll(expression)){
      const body=[match[1],match[2],match[3],match[4]].find(value=>value!==undefined)?.trim()||'';
      if(!body||(!/[\\^_{}=+\-×÷]/.test(body)&&!/^\s*[\p{L}]\s*$/u.test(body)))continue;
      formulas.push({source:match[0],...latexFormulaRecord(body)});
    }
    return formulas;
  }

  function formatArithmeticText(value) {
    const formulas=[];
    const html=String(value||'').split(/\r?\n/).map(line=>{
      const expression=/(?<![\p{L}\d])\d+(?:[.,]\d+)?(?:\s*[×÷]\s*\d+(?:[.,]\d+)?)+(?:\s*=\s*\d+(?:[.,]\d+)?)?(?![\p{L}\d])/gu;
      let result='',offset=0;
      for(const match of line.matchAll(expression)){
        result+=escapeHtml(line.slice(offset,match.index));
        const formula=formulaRecord(`<m:oMath><m:r><m:t>${escapeHtml(match[0])}</m:t></m:r></m:oMath>`);
        formulas.push(formula);result+=formula.html;offset=match.index+match[0].length;
      }
      return `<p>${result+escapeHtml(line.slice(offset))||'<br>'}</p>`;
    }).join('');
    return {html,formulas};
  }

  function mediaMime(extension) {
    const catalog = { png: "image/png", jpg: "image/jpeg", jpeg: "image/jpeg", gif: "image/gif", webp: "image/webp", svg: "image/svg+xml", bmp: "image/bmp", tif: "image/tiff", tiff: "image/tiff", emf: "image/x-emf", wmf: "image/x-wmf" };
    return catalog[String(extension || "").toLowerCase()] || "application/octet-stream";
  }

  function relationshipMap(relsXml) {
    const relationships = new Map();
    const expression = /<Relationship\b([^>]*?)\/?\s*>/gi;
    let match;
    while ((match = expression.exec(String(relsXml || ""))) !== null) {
      const id = match[1].match(/\bId=["']([^"']+)["']/i)?.[1];
      const target = match[1].match(/\bTarget=["']([^"']+)["']/i)?.[1];
      const type = match[1].match(/\bType=["']([^"']+)["']/i)?.[1] || "";
      if (id && target && /\/image$/i.test(type)) relationships.set(id, target.replace(/^\.\//, ""));
    }
    return relationships;
  }

  function mediaAltText(paragraphXml, fallback) {
    const docPr = String(paragraphXml || "").match(/<(?:wp:docPr|pic:cNvPr)\b([^>]*)\/?\s*>/i)?.[1] || "";
    return decodeXml(docPr.match(/\b(?:descr|title|name)=["']([^"']+)["']/i)?.[1] || fallback || "Imagem da questão");
  }

  function mediaTag(media, altText) {
    if (!media || !media.resolved || !media.supported || !media.dataUrl) return "";
    const alt = `AABIMG:${media.hash}:${altText || media.name || "Imagem da questão"}`;
    return `<img src="${media.dataUrl}" alt="${escapeHtml(alt)}" data-aab-image="${media.hash}" data-aab-source="word" style="max-width:100%;height:auto">`;
  }

  function mediaReferences(xml, mediaMap, altText) {
    const references = [];
    const seen = new Set();
    const expression = /<(?:a:blip\b[^>]*(?:r:)?embed|v:imagedata\b[^>]*(?:r:)?id)=["']([^"']+)["'][^>]*\/?\s*>/gi;
    let match;
    while ((match = expression.exec(String(xml || ""))) !== null) {
      if (seen.has(match[1])) continue;
      seen.add(match[1]);
      const media = mediaMap instanceof Map ? mediaMap.get(match[1]) : null;
      references.push(media ? { ...media, relationshipId: match[1], alt: altText } : { relationshipId: match[1], alt: altText, resolved: false, supported: false, name: match[1], hash: hashValue(match[1]) });
    }
    return references;
  }

  function runToHtml(runXml) {
    const propertiesMatch = runXml.match(/<w:rPr\b[^>]*>([\s\S]*?)<\/w:rPr\s*>/i);
    const properties = propertiesMatch ? propertiesMatch[1] : "";
    const text = textFromFragment(runXml);
    if (!text) return "";
    let html = escapeHtml(text).replace(/\t/g, "&emsp;").replace(/\n/g, "<br>");
    const vertical = propertyValue(properties, "vertAlign") || "";
    if (vertical === "superscript") html = `<sup>${html}</sup>`;
    if (vertical === "subscript") html = `<sub>${html}</sub>`;
    if (propertyEnabled(properties, "u")) html = `<u>${html}</u>`;
    if (propertyEnabled(properties, "i")) html = `<em>${html}</em>`;
    if (propertyEnabled(properties, "b")) html = `<strong>${html}</strong>`;
    return html;
  }

  function formulaBlocks(xml) {
    const formulas = [];
    const expression = /<m:(oMathPara|oMath)\b[^>]*>([\s\S]*?)<\/m:\1\s*>/gi;
    let match;
    while ((match = expression.exec(String(xml || ""))) !== null) {
      formulas.push({ start: match.index, end: expression.lastIndex, ...formulaRecord(match[0]) });
    }
    return formulas;
  }

  function paragraphRichHtml(paragraphXml, mediaMap, formulas, media) {
    const segments = [];
    const formulaRanges = (formulas || []).map((entry) => [entry.start, entry.end]);
    const runExpression = /<w:r\b[^>]*>([\s\S]*?)<\/w:r\s*>/gi;
    let runMatch;
    while ((runMatch = runExpression.exec(paragraphXml)) !== null) {
      if (formulaRanges.some(([start, end]) => runMatch.index < end && runExpression.lastIndex > start)) continue;
      const runMedia = mediaReferences(runMatch[0], mediaMap, mediaAltText(paragraphXml));
      const images = runMedia.map((entry) => mediaTag(entry, entry.alt)).join("");
      segments.push({ start: runMatch.index, html: `${runToHtml(runMatch[1])}${images}` });
    }
    (formulas || []).forEach((entry) => segments.push({ start: entry.start, html: entry.html }));
    segments.sort((left, right) => left.start - right.start);
    let html = segments.map((entry) => entry.html).join("");
    if (!html) html = escapeHtml(textFromFragment(paragraphXml));
    const embedded = new Set((media || []).filter((entry) => entry.resolved).map((entry) => entry.hash));
    const alreadyShown = new Set(Array.from(html.matchAll(/data-aab-image=["']([^"']+)/gi)).map((entry) => entry[1]));
    embedded.forEach((hash) => {
      if (alreadyShown.has(hash)) return;
      const item = (media || []).find((entry) => entry.hash === hash);
      html += mediaTag(item, item.alt);
    });
    return html;
  }

  function paragraphMetadata(paragraphXml) {
    const propertiesMatch = paragraphXml.match(/<w:pPr\b[^>]*>([\s\S]*?)<\/w:pPr\s*>/i);
    const properties = propertiesMatch ? propertiesMatch[1] : "";
    return {
      style: propertyValue(properties, "pStyle") || "",
      numId: propertyValue(properties, "numId") || "",
      listLevel: Number(propertyValue(properties, "ilvl") || 0),
      pageBreakBefore: propertyEnabled(properties, "pageBreakBefore")
    };
  }

  function paragraphToRecords(paragraphXml, sourceIndex, mediaMap) {
    const runs = [];
    const runExpression = /<w:r\b[^>]*>([\s\S]*?)<\/w:r\s*>/gi;
    let runMatch;
    while ((runMatch = runExpression.exec(paragraphXml)) !== null) runs.push(runMatch[1]);
    const officeFormulas = formulaBlocks(paragraphXml);
    const formulaRanges = officeFormulas.map((entry) => [entry.start, entry.end]);
    const rawTextParts = [];
    const partExpression = /<w:r\b[^>]*>([\s\S]*?)<\/w:r\s*>/gi;
    let partMatch;
    while ((partMatch = partExpression.exec(paragraphXml)) !== null) {
      if (!formulaRanges.some(([start, end]) => partMatch.index < end && partExpression.lastIndex > start)) rawTextParts.push({ start: partMatch.index, text: textFromFragment(partMatch[1]) });
    }
    officeFormulas.forEach((entry) => rawTextParts.push({ start: entry.start, text: entry.plain }));
    rawTextParts.sort((left, right) => left.start - right.start);
    const rawText = rawTextParts.length ? rawTextParts.map((entry) => entry.text).join("") : textFromFragment(paragraphXml);
    const hasDrawing = /<(?:w:drawing|w:pict|a:blip)\b/i.test(paragraphXml);
    const altText = mediaAltText(paragraphXml, `Imagem do parágrafo ${sourceIndex}`);
    const media = mediaReferences(paragraphXml, mediaMap, altText);
    const latexFormulas=latexFormulaBlocks(rawText);
    let html = paragraphRichHtml(paragraphXml, mediaMap, officeFormulas, media);
    for(const formula of latexFormulas)html=html.replace(escapeHtml(formula.source),formula.html);
    const formulas=[...officeFormulas,...latexFormulas.filter(formula=>html.includes(`data-aab-formula="${formula.hash}"`))];
    const metadata = paragraphMetadata(paragraphXml);
    const plain = normalizeSpaces(rawText);
    return plain || hasDrawing || formulas.length ? [{ plain, html: html.trim(), hasDrawing, media, formulas, sourceIndex, lineIndex: 0, rawPlain: rawText, ...metadata }] : [];
  }

  // Slice text runs while reopening formatting tags. Embedded objects are never guessed across boundaries.
  function richTextSlice(html, start, end) {
    let position = 0, output = "", started = false; const stack = [];
    const begin = () => { if (!started) { output += stack.map(x => x.open).join(""); started = true; } };
    for (const token of String(html || "").match(/<[^>]+>|[^<]+/g) || []) {
      if (token[0] === "<") {
        const closing = token.match(/^<\/([a-z0-9]+)/i), opening = token.match(/^<([a-z0-9]+)/i);
        if (/^<br\b/i.test(token)) { if (position >= start && position < end) { begin(); output += token; } position++; }
        else if (closing) { if (started && stack.length) output += token; stack.pop(); }
        else if (opening && !/\/>$/.test(token)) { if (started) output += token; stack.push({name:opening[1],open:token}); }
      } else {
        const value = decodeXml(token.replace(/&emsp;/gi,"\t").replace(/&nbsp;/gi," "));
        const left = Math.max(0,start-position), right = Math.min(value.length,end-position);
        if (right > left) { begin(); output += escapeHtml(value.slice(left,right)); }
        position += value.length;
      }
      if (position >= end && started) break;
    }
    return output + (started ? stack.slice().reverse().map(x => `</${x.name}>`).join("") : "");
  }

  function expandStructuralRecords(record) {
    const raw = record.rawPlain ?? record.plain;
    const boundaries = new Set([0,raw.length]);
    // Legacy SmartFox exports distinguish the label using a bold run instead
    // of a colon. A complete, known label and a separate value are required.
    const boldPrefix = String(record.html || "").match(/^<strong>([^<]+)<\/strong>/i);
    const prefixText = boldPrefix ? decodeXml(boldPrefix[1]) : "";
    const formattedLabel = prefixText && !/[:–—-]\s*$/.test(prefixText) && Object.values(LABELS).some(re => prefixText.trim().match(re)?.[0].length === prefixText.trim().length)
      && raw.startsWith(prefixText) && raw.length > prefixText.length;
    if (formattedLabel) boundaries.add(prefixText.length);
    for (const m of raw.matchAll(/\n+/g)) { boundaries.add(m.index); boundaries.add(m.index+m[0].length); }
    // Only a complete, ordered option cycle justifies splitting labels inside prose.
    const markers = [...raw.matchAll(/(?:^|\s)(\([A-E]\)|[A-E][).])\s+/gi)];
    const letters = markers.map(m=>m[1].replace(/[^a-e]/gi,'').toUpperCase());
    const cycle = letters.join('').includes('ABCD');
    if (cycle) markers.forEach(m=>boundaries.add(m.index + (m[0][0].trim() ? 0 : 1)));
    if (/^(?:Objetivo|Quest[aã]o\s+\d+\b)/.test(raw) || /\|\s*N[ií]vel\s*:/.test(raw)) {
      for (const m of raw.matchAll(/(?:\s*[•|]\s*|\s+)(?=(?:Objetivo(?:\s+(?:do\s+plano\s+de\s+ensino|espec[ií]fico))?|N[ií]vel(?:\s+de\s+complexidade)?|Grau\s+de\s+dificuldade|Modelo\s+de\s+quest[aã]o|Tema|N[ií]vel\s+cognitivo|Multidisciplinaridade|Conte[uú]do\s+e\s+p[aá]gina\s+abordada|UA\s+que\s+a\s+quest[aã]o\s+foi\s+retirada)\s*:)/gi)) boundaries.add(m.index+m[0].length);
    }
    if (cycle || /^(?:Gabarito|Resposta\s+correta|Alternativa\s+correta)\b/i.test(raw)) {
      for (const m of raw.matchAll(/\s+(?=(?:Gabarito|Resposta\s+(?:correta|esperada)|Feedback(?:\s+pedag[oó]gico)?|Justificativa|Coment[aá]rio\s+da\s+resposta)\s*:)/gi)) boundaries.add(m.index+m[0].length);
    }
    if (cycle || /^(?:Enunciado|Contextualiza[cç][aã]o|Texto[- ]base|Comando|Pergunta)\s*:/i.test(raw)) {
      for (const m of raw.matchAll(/\s+(?=(?:Enunciado|Contextualiza[cç][aã]o|Comando(?: da quest[aã]o)?|Pergunta|Alternativas|Op[cç][oõ]es de resposta)\s*:)/gi)) boundaries.add(m.index+m[0].length);
    }
    if (boundaries.size === 2) return [record];
    if (record.media?.length || record.formulas?.length || record.hasDrawing) {
      // Preserve the original rich paragraph; require a correction only if it contains multiple structural fields.
      const structural = formattedLabel || cycle || /\n\s*(?:[A-E][).]|Gabarito\s*:|Feedback\s*:|Quest[aã]o\s+\d)/i.test(raw);
      return [{...record, segmentationWarning: structural ? 'Um parágrafo reúne campos e objetos incorporados; separe os campos no Word para preservar imagens e fórmulas.' : ''}];
    }
    const points = [...boundaries].sort((a,b)=>a-b), records = [];
    for (let i=0;i<points.length-1;i++) {
      const plain = normalizeSpaces(raw.slice(points[i],points[i+1])).replace(/\s*[•|]\s*$/, ""); if (!plain) continue;
      records.push({...record,plain,rawPlain:raw.slice(points[i],points[i+1]),html:richTextSlice(record.html,points[i],points[i+1]),lineIndex:i,listMarker:i===0?record.listMarker:undefined,numId:i===0?record.numId:''});
    }
    return records;
  }

  function documentParagraphs(xmlText, mediaMap) {
    const records = [];
    const expression = /<w:p\b[^>]*>([\s\S]*?)<\/w:p\s*>/gi;
    let match;
    let sourceIndex = 0;
    while ((match = expression.exec(xmlText)) !== null) {
      sourceIndex += 1;
      records.push(...paragraphToRecords(match[1], sourceIndex, mediaMap));
    }
    if (!records.length) throw new Error("O XML principal do DOCX não contém parágrafos reconhecíveis.");
    return records;
  }

  function alphaNumber(number, lower) {
    let value = Number(number || 1);
    let result = "";
    while (value > 0) {
      value -= 1;
      result = String.fromCharCode(65 + (value % 26)) + result;
      value = Math.floor(value / 26);
    }
    return lower ? result.toLowerCase() : result;
  }

  function parseNumbering(numberingXml) {
    if (!numberingXml) return new Map();
    const abstracts = new Map();
    const abstractExpression = /<w:abstractNum\b[^>]*w:abstractNumId=["'](\d+)["'][^>]*>([\s\S]*?)<\/w:abstractNum>/gi;
    let abstractMatch;
    while ((abstractMatch = abstractExpression.exec(numberingXml)) !== null) {
      const levels = new Map();
      const levelExpression = /<w:lvl\b[^>]*w:ilvl=["'](\d+)["'][^>]*>([\s\S]*?)<\/w:lvl>/gi;
      let levelMatch;
      while ((levelMatch = levelExpression.exec(abstractMatch[2])) !== null) {
        levels.set(Number(levelMatch[1]), {
          format: propertyValue(levelMatch[2], "numFmt") || "decimal",
          start: Number(propertyValue(levelMatch[2], "start") || 1),
          template: propertyValue(levelMatch[2], "lvlText") || "%1"
        });
      }
      abstracts.set(abstractMatch[1], levels);
    }
    const resolved = new Map();
    const numberExpression = /<w:num\b[^>]*w:numId=["'](\d+)["'][^>]*>([\s\S]*?)<\/w:num>/gi;
    let numberMatch;
    while ((numberMatch = numberExpression.exec(numberingXml)) !== null) {
      const abstractId = propertyValue(numberMatch[2], "abstractNumId");
      if (abstractId && abstracts.has(abstractId)) {
        const levels=new Map([...abstracts.get(abstractId)].map(([k,v])=>[k,{...v}]));
        for(const m of numberMatch[2].matchAll(/<w:lvlOverride\b[^>]*w:ilvl=["'](\d+)["'][^>]*>([\s\S]*?)<\/w:lvlOverride>/gi)){
          const start=propertyValue(m[2],"startOverride"); if(start && levels.has(Number(m[1]))) levels.get(Number(m[1])).start=Number(start);
        }
        resolved.set(numberMatch[1],levels);
      }
    }
    return resolved;
  }

  function decorateAutomaticLists(records, numberingXml) {
    const definitions = parseNumbering(numberingXml);
    const counters = new Map();
    records.forEach((record) => {
      if (!record.numId || !definitions.has(record.numId)) return;
      const definition = definitions.get(record.numId).get(record.listLevel);
      if (!definition) return;
      const key = `${record.numId}:${record.listLevel}`;
      const current = counters.has(key) ? counters.get(key) + 1 : definition.start;
      counters.set(key, current);
      if (definition.format === "upperLetter" || definition.format === "lowerLetter") record.listMarker = alphaNumber(current, definition.format === "lowerLetter");
      else if (definition.format === "decimal") record.listMarker = String(current);
    });
    return records;
  }

  function parseHeader(input) {
    const record = typeof input === "string" ? { plain: input, style: "" } : (input || {});
    const normalized = normalizeSpaces(record.plain);
    let match = normalized.match(/^Quest(?:ão|ao)\s*(?:n(?:[º°o]|\.)?\s*)?[\(\[]?\s*(\d+)\s*[\)\]]?/i);
    let boundaryKind = "explicit-question";
    let inlineBody = "";
    if (!match) {
      match = normalized.match(/^(?:Item|Pergunta)\s*(?:n(?:[º°o]|\.)?\s*)?[\(\[]?\s*(\d+)\s*[\)\]]?/i);
      boundaryKind = "explicit-item";
    }
    if (!match) {
      match = normalized.match(/^Q\s*[\-_.:]?\s*(\d+)\b/i);
      boundaryKind = "compact-q";
    }
    if (!match) {
      match = normalized.match(/^(\d+)\s*[\).:\-]\s*(?:Quest(?:ão|ao)|Pergunta|Item)\b/i);
      boundaryKind = "numbered-question";
    }
    if (!match) {
      const numeric = normalized.match(/^(\d{1,3})\s*[\).:\-]\s+(.{15,})$/);
      if (numeric && /(?:heading|t[ií]tulo|quest)/i.test(record.style || "")) {
        match = numeric;
        boundaryKind = "styled-number";
        inlineBody = numeric[2];
      }
    }
    if (!match) {
      match = normalized.match(/^(?:Estudo\s+de\s+Caso|Situa[cç][aã]o[- ]problema)\s*(\d+)\s*[:–-]?/i);
      if (match) boundaryKind = "explicit-case";
    }
    if (!match) return null;
    const tail = normalized.slice(match[0].length);
    if (!inlineBody && tail.trim().length > 35 && !/^\s*[_•|:(\[–—-]/.test(tail) && !/^\s*(?:Discursiva|Objetiva|N[ií]vel|Livro|Modelo|UA)\b/i.test(tail)) inlineBody = tail.trim();
    if (!inlineBody && /^\s*[:.\-–—]\s*\S/.test(tail) && !/^\s*[:.\-–—]\s*(?:Discursiva|Objetiva|N[ií]vel|Livro|Modelo)\b/i.test(tail)) inlineBody = tail.replace(/^\s*[:.\-–—]\s*/, "");
    const assessmentMatch = normalized.match(/_([A-Z0-9]+)_UA\b/i);
    const uaMatch = normalized.match(/_UA\s*[\(\[]\s*([^\)\]]+)\s*[\)\]]/i);
    const objectiveMatch = normalized.match(/_Obj(?:etivo)?\s*[\(\[]\s*([^\)\]]+)\s*[\)\]]/i);
    const difficultyMatch = normalized.match(/_Obj(?:etivo)?\s*[\(\[][^\)\]]+[\)\]]\s*_\s*([^_]+?)(?:_Discursiva)?$/i)
      || normalized.match(/(?:Dificuldade|N[ií]vel)\s*[:\-]?\s*(F[aá]cil|M[eé]di[oa]|Dif[ií]cil)\b/i);
    const athusFormat = Boolean(assessmentMatch || uaMatch || objectiveMatch);
    return {
      name: inlineBody ? normalized.slice(0, normalized.length - tail.length).trim() : normalized,
      number: Number(match[1]),
      assessment: assessmentMatch ? assessmentMatch[1].toUpperCase() : "",
      ua: uaMatch ? normalizeSpaces(uaMatch[1]) : "",
      objectiveNumber: objectiveMatch ? normalizeSpaces(objectiveMatch[1]) : "",
      difficulty: difficultyMatch ? normalizeSpaces(difficultyMatch[1]) : "",
      headerFormat: athusFormat ? "athus" : "generic",
      boundaryKind,
      questionFormat: boundaryKind === "explicit-case" ? "discursive" : undefined,
      boundaryConfidence: athusFormat ? 1 : boundaryKind === "styled-number" ? 0.76 : 0.94,
      inlineMedia: inlineBody ? record.media || [] : [], inlineFormulas: inlineBody ? record.formulas || [] : [], inlineDrawing: inlineBody && record.hasDrawing,
      inlineBody, inlineHtml: inlineBody ? stripVisiblePrefix(record.html || escapeHtml(normalized), normalized.length - inlineBody.length) : ""
    };
  }

  // A word that starts a sentence is not a field label. Labels must stand
  // alone or be followed by a delimiter; this protects "Objetivo principal..."
  // and "Resposta rápida..." when they are actual teaching content.
  const LABELS = Object.freeze({
    theme: /^Tema(?:\s+(?:Gerador|geral))?(?:\s*[:–—-]\s*|\s*$)/i,
    objective: /^Objetivo(?:\s+(?:de\s+aprendizagem|associado|espec[ií]fico|do\s+plano\s+de\s+ensino))?(?:\s*[:–—-]\s*|\s*$)/i,
    type: /^(?:Tipo|Modelo|Formato)\s+(?:da|de)\s+quest[aã]o(?:\s*[:–—-]\s*|\s*$)/i,
    difficulty: /^(?:Dificuldade|Grau\s+de\s+dificuldade|N[ií]vel\s+de\s+(?:dificuldade|complexidade))(?:\s*[:–—-]\s*|\s*$)/i,
    body: /^(?:Enunciado|Contextualiza[cç][aã]o|Texto[- ]base|Situa[cç][aã]o[- ]problema|Texto\s+(?:da\s+)?Quest[aã]o|Comando(?:\s+da\s+quest[aã]o)?|Pergunta|Quest[aã]o)(?:\s*[:–—-]\s*|\s*$)/i,
    answer: /^(?:Gabarito(?:\s+discursivo)?|Padr[aã]o\s+de\s+resposta(?:\s+esperad[oa])?|Resposta\s+(?:esperada|correta)|Alternativa\s+correta|Resposta)(?:\s*[:–—-]\s*|\s*$|\s+(?=[A-E](?:\s*$|[).])))/i,
    feedback: /^(?:Feedback(?:\s+pedag[oó]gico)?|Justificativa|Coment[aá]rio(?:\s+pedag[oó]gico)?|Resposta\s+comentada|Coment[aá]rio\s+da\s+resposta)(?:\s*[:–—-]\s*|\s*$)/i,
    references: /^Refer[eê]ncias?(?:\s+bibliogr[aá]ficas?)?(?:\s*[:–—-]\s*|\s*$)/i,
    administrative: /^(?:N[ií]vel(?: cognitivo)?|Multidisciplinaridade|Conte[uú]do e p[aá]gina abordada|UA(?: que a quest[aã]o foi retirada)?|Identifica[cç][aã]o(?: da quest[aã]o)?|C[oó]digo(?: da quest[aã]o)?|Disciplina|Professor(?:a)?|Turma|Valor(?: da quest[aã]o)?|Pontua[cç][aã]o|Observa[cç][oõ]es(?: (?:do|para o) professor)?)(?:\s*[:–—-]\s*|\s*$)/i,
    options: /^(?:Alternativas|Op[cç][oõ]es(?: de resposta)?)(?:\s*:\s*|\s*$)/i,
    section: /^(?:Quest[oõ]es\s+(?:F[aá]ceis|M[eé]dias|Dif[ií]ceis|Objetivas|Discursivas)|P[aá]gina\s+\d+(?:\s+de\s+\d+)?|Fim\s+da\s+(?:prova|avalia[cç][aã]o))\s*[.:]?$/i
  });

  function stripVisiblePrefix(html, characterCount) {
    let remaining = Math.max(0, Number(characterCount || 0));
    if (!remaining) return String(html || "");
    return String(html || "").replace(/(^|>)([^<]+)/g, (_match, boundary, encoded) => {
      if (!remaining) return `${boundary}${encoded}`;
      const decoded = decodeXml(encoded.replace(/&emsp;/gi, "\t").replace(/&nbsp;/gi, " "));
      if (decoded.length <= remaining) {
        remaining -= decoded.length;
        return boundary;
      }
      const kept = decoded.slice(remaining);
      remaining = 0;
      return `${boundary}${escapeHtml(kept).replace(/\t/g, "&emsp;")}`;
    });
  }

  function alternativeRecord(record) {
    const plain = normalizeSpaces(record && record.plain);
    let match = plain.match(/^(?:(?:Alternativa|Op(?:ç|c)[aã]o|Resposta)\s+)?[\(\[]?([A-E])\s*[\)\]\.:\-]\s*(.*)$/i);
    if (!match) match = plain.match(/^([A-E])$/i);
    const automaticMarker = !match && /^[A-E]$/i.test(record && record.listMarker || "");
    if (automaticMarker) match = [plain, String(record.listMarker).toUpperCase(), plain];
    if (!match) return null;
    const letter = match[1].toUpperCase();
    const answer = normalizeSpaces(match[2] || "");
    const prefixLength = automaticMarker ? 0 : Math.max(0, plain.length - answer.length);
    return {
      letter,
      plain: answer,
      html: stripVisiblePrefix(record?.html || escapeHtml(plain), prefixLength),
      hasDrawing: Boolean(record && record.hasDrawing),
      media: Array.isArray(record?.media) ? record.media : [],
      formulas: Array.isArray(record?.formulas) ? record.formulas : [],
      sourceIndex: record && record.sourceIndex
    };
  }

  function isKnownLabel(record) {
    return Object.values(LABELS).some((expression) => expression.test(record.plain));
  }

  function removeLabel(record, expression) {
    const match = String(record.plain || "").match(expression);
    const plain = normalizeSpaces(String(record.plain || "").replace(expression, ""));
    return { ...record, plain, html: stripVisiblePrefix(record.html || escapeHtml(record.plain), match ? match[0].length : 0) };
  }

  function extractField(records, expression) {
    const index = records.findIndex((record) => expression.test(record.plain));
    if (index < 0) return { value: "", indexes: [], index: -1 };
    const stripped = removeLabel(records[index], expression).plain;
    if (stripped) return { value: stripped, indexes: [index], index };
    for (let next = index + 1; next < records.length; next += 1) {
      if (!records[next].plain) continue;
      if (isKnownLabel(records[next]) || alternativeRecord(records[next]) || parseHeader(records[next])) break;
      return { value: records[next].plain, indexes: [index, next], index };
    }
    return { value: "", indexes: [index], index };
  }

  function directType(description) {
    const value = normalizeForMatch(description);
    const rules = [
      { id: "158", expressions: [/questao\s+discursiva/, /discursiva/, /dissertativa/, /resposta\s+aberta/] },
      { id: "60", expressions: [/complementacao/, /completar\s+lacuna/, /preenchimento\s+de\s+lacuna/] },
      { id: "62", expressions: [/resposta\s+multipla/, /multiplas\s+afirmativas/, /afirmativas\s+(?:i|1)/] },
      { id: "63", expressions: [/assercao\s+e\s+razao/, /asser[cç][aã]o.*raz[aã]o/] },
      { id: "64", expressions: [/interpretacao/, /interpretativa/] },
      { id: "65", expressions: [/outro\s+tipo/, /objetiva/, /multipla\s+escolha/, /resposta\s+unica/, /escolha\s+unica/] }
    ];
    const rule = rules.find((candidate) => candidate.expressions.some((expression) => expression.test(value)));
    return rule ? TYPE_CATALOG.find((type) => type.id === rule.id) : null;
  }

  function classifyQuestionType(description, bodyText, alternatives) {
    const explicit = directType(description);
    if (explicit) {
      return {
        id: explicit.id, key: explicit.key, label: explicit.label, modelLabel: explicit.shortLabel,
        inferred: false, confidence: 1,
        evidence: [`O Word informou “${normalizeSpaces(description)}”.`],
        candidates: [{ id: explicit.id, label: explicit.label, score: 1, evidence: "Tipo declarado no arquivo" }]
      };
    }

    const body = normalizeForMatch(bodyText);
    const options = normalizeForMatch((alternatives || []).map((item) => item.plain || item).join(" | "));
    const scores = new Map(TYPE_CATALOG.map((type) => [type.id, { type, score: type.id === "65" ? 0.34 : 0.08, evidence: [] }]));
    const add = (id, amount, evidence) => {
      const entry = scores.get(id);
      entry.score += amount;
      if (evidence && !entry.evidence.includes(evidence)) entry.evidence.push(evidence);
    };

    const romanStatements = (body.match(/(?:^|[\s;])(?:i|ii|iii|iv|v)\s*[\.\-\)]/g) || []).length;
    const assertionSignals = [/(?:as\s+)?assercoes?/, /porque/, /razao/, /a\s+segunda.*justifica.*primeira/].filter((expression) => expression.test(body)).length;
    const completionSignals = [/_\s*_+/, /\blacuna\b/, /\bcomplete\b/, /\bpreencha\b/, /assinale.*completa/].filter((expression) => expression.test(body)).length;
    const interpretationSignals = [/com\s+base\s+(?:no|na|nos|nas)\s+(?:texto|excerto|caso|situacao)/, /leia\s+(?:o|a)\s+(?:texto|trecho|situacao)/, /de\s+acordo\s+com\s+(?:o|a)\s+(?:texto|passagem)/, /texto[-\s]base/, /analise\s+o\s+caso/].filter((expression) => expression.test(body)).length;
    const combinationOptions = (options.match(/\b(?:i|ii|iii|iv)(?:\s*,\s*|\s+e\s+)(?:i|ii|iii|iv)\b/g) || []).length;

    if (assertionSignals >= 2) add("63", 0.74, "Foram reconhecidas duas asserções ligadas por razão/justificativa.");
    else if (assertionSignals === 1) add("63", 0.24, "Há vocabulário típico de asserção e razão.");
    if (romanStatements >= 2) add("62", 0.62, `${romanStatements} afirmativas numeradas em algarismos romanos.`);
    if (combinationOptions >= 1) add("62", 0.23, "As alternativas combinam afirmativas I, II, III ou IV.");
    if (/esta\s+correto\s+o\s+que\s+se\s+afirma/.test(body)) add("62", 0.28, "Comando típico de resposta múltipla.");
    if (completionSignals >= 1) add("60", 0.66 + Math.min(0.16, (completionSignals - 1) * 0.08), "O enunciado pede completar/preencher uma lacuna.");
    if (interpretationSignals >= 1) add("64", 0.58 + Math.min(0.18, (interpretationSignals - 1) * 0.09), "Há texto, caso ou situação-base a ser interpretada.");
    if (/\b(?:qual|assinale|selecione|indique)\b/.test(body)) add("65", 0.18, "Comando padrão de escolha única.");

    const ranked = Array.from(scores.values()).sort((left, right) => right.score - left.score);
    const winner = ranked[0];
    const runnerUp = ranked[1];
    const margin = Math.max(0, winner.score - runnerUp.score);
    const confidence = Math.max(0.46, Math.min(0.97, 0.56 + margin * 0.46 + Math.min(0.18, winner.evidence.length * 0.06)));
    return {
      id: winner.type.id, key: winner.type.key, label: winner.type.label, modelLabel: winner.type.shortLabel,
      inferred: true, confidence: Math.round(confidence * 100) / 100,
      evidence: winner.evidence.length ? winner.evidence : ["Não apareceu um padrão especial; classificada como escolha única."],
      candidates: ranked.slice(0, 3).map((entry) => ({
        id: entry.type.id, label: entry.type.label, score: Math.round(Math.min(1, entry.score) * 100) / 100,
        evidence: entry.evidence[0] || "Compatibilidade geral"
      }))
    };
  }

  function cognitiveFromObjective(objective, difficulty, bodyText) {
    const value = normalizeForMatch(objective || bodyText);
    const words = value.replace(/^(?:o\s+aluno\s+devera|ser\s+capaz\s+de)\s+/, "").split(/\s+/);
    const candidates = COGNITIVE_CATALOG.map((level) => {
      const matches = level.verbs.filter((verb) => words.includes(verb) || value.includes(`${verb} `));
      const firstPosition = matches.length ? Math.min(...matches.map((verb) => words.indexOf(verb)).filter((index) => index >= 0)) : Number.MAX_SAFE_INTEGER;
      return { ...level, matches, firstPosition, score: matches.length ? 0.88 + Math.min(0.1, (matches.length - 1) * 0.05) : 0 };
    }).sort((left, right) => left.firstPosition - right.firstPosition || right.score - left.score);
    if (candidates[0].score) {
      return {
        id: candidates[0].id, label: candidates[0].label, inferredFrom: candidates[0].matches[0],
        confidence: Math.min(1, candidates[0].score), evidence: `Verbo cognitivo reconhecido: ${candidates[0].matches.join(", ")}.`
      };
    }
    const level = normalizeForMatch(difficulty);
    if (level.includes("dificil")) return { id: "223", label: "Análise", inferredFrom: "dificuldade", confidence: 0.78, evidence: "Estimado pela dificuldade informada." };
    if (level.includes("medio") || level.includes("media")) return { id: "224", label: "Aplicação", inferredFrom: "dificuldade", confidence: 0.74, evidence: "Estimado pela dificuldade informada." };
    return { id: "229", label: "Compreensão", inferredFrom: "padrão", confidence: 0.64, evidence: "Estimativa padrão por ausência de verbo explícito." };
  }

  function paragraphBlock(records) {
    return records.filter((record) => record.plain || record.hasDrawing).map((record) => `<p>${record.html || escapeHtml(record.plain)}</p>`).join("");
  }

  function attributesFromHtml(html, attribute) {
    const expression = new RegExp(`${attribute}=["']([^"']+)["']`, "gi");
    return Array.from(String(html || "").matchAll(expression)).map((entry) => entry[1]).sort();
  }

  function specialCharacterInventory(text) {
    const counts = new Map();
    for (const character of String(text || "").normalize("NFC")) {
      const codePoint = character.codePointAt(0);
      if (codePoint < 0x80 || /\s/.test(character)) continue;
      const key = `${character} (U+${codePoint.toString(16).toUpperCase().padStart(4, "0")})`;
      counts.set(key, (counts.get(key) || 0) + 1);
    }
    return Array.from(counts.entries()).sort(([left], [right]) => left.localeCompare(right)).map(([character, count]) => ({ character, count }));
  }

  function semanticScripts(html) {
    const result = [];
    const expression = /<(sup|sub)\b[^>]*>([\s\S]*?)<\/\1\s*>/gi;
    let match;
    while ((match = expression.exec(String(html || ""))) !== null) result.push(`${match[1].toLowerCase()}:${normalizeSpaces(decodeXml(match[2].replace(/<[^>]+>/g, " ")))}`);
    return result.sort();
  }

  function richFieldIntegrity(html, text) {
    const value = String(html || "");
    return {
      images: attributesFromHtml(value, "data-aab-image"),
      formulas: attributesFromHtml(value, "data-aab-formula"),
      scripts: semanticScripts(value),
      specialCharacters: specialCharacterInventory(text)
    };
  }

  function computeRichIntegrity(question) {
    const fields = {
      body: richFieldIntegrity(question.bodyHtml, question.bodyText),
      expectedResponse: richFieldIntegrity(question.expectedResponseHtml, question.expectedResponseText),
      feedback: richFieldIntegrity(question.feedbackHtml, question.feedbackText)
    };
    (question.alternatives || []).forEach((alternative) => {
      fields[`alternative${alternative.letter}`] = richFieldIntegrity(alternative.html, alternative.plain);
    });
    const all = Object.values(fields);
    const integrity = {
      fields,
      imageHashes: Array.from(new Set(all.flatMap((field) => field.images))).sort(),
      formulaHashes: Array.from(new Set(all.flatMap((field) => field.formulas))).sort(),
      specialCharacterCount: all.reduce((total, field) => total + field.specialCharacters.reduce((sum, entry) => sum + entry.count, 0), 0),
      scriptCount: all.reduce((total, field) => total + field.scripts.length, 0)
    };
    integrity.signature = hashValue(JSON.stringify(integrity.fields));
    return integrity;
  }

  function suspiciousCharacterInventory(question) {
    const text = [
      question?.name,
      question?.bodyText,
      ...(question?.alternatives || []).map((item) => item.plain),
      question?.expectedResponseText,
      question?.feedbackText
    ].join("\n");
    const suspicious = new Map();
    for (const character of text) {
      const codePoint = character.codePointAt(0);
      const invisible = [0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF].includes(codePoint) || (codePoint >= 0x202A && codePoint <= 0x202E) || (codePoint >= 0x2066 && codePoint <= 0x2069);
      const replacement = codePoint === 0xFFFD || codePoint === 0xFFFC;
      const privateUse = (codePoint >= 0xE000 && codePoint <= 0xF8FF) || (codePoint >= 0xF0000 && codePoint <= 0xFFFFD) || (codePoint >= 0x100000 && codePoint <= 0x10FFFD);
      if (!invisible && !replacement && !privateUse) continue;
      const key = `U+${codePoint.toString(16).toUpperCase().padStart(4, "0")}`;
      suspicious.set(key, (suspicious.get(key) || 0) + 1);
    }
    return Array.from(suspicious.entries()).map(([codePoint, count]) => ({ codePoint, count }));
  }

  function stemToken(token) {
    return String(token || "")
      .replace(/(?:amentos?|imentos?|idades?|mente|ções|cao|sões|sao)$/i, "")
      .replace(/(?:icas?|icos?|ais|eis|os|as|es|s)$/i, "")
      .slice(0, 18);
  }

  function subjectTokens(value) {
    return Array.from(new Set(normalizeForMatch(value)
      .replace(/[^a-z0-9]+/g, " ")
      .split(/\s+/)
      .map(stemToken)
      .filter((token) => token.length >= 3 && !SUBJECT_STOPWORDS.has(token))));
  }

  function subjectHintFromFileName(fileName) {
    return normalizeSpaces(String(fileName || "")
      .replace(/\.docx$/i, "")
      .replace(/\([^)]*\)\s*$/g, "")
      .replace(/[_\-.]+/g, " ")
      .replace(/\b(?:AD|AP|P\d+|AV\d+|PROJETO[_\s-]*ATHUS|20\d{2}|\d+)\b/gi, " ")
    );
  }

  function assessAllocation(question, disciplines, fileSubjectHint) {
    const rows = (Array.isArray(disciplines) ? disciplines : []).map((label) => String(label || "").trim()).filter(Boolean);
    const hint = normalizeSpaces(fileSubjectHint || question?.subjectHint || "");
    const contentTokens = subjectTokens([question?.bodyText || normalizeSpaces(String(question?.bodyHtml || "").replace(/<[^>]*>/g," ")), ...(question?.alternatives || []).map(item => item.plain || normalizeSpaces(String(item.html || "").replace(/<[^>]*>/g," ")))].join(" "));
    const scope = "statement-and-alternatives";
    if (!rows.length) return {status:"unknown",score:0,selectedDiscipline:"",subjectHint:hint,contentScope:scope,reason:"Nenhuma disciplina está disponível para comparação.",matchedTerms:[],missingTerms:[]};
    const candidates = rows.map(label => {
      const terms = subjectTokens(label);
      const matches = terms.filter(t => contentTokens.some(c => c === t || (c.length >= 5 && t.length >= 5 && (c.startsWith(t) || t.startsWith(c)))));
      return {label, terms, matches, score:terms.length ? matches.length/terms.length : 0};
    }).sort((a,b)=>b.score-a.score);
    const best=candidates[0], tied=candidates[1] && best.score-candidates[1].score < 0.15;
    const status = best.score >= 0.65 && !tied ? "match" : best.score > 0 ? "review" : "inconsistent";
    return {status,score:Math.round(best.score*100),selectedDiscipline:best.label,subjectHint:hint,contentScope:scope,
      reason:status === "match" ? `Enunciado e alternativas compartilham termos com “${best.label}”. Confirme a pertinência na revisão.` : tied && best.score > 0 ? "O conteúdo combina com mais de uma disciplina; confirme a alocação." : "Enunciado e alternativas não permitem confirmar a disciplina apenas por termos; revise a alocação.",
      matchedTerms:best.matches,missingTerms:best.terms.filter(t=>!best.matches.includes(t)),
      candidates:candidates.slice(0,3).map(c=>({label:c.label,score:Math.round(c.score*100)}))};
  }

  function delimiterBalance(text, opening, closing) {
    let balance = 0;
    for (const character of String(text || "")) {
      if (character === opening) balance += 1;
      if (character === closing) balance -= 1;
      if (balance < 0) return false;
    }
    return balance === 0;
  }

  function textualAudit(question) {
    const checks = [];
    const add = (id, status, label, message, overridable) => checks.push({ id, status, label, message, overridable: overridable !== false });
    const body = normalizeSpaces(question.bodyText);
    const feedback = normalizeSpaces(question.feedbackText);
    const expectedResponse = normalizeSpaces(question.expectedResponseText);
    const combined = [body, expectedResponse, feedback, ...(question.alternatives || []).map((item) => item.plain)].join(" ");
    const wordCount = (value) => normalizeSpaces(value).split(/\s+/).filter(Boolean).length;
    const incompleteEnding = /\b(?:a|ao|aos|as|com|como|da|das|de|do|dos|e|em|entre|ou|para|por|que|se|sem|um|uma)$/i;

    add("body-length", wordCount(body) >= 12 ? "pass" : "blocking", "Enunciado completo",
      wordCount(body) >= 12 ? "O enunciado possui extensão suficiente." : "O enunciado é curto e pode ter sido recortado.");
    add("feedback-length", wordCount(feedback) >= 8 ? "pass" : "blocking", "Feedback completo",
      wordCount(feedback) >= 8 ? "O feedback possui uma explicação mínima." : "O feedback é curto para explicar o gabarito.");
    const straightQuotes = (combined.match(/"/g) || []).length;
    const curlyQuotesBalanced = (combined.match(/“/g) || []).length === (combined.match(/”/g) || []).length;
    const balanced = [["(", ")"], ["[", "]"], ["{", "}"]].every(([opening, closing]) => delimiterBalance(combined, opening, closing)) && straightQuotes % 2 === 0 && curlyQuotesBalanced;
    add("delimiters", balanced ? "pass" : "blocking", "Parênteses, colchetes e aspas", balanced ? "Os delimitadores estão equilibrados." : "Há delimitador ou aspas sem fechamento.");
    const hasPlaceholder = /\b(?:XXX+|TBD|TODO)\b/.test(combined)
      || /\b(?:(?:inserir|insira|preencher|preencha)\s+aqui|texto\s+aqui)\b|\{\{[^}]+\}\}|\[[^\]]*(?:inserir|preencher)[^\]]*\]/i.test(combined);
    add("placeholders", hasPlaceholder ? "blocking" : "pass", "Campos pendentes", hasPlaceholder ? "Foi encontrado um marcador que parece não ter sido substituído." : "Nenhum marcador pendente foi localizado.");
    const truncated = /(?:\.{3,}|…)$/.test(body) || incompleteEnding.test(body) || incompleteEnding.test(feedback);
    add("truncation", truncated ? "blocking" : "pass", "Sinais de truncamento", truncated ? "O enunciado ou o feedback termina de forma possivelmente incompleta." : "Não há sinal objetivo de corte no final do texto.");
    const completionStem = String(question.typeId) === "60" && /(?:^|\s)(?:e|sao|corresponde\s+a|denomina-se)$/i.test(normalizeForMatch(body));
    const hasInstruction = completionStem || /\b(?:assinale|identifique|analise|avalie|julgue|selecione|indique|calcule|determine|considere|complete|apresente|corresponde|representa|expressa|qual|quais|correta|incorreta|compat[ií]vel)\b/i.test(body);
    add("instruction", hasInstruction ? "pass" : "advisory", "Comando da questão", hasInstruction ? "Foi identificado um comando de resposta." : "Não foi identificado um comando explícito; confira a clareza.");
    const bodyEndsClearly = completionStem || /[.?!:;\)\]”’\"]$/.test(body);
    add("body-ending", bodyEndsClearly ? "pass" : "advisory", "Final do enunciado", bodyEndsClearly ? "O enunciado possui encerramento reconhecível." : "O enunciado termina sem pontuação.");
    const alternatives = question.alternatives || [];
    const discursive = question.questionFormat === "discursive";
    const contentKey = (item) => normalizeForMatch(item.plain) || attributesFromHtml(item.html, "data-aab-image").join("|") || attributesFromHtml(item.html, "data-aab-formula").join("|");
    const unique = new Set(alternatives.map(contentKey)).size === alternatives.length;
    const complete = alternatives.length === REQUIRED_ALTERNATIVES && alternatives.every((item) => Boolean(contentKey(item))) && unique;
    add("alternatives", discursive || complete ? "pass" : "blocking", discursive ? "Estrutura discursiva" : "Alternativas A–D", discursive ? "A questão foi reconhecida como discursiva e não exige alternativas." : complete ? "As quatro alternativas têm texto e são distintas." : "As alternativas estão vazias, repetidas ou fora do conjunto A–D.", false);
    const explained = discursive ? wordCount(expectedResponse) >= 8 : Number(question.correctIndex) >= 0 && wordCount(feedback) >= 8;
    add("answer-explanation", explained ? "pass" : "blocking", discursive ? "Resposta esperada explicada" : "Gabarito explicado", explained ? (discursive ? "A questão possui um padrão de resposta suficientemente explicado." : `O gabarito ${question.correctLetter} possui feedback associado.`) : (discursive ? "Não foi localizado um padrão de resposta suficientemente explicado." : "Não foi possível associar uma explicação ao gabarito."), false);
    const blocking = checks.filter((check) => check.status === "blocking");
    const advisory = checks.filter((check) => check.status === "advisory");
    const passed = checks.filter((check) => check.status === "pass").length;
    return { checks, blocking, advisory, score: Math.round((passed / checks.length) * 100), ready: blocking.length === 0 };
  }

  function technicalErrors(question) {
    return technicalIssues(question).map((issue) => issue.message);
  }

  function optionSourceArtifact(value) {
    const text = normalizeSpaces(value);
    if (!text) return "";
    if (/(?:https?:\/\/|www\.|\/\/\s*[a-z0-9.-]+\.[a-z]{2,}|\bdoi\s*:|10\.\d{4,9}\/[\w.()/:;-]+)/i.test(text)) return "URL ou DOI";
    if (/^(?:fonte|refer[eê]ncia(?:s)?|bibliografia)\s*[:\-]/i.test(text)) return "rótulo de fonte ou referência";
    if (/\b(?:isbn|issn)\s*[:\-]?\s*[\dXx-]{8,}\b/i.test(text)) return "ISBN ou ISSN";
    if (/\b[A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇ]{2,},\s*(?:[A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇ](?:\.|\b)\s*){1,4}(?:\([^)]*(?:19|20)\d{2}[^)]*\)|[.;]\s*(?:19|20)\d{2})/u.test(text)) return "registro bibliográfico de autoria";
    if (/\b(?:v\.|vol\.|n\.|ed\.|pp?\.)\s*\d+[\s,.;]*(?:19|20)\d{2}\b/i.test(text)) return "dados de volume, edição ou página";
    return "";
  }

  function detectQuestionFormat(question) {
    if (["objective","discursive"].includes(question?.questionFormat)) return question.questionFormat;
    const declared = normalizeForMatch(`${question?.questionFormat || ""} ${question?.typeDescription || ""} ${question?.name || ""}`).replace(/_/g, " ");
    if (/\b(?:discursiv[ao]s?|dissertativ[ao]s?|resposta aberta|questao aberta)\b/.test(declared)) return "discursive";
    if (!(question?.alternatives || []).length && normalizeSpaces(question?.expectedResponseText || question?.expectedResponseHtml)) return "discursive";
    return "objective";
  }

  function forbiddenAlternative(value) {
    const text = normalizeForMatch(value).replace(/[^a-z0-9 ]+/g, " ").replace(/\s+/g, " ").trim();
    return /^(?:nra|nenhuma das anteriores|nenhuma das alternativas|todas (?:as )?(?:alternativas|respostas)? ?(?:estao )?(?:corretas|erradas)|todas estao corretas|todas estao erradas)$/.test(text);
  }

  function estimatedVisualLines(value) {
    const text = normalizeSpaces(value);
    if (!text) return 0;
    const explicit = String(value || "").split(/\n+/).filter((line) => normalizeSpaces(line)).length;
    return Math.max(explicit, Math.ceil(text.length / 88));
  }

  function athusQuestionRuleIssues(question) {
    const issues = [];
    const add = (code, field, title, message, impact, action, severity) => issues.push({
      code, field, title, message, impact, action, severity: severity || "review", category: "rules", overridable: true
    });
    const visible = [question.bodyText, ...(question.alternatives || []).map((item) => item.plain), question.expectedResponseText, question.feedbackText].join(" ");
    const normalized = normalizeForMatch(visible);
    const format = question.questionFormat || detectQuestionFormat(question);
    if (question.headerFormat !== "athus" || !question.assessment || !question.ua || !question.objectiveNumber || !question.difficulty) add(
      "ATHUS.IDENTIFICACAO_INCOMPLETA", "Identificação", "Identificação fora do padrão Athus",
      "A identificação deve informar número, avaliação, UA, objetivo e dificuldade.",
      "A rastreabilidade entre conteúdo, objetivo e questão fica incompleta.",
      "Use o formato ‘Questão (x)_AVALIAÇÃO_UA (x)_Obj (x)_nível’."
    );
    if (!normalizeSpaces(question.theme)) add(
      "ATHUS.TEMA_GERADOR_AUSENTE", "Tema Gerador", "Tema Gerador ausente",
      "A questão não declara a disciplina ou o eixo temático.", "O vínculo pedagógico fica incompleto.",
      "Inclua ‘Tema Gerador: [disciplina ou eixo]’ no bloco da questão."
    );
    if (!normalizeSpaces(question.objective)) add(
      "ATHUS.OBJETIVO_ASSOCIADO_AUSENTE", "Objetivo associado", "Objetivo associado ausente",
      "Não foi localizado o objetivo de aprendizagem que a questão mede.", "Não é possível auditar plenamente conteúdo → objetivo → habilidade.",
      "Inclua um objetivo observável e coerente com o comando."
    );
    if (!normalizeSpaces(question.typeDescription)) add(
      "ATHUS.HABILIDADE_NAO_DECLARADA", "Tipo de questão", "Habilidade avaliada não declarada",
      `O modelo técnico foi autodetectado como ${question.typeLabel || "não definido"}, mas o tipo pedagógico não foi informado.`,
      "A habilidade mobilizada fica menos rastreável.", "Informe, por exemplo, diagnóstico aplicado, tomada de decisão ou análise comparativa.", "warning"
    );
    const difficulty = normalizeForMatch(question.difficulty);
    if (question.difficulty && !/(?:facil|medio|media|dificil)/.test(difficulty)) add(
      "ATHUS.DIFICULDADE_INVALIDA", "Dificuldade", "Dificuldade não reconhecida",
      `Valor encontrado: “${normalizeSpaces(question.difficulty)}”.`, "A distribuição 40/40/20 não pode ser conferida.",
      "Use Fácil, Médio ou Difícil."
    );
    const bodyLines = estimatedVisualLines(question.bodyText);
    if (format === "objective" && (bodyLines < 10 || bodyLines > 15)) add(
      "ATHUS.ENUNCIADO_FORA_DA_FAIXA", "Enunciado", "Extensão do enunciado fora do padrão",
      `A estimativa é de ${bodyLines} linha(s); o padrão objetivo prevê de 10 a 15.`,
      "Um texto curto pode não contextualizar; um texto longo pode criar dificuldade artificial.",
      "Revise a contextualização. A contagem é estimada pelo texto, pois a quebra visual varia conforme o Word."
    );
    if (format === "discursive" && bodyLines > 15) add(
      "ATHUS.DISCURSIVA_LONGA", "Enunciado", "Discursiva acima do limite recomendado",
      `A estimativa é de ${bodyLines} linha(s); a P1 prevê até 15.`, "O comando pode ficar excessivamente longo.",
      "Resuma a contextualização sem remover os dados necessários."
    );
    const feedbackLines = estimatedVisualLines(question.feedbackText);
    if (question.feedbackText && feedbackLines > 6) add(
      "ATHUS.FEEDBACK_LONGO", "Feedback pedagógico", "Feedback acima do padrão",
      `A estimativa é de ${feedbackLines} linha(s); o padrão prevê de 1 a 6.`, "A correção pode ficar excessivamente extensa.",
      "Resuma a justificativa, mantendo conceito, aplicação e razão do gabarito.", "warning"
    );
    if (/\b(?:material estudado|conteudo estudado|conforme o material|de acordo com o arquivo|segundo o pdf|na ua enviada|conforme o documento)\b/.test(normalized)) add(
      "ATHUS.REFERENCIA_A_FONTE_INTERNA", "Texto da questão", "Referência proibida ao material interno",
      "O texto menciona arquivo, PDF, UA enviada ou material estudado.", "A questão deixa de ser autônoma para o estudante.",
      "Reescreva o trecho apresentando diretamente o contexto ou conceito, sem mencionar a fonte interna."
    );
    const body = normalizeSpaces(question.bodyText);
    const commandRaw = body.match(/(?:^|[.!])\s*([^.!?]{5,260}\?)\s*$/)?.[1] || body.slice(-260);
    const command = normalizeForMatch(commandRaw);
    const doubleNegative = /\bnao\b[^?.!]{0,140}\b(?:nao|incorreta|exceto|falsa)\b/.test(command)
      || /\b(?:incorreta|exceto|falsa)\b[^?.!]{0,140}\bnao\b/.test(command);
    if (doubleNegative) add(
      "ATHUS.DUPLA_NEGACAO", "Comando", "Possível dupla negação",
      "O comando reúne dois ou mais marcadores negativos.", "A dificuldade pode decorrer da redação, não do raciocínio.",
      "Reescreva o comando de modo afirmativo e direto."
    );
    const alternatives = question.alternatives || [];
    if (format === "objective" && alternatives.length === REQUIRED_ALTERNATIVES) {
      const lengths = alternatives.map((item) => normalizeSpaces(item.plain).split(/\s+/).filter(Boolean).length).filter(Boolean);
      const shortest = Math.min(...lengths);
      const longest = Math.max(...lengths);
      if (lengths.length === REQUIRED_ALTERNATIVES && longest >= shortest * 2.25 && longest - shortest >= 10) add(
        "ATHUS.ALTERNATIVAS_DESEQUILIBRADAS", "Alternativas", "Alternativas com extensões muito diferentes",
        `A menor opção tem ${shortest} palavra(s) e a maior, ${longest}.`, "O tamanho pode oferecer pista involuntária sobre o gabarito.",
        "Aproxime a extensão e a estrutura gramatical das quatro alternativas.", "warning"
      );
    }
    return issues;
  }

  function technicalIssues(question) {
    const errors = [];
    const add = (code, field, message, impact, action, details) => errors.push({
      code, severity: "blocking", category: "structure", field, message, impact, action, overridable: false, ...(details || {})
    });
    for (const warning of question.segmentationWarnings || []) add(
      "ARQUIVO.SEPARACAO_AMBIGUA", "Separação dos campos", warning,
      "O conteúdo original foi preservado, mas não é seguro distribuir este parágrafo automaticamente.", "Separe identificação, enunciado e alternativas em parágrafos distintos no Word e importe novamente."
    );
    if (!normalizeSpaces(question.name)) add(
      "ARQUIVO.IDENTIFICACAO_AUSENTE", "Identificação", "A identificação da questão está ausente.",
      "O AvaliA exige esse campo e não permitirá salvar a questão.", "Preencha a identificação no Word ou no editor da extensão."
    );
    if (!normalizeSpaces(question.bodyText)) add(
      "ARQUIVO.ENUNCIADO_AUSENTE", "Enunciado", "O enunciado da questão está ausente.",
      "Não existe texto suficiente para apresentar a pergunta ao aluno.", "Inclua o enunciado entre os metadados da questão e a alternativa A."
    );
    const alternatives = question.alternatives || [];
    const discursive = (question.questionFormat || detectQuestionFormat(question)) === "discursive";
    if (discursive && !normalizeSpaces(question.expectedResponseText)) add(
      "ARQUIVO.PADRAO_RESPOSTA_AUSENTE", "Padrão de resposta", "A questão discursiva não possui resposta esperada ou padrão de correção.",
      "O AvaliA exige um padrão de resposta para orientar a correção da questão aberta.", "Inclua ‘Padrão de resposta:’ ou ‘Resposta esperada:’ com os elementos que devem aparecer na resposta do estudante."
    );
    if (!discursive && alternatives.length !== REQUIRED_ALTERNATIVES) add(
      "ARQUIVO.QUANTIDADE_ALTERNATIVAS", "Alternativas", `A questão possui ${alternatives.length} alternativa(s); são exigidas exatamente ${REQUIRED_ALTERNATIVES}.`,
      "O lote não pode preservar o padrão obrigatório A–D.", alternatives.length > REQUIRED_ALTERNATIVES
        ? "Remova as alternativas além de D e ajuste o gabarito para A, B, C ou D."
        : `Inclua ${REQUIRED_ALTERNATIVES - alternatives.length} alternativa(s) e mantenha a ordem A, B, C e D.`,
      { detectedValue: alternatives.length, expectedValue: REQUIRED_ALTERNATIVES }
    );
    const expected = ["A", "B", "C", "D"];
    if (!discursive && alternatives.length === REQUIRED_ALTERNATIVES && alternatives.some((item, index) => item.letter !== expected[index])) add(
      "ARQUIVO.ORDEM_ALTERNATIVAS", "Alternativas", "As alternativas não estão identificadas, em ordem, como A, B, C e D.",
      "Uma resposta pode ser associada à letra errada durante o preenchimento.", "Renomeie e ordene as alternativas como A), B), C) e D).",
      { detectedValue: alternatives.map((item) => item.letter).join(", "), expectedValue: expected.join(", ") }
    );
    const alternativeKey = (item) => normalizeForMatch(item.plain) || attributesFromHtml(item.html, "data-aab-image").join("|") || attributesFromHtml(item.html, "data-aab-formula").join("|");
    const emptyAlternatives = alternatives.filter((item) => !alternativeKey(item)).map((item) => item.letter || "sem letra");
    if (!discursive && emptyAlternatives.length) add(
      "ARQUIVO.ALTERNATIVA_VAZIA", "Alternativas", `Há alternativa sem texto, imagem ou fórmula: ${emptyAlternatives.join(", ")}.`,
      "O AvaliA recusará o campo ou exibirá uma opção sem conteúdo.", "Preencha cada alternativa vazia ou insira nela uma imagem/fórmula válida.",
      { detectedValue: emptyAlternatives }
    );
    if (!discursive && new Set(alternatives.map(alternativeKey)).size !== alternatives.length) add(
      "ARQUIVO.ALTERNATIVAS_DUPLICADAS", "Alternativas", "Há alternativas com conteúdo idêntico.",
      "A questão deixa de ter quatro opções distintas e pode admitir uma resposta ambígua.", "Reescreva as opções repetidas para que A–D sejam semanticamente diferentes."
    );
    if (!discursive) alternatives.forEach((alternative) => {
      const artifact = optionSourceArtifact(alternative.plain);
      if (!artifact) return;
      add(
        "ARQUIVO.REFERENCIA_COMO_ALTERNATIVA", `Alternativa ${alternative.letter || "?"}`,
        `A alternativa ${alternative.letter || "?"} contém ${artifact}, não uma opção de resposta.`,
        "Referências, URLs, autoria e dados bibliográficos não podem ser usados como resposta.",
        "Mova a referência para a seção Referências e substitua a alternativa por um conceito completo e plausível.",
        { detectedValue: normalizeSpaces(alternative.plain).slice(0, 240) }
      );
    });
    const forbiddenOptions = discursive ? [] : alternatives.filter((alternative) => forbiddenAlternative(alternative.plain)).map((alternative) => alternative.letter || "?");
    if (forbiddenOptions.length) add(
      "ARQUIVO.ALTERNATIVA_PROIBIDA", `Alternativa ${forbiddenOptions.join(", ")}`,
      `Há alternativa genérica proibida em ${forbiddenOptions.join(", ")} (NRA, “todas” ou “nenhuma”).`,
      "A opção não funciona como distrator conceitual e viola o padrão Athus.",
      "Substitua por uma alternativa específica, plausível e ligada ao problema.",
      { detectedValue: forbiddenOptions }
    );
    if (!discursive && !expected.includes(question.correctLetter)) add(
      "ARQUIVO.GABARITO_INVALIDO", "Gabarito", "O gabarito está ausente ou fora do intervalo A–D.",
      "A extensão não consegue marcar uma única resposta correta.", "Informe Gabarito: A, B, C ou D e confira se a letra corresponde à alternativa correta.",
      { detectedValue: question.correctLetter || "vazio", expectedValue: "A, B, C ou D" }
    );
    if (!normalizeSpaces(question.feedbackText)) add(
      "ARQUIVO.FEEDBACK_AUSENTE", "Feedback pedagógico", "O feedback pedagógico está ausente.",
      "A etapa de correção fica incompleta e o aluno não recebe a justificativa da resposta.", discursive ? "Inclua um feedback pedagógico que explique os critérios esperados na resposta." : "Inclua uma explicação objetiva que justifique a alternativa correta."
    );
    if (!question.typeId || !TYPE_CATALOG.some((type) => type.id === String(question.typeId))) add(
      "ARQUIVO.TIPO_NAO_RECONHECIDO", "Tipo da questão", "O tipo da questão não foi reconhecido.",
      "O AvaliA pode abrir um modelo incompatível com a estrutura do enunciado.", "Escolha o tipo no editor da extensão ou declare ‘Tipo de questão’ no Word."
    );
    const unresolvedMedia = (question.media || []).filter((entry) => !entry.resolved);
    const unsupportedMedia = (question.media || []).filter((entry) => entry.resolved && !entry.supported);
    if (unresolvedMedia.length) add(
      "ARQUIVO.IMAGEM_NAO_LOCALIZADA", "Imagem", `${unresolvedMedia.length} imagem(ns) do Word não puderam ser localizadas dentro do DOCX.`,
      "A questão ficaria diferente do documento original.", "Abra o Word, reinsira a imagem como arquivo incorporado e salve novamente em DOCX.",
      { detectedValue: unresolvedMedia.map((entry) => entry.name || entry.relationshipId) }
    );
    if (unsupportedMedia.length) add(
      "ARQUIVO.IMAGEM_NAO_SUPORTADA", "Imagem", `${unsupportedMedia.length} imagem(ns) não puderam ser importadas com segurança.`,
      "A mídia não pode ser reproduzida e comparada fielmente no AvaliA.", `Converta a imagem para PNG ou JPEG e mantenha até 12 MB por imagem e 40 MB no DOCX. Motivo: ${Array.from(new Set(unsupportedMedia.map((entry) => entry.reason || `formato ${entry.extension || "desconhecido"}`))).join(" ")}`,
      { detectedValue: unsupportedMedia.map((entry) => `${entry.name || "imagem"}: ${entry.reason || entry.extension || "formato desconhecido"}`) }
    );
    return errors;
  }

  function calculateConfidence(question) {
    let score = 0.08;
    score += Math.min(0.2, Number(question.segmentationConfidence || 0.7) * 0.2);
    if (question.bodyText.length >= 30) score += 0.18;
    else if (question.bodyText) score += 0.08;
    if (question.questionFormat === "discursive") {
      if (question.expectedResponseText.length >= 30) score += 0.22;
      if (question.typeId === "158") score += 0.12;
    } else {
      if (question.alternatives.length === REQUIRED_ALTERNATIVES && question.alternatives.every((item, index) => item.letter === "ABCD"[index] && item.plain)) score += 0.22;
      if (question.correctIndex >= 0 && question.correctIndex < REQUIRED_ALTERNATIVES) score += 0.12;
    }
    if (question.feedbackText.length >= 20) score += 0.1;
    if (question.theme) score += 0.025;
    if (question.objective) score += 0.025;
    score += Math.min(0.1, Number(question.typeConfidence || 0.5) * 0.1);
    score += Math.min(0.06, Number(question.cognitiveConfidence || 0.5) * 0.06);
    return Math.min(1, Math.round(score * 100) / 100);
  }

  function finalizeQuestion(question, settings) {
    const options = settings || {};
    question.name = normalizeSpaces(question.name);
    question.bodyText = normalizeSpaces(question.bodyText).replace(/\s*\n\s*/g, "\n");
    question.expectedResponseText = normalizeSpaces(question.expectedResponseText).replace(/\s*\n\s*/g, "\n");
    question.feedbackText = normalizeSpaces(question.feedbackText).replace(/\s*\n\s*/g, "\n");
    question.bodyHtml = options.regenerateHtml ? textToHtml(question.bodyText) : (question.bodyHtml || textToHtml(question.bodyText));
    question.expectedResponseHtml = options.regenerateHtml ? textToHtml(question.expectedResponseText) : (question.expectedResponseHtml || textToHtml(question.expectedResponseText));
    question.feedbackHtml = options.regenerateHtml ? textToHtml(question.feedbackText) : (question.feedbackHtml || textToHtml(question.feedbackText));
    question.alternatives = (question.alternatives || []).map((item, index) => ({ ...item, letter: item.letter || LETTERS[index], plain: normalizeSpaces(item.plain), html: options.regenerateHtml ? textToHtml(item.plain) : (item.html || textToHtml(item.plain)) }));
    const normalizedCorrectLetter = String(question.correctLetter || "").trim().toUpperCase();
    question.correctIndex = normalizedCorrectLetter ? "ABCD".indexOf(normalizedCorrectLetter) : -1;
    question.questionFormat = detectQuestionFormat(question);
    question.name = question.name.replace(/_Discursiva$/i, '') + (question.questionFormat === 'discursive' ? '_Discursiva' : '');
    question.media = Array.from(new Map((question.media || []).map((entry) => [`${entry.relationshipId || ""}:${entry.hash || entry.name || ""}`, entry])).values())
      .map((entry) => {
        const { dataUrl: _embeddedInHtml, ...metadata } = entry;
        return metadata;
      });
    question.formulas = Array.from(new Map((question.formulas || []).map((entry) => [entry.hash || hashValue(entry.canonical || entry.plain), entry])).values());
    question.richIntegrity = computeRichIntegrity(question);
    question.richSignature = question.richIntegrity.signature;

    let type;
    if (options.preserveType && TYPE_CATALOG.some((entry) => entry.id === String(question.typeId))) {
      const selected = TYPE_CATALOG.find((entry) => entry.id === String(question.typeId));
      type = { id: selected.id, key: selected.key, label: selected.label, modelLabel: selected.shortLabel, inferred: false, confidence: 1, evidence: ["Tipo confirmado manualmente na revisão."], candidates: [{ id: selected.id, label: selected.label, score: 1, evidence: "Seleção manual" }] };
    } else if (question.questionFormat === "discursive") {
      const selected = TYPE_CATALOG.find((entry) => entry.id === "158");
      type = {
        id: selected.id, key: selected.key, label: selected.label, modelLabel: selected.shortLabel,
        inferred: !directType(question.typeDescription), confidence: directType(question.typeDescription) ? 1 : 0.92,
        evidence: [question.typeDescription ? `O Word informou “${normalizeSpaces(question.typeDescription)}”.` : "O título da questão identifica o modelo discursivo."],
        candidates: [{ id: selected.id, label: selected.label, score: 1, evidence: "Estrutura aberta sem alternativas A–D" }]
      };
    } else type = classifyQuestionType(question.typeDescription, question.bodyText, question.alternatives);
    question.typeId = type.id;
    question.typeKey = type.key;
    question.typeLabel = type.label;
    question.modelLabel = type.modelLabel;
    question.typeInferred = type.inferred;
    question.typeConfidence = type.confidence;
    question.typeEvidence = type.evidence;
    question.typeCandidates = type.candidates;

    if (options.preserveCognitive && COGNITIVE_CATALOG.some((entry) => entry.id === String(question.cognitiveId))) {
      const selected = COGNITIVE_CATALOG.find((entry) => entry.id === String(question.cognitiveId));
      question.cognitiveLabel = selected.label;
      question.cognitiveBasis = "confirmação manual";
      question.cognitiveConfidence = 1;
      question.cognitiveEvidence = "Nível confirmado manualmente na revisão.";
    } else {
      const cognitive = cognitiveFromObjective(question.objective, question.difficulty, question.bodyText);
      question.cognitiveId = cognitive.id;
      question.cognitiveLabel = cognitive.label;
      question.cognitiveBasis = cognitive.inferredFrom;
      question.cognitiveConfidence = cognitive.confidence;
      question.cognitiveEvidence = cognitive.evidence;
    }

    question.audit = textualAudit(question);
    question.technicalIssues = technicalIssues(question);
    question.athusRuleIssues = athusQuestionRuleIssues(question);
    question.hardErrors = question.technicalIssues.map((issue) => issue.message);
    const mathIssues = [...new Set((question.formulas || []).flatMap(f => f.conversionIssues || []))];
    if (mathIssues.length) question.hardErrors.push(`Fórmula requer correção antes do envio: ${mathIssues.join('; ')}. Confira a equação original no Word.`);
    question.reviewBlocks = question.audit.blocking.filter((check) => check.overridable).map((check) => check.message);
    question.athusRuleIssues.filter((issue) => issue.severity === "review").forEach((issue) => question.reviewBlocks.push(issue.message));
    if ((question.media || []).some((entry) => entry.resolved && entry.supported)) question.warnings = [`${question.richIntegrity.imageHashes.length} imagem(ns) serão inseridas e comparadas por assinatura antes do envio.`];
    else question.warnings = [];
    if (question.richIntegrity.formulaHashes.length) question.warnings.push(`${question.richIntegrity.formulaHashes.length} fórmula(s) do Word serão comparadas por estrutura antes do envio.`);
    const suspiciousCharacters = suspiciousCharacterInventory(question);
    if (suspiciousCharacters.length) question.reviewBlocks.push(`Foram encontrados caracteres invisíveis, de substituição ou de uso privado: ${suspiciousCharacters.map((entry) => `${entry.codePoint} × ${entry.count}`).join(", ")}. Confira o trecho antes do envio.`);
    if (Number(question.segmentationConfidence || 0) < 0.72) question.reviewBlocks.push("A separação desta questão foi inferida com baixa confiança; confira o trecho de origem.");
    if (question.typeInferred && Number(question.typeConfidence || 0) < 0.66) question.reviewBlocks.push("O tipo foi inferido com baixa confiança; confirme o modelo antes do envio.");
    question.audit.advisory.forEach((check) => question.warnings.push(check.message));
    question.athusRuleIssues.filter((issue) => issue.severity === "warning").forEach((issue) => question.warnings.push(issue.message));
    if (!question.typeDescription) question.warnings.push(`Tipo não declarado; autodetecção: ${question.typeLabel} (${Math.round(question.typeConfidence * 100)}%).`);
    if (!question.objective) question.warnings.push("Objetivo associado ausente; o nível cognitivo foi estimado pelo texto e pela dificuldade.");
    question.errors = [...question.hardErrors];
    question.confidence = calculateConfidence(question);
    question.executable = question.hardErrors.length === 0;
    question.needsReview = Boolean(question.hardErrors.length || question.reviewBlocks.length || question.confidence < REVIEW_THRESHOLD);
    question.autoApproved = question.executable && !question.needsReview;
    const engine = window.AvaliaBatchEngine;
    question.fingerprint = engine ? engine.questionFingerprint(question) : normalizeForMatch(question.name + question.bodyText);
    return question;
  }

  function extractQuestion(header, records, sourceInfo) {
    const themeField = extractField(records, LABELS.theme);
    const objectiveField = extractField(records, LABELS.objective);
    const explicitObjectives=records.filter(r=>/^Objetivo:\s*OB\d+:/i.test(r.plain)).map(r=>removeLabel(r,LABELS.objective).plain);
    if(explicitObjectives.length) objectiveField.value=explicitObjectives.join('; ');
    const typeField = extractField(records, LABELS.type);
    const difficultyField = extractField(records, LABELS.difficulty);
    const answerField = extractField(records, LABELS.answer);
    const feedbackField = extractField(records, LABELS.feedback);
    const bodyLabel = extractField(records, LABELS.body);
    const optionLimit = [answerField.index,feedbackField.index].filter(i=>i>=0).reduce((a,b)=>Math.min(a,b),records.length);
    const cycleStarts = records.map((record,i)=>i<optionLimit && alternativeRecord(record)?.letter==='A' && hasAlternativeCycle(records.slice(0,optionLimit),i,100) ? i : -1).filter(i=>i>=0);
    let firstAlternativeIndex = cycleStarts.length ? cycleStarts[cycleStarts.length-1] : records.findIndex((record,i) => i<optionLimit && alternativeRecord(record));
    const answerIndex = answerField.index;
    const feedbackIndex = feedbackField.index;
    const referencesIndex = records.findIndex((record) => LABELS.references.test(record.plain));
    const explicitDiscursiveAnswer = answerField.index >= 0 && /^(?:Gabarito\s+discursivo|Padr[aã]o\s+de\s+resposta(?:\s+esperad[oa])?|Resposta\s+esperada)(?:\s*[:–—-]\s*|\s*$)/i.test(records[answerField.index]?.plain || "");
    const provisionalDiscursive = detectQuestionFormat({ name: header.name, questionFormat: header.questionFormat, typeDescription: typeField.value }) === "discursive"
      || (!cycleStarts.length && explicitDiscursiveAnswer);
    // Lettered subcommands in an open response belong to the statement, not alternatives.
    if (provisionalDiscursive) firstAlternativeIndex = -1;
    const consumed = new Set([...themeField.indexes, ...objectiveField.indexes, ...typeField.indexes, ...difficultyField.indexes]);
    const metadataLabels = [LABELS.theme, LABELS.objective, LABELS.type, LABELS.difficulty, LABELS.administrative, LABELS.section];
    records.forEach((record, index) => {
      const label = metadataLabels.find(re => re.test(record.plain));
      if (!label) return;
      consumed.add(index);
      if (label === LABELS.section) return;
      if (bodyLabel.index > index && /^(?:Enunciado|Contextualiza[cç][aã]o|Texto[- ]base)\b/i.test(records[bodyLabel.index].plain)) {
        for (let next = index + 1; next < bodyLabel.index && !isKnownLabel(records[next]) && !alternativeRecord(records[next]); next++) consumed.add(next);
      } else if (!removeLabel(record, label).plain && records[index+1] && !isKnownLabel(records[index+1]) && !alternativeRecord(records[index+1])) consumed.add(index+1);
    });
    records.forEach((r,i)=>{if (/^(?:N[ií]vel(?: cognitivo| de complexidade)?|Grau de dificuldade|Multidisciplinaridade|Conte[uú]do e p[aá]gina abordada|UA que a quest[aã]o foi retirada)\s*:/i.test(r.plain)) consumed.add(i);});
    const bodyBoundaries = [firstAlternativeIndex, answerIndex, feedbackIndex, referencesIndex].filter((index) => index >= 0);
    const bodyEnd = bodyBoundaries.length ? Math.min(...bodyBoundaries) : records.length;
    let bodyRecords = records.slice(0, bodyEnd).filter((_record, index) => !consumed.has(index) && !LABELS.options.test(_record.plain));
    if (bodyLabel.index >= 0 && bodyLabel.index < bodyEnd) {
      bodyRecords = bodyRecords.flatMap((record) => {
        if (!LABELS.body.test(record.plain)) return [record];
        const stripped = removeLabel(record, LABELS.body);
        return stripped.plain ? [stripped] : [];
      });
    }
    if (header.inlineBody) bodyRecords.unshift({ plain: header.inlineBody, html: header.inlineHtml || escapeHtml(header.inlineBody), hasDrawing: Boolean(header.inlineDrawing), media: header.inlineMedia || [], formulas: header.inlineFormulas || [], sourceIndex: sourceInfo.start });
    const alternativesEnd = [answerIndex, feedbackIndex, referencesIndex].filter(i => i >= 0).reduce((a,b)=>Math.min(a,b),records.length);
    const alternatives = [];
    let currentAlternative = null;
    if (firstAlternativeIndex >= 0) {
      for (let index = firstAlternativeIndex; index < alternativesEnd; index += 1) {
        if (consumed.has(index)) { currentAlternative = null; continue; }
        const parsed = alternativeRecord(records[index]);
        if (parsed) { currentAlternative = parsed; alternatives.push(currentAlternative); }
        else if (currentAlternative && (records[index].plain || records[index].hasDrawing || records[index].formulas?.length) && !isKnownLabel(records[index])) {
          currentAlternative.plain = normalizeSpaces(`${currentAlternative.plain} ${records[index].plain}`);
          currentAlternative.sourceEnd = records[index].sourceIndex;
          currentAlternative.html += `${currentAlternative.html ? "<br>" : ""}${records[index].html || escapeHtml(records[index].plain)}`;
          currentAlternative.hasDrawing = currentAlternative.hasDrawing || records[index].hasDrawing;
          currentAlternative.media = [...(currentAlternative.media || []), ...(records[index].media || [])];
          currentAlternative.formulas = [...(currentAlternative.formulas || []), ...(records[index].formulas || [])];
        }
      }
    }
    const nextAnswer = answerIndex >= 0 ? records[answerIndex + 1]?.plain || "" : "";
    const answerText = answerField.value || (/^[A-E]$/i.test(nextAnswer) ? nextAnswer : "");
    const answerMatch = answerText.match(/^\s*(?:(?:alternativa|letra)\s*)?[\(\[]?([A-E])(?:[\)\]\.:\-]|\b)/i);
    const correctLetter = !provisionalDiscursive && answerMatch ? answerMatch[1].toUpperCase() : "";
    let expectedResponseRecords = [];
    let feedbackRecords = [];
    let referenceRecords = [];
    if (provisionalDiscursive && answerIndex >= 0) {
      const boundaries = [feedbackIndex, referencesIndex].filter((index) => index > answerIndex);
      const end = boundaries.length ? Math.min(...boundaries) : records.length;
      expectedResponseRecords = records.slice(answerIndex, end).filter((_r,i)=>!consumed.has(answerIndex+i));
      expectedResponseRecords[0] = removeLabel(expectedResponseRecords[0], LABELS.answer);
      expectedResponseRecords = expectedResponseRecords.filter((record) => record.plain || record.hasDrawing || record.formulas?.length);
    }
    if (feedbackIndex >= 0) {
      const end = [referencesIndex, answerIndex].filter(i => i > feedbackIndex).reduce((a,b)=>Math.min(a,b),records.length);
      feedbackRecords = records.slice(feedbackIndex, end).filter((_r,i)=>!consumed.has(feedbackIndex+i));
      feedbackRecords[0] = removeLabel(feedbackRecords[0], LABELS.feedback);
      feedbackRecords = feedbackRecords.filter((record) => record.plain || record.hasDrawing);
    }
    if (referencesIndex >= 0) {
      referenceRecords = records.slice(referencesIndex);
      referenceRecords[0] = removeLabel(referenceRecords[0], LABELS.references);
      referenceRecords = referenceRecords.filter((record) => record.plain || record.hasDrawing);
    }
    const difficulty = header.difficulty || difficultyField.value;
    const uaFields = records.map(r=>r.plain.match(/^UA(?: que a quest[aã]o foi retirada)?\s*:\s*(?:UA\s*)?(\d+)\b/i)).filter(Boolean);
    const uniqueUas=[...new Set(uaFields.map(m=>String(Number(m[1]))))];
    if(!header.ua && uniqueUas.length===1)header.ua=uniqueUas[0];
    const richRecords = [...bodyRecords, ...alternatives, ...expectedResponseRecords, ...feedbackRecords];
    const hasMedia = richRecords.some((record) => record.hasDrawing || record.media?.length);
    const media = richRecords.flatMap((record) => record.media || []);
    const formulas = richRecords.flatMap((record) => record.formulas || []);
    const sourceLines = records.map((record) => record.plain).filter(Boolean);
    const question = {
      ...header, questionFormat: provisionalDiscursive ? "discursive" : header.questionFormat, difficulty, theme: themeField.value, objective: objectiveField.value, typeDescription: typeField.value,
      bodyHtml: paragraphBlock(bodyRecords), bodyText: bodyRecords.map((record) => record.plain).join("\n"),
      alternatives, correctLetter, feedbackHtml: paragraphBlock(feedbackRecords), feedbackText: feedbackRecords.map((record) => record.plain).join("\n"),
      expectedResponseHtml: paragraphBlock(expectedResponseRecords), expectedResponseText: expectedResponseRecords.map((record) => record.plain).join("\n"),
      referencesText: referenceRecords.map((record) => record.plain).join("\n"),
      keywords: [themeField.value, header.ua ? `UA ${header.ua}` : ""].filter(Boolean), hasMedia, media, formulas,
      sourceStart: sourceInfo.start, sourceEnd: sourceInfo.end, sourceText: sourceLines.join("\n"), sourceExcerpt: normalizeSpaces(sourceLines.join(" ")).slice(0, 320),
      contentScope: "statement-and-alternatives",
      segmentationMethod: sourceInfo.method, segmentationConfidence: sourceInfo.confidence,
      segmentationWarnings: [...records.map(r=>r.segmentationWarning).filter(Boolean), ...(records.filter(r=>/^(?:Gabarito|Resposta correta)\s*:/i.test(r.plain)).length>1?["Há mais de um gabarito neste bloco. Identifique cada questão separadamente para evitar misturar enunciados e alternativas."]:[])],
      fieldMap: [
        {field:"Identificação",start:sourceInfo.start,end:sourceInfo.start},
        ...bodyRecords.map(r=>({field:"Enunciado",start:r.sourceIndex,end:r.sourceIndex})),
        ...alternatives.map(r=>({field:`Alternativa ${r.letter}`,start:r.sourceIndex,end:r.sourceEnd || r.sourceIndex})),
        ...[...consumed].map(i=>({field:"Metadados (fora do conteúdo)",start:records[i].sourceIndex,end:records[i].sourceIndex})),
        ...(provisionalDiscursive ? expectedResponseRecords.map(r=>({field:"Padrão de resposta",start:r.sourceIndex,end:r.sourceIndex})) : answerIndex>=0?[{field:"Gabarito / resposta esperada",start:records[answerIndex].sourceIndex,end:records[answerIndex].sourceIndex}]:[]),
        ...feedbackRecords.map(r=>({field:"Feedback",start:r.sourceIndex,end:r.sourceIndex}))
      ]
    };
    return finalizeQuestion(question);
  }

  function hasAlternativeCycle(records, startIndex, limit) {
    const end = Math.min(records.length, startIndex + (limit || 40));
    let expected = 0;
    for (let index = startIndex; index < end; index += 1) {
      // A later explicit question cannot provide alternatives for a numbered objective in the cover.
      const boundary = parseHeader(records[index]);
      if (boundary && boundary.boundaryKind !== 'styled-number') return false;
      if (index > startIndex && [LABELS.answer,LABELS.feedback,LABELS.references,LABELS.objective,LABELS.theme].some(re=>re.test(records[index].plain))) return false;
      const alternative = alternativeRecord(records[index]);
      if (!alternative) continue;
      if (alternative.letter === "ABCD"[expected]) expected += 1;
      else if (alternative.letter === "A") expected = 1;
      if (expected === REQUIRED_ALTERNATIVES) return true;
    }
    return false;
  }

  function inferGroupsFromCycles(records) {
    const aIndexes = records.map((r,i)=>alternativeRecord(r)?.letter==='A' && hasAlternativeCycle(records,i,100)?i:-1).filter(i=>i>=0);
    if (!aIndexes.length) return [];
    const starts = [];
    for (let i=0;i<aIndexes.length;i++) {
      const aIndex=aIndexes[i]; let start=0;
      if (i) {
        const prior=aIndexes[i-1];
        const meta=records.findIndex((r,j)=>j>prior && j<aIndex && (LABELS.theme.test(r.plain)||LABELS.objective.test(r.plain)||/\|\s*N[ií]vel\s*:/.test(r.plain)));
        if (meta>=0) start=meta;
        else {
          const terminal=records.map((r,j)=>j>prior&&j<aIndex&&(LABELS.feedback.test(r.plain)||LABELS.answer.test(r.plain))?j:-1).filter(j=>j>=0).at(-1);
          if (terminal!==undefined) { start=terminal+1; if (!removeLabel(records[terminal],LABELS.feedback.test(records[terminal].plain)?LABELS.feedback:LABELS.answer).plain) start++; }
          else {
            // With no key or feedback, only a visible break after the last option can delimit the next statement.
            let lastOption=prior;for(let j=prior;j<aIndex;j++) if(alternativeRecord(records[j])) lastOption=j;
            start=lastOption+1;
          }
        }
      } else {
        const meta=records.findIndex((r,j)=>j<aIndex&&(LABELS.theme.test(r.plain)||LABELS.objective.test(r.plain)||/\|\s*N[ií]vel\s*:/.test(r.plain)));
        if(meta>=0)start=meta;
      }
      starts.push({start,aIndex});
    }
    return starts.map((candidate,i)=>{
      const slice=records.slice(candidate.start,starts[i+1]?.start??records.length),number=i+1;
      return {header:{name:`Questão ${number} · detectada automaticamente`,number,assessment:"",ua:"",objectiveNumber:"",difficulty:"",headerFormat:"inferred",boundaryKind:"alternative-cycle",boundaryConfidence:0.68,inlineBody:""},records:slice,
        sourceInfo:{start:slice[0]?.sourceIndex||1,end:slice.at(-1)?.sourceIndex||1,method:"Ciclo de alternativas; conferir limites do enunciado",confidence:0.68}};
    });
  }

  function splitQuestions(records) {
    const groups = []; let active = null; let pending = [];
    const metadata = r => [LABELS.theme,LABELS.objective,LABELS.type,LABELS.difficulty,LABELS.administrative].some(p=>p.test(r.plain)) || /^(?:N[ií]vel|Multidisciplinaridade|Grau de dificuldade|Quest[oõ]es? (?:de |discursiva))/i.test(r.plain);
    records.forEach((record,index) => {
      let header = parseHeader(record);
      if (header?.boundaryKind === "styled-number") header = null;
      if (!header) {
        const numeric = record.plain.match(/^(\d{1,3})\s*[).:\-]\s+(.{15,})$/) || (/^\d{1,3}$/.test(record.listMarker||'') ? [record.plain,record.listMarker,record.plain] : null);
        const previousComplete = !active || active.records.some(r=>LABELS.answer.test(r.plain)||LABELS.feedback.test(r.plain)) || hasAlternativeCycle(active.records,0,active.records.length);
        const consecutive = !active || Number(numeric?.[1]) === active.header.number+1;
        if (numeric && previousComplete && consecutive && hasAlternativeCycle(records,index+1,100)) {
          header = {name:`Questão ${numeric[1]}`,number:Number(numeric[1]),assessment:"",ua:"",objectiveNumber:"",difficulty:"",headerFormat:"inferred",boundaryKind:"numbered-body",boundaryConfidence:0.78,inlineBody:numeric[2],inlineHtml:stripVisiblePrefix(record.html,record.plain.length-numeric[2].length)};
        }
      }
      if (header && active && header.number === active.header.number && !active.header.inlineBody && active.records.every(r=>metadata(r)||(!r.plain&&r.hasDrawing))) {
        active.header = {...active.header,...header}; return;
      }
      if (header) {
        const identificationStart=pending.map((r,i)=>/^Identifica[cç][aã]o da quest[aã]o/i.test(r.plain)?i:-1).filter(i=>i>=0).at(-1);
        let carry = pending.slice(identificationStart??0).filter(metadata); pending = [];
        if (active) {
          // Objectives placed immediately BEFORE the next title belong to that question.
          const tail = [];
          while (active.records.length && metadata(active.records[active.records.length-1])) tail.unshift(active.records.pop());
          carry = [...tail,...carry];
          active.sourceInfo.end = active.records.at(-1)?.sourceIndex || active.sourceInfo.start;
          groups.push(active);
        }
        active = {header,records:carry,sourceInfo:{start:record.sourceIndex,end:record.sourceIndex,method:header.boundaryKind,confidence:header.boundaryConfidence}};
      } else if (active) active.records.push(record);
      else pending.push(record);
    });
    if (active) { active.sourceInfo.end=active.records.at(-1)?.sourceIndex||active.sourceInfo.start; groups.push(active); }
    return groups.length ? groups : inferGroupsFromCycles(records);
  }

  function auditDuplicates(questions) {
    (questions || []).forEach((question) => {
      question.warnings = (question.warnings || []).filter((warning) => !/^(?:A numeração .* aparece|Conteúdo idêntico à questão na posição|Conteúdo muito semelhante à questão na posição)/.test(warning));
      delete question.duplicateOf;
      delete question.nearDuplicateOf;
      delete question.nearDuplicateScore;
    });
    const numberPositions = new Map();
    (questions || []).forEach((question, index) => {
      const positions = numberPositions.get(question.number) || [];
      positions.push(index + 1);
      numberPositions.set(question.number, positions);
    });
    (questions || []).forEach((question) => {
      const positions = numberPositions.get(question.number) || [];
      if (positions.length > 1) question.warnings.push(`A numeração ${question.number} aparece ${positions.length} vezes no arquivo (posições ${positions.join(", ")}). Cada ocorrência será tratada separadamente.`);
    });
    const firstByFingerprint = new Map();
    (questions || []).forEach((question, index) => {
      const normalizedContent = [
        question.bodyText,
        ...(question.alternatives || []).map((alternative) => alternative.plain),
        question.correctLetter,
        question.expectedResponseText,
        question.questionFormat,
        question.feedbackText
      ].map(normalizeForMatch).join("\u241f");
      const engine = window.AvaliaBatchEngine;
      question.duplicateFingerprint = engine ? engine.fnv1a(normalizedContent) : normalizedContent;
      if (!firstByFingerprint.has(question.duplicateFingerprint)) firstByFingerprint.set(question.duplicateFingerprint, index);
      else {
        const firstIndex = firstByFingerprint.get(question.duplicateFingerprint);
        question.duplicateOf = firstIndex + 1;
        question.warnings.push(`Conteúdo idêntico à questão na posição ${firstIndex + 1}. Isto é apenas um aviso; esta ocorrência continuará válida para o envio.`);
      }
    });
    const tokenSet = (question) => new Set(normalizeForMatch([
      question.bodyText,
      ...(question.alternatives || []).map((alternative) => alternative.plain),
      question.expectedResponseText
    ].join(" ")).replace(/[^a-z0-9áàâãéèêíïóôõöúç]+/gi, " ").split(/\s+/).filter((token) => token.length >= 3));
    const sets = (questions || []).map(tokenSet);
    const similarity = (left, right) => {
      if (left.size < 18 || right.size < 18) return 0;
      let intersection = 0;
      left.forEach((token) => { if (right.has(token)) intersection += 1; });
      return intersection / (left.size + right.size - intersection || 1);
    };
    for (let index = 1; index < sets.length; index += 1) {
      if (questions[index].duplicateOf) continue;
      let bestIndex = -1;
      let bestScore = 0;
      for (let previous = 0; previous < index; previous += 1) {
        const score = similarity(sets[index], sets[previous]);
        if (score > bestScore) { bestScore = score; bestIndex = previous; }
      }
      if (bestIndex >= 0 && bestScore >= 0.9) {
        questions[index].nearDuplicateOf = bestIndex + 1;
        questions[index].nearDuplicateScore = Math.round(bestScore * 100);
        questions[index].warnings.push(`Conteúdo muito semelhante à questão na posição ${bestIndex + 1} (${questions[index].nearDuplicateScore}% de termos em comum). Isto é apenas um aviso; esta ocorrência continuará válida para o envio.`);
      }
    }
  }

  const REVIEW_DIAGNOSTICS = Object.freeze({
    "body-length": {
      code: "ARQUIVO.ENUNCIADO_CURTO", field: "Enunciado", title: "Enunciado possivelmente recortado",
      impact: "A pergunta pode ter perdido contexto ou não apresentar uma tarefa completa.",
      action: "Compare o trecho indicado com o Word e complete o enunciado antes de autorizar."
    },
    "feedback-length": {
      code: "ARQUIVO.FEEDBACK_CURTO", field: "Feedback pedagógico", title: "Feedback possivelmente incompleto",
      impact: "A justificativa pode não explicar por que o gabarito está correto.",
      action: "Amplie o feedback com a justificativa conceitual da resposta correta."
    },
    delimiters: {
      code: "ARQUIVO.DELIMITADOR_ABERTO", field: "Texto", title: "Parêntese, colchete ou aspas sem fechamento",
      impact: "O texto pode ter sido cortado ou conter uma fórmula/citação mal formada.",
      action: "Abra a questão e feche ou remova o delimitador incorreto, comparando com o Word."
    },
    placeholders: {
      code: "ARQUIVO.MARCADOR_PENDENTE", field: "Texto", title: "Marcador de edição não substituído",
      impact: "O aluno receberia instruções internas como TODO, texto aqui ou um campo de modelo.",
      action: "Substitua o marcador pelo conteúdo definitivo da questão."
    },
    truncation: {
      code: "ARQUIVO.TEXTO_TRUNCADO", field: "Enunciado ou feedback", title: "Final de texto possivelmente cortado",
      impact: "Uma frase incompleta pode alterar o sentido da pergunta ou da correção.",
      action: "Confira o fim do enunciado e do feedback no trecho de origem e restaure o conteúdo ausente."
    },
    instruction: {
      code: "ARQUIVO.COMANDO_POUCO_CLARO", field: "Enunciado", title: "Comando da questão não identificado",
      impact: "O aluno pode não saber exatamente o que deve selecionar.",
      action: "Inclua um comando direto, como ‘Qual alternativa...?’ ou ‘Assinale...’."
    },
    "body-ending": {
      code: "ARQUIVO.ENUNCIADO_SEM_ENCERRAMENTO", field: "Enunciado", title: "Enunciado termina sem pontuação",
      impact: "Pode ser apenas estilo, mas também pode indicar uma frase incompleta.",
      action: "Confira o final do enunciado no Word e ajuste a pontuação se necessário."
    }
  });

  function diagnosticSource(question) {
    return {
      start: Number(question?.sourceStart || 0),
      end: Number(question?.sourceEnd || question?.sourceStart || 0),
      method: question?.segmentationMethod || "não informado",
      confidence: Math.round(Number(question?.segmentationConfidence || 0) * 100)
    };
  }

  function enrichQuestionIssue(question, questionIndex, issue) {
    return {
      severity: issue.severity || "warning",
      category: issue.category || "quality",
      code: issue.code || "ARQUIVO.REVISAO",
      title: issue.title || issue.message || "Conferência necessária",
      field: issue.field || "Questão",
      message: issue.message || issue.title || "Conferência necessária.",
      impact: issue.impact || "O conteúdo pode ficar diferente do documento original.",
      action: issue.action || "Abra a questão, confira o trecho do Word e corrija ou autorize conscientemente.",
      overridable: issue.overridable !== false,
      questionIndex,
      questionNumber: question?.number ?? questionIndex + 1,
      questionName: question?.name || `Questão ${questionIndex + 1}`,
      source: diagnosticSource(question),
      excerpt: normalizeSpaces(question?.sourceExcerpt || question?.sourceText || question?.bodyText).slice(0, 320),
      ...(Object.prototype.hasOwnProperty.call(issue, "detectedValue") ? { detectedValue: issue.detectedValue } : {}),
      ...(Object.prototype.hasOwnProperty.call(issue, "expectedValue") ? { expectedValue: issue.expectedValue } : {})
    };
  }

  function questionDiagnosticIssues(question, questionIndex) {
    const technical = question.technicalIssues || technicalIssues(question);
    const technicalCodes = new Set(technical.map((issue) => issue.code));
    const issues = technical.map((issue) => enrichQuestionIssue(question, questionIndex, {
      ...issue,
      title: issue.message.replace(/[.!?]+$/, "")
    }));
    (question.athusRuleIssues || athusQuestionRuleIssues(question)).forEach((issue) => {
      issues.push(enrichQuestionIssue(question, questionIndex, issue));
    });
    (question.audit?.checks || []).forEach((check) => {
      if (check.status === "pass" || ["alternatives", "answer-explanation"].includes(check.id)) return;
      if (check.id === "body-length" && technicalCodes.has("ARQUIVO.ENUNCIADO_AUSENTE")) return;
      if (check.id === "feedback-length" && technicalCodes.has("ARQUIVO.FEEDBACK_AUSENTE")) return;
      const rule = REVIEW_DIAGNOSTICS[check.id];
      if (!rule) return;
      issues.push(enrichQuestionIssue(question, questionIndex, {
        ...rule,
        severity: check.status === "blocking" ? "review" : "warning",
        category: "quality",
        message: check.message,
        overridable: true
      }));
    });
    if (Number(question.segmentationConfidence || 0) < 0.72) issues.push(enrichQuestionIssue(question, questionIndex, {
      code: "ARQUIVO.SEPARACAO_BAIXA_CONFIANCA", severity: "review", category: "segmentation", field: "Limites da questão",
      title: "Separação da questão inferida com baixa confiança",
      message: `Os limites foram inferidos com ${Math.round(Number(question.segmentationConfidence || 0) * 100)}% de confiança.`,
      impact: "Uma linha da questão anterior ou seguinte pode ter sido incluída no bloco errado.",
      action: "Abra o trecho de origem, compare o início e o fim e ajuste o Word ou os campos no editor.", overridable: true
    }));
    if (question.typeInferred && Number(question.typeConfidence || 0) < 0.66) issues.push(enrichQuestionIssue(question, questionIndex, {
      code: "ARQUIVO.TIPO_BAIXA_CONFIANCA", severity: "review", category: "classification", field: "Tipo da questão",
      title: "Tipo detectado com baixa confiança", message: `A melhor hipótese foi ${question.typeLabel}, com ${Math.round(Number(question.typeConfidence || 0) * 100)}% de confiança.`,
      impact: "Um modelo incorreto pode fazer o AvaliA exigir campos incompatíveis.",
      action: "Escolha manualmente o tipo correto na revisão e aplique a conferência novamente.", overridable: true
    }));
    const suspicious = suspiciousCharacterInventory(question);
    if (suspicious.length) issues.push(enrichQuestionIssue(question, questionIndex, {
      code: "ARQUIVO.CARACTERE_SUSPEITO", severity: "review", category: "integrity", field: "Texto",
      title: "Caractere invisível ou não textual encontrado",
      message: suspicious.map((entry) => `${entry.codePoint} × ${entry.count}`).join(", "),
      impact: "O texto pode conter um marcador invisível, glifo substituído ou símbolo que não será reproduzido como esperado.",
      action: "Compare o trecho com o Word, remova o caractere estranho ou substitua-o pelo símbolo correto.", overridable: true
    }));
    if (!question.typeDescription) issues.push(enrichQuestionIssue(question, questionIndex, {
      code: "ARQUIVO.TIPO_AUTODETECTADO", severity: "warning", category: "classification", field: "Tipo da questão",
      title: "Tipo não declarado no Word", message: `A extensão escolheu ${question.typeLabel} com ${Math.round(Number(question.typeConfidence || 0) * 100)}% de confiança.`,
      impact: "A classificação dependeu apenas da estrutura e do comando encontrados.",
      action: "Confira o tipo detectado; se estiver correto, nenhuma alteração é necessária.", overridable: true
    }));
    if (question.duplicateOf) issues.push(enrichQuestionIssue(question, questionIndex, {
      code: "ARQUIVO.QUESTAO_REPETIDA", severity: "warning", category: "duplication", field: "Questão completa",
      title: "Questão repetida no mesmo arquivo", message: `O conteúdo é idêntico ao da questão na posição ${question.duplicateOf}.`,
      impact: "A repetição não impede o envio, mas reduz a variedade da avaliação.",
      action: "Mantenha se a repetição for intencional ou substitua a questão; as demais válidas continuarão liberadas.", overridable: true
    }));
    if (question.nearDuplicateOf) issues.push(enrichQuestionIssue(question, questionIndex, {
      code: "ARQUIVO.QUESTAO_MUITO_SEMELHANTE", severity: "warning", category: "duplication", field: "Questão completa",
      title: "Questão muito semelhante a outra do arquivo", message: `A questão compartilha ${question.nearDuplicateScore}% dos termos relevantes com a questão na posição ${question.nearDuplicateOf}.`,
      impact: "Pode ser uma repetição reformulada e reduzir a variedade, mas também pode ser uma escolha pedagógica legítima.",
      action: "Compare as duas questões e mantenha ambas se avaliarem habilidades ou contextos distintos; o aviso não bloqueia o envio.", overridable: true
    }));
    return issues;
  }

  function fileLevelDiagnosticIssues(parsed) {
    const issues = [];
    const questions = parsed.questions || [];
    const declaredAssessments = questions.map((question) => String(question.assessment || "").toUpperCase()).filter(Boolean);
    const assessmentCounts = declaredAssessments.reduce((counts, assessment) => ({ ...counts, [assessment]: (counts[assessment] || 0) + 1 }), {});
    const declaredAssessment = Object.entries(assessmentCounts).sort((left, right) => right[1] - left[1])[0]?.[0] || "";
    const fileAssessment = String(parsed.fileName || "").match(/(?:^|[_\s.-])(AD|AI|PS|P1|P2|SCH|P3)(?=[_\s.-]|$)/i)?.[1]?.toUpperCase() || "";
    const assessment = declaredAssessment || fileAssessment;
    if (Object.keys(assessmentCounts).length > 1) issues.push({
      severity: "review", category: "rules", code: "ATHUS.AVALIACOES_MISTURADAS", title: "Mais de um tipo de avaliação no mesmo arquivo",
      field: "Identificação", message: `Identificações encontradas: ${Object.entries(assessmentCounts).map(([key, count]) => `${key} (${count})`).join(", ")}.`,
      impact: "As regras de quantidade, abrangência e dificuldade podem ser aplicadas ao modelo errado.",
      action: "Separe as avaliações em arquivos distintos ou corrija as identificações antes de autorizar.", overridable: true,
      questionIndex: null, questionNumber: null, questionName: "Arquivo", source: null, excerpt: ""
    });
    const expectedByAssessment = { AD: 10, AI: 5, PS: 5, P1: 18, P2: 18, SCH: 18, P3: 18 };
    const expectedQuestions = expectedByAssessment[assessment] || 0;
    if (expectedQuestions && questions.length !== expectedQuestions) {
      const difference = expectedQuestions - questions.length;
      issues.push({
        severity: "review", category: "rules", code: "ARQUIVO.QUANTIDADE_QUESTOES", title: `Quantidade de questões diferente do padrão ${assessment}`,
        field: "Quantidade do arquivo", message: `Foram reconhecidas ${questions.length} questões; o padrão ${assessment} prevê ${expectedQuestions}. ${difference > 0 ? `Faltam ${difference}.` : `Há ${Math.abs(difference)} adicional(is).`}`,
        impact: "O arquivo pode estar incompleto ou usar uma exceção que ainda não foi confirmada pelo professor.",
        action: `Confira se esta avaliação recebeu uma quantidade excepcional. Caso contrário, ${difference > 0 ? `inclua as ${difference} questão(ões) ausente(s)` : `remova as ${Math.abs(difference)} questão(ões) excedente(s)`} e importe novamente.`,
        overridable: true, detectedValue: questions.length, expectedValue: expectedQuestions,
        questionIndex: null, questionNumber: null, questionName: "Arquivo", source: null, excerpt: ""
      });
    }
    const objectiveCount = questions.filter((question) => (question.questionFormat || detectQuestionFormat(question)) !== "discursive").length;
    const discursiveCount = questions.length - objectiveCount;
    if (assessment === "P1" && (objectiveCount !== 16 || discursiveCount !== 2)) issues.push({
      severity: "review", category: "rules", code: "ATHUS.P1_COMPOSICAO_INVALIDA", title: "Composição da P1 diferente de 16 objetivas + 2 discursivas",
      field: "Composição da avaliação", message: `Foram reconhecidas ${objectiveCount} objetiva(s) e ${discursiveCount} discursiva(s).`,
      impact: "A P1 não atende à composição consolidada do Projeto Athus, mesmo que possua 18 questões no total.",
      action: "Inclua ou reclassifique as questões necessárias. Uma exceção específica deve ser lida e aprovada pelo professor no lote.",
      overridable: true, detectedValue: { objective: objectiveCount, discursive: discursiveCount }, expectedValue: { objective: 16, discursive: 2 },
      questionIndex: null, questionNumber: null, questionName: "Arquivo", source: null, excerpt: ""
    });
    const difficultyKey = (value) => {
      const level = normalizeForMatch(value);
      if (level.includes("facil")) return "easy";
      if (level.includes("medio") || level.includes("media")) return "medium";
      if (level.includes("dificil")) return "hard";
      return "unknown";
    };
    const difficultyCounts = questions.reduce((counts, question) => {
      counts[difficultyKey(question.difficulty)] += 1;
      return counts;
    }, { easy: 0, medium: 0, hard: 0, unknown: 0 });
    const expectedDifficulty = ({ AD: [4, 4, 2], AI: [2, 2, 1], PS: [2, 2, 1], P1: [7, 7, 4], P2: [7, 7, 4], SCH: [7, 7, 4], P3: [7, 7, 4] })[assessment];
    if (expectedDifficulty && questions.length === expectedQuestions && !difficultyCounts.unknown
      && [difficultyCounts.easy, difficultyCounts.medium, difficultyCounts.hard].some((count, index) => count !== expectedDifficulty[index])) issues.push({
      severity: "review", category: "rules", code: "ATHUS.DISTRIBUICAO_DIFICULDADE", title: "Distribuição de dificuldade fora do padrão",
      field: "Dificuldade", message: `Encontrado: ${difficultyCounts.easy} fáceis, ${difficultyCounts.medium} médias e ${difficultyCounts.hard} difíceis. Esperado: ${expectedDifficulty[0]}, ${expectedDifficulty[1]} e ${expectedDifficulty[2]}.`,
      impact: "A avaliação pode ficar desequilibrada em relação à distribuição 40%/40%/20%.",
      action: "Reclassifique ou substitua questões; se houver regra específica para esta atividade, registre e aprove a exceção.", overridable: true,
      detectedValue: difficultyCounts, expectedValue: { easy: expectedDifficulty[0], medium: expectedDifficulty[1], hard: expectedDifficulty[2] },
      questionIndex: null, questionNumber: null, questionName: "Arquivo", source: null, excerpt: ""
    });
    if (assessment === "AD") {
      const uaCounts = questions.reduce((counts, question) => {
        const ua = Number(String(question.ua || "").match(/\d+/)?.[0]);
        if (Number.isFinite(ua)) counts[ua] = (counts[ua] || 0) + 1;
        return counts;
      }, {});
      const invalidUas = Object.keys(uaCounts).map(Number).filter((ua) => ua < 1 || ua > 5);
      const distributionMismatch = [1, 2, 3, 4, 5].some((ua) => Number(uaCounts[ua] || 0) !== 2);
      if (invalidUas.length || distributionMismatch) issues.push({
        severity: invalidUas.length ? "review" : "warning", category: "rules", code: "ATHUS.AD_ABRANGENCIA_UA", title: "Distribuição da AD entre UA1 e UA5 precisa ser conferida",
        field: "Abrangência", message: `Distribuição encontrada: ${[1, 2, 3, 4, 5].map((ua) => `UA${ua}=${uaCounts[ua] || 0}`).join(" · ")}${invalidUas.length ? ` · fora da abrangência: ${invalidUas.map((ua) => `UA${ua}`).join(", ")}` : ""}.`,
        impact: invalidUas.length ? "A AD contém conteúdo fora da abrangência exclusiva UA1–UA5." : "A cobertura preferencial de duas questões por UA não foi alcançada.",
        action: invalidUas.length ? "Remova ou substitua as questões fora de UA1–UA5." : "Confira se a distribuição diferente foi intencional.", overridable: true,
        questionIndex: null, questionNumber: null, questionName: "Arquivo", source: null, excerpt: ""
      });
    }
    const numbers = questions.map((question) => Number(question.number)).filter(Number.isFinite);
    const uniqueNumbers = new Set(numbers);
    if (numbers.length === questions.length && uniqueNumbers.size === numbers.length && numbers.length > 1) {
      const expected = Array.from({ length: numbers.length }, (_unused, index) => index + 1);
      if (numbers.some((number, index) => number !== expected[index])) issues.push({
        severity: "warning", category: "structure", code: "ARQUIVO.NUMERACAO_NAO_SEQUENCIAL", title: "Numeração fora da sequência 1 até o total",
        field: "Numeração", message: `Ordem encontrada: ${numbers.join(", ")}.`,
        impact: "A ordem de envio seguirá a posição no arquivo, não o valor do número.",
        action: "Confira se a ordem é intencional; renumere no Word se desejar correspondência direta.", overridable: true,
        questionIndex: null, questionNumber: null, questionName: "Arquivo", source: null, excerpt: ""
      });
    }
    if (parsed.answerDistributionWarning) issues.push({
      severity: "warning", category: "quality", code: "ARQUIVO.GABARITO_CONCENTRADO", title: "Gabarito muito concentrado em uma letra",
      field: "Distribuição do gabarito", message: parsed.answerDistributionWarning,
      impact: "Um padrão previsível pode reduzir a qualidade pedagógica da avaliação.",
      action: "Confira as respostas; altere apenas se a concentração não for intencional.", overridable: true,
      questionIndex: null, questionNumber: null, questionName: "Arquivo", source: null, excerpt: ""
    });
    return issues;
  }

  function buildFileDiagnostics(parsed) {
    const questions = parsed?.questions || [];
    const issues = questions.flatMap((question, index) => questionDiagnosticIssues(question, index));
    issues.push(...fileLevelDiagnosticIssues(parsed || {}));
    const counts = issues.reduce((result, issue) => {
      const key = ["blocking", "review", "warning", "info"].includes(issue.severity) ? issue.severity : "warning";
      result[key] += 1;
      return result;
    }, { blocking: 0, review: 0, warning: 0, info: 0 });
    const status = counts.blocking ? "blocked" : counts.review ? "review" : counts.warning ? "warning" : "ready";
    return {
      schemaVersion: FILE_DIAGNOSTIC_VERSION,
      parserVersion: parsed?.parserVersion || "",
      generatedAt: new Date().toISOString(),
      fileName: parsed?.fileName || "avaliação.docx",
      fileFingerprint: parsed?.fileFingerprint || "",
      status,
      scope: "Estrutura do DOCX, limites das questões, regras consolidadas do Projeto Athus, composição, dificuldade, campos obrigatórios, alternativas A–D e gabarito nas objetivas, padrão de resposta nas discursivas, qualidade textual e integridade de mídia. A correção conceitual depende dos materiais da coleção ativa.",
      summary: {
        questions: questions.length,
        validQuestions: questions.filter((question) => question.executable).length,
        blockedQuestions: questions.filter((question) => !question.executable).length,
        reviewQuestions: questions.filter((question) => question.executable && question.needsReview).length,
        duplicateQuestions: questions.filter((question) => Boolean(question.duplicateOf)).length,
        similarQuestions: questions.filter((question) => Boolean(question.nearDuplicateOf)).length,
        objectiveQuestions: questions.filter((question) => (question.questionFormat || detectQuestionFormat(question)) !== "discursive").length,
        discursiveQuestions: questions.filter((question) => (question.questionFormat || detectQuestionFormat(question)) === "discursive").length,
        actionable: counts.blocking + counts.review,
        assessment: questions.map((question) => String(question.assessment || "").toUpperCase()).find(Boolean) || String(parsed?.fileName || "").match(/(?:^|[_\s.-])(AD|AI|PS|P1|P2|SCH|P3)(?=[_\s.-]|$)/i)?.[1]?.toUpperCase() || "",
        ...counts
      },
      issues
    };
  }

  function importFailureDiagnostic(error, file) {
    const message = normalizeSpaces(error?.message || error || "Falha não identificada ao ler o arquivo.");
    let issue = {
      code: "ARQUIVO.LEITURA_FALHOU", title: "O Word não pôde ser interpretado", field: "Arquivo",
      message, impact: "Nenhuma questão foi criada e nada foi enviado ao AvaliA.",
      action: "Abra o arquivo no Word, use Salvar como DOCX e tente importar a nova cópia."
    };
    if (!/\.docx$/i.test(file?.name || "")) issue = {
      ...issue, code: "ARQUIVO.EXTENSAO_INVALIDA", title: "O arquivo não é DOCX", message: "A extensão aceita avaliações prontas somente no formato .docx.", action: "Salve o documento como Documento do Word (.docx) e selecione essa cópia."
    };
    else if (/password|encrypted|criptograf|senha/i.test(message)) issue = {
      ...issue, code: "ARQUIVO.PROTEGIDO", title: "O DOCX está protegido ou criptografado", action: "Remova a senha ou proteção de abertura no Word, salve uma cópia e importe novamente."
    };
    else if (/central directory|zip|corrupt|invalid signature|unexpected end|can't find end/i.test(message)) issue = {
      ...issue, code: "ARQUIVO.CORROMPIDO", title: "O arquivo está corrompido ou não é um DOCX real", action: "Abra-o no Word e gere uma nova cópia com Salvar como Documento do Word (.docx)."
    };
    else if (/word\/document\.xml/i.test(message)) issue = {
      ...issue, code: "ARQUIVO.PACOTE_INVALIDO", title: "Falta o conteúdo principal do DOCX", action: "Converta o arquivo novamente pelo Word; apenas renomear a extensão não cria um DOCX válido."
    };
    else if (/Nenhuma questão foi reconhecida/i.test(message)) issue = {
      ...issue, code: "ARQUIVO.QUESTOES_NAO_RECONHECIDAS", title: "Nenhum limite de questão foi reconhecido", action: "Use títulos como ‘Questão (1)_P1_UA (1)_Obj (1)_Fácil’ e marque cada opção como A), B), C) e D)."
    };
    else if (/não contém parágrafos reconhecíveis/i.test(message)) issue = {
      ...issue, code: "ARQUIVO.SEM_TEXTO_RECONHECIVEL", title: "O DOCX não contém texto em parágrafos reconhecíveis", action: "Se o documento for composto por imagens, faça OCR ou cole o texto em parágrafos do Word antes de importar."
    };
    const fullIssue = {
      ...issue, severity: "blocking", category: "file", overridable: false,
      questionIndex: null, questionNumber: null, questionName: "Arquivo", source: null, excerpt: "",
      technicalDetail: message
    };
    return {
      schemaVersion: FILE_DIAGNOSTIC_VERSION,
      parserVersion: "",
      generatedAt: new Date().toISOString(),
      fileName: file?.name || "arquivo sem nome",
      fileSize: Number(file?.size || 0),
      fileType: file?.type || "",
      status: "blocked",
      scope: "Falha de abertura ou reconhecimento do DOCX.",
      summary: { questions: 0, validQuestions: 0, blockedQuestions: 0, reviewQuestions: 0, duplicateQuestions: 0, actionable: 1, blocking: 1, review: 0, warning: 0, info: 0 },
      issues: [fullIssue]
    };
  }

  function summarizeParsed(parsed) {
    const questions = parsed.questions || [];
    questions.forEach((question) => {
      question.warnings = (question.warnings || []).filter((warning) => !/ocorr[eê]ncia\(s\).*caracteres Unicode.*preservad/i.test(warning));
    });
    auditDuplicates(questions);
    parsed.questionCount = questions.length;
    let discursiveOrdinal = 0;
    questions.forEach(question => {
      question.discursiveOrdinal = question.questionFormat === "discursive" ? ++discursiveOrdinal : null;
      question.suggestedTagLabel = question.discursiveOrdinal && question.discursiveOrdinal <= 2
        ? `Discursiva ${/^PS$/i.test(question.assessment || '') ? 'PS ' : ''}${question.discursiveOrdinal}` : '';
    });
    parsed.errors = questions.flatMap((question) => question.hardErrors.map((error) => `Questão ${question.number}: ${error}`));
    parsed.reviewIssues = questions.flatMap((question) => question.reviewBlocks.map((issue) => `Questão ${question.number}: ${issue}`));
    parsed.warnings = questions.flatMap((question) => question.warnings.map((warning) => `Questão ${question.number}: ${warning}`));
    parsed.autoReady = questions.length > 0 && questions.every((question) => question.autoApproved);
    parsed.executableCount = questions.filter((question) => question.executable).length;
    parsed.validQuestionCount = parsed.executableCount;
    parsed.reviewCount = questions.filter((question) => question.needsReview && question.executable).length;
    parsed.blockedCount = questions.filter((question) => !question.executable).length;
    parsed.duplicateQuestionCount = questions.filter((question) => Boolean(question.duplicateOf)).length;
    parsed.similarQuestionCount = questions.filter((question) => Boolean(question.nearDuplicateOf)).length;
    parsed.uniqueQuestionCount = new Set(questions.map((question) => question.duplicateFingerprint || question.fingerprint)).size;
    const objectiveQuestions = questions.filter((question) => (question.questionFormat || detectQuestionFormat(question)) !== "discursive");
    parsed.answerDistribution = objectiveQuestions.reduce((counts, question) => {
      if (Object.prototype.hasOwnProperty.call(counts, question.correctLetter)) counts[question.correctLetter] += 1;
      return counts;
    }, { A: 0, B: 0, C: 0, D: 0 });
    const dominantAnswer = Object.entries(parsed.answerDistribution).sort((left, right) => right[1] - left[1])[0] || ["", 0];
    parsed.answerDistributionWarning = objectiveQuestions.length >= 4 && dominantAnswer[1] / objectiveQuestions.length >= 0.7
      ? `O gabarito está concentrado em ${dominantAnswer[0]} (${dominantAnswer[1]} de ${objectiveQuestions.length} objetivas). Isto não bloqueia o lote, mas merece conferência pedagógica.`
      : "";
    if (parsed.answerDistributionWarning) parsed.warnings.push(`Lote: ${parsed.answerDistributionWarning}`);
    const engine = window.AvaliaBatchEngine;
    parsed.fileFingerprint = engine ? engine.fileFingerprint(parsed) : normalizeForMatch(questions.map((question) => question.fingerprint).join("|"));
    parsed.fileDiagnostics = buildFileDiagnostics(parsed);
    return parsed;
  }

  // Only explicit identification blocks are normalized; equations/commands are untouched.
  function normalizeIdentificationBlocks(records) {
    let identification = false;
    return records.map(record => {
      if (/^Identifica[cç][aã]o da quest[aã]o\s*[:.]?$/i.test(record.plain)) identification = true;
      else if (parseHeader(record)) identification = false;
      if (!identification) return record;
      let value = record.plain;
      const objective = value.match(/^OB(?:J)?\s*(\d+)\s*[:.\-]\s*(.+)$/i);
      const ua = value.match(/^UA\s*(\d+)\s*[:.\-]\s*(.+)$/i);
      if (objective) value = `Objetivo: OB${objective[1]}: ${objective[2]}`;
      else if (ua) value = `UA: ${ua[1]} — ${ua[2]}`;
      else if (/^(?:F[aá]cil|M[eé]di[oa]|Dif[ií]cil|Aplicad[ao])\s*$/i.test(value)) value = `Dificuldade: ${value}`;
      return value === record.plain ? record : {...record, plain:value, html:escapeHtml(value)};
    });
  }

  function separateSolutionAppendices(groups) {
    // A consecutive answer-key table is metadata, never the final distractor/feedback.
    const keyRecords=groups.flatMap(g=>g.records).filter(r=>/^\d{1,3}\s*[–—-]\s*[A-E]\s*$/i.test(r.plain));
    const keys=keyRecords.map(r=>({record:r,owner:groups.find(g=>g.records.includes(r)),match:r.plain.match(/^(\d+)\s*[–—-]\s*([A-E])\s*$/i)}));
    const answerKey=keys.length>=2 && keys.every((x,i)=>Number(x.match[1])===i+1) && keys.length===new Set(groups.map(g=>g.header.number)).size ? keys : [];
    const removed=new Set(answerKey.map(x=>x.record));
    if(removed.size) for(const g of groups) g.records=g.records.filter(r=>!removed.has(r));
    const result=[];
    const complete = records => records.some((r,i)=>alternativeRecord(r)?.letter==='A' && hasAlternativeCycle(records,i,records.length));
    const explanatory = records => {
      const text=normalizeForMatch(records.map(r=>r.plain).join(' '));
      return /^para (?:calcular|determinar|resolver|encontrar)\b/.test(text)
        && /\b(?:podemos|voce (?:deve|pode)|primeiro|substituindo)\b/.test(text)
        && /\b(?:portanto|agora|isso nos da|resultado)\b/.test(text);
    };
    const label = record => ({...record,plain:`Feedback: ${record.plain}`,html:`Feedback: ${record.html||escapeHtml(record.plain)}`});
    for (const group of groups) {
      const prior=result.filter(g=>g.header.number===group.header.number && (g.header.assessment||'')===(group.header.assessment||'') && complete(g.records));
      if (prior.length===1 && !group.header.inlineBody && !/discursiv/i.test(group.header.name)
          && !group.records.some(alternativeRecord) && explanatory(group.records)) {
        const first={...label(group.records[0]),segmentationWarning:'Resolução com número repetido foi associada ao feedback da questão. Confira a associação e o gabarito antes de enviar.'};
        prior[0].records.push(first,...group.records.slice(1));
        continue;
      }
      const lastOption=group.records.map((r,i)=>alternativeRecord(r)?i:-1).filter(i=>i>=0).at(-1);
      if(lastOption!==undefined && complete(group.records)) {
        for(let i=lastOption+1;i<group.records.length;i++) {
          const tail=group.records.slice(i);
          if(explanatory(tail)) {
            group.records[i]={...label(group.records[i]),segmentationWarning:'Texto de resolução após as alternativas foi separado como feedback. Confira a separação e a correção matemática.'};
            break;
          }
        }
      }
      result.push(group);
    }
    for(const entry of answerKey) {
      const targets=result.filter(g=>g.header.number===Number(entry.match[1]));
      if(targets.length!==1) {entry.owner.records.push({...entry.record,segmentationWarning:'A tabela de gabaritos tem numeração ambígua; confirme a qual questão pertence.'});continue;}
      const target=targets[0],existing=target.records.filter(r=>LABELS.answer.test(r.plain));
      const answer={...entry.record,plain:`Gabarito: ${entry.match[2].toUpperCase()}`,html:`Gabarito: ${entry.match[2].toUpperCase()}`};
      if(existing.length) answer.segmentationWarning='O arquivo possui gabarito individual e tabela de gabaritos. Confira se os dois concordam.';
      target.records.push(answer);
    }
    return result;
  }

  function parseDocumentXml(xmlText, fileName, numberingXml, mediaMap) {
    const sourceRecords = decorateAutomaticLists(documentParagraphs(xmlText, mediaMap), numberingXml || "");
    const indexEntries=[];
    const filteredRecords = sourceRecords.filter(r=>{
      const m=r.plain.match(/^Quest[aã]o\s*(?:n[º°o.]?\s*)?0*(\d+)\s*:\s*UA\s*0*(\d+)\s*[–—-]\s*Objetivo\s*:\s*(.*?)\s*\(OBJ\s*(\d+|Geral)\)\s*$/i);
      if(m){indexEntries.push({number:Number(m[1]),ua:String(Number(m[2])),objective:m[3],objectiveNumber:/^\d+$/.test(m[4])?String(Number(m[4])):"",sourceIndex:r.sourceIndex});return false;}
      return !/^Com base nas informa[cç][oõ]es fornecidas.*(?:preparei uma nova quest[aã]o|segue a identifica[cç][aã]o)/i.test(r.plain);
    });
    const records = normalizeIdentificationBlocks(filteredRecords).flatMap(expandStructuralRecords);
    const groups = separateSolutionAppendices(splitQuestions(records));
    if (!groups.length) throw new Error("Nenhuma questão foi reconhecida. Use títulos como ‘Questão 1’ ou mantenha um conjunto A–D para cada enunciado.");
    const subjectHint = subjectHintFromFileName(fileName);
    const questions = groups.map((group) => {
      const question = extractQuestion(group.header, group.records, group.sourceInfo);
      const entries=indexEntries.filter(e=>e.number===question.number);
      if(entries.length===1 && groups.filter(g=>g.header.number===question.number).length===1){
        const e=entries[0];
        if(question.ua && question.ua!==e.ua)question.segmentationWarnings.push("A UA do apêndice diverge da identificação da questão. Corrija a identificação no Word.");
        if(question.objectiveNumber && e.objectiveNumber && question.objectiveNumber!==e.objectiveNumber)question.segmentationWarnings.push("O objetivo do apêndice diverge da identificação da questão. Confirme o objetivo no Word.");
        if(!question.ua)question.ua=e.ua;
        if(!question.objectiveNumber)question.objectiveNumber=e.objectiveNumber;
        if(!question.objective)question.objective=e.objective;
        question.fieldMap.push({field:"Identificação complementar (UA / objetivo)",start:e.sourceIndex,end:e.sourceIndex});
      }
      finalizeQuestion(question);
      question.subjectHint = subjectHint;
      question.allocationAudit = { status: "unknown", score: 0, selectedDiscipline: "", subjectHint, reason: "Aguardando a disciplina selecionada no AvaliA.", matchedTerms: [], missingTerms: subjectTokens(subjectHint) };
      return question;
    });
    questions.forEach((question) => {
      question.errors = [...question.hardErrors];
      question.executable = question.hardErrors.length === 0;
      question.needsReview = Boolean(question.hardErrors.length || question.reviewBlocks.length || question.confidence < REVIEW_THRESHOLD);
      question.autoApproved = question.executable && !question.needsReview;
    });
    return summarizeParsed({ parserVersion: "11.0", fileName: fileName || "avaliação.docx", subjectHint, questions, requiredAlternatives: REQUIRED_ALTERNATIVES, reviewThreshold: REVIEW_THRESHOLD, sourceParagraphCount: records[records.length - 1]?.sourceIndex || records.length });
  }

  function reevaluateQuestion(question, settings) {
    return finalizeQuestion(JSON.parse(JSON.stringify(question)), settings || {});
  }

  function normalizeZipPath(target) {
    const initial = String(target || "").replace(/^\//, "").split("/");
    const parts = String(target || "").startsWith("/") ? [] : ["word"];
    initial.forEach((part) => {
      if (!part || part === ".") return;
      if (part === "..") parts.pop();
      else parts.push(part);
    });
    return parts.join("/");
  }

  async function loadDocumentMedia(zip, relsXml) {
    const relationships = relationshipMap(relsXml);
    const result = new Map();
    let totalBytes = 0;
    for (const [relationshipId, target] of relationships.entries()) {
      const path = normalizeZipPath(target);
      const entry = zip.file(path);
      const name = path.split("/").pop() || relationshipId;
      const extension = (name.match(/\.([^.]+)$/)?.[1] || "").toLowerCase();
      if (!entry) {
        result.set(relationshipId, { relationshipId, path, name, extension, resolved: false, supported: false, hash: hashValue(`${relationshipId}:${path}`), reason: "Arquivo de mídia ausente no pacote DOCX." });
        continue;
      }
      const base64 = await entry.async("base64");
      const estimatedBytes = Math.floor(base64.length * 0.75);
      totalBytes += estimatedBytes;
      const supportedFormat = SUPPORTED_IMAGE_TYPES.has(extension);
      const withinLimit = estimatedBytes <= 12 * 1024 * 1024 && totalBytes <= 40 * 1024 * 1024;
      const hash = hashValue(base64);
      result.set(relationshipId, {
        relationshipId, path, name, extension, mime: mediaMime(extension), hash,
        size: estimatedBytes, resolved: true, supported: supportedFormat && withinLimit,
        reason: !supportedFormat ? "Formato de imagem não renderizável no navegador." : !withinLimit ? "Imagem ou conjunto de imagens acima do limite seguro de 12 MB por arquivo e 40 MB por DOCX." : "",
        dataUrl: supportedFormat && withinLimit ? `data:${mediaMime(extension)};base64,${base64}` : ""
      });
    }
    return result;
  }

  async function parse(file) {
    if (!file || !/\.docx$/i.test(file.name || "")) throw new Error("Selecione um arquivo com extensão .docx.");
    if (typeof JSZip === "undefined") throw new Error("O leitor de DOCX não foi carregado.");
    const zip = await JSZip.loadAsync(await file.arrayBuffer());
    const documentEntry = zip.file("word/document.xml");
    if (!documentEntry) throw new Error("O arquivo não contém word/document.xml e pode não ser um DOCX válido.");
    const numberingEntry = zip.file("word/numbering.xml");
    const relsEntry = zip.file("word/_rels/document.xml.rels");
    const [documentXml, numberingXml, relsXml] = await Promise.all([
      documentEntry.async("string"),
      numberingEntry ? numberingEntry.async("string") : Promise.resolve(""),
      relsEntry ? relsEntry.async("string") : Promise.resolve("")
    ]);
    const mediaMap = await loadDocumentMedia(zip, relsXml);
    return parseDocumentXml(documentXml, file.name, numberingXml, mediaMap);
  }

  window.AvaliaDocxParser = Object.freeze({
    parse, parseDocumentXml, parseHeader, classifyQuestionType,
    typeFromDescription: (description, bodyText, alternatives) => classifyQuestionType(description, bodyText, alternatives || []),
    cognitiveFromObjective, textualAudit, reevaluateQuestion, summarizeParsed,
    technicalIssues, questionDiagnosticIssues, buildFileDiagnostics, importFailureDiagnostic,
    assessAllocation, subjectHintFromFileName, computeRichIntegrity, specialCharacterInventory, textToHtml, formatArithmeticText,
    typeCatalog: TYPE_CATALOG, cognitiveCatalog: COGNITIVE_CATALOG,
    requiredAlternatives: REQUIRED_ALTERNATIVES, reviewThreshold: REVIEW_THRESHOLD, fileDiagnosticVersion: FILE_DIAGNOSTIC_VERSION
  });
})();
