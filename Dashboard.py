import streamlit as st
import pandas as pd
import plotly.express as px

# ================= CONFIG =================
st.set_page_config(layout="wide")

# ================= CSS TOP =================
st.markdown("""
<style>
.card {
    background: linear-gradient(135deg, #1f1f1f, #2c2c2c);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0px 0px 20px rgba(0,255,200,0.2);
    transition: 0.3s;
}
.card:hover {
    transform: scale(1.05);
}
.big {
    font-size: 28px;
    font-weight: bold;
}
.small {
    color: #aaa;
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

# ================= FILTROS GLOBAIS =================
st.sidebar.subheader("📅 Filtros")

meses = sorted(df["mes"].dropna().unique())
mes_sel = st.sidebar.selectbox("Mês", ["Todos"] + list(meses))

dias = sorted(df["dia"].dropna().unique())
dia_sel = st.sidebar.selectbox("Dia", ["Todos"] + list(dias))

df_filtro = df.copy()

if mes_sel != "Todos":
    df_filtro = df_filtro[df_filtro["mes"] == mes_sel]

if dia_sel != "Todos":
    df_filtro = df_filtro[df_filtro["dia"] == dia_sel]

# ================= DASHBOARD =================
if pagina == "📊 Dashboard":

    st.title("📊 Visão Geral")

    total = len(df_filtro)
    categ = len(df_filtro[df_filtro["status"] == "Categorizado"])
    sem = len(df_filtro[df_filtro["status"] == "Sem categoria"])
    taxa = (categ / total * 100) if total > 0 else 0

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.markdown(f'<div class="card"><div class="big">{total}</div><div class="small">Total</div></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="card"><div class="big">{categ}</div><div class="small">Categorizados</div></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="card"><div class="big">{sem}</div><div class="small">Sem categoria</div></div>', unsafe_allow_html=True)
    col4.markdown(f'<div class="card"><div class="big">{df_filtro["analista"].nunique()}</div><div class="small">Analistas</div></div>', unsafe_allow_html=True)
    col5.markdown(f'<div class="card"><div class="big">{taxa:.1f}%</div><div class="small">Taxa acerto</div></div>', unsafe_allow_html=True)

    st.divider()

    # 🔥 ALERTA INTELIGENTE
    if taxa < 70:
        st.error("⚠️ Baixa precisão! Muitos erros detectados")
    elif taxa < 90:
        st.warning("⚠️ Pode melhorar...")
    else:
        st.success("🔥 Performance alta!")

    st.divider()

    # 📊 DISTRIBUIÇÃO
    st.subheader("📊 Distribuição por Analista")

    dist = df_filtro["analista"].value_counts().reset_index()
    dist.columns = ["Analista", "Quantidade"]

    fig = px.bar(
        dist,
        x="Analista",
        y="Quantidade",
        color="Analista",
        template="plotly_dark",
        text="Quantidade"
    )

    st.plotly_chart(fig, use_container_width=True)

    # 🏆 RANKING (CORRIGIDO)
    st.subheader("🏆 Ranking de Analistas")

    ranking = df_filtro["analista"].dropna().value_counts().reset_index()
    ranking.columns = ["Analista", "Qtd"]

    if not ranking.empty:
        fig_rank = px.bar(
            ranking,
            x="Analista",
            y="Qtd",
            text="Qtd",
            template="plotly_dark",
            color="Analista"
        )
        st.plotly_chart(fig_rank, use_container_width=True)
    else:
        st.info("Sem dados para ranking")

# ================= ANALISE =================
elif pagina == "📈 Análises":

    st.title("📈 Análises Detalhadas")

    col1, col2 = st.columns(2)

    dist = df_filtro["analista"].value_counts().reset_index()
    dist.columns = ["Analista", "Qtd"]

    fig1 = px.pie(
        dist,
        names="Analista",
        values="Qtd",
        hole=0.5,
        template="plotly_dark"
    )
    col1.plotly_chart(fig1, use_container_width=True)

    motivos = df_filtro["motivo"].value_counts().reset_index()
    motivos.columns = ["Motivo", "Qtd"]

    fig2 = px.bar(
        motivos,
        x="Qtd",
        y="Motivo",
        orientation="h",
        template="plotly_dark",
        color="Qtd"
    )
    col2.plotly_chart(fig2, use_container_width=True)

    st.divider()

    timeline = df_filtro.groupby("dia").size().reset_index(name="Qtd")

    fig3 = px.line(
        timeline,
        x="dia",
        y="Qtd",
        markers=True,
        template="plotly_dark",
        title="Volume de Emails por Dia"
    )

    st.plotly_chart(fig3, use_container_width=True)

# ================= POR DIA =================
elif pagina == "📅 Por Dia":

    st.title("📅 Análise por Dia")

    dias = sorted(df["dia"].dropna().unique())
    dia_sel = st.selectbox("Selecione o dia", dias)

    df_dia = df[df["dia"] == dia_sel]

    col1, col2, col3 = st.columns(3)

    col1.metric("Total", len(df_dia))
    col2.metric("Categorizados", len(df_dia[df_dia["status"] == "Categorizado"]))
    col3.metric("Sem categoria", len(df_dia[df_dia["status"] == "Sem categoria"]))

    st.divider()

    dist_dia = df_dia["analista"].value_counts().reset_index()
    dist_dia.columns = ["Analista", "Qtd"]

    fig_dia = px.bar(
        dist_dia,
        x="Analista",
        y="Qtd",
        color="Analista",
        template="plotly_dark",
        text="Qtd"
    )

    st.plotly_chart(fig_dia, use_container_width=True)

# ================= DADOS =================
elif pagina == "📄 Dados":

    st.title("📄 Logs Detalhados")

    analista = st.selectbox(
        "Filtrar por analista",
        ["Todos"] + sorted(df["analista"].dropna().unique())
    )

    df_final = df if analista == "Todos" else df[df["analista"] == analista]

    st.dataframe(df_final, use_container_width=True)

    if st.button("📥 Exportar CSV"):
        df_final.to_csv("export.csv", index=False)
        st.success("Arquivo exportado!")
