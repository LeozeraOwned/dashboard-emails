import streamlit as st
import pandas as pd
import plotly.express as px

# ================= CONFIG =================
st.set_page_config(layout="wide")

# ================= LOAD =================
df = pd.read_csv("log_emails.csv")
df["data"] = pd.to_datetime(df["data"], errors="coerce")
df["dia"] = df["data"].dt.date

# ================= SIDEBAR =================
st.sidebar.title("📊 MENU")

pagina = st.sidebar.radio(
    "Navegação",
    ["📊 Dashboard", "📈 Análises", "📅 Por Dia", "📄 Dados"]
)

# ================= DASHBOARD =================
if pagina == "📊 Dashboard":

    st.title("📊 Visão Geral")

    col1, col2, col3, col4, col5 = st.columns(5)

    total = len(df)
    categ = len(df[df["status"] == "Categorizado"])
    sem = len(df[df["status"] == "Sem categoria"])

    taxa = (categ / total * 100) if total > 0 else 0

    col1.metric("Total Emails", total)
    col2.metric("Categorizados", categ)
    col3.metric("Sem categoria", sem)
    col4.metric("Analistas", df["analista"].nunique())
    col5.metric("Taxa de acerto (%)", f"{taxa:.1f}%")

    st.divider()

    st.subheader("📌 Distribuição por Analista")

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

    timeline = df.groupby("dia").size().reset_index(name="Qtd")

    fig3 = px.line(
        timeline,
        x="dia",
        y="Qtd",
        markers=True,
        template="plotly_dark",
        title="Volume de Emails por Dia"
    )

    st.plotly_chart(fig3, use_container_width=True)

# ================= NOVA ABA =================
elif pagina == "📅 Por Dia":

    st.title("📅 Análise por Dia")

    # 📅 FILTRO DE DATA
    dias = sorted(df["dia"].dropna().unique())

    dia_sel = st.selectbox("Selecione o dia", dias)

    df_dia = df[df["dia"] == dia_sel]

    col1, col2, col3 = st.columns(3)

    col1.metric("Total", len(df_dia))
    col2.metric("Categorizados", len(df_dia[df_dia["status"] == "Categorizado"]))
    col3.metric("Sem categoria", len(df_dia[df_dia["status"] == "Sem categoria"]))

    st.divider()

    # 📊 POR ANALISTA NO DIA
    st.subheader("📊 Distribuição no Dia")

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

    st.divider()

    # 🔥 HEATMAP
    st.subheader("🔥 Heatmap Analista x Dia")

    heat = df.pivot_table(
        index="dia",
        columns="analista",
        aggfunc="size",
        fill_value=0
    )

    fig_heat = px.imshow(
        heat,
        text_auto=True,
        aspect="auto",
        template="plotly_dark"
    )

    st.plotly_chart(fig_heat, use_container_width=True)

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
