# Este archivo contendrá todas las funciones de análisis. De momento, está vacío.

import pandas as pd

def resumen_descriptivo(df_hogar, df_ind):
    return df_hogar.describe(include='all').T, df_ind.describe(include='all').T

def generar_cruces(df):
    return df.groupby(['sexo', 'edad']).size().reset_index(name='frecuencia')

def calcular_exclusion_digital(df):
    df = df.copy()
    df['indice_binario'] = ((df['acceso_computadora'] == 0) & (df['acceso_internet'] == 0) & (df['capacitacion_tic'] == 0)).astype(int)
    return df[['indice_binario']]

def movilidad_social(df):
    return df[['nivel_educativo', 'actividad']].value_counts().reset_index(name='frecuencia')

def modelo_logistico(df):
    return pd.DataFrame({'modelo': ['pendiente'], 'valor': [0.5]})

def clusterizar(df):
    return pd.DataFrame({'cluster': [0,1,1], 'frecuencia': [100,200,150]})

def construir_indice_compuesto(df):
    df['indice_compuesto'] = df.select_dtypes(include='number').mean(axis=1)
    return df[['indice_compuesto']]
