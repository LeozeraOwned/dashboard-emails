import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(layout="wide")

# ================= CSS ULTRA =================
st.markdown("""
<style>

/* FUNDO */
body {
    background-color: #0e1117;
}

/* SIDEBAR ANIMADA */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0e1117, #111827);
    box-shadow: 0 0 20px #00ffe0;
    animation: glowMenu 2s infinite alternate;
}

@keyframes glowMenu {
    from { box-shadow: 0 0 5px #00ffe0; }
    to { box-shadow: 0 0 25px #00ffe0; }
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

/* BORDA ANIMADA */
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

/* TEXTO */
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

/* ANIMAÇÃO DO NÚMERO - APENAS UMA VEZ */
.animate-once {
    animation: popOnce 0.8s ease-out 1;
}

@keyframes popOnce {
    0% {
        opacity: 0;
        transform: translateY(12px) scale(0.96);
    }
    70% {
        opacity: 1;
        transform: translateY(0px) scale(1.03);
    }
    100% {
        opacity: 1;
        transform: translateY(0px) scale(1);
    }
}

/* ANIMAÇÃO BORDA */
@keyframes borderMove {
    0% {transform: rotate(0deg);}
    100% {transform: rotate(360deg);}
}

/* TAXA */
.pulse-green {
    color: #00ff9f;
}

.pulse-red {
    color: #ff4d4d;
}

/* PULSO SOMENTE QUANDO FILTRO MUDA */
.pulse-green.animate-once {
    animation: pulseGreen 1s 1;
}

.pulse-red.animate-once {
    animation: pulseRed 1s 1;
}

@keyframes pulseGreen {
    0% {opacity: 1;}
    50% {opacity: 0.3;}
    100% {opacity: 1;}
}

@keyframes pulseRed {
    0% {opacity: 1;}
    50% {opacity: 0.3;}
    100% {opacity: 1;}
}

/* BARRA */
.plotly .bars path {
    transition: all 0.8s ease-in-out !important;
}

</style>
""", unsafe_allow_html=True)

# ================= LOAD =================
df = pd.read_csv("log_emails.csv")

df["data"] = pd.to_datetime(df["data"], errors="coerce")
df["dia"] = df["data"].dt.date
df["mes"] = df["data"].dt.month

# ORDEM FIXA DOS ANALISTAS (IMPORTANTE PARA AS BARRAS NÃO "ANDAR" DE LADO)
all_analistas = sorted(df["analista"].dropna().astype(str).unique().tolist())
max_qtd_analista = int(df["analista"].value_counts().max()) if not df.empty else 1

# ================= SIDEBAR =================
st.sidebar.title("📊 MENU")

pagina = st.sidebar.radio(
    "Navegação",
    ["📊 Dashboard", "📈 Análises", "📅 Por Dia", "📄 Dados"]
)

# ================= FILTROS =================
meses = sorted(df["mes"].dropna().unique())
mes_sel = st.sidebar.selectbox("Mês", ["Todos"] + list(meses))

dias = sorted(df["dia"].dropna().unique())
dia_sel = st.sidebar.selectbox("Dia", ["Todos"] + list(dias))

df_f = df.copy()

if mes_sel != "Todos":
    df_f = df_f[df_f["mes"] == mes_sel]

if dia_sel != "Todos":
    df_f = df_f[df_f["dia"] == dia_sel]

# ================= CONTROLE DE ANIMAÇÃO =================
# anima apenas na primeira carga ou quando filtro mudar
filtro_key = f"{mes_sel}|{dia_sel}"

if "last_filter_key" not in st.session_state:
    st.session_state["last_filter_key"] = filtro_key
    st.session_state["animar_cards"] = True
elif st.session_state["last_filter_key"] != filtro_key:
    st.session_state["last_filter_key"] = filtro_key
    st.session_state["animar_cards"] = True
else:
    st.session_state["animar_cards"] = False

# ================= FUNÇÃO CARD =================
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

# ================= FUNÇÃO DIST ANALISTA =================
def get_dist_analista(dataframe):
    contagem = dataframe["analista"].astype(str).value_counts().reindex(all_analistas, fill_value=0)
    dist = pd.DataFrame({
        "Analista": all_analistas,
        "Qtd": contagem.values
    })
    return dist

# ================= FUNÇÃO PARA DESCOBRIR COLUNA "O QUE ESTÁ SENDO ANALISADO" =================
def detectar_coluna_analise(dataframe):
    mapa = {col.lower(): col for col in dataframe.columns}

    candidatos = [
        "analise", "análise",
        "assunto",
        "categoria",
        "objeto",
        "descricao", "descrição",
        "tipo",
        "email",
        "arquivo",
        "processo",
        "item"
    ]

    for c in candidatos:
        if c in mapa:
            return mapa[c]

    return None

# ================= DASHBOARD =================
if pagina == "📊 Dashboard":

    st.title("🚀 Painel Inteligente")

    total = len(df_f)
    categ = len(df_f[df_f["status"] == "Categorizado"])
    erros = len(df_f[df_f["status"] == "Erro"])
    taxa = (categ / total * 100) if total > 0 else 0

    classe_taxa = "pulse-green" if taxa >= 85 else "pulse-red"

    col1, col2, col3, col4 = st.columns(4)

    animar = st.session_state.get("animar_cards", False)

    col1.markdown(card("📩", total, "Total", animate=animar), unsafe_allow_html=True)
    col2.markdown(card("✅", categ, "Categorizados", animate=animar), unsafe_allow_html=True)
    col3.markdown(card("❌", erros, "Erros", animate=animar), unsafe_allow_html=True)
    col4.markdown(card("⚡", f"{taxa:.1f}%", "Taxa", classe_taxa, animate=animar), unsafe_allow_html=True)

    st.divider()

    # 📊 BARRA FIXA - NÃO ANDA PARA O LADO
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

# ================= ANALISE =================
elif pagina == "📈 Análises":

    st.title("📈 Performance Geral")

    total = len(df_f)
    categ = len(df_f[df_f["status"] == "Categorizado"])
    taxa = (categ / total * 100) if total > 0 else 0

    # COR DO CARD CIRCULAR
    if taxa >= 85:
        cor_taxa = "#00e5ff"
    elif taxa >= 50:
        cor_taxa = "#ffd54f"
    else:
        cor_taxa = "#ff4d4d"

    restante = max(0, 100 - taxa)

    # 🔥 NOVO "VELOCÍMETRO" ESTILO CARD CIRCULAR
    fig = go.Figure(
        data=[
            go.Pie(
                values=[taxa, restante],
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

    fig.update_layout(
        template="plotly_dark",
        height=360,
        margin=dict(t=30, b=20, l=20, r=20),
        showlegend=False,
        annotations=[
            dict(
                text=f"<b>{taxa:.1f}%</b><br><span style='font-size:14px;color:#B8C1CC'>Perc. Meta</span>",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=30, color=cor_taxa)
            ),
            dict(
                text="Taxa de Acerto",
                x=0.5,
                y=1.08,
                showarrow=False,
                font=dict(size=20, color="white")
            )
        ]
    )

    st.plotly_chart(fig, use_container_width=True)

    # 📊 TIMELINE COM DATA EM PORTUGUÊS
    timeline = df_f.groupby("dia").size().reset_index(name="Qtd")
    timeline["Data"] = pd.to_datetime(timeline["dia"]).dt.strftime("%d/%m/%Y")

    fig2 = px.line(
        timeline,
        x="Data",
        y="Qtd",
        markers=True,
        template="plotly_dark"
    )

    fig2.update_traces(
        line=dict(color="#6C7BFF", width=3),
        marker=dict(size=8, color="#6C7BFF")
    )

    fig2.update_layout(
        transition_duration=800,
        xaxis_title="Data",
        yaxis_title="Qtd"
    )

    st.plotly_chart(fig2, use_container_width=True)

    # 📋 TABELA COM O QUE ESTÁ SENDO ANALISADO
    st.subheader("📋 Detalhamento")

    col_analise = detectar_coluna_analise(df_f)

    tabela_analises = df_f.copy()
    tabela_analises["Data"] = tabela_analises["data"].dt.strftime("%d/%m/%Y %H:%M").fillna("")

    if col_analise:
        tabela_analises["O que está sendo analisado"] = tabela_analises[col_analise].astype(str)
    else:
        tabela_analises["O que está sendo analisado"] = (
            "Status: " + tabela_analises["status"].astype(str) +
            " | Analista: " + tabela_analises["analista"].astype(str)
        )

    colunas_exibir = ["Data", "O que está sendo analisado"]

    if "status" in tabela_analises.columns:
        colunas_exibir.append("status")
    if "analista" in tabela_analises.columns:
        colunas_exibir.append("analista")

    tabela_final = tabela_analises[colunas_exibir].rename(columns={
        "status": "Status",
        "analista": "Analista"
    })

    st.dataframe(tabela_final, use_container_width=True)

# ================= POR DIA =================
elif pagina == "📅 Por Dia":

    st.title("📅 Visão Detalhada")

    col1, col2, col3 = st.columns(3)

    total = len(df_f)
    categ = len(df_f[df_f["status"] == "Categorizado"])
    erros = len(df_f[df_f["status"] == "Erro"])

    col1.metric("Total", total)
    col2.metric("Categorizados", categ)
    col3.metric("Erros", erros)

    st.divider()

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

    # ESSA PARTE FIXA A POSIÇÃO DAS BARRAS PARA ELAS SUBIREM,
    # EM VEZ DE "ESCORREGAREM" PARA A ESQUERDA
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_xaxes(categoryorder="array", categoryarray=all_analistas)
    fig.update_yaxes(range=[0, max_qtd_analista + 5])

    fig.update_layout(
        transition_duration=800,
        xaxis_title="Analista",
        yaxis_title="Qtd"
    )

    st.plotly_chart(fig, use_container_width=True)

# ================= DADOS =================
elif pagina == "📄 Dados":

    st.title("📄 Logs")

    st.dataframe(df_f, use_container_width=True)

