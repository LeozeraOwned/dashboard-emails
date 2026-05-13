import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# ================= LOAD =================
url = "https://raw.githubusercontent.com/LeozeraOwned/dashboard-emails/main/log_emails.csv"

df = pd.read_csv(url, sep=";", on_bad_lines="skip")

# ================= TRATAMENTO =================

# ✅ Corrige o T da data
df["data"] = df["data"].astype(str).str.replace("T", " ")

df["data"] = pd.to_datetime(df["data"], errors="coerce")

# remove linhas inválidas
df = df.dropna(subset=["data"])

df["dia"] = df["data"].dt.date
df["mes"] = df["data"].dt.month

# ✅ CORREÇÃO PRINCIPAL (STATUS)
df["status"] = (
    df["status"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.lower()
    .str.replace(";", "")
)

df["motivo"] = df["motivo"].fillna("").astype(str).str.strip()
df["analista"] = df["analista"].fillna("").astype(str).str.strip()
df["assunto"] = df["assunto"].fillna("").astype(str).str.strip()

df["analista_exibicao"] = df["analista"].replace("", "Sem analista")

# ================= FILTRO =================
df_perf = df[
    ~(
        (df["status"] == "sem categoria") &
        (df["motivo"].str.lower() == "aprendido: não categorizar")
    )
].copy()

# ================= SIDEBAR =================
st.sidebar.title("📊 MENU")

pagina = st.sidebar.radio(
    "Navegação",
    ["📊 Dashboard", "📈 Análises", "📅 Por Dia", "📄 Dados"]
)

# ================= FILTROS =================
meses = sorted(df["mes"].dropna().unique())
mes_sel = st.sidebar.selectbox("Mês", ["Todos"] + list(meses))

dias_base = df if mes_sel == "Todos" else df[df["mes"] == mes_sel]
dias = sorted(dias_base["dia"].dropna().unique())
dia_sel = st.sidebar.selectbox("Dia", ["Todos"] + list(dias))

df_f = df.copy()
df_perf_f = df_perf.copy()

if mes_sel != "Todos":
    df_f = df_f[df_f["mes"] == mes_sel]
    df_perf_f = df_perf_f[df_perf_f["mes"] == mes_sel]

if dia_sel != "Todos":
    df_f = df_f[df_f["dia"] == dia_sel]
    df_perf_f = df_perf_f[df_perf_f["dia"] == dia_sel]

# ================= FUNÇÕES =================
def card(icon, valor, label):
    return f"""
    <div style="background:#1a1f2b;padding:20px;border-radius:15px;text-align:center;">
        <div style="font-size:24px">{icon}</div>
        <div style="font-size:30px;font-weight:bold">{valor}</div>
        <div style="color:#aaa">{label}</div>
    </div>
    """

def resumo(df):
    total = len(df)
    total_categ = df["status"].isin(["categorizado","erro","correto"]).sum()
    errados = (df["status"] == "erro").sum()
    certos = total_categ - errados
    sem_cat = (df["status"] == "sem categoria").sum()
    return total, total_categ, certos, errados, sem_cat

# ================= DASHBOARD =================
if pagina == "📊 Dashboard":

    st.title("🚀 Painel Inteligente")
    st.caption(f"📅 Último dado carregado: {df['data'].max()}")

    total, total_categ, certos, errados, sem_cat = resumo(df_perf_f)

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.markdown(card("📩", total, "Total"), unsafe_allow_html=True)
    c2.markdown(card("📌", total_categ, "Total categorizados"), unsafe_allow_html=True)
    c3.markdown(card("✅", certos, "Categorizados certos"), unsafe_allow_html=True)
    c4.markdown(card("❌", errados, "Categorizados errados"), unsafe_allow_html=True)
    c5.markdown(card("🚫", sem_cat, "Sem categoria"), unsafe_allow_html=True)

    st.divider()
    st.subheader("📊 Volume por Analista")

    dist = (
        df_perf_f
        .groupby("analista_exibicao")
        .size()
        .reset_index(name="Qtd")
    )

    fig = px.bar(
        dist,
        x="analista_exibicao",
        y="Qtd",
        color="analista_exibicao",
        text="Qtd",
        template="plotly_dark"
    )

    fig.update_traces(textposition="outside")

    st.plotly_chart(fig, use_container_width=True)

# ================= ANÁLISES =================
elif pagina == "📈 Análises":

    st.title("📈 Análises")

    _, total_categ, certos, errados, _ = resumo(df_perf_f)

    qualidade = (certos / total_categ * 100) if total_categ > 0 else 0

    fig = go.Figure(
        data=[go.Pie(
            labels=["Certos", "Errados"],
            values=[certos, errados],
            hole=.7,
            marker=dict(colors=["#00ff9f", "#ff4d4d"])
        )]
    )

    fig.update_layout(
        template="plotly_dark",
        annotations=[dict(
            text=f"<b>{qualidade:.1f}%</b><br>Qualidade",
            x=.5, y=.5,
            showarrow=False
        )]
    )

    st.plotly_chart(fig, use_container_width=True)

# ================= POR DIA =================
elif pagina == "📅 Por Dia":

    st.title("📅 Erros por Dia")

    erros_por_dia = (
        df_perf_f[df_perf_f["status"] == "erro"]
        .groupby("dia")
        .size()
        .reset_index(name="Qtd")
        .sort_values("dia")
    )

    fig = px.line(
        erros_por_dia,
        x="dia",
        y="Qtd",
        markers=True,
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

# ================= DADOS =================
elif pagina == "📄 Dados":

    st.title("📄 Logs")

    st.dataframe(df_f, use_container_width=True)












