import streamlit as st
import pandas as pd
import io
import fitz
import re
from docx import Document
from analyzer import (
    definicion_exclusion_digital,
    resumen_descriptivo, 
    generar_cruces, 
    calcular_exclusion_digital,
    movilidad_social,
    modelo_logistico,
    clusterizar,
    construir_indice_compuesto,
    generar_informe_word_completo
)

st.set_page_config(page_title="Calculadora EPH – Informe Automático", layout="wide")

# Título y descripción
st.title("📊 Calculadora EPH – Informe Integral Automático")
st.markdown("### Análisis completo de bases EPH con informe Word detallado")

# Información sobre la aplicación
st.info("""
**Esta calculadora genera automáticamente:**
- ✅ Informe Word completo con análisis detallado por apartados
- ✅ Valores absolutos y porcentajes para todas las variables
- ✅ Estadísticas descriptivas completas
- ✅ Análisis de hogares e individuos por separado
- ✅ Cruces de variables y análisis correlacional
- ✅ Archivo Excel con todos los cálculos
""")

# Selección de año
anio = st.selectbox(
    "📅 Seleccioná el año de la base EPH", 
    ["2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024"]
)

# Carga de archivos
# NUEVO BLOQUE DE CARGA DE ARCHIVOS

# Carga de archivos (4 bases + instructivo)
col1, col2 = st.columns(2)
with col1:
    hogares_file = st.file_uploader("🏠 Base de Hogares EPH (.xlsx)", type="xlsx", key="hogares_eph")
    hogares_tic_file = st.file_uploader("🏠 Base de Hogares TIC (.xlsx)", type="xlsx", key="hogares_tic")
with col2:
    individuos_file = st.file_uploader("👤 Base de Individuos EPH (.xlsx)", type="xlsx", key="individuos_eph")
    individuos_tic_file = st.file_uploader("👤 Base de Individuos TIC (.xlsx)", type="xlsx", key="individuos_tic")

# Instructivo de variables
instructivo_pdf = st.file_uploader("📄 Instructivo PDF de códigos", type="pdf")


with col1:
    hogares_file = st.file_uploader("🏠 Base de Hogares (.xlsx)", type="xlsx")
    
with col2:
    individuos_file = st.file_uploader("👤 Base de Individuos (.xlsx)", type="xlsx")
    
with col3:
    instructivo_pdf = st.file_uploader("📄 Instructivo PDF", type="pdf")

def limpiar_descripcion_variable(desc):
    """Limpia las descripciones de variables del instructivo"""
    desc = desc.replace(".....", "").replace("....", "").replace("...", "").strip()
    return desc.strip().capitalize()

def extraer_diccionario_desde_pdf(pdf_file):
    """Extrae el diccionario de variables desde el PDF instructivo"""
    try:
        text = ""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        for page in doc:
            text += page.get_text()
        doc.close()
        
        # Patrón para extraer variables
        regex = re.compile(r"^(\w{2,})\s+[NC]\(\d+\)\s+(.+)$", re.MULTILINE)
        matches = regex.findall(text)
        
        diccionario = {}
        for codigo, desc in matches:
            diccionario[codigo.strip()] = limpiar_descripcion_variable(desc)
            
        return diccionario
    except Exception as e:
        st.error(f"Error al procesar el PDF: {str(e)}")
        return {}

def procesar_datos(df_hogar, df_ind, mapa_variables):
    """Procesa y limpia los datos de hogares e individuos"""
    
    # Aplicar mapeo de variables si está disponible
    if mapa_variables:
        df_hogar = df_hogar.rename(columns=mapa_variables)
        df_ind = df_ind.rename(columns=mapa_variables)
    
    # Identificar columnas relevantes para hogares
    palabras_clave_hogar = ["región", "region", "agua", "baño", "bano", "vivienda", "tipo", 
                           "ipcf", "itf", "ingreso", "total", "familiar", "pondih"]
    
    cols_hogar = []
    for col in df_hogar.columns:
        if any(palabra in col.lower() for palabra in palabras_clave_hogar):
            cols_hogar.append(col)
    
    # Identificar columnas relevantes para individuos
    palabras_clave_ind = ["sexo", "edad", "educ", "educación", "educacion", "nivel", "actividad", 
                         "estado", "ingreso", "ocupación", "ocupacion", "ch04", "ch06", "pondiim"]
    
    cols_ind = []
    for col in df_ind.columns:
        if any(palabra in col.lower() for palabra in palabras_clave_ind):
            cols_ind.append(col)
    
    # Filtrar DataFrames
    df_hogar_filtrado = df_hogar[cols_hogar] if cols_hogar else df_hogar
    df_ind_filtrado = df_ind[cols_ind] if cols_ind else df_ind
    
    return df_hogar_filtrado, df_ind_filtrado, cols_hogar, cols_ind

def generar_archivo_excel(df_hogar, df_ind, cols_hogar, cols_ind):
    """Genera archivo Excel con todos los análisis"""
    
    output_excel = io.BytesIO()
    
    with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
        
        # Resúmenes descriptivos
        resumen_hogar, resumen_ind = resumen_descriptivo(df_hogar, df_ind)
        resumen_hogar.to_excel(writer, sheet_name="Resumen Hogares")
        resumen_ind.to_excel(writer, sheet_name="Resumen Individuos")
        
        # Datos originales (muestra)
        df_hogar.head(1000).to_excel(writer, sheet_name="Muestra Hogares", index=False)
        df_ind.head(1000).to_excel(writer, sheet_name="Muestra Individuos", index=False)
        
        # Análisis adicionales si hay datos suficientes
        try:
            # Cruces de variables (si existen las columnas necesarias)
            if any('sexo' in col.lower() for col in df_ind.columns):
                cruces = generar_cruces(df_ind)
                cruces.to_excel(writer, sheet_name="Cruces Variables", index=False)
        except Exception as e:
            st.warning(f"No se pudieron generar algunos análisis cruzados: {str(e)}")
        
        # Información de las columnas utilizadas
        info_cols = pd.DataFrame({
            'Columnas Hogares': pd.Series(cols_hogar),
            'Columnas Individuos': pd.Series(cols_ind)
        })
        info_cols.to_excel(writer, sheet_name="Información Columnas", index=False)
    
    output_excel.seek(0)
    return output_excel


# Procesamiento principal de las 4 bases
if hogares_file and individuos_file and hogares_tic_file and individuos_tic_file and instructivo_pdf:

    with st.spinner("🔄 Procesando archivos cargados..."):

        try:
            # Cargar bases
            df_hogar = pd.read_excel(hogares_file)
            df_ind = pd.read_excel(individuos_file)
            df_hogar_tic = pd.read_excel(hogares_tic_file)
            df_ind_tic = pd.read_excel(individuos_tic_file)

            # Unir TIC a EPH por claves
            claves_hogar = ['CODUSU', 'NRO_HOGAR', 'AGLOMERADO']
            claves_ind = ['CODUSU', 'NRO_HOGAR', 'COMPONENTE', 'AGLOMERADO']

            df_hogar_merged = pd.merge(df_hogar, df_hogar_tic, on=claves_hogar, how="left")
            df_ind_merged = pd.merge(df_ind, df_ind_tic, on=claves_ind, how="left")

            df_merged = pd.merge(df_ind_merged, df_hogar_merged, on=["CODUSU", "NRO_HOGAR", "AGLOMERADO"], how="left")

            st.success(f"✅ Bases unidas correctamente. Registros: {len(df_merged):,}")

        except Exception as e:
            st.error(f"❌ Error al unir las bases: {e}")
            st.stop()


# Procesamiento principal
if hogares_file and individuos_file and instructivo_pdf:
    
    with st.spinner("🔄 Procesando archivos..."):
        
        # Extraer diccionario de variables
        mapa_variables = extraer_diccionario_desde_pdf(instructivo_pdf)
        
        # Cargar bases de datos
        try:
            df_hogar = pd.read_excel(hogares_file)
            df_ind = pd.read_excel(individuos_file)
            
            st.success(f"✅ Archivos cargados exitosamente")
            st.info(f"📊 Hogares: {len(df_hogar):,} registros | Individuos: {len(df_ind):,} registros")
            
        except Exception as e:
            st.error(f"❌ Error al cargar los archivos Excel: {str(e)}")
            st.stop()
    
    with st.spinner("🔍 Analizando datos..."):
        
        # Procesar datos
        df_hogar_proc, df_ind_proc, cols_hogar, cols_ind = procesar_datos(df_hogar, df_ind, mapa_variables)
        
        # Mostrar información de las variables encontradas
        with st.expander("📋 Variables identificadas para el análisis"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Variables de Hogares:**")
                for col in cols_hogar[:10]:  # Mostrar primeras 10
                    st.write(f"• {col}")
                if len(cols_hogar) > 10:
                    st.write(f"... y {len(cols_hogar) - 10} más")
            
            with col2:
                st.write("**Variables de Individuos:**")
                for col in cols_ind[:10]:  # Mostrar primeras 10
                    st.write(f"• {col}")
                if len(cols_ind) > 10:
                    st.write(f"... y {len(cols_ind) - 10} más")
    
    with st.spinner("📝 Generando informe Word completo..."):
        
        try:
            # Generar informe Word completo
            output_word = generar_informe_word_completo(
                anio, 
                df_hogar_proc, 
                df_ind_proc, 
                mapa_variables
            )
            
            # Generar archivo Excel
            output_excel = generar_archivo_excel(
                df_hogar_proc, 
                df_ind_proc, 
                cols_hogar, 
                cols_ind
            )
            
            st.success("✅ ¡Análisis completado exitosamente!")
            
        except Exception as e:
            st.error(f"❌ Error al generar los informes: {str(e)}")
            st.stop()
    
    # Mostrar resumen de resultados
    st.markdown("### 📈 Resumen de Resultados")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏠 Total Hogares", f"{len(df_hogar):,}")
    
    with col2:
        st.metric("👤 Total Individuos", f"{len(df_ind):,}")
    
    with col3:
        st.metric("📊 Variables Hogares", len(cols_hogar))
    
    with col4:
        st.metric("📊 Variables Individuos", len(cols_ind))
    
    # Botones de descarga
    st.markdown("### 📥 Descargar Resultados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📄 Descargar Informe Word Completo",
            data=output_word.getvalue(),
            file_name=f"informe_eph_completo_{anio}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            help="Informe Word con análisis detallado por apartados"
        )
    
    with col2:
        st.download_button(
            label="📊 Descargar Análisis Excel",
            data=output_excel.getvalue(),
            file_name=f"analisis_eph_{anio}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Archivo Excel con todos los cálculos y análisis"
        )
    
    # Vista previa de algunos análisis
    with st.expander("👀 Vista previa de análisis"):
        
        tab1, tab2 = st.tabs(["Resumen Hogares", "Resumen Individuos"])
        
        with tab1:
            resumen_hogar, _ = resumen_descriptivo(df_hogar_proc, df_ind_proc)
            st.dataframe(resumen_hogar.head(10), use_container_width=True)
        
        with tab2:
            _, resumen_ind = resumen_descriptivo(df_hogar_proc, df_ind_proc)
            st.dataframe(resumen_ind.head(10), use_container_width=True)

else:
    # Instrucciones de uso
    st.markdown("### 📋 Instrucciones de Uso")
    
    st.markdown("""
    **Paso 1:** Selecciona el año de la base EPH (2017-2024)
    
    **Paso 2:** Sube los archivos requeridos:
    - 🏠 **Base de Hogares**: Archivo Excel con datos de hogares
    - 👤 **Base de Individuos**: Archivo Excel con datos de individuos  
    - 📄 **Instructivo PDF**: Documento con definiciones de variables
    
    **Paso 3:** La aplicación generará automáticamente:
    - 📄 **Informe Word completo** con análisis detallado por apartados
    - 📊 **Archivo Excel** con todos los cálculos y análisis
    """)
    
    st.markdown("### 🎯 Contenido del Informe Word")
    
    st.markdown("""
    **El informe incluye:**
    - 📊 **Resumen ejecutivo** con principales hallazgos
    - 🏠 **Análisis de hogares** con distribución regional, tipo de vivienda, servicios básicos
    - 👤 **Análisis de individuos** con estructura demográfica, educativa y laboral
    - 💰 **Análisis de ingresos** con estadísticas descriptivas completas
    - 📈 **Valores absolutos y porcentajes** para todas las variables
    - 🔍 **Análisis cruzados** y correlaciones
    - 📋 **Conclusiones y recomendaciones** de política pública
    """)
    
    st.info("👆 **Sube los archivos requeridos para comenzar el análisis**"
        # Tablas conceptuales (componentes, brechas e implicancias)
        try:
            conceptos = definicion_exclusion_digital()
            for nombre, tabla in conceptos.items():
                tabla.to_excel(writer, sheet_name=nombre[:30], index=False)
        except Exception as e:
            st.warning(f"No se pudieron generar las tablas teóricas de exclusión digital: {str(e)}")

)
