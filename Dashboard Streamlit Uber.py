import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import BytesIO
from datetime import datetime

# 🎯 Configurações da página
st.set_page_config(page_title="Painel Uber - BYD Dolphin", layout="wide", initial_sidebar_state="collapsed")

st.info("✅ Versão com dados carregados do Google Drive.")

# 🏷️ Cabeçalho
st.title("📊 Painel de Desempenho - Uber com BYD Dolphin")

# 🔁 Carregar dados diretamente do Google Drive
@st.cache_data(show_spinner="Carregando dados...")
def carregar_dados():
    file_id = "1Ek9-wZPLWuf3uZBAm8Sr_lEIbZCSD0Ia"
    url = f"https://drive.google.com/uc?id={file_id}"
    response = requests.get(url)
    response.raise_for_status()
    file_stream = BytesIO(response.content)

    df = pd.read_excel(file_stream)
    df["Data"] = pd.to_datetime(df["Data"])
    df["Mês"] = df["Data"].dt.to_period("M").astype(str)
    df["Semana"] = df["Data"].dt.strftime("%U")
    return df

# 📦 Dataset completo
df = carregar_dados()
st.write("📝 Colunas disponíveis no DataFrame:", df.columns.tolist())

# 📆 Seleciona dados do mês atual até o dia de hoje
hoje = pd.to_datetime(datetime.today().date())
mes_atual = hoje.to_period("M").strftime("%Y-%m")
df_mes_atual = df[df["Mês"] == mes_atual]

# 📈 Métricas principais (KPIs)
total_ganho = df_mes_atual["Valor Uber (R$)"].sum()
lucro_liquido = df_mes_atual["Lucro Líquido (R$)"].sum()
numero_viagens = df_mes_atual["Qtd. Viagens"].sum()
km_total = df_mes_atual["Trip B (km)"].sum()
media_ganho_km = df_mes_atual["Ganhos por Km (R$/km)"].mean()

st.subheader(f"📅 Desempenho - {mes_atual}")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💵 Ganhos Totais", f"R$ {total_ganho:.2f}")
col2.metric("🧮 Lucro Líquido", f"R$ {lucro_liquido:.2f}")
col3.metric("🚗 Nº de Viagens", int(numero_viagens))
col4.metric("🛣️ Km Rodados (Trip B)", f"{km_total:.1f} km")
col5.metric("📏 Ganhos por Km", f"R$ {media_ganho_km:.2f}")

# 📊 Gráfico de ganhos diários
fig_ganhos = px.line(
    df_mes_atual,
    x="Data",
    y="Valor Uber (R$)",
    title="📈 Evolução Diária de Ganhos",
    markers=True,
    labels={"Data": "Dia", "Valor Uber (R$)": "Ganhos (R$)"}
)
fig_ganhos.update_layout(xaxis_title="Data", yaxis_title="R$ Ganhos")
st.plotly_chart(fig_ganhos, use_container_width=True)

# ⚡ Gráfico de eficiência energética
if "Eficiência (km/kWh)\n=100/consumo médio" in df_mes_atual.columns:
    fig_eficiencia = px.bar(
        df_mes_atual.dropna(subset=["Eficiência (km/kWh)\n=100/consumo médio"]),
        x="Data",
        y="Eficiência (km/kWh)\n=100/consumo médio",
        title="🔋 Eficiência Energética Diária",
        color="Eficiência (km/kWh)\n=100/consumo médio",
        color_continuous_scale="Viridis",
        labels={"Eficiência (km/kWh)\n=100/consumo médio": "km por kWh", "Data": "Dia"}
    )
    fig_eficiencia.update_layout(xaxis_title="Data", yaxis_title="Eficiência (km/kWh)")
    st.plotly_chart(fig_eficiencia, use_container_width=True)
else:
    st.warning("A coluna 'Eficiência (km/kWh)' não está disponível nos dados.")

# ⚡ Consumo médio de eletricidade (kWh/100km)
if "Consumo Médio Instantâneo\nde Eletricidade (kWh/100km)" in df_mes_atual.columns:
    fig_consumo = px.line(
        df_mes_atual,
        x="Data",
        y="Consumo Médio Instantâneo\nde Eletricidade (kWh/100km)",
        title="⚡ Consumo Médio de Eletricidade",
        markers=True,
        labels={"Consumo Médio Instantâneo\nde Eletricidade (kWh/100km)": "kWh/100km", "Data": "Dia"}
    )
    fig_consumo.update_layout(xaxis_title="Data", yaxis_title="kWh/100km")
    st.plotly_chart(fig_consumo, use_container_width=True)

# ⏱️ Ganhos por hora dirigida
if "Ganhos por Hora (R$/h)" in df_mes_atual.columns:
    fig_ganho_hora = px.bar(
        df_mes_atual,
        x="Data",
        y="Ganhos por Hora (R$/h)",
        title="⏱️ Ganhos por Hora Dirigida",
        color="Ganhos por Hora (R$/h)",
        color_continuous_scale="Plasma",
        labels={"Ganhos por Hora (R$/h)": "R$/h", "Data": "Dia"}
    )
    fig_ganho_hora.update_layout(xaxis_title="Data", yaxis_title="R$/h")
    st.plotly_chart(fig_ganho_hora, use_container_width=True)

# 🔌 Tempo estimado para carga total
if "Tempo Restante\np/ Carga Total (h)" in df_mes_atual.columns and "Hora\n(Início da Recarga)" in df_mes_atual.columns:
    fig_carga = px.scatter(
        df_mes_atual,
        x="Hora\n(Início da Recarga)",
        y="Tempo Restante\np/ Carga Total (h)",
        title="🔌 Tempo Estimado para Carga Total",
        labels={"Hora\n(Início da Recarga)": "Início da Carga", "Tempo Restante\np/ Carga Total (h)": "Horas Restantes"},
        color="Tempo Restante\np/ Carga Total (h)",
        color_continuous_scale="Turbo"
    )
    st.plotly_chart(fig_carga, use_container_width=True)

# 📄 Visualização tabular
with st.expander("🔍 Ver dados detalhados do mês"):
    st.dataframe(df_mes_atual)

# 📥 Botão de download
csv = df_mes_atual.to_csv(index=False).encode('utf-8')
st.download_button(
    label="⬇️ Baixar dados do mês (CSV)",
    data=csv,
    file_name=f"uber_byddolphin_{mes_atual}.csv",
    mime="text/csv"
)

# Rodapé
st.markdown("---")
st.caption("Criado com ❤️ por Jefferson e assistido por Jarvis ✨")
