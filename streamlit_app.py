
import streamlit as st
import pandas as pd
import io
import fitz
import re
from docx import Document

st.set_page_config(page_title="Calculadora EPH – Informe Automático", layout="wide")
st.title("📊 Calculadora EPH – Informe Excel + Word")

anio = st.selectbox("📅 Seleccioná el año de la base", ["2017", "2018", "2019", "2020", "2021", "2022", "2023"])
hogares_file = st.file_uploader("🏠 Base de Hogares anual (.xlsx)", type="xlsx")
individuos_file = st.file_uploader("👤 Base de Individuos anual (.xlsx)", type="xlsx")
instructivo_pdf = st.file_uploader("📄 Instructivo PDF", type="pdf")

def limpiar_descripcion_variable(desc):
    desc = desc.replace(".....", "").replace("....", "").replace("...", "").strip()
    return desc.strip().capitalize()

def extraer_diccionario_desde_pdf(pdf_file):
    text = ""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    for page in doc:
        text += page.get_text()
    doc.close()
    regex = re.compile(r"^(\w{2,})\s+[NC]\(\d+\)\s+(.+)$", re.MULTILINE)
    matches = regex.findall(text)
    return {codigo.strip(): limpiar_descripcion_variable(desc) for codigo, desc in matches}

def generar_informe_word(anio):
    doc = Document()
    doc.add_heading(f"Informe Interpretativo EPH – Anual {anio}", level=1)
    doc.add_heading("🏠 Base de Hogares – Interpretación", level=2)
    doc.add_paragraph("El análisis de la base de hogares permite observar las condiciones de vida, acceso a servicios y tipo de vivienda.")
    doc.add_heading("👤 Base de Individuos – Interpretación", level=2)
    doc.add_paragraph("Este análisis revela características demográficas, educativas y laborales de la población residente en hogares urbanos.")
    doc.add_heading("📌 Conclusión General", level=2)
    doc.add_paragraph("Los resultados permiten comprender la estructura social y económica de los hogares urbanos argentinos.")
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

if hogares_file and individuos_file and instructivo_pdf:
    mapa = extraer_diccionario_desde_pdf(instructivo_pdf)
    df_hogar = pd.read_excel(hogares_file)
    df_ind = pd.read_excel(individuos_file)

    if mapa:
        df_hogar = df_hogar.rename(columns=mapa)
        df_ind = df_ind.rename(columns=mapa)

    posibles_hogar = ["ingreso", "región", "agua", "baño", "vivienda", "ipcf", "itf"]
    posibles_ind = ["sexo", "edad", "educ", "actividad", "ingreso", "estado", "ch04", "nivel_ed"]

    cols_hogar = [c for c in df_hogar.columns if any(x in c.lower() for x in posibles_hogar)]
    cols_ind = [c for c in df_ind.columns if any(x in c.lower() for x in posibles_ind)]

    resumen_hogar = df_hogar[cols_hogar].describe(include="all").transpose()
    resumen_ind = df_ind[cols_ind].describe(include="all").transpose()

    output_excel = io.BytesIO()
    with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
        resumen_hogar.to_excel(writer, sheet_name="Resumen Hogares")
        resumen_ind.to_excel(writer, sheet_name="Resumen Individuos")
    output_excel.seek(0)

    output_word = generar_informe_word(anio)

    st.success("✅ Análisis generado.")
    st.download_button("📥 Descargar Excel", data=output_excel, file_name=f"informe_eph_{anio}.xlsx")
    st.download_button("📥 Descargar Informe Interpretativo (Word)", data=output_word, file_name=f"informe_eph_{anio}.docx")
else:
    st.info("📥 Subí las bases de hogares, individuos y el instructivo PDF para comenzar.")
