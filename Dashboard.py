import streamlit as st
import pandas as pd
import plotly.express as px

# ================= CONFIG =================
st.set_page_config(layout="wide")

# ✅ LER DO REPOSITÓRIO
df = pd.read_csv("log_emails.csv")
df["data"] = pd.to_datetime(df["data"], errors="coerce")

# ================= SIDEBAR =================
st.sidebar.title("📊 MENU")

pagina = st.sidebar.radio(
    "Navegação",
    ["📊 Dashboard", "📈 Análises", "📄 Dados"]
)

# ================= DASHBOARD =================
if pagina == "📊 Dashboard":

    st.title("📊 Visão Geral")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Emails", len(df))
    col2.metric("Categorizados", len(df[df["status"] == "Categorizado"]))
    col3.metric("Sem categoria", len(df[df["status"] == "Sem categoria"]))
    col4.metric("Analistas", df["analista"].nunique())

    st.divider()

    st.subheader("📌 Distribuição")

    dist = df["analista"].value_counts().reset_index()
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

# ================= ANALISE =================
elif pagina == "📈 Análises":

    st.title("📈 Análises Detalhadas")

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
        template="plotly_dark",
        color="Qtd"
    )
    col2.plotly_chart(fig2, use_container_width=True)

    st.divider()

    df["dia"] = df["data"].dt.date
    timeline = df.groupby("dia").size().reset_index(name="Qtd")

    fig3 = px.line(
        timeline,
        x="dia",
        y="Qtd",
        markers=True,
        template="plotly_dark"
    )

    st.plotly_chart(fig3, use_container_width=True)

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
