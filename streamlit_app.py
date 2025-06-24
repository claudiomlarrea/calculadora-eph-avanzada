import streamlit as st
import pandas as pd
import numpy as np
import io

# -----------------------------------------------
# TÍTULOS INSTITUCIONALES
st.markdown("<h1 style='text-align: center; color: white;'>Universidad Católica de Cuyo</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: white;'>Facultad de Ciencias Económicas y Empresariales</h3>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: white;'>Instituto de Desarrollo Sostenible</h4>", unsafe_allow_html=True)

st.title("Calculadora de Exclusión Digital y Movilidad Social")
st.subheader("Herramienta para el análisis de la brecha digital y oportunidades de desarrollo social.")

st.markdown("""
Esta aplicación permite estimar indicadores de exclusión digital y movilidad social a partir de datos individuales o archivos Excel.
""", unsafe_allow_html=True)

st.markdown("""
**Definición de indicadores calculados:**
- **Índice Binario de Exclusión Digital:** 1 si la persona está completamente excluida digitalmente; 0 en caso contrario.
- **Índice Ordinal de Exclusión Digital (%):** Expresa el nivel de acceso digital en porcentaje (10%-100%).
- **Porcentaje de Vulnerabilidad Digital (%):** Cuantifica la exclusión digital en escala de 10%-100%.
- **Porcentaje de Vulnerabilidad de Movilidad Social (%):** Calcula el riesgo de movilidad social reducida (0%-100%).
""", unsafe_allow_html=True)

# -----------------------------------------------
# MODO DE USO
modo = st.radio('Seleccioná el modo de uso:', ['Ingreso individual', 'Carga por lote (Excel)'])

# -----------------------------------------------
# INGRESO INDIVIDUAL
if modo == 'Ingreso individual':
    st.header('Ingreso de Datos')

    sexo = st.selectbox('Sexo:', ['Varón', 'Mujer'])
    edad = st.number_input('Edad:', min_value=0, max_value=120, value=30)
    nivel_educativo = st.selectbox('Nivel Educativo:', [
        'Sin instrucción', 'Primario incompleto', 'Primario completo',
        'Secundario incompleto', 'Secundario completo',
        'Superior universitario incompleto', 'Superior universitario completo'
    ])
    acceso_computadora = st.selectbox('¿Tiene acceso a computadora?', ['Sí', 'No'])
    acceso_internet = st.selectbox('¿Tiene acceso a internet?', ['Sí', 'No'])
    capacitacion_tic = st.selectbox('¿Tiene capacitación en TIC?', ['Sí', 'No'])
    region = st.selectbox('Región:', ['Gran Buenos Aires', 'Pampeana', 'Noroeste', 'Noreste', 'Cuyo', 'Patagonia'])
    provincia = st.text_input('Provincia (opcional):', '')

    # Cálculo de índices individuales
    sub_total = sum([
        acceso_computadora == 'Sí',
        acceso_internet == 'Sí',
        capacitacion_tic == 'Sí'
    ])
    indice_binario = 1 if sub_total == 0 else 0
    indice_ordinal = ((sub_total) / 3 * 90) + 10
    vulnerabilidad_digital = ((3 - sub_total) / 3 * 90) + 10

    puntajes = {
        'Sin instrucción': 7, 'Primario incompleto': 6, 'Primario completo': 5,
        'Secundario incompleto': 4, 'Secundario completo': 3,
        'Superior universitario incompleto': 2, 'Superior universitario completo': 1
    }
    vulnerabilidad_educativa = (puntajes[nivel_educativo] / 7) * 50
    vulnerabilidad_tic = 50 if capacitacion_tic == 'No' else 0
    vulnerabilidad_movilidad = min(vulnerabilidad_educativa + vulnerabilidad_tic, 100)

    # Mostrar resultados
    st.header('Resultados')
    st.write(f"**Índice Binario de Exclusión Digital:** {indice_binario}")
    st.write(f"**Índice Ordinal de Exclusión Digital:** {indice_ordinal:.1f}%")
    st.write(f"**Porcentaje de Vulnerabilidad Digital:** {vulnerabilidad_digital:.1f}%")
    st.write(f"**Porcentaje de Vulnerabilidad de Movilidad Social:** {vulnerabilidad_movilidad:.1f}%")

    resultados = pd.DataFrame({
        'sexo': [sexo], 'edad': [edad], 'nivel_educativo': [nivel_educativo],
        'acceso_computadora': [acceso_computadora], 'acceso_internet': [acceso_internet],
        'capacitacion_tic': [capacitacion_tic], 'region': [region], 'provincia': [provincia],
        'indice_binario': [indice_binario], 'indice_ordinal': [indice_ordinal],
        'vulnerabilidad_digital': [vulnerabilidad_digital],
        'vulnerabilidad_movilidad': [vulnerabilidad_movilidad]
    })

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        resultados.to_excel(writer, index=False)
    output.seek(0)

    st.download_button(
        label="Descargar resultados individuales en Excel",
        data=output,
        file_name='resultados_individual.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# -----------------------------------------------
# CARGA POR LOTE
elif modo == 'Carga por lote (Excel)':
    st.header('Carga de Datos por Lote')
    archivo = st.file_uploader('Subí el archivo consolidado (.xlsx)', type='xlsx')

    if archivo:
        try:
            df = pd.read_excel(archivo)
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

            # Variables TIC
            df['acceso_computadora'] = df.get('ip_iii_04', pd.Series()).map({1: 'Sí', 2: 'No'})
            df['acceso_internet'] = df.get('ip_iii_05', pd.Series()).map({1: 'Sí', 2: 'No'})
            df['capacitacion_tic'] = df.get('ip_iii_06', pd.Series()).map({1: 'Sí', 2: 'No'})

            # Nivel educativo
            nivel_ed_col = next((col for col in df.columns if 'nivel_ed' in col), None)
            if nivel_ed_col:
                mapeo = {
                    1: 'Sin instrucción', 2: 'Primario incompleto', 3: 'Primario completo',
                    4: 'Secundario incompleto', 5: 'Secundario completo',
                    6: 'Superior universitario incompleto', 7: 'Superior universitario completo'
                }
                df['nivel_educativo'] = df[nivel_ed_col].map(mapeo)

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

            df[['indice_binario', 'indice_ordinal', 'vulnerabilidad_digital', 'vulnerabilidad_movilidad']] = df.apply(calcular_indices, axis=1)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            output.seek(0)

            st.download_button(
                label='Descargar resultados en Excel',
                data=output,
                file_name='resultados_lote.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
