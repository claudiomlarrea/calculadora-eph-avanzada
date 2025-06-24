import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import statsmodels.api as sm

def resumen_descriptivo(df_hogar, df_ind):
    return df_hogar.describe(include='all').T, df_ind.describe(include='all').T

def generar_cruces(df):
    return df.groupby(['sexo', 'nivel_educativo']).agg({
        'acceso_internet': lambda x: (x == 'Sí').mean() * 100
    }).reset_index()

def calcular_exclusion_digital(df):
    df = df.copy()
    df['excluido'] = ((df['acceso_computadora'] == 'No') & (df['acceso_internet'] == 'No')).astype(int)
    return df[['sexo', 'edad', 'nivel_educativo', 'excluido']]

def movilidad_social(df):
    return df.groupby(['nivel_educativo', 'actividad']).size().reset_index(name='frecuencia')

def modelo_logistico(df):
    df = df.dropna(subset=['edad', 'sexo', 'nivel_educativo', 'excluido'])
    df['sexo'] = df['sexo'].map({'Varón': 0, 'Mujer': 1})
    X = pd.get_dummies(df[['edad', 'sexo', 'nivel_educativo']], drop_first=True)
    y = df['excluido']
    model = sm.Logit(y, sm.add_constant(X)).fit(disp=0)
    summary = model.summary2().tables[1]
    return summary

def clusterizar(df):
    df_numeric = df.select_dtypes(include=np.number).dropna()
    model = KMeans(n_clusters=3, random_state=0).fit(df_numeric)
    df_out = df_numeric.copy()
    df_out['cluster'] = model.labels_
    return df_out

def construir_indice_compuesto(df):
    df = df.copy()
    df['indice_compuesto'] = df[['edad']].apply(lambda x: (x - x.min()) / (x.max() - x.min()))
    return df[['edad', 'indice_compuesto']]

