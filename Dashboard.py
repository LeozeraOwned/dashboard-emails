import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(layout="wide")

# ================= CSS ULTRA =================
st.markdown("""
<style>
/* (CSS mantido exatamente igual) */
</style>
""", unsafe_allow_html=True)

# ================= LOAD =================
df = pd.read_csv("log_emails.csv")

# Normalização básica
df.columns = [c.strip() for c in df.columns]

df["data"] = pd.to_datetime(df["data"], errors="coerce")

# 🔥 FILTRO: somente hoje em diante
hoje = pd.Timestamp.now().normalize()
df = df[df["data"] >= hoje]

df["dia"] = df["data"].dt.date
df["mes"] = df["data"].dt.month

df["assunto"] = df["assunto"].fillna("").astype(str).str.strip()
df["analista"] = df["analista"].fillna("").astype(str).str.strip()
df["motivo"] = df["motivo"].fillna("").astype(str).str.strip()
df["status"] = df["status"].fillna("").astype(str).str.strip()

df["analista_exibicao"] = df["analista"].replace("", "Sem analista")

# ORDEM FIXA DOS ANALISTAS
all_analistas = sorted(df["analista_exibicao"].dropna().astype(str).unique().tolist())
max_qtd_analista = int(df["analista_exibicao"].value_counts().max()) if not df.empty else 1

# ================= SIDEBAR =================
st.sidebar.title("📊 MENU")

pagina = st.sidebar.radio(
    "Navegação",
    ["📊 Dashboard", "📈 Análises", "📅 Por Dia", "📄 Dados"]
)

# ================= FILTROS =================
meses = sorted([int(m) for m in df["mes"].dropna().unique()])
mes_sel = st.sidebar.selectbox("Mês", ["Todos"] + list(meses))

dias_base = df.copy()
if mes_sel != "Todos":
    dias_base = dias_base[dias_base["mes"] == mes_sel]

dias = sorted(dias_base["dia"].dropna().unique())
dia_sel = st.sidebar.selectbox("Dia", ["Todos"] + list(dias))

df_f = df.copy()

if mes_sel != "Todos":
    df_f = df_f[df_f["mes"] == mes_sel]

if dia_sel != "Todos":
    df_f = df_f[df_f["dia"] == dia_sel]

# ================= CONTROLE DE ANIMAÇÃO =================
filtro_key = f"{mes_sel}|{dia_sel}"

if "last_filter_key" not in st.session_state:
    st.session_state["last_filter_key"] = filtro_key
    st.session_state["animar_cards"] = True
elif st.session_state["last_filter_key"] != filtro_key:
    st.session_state["last_filter_key"] = filtro_key
    st.session_state["animar_cards"] = True
else:
    st.session_state["animar_cards"] = False

# ================= FUNÇÕES =================
def card(icon, valor, label, extra_class="", animate=False):
    anim_class = "animate-once" if animate else ""
    return f"""
    <div class="card">
        <div class="content">
            {icon}
            <div class="big {extra_class} {anim_class}">{valor}</div>
            <div class="small">{label}</div>
        </div>
    </div>
    """

def get_dist_analista(dataframe):
    contagem = (
        dataframe["analista_exibicao"]
        .astype(str)
        .value_counts()
        .reindex(all_analistas, fill_value=0)
    )

    dist = pd.DataFrame({
        "Analista": all_analistas,
        "Qtd": contagem.values
    })
    return dist

def calcular_resumo_categorizacao(dataframe):
    status_norm = dataframe["status"].astype(str).str.strip().str.lower()
    motivo_norm = dataframe["motivo"].astype(str).str.strip().str.lower()

    total_categorizados = int(status_norm.isin(["categorizado", "correto", "erro"]).sum())

    categorizados_certos = int(
        ((status_norm == "correto") | ((status_norm == "erro") & (motivo_norm == "humano removeu categoria"))).sum()
    )

    categorizados_errados = int(
        ((status_norm == "erro") & (motivo_norm != "humano removeu categoria")).sum()
    )

    pendentes_validacao = int((status_norm == "categorizado").sum())

    return total_categorizados, categorizados_certos, categorizados_errados, pendentes_validacao

def formatar_data_pt(valor):
    if pd.isna(valor):
        return ""
    try:
        return pd.to_datetime(valor).strftime("%d/%m/%Y %H:%M")
    except:
        return ""

# ================= DASHBOARD =================
if pagina == "📊 Dashboard":

    st.title("🚀 Painel Inteligente")

    total = len(df_f)
    total_categorizados, categorizados_certos, categorizados_errados, pendentes_validacao = calcular_resumo_categorizacao(df_f)

    col1, col2, col3, col4 = st.columns(4)
    animar = st.session_state.get("animar_cards", False)

    col1.markdown(card("📩", total, "Total", animate=animar), unsafe_allow_html=True)
    col2.markdown(card("📌", total_categorizados, "Total categorizados", animate=animar), unsafe_allow_html=True)
    col3.markdown(card("✅", categorizados_certos, "Categorizados certos", "pulse-green", animate=animar), unsafe_allow_html=True)
    col4.markdown(card("❌", categorizados_errados, "Categorizados errados", "pulse-red", animate=animar), unsafe_allow_html=True)

    st.caption(f"Pendentes de validação: {pendentes_validacao}")

    st.divider()

    st.subheader("📊 Volume por Analista")

    dist = get_dist_analista(df_f)

    fig = px.bar(
        dist,
        x="Analista",
        y="Qtd",
        color="Analista",
        text="Qtd",
        template="plotly_dark",
        category_orders={"Analista": all_analistas}
    )

    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_xaxes(categoryorder="array", categoryarray=all_analistas)
    fig.update_yaxes(range=[0, max_qtd_analista + 5])
    fig.update_layout(
        transition_duration=800,
        showlegend=True,
        xaxis_title="Analista",
        yaxis_title="Qtd"
    )

    st.plotly_chart(fig, use_container_width=True)

# ================= ANÁLISES =================
elif pagina == "📈 Análises":

    st.title("📈 Performance Geral")

    total_categorizados, categorizados_certos, categorizados_errados, pendentes_validacao = calcular_resumo_categorizacao(df_f)

    revisados = categorizados_certos + categorizados_errados
    qualidade_categorizacao = (
        categorizados_certos / revisados * 100
        if revisados > 0 else 0
    )

    if qualidade_categorizacao >= 85:
        cor_taxa = "#00e5ff"
    elif qualidade_categorizacao >= 50:
        cor_taxa = "#ffd54f"
    else:
        cor_taxa = "#ff4d4d"

    restante = max(0, 100 - qualidade_categorizacao)

    fig = go.Figure(
        data=[
            go.Pie(
                values=[qualidade_categorizacao, restante],
                hole=0.78,
                sort=False,
                direction="clockwise",
                rotation=90,
                textinfo="none",
                hoverinfo="skip",
                marker=dict(
                    colors=[cor_taxa, "rgba(255,255,255,0.08)"],
                    line=dict(color="#0e1117", width=2)
                )
            )
        ]
    )

    fig.update_layout(template="plotly_dark")

    st.plotly_chart(fig, use_container_width=True)




