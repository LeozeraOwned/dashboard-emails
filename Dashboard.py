import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# ================= CSS ULTRA (INALTERADO) =================
st.markdown("""
<style>

/* FUNDO */
body { background-color: #0e1117; }

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0e1117, #111827);
    box-shadow: 0 0 20px #00ffe0;
    animation: glowMenu 2s infinite alternate;
}

@keyframes glowMenu {
    from { box-shadow: 0 0 5px #00ffe0; }
    to { box-shadow: 0 0 25px #00ffe0; }
}

/* MENU */
section[data-testid="stSidebar"] div[role="radiogroup"] > label {
    position: relative;
    padding: 10px 14px;
    border-radius: 14px;
    transition: all .3s ease;
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    transform: translateX(6px);
    background: rgba(0,255,224,.08);
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

.card::before {
    content: "";
    position: absolute;
    inset: -2px;
    background: linear-gradient(90deg,#00ffe0,#007cf0,#00ffe0);
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

@keyframes borderMove {
    0% {transform: rotate(0deg);}
    100% {transform: rotate(360deg);}
}

.content { position: relative; z-index: 2; }
.big { font-size: 32px; font-weight: bold; }
.small { color: #aaa; }

.animate-once { animation: popOnce .8s ease-out 1; }

@keyframes popOnce {
    from { opacity:0; transform: translateY(12px) scale(.96); }
    to { opacity:1; transform:none; }
}

.pulse-green { color:#00ff9f; }
.pulse-red { color:#ff4d4d; }

.plotly .bars path {
    transition: all .8s ease-in-out !important;
}

</style>
""", unsafe_allow_html=True)

# ================= LOAD =================
df = pd.read_csv("log_emails.csv", sep=";")
df["data"] = pd.to_datetime(df["data"], errors="coerce")

# ✅ SOMENTE HOJE PRA FRENTE
hoje = pd.Timestamp.now().date()
df = df[df["data"].dt.date >= hoje].copy()

df["dia"] = df["data"].dt.date
df["mes"] = df["data"].dt.month
df["status"] = df["status"].fillna("").astype(str).str.strip()
df["motivo"] = df["motivo"].fillna("").astype(str).str.strip()
df["analista"] = df["analista"].fillna("").astype(str).str.strip()
df["assunto"] = df["assunto"].fillna("").astype(str).str.strip()
df["analista_exibicao"] = df["analista"].replace("", "Sem analista")

# ================= DATAFRAME DE PERFORMANCE (INALTERADO) =================
df_perf = df[
    ~(
        (df["status"] == "Sem categoria") &
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
def card(icon, valor, label, extra=""):
    return f"""
    <div class="card">
        <div class="content">
            {icon}
            <div class="big {extra} animate-once">{valor}</div>
            <div class="small">{label}</div>
        </div>
    </div>
    """

def resumo(df):
    total = len(df)
    total_categ = df["status"].isin(["Categorizado","Erro","Correto"]).sum()
    errados = (df["status"]=="Erro").sum()
    certos = total_categ - errados
    sem_cat = (df["status"]=="Sem categoria").sum()
    return total,total_categ,certos,errados,sem_cat

# ================= DASHBOARD =================
if pagina=="📊 Dashboard":
    st.title("🚀 Painel Inteligente")

    total,total_categ,certos,errados,sem_cat = resumo(df_perf_f)
    c1,c2,c3,c4,c5 = st.columns(5)

    c1.markdown(card("📩",total,"Total"),unsafe_allow_html=True)
    c2.markdown(card("📌",total_categ,"Total categorizados"),unsafe_allow_html=True)
    c3.markdown(card("✅",certos,"Categorizados certos","pulse-green"),unsafe_allow_html=True)
    c4.markdown(card("❌",errados,"Categorizados errados","pulse-red"),unsafe_allow_html=True)
    c5.markdown(card("🚫",sem_cat,"Sem categoria"),unsafe_allow_html=True)

    st.divider()
    st.subheader("📊 Volume por Analista")

    # ✅ CORREÇÃO CONCEITUAL: somente decisões do modelo
    dist = (
        df_perf_f[df_perf_f["tipo_evento"] == "modelo"]
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

    fig.update_layout(transition_duration=800)
    st.plotly_chart(fig, use_container_width=True)

# ================= ANÁLISES =================
elif pagina=="📈 Análises":
    st.title("📈 Análises")

    _,total_categ,certos,errados,_ = resumo(df_perf_f)
    qualidade = (certos/total_categ*100) if total_categ > 0 else 0

    fig = go.Figure(
        data=[go.Pie(
            labels=["Categorizados certos","Categorizados errados"],
            values=[certos,errados],
            hole=.72,
            marker=dict(colors=["#00ff9f","#ff4d4d"]),
            textinfo="percent"
        )]
    )

    fig.update_layout(
        template="plotly_dark",
        annotations=[dict(
            text=f"<b>{qualidade:.1f}%</b><br>Qualidade",
            x=.5,y=.5,showarrow=False,font=dict(size=26)
        )],
        transition_duration=800
    )

    st.plotly_chart(fig, use_container_width=True)

# ================= POR DIA =================
elif pagina=="📅 Por Dia":
    st.title("📅 Por Dia")

    st.subheader("📉 Evolução de erros por dia")

    erros_por_dia = (
        df_perf_f[df_perf_f["status"]=="Erro"]
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

    fig.update_traces(line=dict(width=3), marker=dict(size=8))
    fig.update_layout(
        transition_duration=800,
        xaxis_title="Dia",
        yaxis_title="Qtd de erros"
    )

    st.plotly_chart(fig, use_container_width=True)

# ================= DADOS =================
elif pagina=="📄 Dados":
    st.title("📄 Logs")
    st.dataframe(df_f,use_container_width=True)






