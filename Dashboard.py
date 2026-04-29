import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# ================= CSS (INALTERADO) =================
st.markdown("""<style>
/* TODO O SEU CSS DE ANIMAÇÃO PERMANECE IGUAL */
</style>""", unsafe_allow_html=True)

# ================= LOAD =================
df = pd.read_csv("log_emails.csv")

df["data"] = pd.to_datetime(df["data"], errors="coerce")

# 🔒 SOMENTE HOJE PRA FRENTE
hoje = pd.Timestamp.now().date()
df = df[df["data"].dt.date >= hoje].copy()

df["dia"] = df["data"].dt.date
df["mes"] = df["data"].dt.month

df["status"] = df["status"].fillna("").astype(str).str.strip()
df["analista"] = df["analista"].fillna("").astype(str).str.strip()
df["assunto"] = df["assunto"].fillna("").astype(str).str.strip()

df["analista_exibicao"] = df["analista"].replace("", "Sem analista")

# ================= FILTROS =================
st.sidebar.title("📊 MENU")

pagina = st.sidebar.radio(
    "Navegação",
    ["📊 Dashboard", "📈 Análises", "📅 Por Dia", "📄 Dados"]
)

meses = sorted(df["mes"].dropna().unique())
mes_sel = st.sidebar.selectbox("Mês", ["Todos"] + list(meses))

dias_base = df if mes_sel == "Todos" else df[df["mes"] == mes_sel]
dias = sorted(dias_base["dia"].dropna().unique())
dia_sel = st.sidebar.selectbox("Dia", ["Todos"] + list(dias))

df_f = df.copy()
if mes_sel != "Todos":
    df_f = df_f[df_f["mes"] == mes_sel]
if dia_sel != "Todos":
    df_f = df_f[df_f["dia"] == dia_sel]

# ================= FUNÇÕES =================
def card(icon, valor, label, extra_class="", animate=False):
    anim = "animate-once" if animate else ""
    return f"""
    <div class="card">
        <div class="content">
            {icon}
            <div class="big {extra_class} {anim}">{valor}</div>
            <div class="small">{label}</div>
        </div>
    </div>
    """

def resumo_categorizacao(df):
    total = len(df)

    total_categorizados = df["status"].isin(
        ["Categorizado", "Erro", "Correto"]
    ).sum()

    categ_errados = (df["status"] == "Erro").sum()
    categ_certos = total_categorizados - categ_errados

    sem_categoria = (df["status"] == "Sem categoria").sum()

    return total, total_categorizados, categ_certos, categ_errados, sem_categoria

# ================= DASHBOARD =================
if pagina == "📊 Dashboard":

    st.title("🚀 Painel Inteligente")

    total, total_categ, certos, errados, sem_cat = resumo_categorizacao(df_f)

    animar = st.session_state.get("animar_cards", True)

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.markdown(card("📩", total, "Total", animate=animar), unsafe_allow_html=True)
    col2.markdown(card("📌", total_categ, "Total categorizados", animate=animar), unsafe_allow_html=True)
    col3.markdown(card("✅", certos, "Categorizados certos", "pulse-green", animate=animar), unsafe_allow_html=True)
    col4.markdown(card("❌", errados, "Categorizados errados", "pulse-red", animate=animar), unsafe_allow_html=True)
    col5.markdown(card("🚫", sem_cat, "Sem categoria", animate=animar), unsafe_allow_html=True)

    st.divider()

    st.subheader("📊 Volume por Analista")

    dist = (
        df_f["analista_exibicao"]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "Analista", "analista_exibicao": "Qtd"})
    )

    fig = px.bar(
        dist,
        x="Analista",
        y="Qtd",
        text="Qtd",
        template="plotly_dark"
    )

    fig.update_layout(transition_duration=800)
    st.plotly_chart(fig, use_container_width=True)

# ================= DADOS =================
elif pagina == "📄 Dados":
    st.title("📄 Logs")
    st.dataframe(df_f, use_container_width=True)




