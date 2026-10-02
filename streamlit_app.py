import math
import re

import streamlit as st

from calculos import (
    DadosInsuficientesError,
    calcular_dados_brutos,
    calcular_tabela_frequencia_simples,
    calcular_tabela_frequencia_classes,
)


# Configuração da página
st.set_page_config(
    page_title="Calculadora de Medidas de Dispersão",
    page_icon="📊",
    layout="wide",
)


# Estilos da interface
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --navy: #102b59;
    --blue: #2563eb;
    --blue-light: #eff6ff;
    --background: #f3f6fc;
    --surface: #ffffff;
    --text: #1e293b;
    --muted: #64748b;
    --border: #dfe7f2;
    color-scheme: light;
}

html, body, .stApp {
    background: var(--background) !important;
    color: var(--text);
    color-scheme: light;
}

.stApp,
.stApp [data-testid="stMarkdownContainer"],
.stApp label,
.stApp input,
.stApp textarea,
.stApp button {
    font-family: "Inter", sans-serif !important;
}

/* Esconde barra superior do Streamlit */
[data-testid="stHeader"] {
    background: transparent !important;
}

.block-container {
    max-width: 1050px;
    padding: 28px 28px 55px;
}

/* Cabeçalho */
.hero {
    position: relative;
    overflow: hidden;
    background: linear-gradient(115deg, #102b59 0%, #1e40af 65%, #2455d6 100%);
    border-radius: 20px;
    padding: 38px 42px;
    color: #ffffff;
    box-shadow: 0 10px 28px rgba(15, 42, 86, 0.12);
    margin-bottom: 24px;
}

.hero::after {
    content: "";
    position: absolute;
    right: -70px;
    top: -100px;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(255,255,255,.12), transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}

.hero .eyebrow {
    display: inline-flex;
    align-items: center;
    color: #dbeafe;
    background: rgba(255,255,255,.10);
    border: 1px solid rgba(255,255,255,.20);
    border-radius: 999px;
    padding: 6px 13px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .12em;
    text-transform: uppercase;
}

.hero h1 {
    position: relative;
    z-index: 1;
    color: #ffffff;
    font-size: 31px;
    font-weight: 800;
    line-height: 1.25;
    letter-spacing: -.03em;
    margin: 16px 0 0;
    padding: 0;
}

.hero p {
    position: relative;
    z-index: 1;
    color: #e0ecff;
    font-size: 15px;
    line-height: 1.55;
    max-width: 620px;
    margin: 9px 0 0;
}

/* Cartões das seções */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 15px;
    box-shadow: 0 2px 5px rgba(15, 42, 86, .035);
}

/* Títulos das etapas */
.step-heading {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 11px;
    color: var(--text);
    font-size: 17px;
    font-weight: 700;
    margin: 0 0 18px;
}

.step-number {
    width: 29px;
    height: 29px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    border-radius: 8px;
    background: #edf5ff;
    color: var(--blue);
    font-size: 13px;
    font-weight: 700;
}

.hint {
    color: var(--muted);
    font-size: 12px;
    font-weight: 400;
    margin-left: auto;
}

.helper {
    color: var(--muted);
    font-size: 13px;
    line-height: 1.65;
}

/* Rótulos personalizados */
.field-label {
    color: var(--text);
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 8px;
    min-height: 20px;
}

/* Rótulos nativos dos campos (ex.: "Valores") */
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label {
    color: #1e293b !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}

/* ---------- Seletor "Tipo de entrada" ---------- */
[data-testid="stSelectbox"] {
    width: 100%;
}

[data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background: #ffffff !important;
    background-color: #ffffff !important;
    color: #1e293b !important;
    border-radius: 10px !important;
    min-height: 44px !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    border: 1px solid #dbe4f0 !important;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04) !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] div,
[data-testid="stSelectbox"] [data-baseweb="select"] span,
[data-testid="stSelectbox"] [data-baseweb="select"] input {
    background-color: transparent !important;
    color: #1e293b !important;
    font-size: 14px !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] svg {
    fill: #64748b !important;
    color: #64748b !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"]:focus-within > div {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12) !important;
}

/* Menu aberto do seletor */
[data-baseweb="popover"],
[data-baseweb="popover"] > div,
[data-baseweb="menu"],
[data-baseweb="menu"] ul {
    background: #ffffff !important;
    background-color: #ffffff !important;
    border-radius: 10px !important;
}

[data-baseweb="popover"] {
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 8px 24px rgba(15, 42, 86, 0.12) !important;
}

[data-baseweb="popover"] *,
[data-baseweb="menu"] * {
    color: #334155 !important;
}

[role="option"] {
    background: #ffffff !important;
    font-size: 14px !important;
}

[role="option"]:hover,
[role="option"][aria-selected="true"] {
    background: #eff6ff !important;
}

[role="option"]:hover *,
[role="option"][aria-selected="true"] * {
    color: #1d4ed8 !important;
}

/* ---------- População / Amostra (segmentado) ---------- */
[data-testid="stRadio"] {
    width: 100%;
}

/* esconde o rótulo nativo (já usamos o rótulo personalizado) */
[data-testid="stRadio"] > label,
[data-testid="stRadio"] [data-testid="stWidgetLabel"] {
    display: none !important;
}

[data-testid="stRadio"] div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    align-items: stretch !important;
    gap: 4px !important;
    width: 100% !important;
    min-height: 44px !important;
    padding: 4px !important;
    background: #f5f7fb !important;
    border: 1px solid #dbe4f0 !important;
    border-radius: 10px !important;
    box-sizing: border-box !important;
}

[data-testid="stRadio"] div[role="radiogroup"] > label {
    flex: 1 1 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 0 !important;
    padding: 6px 10px !important;
    border-radius: 8px !important;
    cursor: pointer !important;
    background: transparent !important;
    transition: all .15s ease;
}

/* esconde a bolinha do radio */
[data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}

[data-testid="stRadio"] div[role="radiogroup"] > label p {
    color: #64748b !important;
    font-size: 13.5px !important;
    font-weight: 600 !important;
    margin: 0 !important;
    text-align: center;
}

/* opção selecionada */
[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) {
    background: #ffffff !important;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.10) !important;
}

[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) p {
    color: #2563eb !important;
}

/* ---------- Campos de texto ---------- */
[data-testid="stTextArea"] [data-baseweb="textarea"],
[data-testid="stTextArea"] [data-baseweb="base-input"],
[data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stTextInput"] [data-baseweb="base-input"] {
    background: #ffffff !important;
    background-color: #ffffff !important;
    border: 1px solid #dbe4f0 !important;
    border-radius: 10px !important;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04) !important;
}

[data-testid="stTextArea"] [data-baseweb="base-input"],
[data-testid="stTextInput"] [data-baseweb="base-input"] {
    border: none !important;
    box-shadow: none !important;
}

[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input {
    background: #ffffff !important;
    color: #1e293b !important;
    font-size: 14px !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
}

[data-testid="stTextArea"] textarea::placeholder,
[data-testid="stTextInput"] input::placeholder {
    color: #94a3b8 !important;
    opacity: 1 !important;
}

[data-testid="stTextArea"] [data-baseweb="textarea"]:focus-within,
[data-testid="stTextInput"] [data-baseweb="input"]:focus-within {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12) !important;
}

/* ---------- Botões ---------- */
.stButton > button {
    min-height: 44px;
    border-radius: 10px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    white-space: nowrap !important;
    transition: all .15s ease;
}

.stButton > button p {
    font-size: 14px !important;
    font-weight: 600 !important;
    white-space: nowrap !important;
}

.stButton > button[kind="secondary"] {
    background: #eff6ff !important;
    color: #2563eb !important;
    border: 1px solid transparent !important;
}

.stButton > button[kind="secondary"] p {
    color: #2563eb !important;
}

.stButton > button[kind="secondary"]:hover {
    background: #dbeafe !important;
    color: #1d4ed8 !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
    color: #ffffff !important;
    border: 1px solid transparent !important;
    box-shadow: 0 6px 16px -6px rgba(37, 99, 235, .45);
}

.stButton > button[kind="primary"] p {
    color: #ffffff !important;
}

.stButton > button[kind="primary"]:hover {
    filter: brightness(1.06);
    transform: translateY(-1px);
}

/* ---------- Cartões dos resultados ---------- */
.results-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 14px;
    margin-top: 14px;
}

.stat {
    min-width: 0;
    background: #f5f7fb;
    border: 1px solid #e1e8f2;
    border-radius: 12px;
    padding: 17px 18px;
    min-height: 98px;
}

.stat-label {
    color: #64748b;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .07em;
    text-transform: uppercase;
}

.stat-value {
    color: #1e293b;
    font-size: 23px;
    font-weight: 800;
    line-height: 1.2;
    margin-top: 7px;
    overflow-wrap: anywhere;
}

.stat-sub {
    color: #64748b;
    font-size: 11px;
    margin-top: 4px;
}

.stat.highlight {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    border-color: transparent;
}

.stat.highlight .stat-label,
.stat.highlight .stat-sub {
    color: #dbeafe;
}

.stat.highlight .stat-value {
    color: #ffffff;
}

.footnote {
    text-align: center;
    color: #94a3b8;
    font-size: 12px;
    margin-top: 28px;
}

/* Exemplos numéricos */
.stMarkdown p code,
.helper code {
    background: #f5f7fb !important;
    color: #1e293b !important;
    border: 1px solid #e1e8f2 !important;
    border-radius: 5px;
    padding: 1px 6px;
    font-size: .88em;
    font-weight: 500;
}

/* Expander */
[data-testid="stExpander"] {
    border: 1px solid #e1e8f2 !important;
    border-radius: 10px !important;
    background: #ffffff !important;
}

[data-testid="stExpander"] summary,
[data-testid="stExpander"] p,
[data-testid="stExpander"] li {
    color: #334155 !important;
}

/* Ajustes para telas menores */
@media (max-width: 900px) {
    .results-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 700px) {
    .block-container {
        padding: 16px 12px 40px;
    }

    .hero {
        padding: 27px 24px;
    }

    .hero h1 {
        font-size: 24px;
    }

    .hero p {
        font-size: 14px;
    }

    .results-grid {
        gap: 10px;
    }

    .stat {
        padding: 13px;
        min-height: 96px;
    }

    .stat-value {
        font-size: 19px;
    }

    .hint {
        width: 100%;
        margin-left: 40px;
    }
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# Cabeçalho
st.markdown(
    """
    <header class="hero">
        <span class="eyebrow">Estatística Descritiva</span>
        <h1>Calculadora de Medidas de Dispersão</h1>
        <p>
            Calcule e explore os principais indicadores estatísticos dos seus dados:
            amplitude, variância, desvio padrão e coeficiente de variação.
        </p>
    </header>
    """,
    unsafe_allow_html=True,
)


# Valores iniciais dos campos
valores_iniciais = {
    "dados_texto": "",
    "valores_texto": "",
    "frequencias_texto": "",
    "limites_inferiores_texto": "",
    "limites_superiores_texto": "",
    "frequencias_classes_texto": "",
}

for chave, valor in valores_iniciais.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor


def carregar_exemplo():
    tipo = st.session_state.get("tipo_dados", "Dados brutos")

    if tipo == "Dados brutos":
        st.session_state["dados_texto"] = "10, 12, 15, 18, 20, 22, 25"

    elif tipo == "Tabela de frequência simples":
        st.session_state["valores_texto"] = "10, 20, 30"
        st.session_state["frequencias_texto"] = "2, 4, 3"

    else:
        st.session_state["limites_inferiores_texto"] = "10, 20, 30"
        st.session_state["limites_superiores_texto"] = "19, 29, 39"
        st.session_state["frequencias_classes_texto"] = "5, 8, 4"


def ler_numeros(texto: str, nome_campo: str) -> list[float]:
    texto = texto.strip()

    if not texto:
        raise ValueError(f"Preencha o campo: {nome_campo}.")

    if ";" in texto:
        partes = [
            parte.replace(",", ".")
            for parte in re.split(r"[;\s]+", texto)
            if parte
        ]
    else:
        partes = [
            parte
            for parte in re.split(r"[,\s]+", texto)
            if parte
        ]

    try:
        numeros = [float(parte) for parte in partes]
    except ValueError:
        raise ValueError(
            f"Há um valor inválido no campo '{nome_campo}'. "
            "Separe os números por vírgula, ponto e vírgula ou espaço."
        )

    if not all(math.isfinite(numero) for numero in numeros):
        raise ValueError(f"O campo '{nome_campo}' contém um número inválido.")

    return numeros


def ler_frequencias(texto: str) -> list[float]:
    frequencias = ler_numeros(texto, "Frequências")

    if any(frequencia < 0 for frequencia in frequencias):
        raise ValueError("As frequências não podem ser negativas.")

    if any(not frequencia.is_integer() for frequencia in frequencias):
        raise ValueError("As frequências devem ser números inteiros.")

    if sum(frequencias) == 0:
        raise ValueError("A soma das frequências deve ser maior que zero.")

    return frequencias


def calcular_mediana_ponderada(valores, frequencias):
    pares = sorted(zip(valores, frequencias))
    total = int(sum(frequencias))

    posicoes_centrais = ((total - 1) // 2, total // 2)
    encontrados = []
    acumulada = 0
    indice_posicao = 0

    for valor, frequencia in pares:
        proxima_acumulada = acumulada + int(frequencia)

        while (
            indice_posicao < len(posicoes_centrais)
            and posicoes_centrais[indice_posicao] < proxima_acumulada
        ):
            encontrados.append(valor)
            indice_posicao += 1

        acumulada = proxima_acumulada

        if indice_posicao == len(posicoes_centrais):
            break

    return sum(encontrados) / len(encontrados)


def titulo_etapa(numero, titulo, dica=""):
    dica_html = f'<span class="hint">{dica}</span>' if dica else ""

    st.markdown(
        f"""
        <div class="step-heading">
            <span class="step-number">{numero}</span>
            <span>{titulo}</span>
            {dica_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def exibir_resultado(resultado, tipo_conjunto, mediana):
    st.markdown(
        f'<div class="helper">{tipo_conjunto} &nbsp;•&nbsp; {resultado.n} valores</div>',
        unsafe_allow_html=True,
    )

    simbolo_dp = (
        "s (amostral)"
        if tipo_conjunto == "Amostra"
        else "σ (populacional)"
    )
    simbolo_var = "s²" if tipo_conjunto == "Amostra" else "σ²"
    formula_cv = "CV = s / x̄" if tipo_conjunto == "Amostra" else "CV = σ / μ"

    if math.isnan(resultado.coeficiente_variacao):
        coeficiente_variacao = "Indefinido"
    else:
        coeficiente_variacao = f"{resultado.coeficiente_variacao:.1f}%"

    medidas = [
        ("Desvio padrão", f"{resultado.desvio_padrao:.2f}", simbolo_dp, True),
        ("Variância", f"{resultado.variancia:.2f}", simbolo_var, False),
        ("Média", f"{resultado.media:.2f}", "x̄", False),
        ("Amplitude", f"{resultado.amplitude_total:.2f}", "máx − mín", False),
        ("Coef. de variação", coeficiente_variacao, formula_cv, False),
        ("Mediana", f"{mediana:.2f}", "Md", False),
    ]

    cartoes = []

    for rotulo, valor, complemento, destaque in medidas:
        classe = "stat highlight" if destaque else "stat"

        cartoes.append(
            f'<div class="{classe}">'
            f'<div class="stat-label">{rotulo}</div>'
            f'<div class="stat-value">{valor}</div>'
            f'<div class="stat-sub">{complemento}</div>'
            f'</div>'
        )

    st.markdown(
        '<div class="results-grid">' + "".join(cartoes) + "</div>",
        unsafe_allow_html=True,
    )

    with st.expander("Entenda as medidas"):
        st.markdown(
            """
            - **Média:** valor médio do conjunto de dados.
            - **Mediana:** valor central dos dados ordenados.
            - **Amplitude:** diferença entre o maior e o menor valor.
            - **Variância:** medida da dispersão dos dados em relação à média.
            - **Desvio padrão:** raiz quadrada da variância.
            - **Coeficiente de variação:** desvio padrão dividido pela média,
              expresso em porcentagem.
            """
        )


# 1. Configuração do cálculo
with st.container(border=True):
    titulo_etapa(1, "Configuração do cálculo")

    coluna_tipo, coluna_conjunto = st.columns(2)

    with coluna_tipo:
        st.markdown(
            '<div class="field-label">Tipo de entrada</div>',
            unsafe_allow_html=True,
        )

        tipo_dados = st.selectbox(
            "Tipo de entrada",
            [
                "Dados brutos",
                "Tabela de frequência simples",
                "Tabela de frequência por classes",
            ],
            key="tipo_dados",
            label_visibility="collapsed",
        )

    with coluna_conjunto:
        st.markdown(
            '<div class="field-label">Conjunto estatístico</div>',
            unsafe_allow_html=True,
        )

        tipo_conjunto = st.radio(
            "Conjunto estatístico",
            ["População", "Amostra"],
            horizontal=True,
            key="tipo_conjunto",
            label_visibility="collapsed",
        )

amostral = tipo_conjunto == "Amostra"


# 2. Inserção dos dados
with st.container(border=True):
    titulo_etapa(
        2,
        "Insira seus dados",
        "Valores separados por vírgula, espaço ou quebra de linha",
    )

    st.markdown(
        """
        <p class="helper">
            Para números decimais, use ponto (<code>10.5</code>) ou vírgula
            (<code>10,5</code>) com ponto e vírgula entre os valores.
            Exemplo: <code>10; 12,5; 15; 18; 20</code>
        </p>
        """,
        unsafe_allow_html=True,
    )

    if tipo_dados == "Dados brutos":
        dados_texto = st.text_area(
            "Valores",
            placeholder="Ex.: 10, 12, 15, 18, 20",
            height=125,
            key="dados_texto",
        )

    elif tipo_dados == "Tabela de frequência simples":
        coluna_valores, coluna_frequencias = st.columns(2)

        with coluna_valores:
            valores_texto = st.text_area(
                "Valores (x)",
                placeholder="Ex.: 10, 20, 30",
                height=125,
                key="valores_texto",
            )

        with coluna_frequencias:
            frequencias_texto = st.text_area(
                "Frequências (f)",
                placeholder="Ex.: 2, 4, 3",
                height=125,
                key="frequencias_texto",
            )

    else:
        coluna_inferiores, coluna_superiores, coluna_frequencias = st.columns(3)

        with coluna_inferiores:
            limites_inferiores_texto = st.text_area(
                "Limites inferiores",
                placeholder="Ex.: 10, 20, 30",
                height=125,
                key="limites_inferiores_texto",
            )

        with coluna_superiores:
            limites_superiores_texto = st.text_area(
                "Limites superiores",
                placeholder="Ex.: 19, 29, 39",
                height=125,
                key="limites_superiores_texto",
            )

        with coluna_frequencias:
            frequencias_classes_texto = st.text_area(
                "Frequências",
                placeholder="Ex.: 5, 8, 4",
                height=125,
                key="frequencias_classes_texto",
            )

    coluna_exemplo, coluna_calcular = st.columns([1, 2], gap="small")

    with coluna_exemplo:
        st.button(
            "↺ Carregar exemplo",
            use_container_width=True,
            on_click=carregar_exemplo,
            type="secondary",
        )

    with coluna_calcular:
        calcular = st.button(
            "Calcular medidas",
            use_container_width=True,
            type="primary",
        )


# 3. Cálculo e apresentação dos resultados
if calcular:
    try:
        if tipo_dados == "Dados brutos":
            dados = ler_numeros(dados_texto, "Valores")

            if amostral and len(dados) < 2:
                raise ValueError(
                    "Para calcular medidas amostrais, informe pelo menos dois dados."
                )

            resultado = calcular_dados_brutos(dados, amostral)
            mediana = calcular_mediana_ponderada(
                dados,
                [1] * len(dados),
            )

        elif tipo_dados == "Tabela de frequência simples":
            valores = ler_numeros(valores_texto, "Valores")
            frequencias = ler_frequencias(frequencias_texto)

            if len(valores) != len(frequencias):
                raise ValueError(
                    "Informe a mesma quantidade de valores e frequências."
                )

            if amostral and sum(frequencias) < 2:
                raise ValueError(
                    "Para calcular medidas amostrais, a soma das frequências "
                    "deve ser de pelo menos dois."
                )

            resultado = calcular_tabela_frequencia_simples(
                valores,
                frequencias,
                amostral,
            )

            mediana = calcular_mediana_ponderada(
                valores,
                frequencias,
            )

        else:
            inferiores = ler_numeros(
                limites_inferiores_texto,
                "Limites inferiores",
            )
            superiores = ler_numeros(
                limites_superiores_texto,
                "Limites superiores",
            )
            frequencias = ler_frequencias(frequencias_classes_texto)

            if not (
                len(inferiores) == len(superiores) == len(frequencias)
            ):
                raise ValueError(
                    "Informe a mesma quantidade de limites inferiores, "
                    "limites superiores e frequências."
                )

            if any(
                inferior > superior
                for inferior, superior in zip(inferiores, superiores)
            ):
                raise ValueError(
                    "Cada limite inferior deve ser menor ou igual "
                    "ao respectivo limite superior."
                )

            if amostral and sum(frequencias) < 2:
                raise ValueError(
                    "Para calcular medidas amostrais, a soma das frequências "
                    "deve ser de pelo menos dois."
                )

            pontos_medios = [
                (inferior + superior) / 2
                for inferior, superior in zip(inferiores, superiores)
            ]

            resultado = calcular_tabela_frequencia_classes(
                inferiores,
                superiores,
                frequencias,
                amostral,
            )

            mediana = calcular_mediana_ponderada(
                pontos_medios,
                frequencias,
            )

        with st.container(border=True):
            titulo_etapa(3, "Resultados")
            exibir_resultado(resultado, tipo_conjunto, mediana)

    except (ValueError, DadosInsuficientesError) as erro:
        st.error(str(erro))


# Rodapé
st.markdown(
    '<div class="footnote">Calculadora de Medidas de Dispersão</div>',
    unsafe_allow_html=True,
)