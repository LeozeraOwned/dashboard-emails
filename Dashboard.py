import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(layout="wide")

# ================= CSS ULTRA =================
st.markdown("""
<style>

/* FUNDO */
body {
    background-color: #0e1117;
}

/* SIDEBAR ANIMADA */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0e1117, #111827);
    box-shadow: 0 0 20px rgba(0,255,224,0.35);
    animation: glowMenu 2.4s infinite alternate;
    border-right: 1px solid rgba(0,255,224,0.12);
}

@keyframes glowMenu {
    from { box-shadow: 0 0 8px rgba(0,255,224,0.18); }
    to { box-shadow: 0 0 24px rgba(0,255,224,0.35); }
}

/* TÍTULO DO MENU */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    animation: titlePulse 2.5s ease-in-out infinite;
    letter-spacing: 0.5px;
}

@keyframes titlePulse {
    0%   { text-shadow: 0 0 0px rgba(0,255,224,0.0); }
    50%  { text-shadow: 0 0 12px rgba(0,255,224,0.35); }
    100% { text-shadow: 0 0 0px rgba(0,255,224,0.0); }
}

/* ================= MENU ANIMADO ================= */

/* grupo do radio */
section[data-testid="stSidebar"] div[role="radiogroup"] {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

/* item do menu */
section[data-testid="stSidebar"] div[role="radiogroup"] > label {
    position: relative;
    padding: 10px 14px;
    border-radius: 14px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    transition: all 0.35s ease;
    overflow: hidden;
    cursor: pointer;
}

/* animação de entrada */
section[data-testid="stSidebar"] div[role="radiogroup"] > label {
    animation: menuEnter 0.6s ease forwards;
}

@keyframes menuEnter {
    from {
        opacity: 0;
        transform: translateX(-12px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

/* brilho correndo */
section[data-testid="stSidebar"] div[role="radiogroup"] > label::before {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(
        120deg,
        transparent,
        rgba(0,255,224,0.25),
        transparent
    );
    transform: translateX(-120%);
    transition: transform 0.6s ease;
}

/* barra lateral animada */
section[data-testid="stSidebar"] div[role="radiogroup"] > label::after {
    content: "";
    position: absolute;
    left: 0;
    top: 15%;
    width: 4px;
    height: 70%;
    background: linear-gradient(180deg, #00ffe0, #007cf0);
    border-radius: 4px;
    opacity: 0;
    box-shadow: 0 0 12px rgba(0,255,224,0.6);
    transition: all 0.3s ease;
}

/* hover */
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    transform: translateX(6px);
    background: rgba(0,255,224,0.08);
    border-color: rgba(0,255,224,0.35);
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover::before {
    transform: translateX(120%);
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover::after {
    opacity: 1;
}

/* item ativo */
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
    background: rgba(0,255,224,0.12);
    border-color: rgba(0,255,224,0.5);
    transform: translateX(6px);
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked)::after {
    opacity: 1;
    animation: activePulse 1.4s infinite;
}

@keyframes activePulse {
    0%   { box-shadow: 0 0 8px rgba(0,255,224,0.4); }
    50%  { box-shadow: 0 0 18px rgba(0,255,224,0.9); }
    100% { box-shadow: 0 0 8px rgba(0,255,224,0.4); }
}

/* LABELS DOS FILTROS */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stSelectbox label {
    font-weight: 600;
}

/* SELECTBOX ANIMADO */
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background: linear-gradient(90deg, rgba(255,255,255,0.02), rgba(0,255,224,0.02)) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
    transition: all 0.28s ease !important;
    box-shadow: none !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div:hover {
    transform: translateX(4px);
    border-color: rgba(0,255,224,0.35) !important;
    box-shadow: 0 0 14px rgba(0,255,224,0.12) !important;
    background: linear-gradient(90deg, rgba(0,255,224,0.06), rgba(255,255,255,0.03)) !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"]:focus-within > div,
section[data-testid="stSidebar"] div[data-baseweb="select"] > div:focus-within {
    border-color: rgba(0,255,224,0.55) !important;
    box-shadow: 0 0 0 1px rgba(0,255,224,0.35), 0 0 18px rgba(0,255,224,0.18) !important;
    transform: translateX(4px);
}

/* CARD */
.card {
    position: relative;
    background: #1a1f2b;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    overflow: hidden;
}

/* BORDA ANIMADA */
.card::before {
    content: "";
    position: absolute;
    inset: -2px;
    background: linear-gradient(90deg, #00ffe0, #007cf0, #00ffe0);
    animation: borderMove 4s linear infinite;
    z-index: 0;
}

.card::after {
    content: "";
    position: absolute;
    inset: 2px;
    background: #1a1f2b;
    border-radius: 15px;
    z-index: 1;
}

/* TEXTO */
.content {
    position: relative;
    z-index: 2;
}

.big {
    font-size: 32px;
    font-weight: bold;
}

.small {
    color: #aaa;
}

/* ANIMAÇÃO DO NÚMERO - APENAS UMA VEZ */
.animate-once {
    animation: popOnce 0.8s ease-out 1;
}

@keyframes popOnce {
    0% {
        opacity: 0;
        transform: translateY(12px) scale(0.96);
    }
    70% {
        opacity: 1;
        transform: translateY(0px) scale(1.03);
    }
    100% {
        opacity: 1;
        transform: translateY(0px) scale(1);
    }
}

/* ANIMAÇÃO BORDA */
@keyframes borderMove {
    0% {transform: rotate(0deg);}
    100% {transform: rotate(360deg);}
}

/* CORES DE STATUS */
.pulse-green {
    color: #00ff9f;
}

.pulse-red {
    color: #ff4d4d;
}

/* PULSO SOMENTE QUANDO FILTRO MUDA */
.pulse-green.animate-once {
    animation: pulseGreen 1s 1;
}

.pulse-red.animate-once {
    animation: pulseRed 1s 1;
}

@keyframes pulseGreen {
    0% {opacity: 1;}
    50% {opacity: 0.3;}
    100% {opacity: 1;}
}

@keyframes pulseRed {
    0% {opacity: 1;}
    50% {opacity: 0.3;}
    100% {opacity: 1;}
}

/* BARRA */
.plotly .bars path {
    transition: all 0.8s ease-in-out !important;
}

</style>
""", unsafe_allow_html=True)

# ================= LOAD =================
df = pd.read_csv("log_emails.csv")

# Normalização básica
df.columns = [c.strip() for c in df.columns]

df["data"] = pd.to_datetime(df["data"], errors="coerce")
df["dia"] = df["data"].dt.date
df["mes"] = df["data"].dt.month

df["assunto"] = df["assunto"].fillna("").astype(str).str.strip()
df["analista"] = df["analista"].fillna("").astype(str).str.strip()
df["motivo"] = df["motivo"].fillna("").astype(str).str.strip()
df["status"] = df["status"].fillna("").astype(str).str.strip()

# Campo de exibição para evitar branco no gráfico
df["analista_exibicao"] = df["analista"].replace("", "Sem analista")

# ORDEM FIXA DOS ANALISTAS
all_analistas = sorted(df["analista_exibicao"].dropna().astype(str).unique().tolist())
max_qtd_analista = int(df["analista_exibicao"].value_counts().max()) if not df.empty else 1

# ================= SIDEBAR =================
st.sidebar.title("📊 MENU")

pagina = st.sidebar.radio(
    "Navegação",
    ["📊 Dashboard", "📈 Análises", "📅 Por Dia", "📄 Dados"]
)

# ================= FILTROS =================
meses = sorted([int(m) for m in df["mes"].dropna().unique()])
mes_sel = st.sidebar.selectbox("Mês", ["Todos"] + list(meses))

dias_base = df.copy()
if mes_sel != "Todos":
    dias_base = dias_base[dias_base["mes"] == mes_sel]

dias = sorted(dias_base["dia"].dropna().unique())
dia_sel = st.sidebar.selectbox("Dia", ["Todos"] + list(dias))

df_f = df.copy()

if mes_sel != "Todos":
    df_f = df_f[df_f["mes"] == mes_sel]

if dia_sel != "Todos":
    df_f = df_f[df_f["dia"] == dia_sel]

# ================= CONTROLE DE ANIMAÇÃO =================
filtro_key = f"{mes_sel}|{dia_sel}"

if "last_filter_key" not in st.session_state:
    st.session_state["last_filter_key"] = filtro_key
    st.session_state["animar_cards"] = True
elif st.session_state["last_filter_key"] != filtro_key:
    st.session_state["last_filter_key"] = filtro_key
    st.session_state["animar_cards"] = True
else:
    st.session_state["animar_cards"] = False

# ================= FUNÇÕES =================
def card(icon, valor, label, extra_class="", animate=False):
    anim_class = "animate-once" if animate else ""
    return f"""
    <div class="card">
        <div class="content">
            {icon}
            <div class="big {extra_class} {anim_class}">{valor}</div>
            <div class="small">{label}</div>
        </div>
    </div>
    """

def get_dist_analista(dataframe):
    contagem = (
        dataframe["analista_exibicao"]
        .astype(str)
        .value_counts()
        .reindex(all_analistas, fill_value=0)
    )

    dist = pd.DataFrame({
        "Analista": all_analistas,
        "Qtd": contagem.values
    })
    return dist

def calcular_resumo_categorizacao(dataframe):
    status_norm = dataframe["status"].astype(str).str.strip().str.lower()
    motivo_norm = dataframe["motivo"].astype(str).str.strip().str.lower()

    # Total categorizados = tudo que entrou em fluxo de categorização
    # inclui: Categorizado, Correto e Erro
    total_categorizados = int(status_norm.isin(["categorizado", "correto", "erro"]).sum())

    # Sua regra:
    # CERTO = Correto OU "Humano removeu categoria"
    categorizados_certos = int(
        ((status_norm == "correto") | ((status_norm == "erro") & (motivo_norm == "humano removeu categoria"))).sum()
    )

    # ERRADO = Erro que NÃO seja "Humano removeu categoria"
    categorizados_errados = int(
        ((status_norm == "erro") & (motivo_norm != "humano removeu categoria")).sum()
    )

    # Pendentes = ainda ficaram só como Categorizado
    pendentes_validacao = int((status_norm == "categorizado").sum())

    return total_categorizados, categorizados_certos, categorizados_errados, pendentes_validacao

def formatar_data_pt(valor):
    if pd.isna(valor):
        return ""
    try:
        return pd.to_datetime(valor).strftime("%d/%m/%Y %H:%M")
    except:
        return ""

# ================= DASHBOARD =================
if pagina == "📊 Dashboard":

    st.title("🚀 Painel Inteligente")

    total = len(df_f)
    total_categorizados, categorizados_certos, categorizados_errados, pendentes_validacao = calcular_resumo_categorizacao(df_f)

    col1, col2, col3, col4 = st.columns(4)
    animar = st.session_state.get("animar_cards", False)

    col1.markdown(card("📩", total, "Total", animate=animar), unsafe_allow_html=True)
    col2.markdown(card("📌", total_categorizados, "Total categorizados", animate=animar), unsafe_allow_html=True)
    col3.markdown(card("✅", categorizados_certos, "Categorizados certos", "pulse-green", animate=animar), unsafe_allow_html=True)
    col4.markdown(card("❌", categorizados_errados, "Categorizados errados", "pulse-red", animate=animar), unsafe_allow_html=True)

    st.caption(f"Pendentes de validação: {pendentes_validacao}")

    st.divider()

    st.subheader("📊 Volume por Analista")

    dist = get_dist_analista(df_f)

    fig = px.bar(
        dist,
        x="Analista",
        y="Qtd",
        color="Analista",
        text="Qtd",
        template="plotly_dark",
        category_orders={"Analista": all_analistas}
    )

    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_xaxes(categoryorder="array", categoryarray=all_analistas)
    fig.update_yaxes(range=[0, max_qtd_analista + 5])
    fig.update_layout(
        transition_duration=800,
        showlegend=True,
        xaxis_title="Analista",
        yaxis_title="Qtd"
    )

    st.plotly_chart(fig, use_container_width=True)

# ================= ANÁLISES =================
elif pagina == "📈 Análises":

    st.title("📈 Performance Geral")

    total_categorizados, categorizados_certos, categorizados_errados, pendentes_validacao = calcular_resumo_categorizacao(df_f)

    # Qualidade = certos sobre os revisados (certos + errados)
    revisados = categorizados_certos + categorizados_errados
    qualidade_categorizacao = (
        categorizados_certos / revisados * 100
        if revisados > 0 else 0
    )

    if qualidade_categorizacao >= 85:
        cor_taxa = "#00e5ff"
    elif qualidade_categorizacao >= 50:
        cor_taxa = "#ffd54f"
    else:
        cor_taxa = "#ff4d4d"

    restante = max(0, 100 - qualidade_categorizacao)

    fig = go.Figure(
        data=[
            go.Pie(
                values=[qualidade_categorizacao, restante],
                hole=0.78,
                sort=False,
                direction="clockwise",
                rotation=90,
                textinfo="none",
                hoverinfo="skip",
                marker=dict(
                    colors=[cor_taxa, "rgba(255,255,255,0.08)"],
                    line=dict(color="#0e1117", width=2)
                )
            )
        ]
    )

    fig.update_layout(
        template="plotly_dark",
        height=360,
        margin=dict(t=30, b=20, l=20, r=20),
        showlegend=False,
        annotations=[
            dict(
                text=f"<b>{qualidade_categorizacao:.1f}%</b><br><span style='font-size:14px;color:#B8C1CC'>Categorizados certos</span>",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=30, color=cor_taxa)
            ),
            dict(
                text="Qualidade da Categorização",
                x=0.5,
                y=1.08,
                showarrow=False,
                font=dict(size=20, color="white")
            )
        ]
    )

    st.plotly_chart(fig, use_container_width=True)

    colm1, colm2, colm3 = st.columns(3)
    colm1.metric("Total categorizados", total_categorizados)
    colm2.metric("Revisados", revisados)
    colm3.metric("Pendentes", pendentes_validacao)

    timeline = df_f.groupby("dia").size().reset_index(name="Qtd")

    if not timeline.empty:
        timeline["Data"] = pd.to_datetime(timeline["dia"]).dt.strftime("%d/%m/%Y")

        fig2 = px.line(
            timeline,
            x="Data",
            y="Qtd",
            markers=True,
            template="plotly_dark"
        )

        fig2.update_traces(
            line=dict(color="#6C7BFF", width=3),
            marker=dict(size=8, color="#6C7BFF")
        )

        fig2.update_layout(
            transition_duration=800,
            xaxis_title="Data",
            yaxis_title="Qtd"
        )

        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Sem dados para o período selecionado.")

    st.subheader("📋 O que está sendo analisado")

    tabela_analises = df_f.copy()
    tabela_analises["Data"] = tabela_analises["data"].apply(formatar_data_pt)

    tabela_final = tabela_analises[
        ["Data", "assunto", "analista_exibicao", "motivo", "status"]
    ].rename(columns={
        "assunto": "O que está sendo analisado",
        "analista_exibicao": "Analista",
        "motivo": "Motivo",
        "status": "Status"
    })

    st.dataframe(tabela_final, use_container_width=True)

# ================= POR DIA =================
elif pagina == "📅 Por Dia":

    st.title("📅 Visão Detalhada")

    total = len(df_f)
    total_categorizados, categorizados_certos, categorizados_errados, pendentes_validacao = calcular_resumo_categorizacao(df_f)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total", total)
    col2.metric("Total categorizados", total_categorizados)
    col3.metric("Categorizados certos", categorizados_certos)
    col4.metric("Categorizados errados", categorizados_errados)

    st.caption(f"Pendentes de validação: {pendentes_validacao}")

    st.divider()

    dist = get_dist_analista(df_f)

    fig = px.bar(
        dist,
        x="Analista",
        y="Qtd",
        color="Analista",
        text="Qtd",
        template="plotly_dark",
        category_orders={"Analista": all_analistas}
    )

    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_xaxes(categoryorder="array", categoryarray=all_analistas)
    fig.update_yaxes(range=[0, max_qtd_analista + 5])

    fig.update_layout(
        transition_duration=800,
        xaxis_title="Analista",
        yaxis_title="Qtd"
    )

    st.plotly_chart(fig, use_container_width=True)

# ================= DADOS =================
elif pagina == "📄 Dados":

    st.title("📄 Logs")

    dados_exibir = df_f.copy()
    dados_exibir["data"] = dados_exibir["data"].apply(formatar_data_pt)
    dados_exibir["analista"] = dados_exibir["analista"].replace("", "Sem analista")

    st.dataframe(
        dados_exibir[["data", "assunto", "analista", "motivo", "status"]],
        use_container_width=True
    )



