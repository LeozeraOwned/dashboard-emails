import streamlit as st
import pandas as pd
import plotly.express as px

# ================= CONFIG =================
st.set_page_config(layout="wide")

# ================= CSS =================
st.markdown("""
<style>
.card {
    padding: 20px;
    border-radius: 12px;
    background: linear-gradient(145deg, #1f1f1f, #2b2b2b);
    box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    text-align: center;
}
.card h3 {
    margin: 0;
    font-size: 18px;
    color: #aaa;
}
.card h1 {
    margin: 5px 0;
    font-size: 32px;
    color: #fff;
}
</style>
""", unsafe_allow_html=True)

# ================= LOAD =================
df = pd.read_csv("log_emails.csv")
df["data"] = pd.to_datetime(df["data"], errors="coerce")

df["dia"] = df["data"].dt.date
df["mes"] = df["data"].dt.strftime("%Y-%m")

# ================= SIDEBAR =================
st.sidebar.title("📊 MENU")

pagina = st.sidebar.radio(
    "Navegação",
    ["📊 Dashboard", "📈 Análises", "📅 Por Dia", "📄 Dados"]
)

# ================= DASHBOARD =================
if pagina == "📊 Dashboard":

    st.title("📊 Visão Geral")

    # 🔥 FILTROS
    colf1, colf2 = st.columns(2)

    meses = ["Todos"] + sorted(df["mes"].dropna().unique())
    mes_sel = colf1.selectbox("📅 Filtrar por mês", meses)

    dias = ["Todos"] + sorted(df["dia"].dropna().astype(str).unique())
    dia_sel = colf2.selectbox("📆 Filtrar por dia", dias)

    df_filtro = df.copy()

    if mes_sel != "Todos":
        df_filtro = df_filtro[df_filtro["mes"] == mes_sel]

    if dia_sel != "Todos":
        df_filtro = df_filtro[df_filtro["dia"].astype(str) == dia_sel]

    # ================= KPIs =================
    total = len(df_filtro)
    categ = len(df_filtro[df_filtro["status"] == "Categorizado"])
    erros = len(df_filtro[df_filtro["status"] == "Erro"])

    taxa = (categ / total * 100) if total > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f"""
    <div class="card">
        <h3>Total Emails</h3>
        <h1>{total}</h1>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
    <div class="card">
        <h3>Categorizados</h3>
        <h1>{categ}</h1>
    </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
    <div class="card">
        <h3>Erros</h3>
        <h1>{erros}</h1>
    </div>
    """, unsafe_allow_html=True)

    col4.markdown(f"""
    <div class="card">
        <h3>Taxa de acerto</h3>
        <h1>{taxa:.1f}%</h1>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # 📊 DISTRIBUIÇÃO
    st.subheader("📊 Distribuição por Analista")

    dist = df_filtro["analista"].value_counts().reset_index()
    dist.columns = ["Analista", "Qtd"]

    fig = px.bar(
        dist,
        x="Analista",
        y="Qtd",
        color="Analista",
        text="Qtd",
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

# ================= ANALISE =================
elif pagina == "📈 Análises":

    st.title("📈 Análises")

    col1, col2 = st.columns(2)

    dist = df["analista"].value_counts().reset_index()
    dist.columns = ["Analista", "Qtd"]

    fig1 = px.pie(
        dist,
        names="Analista",
        values="Qtd",
        hole=0.5,
        template="plotly_dark"
    )
    col1.plotly_chart(fig1, use_container_width=True)

    motivos = df["motivo"].value_counts().reset_index()
    motivos.columns = ["Motivo", "Qtd"]

    fig2 = px.bar(
        motivos,
        x="Qtd",
        y="Motivo",
        orientation="h",
        template="plotly_dark"
    )
    col2.plotly_chart(fig2, use_container_width=True)

    st.divider()

    timeline = df.groupby("dia").size().reset_index(name="Qtd")

    fig3 = px.line(
        timeline,
        x="dia",
        y="Qtd",
        markers=True,
        template="plotly_dark"
    )

    st.plotly_chart(fig3, use_container_width=True)

# ================= POR DIA =================
elif pagina == "📅 Por Dia":

    st.title("📅 Análise por Dia")

    dias = sorted(df["dia"].dropna().unique())

    dia_sel = st.selectbox("Selecione o dia", dias)

    df_dia = df[df["dia"] == dia_sel]

    # 🔥 KPIs
    col1, col2, col3 = st.columns(3)

    col1.metric("Total", len(df_dia))
    col2.metric("Categorizados", len(df_dia[df_dia["status"] == "Categorizado"]))
    col3.metric("Erros", len(df_dia[df_dia["status"] == "Erro"]))

    st.divider()

    # 📊 GRÁFICO
    st.subheader("📊 Distribuição no Dia")

    dist_dia = df_dia["analista"].value_counts().reset_index()
    dist_dia.columns = ["Analista", "Qtd"]

    fig_dia = px.bar(
        dist_dia,
        x="Analista",
        y="Qtd",
        color="Analista",
        text="Qtd",
        template="plotly_dark"
    )

    st.plotly_chart(fig_dia, use_container_width=True)

    st.divider()

    # 📄 TABELA FORMATADA
    st.subheader("📄 Detalhamento")

    df_dia_formatado = df_dia.copy()
    df_dia_formatado["data"] = df_dia_formatado["data"].dt.strftime("%d/%m/%Y %H:%M")

    st.dataframe(df_dia_formatado, use_container_width=True)

# ================= DADOS =================
elif pagina == "📄 Dados":

    st.title("📄 Logs")

    analista = st.selectbox(
        "Filtrar por analista",
        ["Todos"] + sorted(df["analista"].dropna().unique())
    )

    df_final = df if analista == "Todos" else df[df["analista"] == analista]

    st.dataframe(df_final, use_container_width=True)

    if st.button("📥 Exportar CSV"):
        df_final.to_csv("export.csv", index=False)
        st.success("Exportado!")
