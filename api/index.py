import json
import sys
from pathlib import Path

from flask import Flask, jsonify, request

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from calculos import (  # noqa: E402
    DadosInsuficientesError,
    calcular_dados_brutos,
    calcular_tabela_frequencia_classes,
    calcular_tabela_frequencia_simples,
)

app = Flask(__name__)

PAGE = """<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Medidas de Dispersão</title>
  <style>
    :root { --ink:#172033; --muted:#647087; --line:#d9e1ec; --blue:#246bce; --bg:#f5f7fb; --card:#fff; }
    * { box-sizing:border-box; }
    body { margin:0; background:linear-gradient(135deg,#eef4ff 0%,var(--bg) 48%,#fff8ed 100%); color:var(--ink); font:16px system-ui,sans-serif; }
    main { max-width:960px; margin:0 auto; padding:48px 20px; }
    h1 { margin:0; font-size:clamp(2rem,5vw,3.5rem); letter-spacing:-.04em; }
    header p { color:var(--muted); margin:8px 0 28px; }
    .layout { display:grid; grid-template-columns:minmax(0,1.1fr) minmax(280px,.9fr); gap:20px; }
    section { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:24px; box-shadow:0 12px 32px #253b5c12; }
    .tabs { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:20px; }
    button, input, textarea { font:inherit; }
    button { border:0; border-radius:8px; padding:11px 16px; cursor:pointer; }
    .tab { background:#edf2f8; color:var(--ink); }
    .tab.active, .primary { background:var(--blue); color:#fff; }
    .mode { display:none; } .mode.active { display:block; }
    label { display:block; color:var(--muted); font-size:.9rem; margin:12px 0 6px; }
    textarea, input { width:100%; border:1px solid var(--line); border-radius:7px; padding:10px; }
    textarea { min-height:130px; resize:vertical; }
    .row { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; margin-bottom:8px; }
    .row strong { color:var(--muted); font-size:.85rem; }
    .actions { display:flex; gap:8px; margin-top:20px; }
    .secondary { background:#edf2f8; color:var(--ink); }
    .results { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
    .metric { border:1px solid var(--line); border-radius:8px; padding:14px; }
    .metric small { display:block; color:var(--muted); } .metric b { display:block; color:var(--blue); font-size:1.45rem; margin-top:4px; }
    #status { min-height:24px; margin-top:14px; color:#b42318; } .ok { color:#16794c !important; }
    @media (max-width:700px) { .layout { grid-template-columns:1fr; } main { padding:28px 14px; } .row { grid-template-columns:1fr; } }
  </style>
</head>
<body><main>
  <header><h1>Medidas de Dispersão</h1><p>Calcule amplitude, variância, desvio padrão e coeficiente de variação.</p></header>
  <div class="layout"><section>
    <div class="tabs"><button class="tab active" data-mode="raw">Dados brutos</button><button class="tab" data-mode="simple">Frequência simples</button><button class="tab" data-mode="classes">Frequência em classes</button></div>
    <div id="raw" class="mode active"><label for="values">Valores separados por espaço, vírgula ou ponto e vírgula</label><textarea id="values">2, 4, 4, 4, 5, 5, 7, 9</textarea></div>
    <div id="simple" class="mode"><div class="row"><strong>Valor (x)</strong><strong>Frequência (f)</strong></div><div id="simple-rows"></div><button class="secondary" type="button" onclick="addRow('simple')">+ Adicionar linha</button></div>
    <div id="classes" class="mode"><div class="row"><strong>Limite inferior</strong><strong>Limite superior</strong><strong>Frequência</strong></div><div id="class-rows"></div><button class="secondary" type="button" onclick="addRow('classes')">+ Adicionar linha</button></div>
    <label><input id="sample" type="checkbox" style="width:auto"> Variância amostral (n-1)</label>
    <div class="actions"><button class="primary" type="button" onclick="calculate()">Calcular</button><button class="secondary" type="button" onclick="clearForm()">Limpar</button></div>
    <div id="status"></div>
  </section><section><h2>Resultados</h2><div class="results"><div class="metric"><small>Amplitude total</small><b id="amplitude">-</b></div><div class="metric"><small>Variância</small><b id="variance">-</b></div><div class="metric"><small>Desvio padrão</small><b id="stddev">-</b></div><div class="metric"><small>Coeficiente de variação</small><b id="cv">-</b></div></div><p id="summary" style="color:var(--muted)"></p></section></div>
</main><script>
let current='raw';
const number = value => Number(String(value).trim().replace(',', '.'));
function addRow(mode) { const row=document.createElement('div'); row.className='row'; row.innerHTML=(mode==='simple'?2:3).toString().split('').map(()=>'<input type="text" inputmode="decimal">').join(''); document.getElementById(mode+'-rows').appendChild(row); }
for(let i=0;i<3;i++){ addRow('simple'); addRow('classes'); }
document.querySelectorAll('.tab').forEach(button=>button.onclick=()=>{ current=button.dataset.mode; document.querySelectorAll('.tab').forEach(item=>item.classList.toggle('active',item===button)); document.querySelectorAll('.mode').forEach(item=>item.classList.toggle('active',item.id===current)); });
function values(mode) { return [...document.querySelectorAll('#'+mode+'-rows .row')].map(row=>[...row.querySelectorAll('input')].map(input=>number(input.value))).filter(row=>row.some(value=>!Number.isNaN(value))); }
async function calculate() { let payload={mode:current,sample:document.getElementById('sample').checked}; if(current==='raw') payload.values=document.getElementById('values').value; else payload.rows=values(current); try { const response=await fetch('/calculate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); const result=await response.json(); if(!response.ok) throw new Error(result.error); ['amplitude','variance','stddev','cv'].forEach(key=>document.getElementById(key).textContent=result[key]); document.getElementById('summary').textContent=`n = ${result.n} | média = ${result.mean} | variância ${payload.sample?'amostral':'populacional'}`; document.getElementById('status').textContent='Cálculo realizado com sucesso.'; document.getElementById('status').className='ok'; } catch(error) { document.getElementById('status').textContent='Erro: '+error.message; document.getElementById('status').className=''; } }
function clearForm(){ document.getElementById('values').value=''; document.querySelectorAll('input[type=text]').forEach(input=>input.value=''); document.querySelectorAll('.metric b').forEach(item=>item.textContent='-'); document.getElementById('summary').textContent=''; document.getElementById('status').textContent=''; }
</script></body></html>"""


def _result_json(result):
    return {
        "n": result.n,
        "mean": f"{result.media:.4f}",
        "amplitude": f"{result.amplitude_total:.4f}",
        "variance": f"{result.variancia:.4f}",
        "stddev": f"{result.desvio_padrao:.4f}",
        "cv": "indefinido" if result.coeficiente_variacao != result.coeficiente_variacao else f"{result.coeficiente_variacao:.2f}%",
    }


@app.get("/")
def index():
    return PAGE


@app.post("/calculate")
def calculate():
    try:
        data = request.get_json(force=True)
        sample = bool(data.get("sample"))
        mode = data.get("mode")
        if mode == "raw":
            import re
            values = [float(item.replace(",", ".")) for item in re.split(r"[\\s,;]+", data.get("values", "").strip()) if item]
            result = calcular_dados_brutos(values, sample)
        elif mode == "simple":
            rows = data.get("rows", [])
            result = calcular_tabela_frequencia_simples([row[0] for row in rows], [row[1] for row in rows], sample)
        elif mode == "classes":
            rows = data.get("rows", [])
            result = calcular_tabela_frequencia_classes([row[0] for row in rows], [row[1] for row in rows], [row[2] for row in rows], sample)
        else:
            raise ValueError("Modo de entrada inválido.")
        return jsonify(_result_json(result))
    except (ValueError, TypeError, IndexError, DadosInsuficientesError) as error:
        return jsonify({"error": str(error)}), 400


if __name__ == "__main__":
    app.run(debug=True)
