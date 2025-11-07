import streamlit as st
import pandas as pd
import sqlite3
from datetime import date

DB_PATH = "fittrack.db"

# -------------------------------
# Banco e dados
# -------------------------------
def conectar():
    return sqlite3.connect(DB_PATH)

def carregar_dados():
    con = conectar()
    try:
        df = pd.read_sql_query("SELECT * FROM progresso ORDER BY data", con)
    except Exception:
        df = pd.DataFrame(columns=["data", "peso", "meta", "dieta", "frequencia"])
    finally:
        con.close()
    return df

# -------------------------------
# Interface principal
# -------------------------------
st.set_page_config(page_title="FitTrack AI Dashboard", page_icon="🏋️", layout="wide")

st.markdown("""
    <style>
    body {background-color: #0e1117; color: white;}
    .block-container {padding-top: 2rem; padding-bottom: 0rem;}
    h1 {color: #FFD700; text-align: center;}
    .metric-card {
        background-color: #1e2229;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.15);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>🏋️ FitTrack AI — Painel de Progresso</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#aaa;'>Seu acompanhamento inteligente de evolução física 💪</p>", unsafe_allow_html=True)
st.markdown("---")

df = carregar_dados()

if df.empty:
    st.warning("⚠️ Nenhum progresso registrado ainda. Use o app FitTrack para registrar seus dados.")
else:
    df["data"] = pd.to_datetime(df["data"])
    peso_inicial = df["peso"].iloc[0]
    peso_atual = df["peso"].iloc[-1]
    meta = df["meta"].iloc[-1]
    progresso = (peso_atual - peso_inicial) / (meta - peso_inicial)
    progresso = max(0, min(progresso, 1))
    diferenca = peso_atual - peso_inicial

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("<div class='metric-card'><h3>🏋️ Peso Atual</h3><h2>{:.1f} kg</h2></div>".format(peso_atual), unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='metric-card'><h3>🎯 Meta</h3><h2>{:.1f} kg</h2></div>".format(meta), unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='metric-card'><h3>📈 Progresso</h3><h2>{:.1f}%</h2></div>".format(progresso*100), unsafe_allow_html=True)
    with col4:
        cor = "#32CD32" if diferenca < 0 else "#FFD700"
        st.markdown(f"<div class='metric-card'><h3>⚖️ Diferença</h3><h2 style='color:{cor};'>{diferenca:+.1f} kg</h2></div>", unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### 📋 Histórico de Registros")
    st.dataframe(
        df[["data", "peso", "meta", "dieta", "frequencia"]],
        use_container_width=True,
        height=280
    )

    ultima_dieta = df["dieta"].iloc[-1].capitalize()
    ultima_freq = int(df["frequencia"].iloc[-1])
    st.markdown("---")
    st.markdown(f"""
        <div style='text-align:center;'>
            <h3>🍽️ Dieta Atual: <span style='color:#FFD700;'>{ultima_dieta}</span></h3>
            <h3>📅 Frequência de Treinos: <span style='color:#32CD32;'>{ultima_freq}x/semana</span></h3>
        </div>
    """, unsafe_allow_html=True)

st.markdown("""
    <hr>
    <p style='text-align: center; color: gray; font-size: 13px;'>
        Desenvolvido por <b>Lucas Barboza</b> — Projeto <b>FitTrack AI</b> 💪<br>
        <span style='font-size: 11px;'>Python • SQLite • Streamlit</span>
    </p>
""", unsafe_allow_html=True)
