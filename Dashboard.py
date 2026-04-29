import streamlit as st
import pandas as pd
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
}

/* MENU GLOW */
.css-1d391kg {
    animation: glowMenu 2s infinite alternate;
}

@keyframes glowMenu {
    from { box-shadow: 0 0 5px #00ffe0; }
    to { box-shadow: 0 0 20px #00ffe0; }
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

/* BORDA GIRANDO */
@keyframes borderMove {
    0% {transform: rotate(0deg);}
    100% {transform: rotate(360deg);}
}

/* PULSE VERDE */
.pulse-green {
    animation: pulseGreen 1s infinite;
    color: #00ff9f;
}

@keyframes pulseGreen {
    0% {opacity: 1;}
    50% {opacity: 0.3;}
    100% {opacity: 1;}
}

/* PULSE VERMELHO */
.pulse-red {
    animation: pulseRed 1s infinite;
    color: #ff4d4d;
}

@keyframes pulseRed {
    0% {opacity: 1;}
    50% {opacity: 0.3;}
    100% {opacity: 1;}
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

# ================= DASHBOARD =================
if pagina == "📊 Dashboard":

    st.title("🚀 Painel Inteligente")

    total = len(df_f)
    categ = len(df_f[df_f["status"] == "Categorizado"])
    erros = len(df_f[df_f["status"] == "Erro"])
    taxa = (categ / total * 100) if total > 0 else 0

    # 🔥 DEFINE COR DINÂMICA
    classe_taxa = "pulse-green" if taxa >= 85 else "pulse-red"

    col1, col2, col3, col4 = st.columns(4)

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

    col1.markdown(card("📩", total, "Total"), unsafe_allow_html=True)
    col2.markdown(card("✅", categ, "Categorizados"), unsafe_allow_html=True)
    col3.markdown(card("❌", erros, "Erros"), unsafe_allow_html=True)
    col4.markdown(card("⚡", f"{taxa:.1f}%", "Taxa", classe_taxa), unsafe_allow_html=True)

    st.divider()

    # 📊 DISTRIBUIÇÃO ANIMADA
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

    # 🔥 ANIMAÇÃO SUAVE
    fig.update_layout(
        transition=dict(duration=800),
    )

    st.plotly_chart(fig, use_container_width=True)

    # 🏆 PERFORMANCE
    st.subheader("🏆 Ranking (Performance)")

    perf = df_f.groupby("analista")["status"].apply(
        lambda x: (x == "Categorizado").sum() / len(x) * 100
    ).reset_index()

    perf.columns = ["Analista", "Performance"]

    fig2 = px.bar(
        perf.sort_values("Performance", ascending=False),
        x="Analista",
        y="Performance",
        color="Performance",
        text="Performance",
        template="plotly_dark"
    )

    fig2.update_layout(
        transition=dict(duration=800)
    )

    st.plotly_chart(fig2, use_container_width=True)

# ================= ANALISE =================
elif pagina == "📈 Análises":

    st.title("📈 Análises")

    timeline = df_f.groupby("dia").size().reset_index(name="Qtd")

    fig = px.line(
        timeline,
        x="dia",
        y="Qtd",
        markers=True,
        template="plotly_dark"
    )

    fig.update_layout(
        transition=dict(duration=800)
    )

    st.plotly_chart(fig, use_container_width=True)

# ================= POR DIA =================
elif pagina == "📅 Por Dia":

    st.title("📅 Detalhe por Dia")

    dias = sorted(df["dia"].dropna().unique())
    dia_sel = st.selectbox("Escolha o dia", dias)

    df_dia = df[df["dia"] == dia_sel]

    st.dataframe(df_dia)

# ================= DADOS =================
elif pagina == "📄 Dados":

    st.title("📄 Dados")

    st.dataframe(df_f)
