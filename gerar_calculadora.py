#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador da CALCULADORA DE PEPTÍDEOS.

Uso:
    python gerar_calculadora.py                 # gera calculadora.html e abre no navegador
    python gerar_calculadora.py --no-open       # só gera o arquivo
    python gerar_calculadora.py -o saida.html --whatsapp 5511999999999

O arquivo gerado é uma página única (HTML + CSS + JS embutidos), sem dependências externas
e usa apenas fontes do sistema.
"""

import argparse
import json
import webbrowser
from pathlib import Path

# ─────────────────────────── CONFIGURAÇÃO ───────────────────────────
CONFIG = {
    # Opções exibidas nos botões
    "doses_mcg": [100, 150, 200, 250, 300, 400, 500, 600, 750, 1000],
    "doses_mg": [1, 1.5, 2, 2.5, 3, 4, 5, 7.5, 10],
    "frascos_mg": [2, 5, 10, 15, 20, 30, 50, 100, 500],
    "diluentes_ml": [0.5, 1, 1.5, 2, 2.5, 3, 4, 5],
    "seringas": [
        {"ml": 0.3, "u": 30, "lab": "0,3 ml (30 UI)"},
        {"ml": 0.5, "u": 50, "lab": "0,5 ml (50 UI)"},
        {"ml": 1, "u": 100, "lab": "1 ml (100 UI)"},
    ],
    # Estado inicial (igual ao print)
    "estado_inicial": {"unit": "mcg", "dose": 250, "vial": 10, "dil": 2, "syr": 1},
    # Links
    "whatsapp": "5500000000000",
    "guia_pdf": "reconstituicao/1.pdf",
    "titulo": "Calculadora de Peptídeos",
}

# ─────────────────────────── TEMPLATE HTML ───────────────────────────
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>__TITULO__</title>
<style>
:root{
  --red:#e10600;
  --mono:ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono','DejaVu Sans Mono',monospace;
  --sans:system-ui,-apple-system,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  min-height:100vh;color:#fff;font-family:var(--sans);
  background:#0a0a0a radial-gradient(ellipse 80% 40% at 50% 0%,rgba(225,6,0,.10),transparent 70%) no-repeat;
  padding:20px 0;
}

/* ══════════ CALCULADORA DE PEPTÍDEOS ══════════ */
.calc-wrap{max-width:1100px;margin:26px auto 6px;padding:0 14px}
.calc-card{background:linear-gradient(180deg,rgba(255,255,255,.045),rgba(255,255,255,.015));
  border:1px solid rgba(255,255,255,.10);border-radius:20px;padding:20px 16px;position:relative;overflow:hidden}
.calc-card::before{content:"";position:absolute;inset:0;pointer-events:none;
  background:radial-gradient(ellipse 90% 55% at 50% 0%,rgba(225,6,0,.20),transparent 62%)}
.calc-card h2{position:relative;font-size:1.35rem;font-weight:900;letter-spacing:.02em;text-align:center;margin:0 0 4px}
.calc-card h2 span{color:var(--red)}
.calc-sub{position:relative;text-align:center;font-family:var(--mono);font-size:.68rem;letter-spacing:.18em;
  text-transform:uppercase;color:rgba(255,255,255,.55);margin-bottom:16px}
.calc-grid{position:relative;display:grid;gap:16px}
@media(min-width:900px){.calc-grid{grid-template-columns:1.05fr .95fr;align-items:start}}
.calc-step{margin-bottom:14px}
.calc-step-t{font-family:var(--mono);font-size:.66rem;letter-spacing:.16em;text-transform:uppercase;
  color:rgba(255,255,255,.6);margin-bottom:8px;display:flex;align-items:center;gap:8px}
.calc-step-t b{display:grid;place-items:center;width:20px;height:20px;border-radius:50%;
  background:var(--red);color:#fff;font-size:.62rem}
.calc-opts{display:flex;flex-wrap:wrap;gap:8px}
.calc-opt{padding:9px 13px;border-radius:999px;cursor:pointer;font-family:var(--mono);font-size:.72rem;
  letter-spacing:.06em;color:rgba(255,255,255,.8);background:rgba(255,255,255,.04);
  border:1px solid rgba(255,255,255,.12);transition:all .2s;white-space:nowrap;text-decoration:none;
  display:inline-block;line-height:1.2}
.calc-opt:hover{color:#fff;border-color:rgba(255,255,255,.35);transform:translateY(-1px)}
.calc-opt.active{background:var(--red);border-color:var(--red);color:#fff;font-weight:700;
  box-shadow:0 0 18px rgba(225,6,0,.45)}
.calc-custom{display:flex;align-items:center;gap:6px;background:rgba(255,255,255,.04);
  border:1px solid rgba(255,255,255,.12);border-radius:999px;padding:4px 10px}
.calc-custom input{width:70px;background:transparent;border:0;color:#fff;font-family:var(--mono);
  font-size:.75rem;outline:none;text-align:center}
.calc-custom input::placeholder{color:rgba(255,255,255,.4)}
.calc-custom span{font-family:var(--mono);font-size:.62rem;color:rgba(255,255,255,.5)}
.calc-res{background:rgba(0,0,0,.35);border:1px solid rgba(255,255,255,.10);border-radius:16px;padding:16px}
.calc-big{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:14px}
.calc-big div{flex:1 1 120px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.10);
  border-radius:12px;padding:10px 12px}
.calc-big small{display:block;font-family:var(--mono);font-size:.58rem;letter-spacing:.14em;
  text-transform:uppercase;color:rgba(255,255,255,.5);margin-bottom:4px}
.calc-big b{font-size:1.3rem;font-weight:900;color:#fff}
.calc-big b em{font-style:normal;font-size:.75rem;color:rgba(255,255,255,.6);font-weight:600}
.syr{position:relative;margin:6px 0 4px}
.syr svg{width:100%;height:auto;display:block;overflow:visible}
.calc-note{font-size:.74rem;line-height:1.5;color:rgba(255,255,255,.6);margin-top:10px}
.calc-warn{margin-top:10px;font-size:.76rem;font-weight:700;color:#ffb4b0;background:rgba(225,6,0,.12);
  border:1px solid rgba(225,6,0,.35);border-radius:10px;padding:9px 11px}
.calc-actions{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
</style>
</head>
<body>

<!-- CALCULADORA DE PEPTÍDEOS -->
<section class="calc-wrap" id="calculadora">
  <div class="calc-card">
    <h2>CALCULADORA DE <span>PEPTÍDEOS</span></h2>
    <div class="calc-sub">Dose • Frasco • Diluente • Seringa</div>
    <div class="calc-grid">
      <div>
        <div class="calc-step">
          <div class="calc-step-t"><b>1</b> Dose desejada</div>
          <div class="calc-opts" id="calcDoseOpts"></div>
          <div class="calc-opts" style="margin-top:8px">
            <label class="calc-custom">
              <input id="calcDoseCustom" type="number" min="0" step="any" placeholder="outra"/>
              <span id="calcDoseUnit">mcg</span>
            </label>
            <button type="button" class="calc-opt" id="calcUnitMcg" onclick="calcSetUnit('mcg')">mcg</button>
            <button type="button" class="calc-opt" id="calcUnitMg" onclick="calcSetUnit('mg')">mg</button>
          </div>
        </div>
        <div class="calc-step">
          <div class="calc-step-t"><b>2</b> Volume / conteúdo do frasco (mg)</div>
          <div class="calc-opts" id="calcVialOpts"></div>
          <div class="calc-opts" style="margin-top:8px">
            <label class="calc-custom">
              <input id="calcVialCustom" type="number" min="0" step="any" placeholder="outro"/>
              <span>mg</span>
            </label>
          </div>
        </div>
        <div class="calc-step">
          <div class="calc-step-t"><b>3</b> Diluente adicionado (ml de água bacteriostática)</div>
          <div class="calc-opts" id="calcDilOpts"></div>
          <div class="calc-opts" style="margin-top:8px">
            <label class="calc-custom">
              <input id="calcDilCustom" type="number" min="0" step="any" placeholder="outro"/>
              <span>ml</span>
            </label>
          </div>
        </div>
        <div class="calc-step" style="margin-bottom:0">
          <div class="calc-step-t"><b>4</b> Seringa de insulina</div>
          <div class="calc-opts" id="calcSyrOpts"></div>
        </div>
      </div>
      <div class="calc-res">
        <div class="calc-big">
          <div class="hl"><small>Aplicar</small><b id="calcUI">—</b></div>
          <div><small>Volume</small><b id="calcML">—</b></div>
          <div><small>Concentração</small><b id="calcConc">—</b></div>
        </div>
        <div class="syr" id="calcSyr"></div>
        <div id="calcExtra" class="calc-note"></div>
        <div id="calcWarn"></div>
        <div class="calc-actions">
          <button type="button" class="calc-opt" onclick="calcReset()">↺ Limpar</button>
          <a class="calc-opt" href="__GUIA_PDF__" target="_blank" rel="noopener">💧 Guia de reconstituição</a>
          <a class="calc-opt" id="calcZap" href="#" target="_blank" rel="noopener">💬 Tirar dúvida</a>
        </div>
        <div class="calc-note">Cálculo de referência para uso em pesquisa. <b>1 ml = 100 UI</b> na seringa U-100. Confira sempre o rótulo do frasco.</div>
      </div>
    </div>
  </div>
</section>

<script>
const $ = id => document.getElementById(id);
const WHATSAPP_NUM = "__WHATSAPP__";

/* =====================================================================
   CALCULADORA DE PEPTÍDEOS
   ===================================================================== */
const CALC_DOSES_MCG = __DOSES_MCG__;
const CALC_DOSES_MG  = __DOSES_MG__;
const CALC_VIALS     = __FRASCOS__;
const CALC_DILS      = __DILUENTES__;
const CALC_SYRS      = __SERINGAS__;

const calcState = __ESTADO__;

function calcNum(v){ const n = parseFloat(String(v).replace(",", ".")); return isFinite(n) && n > 0 ? n : null; }
function calcFmt(n, d){
  return n.toLocaleString("pt-BR", { minimumFractionDigits:0, maximumFractionDigits:(d===undefined?2:d) });
}
function calcSetUnit(u){
  if (calcState.unit === u) return;
  const d = calcState.dose;
  calcState.unit = u;
  if (d != null) calcState.dose = (u === "mg") ? d/1000 : d*1000;
  $("calcDoseCustom").value = "";
  calcRender();
}
function calcPick(key, val){ calcState[key] = val;
  const map = { dose:"calcDoseCustom", vial:"calcVialCustom", dil:"calcDilCustom" };
  if (map[key]) $(map[key]).value = "";
  calcRender();
}
function calcReset(){
  Object.assign(calcState, __ESTADO__);
  ["calcDoseCustom","calcVialCustom","calcDilCustom"].forEach(i => { const e = $(i); if (e) e.value = ""; });
  calcRender();
}
function calcOptsHtml(list, key, fmt){
  return list.map(v => `<button type="button" class="calc-opt${calcState[key] === v ? " active":""}"
    onclick="calcPick('${key}',${v})">${fmt(v)}</button>`).join("");
}
function calcSyringeSvg(maxU, u){
  const W = 520, H = 96, x0 = 46, x1 = 470, yT = 30, hB = 30;
  const frac = maxU > 0 ? Math.max(0, Math.min(1, u / maxU)) : 0;
  const fw = (x1 - x0) * frac;
  const step = 1;
  let ticks = "";
  for (let t = 0; t <= maxU + 0.001; t += step){
    const x = x0 + (x1 - x0) * (t / maxU);
    const big = (t % 5 === 0) || t === maxU;
    ticks += `<line x1="${x.toFixed(1)}" y1="${yT}" x2="${x.toFixed(1)}" y2="${(yT + (big?11:7)).toFixed(1)}"
      stroke="rgba(255,255,255,${big?0.85:0.45})" stroke-width="${big?1.6:1}"/>`;
    if (big) ticks += `<text x="${x.toFixed(1)}" y="${yT-6}" fill="rgba(255,255,255,.7)" font-size="12"
      font-family="monospace" text-anchor="middle">${t}</text>`;
  }
  const mx = x0 + (x1 - x0) * frac;
  const marker = u > 0 ? `
    <line x1="${mx.toFixed(1)}" y1="${yT-16}" x2="${mx.toFixed(1)}" y2="${yT+hB+10}" stroke="#e10600" stroke-width="2"/>
    <circle cx="${mx.toFixed(1)}" cy="${yT+hB+14}" r="3.4" fill="#e10600"/>
    <text x="${Math.min(mx, x1-26).toFixed(1)}" y="${H-4}" fill="#ff6b66" font-size="12" font-weight="700"
      font-family="monospace" text-anchor="middle">${calcFmt(u,1)} UI</text>` : "";
  return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Seringa de insulina">
    <rect x="${x0-34}" y="${yT+hB/2-3}" width="34" height="6" rx="2" fill="rgba(255,255,255,.35)"/>
    <rect x="${x0-52}" y="${yT+hB/2-1.2}" width="20" height="2.4" fill="rgba(255,255,255,.55)"/>
    <rect x="${x0}" y="${yT}" width="${x1-x0}" height="${hB}" rx="6" fill="rgba(255,255,255,.06)"
      stroke="rgba(255,255,255,.28)"/>
    <rect x="${x0}" y="${yT}" width="${fw.toFixed(1)}" height="${hB}" rx="6" fill="rgba(225,6,0,.55)"/>
    <rect x="${(x0+fw).toFixed(1)}" y="${yT-4}" width="7" height="${hB+8}" rx="2" fill="rgba(255,255,255,.75)"/>
    <rect x="${x1}" y="${yT-6}" width="8" height="${hB+12}" rx="3" fill="rgba(255,255,255,.3)"/>
    <rect x="${x1+8}" y="${yT+hB/2-2.5}" width="34" height="5" rx="2" fill="rgba(255,255,255,.35)"/>
    ${ticks}${marker}
  </svg>`;
}
function calcRender(){
  const st = calcState;
  const doses = st.unit === "mg" ? CALC_DOSES_MG : CALC_DOSES_MCG;
  $("calcDoseOpts").innerHTML = calcOptsHtml(doses, "dose", v => `${calcFmt(v,2)} ${st.unit}`);
  $("calcVialOpts").innerHTML = calcOptsHtml(CALC_VIALS, "vial", v => `${calcFmt(v,2)} mg`);
  $("calcDilOpts").innerHTML  = calcOptsHtml(CALC_DILS, "dil", v => `${calcFmt(v,2)} ml`);
  $("calcSyrOpts").innerHTML  = CALC_SYRS.map(s => `<button type="button"
    class="calc-opt${st.syr === s.ml ? " active":""}" onclick="calcPick('syr',${s.ml})">${s.lab}</button>`).join("");
  $("calcDoseUnit").textContent = st.unit;
  $("calcUnitMcg").classList.toggle("active", st.unit === "mcg");
  $("calcUnitMg").classList.toggle("active", st.unit === "mg");

  const doseMg = st.dose == null ? null : (st.unit === "mg" ? st.dose : st.dose/1000);
  const vial = st.vial, dil = st.dil;
  const syr = CALC_SYRS.find(s => s.ml === st.syr) || CALC_SYRS[CALC_SYRS.length - 1];
  const ok = doseMg && vial && dil;
  if (!ok){
    $("calcUI").textContent = "—"; $("calcML").textContent = "—"; $("calcConc").textContent = "—";
    $("calcSyr").innerHTML = calcSyringeSvg(syr.u, 0);
    $("calcExtra").innerHTML = "Escolha a dose, o frasco e o diluente.";
    $("calcWarn").innerHTML = "";
    return;
  }
  const conc = vial / dil;               // mg/ml
  const ml   = doseMg / conc;            // ml por aplicação
  const ui   = ml * 100;                 // UI (seringa U-100)
  const aplic = Math.floor(vial / doseMg);

  $("calcConc").innerHTML = `${calcFmt(conc,2)} <em>mg/ml</em>`;
  $("calcML").innerHTML   = `${calcFmt(ml,3)} <em>ml</em>`;
  $("calcUI").innerHTML   = `${calcFmt(ui,1)} <em>UI</em>`;
  $("calcSyr").innerHTML  = calcSyringeSvg(syr.u, ui);
  $("calcExtra").innerHTML = `Frasco de <b>${calcFmt(vial,2)} mg</b> diluído em <b>${calcFmt(dil,2)} ml</b> → cada
    <b>${calcFmt(ui,1)} UI</b> (${calcFmt(ml,3)} ml) entrega <b>${st.unit === "mg" ? calcFmt(doseMg,3)+" mg" : calcFmt(doseMg*1000,0)+" mcg"}</b>.
    Rende aproximadamente <b>${aplic}</b> aplicaç${aplic === 1 ? "ão" : "ões"} por frasco.`;
  let w = "";
  if (ui > syr.u) w = `⚠ A dose ocupa ${calcFmt(ui,1)} UI e não cabe na seringa de ${syr.lab}. Use uma seringa maior, divida em 2 aplicações ou reduza o diluente.`;
  else if (ui < 2) w = `⚠ Volume muito pequeno (${calcFmt(ui,1)} UI) — difícil de medir com precisão. Use menos diluente.`;
  $("calcWarn").innerHTML = w ? `<div class="calc-warn">${w}</div>` : "";

  const zap = $("calcZap");
  if (zap) zap.href = `https://wa.me/${WHATSAPP_NUM}?text=` + encodeURIComponent(
    `Olá! Dúvida sobre reconstituição: frasco de ${calcFmt(vial,2)} mg, ${calcFmt(dil,2)} ml de diluente, dose de ${st.unit === "mg" ? calcFmt(doseMg,3)+" mg" : calcFmt(doseMg*1000,0)+" mcg"} (${calcFmt(ui,1)} UI).`);
}
["calcDoseCustom","calcVialCustom","calcDilCustom"].forEach(id => {
  const el = $(id); if (!el) return;
  el.addEventListener("input", () => {
    const key = id === "calcDoseCustom" ? "dose" : (id === "calcVialCustom" ? "vial" : "dil");
    calcState[key] = calcNum(el.value);
    calcRender();
  });
});
calcRender();
</script>
</body>
</html>
"""


def js(valor) -> str:
    """Serializa um valor Python para literal JavaScript."""
    return json.dumps(valor, ensure_ascii=False)


def gerar_html(cfg: dict) -> str:
    substituicoes = {
        "__TITULO__": cfg["titulo"],
        "__GUIA_PDF__": cfg["guia_pdf"],
        "__WHATSAPP__": cfg["whatsapp"],
        "__DOSES_MCG__": js(cfg["doses_mcg"]),
        "__DOSES_MG__": js(cfg["doses_mg"]),
        "__FRASCOS__": js(cfg["frascos_mg"]),
        "__DILUENTES__": js(cfg["diluentes_ml"]),
        "__SERINGAS__": js(cfg["seringas"]),
        "__ESTADO__": js(cfg["estado_inicial"]),
    }
    html = HTML_TEMPLATE
    for chave, valor in substituicoes.items():
        html = html.replace(chave, valor)
    return html


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera a Calculadora de Peptídeos em HTML.")
    parser.add_argument("-o", "--output", default="calculadora.html", help="arquivo de saída")
    parser.add_argument("--whatsapp", default=CONFIG["whatsapp"], help="número do WhatsApp (com DDI+DDD)")
    parser.add_argument("--guia", default=CONFIG["guia_pdf"], help="caminho/URL do guia de reconstituição")
    parser.add_argument("--no-open", action="store_true", help="não abrir no navegador")
    args = parser.parse_args()

    cfg = dict(CONFIG, whatsapp=args.whatsapp, guia_pdf=args.guia)
    saida = Path(args.output).resolve()
    saida.write_text(gerar_html(cfg), encoding="utf-8")
    print(f"✔ Calculadora gerada em: {saida}")

    if not args.no_open:
        webbrowser.open(saida.as_uri())


if __name__ == "__main__":
    main()
