# ============================================
# DASHBOARD: TURISMO Y CLIMA COSTA RICA 2025-2026
# Proyecto con POO Básica
# ============================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ============================================
# CLASE 1: AnalizadorClima
# ============================================
class AnalizadorClima:
    """
    Clase que analiza datos climáticos mensuales de Costa Rica.
    
    ¿Qué hace esta clase?
    - Carga los datos de clima (2025-2026)
    - Transforma los datos para análisis
    - Calcula estadísticas del clima
    - Crea gráficos relacionados con el clima
    
    Atributos:
    - df_clima: DataFrame con los datos de clima
    """
    
    def __init__(self, ruta_archivo):
        """
        Constructor de la clase.
        
        Parámetros:
        - ruta_archivo: Ruta del CSV con datos de clima
        """
        self.ruta_archivo = r'C:\Users\XPC\Documents\CUC\Cuatri 5\BD - 143 - Programación ll\Trabajos\Proyecto 3\data\processed\clima_costa_rica_datos_transformado.csv'
        self.df_clima = None
        self.df_clima_largo = None  # DataFrame en formato largo
    
    def cargar_datos(self):
        """
        Carga y transforma el archivo CSV de clima.
        
        Returns:
        - bool: True si cargó bien, False si hubo error
        """
        try:
            # Leer CSV
            self.df_clima = pd.read_csv(self.ruta_archivo)
            
            # Transformar a formato largo (más fácil de analizar)
            # De: variable | Jan-25 | Feb-25 | ...
            # A: variable | mes | valor
            
            meses_cols = [col for col in self.df_clima.columns if col != 'variable']
            
            self.df_clima_largo = self.df_clima.melt(
                id_vars=['variable'],
                value_vars=meses_cols,
                var_name='mes',
                value_name='valor'
            )
            
            # Extraer año y mes
            self.df_clima_largo['año'] = self.df_clima_largo['mes'].apply(lambda x: '2025' if '-25' in x else '2026')
            self.df_clima_largo['mes_nombre'] = self.df_clima_largo['mes'].apply(lambda x: x.split('-')[0])
            
            return True
        except Exception as e:
            st.error(f"Error al cargar datos de clima: {e}")
            return False
    
    def obtener_datos_por_variable(self, nombre_variable):
        """
        Obtiene los datos de una variable específica.
        
        Parámetros:
        - nombre_variable: 'temperature_2m_max', 'temperature_2m_min', 'precipitation_sum'
        
        Returns:
        - DataFrame filtrado
        """
        return self.df_clima_largo[self.df_clima_largo['variable'] == nombre_variable].copy()
    
    def calcular_estadisticas_basicas(self):
        """
        Calcula estadísticas básicas del clima.
        
        Returns:
        - dict: Diccionario con las estadísticas
        """
        temp_max = self.obtener_datos_por_variable('temperature_2m_max')
        temp_min = self.obtener_datos_por_variable('temperature_2m_min')
        precip = self.obtener_datos_por_variable('precipitation_sum')
        
        stats = {
            'temp_max_promedio': temp_max['valor'].mean(),
            'temp_min_promedio': temp_min['valor'].mean(),
            'precipitacion_promedio': precip['valor'].mean(),
            'mes_mas_calido': temp_max.loc[temp_max['valor'].idxmax(), 'mes'],
            'mes_mas_lluvioso': precip.loc[precip['valor'].idxmax(), 'mes'],
            'precipitacion_total_2025': precip[precip['año'] == '2025']['valor'].sum()
        }
        return stats
    
    def grafico_temperatura_mensual(self):
        """
        Crea gráfico de evolución de temperatura mensual.
        
        Returns:
        - plotly figure
        """
        temp_max = self.obtener_datos_por_variable('temperature_2m_max')
        temp_min = self.obtener_datos_por_variable('temperature_2m_min')
        
        # Crear gráfico
        fig = go.Figure()
        
        # Temperatura máxima
        fig.add_trace(go.Scatter(
            x=temp_max['mes'],
            y=temp_max['valor'],
            mode='lines+markers',
            name='Temp. Máxima',
            line=dict(color='red', width=3),
            marker=dict(size=8),
            fill='tonexty'
        ))
        
        # Temperatura mínima
        fig.add_trace(go.Scatter(
            x=temp_min['mes'],
            y=temp_min['valor'],
            mode='lines+markers',
            name='Temp. Mínima',
            line=dict(color='blue', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title='Evolución de Temperatura Mensual (2025-2026)',
            xaxis_title='Mes',
            yaxis_title='Temperatura (°C)',
            hovermode='x unified',
            height=400
        )
        
        return fig
    
    def grafico_precipitacion_mensual(self):
        """
        Crea gráfico de precipitación mensual.
        
        Returns:
        - plotly figure
        """
        precip = self.obtener_datos_por_variable('precipitation_sum')
        
        # Crear gráfico de barras
        fig = px.bar(
            precip,
            x='mes',
            y='valor',
            title='Precipitación Mensual (2025-2026)',
            labels={'mes': 'Mes', 'valor': 'Precipitación (mm)'},
            color='valor',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(height=400)
        
        return fig
    
    def grafico_estaciones(self):
        """
        Identifica y muestra las estaciones (seca vs lluviosa).
        
        Returns:
        - plotly figure
        """
        precip = self.obtener_datos_por_variable('precipitation_sum')
        
        # Clasificar estaciones basado en precipitación
        # < 200mm = Seca, >= 200mm = Lluviosa
        precip['estacion'] = precip['valor'].apply(lambda x: 'Estación Seca' if x < 200 else 'Estación Lluviosa')
        
        # Contar meses por estación
        estaciones_count = precip.groupby('estacion').size().reset_index(name='cantidad_meses')
        
        fig = px.pie(
            estaciones_count,
            values='cantidad_meses',
            names='estacion',
            title='Distribución de Estaciones Climáticas',
            color='estacion',
            color_discrete_map={'Estación Seca': '#FFD700', 'Estación Lluviosa': '#1E90FF'}
        )
        
        fig.update_layout(height=400)
        
        return fig


# ============================================
# CLASE 2: AnalizadorTurismo
# ============================================
class AnalizadorTurismo:
    """
    Clase que analiza datos mensuales de turismo de Costa Rica.
    
    ¿Qué hace esta clase?
    - Carga los datos de turismo (2025-2026)
    - Calcula estadísticas de turistas
    - Crea gráficos relacionados con turismo
    
    Atributos:
    - df_turismo: DataFrame con los datos de turismo
    """
    
    def __init__(self, ruta_archivo):
        """
        Constructor de la clase.
        
        Parámetros:
        - ruta_archivo: Ruta del CSV con datos de turismo
        """
        self.ruta_archivo = r'C:\Users\XPC\Documents\CUC\Cuatri 5\BD - 143 - Programación ll\Trabajos\Proyecto 3\data\processed\turismo_combinado_2025_2026.csv'
        self.df_turismo = None
        self.meses_cols = None
    
    def cargar_datos(self):
        """
        Carga el archivo CSV de turismo.
        
        Returns:
        - bool: True si cargó bien, False si hubo error
        """
        try:
            self.df_turismo = pd.read_csv(self.ruta_archivo)
            
            # Identificar columnas de meses
            self.meses_cols = [col for col in self.df_turismo.columns 
                              if '-2025' in col or '-2026' in col]
            
            return True
        except Exception as e:
            st.error(f"Error al cargar datos de turismo: {e}")
            return False
    
    def calcular_estadisticas_basicas(self):
        """
        Calcula estadísticas básicas del turismo.
        
        Returns:
        - dict: Diccionario con las estadísticas
        """
        # Obtener fila de totales
        total_row = self.df_turismo[self.df_turismo['Zona_Pais'] == 'TOTAL'].iloc[0]
        
        # Calcular promedio mensual
        meses_2025 = [col for col in self.meses_cols if '-2025' in col]
        valores_2025 = [total_row[mes] for mes in meses_2025]
        promedio_mensual = np.mean(valores_2025)
        
        # Mes con más y menos turistas
        turistas_mensuales = {mes: total_row[mes] for mes in meses_2025}
        mes_mas_turistas = max(turistas_mensuales, key=turistas_mensuales.get)
        mes_menos_turistas = min(turistas_mensuales, key=turistas_mensuales.get)
        
        stats = {
            'total_2025': total_row['Total_2025'],
            'promedio_mensual_2025': promedio_mensual,
            'mes_mas_turistas': mes_mas_turistas,
            'cantidad_mes_alto': turistas_mensuales[mes_mas_turistas],
            'mes_menos_turistas': mes_menos_turistas,
            'cantidad_mes_bajo': turistas_mensuales[mes_menos_turistas]
        }
        return stats
    
    def grafico_evolucion_mensual(self):
        """
        Crea gráfico de evolución mensual de turistas.
        
        Returns:
        - plotly figure
        """
        total_row = self.df_turismo[self.df_turismo['Zona_Pais'] == 'TOTAL'].iloc[0]
        
        # Obtener datos mensuales
        meses = self.meses_cols
        valores = [total_row[mes] for mes in meses]
        
        # Crear gráfico
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=meses,
            y=valores,
            mode='lines+markers',
            name='Turistas',
            line=dict(color='green', width=3),
            marker=dict(size=10),
            fill='tozeroy',
            fillcolor='rgba(0,255,0,0.1)'
        ))
        
        fig.update_layout(
            title='Evolución Mensual del Turismo (2025-2026)',
            xaxis_title='Mes',
            yaxis_title='Número de Turistas',
            hovermode='x unified',
            height=400
        )
        
        return fig
    
    def grafico_top_regiones(self, top_n=10):
        """
        Crea gráfico de top regiones/países emisores.
        
        Parámetros:
        - top_n: Cantidad de regiones a mostrar
        
        Returns:
        - plotly figure
        """
        # Filtrar datos (excluir totales y continentes)
        zonas_excluir = ['TOTAL', 'AMERICA DEL NORTE', 'AMERICA CENTRAL', 
                        'AMÉRICA DEL SUR', 'CARIBE', 'EUROPA', 'ASIA', 
                        'AFRICA', 'OCEANIA', 'OTROS']
        
        df_paises = self.df_turismo[~self.df_turismo['Zona_Pais'].isin(zonas_excluir)].copy()
        
        # Ordenar por Total_2025 y obtener top
        df_top = df_paises.nlargest(top_n, 'Total_2025')
        
        # Crear gráfico
        fig = px.bar(
            df_top,
            x='Total_2025',
            y='Zona_Pais',
            orientation='h',
            title=f'Top {top_n} Países Emisores de Turistas (2025)',
            labels={'Total_2025': 'Total de Turistas 2025', 'Zona_Pais': 'País'},
            color='Total_2025',
            color_continuous_scale='Greens'
        )
        
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            height=500
        )
        
        return fig
    
    def grafico_participacion_continentes(self):
        """
        Muestra la participación de cada continente.
        
        Returns:
        - plotly figure
        """
        # Obtener solo continentes
        continentes = ['AMERICA DEL NORTE', 'AMERICA CENTRAL', 'AMÉRICA DEL SUR', 'CARIBE']
        df_continentes = self.df_turismo[self.df_turismo['Zona_Pais'].isin(continentes)].copy()
        
        fig = px.pie(
            df_continentes,
            values='Total_2025',
            names='Zona_Pais',
            title='Participación por Continente/Región (2025)',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_layout(height=400)
        
        return fig


# ============================================
# CLASE 3: AnalizadorCombinado
# ============================================
class AnalizadorCombinado:
    """
    Clase que combina análisis de clima y turismo.
    
    Esta clase relaciona el clima con el turismo para encontrar
    hallazgos interesantes.
    
    Atributos:
    - analizador_clima: Objeto de tipo AnalizadorClima
    - analizador_turismo: Objeto de tipo AnalizadorTurismo
    """
    
    def __init__(self, analizador_clima, analizador_turismo):
        """
        Constructor.
        
        Parámetros:
        - analizador_clima: Objeto AnalizadorClima
        - analizador_turismo: Objeto AnalizadorTurismo
        """
        self.clima = analizador_clima
        self.turismo = analizador_turismo
    
    def preparar_datos_combinados(self):
        """
        Prepara datos combinados de clima y turismo.
        
        Returns:
        - DataFrame con datos combinados
        """
        # Obtener datos de turismo total por mes
        total_row = self.turismo.df_turismo[self.turismo.df_turismo['Zona_Pais'] == 'TOTAL'].iloc[0]
        meses_2025 = [col for col in self.turismo.meses_cols if '-2025' in col]
        
        # Crear DataFrame
        datos_combinados = pd.DataFrame({
            'mes': meses_2025,
            'turistas': [total_row[mes] for mes in meses_2025]
        })
        
        # Agregar datos de clima
        temp_max = self.clima.obtener_datos_por_variable('temperature_2m_max')
        precip = self.clima.obtener_datos_por_variable('precipitation_sum')
        
        # Filtrar solo 2025
        temp_max_2025 = temp_max[temp_max['año'] == '2025']
        precip_2025 = precip[precip['año'] == '2025']
        
        # Merge con turismo
        datos_combinados['temperatura'] = temp_max_2025['valor'].values
        datos_combinados['precipitacion'] = precip_2025['valor'].values
        
        return datos_combinados
    
    def grafico_turismo_vs_clima(self):
        """
        Crea gráfico que relaciona turismo con clima.
        
        Returns:
        - plotly figure
        """
        datos = self.preparar_datos_combinados()
        
        # Crear figura con dos ejes Y
        fig = go.Figure()
        
        # Turistas (eje Y izquierdo)
        fig.add_trace(go.Bar(
            x=datos['mes'],
            y=datos['turistas'],
            name='Turistas',
            marker_color='lightgreen',
            yaxis='y',
            opacity=0.7
        ))
        
        # Precipitación (eje Y derecho)
        fig.add_trace(go.Scatter(
            x=datos['mes'],
            y=datos['precipitacion'],
            name='Precipitación',
            line=dict(color='blue', width=3),
            yaxis='y2'
        ))
        
        # Configurar layout con dos ejes Y
        fig.update_layout(
            title='Turistas vs Precipitación por Mes (2025)',
            xaxis=dict(title='Mes'),
            yaxis=dict(
                title='Número de Turistas',
                side='left'
            ),
            yaxis2=dict(
                title='Precipitación (mm)',
                overlaying='y',
                side='right'
            ),
            hovermode='x unified',
            height=500,
            legend=dict(x=0.01, y=0.99)
        )
        
        return fig
    
    def calcular_correlacion(self):
        """
        Calcula la correlación entre clima y turismo.
        
        Returns:
        - dict con correlaciones
        """
        datos = self.preparar_datos_combinados()
        
        # Calcular correlaciones
        corr_temp = datos['turistas'].corr(datos['temperatura'])
        corr_precip = datos['turistas'].corr(datos['precipitacion'])
        
        return {
            'correlacion_temperatura': corr_temp,
            'correlacion_precipitacion': corr_precip
        }
    
    def grafico_tendencia_temporada(self):
        """
        Muestra tendencia de turismo en temporada seca vs lluviosa.
        
        Returns:
        - plotly figure
        """
        datos = self.preparar_datos_combinados()
        
        # Clasificar en temporadas
        datos['temporada'] = datos['precipitacion'].apply(
            lambda x: 'Temporada Seca' if x < 200 else 'Temporada Lluviosa'
        )
        
        # Agrupar por temporada
        por_temporada = datos.groupby('temporada').agg({
            'turistas': 'mean',
            'precipitacion': 'mean'
        }).reset_index()
        
        fig = px.bar(
            por_temporada,
            x='temporada',
            y='turistas',
            title='Promedio de Turistas por Temporada',
            labels={'turistas': 'Promedio de Turistas', 'temporada': 'Temporada'},
            color='temporada',
            color_discrete_map={
                'Temporada Seca': '#FFD700',
                'Temporada Lluviosa': '#1E90FF'
            },
            text='turistas'
        )
        
        fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig.update_layout(height=400)
        
        return fig


# ============================================
# CLASE 4: InterfazDashboard
# ============================================
class InterfazDashboard:
    """
    Clase que maneja la interfaz del dashboard con Streamlit.
    
    Atributos:
    - clima: Objeto AnalizadorClima
    - turismo: Objeto AnalizadorTurismo
    - combinado: Objeto AnalizadorCombinado
    """
    
    def __init__(self, analizador_clima, analizador_turismo, analizador_combinado):
        """
        Constructor.
        """
        self.clima = analizador_clima
        self.turismo = analizador_turismo
        self.combinado = analizador_combinado
    
    def configurar_pagina(self):
        """
        Configura la página de Streamlit.
        """
        st.set_page_config(
            page_title="Turismo y Clima CR 2025-2026 🇨🇷",
            page_icon="🌴",
            layout="wide"
        )
    
    def mostrar_header(self):
        """
        Muestra el encabezado del dashboard.
        """
        st.title("🌴 Dashboard: Turismo y Clima de Costa Rica 2025-2026 🇨🇷")
        st.markdown("---")
        st.markdown("""
        **Análisis mensual de la relación entre el clima y el turismo en Costa Rica**
        
        Este dashboard explora hallazgos interesantes sobre cómo el clima afecta 
        el turismo mes a mes en Costa Rica durante 2025-2026.
        """)
    
    def mostrar_metricas_principales(self):
        """
        Muestra las métricas principales en la parte superior.
        """
        st.markdown("### 📊 Métricas Principales 2025")
        
        # Obtener estadísticas
        stats_clima = self.clima.calcular_estadisticas_basicas()
        stats_turismo = self.turismo.calcular_estadisticas_basicas()
        
        # Crear 5 columnas
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                label="🌡️ Temp. Máx. Promedio",
                value=f"{stats_clima['temp_max_promedio']:.1f}°C"
            )
        
        with col2:
            st.metric(
                label="🌧️ Precipitación Total",
                value=f"{stats_clima['precipitacion_total_2025']:,.0f} mm"
            )
        
        with col3:
            st.metric(
                label="✈️ Total Turistas 2025",
                value=f"{stats_turismo['total_2025']:,.0f}"
            )
        
        with col4:
            st.metric(
                label="📈 Promedio Mensual",
                value=f"{stats_turismo['promedio_mensual_2025']:,.0f}"
            )
        
        with col5:
            # Calcular variación mes más alto vs más bajo
            variacion = ((stats_turismo['cantidad_mes_alto'] - stats_turismo['cantidad_mes_bajo']) / 
                        stats_turismo['cantidad_mes_bajo'] * 100)
            st.metric(
                label="📊 Variación Estacional",
                value=f"{variacion:.1f}%"
            )
        
        st.markdown("---")
    
    def mostrar_hallazgo_1(self):
        """
        HALLAZGO 1: Temporadas claramente diferenciadas
        """
        st.markdown("## 🔍 Hallazgo 1: La lluvia define claramente las temporadas turísticas")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            **Descubrimiento:**
            
            Costa Rica muestra un patrón claro de dos temporadas:
            
            - **🌞 Temporada Seca (Dic-Abr):**
              - Precipitación < 200mm/mes
              - Temperaturas más altas (~26°C)
              - **MÁS turistas**
            
            - **🌧️ Temporada Lluviosa (May-Nov):**
              - Precipitación > 200mm/mes
              - Temperaturas más frescas (~23-24°C)
              - **MENOS turistas**
            
            **Meses extremos:**
            - 🌞 Más seco: Enero-Febrero (~50mm)
            - 🌧️ Más lluvioso: Octubre (~565mm)
            """)
        
        with col2:
            fig_estaciones = self.clima.grafico_estaciones()
            st.plotly_chart(fig_estaciones, use_container_width=True)
        
        # Gráfico de precipitación
        st.markdown("### Precipitación Mensual 2025-2026")
        fig_precip = self.clima.grafico_precipitacion_mensual()
        st.plotly_chart(fig_precip, use_container_width=True)
        
        st.markdown("---")
    
    def mostrar_hallazgo_2(self):
        """
        HALLAZGO 2: Relación inversa entre lluvia y turismo
        """
        st.markdown("## 🔍 Hallazgo 2: A más lluvia, menos turistas (relación inversa)")
        
        # Calcular correlación
        correlaciones = self.combinado.calcular_correlacion()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig_turismo_clima = self.combinado.grafico_turismo_vs_clima()
            st.plotly_chart(fig_turismo_clima, use_container_width=True)
        
        with col2:
            st.markdown(f"""
            **Descubrimiento clave:**
            
            Existe una **correlación negativa** entre 
            precipitación y turismo:
            
            📉 **Correlación lluvia-turismo:**  
            `{correlaciones['correlacion_precipitacion']:.2f}`
            
            **¿Qué significa?**
            - Cuando llueve MÁS → Vienen MENOS turistas
            - Cuando llueve MENOS → Vienen MÁS turistas
            
            **Meses críticos:**
            - 🌞 Dic (145mm): ~347K turistas
            - 🌧️ Oct (565mm): ~146K turistas
            
            **Diferencia:** -58% de turistas en mes lluvioso
            
            **Implicación:**
            El clima es un factor DETERMINANTE 
            para el turismo en Costa Rica.
            """)
        
        # Gráfico de temporadas
        st.markdown("### Comparación por Temporada")
        fig_temporada = self.combinado.grafico_tendencia_temporada()
        st.plotly_chart(fig_temporada, use_container_width=True)
        
        st.markdown("---")
    
    def mostrar_hallazgo_3(self):
        """
        HALLAZGO 3: Estados Unidos domina completamente
        """
        st.markdown("## 🔍 Hallazgo 3: Estados Unidos representa más de la mitad del turismo")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig_top = self.turismo.grafico_top_regiones(top_n=15)
            st.plotly_chart(fig_top, use_container_width=True)
        
        with col2:
            # Obtener datos de EE.UU.
            usa_row = self.turismo.df_turismo[self.turismo.df_turismo['Zona_Pais'] == 'ESTADOS UNIDOS'].iloc[0]
            total_row = self.turismo.df_turismo[self.turismo.df_turismo['Zona_Pais'] == 'TOTAL'].iloc[0]
            
            porcentaje_usa = (usa_row['Total_2025'] / total_row['Total_2025']) * 100
            
            st.markdown(f"""
            **Descubrimiento:**
            
            Estados Unidos domina el mercado turístico 
            de forma abrumadora:
            
            🇺🇸 **Estados Unidos:**
            - {usa_row['Total_2025']:,.0f} turistas
            - **{porcentaje_usa:.1f}%** del total
            
            **Top 5 países (2025):**
            1. 🇺🇸 EE.UU.: ~1.63M
            2. 🇨🇦 Canadá: ~274K
            3. 🇲🇽 México: ~98K
            4. 🇳🇮 Nicaragua: ~98K
            5. 🇬🇹 Guatemala: ~46K
            
            **Problema:**
            - Alta dependencia de un solo país
            - Vulnerabilidad ante crisis en EE.UU.
            
            **Oportunidad:**
            - Diversificar mercados
            - Atraer más europeos y asiáticos
            """)
        
        # Participación por continente
        st.markdown("### Participación por Continente/Región")
        fig_continentes = self.turismo.grafico_participacion_continentes()
        st.plotly_chart(fig_continentes, use_container_width=True)
        
        st.markdown("---")
    
    def mostrar_hallazgo_4(self):
        """
        HALLAZGO 4: Patrones mensuales predecibles
        """
        st.markdown("## 🔍 Hallazgo 4: El turismo sigue un patrón mensual muy predecible")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig_evolucion = self.turismo.grafico_evolucion_mensual()
            st.plotly_chart(fig_evolucion, use_container_width=True)
        
        with col2:
            stats = self.turismo.calcular_estadisticas_basicas()
            
            st.markdown(f"""
            **Descubrimiento:**
            
            El turismo muestra un patrón mensual 
            altamente predecible:
            
            **Temporada ALTA (Dic-Abr):**
            - Pico en Diciembre: ~347K turistas
            - Marzo también alto: ~336K turistas
            - Coincide con verano del hemisferio norte
            
            **Temporada BAJA (May-Nov):**
            - Mínimo en Septiembre: ~122K turistas
            - Mayo-Octubre: < 250K turistas/mes
            - Coincide con época lluviosa
            
            **Patrón:**
            📈 Dic-Mar: Alta (temporada seca)  
            📉 Abr-Nov: Baja (temporada lluviosa)  
            📈 Dic: Repunta (fiestas de fin de año)
            
            **Variación estacional:**
            - Diferencia mes alto-bajo: **185%**
            - Muy marcada estacionalidad
            """)
        
        # Temperatura
        st.markdown("### Temperatura Mensual")
        fig_temp = self.clima.grafico_temperatura_mensual()
        st.plotly_chart(fig_temp, use_container_width=True)
        
        st.markdown("---")
    
    def mostrar_conclusiones(self):
        """
        Muestra las conclusiones finales.
        """
        st.markdown("## 🎯 Conclusiones y Recomendaciones")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 📌 Principales Hallazgos:
            
            1. **🌧️ La lluvia es el factor determinante:**
               - Correlación negativa clara entre lluvia y turismo
               - Temporada seca (Dic-Abr) = Temporada alta
               - Octubre (mes más lluvioso) = Mes con menos turistas
            
            2. **🇺🇸 Altísima dependencia de EE.UU.:**
               - 55%+ del turismo viene de un solo país
               - Riesgo de concentración de mercado
               - Nicaragua y Canadá muy lejos del segundo lugar
            
            3. **📅 Estacionalidad muy marcada:**
               - Diferencia de 185% entre mes alto y bajo
               - Patrón predecible año tras año
               - Diciembre es el pico absoluto
            
            4. **🌡️ Clima relativamente estable:**
               - Temperatura varía poco (23-26°C)
               - La precipitación es la variable clave
               - Septiembre-Octubre: meses críticos
            """)
        
        with col2:
            st.markdown("""
            ### 💡 Recomendaciones Estratégicas:
            
            **Para el Sector Turístico:**
            
            1. **📢 Marketing diferenciado:**
               - Promoción agresiva en temporada seca
               - Ofertas especiales en temporada lluviosa
               - Enfatizar ecoturismo en época de lluvia
            
            2. **🌍 Diversificación de mercados:**
               - Atraer más turistas europeos
               - Desarrollar mercado asiático
               - Reducir dependencia de EE.UU.
            
            3. **🎯 Productos por temporada:**
               - Temporada seca: Playa, aventura
               - Temporada lluviosa: Cultura, wellness, naturaleza
               - Aprovechar lluvia para observación de fauna
            
            4. **💰 Estrategia de precios:**
               - Precios premium en temporada alta
               - Descuentos atractivos en temporada baja
               - Paquetes especiales en meses valle
            
            5. **🏨 Gestión de capacidad:**
               - Planificar personal según estacionalidad
               - Mantenimiento en temporada baja
               - Overbooking controlado en alta
            """)
        
        st.markdown("---")
        
        st.markdown("""
        ### 🔮 Predicciones para 2026:
        
        Basado en los patrones observados:
        - **Enero-Febrero 2026:** Mantendrá niveles altos (~295-300K turistas/mes)
        - **Temporada seca 2026:** Similar a 2025 si clima se mantiene
        - **Dependencia de EE.UU.:** Seguirá siendo alta sin estrategia de diversificación
        - **Estacionalidad:** Continuará marcada mientras no cambien patrones climáticos
        """)
    
    def ejecutar(self):
        """
        Método principal que ejecuta todo el dashboard.
        """
        self.configurar_pagina()
        self.mostrar_header()
        self.mostrar_metricas_principales()
        self.mostrar_hallazgo_1()
        self.mostrar_hallazgo_2()
        self.mostrar_hallazgo_3()
        self.mostrar_hallazgo_4()
        self.mostrar_conclusiones()


# ============================================
# FUNCIÓN PRINCIPAL
# ============================================
def main():
    """
    Función principal que inicializa y ejecuta el dashboard.
    """
    # PASO 1: Crear analizadores
    analizador_clima = AnalizadorClima('clima_costa_rica_datos_transformado.csv')
    analizador_turismo = AnalizadorTurismo('turismo_combinado_2025_2026.csv')
    
    # PASO 2: Cargar datos
    if not analizador_clima.cargar_datos():
        st.stop()
    
    if not analizador_turismo.cargar_datos():
        st.stop()
    
    # PASO 3: Crear analizador combinado
    analizador_combinado = AnalizadorCombinado(analizador_clima, analizador_turismo)
    
    # PASO 4: Crear interfaz
    interfaz = InterfazDashboard(analizador_clima, analizador_turismo, analizador_combinado)
    
    # PASO 5: Ejecutar dashboard
    interfaz.ejecutar()


# ============================================
# PUNTO DE ENTRADA
# ============================================
if __name__ == "__main__":
    main()
