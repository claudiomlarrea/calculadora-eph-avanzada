
import streamlit as st
import pandas as pd
import numpy as np
import io
import fitz
import re

st.set_page_config(page_title="EPH – Exclusión Digital Unificada", layout="wide")
st.title("📊 Calculadora de Exclusión Digital y Movilidad Social (Base Completa)")

anio = st.selectbox("📅 Seleccioná el año de la base", [str(a) for a in range(2017, 2025)])
hogares_file = st.file_uploader("🏠 Base de Hogares anual (.xlsx)", type="xlsx")
individuos_file = st.file_uploader("👤 Base de Individuos anual (.xlsx)", type="xlsx")
instructivo_pdf = st.file_uploader("📄 Instructivo PDF del INDEC (.pdf)", type="pdf")

def extraer_diccionario_desde_pdf(pdf_file):
    text = ""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    for page in doc:
        text += page.get_text()
    doc.close()
    matches = re.findall(r"^(\w{2,})\s+[NC]\(\d+\)\s+(.+)$", text, re.MULTILINE)
    return {codigo.strip(): desc.strip().capitalize() for codigo, desc in matches}

if hogares_file and individuos_file and instructivo_pdf:
    mapa = extraer_diccionario_desde_pdf(instructivo_pdf)
    df_hogar = pd.read_excel(hogares_file)
    df_ind = pd.read_excel(individuos_file)
    df_ind = df_ind.rename(columns=mapa)

    df_ind.columns = df_ind.columns.str.lower()

    df_ind['acceso_computadora'] = df_ind.get('ip_iii_04', pd.Series()).map({1: 'Sí', 2: 'No'})
    df_ind['acceso_internet'] = df_ind.get('ip_iii_05', pd.Series()).map({1: 'Sí', 2: 'No'})
    df_ind['capacitacion_tic'] = df_ind.get('ip_iii_06', pd.Series()).map({1: 'Sí', 2: 'No'})

    nivel_ed_col = next((col for col in df_ind.columns if 'nivel_ed' in col), None)
    if nivel_ed_col:
        mapeo = {
            1: 'Sin instrucción', 2: 'Primario incompleto', 3: 'Primario completo',
            4: 'Secundario incompleto', 5: 'Secundario completo',
            6: 'Superior universitario incompleto', 7: 'Superior universitario completo'
        }
        df_ind['nivel_educativo'] = df_ind[nivel_ed_col].map(mapeo)

    def calcular_indices(row):
        total = sum([
            row.get('acceso_computadora') == 'Sí',
            row.get('acceso_internet') == 'Sí',
            row.get('capacitacion_tic') == 'Sí'
        ])
        ind_bin = 1 if total == 0 else 0
        ind_ord = ((total) / 3 * 90) + 10
        vuln_dig = ((3 - total) / 3 * 90) + 10
        puntaje_ed = {
            'Sin instrucción': 7, 'Primario incompleto': 6, 'Primario completo': 5,
            'Secundario incompleto': 4, 'Secundario completo': 3,
            'Superior universitario incompleto': 2, 'Superior universitario completo': 1
        }.get(row.get('nivel_educativo'), np.nan)
        if pd.isna(puntaje_ed):
            return pd.Series([ind_bin, ind_ord, vuln_dig, np.nan])
        vuln_ed = (puntaje_ed / 7) * 50
        vuln_tic = 50 if row.get('capacitacion_tic') == 'No' else 0
        vuln_mov = min(vuln_ed + vuln_tic, 100)
        return pd.Series([ind_bin, ind_ord, vuln_dig, vuln_mov])

    df_ind[['indice_binario', 'indice_ordinal', 'vulnerabilidad_digital', 'vulnerabilidad_movilidad']] = df_ind.apply(calcular_indices, axis=1)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_ind.to_excel(writer, index=False)
    output.seek(0)

    st.success("✅ Cálculo completado.")
    st.download_button(
        label='📥 Descargar resultados en Excel',
        data=output,
        file_name=f'resultados_exclusion_{anio}.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
else:
    st.info("📥 Subí las tres bases (hogares, individuos, instructivo PDF) para comenzar.")
