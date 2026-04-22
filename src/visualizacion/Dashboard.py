# src/dashboard/dashboard_modelos.py
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import joblib
import numpy as np

# ================================
# CONFIGURACIÓN DE PÁGINA
# ================================
st.set_page_config(page_title="Dashboard Predicción Turismo Costa Rica",
                   layout="wide",
                   page_icon="none")

st.title("🌎 Dashboard de Modelado y Predicción del Turismo en Costa Rica")
st.markdown("---")

# ================================
# CARGA DE DATOS
# ================================
st.sidebar.header("📂 Opciones de entrada")

ruta_resultados = st.sidebar.text_input("Ruta del archivo resultados (CSV)", "../data/processed/resultados_modelos.csv")
ruta_modelo = st.sidebar.text_input("Ruta del modelo entrenado (.pkl)", "../models/modelo_turismo_rf.pkl")

# Intentar cargar
try:
    resultados = pd.read_csv(ruta_resultados)
    st.success(f"✅ Resultados cargados ({resultados.shape})")
except Exception as e:
    st.warning("⚠️ No se encontró archivo de resultados. Usa datos de muestra.")
    resultados = pd.DataFrame({
        'Modelo': ['Regresión Lineal', 'KNN', 'Random Forest'],
        'R2_Test': [0.61, 0.58, 0.86],
        'RMSE_Test': [21000, 23500, 14500],
        'CV_Promedio': [0.60, 0.55, 0.84]
    })

# ================================
# SECCIÓN: COMPARACIÓN DE MODELOS
# ================================
st.subheader("📊 Comparación de desempeño entre modelos")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### **R² en conjunto de prueba**")
    fig1, ax1 = plt.subplots(figsize=(6,4))
    sns.barplot(x='Modelo', y='R2_Test', data=resultados, palette='viridis', ax=ax1)
    ax1.set_title("Comparación de R² (mayor es mejor)")
    st.pyplot(fig1)

with col2:
    st.markdown("#### **RMSE en conjunto de prueba**")
    fig2, ax2 = plt.subplots(figsize=(6,4))
    sns.barplot(x='Modelo', y='RMSE_Test', data=resultados, palette='magma', ax=ax2)
    ax2.set_title("Comparación de RMSE (menor es mejor)")
    st.pyplot(fig2)

st.markdown("---")

# ================================
# SECCIÓN: SIMULACIÓN FUTURA
# ================================
st.subheader("🔮 Simulación de escenarios turísticos futuros")

# Cargar el modelo Random Forest
try:
    rf = joblib.load(ruta_modelo)
    st.success("✅ Modelo RandomForest cargado correctamente.")
except:
    st.error("❌ No se pudo cargar el modelo. Verifica la ruta o entrena antes.")

# Parámetros del escenario
col1, col2, col3 = st.columns(3)
año = col1.number_input("Año de predicción", 2026, 2035, 2026)
mes_inicio = col2.number_input("Mes inicial", 1, 12, 3)
mes_fin = col3.number_input("Mes final", 1, 12, 12)

escenario = st.selectbox("Escenario climático", ['normal', 'lluvias_altas', 'sequía', 'calor_extremo'])

# Botón para lanzar predicción
if st.button("🔁 Generar predicción"):
    # Simulación básica de datos futuros
    meses = [f"{str(m).zfill(2)}-{año}" for m in range(mes_inicio, mes_fin+1)]
    clima_mean = {'temperature_2m_max': 29, 'temperature_2m_min': 20, 'precipitation_sum': 180}
    np.random.seed(42)
    df_futuro = pd.DataFrame({
        'Mes': meses,
        'Año': año,
        'Mes_Num': [int(mes[:2]) for mes in meses],
        'temperature_2m_max': clima_mean['temperature_2m_max'] + np.random.uniform(-3, 3, len(meses)),
        'temperature_2m_min': clima_mean['temperature_2m_min'] + np.random.uniform(-2, 2, len(meses)),
        'precipitation_sum': clima_mean['precipitation_sum'] * np.random.uniform(0.8, 1.2, len(meses))
    })

    # Predicciones simuladas (si existiera el modelo)
    try:
        pred = rf.predict(df_futuro)
    except Exception as e:
        st.warning("⚠️ No se pudo predecir con el modelo real, usando datos simulados.")
        pred = np.random.uniform(200000, 400000, len(meses))

    df_futuro['Pred_Turistas'] = pred
    st.dataframe(df_futuro)

    # Gráfico con línea de tiempo
    st.markdown("#### 📈 Predicción mensual de turistas")
    fig_pred, ax_pred = plt.subplots(figsize=(10,5))
    sns.lineplot(data=df_futuro, x='Mes_Num', y='Pred_Turistas', marker='o', color='teal', ax=ax_pred)
    ax_pred.set_title(f"Predicción de Turismo - Escenario {escenario} {año}")
    ax_pred.set_xlabel("Mes")
    ax_pred.set_ylabel("Turistas estimados")
    st.pyplot(fig_pred)

# ================================
# SECCIÓN EXTRA: INSPECCIÓN DE DATOS
# ================================
st.subheader("🧾 Dataset usado en el modelado")
st.dataframe(resultados)
