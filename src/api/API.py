# src/api/API.py

import requests
import pandas as pd
from pathlib import Path

class ClienteAPI:
    """
    Clase para conectarse a la API de Open‑Meteo y descargar datos climatológicos históricos.
    Permite obtener datos diarios y convertirlos a valores mensuales.
    """

    def __init__(self, base_url="https://archive-api.open-meteo.com/v1/archive"):
        self.base_url = base_url

    # ---------------------------------------------------------------
    # MÉTODO PRINCIPAL: OBTENER DATOS CLIMÁTICOS DIARIOS
    # ---------------------------------------------------------------
    def obtener_datos_climaticos_diarios(
        self, lat, lon, start_date, end_date,
        variables=None, timezone="America/Costa_Rica"
    ):
        """
        Descarga los registros DIARIOS de la API (no horarios).
        Ejemplo de variables: temperature_2m_max, temperature_2m_min, precipitation_sum.
        """
        if variables is None:
            variables = ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"]

        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "daily": ",".join(variables),
            "timezone": timezone
        }

        print(f"🌤 Descargando datos DIARIOS desde {start_date} hasta {end_date}...")
        response = requests.get(self.base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data["daily"])

            # Convertir columna 'time' a datetime
            if "time" in df.columns:
                df["time"] = pd.to_datetime(df["time"])
                df.set_index("time", inplace=True)

            print(f"✅ Datos DIARIOS descargados correctamente. ({df.shape[0]} registros, {df.shape[1]} columnas)")
            return df
        else:
            print(f"❌ Error en la solicitud ({response.status_code}): {response.text}")
            return pd.DataFrame()

    # ---------------------------------------------------------------
    # MÉTODO PARA EXPORTAR A CSV
    # ---------------------------------------------------------------
    def guardar_csv(self, df, nombre_archivo):
        """
        Guarda el DataFrame en la carpeta data/raw/ con codificación UTF‑8‑sig.
        """
        base_path = Path(__file__).resolve().parents[2] / "data" / "raw"
        base_path.mkdir(parents=True, exist_ok=True)
        file_path = base_path / f"{nombre_archivo}.csv"
        df.to_csv(file_path, encoding="utf-8-sig")
        print(f"💾 Datos guardados en: {file_path}")

    # ---------------------------------------------------------------
    # MÉTODO PARA CONVERTIR DE DIARIO A MENSUAL
    # ---------------------------------------------------------------
    def convertir_a_mensual(self, df):
        """
        Convierte un DataFrame diario a valores mensuales:
        - Promedia temperaturas, nubosidad, etc.
        - Suma variables acumulativas como precipitación total.
        """
        if df.empty:
            print("⚠️ El DataFrame está vacío. No se puede convertir.")
            return df

        df_mensual = pd.DataFrame()

        for col in df.columns:
            if any(keyword in col.lower() for keyword in ["precip", "sum", "total"]):
                # Sumar si es una variable acumulativa
                df_mensual[col] = df[col].resample("ME").sum()
            else:
                # Promediar las demás variables
                df_mensual[col] = df[col].resample("ME").mean()

        # Índice en formato YYYY‑MM
        df_mensual.index = df_mensual.index.strftime("%Y-%m")
        print(f"📆 Datos convertidos a frecuencia MENSUAL. ({df_mensual.shape[0]} meses)")
        return df_mensual
