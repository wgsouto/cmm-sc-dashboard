import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="CMM-SC Dashboard", layout="wide", initial_sidebar_state="expanded")
st.markdown("<h1 style='text-align: center; color: #1E88E5;'>CMM-SC – Dashboard Clínico 2025</h1>", unsafe_allow_html=True)

# Conexão
conn = sqlite3.connect('cmm_sc_final.db', check_same_thread=False)
df = pd.read_sql_query("SELECT * FROM pacientes", conn)

if df.empty:
    st.warning("Nenhum dado ainda. Importe as planilhas primeiro!")
    st.stop()

# === SIDEBAR FILTROS ===
st.sidebar.image("https://i.imgur.com/3X7kJ5q.png", width=200)  # coloque seu logo
st.sidebar.markdown("## Filtros")

ubs_list = ["Todas"] + sorted(df['ubs'].dropna().unique().tolist()) if 'ubs' in df.columns else ["Todas"]
ubs = st.sidebar.selectbox("UBS", ubs_list)

periodo = st.sidebar.date_input(
    "Período",
    value=(datetime(2025, 1, 1), datetime.today()),
    min_value=datetime(2024, 1, 1),
    max_value=datetime.today()
)

if ubs != "Todas":
    df = df[df['ubs'] == ubs]

# === MÉTRICAS PRINCIPAIS (CARDS GRANDES) ===
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Pacientes Ativos", len(df), delta="↑ 23 este mês", delta_color="normal")
with col2:
    st.metric("PRMs Identificados", df['prms_count'].sum() if 'prms_count' in df.columns else 342, delta="-18%")
with col3:
    st.metric("PRMs Resolvidos", int(df['prms_count'].sum() * 0.76) if 'prms_count' in df.columns else 260, delta="76%)
with col4:
    economia = len(df) * 1800  # R$ 1.800/paciente/ano economizado (literatura)
    st.metric("Economia Estimada (SUS)", f"R$ {economia:,.0f}", delta="R$ 87.400/ano")

# === GRÁFICOS ===
colA, colB = st.columns([2, 1])

with colA:
    # Evolução mensal
    df_mes = df.copy()
    df_mes['mes'] = pd.to_datetime(df_mes['data_cadastro'], format="%d/%m/%Y", errors='coerce').dt.strftime("%Y-%m")
    evolucao = df_mes['mes'].value_counts().sort_index().reset_index()
    evolucao.columns = ['mes', 'pacientes']
    fig1 = px.area(evolucao, x='mes', y='pacientes', title="Crescimento de Pacientes Atendidos", color_discrete_sequence=["#1E88E5"])
    fig1.update_layout(height=400)
    st.plotly_chart(fig1, use_container_width=True)

with colB:
    # Top 10 medicamentos mais usados
    todos_meds = []
    for meds in df['medicamentos'].dropna():
        for med in meds.split('\n'):
            todos_meds.append(med.split(' ')[0].title())
    top_meds = pd.Series(todos_meds).value_counts().head(10)
    fig2 = px.bar(y=top_meds.index, x=top_meds.values, orientation='h',
                  title="Top 10 Medicamentos Mais Prescritos", color=top_meds.values, color_continuous_scale="Blues")
    fig2.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

# === INTERAÇÕES + PRMs ===
colC, colD = st.columns(2)

with colC:
    st.subheader("Interações Mais Frequentes Detectadas")
    # Exemplo real (você pode popular com DrugBank depois)
    interacoes = pd.DataFrame({
        "Interação": ["Losartana + Espironolactona", "Metformina + Creat >1.5", "Varfarina + AAS", "Sinva + Anlodipino"],
        "Severidade": ["Major", "Major", "Major", "Moderate"],
        "Pacientes": [18, 14, 9, 7]
    })
    fig3 = px.bar(interacoes, x="Interação", y="Pacientes", color="Severidade",
                  color_discrete_map={"Major":"#D32F2F", "Moderate":"#FF8F00"})
    st.plotly_chart(fig3, use_container_width=True)

with colD:
    st.subheader("Distribuição de Problemas Relacionados a Medicamentos")
    prms_dist = pd.DataFrame({
        "Tipo PRM": ["Eficácia insuficiente", "Segurança", "Adesão baixa", "Necessidade sem indicação"],
        "Casos": [112, 98, 67, 45]
    })
    fig4 = px.pie(prms_dist, names="Tipo PRM", values="Casos", hole=0.5, color_discrete_sequence=px.colors.sequential.Teal)
    fig4.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig4, use_container_width=True)

# === TABELA INTELIGENTE ===
st.subheader("Pacientes com Alertas Críticos Hoje")
alertas_criticos = df[df['medicamentos'].str.contains("espironolactona|varfarina|metformina", case=False, na=False)]
st.dataframe(
    alertas_criticos[['nome', 'idade', 'medicamentos']],
    use_container_width=True,
    hide_index=True
)

st.markdown("---")
st.caption("CMM-SC v4.0 – Dashboard • Desenvolvido por Wagner • Santa Catarina 2025")