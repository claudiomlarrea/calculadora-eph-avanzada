import streamlit as st
import pandas as pd
import io
import fitz
import re
from docx import Document

st.set_page_config(page_title="Calculadora EPH – Informe Ampliado", layout="wide")
st.title("📊 Calculadora EPH – Informe Word con Análisis Cuantitativo Ampliado")

anio = st.selectbox("📅 Seleccioná el año de la base", ["2017", "2018", "2019", "2020", "2021", "2022", "2023"])
hogares_file = st.file_uploader("🏠 Base de Hogares anual (.xlsx)", type="xlsx")
individuos_file = st.file_uploader("👤 Base de Individuos anual (.xlsx)", type="xlsx")
instructivo_pdf = st.file_uploader("📄 Instructivo PDF", type="pdf")

def limpiar_descripcion_variable(desc):
    return desc.replace(".....", "").replace("....", "").replace("...", "").strip().capitalize()

def extraer_diccionario_desde_pdf(pdf_file):
    text = ""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    for page in doc:
        text += page.get_text()
    doc.close()
    regex = re.compile(r"^(\w{2,})\s+[NC]\(\d+\)\s+(.+)$", re.MULTILINE)
    matches = regex.findall(text)
    return {codigo.strip(): limpiar_descripcion_variable(desc) for codigo, desc in matches}

def generar_informe_word(anio, resumen_hogar, resumen_ind):
    doc = Document()
    doc.add_heading(f"Informe Interpretativo EPH – Anual {anio}", level=1)

    doc.add_heading("🏠 Base de Hogares – Interpretación", level=2)
    doc.add_paragraph(
        f"El análisis de la base de hogares del año {anio} permite observar las características generales de las viviendas y su entorno. "
        "Se examinan variables clave como el tipo de vivienda, el acceso al agua potable, el sistema de eliminación de excretas, y la ubicación geográfica por región. "
        "Una alta proporción de viviendas son casas individuales, lo que sugiere una estructura residencial tradicional. "
        "El acceso al agua dentro de la vivienda, si es elevado, refleja buenas condiciones sanitarias, aunque aún pueden existir disparidades regionales. "
        "El análisis de los indicadores de ingresos, como el ITF (Ingreso Total Familiar) y el IPCF (Ingreso Per Cápita Familiar), permite dimensionar la capacidad económica de los hogares y detectar situaciones de vulnerabilidad económica."
    )

    doc.add_heading("👤 Base de Individuos – Interpretación", level=2)
    doc.add_paragraph(
        "El análisis de los individuos residentes en estos hogares ofrece una perspectiva sobre la composición sociodemográfica y el acceso a derechos básicos. "
        "Las variables de sexo y edad permiten caracterizar la pirámide poblacional, mientras que el nivel educativo alcanzado brinda información sobre las capacidades formativas de la población. "
        "El indicador de condición de actividad revela la proporción de personas ocupadas, desocupadas o inactivas, información clave para evaluar la situación del mercado laboral. "
        "Una alta proporción de inactivos puede indicar una estructura etaria envejecida, alta proporción de estudiantes o dificultades en el acceso al empleo formal. "
        "El análisis de los ingresos individuales, junto con los indicadores familiares, permite evaluar desigualdades económicas dentro y entre regiones."
    )

    doc.add_heading("📌 Conclusión General", level=2)
    doc.add_paragraph(
        f"El informe anual consolidado de hogares e individuos de la Encuesta Permanente de Hogares para el año {anio} proporciona evidencia cuantitativa útil "
        "para la formulación de políticas públicas, el monitoreo de la inclusión social y la evaluación de condiciones de vida. "
        "Los resultados muestran cómo se distribuyen los recursos, el acceso a servicios esenciales, el perfil educativo y la inserción laboral de la población urbana argentina. "
        "Este tipo de análisis es fundamental para identificar desigualdades estructurales, orientar intervenciones estatales y promover el desarrollo con equidad."
    )

    doc.add_page_break()
    doc.add_heading("📊 Análisis Cuantitativo Adicional – Valores y Porcentajes", level=1)

    doc.add_heading("🏠 Hogares – Resumen Numérico", level=2)
    doc.add_paragraph("Resumen de variables de hogares")
    for var in resumen_hogar.index:
        media = resumen_hogar.loc[var, 'mean']
        count = int(resumen_hogar.loc[var, 'count'])
        doc.add_paragraph(f"{var}: promedio = {media:.2f} (basado en {count} registros).", style="List Bullet")

    doc.add_heading("👤 Individuos – Resumen Numérico", level=2)
    doc.add_paragraph("Resumen de variables individuales")
    for var in resumen_ind.index:
        media = resumen_ind.loc[var, 'mean']
        count = int(resumen_ind.loc[var, 'count'])
        doc.add_paragraph(f"{var}: promedio = {media:.2f} (basado en {count} registros).", style="List Bullet")

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

    resumen_hogar = df_hogar.describe(include="all").transpose()
    resumen_ind = df_ind.describe(include="all").transpose()

    output_word = generar_informe_word(anio, resumen_hogar, resumen_ind)

    st.success("✅ Informe generado.")
    st.download_button("📥 Descargar Informe Word Ampliado", data=output_word, file_name=f"informe_eph_{anio}_ampliado.docx")
else:
    st.info("📥 Subí las bases de hogares, individuos y el instructivo PDF para generar el informe.")
