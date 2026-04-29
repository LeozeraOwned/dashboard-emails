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
    box-shadow: 0 0 20px #00ffe0;
    animation: glowMenu 2s infinite alternate;
}

@keyframes glowMenu {
    from { box-shadow: 0 0 5px #00ffe0; }
    to { box-shadow: 0 0 25px #00ffe0; }
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

/* ANIMAÇÃO BORDA */
@keyframes borderMove {
    0% {transform: rotate(0deg);}
    100% {transform: rotate(360deg);}
}

/* TAXA */
.pulse-green {
    animation: pulseGreen 1s infinite;
    color: #00ff9f;
}

.pulse-red {
    animation: pulseRed 1s infinite;
    color: #ff4d4d;
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

/* BARRA ANIMADA */
.plotly .bars path {
    transition: all 0.8s ease-in-out !important;
}

</style>
""", unsafe_allow_html=True)

# ================= LOAD =================
df = pd.read_csv("log_emails.csv")

df["data"] = pd.to_datetime(df["data"], errors="coerce")
df["dia"] = df["data"].dt.date
df["mes"] = df["data"].dt.month

# ================= SIDEBAR =================
st.sidebar.title("📊 MENU")

pagina = st.sidebar.radio(
    "Navegação",
    ["📊 Dashboard", "📈 Análises", "📅 Por Dia", "📄 Dados"]
)

# ================= FILTROS =================
meses = sorted(df["mes"].dropna().unique())
mes_sel = st.sidebar.selectbox("Mês", ["Todos"] + list(meses))

dias = sorted(df["dia"].dropna().unique())
dia_sel = st.sidebar.selectbox("Dia", ["Todos"] + list(dias))

df_f = df.copy()

if mes_sel != "Todos":
    df_f = df_f[df_f["mes"] == mes_sel]

if dia_sel != "Todos":
    df_f = df_f[df_f["dia"] == dia_sel]

# ================= FUNÇÃO CARD =================
def card(icon, valor, label, extra_class=""):
    return f"""
    <div class="card">
        <div class="content {extra_class}">
            {icon}
            <div class="big">{valor}</div>
            <div class="small">{label}</div>
        </div>
    </div>
    """

# ================= DASHBOARD =================
if pagina == "📊 Dashboard":

    st.title("🚀 Painel Inteligente")

    total = len(df_f)
    categ = len(df_f[df_f["status"] == "Categorizado"])
    erros = len(df_f[df_f["status"] == "Erro"])
    taxa = (categ / total * 100) if total > 0 else 0

    classe_taxa = "pulse-green" if taxa >= 85 else "pulse-red"

    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(card("📩", total, "Total"), unsafe_allow_html=True)
    col2.markdown(card("✅", categ, "Categorizados"), unsafe_allow_html=True)
    col3.markdown(card("❌", erros, "Erros"), unsafe_allow_html=True)
    col4.markdown(card("⚡", f"{taxa:.1f}%", "Taxa", classe_taxa), unsafe_allow_html=True)

    st.divider()

    # 📊 BARRA ANIMADA
    st.subheader("📊 Volume por Analista")

    dist = df_f["analista"].value_counts().reset_index()
    dist.columns = ["Analista", "Qtd"]

    fig = px.bar(
        dist,
        x="Analista",
        y="Qtd",
        color="Analista",
        text="Qtd",
        template="plotly_dark"
    )

    fig.update_layout(transition_duration=800)
    st.plotly_chart(fig, use_container_width=True)

# ================= ANALISE =================
elif pagina == "📈 Análises":

    st.title("📈 Performance Geral")

    total = len(df_f)
    categ = len(df_f[df_f["status"] == "Categorizado"])
    taxa = (categ / total * 100) if total > 0 else 0

    # 🔥 VELOCÍMETRO
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=taxa,
        title={'text': "Taxa de Acerto"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "cyan"},
            'steps': [
                {'range': [0, 50], 'color': "red"},
                {'range': [50, 85], 'color': "yellow"},
                {'range': [85, 100], 'color': "green"}
            ],
        }
    ))

    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # 📊 TIMELINE
    timeline = df_f.groupby("dia").size().reset_index(name="Qtd")

    fig2 = px.line(
        timeline,
        x="dia",
        y="Qtd",
        markers=True,
        template="plotly_dark"
    )

    fig2.update_layout(transition_duration=800)
    st.plotly_chart(fig2, use_container_width=True)

# ================= POR DIA =================
elif pagina == "📅 Por Dia":

    st.title("📅 Visão Detalhada")

    col1, col2, col3 = st.columns(3)

    total = len(df_f)
    categ = len(df_f[df_f["status"] == "Categorizado"])
    erros = len(df_f[df_f["status"] == "Erro"])

    col1.metric("Total", total)
    col2.metric("Categorizados", categ)
    col3.metric("Erros", erros)

    st.divider()

    dist = df_f["analista"].value_counts().reset_index()
    dist.columns = ["Analista", "Qtd"]

    fig = px.bar(
        dist,
        x="Analista",
        y="Qtd",
        color="Analista",
        text="Qtd",
        template="plotly_dark"
    )

    fig.update_layout(transition_duration=800)
    st.plotly_chart(fig, use_container_width=True)

# ================= DADOS =================
elif pagina == "📄 Dados":

    st.title("📄 Logs")

    st.dataframe(df_f, use_container_width=True)
