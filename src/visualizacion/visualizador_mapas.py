# src/visualizacion/visualizador_mapas.py

import geopandas as gpd
import matplotlib.pyplot as plt
import folium
from folium.plugins import HeatMap
import plotly.express as px
import pandas as pd


class VisualizadorMapas:
    """
    Clase VisualizadorMapas
    ------------------------
    Crea visualizaciones geográficas del turismo y clima en Costa Rica,
    incluyendo:
    - Mapas estáticos (choropleth)
    - Mapas interactivos (puntos por zona)
    - Mapas de calor (intensidad de visitas)
    - Mapas de flujo (rutas desde países de origen hacia Costa Rica)
    """

    def __init__(self):
        self.mapa_base = None

    # ======================================================================
    # MAPA CHOROPLETH
    # ======================================================================
    def mapa_choropleth(self, df_turismo, shapefile_path,
                        col_zona='Zona_Pais', col_valor='Turistas'):
        """
        Genera un mapa estático tipo choropleth donde el color representa
        el número de turistas por zona (require shapefile o geojson).
        """
        gdf = gpd.read_file(shapefile_path)
        df_plot = gdf.merge(df_turismo, left_on='NAME', right_on=col_zona, how='left')

        df_plot.plot(column=col_valor, cmap='YlOrRd', legend=True, figsize=(10, 6))
        plt.title("Distribución de turistas por región")
        plt.axis("off")
        plt.show()

    # ======================================================================
    # MAPA INTERACTIVO
    # ======================================================================
    def mapa_interactivo(self, df_turismo,
                         lat_col='Lat', lon_col='Lon', valor_col='Turistas',
                         color='blue'):
        """
        Crea un mapa interactivo con marcadores circulares para cada zona.
        """
        m = folium.Map(location=[9.75, -83.75], zoom_start=3, tiles='CartoDB positron')

        for _, row in df_turismo.iterrows():
            if pd.notnull(row[lat_col]) and pd.notnull(row[lon_col]):
                folium.CircleMarker(
                    location=[row[lat_col], row[lon_col]],
                    radius=max(row[valor_col] / 50000, 3),
                    popup=f"<b>{row['Zona_Pais']}</b><br>Turistas: {int(row[valor_col])}",
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.6
                ).add_to(m)

        return m

    # ======================================================================
    # MAPA DE CALOR
    # ======================================================================
    def mapa_calor(self, df_turismo, lat_col='Lat', lon_col='Lon', valor_col='Turistas'):
        """
        Genera un mapa de calor donde la intensidad refleja número de turistas.
        """
        m = folium.Map(location=[9.75, -83.75], zoom_start=3, tiles='CartoDB positron')
        heat_data = [[row[lat_col], row[lon_col], row[valor_col]]
                     for _, row in df_turismo.iterrows()
                     if pd.notnull(row[lat_col]) and pd.notnull(row[lon_col])]
        HeatMap(heat_data, radius=15).add_to(m)
        return m

    # ======================================================================
    # MAPA DE FLUJO (RUTAS DESDE PAÍSES DE ORIGEN)
    # ======================================================================
    def mapa_flujo(self, df_origen, lat_col='Lat', lon_col='Lon',
                   valor_col='Turistas', destino=(9.7489, -83.7534)):
        """
        Muestra rutas de flujo turístico desde países de origen hacia Costa Rica.
        Cada línea representa el volumen de turistas.
        """
        m = folium.Map(location=destino, zoom_start=3, tiles='CartoDB positron')

        # Marcador del destino (Costa Rica)
        folium.Marker(
            location=destino,
            popup='Costa Rica (Destino)',
            icon=folium.Icon(color='green', icon='home')
        ).add_to(m)

        # Crear las rutas de flujo
        for _, row in df_origen.iterrows():
            if pd.notnull(row[lat_col]) and pd.notnull(row[lon_col]):
                folium.PolyLine(
                    locations=[(row[lat_col], row[lon_col]), destino],
                    color='blue',
                    weight=max(row[valor_col] / 100000, 1),
                    opacity=0.6
                ).add_to(m)

                # País de origen
                folium.CircleMarker(
                    location=(row[lat_col], row[lon_col]),
                    radius=max(row[valor_col] / 30000, 3),
                    popup=f"{row['Zona_Pais']}<br>Turistas: {int(row[valor_col])}",
                    color='red',
                    fill=True,
                    fill_color='red',
                    fill_opacity=0.7
                ).add_to(m)

        return m
