import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# ================= CSS ULTRA =================
st.markdown("""
<style>

body {
    background-color: #0e1117;
}

/* CARD BASE */
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
    font-size: 30px;
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

/* TAXA PISCANDO */
.pulse {
    animation: pulse 1s infinite;
}

@keyframes pulse {
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

    piscando = "pulse" if taxa < 80 else ""

    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f"""
    <div class="card">
        <div class="content">
            📩
            <div class="big">{total}</div>
            <div class="small">Total</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
    <div class="card">
        <div class="content">
            ✅
            <div class="big">{categ}</div>
            <div class="small">Categorizados</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
    <div class="card">
        <div class="content">
            ❌
            <div class="big">{erros}</div>
            <div class="small">Erros</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col4.markdown(f"""
    <div class="card">
        <div class="content {piscando}">
            ⚡
            <div class="big">{taxa:.1f}%</div>
            <div class="small">Taxa</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # 📊 DISTRIBUIÇÃO (VOLUME)
    st.subheader("📊 Volume por Analista")

    dist = df_f["analista"].value_counts().reset_index()
    dist.columns = ["Analista", "Qtd"]

    fig1 = px.bar(
        dist,
        x="Analista",
        y="Qtd",
        color="Analista",
        template="plotly_dark",
        text="Qtd"
    )

    st.plotly_chart(fig1, use_container_width=True)

    # 🧠 RANKING REAL (PERFORMANCE)
    st.subheader("🏆 Ranking por Performance")

    perf = df_f.groupby("analista")["status"].apply(
        lambda x: (x == "Categorizado").sum() / len(x) * 100
    ).reset_index()

    perf.columns = ["Analista", "Performance"]

    fig2 = px.bar(
        perf.sort_values("Performance", ascending=False),
        x="Analista",
        y="Performance",
        color="Performance",
        template="plotly_dark",
        text="Performance"
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
