#!/usr/bin/env python3
"""
Script gerador de ícones SVG e PNG/ICO para AVALIA AutoBatch
"""
import os
import subprocess
from PIL import Image

ASSETS_DIR = "/home/hamilcar/Antigravity/automacao_avalia_autobatch/assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

SVG_CONCEPT_1 = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <!-- Filtros de Sombra e Brilho -->
    <filter id="squircleShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="16" stdDeviation="20" flood-color="#05070f" flood-opacity="0.8"/>
      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="#3b82f6" flood-opacity="0.25"/>
    </filter>

    <filter id="cardShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="12" stdDeviation="14" flood-color="#000000" flood-opacity="0.6"/>
      <feDropShadow dx="0" dy="0" stdDeviation="8" flood-color="#38bdf8" flood-opacity="0.15"/>
    </filter>

    <filter id="boltGlow" x="-40%" y="-40%" width="180%" height="180%">
      <feDropShadow dx="0" dy="0" stdDeviation="10" flood-color="#fbbf24" flood-opacity="0.7"/>
      <feDropShadow dx="0" dy="8" stdDeviation="16" flood-color="#f59e0b" flood-opacity="0.5"/>
    </filter>

    <filter id="checkGlow" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="0" stdDeviation="6" flood-color="#10b981" flood-opacity="0.8"/>
    </filter>

    <!-- Gradientes de Fundo -->
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#181a29"/>
      <stop offset="40%" stop-color="#11131f"/>
      <stop offset="100%" stop-color="#0b0c14"/>
    </linearGradient>

    <linearGradient id="borderGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#60a5fa" stop-opacity="0.8"/>
      <stop offset="35%" stop-color="#3b82f6" stop-opacity="0.4"/>
      <stop offset="70%" stop-color="#1e293b" stop-opacity="0.2"/>
      <stop offset="100%" stop-color="#475569" stop-opacity="0.5"/>
    </linearGradient>

    <!-- Gradiente de Iluminação Ambiente (Aura central) -->
    <radialGradient id="ambientCyan" cx="50%" cy="40%" r="55%">
      <stop offset="0%" stop-color="#0284c7" stop-opacity="0.3"/>
      <stop offset="60%" stop-color="#3b82f6" stop-opacity="0.1"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
    </radialGradient>

    <!-- Gradiente do Card de Questão -->
    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#23273d"/>
      <stop offset="100%" stop-color="#151726"/>
    </linearGradient>

    <linearGradient id="cardBorder" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#89b4fa" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="#313244" stop-opacity="0.4"/>
    </linearGradient>

    <!-- Gradiente do Monograma 'A' / Badge do Topo -->
    <linearGradient id="badgeAGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="100%" stop-color="#2563eb"/>
    </linearGradient>

    <!-- Gradiente do Raio Turbo -->
    <linearGradient id="boltGradFront" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fffbeb"/>
      <stop offset="25%" stop-color="#fef08a"/>
      <stop offset="70%" stop-color="#f59e0b"/>
      <stop offset="100%" stop-color="#d97706"/>
    </linearGradient>

    <linearGradient id="boltGradBevel" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#d97706"/>
      <stop offset="100%" stop-color="#9a3412"/>
    </linearGradient>

    <!-- Gradiente da Alternativa Correta Selecionada -->
    <linearGradient id="correctRowGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#064e3b" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#065f46" stop-opacity="0.2"/>
    </linearGradient>

    <linearGradient id="emeraldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#34d399"/>
      <stop offset="100%" stop-color="#059669"/>
    </linearGradient>
  </defs>

  <!-- 1. BASE SQUIRCLE COM SOMBRA E BORDA CHANFRADA -->
  <rect x="32" y="32" width="448" height="448" rx="104" ry="104" 
        fill="url(#bgGrad)" filter="url(#squircleShadow)"/>
  
  <!-- Aura de luz ambiente interna -->
  <rect x="32" y="32" width="448" height="448" rx="104" ry="104" 
        fill="url(#ambientCyan)"/>

  <!-- Borda sutil de vidro acrílico -->
  <rect x="32" y="32" width="448" height="448" rx="104" ry="104" 
        fill="none" stroke="url(#borderGrad)" stroke-width="3"/>

  <!-- Brilho de reflexo especular no topo do squircle -->
  <path d="M 136 34 C 74 34, 34 74, 34 136 C 34 82, 80 37, 136 37 L 376 37 C 432 37, 478 82, 478 136 C 478 74, 438 34, 376 34 Z" 
        fill="#ffffff" opacity="0.12"/>

  <!-- 2. CARD PRINCIPAL DA QUESTÃO (FLUTUANTE COM VIDRO ESCURO) -->
  <g filter="url(#cardShadow)">
    <rect x="88" y="80" width="336" height="344" rx="28" ry="28" 
          fill="url(#cardGrad)" stroke="url(#cardBorder)" stroke-width="2"/>
    
    <!-- Reflexo especular superior do card -->
    <path d="M 116 82 L 396 82 C 410 82, 421 93, 422 107 L 422 110 C 420 97, 408 86, 396 86 L 116 86 C 104 86, 92 97, 90 110 L 90 107 C 91 93, 102 82, 116 82 Z" 
          fill="#ffffff" opacity="0.18"/>

    <!-- CABEÇALHO DO CARD -->
    <!-- Badge 'A' do AVALIA / Grupo A -->
    <rect x="114" y="106" width="38" height="38" rx="11" ry="11" fill="url(#badgeAGrad)"/>
    <text x="133" y="133" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" 
          font-weight="900" font-size="22" fill="#ffffff" text-anchor="middle">A</text>

    <!-- Título do Header / Código da Questão -->
    <rect x="164" y="113" width="112" height="11" rx="5.5" fill="#cdd6f4" opacity="0.9"/>
    <rect x="164" y="131" width="70" height="7" rx="3.5" fill="#89b4fa" opacity="0.7"/>

    <!-- Pill de Status 'AUTO' no topo direito -->
    <rect x="330" y="112" width="70" height="24" rx="12" fill="#313244" stroke="#45475a" stroke-width="1.5"/>
    <circle cx="343" cy="124" r="4" fill="#10b981"/>
    <text x="372" y="129" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" 
          font-weight="800" font-size="10" fill="#a6e3a1" text-anchor="middle" letter-spacing="1">BATCH</text>

    <!-- Linha divisória sutil -->
    <line x1="114" y1="160" x2="398" y2="160" stroke="#313244" stroke-width="1.5"/>

    <!-- ENUNCIADO DA QUESTÃO (Barras de Texto) -->
    <rect x="114" y="178" width="280" height="9" rx="4.5" fill="#a6adc8" opacity="0.75"/>
    <rect x="114" y="195" width="240" height="9" rx="4.5" fill="#a6adc8" opacity="0.55"/>
    <rect x="114" y="212" width="170" height="9" rx="4.5" fill="#a6adc8" opacity="0.4"/>

    <!-- ALTERNATIVAS DE RESPOSTA -->
    <!-- Alternativa A -->
    <circle cx="127" cy="245" r="9" fill="none" stroke="#6c7086" stroke-width="2"/>
    <text x="127" y="249" font-family="'Segoe UI', Roboto, sans-serif" font-weight="700" font-size="10" fill="#6c7086" text-anchor="middle">A</text>
    <rect x="146" y="241" width="160" height="8" rx="4" fill="#6c7086" opacity="0.5"/>

    <!-- Alternativa B (CORRETA - SELECIONADA PELO AUTOMATION) -->
    <rect x="112" y="263" width="220" height="32" rx="10" fill="url(#correctRowGrad)" stroke="#10b981" stroke-width="1.5"/>
    <circle cx="127" cy="279" r="10" fill="url(#emeraldGrad)" filter="url(#checkGlow)"/>
    <!-- Checkmark icon -->
    <path d="M 122 279 L 125.5 282.5 L 132.5 274.5" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
    <!-- Texto da Alternativa B -->
    <rect x="146" y="275" width="170" height="8" rx="4" fill="#a6e3a1"/>

    <!-- Alternativa C -->
    <circle cx="127" cy="313" r="9" fill="none" stroke="#6c7086" stroke-width="2"/>
    <text x="127" y="317" font-family="'Segoe UI', Roboto, sans-serif" font-weight="700" font-size="10" fill="#6c7086" text-anchor="middle">C</text>
    <rect x="146" y="309" width="130" height="8" rx="4" fill="#6c7086" opacity="0.5"/>

    <!-- Alternativa D -->
    <circle cx="127" cy="347" r="9" fill="none" stroke="#6c7086" stroke-width="2"/>
    <text x="127" y="351" font-family="'Segoe UI', Roboto, sans-serif" font-weight="700" font-size="10" fill="#6c7086" text-anchor="middle">D</text>
    <rect x="146" y="343" width="100" height="8" rx="4" fill="#6c7086" opacity="0.5"/>

    <!-- Rodapé do Card: Contador de Questões Cadastradas -->
    <rect x="114" y="378" width="140" height="18" rx="9" fill="#181825"/>
    <text x="184" y="391" font-family="'Segoe UI', Roboto, sans-serif" font-weight="700" font-size="10" fill="#89b4fa" text-anchor="middle">QUESTÃO #01 / 25</text>
  </g>

  <!-- 3. ELEMENTO HERO DE AUTOMAÇÃO E VELOCIDADE: RAIO 3D TURBO (AUTOBATCH) -->
  <g filter="url(#boltGlow)">
    <!-- Trilhas / Dash de velocidade -->
    <rect x="250" y="375" width="55" height="5" rx="2.5" fill="#38bdf8" opacity="0.7"/>
    <rect x="280" y="388" width="40" height="5" rx="2.5" fill="#f59e0b" opacity="0.8"/>
    <rect x="235" y="401" width="70" height="5" rx="2.5" fill="#fbbf24" opacity="0.6"/>

    <!-- Sombra chanfrada 3D do Raio -->
    <polygon points="398,172 318,318 376,322 334,444 446,282 384,278" 
             fill="url(#boltGradBevel)"/>

    <!-- Face frontal iluminada do Raio -->
    <polygon points="390,166 312,312 370,316 332,434 438,278 376,274" 
             fill="url(#boltGradFront)"/>

    <!-- Brilho especular no vértice do raio -->
    <polygon points="390,166 350,240 376,274" 
             fill="#ffffff" opacity="0.45"/>
  </g>
</svg>
"""

SVG_CONCEPT_2 = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <filter id="shadowC2" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="16" stdDeviation="22" flood-color="#020617" flood-opacity="0.85"/>
      <feDropShadow dx="0" dy="4" stdDeviation="10" flood-color="#6366f1" flood-opacity="0.3"/>
    </filter>

    <filter id="glowC2" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="0" stdDeviation="12" flood-color="#38bdf8" flood-opacity="0.6"/>
    </filter>

    <linearGradient id="bgGrad2" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e1b4b"/>
      <stop offset="45%" stop-color="#0f172a"/>
      <stop offset="100%" stop-color="#020617"/>
    </linearGradient>

    <linearGradient id="neonCyan" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="100%" stop-color="#2563eb"/>
    </linearGradient>

    <linearGradient id="neonGreen" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#4ade80"/>
      <stop offset="100%" stop-color="#059669"/>
    </linearGradient>

    <linearGradient id="goldGrad2" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fde047"/>
      <stop offset="100%" stop-color="#ea580c"/>
    </linearGradient>
  </defs>

  <!-- Squircle Base -->
  <rect x="32" y="32" width="448" height="448" rx="104" ry="104" 
        fill="url(#bgGrad2)" filter="url(#shadowC2)" stroke="#38bdf8" stroke-width="2.5" stroke-opacity="0.6"/>

  <!-- Halo Central -->
  <circle cx="256" cy="256" r="160" fill="#38bdf8" opacity="0.08"/>

  <!-- Órbita de Automação / Loop de Questões -->
  <path d="M 120 256 A 136 136 0 1 1 392 256" fill="none" stroke="#6366f1" stroke-width="8" stroke-linecap="round" stroke-dasharray="16 12" opacity="0.6"/>
  <path d="M 392 256 A 136 136 0 0 1 120 256" fill="none" stroke="#38bdf8" stroke-width="8" stroke-linecap="round" stroke-dasharray="8 8" opacity="0.8"/>

  <!-- Folha de Exame Central Estilizada -->
  <rect x="146" y="116" width="220" height="280" rx="20" fill="#1e293b" stroke="#475569" stroke-width="2" filter="url(#glowC2)"/>

  <!-- Monograma A estilizado em 3D como torre de lançamento -->
  <path d="M 256 145 L 320 290 L 285 290 L 273 262 L 239 262 L 227 290 L 192 290 Z M 256 210 L 246 238 L 266 238 Z" 
        fill="url(#neonCyan)"/>

  <!-- Badge de Conclusão / Check de Validação -->
  <circle cx="256" cy="340" r="32" fill="url(#neonGreen)"/>
  <path d="M 244 340 L 252 348 L 268 332" fill="none" stroke="#ffffff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>

  <!-- Mini Raio Turbo Acoplado -->
  <polygon points="340,110 295,190 325,193 300,260 365,170 330,167" fill="url(#goldGrad2)"/>
</svg>
"""

# Salva os arquivos SVG
svg_path_1 = os.path.join(ASSETS_DIR, "icon.svg")
svg_path_concept1 = os.path.join(ASSETS_DIR, "icon_concept_sheet.svg")
svg_path_concept2 = os.path.join(ASSETS_DIR, "icon_concept_badge.svg")

with open(svg_path_1, "w", encoding="utf-8") as f:
    f.write(SVG_CONCEPT_1)

with open(svg_path_concept1, "w", encoding="utf-8") as f:
    f.write(SVG_CONCEPT_1)

with open(svg_path_concept2, "w", encoding="utf-8") as f:
    f.write(SVG_CONCEPT_2)

print(f"SVG criado com sucesso em: {svg_path_1}")

# Exporta tamanhos PNG usando Inkscape para máxima fidelidade e anti-aliasing
sizes = [512, 256, 128, 64, 48, 32, 16]
png_files = []

for s in sizes:
    png_out = os.path.join(ASSETS_DIR, f"icon_{s}x{s}.png")
    cmd = ["inkscape", "-w", str(s), "-h", str(s), svg_path_1, "-o", png_out]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    png_files.append(png_out)
    print(f"Gerado PNG: {png_out}")

# Cria icon.png padrão (512x512)
icon_png_main = os.path.join(ASSETS_DIR, "icon.png")
subprocess.run(["cp", os.path.join(ASSETS_DIR, "icon_512x512.png"), icon_png_main], check=True)

# Gera o arquivo Windows ICO multi-resolução
ico_out = os.path.join(ASSETS_DIR, "icon.ico")
img_256 = Image.open(os.path.join(ASSETS_DIR, "icon_256x256.png"))
ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
img_256.save(ico_out, format="ICO", sizes=ico_sizes)
print(f"Gerado Windows ICO multi-resolução: {ico_out}")

# Também gera PNG do Concept 2 para visualização
cmd_c2 = ["inkscape", "-w", "512", "-h", "512", svg_path_concept2, "-o", os.path.join(ASSETS_DIR, "icon_concept_badge_512.png")]
subprocess.run(cmd_c2, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("Ícones gerados com sucesso total!")
