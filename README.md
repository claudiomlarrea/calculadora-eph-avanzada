
# 📊 Calculadora Cuantitativa EPH

Esta aplicación en Streamlit permite cargar bases de datos anuales de la Encuesta Permanente de Hogares (EPH) y generar automáticamente dos productos descargables:

1. 📈 Un archivo Excel con el análisis estadístico anual por hogares e individuos.
2. 📄 Un informe en Word con interpretación detallada, explicaciones desarrolladas y conclusiones útiles para políticas públicas.

---

## ✅ ¿Qué hace la calculadora?

- Renombra automáticamente las columnas según el instructivo oficial del INDEC.
- Detecta y utiliza variables relevantes incluso si no son renombradas.
- Filtra duplicados y consolida hogares e individuos por año.
- Ofrece estadísticas descriptivas completas.
- Genera un informe en Word con:
  - Introducción
  - Análisis por hogares
  - Análisis por individuos
  - Interpretación por categoría (sexo, edad, ingresos, educación)
  - Brechas e indicadores sociales clave
  - Conclusiones y recomendaciones

---

## 📥 Archivos que se deben subir

1. Base de datos de hogares (.xlsx)
2. Base de datos de individuos (.xlsx)
3. Instructivo oficial del INDEC en PDF
4. Seleccionar el año correspondiente desde el menú

---

## 🧾 Requisitos (ya incluidos en `requirements.txt`)

- `streamlit`
- `pandas`
- `openpyxl`
- `python-docx`
- `PyMuPDF`
- `matplotlib`
- `scikit-learn`
- `statsmodels`
- `numpy`
- `xlsxwriter`

---

## 🚀 Ejecutar en Streamlit Cloud

1. Subir los archivos a un repositorio GitHub
2. Crear app en [https://streamlit.io/cloud](https://streamlit.io/cloud)
3. Seleccionar `streamlit_app.py` como archivo principal

---

## 👥 Autores

Aplicación desarrollada con fines académicos, institucionales y de investigación. Lista para ser usada en universidades, organismos públicos y equipos técnicos.

---

