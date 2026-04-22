# Proyecto: Análisis y Predicción del Turismo en Costa Rica  
  
Este proyecto desarrolla un **modelo de análisis y predicción del turismo mensual en Costa Rica**, integrando variables climáticas, datos históricos de visitantes y metodologías de aprendizaje automático (Machine Learning).  
  
La aplicación final incluye:  
- Entrenamiento y evaluación de modelos de predicción.  
- Simulación de escenarios climáticos futuros.  
- Visualizaciones geográficas y mapas interactivos.  
- Dashboard interactivo con Streamlit.

-   
---  
  
## Objetivo  
  
Desarrollar una herramienta que permita **analizar patrones históricos del turismo** y **predecir escenarios futuros** considerando variables como:  
  
- Temperatura máxima y mínima  
- Precipitación  
- Zona de origen de turistas  
- Tendencias anuales y mensuales  
  
---  
  
## Modelos utilizados  
  
| Modelo | Descripción | Métrica R² | RMSE |  
|---------|--------------|-------------|-------|  
| **Regresión Lineal** | Modelo base para relaciones lineales | ~0.61 | ≈21 000 |  
| **KNN Regressor** | Modelo basado en vecinos más cercanos | ~0.58 | ≈23 500 |  
| **Random Forest Regressor** | Modelo ensamble no lineal | ~0.86 | ≈14 500 |  
  
➡️ El modelo seleccionado para predicciones es **Random Forest**, por su mejor desempeño en exactitud y estabilidad.  
  
---  
  
## Simulación de escenarios futuros  
  
El proyecto permite simular distintos **escenarios climáticos** para estimar métricas de turismo:  
  
| Escenario | Descripción |  
|------------|-------------|  
| `normal` | Condiciones promedio de clima |  
| `lluvias_altas` | Incremento de precipitación |  
| `sequía` | Disminución de lluvia |  
| `calor_extremo` | Aumento significativo en temperatura |  
  
---  
  
## Visualizaciones  
  
Incluye módulos de visualización con gráficos estáticos y mapas geográficos:  
  
### Ejemplos:  
- Mapas interactivos con **Folium**.  
- Mapas de calor de distribución turística.  
- Rutas de flujo de turistas desde países de origen hacia Costa Rica.  
- Gráficos comparativos de desempeño de modelos.  
  
---  
