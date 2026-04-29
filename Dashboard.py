import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# ================= CSS =================
st.markdown("""
<style>
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0e1117, #111827);
    box-shadow: 0 0 25px #00ffe0;
}

.card {
    background: #1a1f2b;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    animation: float 3s ease-in-out infinite;
}

@keyframes float {
    0% {transform: translateY(0px);}
    50% {transform: translateY(-5px);}
    100% {transform: translateY(0px);}
}

.pulse-green {color:#00ff9f; animation:pulse 1s infinite;}
.pulse-red {color:#ff4d4d; animation:pulse 1s infinite;}

@keyframes pulse {
    0% {opacity:1;}
    50% {opacity:0.3;}
    100% {opacity:1;}
}
</style>
""", unsafe_allow_html=True)

# ================= LOAD =================
df = pd.read_csv("log_emails.csv")

df["data"] = pd.to_datetime(df["data"], errors="coerce")
df["dia"] = df["data"].dt.date
df["mes"] = df["data"].dt.month

# ================= SIDEBAR =================
st.sidebar.title("⚡ MENU INTERATIVO")

pagina = st.sidebar.radio(
    "Navegação",
    ["📊 Dashboard", "📈 Análises", "📅 Por Dia", "📄 Dados"]
)

mes = st.sidebar.selectbox("Mês", ["Todos"] + sorted(df["mes"].dropna().unique()))
dia = st.sidebar.selectbox("Dia", ["Todos"] + sorted(df["dia"].dropna().unique()))

df_f = df.copy()

if mes != "Todos":
    df_f = df_f[df_f["mes"] == mes]

if dia != "Todos":
    df_f = df_f[df_f["dia"] == dia]

# ================= DASHBOARD =================
if pagina == "📊 Dashboard":

    total = len(df_f)
    categ = len(df_f[df_f["status"] == "Categorizado"])
    erros = len(df_f[df_f["status"] == "Erro"])
    taxa = (categ / total * 100) if total else 0

    classe = "pulse-green" if taxa >= 85 else "pulse-red"

    c1, c2, c3, c4 = st.columns(4)

    c1.markdown(f'<div class="card">📩<h2>{total}</h2>Total</div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="card">✅<h2>{categ}</h2>Categorizados</div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="card">❌<h2>{erros}</h2>Erros</div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="card {classe}">⚡<h2>{taxa:.1f}%</h2>Taxa</div>', unsafe_allow_html=True)

    st.divider()

    dist = df_f["analista"].value_counts().reset_index()
    dist.columns = ["Analista", "Qtd"]

    fig = px.bar(dist, x="Analista", y="Qtd", color="Analista", text="Qtd")

    fig.update_layout(
        template="plotly_dark",
        transition=dict(duration=1200, easing="cubic-in-out")
    )

    st.plotly_chart(fig, use_container_width=True)

# ================= ANALISE =================
elif pagina == "📈 Análises":

    st.title("🚀 Performance Geral")

    total = len(df_f)
    categ = len(df_f[df_f["status"] == "Categorizado"])
    taxa = (categ / total * 100) if total else 0

    # 🔥 VELOCÍMETRO
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=taxa,
        title={'text': "Taxa de Acerto"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "white"},
            'steps': [
                {'range': [0, 70], 'color': "red"},
                {'range': [70, 85], 'color': "yellow"},
                {'range': [85, 100], 'color': "green"}
            ]
        }
    ))

    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# ================= POR DIA =================
elif pagina == "📅 Por Dia":

    st.title("📅 Análise por Dia")

    dias = sorted(df["dia"].dropna().unique())
    dia_sel = st.selectbox("Escolha o dia", dias)

    df_dia = df[df["dia"] == dia_sel]

    # 📊 BARRA
    dist = df_dia["analista"].value_counts().reset_index()
    dist.columns = ["Analista", "Qtd"]

    fig1 = px.bar(dist, x="Analista", y="Qtd", color="Analista", text="Qtd")
    fig1.update_layout(template="plotly_dark", transition=dict(duration=1000))
    st.plotly_chart(fig1, use_container_width=True)

    # 🥧 ROSCA
    fig2 = px.pie(dist, names="Analista", values="Qtd", hole=0.6)
    fig2.update_layout(template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

    # 🚗 VELOCÍMETRO DO DIA
    categ = len(df_dia[df_dia["status"] == "Categorizado"])
    total = len(df_dia)
    taxa = (categ / total * 100) if total else 0

    fig3 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=taxa,
        title={'text': "Performance do Dia"},
        gauge={'axis': {'range': [0, 100]}}
    ))

    fig3.update_layout(template="plotly_dark")
    st.plotly_chart(fig3, use_container_width=True)

# ================= DADOS =================
elif pagina == "📄 Dados":

    st.title("📄 Base de Dados Inteligente")

    analista = st.selectbox(
        "Filtrar",
        ["Todos"] + sorted(df["analista"].dropna().unique())
    )

    df_final = df if analista == "Todos" else df[df["analista"] == analista]

    st.dataframe(df_final, use_container_width=True)

    # 📊 MINI GRÁFICO
    mini = df_final["analista"].value_counts().reset_index()
    mini.columns = ["Analista", "Qtd"]

    fig = px.bar(mini, x="Analista", y="Qtd", color="Analista")
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
