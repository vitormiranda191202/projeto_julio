import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import plotly.express as px
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Função para carregar configurações
def load_config():
    return {
        "DATABASE_URL": "postgresql://neondb_owner:npg_yWMlIa8iB1mH@ep-plain-bonus-adrh7qhm-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
        "PAGE_TITLE": "Dashboard Fichas",
        "LAYOUT": "wide"
    }

# Função para conectar ao banco e executar consultas
def fetch_data():
    try:
        config = load_config()
        engine = create_engine(config["DATABASE_URL"])
        with engine.connect() as conn:
            # Quantidade total de fichas
            qtd_fichas = conn.execute(
                text("SELECT COUNT(*) FROM eguh_vest.fichas_producao")
            ).scalar()

            # Consulta principal
            query = """
            SELECT 
                f.id AS ficha_id,
                f.produto,
                f.corte,
                f.grade,
                f.data,
                i.cor,
                i.g1, i.g2, i.g3,
                (i.g1 + i.g2 + i.g3) AS total_item
            FROM eguh_vest.fichas_producao f
            LEFT JOIN eguh_vest.itens_ficha i ON f.id = i.ficha_id
            ORDER BY f.id;
            """
            df = pd.read_sql(query, conn)
        return qtd_fichas, df
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco ou executar consulta: {e}")
        st.error("Erro ao carregar os dados do banco. Tente novamente mais tarde.")
        return None, pd.DataFrame()

# Função para formatar data
def format_date(date):
    return date.strftime("%d/%m/%Y") if isinstance(date, datetime) else date

# Função para criar gráfico de barras por cor
def plot_by_color(df):
    if not df.empty:
        df_cor = df.groupby("cor")[["g1", "g2", "g3", "total_item"]].sum().reset_index()
        st.subheader("📊 Quantidade por Cor")
        st.dataframe(df_cor, use_container_width=True)
        
        fig_cor = px.bar(
            df_cor,
            x="cor",
            y="total_item",
            title="Total de Peças por Cor",
            text="total_item",
            color="cor",
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        fig_cor.update_layout(showlegend=False)
        st.plotly_chart(fig_cor, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para exibir por cor.")

# Função para criar gráficos de evolução por data
def plot_by_date(df):
    if not df.empty:
        df_data = df.groupby("data")[["total_item"]].sum().reset_index()
        df_data_fichas = df.groupby("data")["ficha_id"].nunique().reset_index().rename(columns={"ficha_id": "qtd_fichas"})

        col1, col2 = st.columns(2)

        with col1:
            fig_data = px.line(
                df_data,
                x="data",
                y="total_item",
                markers=True,
                title="Total de Peças por Data",
                color_discrete_sequence=["#1f77b4"]
            )
            st.plotly_chart(fig_data, use_container_width=True)

        with col2:
            fig_fichas = px.line(
                df_data_fichas,
                x="data",
                y="qtd_fichas",
                markers=True,
                title="Número de Fichas por Data",
                color_discrete_sequence=["#ff7f0e"]
            )
            st.plotly_chart(fig_fichas, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para exibir evolução por data.")

# Configuração inicial da página
def main():
    config = load_config()
    st.set_page_config(page_title=config["PAGE_TITLE"], layout=config["LAYOUT"])
    st.title("📊 Dashboard - Fichas de Produção")

    # Carregar dados diretamente sem cache (sempre atualizado)
    qtd_fichas, df = fetch_data()

    if df.empty and qtd_fichas is None:
        return

    # Visão 1 - Geral
    st.header("1️⃣ Visão Geral")
    st.metric("Total de Fichas", qtd_fichas)

    st.subheader("📋 Tabela Detalhada")
    st.dataframe(df, use_container_width=True)

    st.subheader("📦 Fichas com seus Itens")
    for ficha_id, grupo in df.groupby("ficha_id"):
        st.markdown(f"### Ficha {ficha_id} - {grupo['produto'].iloc[0]} (Corte {grupo['corte'].iloc[0]})")
        st.write(f"📅 Data: {format_date(grupo['data'].iloc[0])} | 👕 Grade: {grupo['grade'].iloc[0]}")
        st.dataframe(grupo[["cor", "g1", "g2", "g3", "total_item"]], use_container_width=True)

    # Visão 2 - Quantidade por Cor
    st.header("2️⃣ Visão por Cor")
    plot_by_color(df)

    # Visão 3 - Evolução no Tempo
    st.header("3️⃣ Evolução por Data")
    plot_by_date(df)

if __name__ == "__main__":
    main()