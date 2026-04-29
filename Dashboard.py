import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# ================= CSS ULTRA (ORIGINAL – ANIMAÇÕES RESTAURADAS) =================
st.markdown("""
<style>

/* FUNDO */
body {
    background-color: #0e1117;
}

/* SIDEBAR ANIMADA */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0e1117, #111827);
    box-shadow: 0 0 20px rgba(0,255,224,0.35);
    animation: glowMenu 2.4s infinite alternate;
}

@keyframes glowMenu {
    from { box-shadow: 0 0 8px rgba(0,255,224,0.18); }
    to { box-shadow: 0 0 24px rgba(0,255,224,0.35); }
}

/* ================= MENU ANIMADO ================= */
section[data-testid="stSidebar"] div[role="radiogroup"] {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label {
    position: relative;
    padding: 10px 14px;
    border-radius: 14px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    transition: all 0.35s ease;
    overflow: hidden;
    cursor: pointer;
    animation: menuEnter 0.6s ease forwards;
}

@keyframes menuEnter {
    from { opacity: 0; transform: translateX(-12px); }
    to { opacity: 1; transform: translateX(0); }
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label::after {
    content: "";
    position: absolute;
    left: 0;
    top: 15%;
    width: 4px;
    height: 70%;
    background: linear-gradient(180deg, #00ffe0, #007cf0);
    opacity: 0;
    transition: all 0.3s ease;
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    transform: translateX(6px);
    background: rgba(0,255,224,0.08);
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover::after {
    opacity: 1;
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked)::after {
    opacity: 1;
    animation: activePulse 1.4s infinite;
}

@keyframes activePulse {
    0% { box-shadow: 0 0 8px rgba(0,255,224,0.4); }
    50% { box-shadow: 0 0 18px rgba(0,255,224,0.9); }
    100% { box-shadow: 0 0 8px rgba(0,255,224,0.4); }
}

/* ================= CARDS ================= */
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

@keyframes borderMove {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.content {
    position: relative;
    z-index: 2;
}

.big {
    font-size: 32px;
    font-weight: bold;
}

.small {
    color: #aaa;
}

.animate-once {
    animation: popOnce 0.8s ease-out 1;
}

@keyframes popOnce {
    0% { opacity: 0; transform: translateY(12px) scale(0.96); }
    100% { opacity: 1; transform: translateY(0) scale(1); }
}

.pulse-green { color: #00ff9f; }
.pulse-red { color: #ff4d4d; }

.plotly .bars path {
    transition: all 0.8s ease-in-out !important;
}

</style>
""", unsafe_allow_html=True)

# ================= LOAD =================
df = pd.read_csv("log_emails.csv")
df["data"] = pd.to_datetime(df["data"], errors="coerce")

# ✅ SOMENTE HOJE PRA FRENTE
hoje = pd.Timestamp.now().date()
df = df[df["data"].dt.date >= hoje].copy()

df["status"] = df["status"].fillna("").astype(str).str.strip()
df["analista"] = df["analista"].fillna("").astype(str).str.strip()
df["analista_exibicao"] = df["analista"].replace("", "Sem analista")

# ================= SIDEBAR =================
st.sidebar.title("📊 MENU")
pagina = st.sidebar.radio(
    "Navegação",
    ["📊 Dashboard", "📄 Dados"]
)

# ================= FUNÇÕES =================
def card(icon, valor, label, extra="", animate=True):
    anim = "animate-once" if animate else ""
    return f"""
    <div class="card">
        <div class="content">
            {icon}
            <div class="big {extra} {anim}">{valor}</div>
            <div class="small">{label}</div>
        </div>
    </div>
    """

def resumo(df):
    total = len(df)
    total_categ = df["status"].isin(["Categorizado", "Erro", "Correto"]).sum()
    errados = (df["status"] == "Erro").sum()
    certos = total_categ - errados
    sem_cat = (df["status"] == "Sem categoria").sum()
    return total, total_categ, certos, errados, sem_cat

# ================= DASHBOARD =================
if pagina == "📊 Dashboard":

    st.title("🚀 Painel Inteligente")

    total, total_categ, certos, errados, sem_cat = resumo(df)

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.markdown(card("📩", total, "Total"), unsafe_allow_html=True)
    c2.markdown(card("📌", total_categ, "Total categorizados"), unsafe_allow_html=True)
    c3.markdown(card("✅", certos, "Categorizados certos", "pulse-green"), unsafe_allow_html=True)
    c4.markdown(card("❌", errados, "Categorizados errados", "pulse-red"), unsafe_allow_html=True)
    c5.markdown(card("🚫", sem_cat, "Sem categoria"), unsafe_allow_html=True)

    st.divider()
    st.subheader("📊 Volume por Analista")

    dist = (
        df.groupby("analista_exibicao")
        .size()
        .reset_index(name="Qtd")
    )

    fig = px.bar(
        dist,
        x="analista_exibicao",
        y="Qtd",
        text="Qtd",
        template="plotly_dark"
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(transition_duration=800)

    st.plotly_chart(fig, use_container_width=True)

# ================= DADOS =================
elif pagina == "📄 Dados":
    st.title("📄 Logs")
    st.dataframe(df, use_container_width=True)




