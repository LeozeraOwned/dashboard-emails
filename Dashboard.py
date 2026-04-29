import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ================= CONFIG =================
st.set_page_config(layout="wide")

# ================= CSS INSANO =================
st.markdown("""
<style>
.card {
    padding: 20px;
    border-radius: 16px;
    background: linear-gradient(145deg, #111, #1f1f1f);
    box-shadow: 0 0 20px rgba(0,255,255,0.1);
    transition: 0.3s;
}
.card:hover {
    transform: scale(1.03);
    box-shadow: 0 0 30px rgba(0,255,255,0.4);
}
.card h3 {
    color: #aaa;
    font-size: 14px;
}
.card h1 {
    color: #fff;
    font-size: 32px;
}
.big-title {
    font-size: 28px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ================= LOAD =================
df = pd.read_csv("log_emails.csv")
df["data"] = pd.to_datetime(df["data"], errors="coerce")
df["dia"] = df["data"].dt.date
df["mes"] = df["data"].dt.strftime("%Y-%m")

# ================= SIDEBAR =================
st.sidebar.title("🚀 CENTRAL")

pagina = st.sidebar.radio(
    "Navegação",
    ["🔥 Dashboard IA", "🏆 Ranking", "📈 Previsão", "📅 Por Dia", "📄 Dados"]
)

# ================= DASHBOARD PRINCIPAL =================
if pagina == "🔥 Dashboard IA":

    st.markdown('<div class="big-title">🔥 Dashboard Inteligente</div>', unsafe_allow_html=True)

    total = len(df)
    categ = len(df[df["status"] == "Categorizado"])
    erros = len(df[df["status"] == "Erro"])

    taxa = (categ / total * 100) if total else 0

    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f'<div class="card"><h3>Total</h3><h1>{total}</h1></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="card"><h3>Categorizados</h3><h1>{categ}</h1></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="card"><h3>Erros</h3><h1>{erros}</h1></div>', unsafe_allow_html=True)
    col4.markdown(f'<div class="card"><h3>Taxa</h3><h1>{taxa:.1f}%</h1></div>', unsafe_allow_html=True)

    st.divider()

    # 🔥 ALERTAS
    st.subheader("🚨 Alertas Inteligentes")

    if erros > total * 0.3:
        st.error("⚠️ Taxa de erro muito alta!")

    if total > 50:
        st.warning("🔥 Alto volume de emails!")

    # 📊 DISTRIBUIÇÃO
    dist = df["analista"].value_counts().reset_index()
    dist.columns = ["Analista", "Qtd"]

    fig = px.bar(dist, x="Analista", y="Qtd", color="Analista", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# ================= RANKING =================
elif pagina == "🏆 Ranking":

    st.title("🏆 Ranking de Analistas")

    total_por_analista = df["analista"].value_counts()

    erros_df = df[df["status"] == "Erro"]["analista"].value_counts()

    ranking = pd.DataFrame({
        "Total": total_por_analista,
        "Erros": erros_df
    }).fillna(0)

    ranking["Taxa Erro %"] = (ranking["Erros"] / ranking["Total"]) * 100

    ranking = ranking.sort_values("Total", ascending=False)

    st.dataframe(ranking, use_container_width=True)

    st.divider()

    fig = px.bar(
        ranking.reset_index(),
        x="index",
        y="Total",
        color="Taxa Erro %",
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

# ================= PREVISÃO =================
elif pagina == "📈 Previsão":

    st.title("🔮 Previsão de Volume")

    timeline = df.groupby("dia").size().reset_index(name="Qtd")

    # 🔥 previsão simples (tendência)
    timeline["media"] = timeline["Qtd"].rolling(3).mean()

    futuro = timeline["media"].iloc[-1] if len(timeline) > 3 else timeline["Qtd"].mean()

    st.metric("📈 Previsão próximo dia", int(futuro))

    fig = px.line(
        timeline,
        x="dia",
        y=["Qtd", "media"],
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

# ================= POR DIA =================
elif pagina == "📅 Por Dia":

    st.title("📅 Análise por Dia")

    dias = sorted(df["dia"].dropna().unique())
    dia_sel = st.selectbox("Selecione", dias)

    df_dia = df[df["dia"] == dia_sel]

    col1, col2, col3 = st.columns(3)

    col1.metric("Total", len(df_dia))
    col2.metric("Categorizados", len(df_dia[df_dia["status"] == "Categorizado"]))
    col3.metric("Erros", len(df_dia[df_dia["status"] == "Erro"]))

    st.divider()

    fig = px.bar(
        df_dia["analista"].value_counts().reset_index(),
        x="index",
        y="analista",
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

# ================= DADOS =================
elif pagina == "📄 Dados":

    st.title("📄 Logs")

    st.dataframe(df, use_container_width=True)
