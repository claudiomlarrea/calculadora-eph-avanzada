
import streamlit as st
import pandas as pd
import io
import fitz
import re
from analyzer import (
    resumen_descriptivo,
    generar_informe_word
)

st.set_page_config(page_title="Calculadora EPH – Avanzada", layout="wide")
st.title("📊 Calculadora EPH – Informe Profesional Automático")

anio = st.selectbox("📅 Seleccioná el año de la base", [str(a) for a in range(2017, 2025)])
hogares_file = st.file_uploader("🏠 Base de Hogares anual (.xlsx)", type="xlsx")
individuos_file = st.file_uploader("👤 Base de Individuos anual (.xlsx)", type="xlsx")
instructivo_pdf = st.file_uploader("📄 Instructivo PDF", type="pdf")

def extraer_diccionario_desde_pdf(pdf_file):
    text = ""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    for page in doc:
        text += page.get_text()
    doc.close()
    matches = re.findall(r"^(\w{2,})\s+[NC]\(\d+)\s+(.+)$", text, re.MULTILINE)
    return {codigo.strip(): desc.strip().capitalize() for codigo, desc in matches}

if hogares_file and individuos_file and instructivo_pdf:
    st.info("📊 Procesando datos y generando informe...")
    mapa = extraer_diccionario_desde_pdf(instructivo_pdf)
    df_hogar = pd.read_excel(hogares_file)
    df_ind = pd.read_excel(individuos_file)

    df_hogar = df_hogar.rename(columns=mapa)
    df_ind = df_ind.rename(columns=mapa)

    df_hogar = df_hogar.drop_duplicates()
    df_ind = df_ind.drop_duplicates()

    resumen_hogar, resumen_ind = resumen_descriptivo(df_hogar, df_ind)
    informe_word = generar_informe_word(anio, resumen_hogar, resumen_ind)

    st.success("✅ Informe generado correctamente.")
    st.download_button(
        label="📥 Descargar Informe Profesional (Word)",
        data=informe_word,
        file_name=f"informe_eph_{anio}_profesional.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
else:
    st.info("📥 Subí la base de hogares, individuos y el instructivo PDF para comenzar.")
