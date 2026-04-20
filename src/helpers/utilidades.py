# src/helpers/utilidades.py

import pandas as pd
from pathlib import Path

class Utilidades:
    """
    Clase de utilidades para gestionar tareas comunes de transformación,
    combinación y soporte general en el proyecto.
    """

    def __init__(self, ruta_data: str = "data"):
        """
        Inicializa las rutas base del proyecto.
        """
        self.ruta_raw = Path(ruta_data) / "raw"
        self.ruta_processed = Path(ruta_data) / "processed"

    def cargar_csv(self, nombre_archivo: str, carpeta: str = "raw") -> pd.DataFrame:
        """
        Carga un archivo CSV desde la carpeta indicada ('raw' o 'processed').
        """
        carpeta_path = self.ruta_raw if carpeta == "raw" else self.ruta_processed
        ruta = carpeta_path / nombre_archivo

        if not ruta.exists():
            raise FileNotFoundError(f"❌ No se encontró el archivo: {ruta}")

        df = pd.read_csv(ruta)
        print(f"📂 Archivo cargado: {ruta.name} | Registros: {len(df)}")
        return df

    def transformar_clima(self, nombre_archivo_raw: str) -> pd.DataFrame:
        """
        Transpone y formatea el archivo de clima para que haya una columna por mes.
        """
        df_clima = self.cargar_csv(nombre_archivo_raw, carpeta="raw")

        if "time" not in df_clima.columns:
            raise ValueError("❌ El archivo de clima no contiene la columna 'time'.")

        # Convertir fechas
        df_clima["time"] = pd.to_datetime(df_clima["time"])
        df_clima["Mes_Anio"] = df_clima["time"].dt.strftime("%b-%y")

        # Agrupar por Mes_Anio (promedio mensual)
        df_mensual = (
            df_clima.groupby("Mes_Anio")[["temperature_2m_max", "temperature_2m_min", "precipitation_sum"]]
            .mean()
            .reset_index()
        )

        print(f"✅ Datos climáticos agrupados por mes: {df_mensual.shape}")

        # Transponer: variables en filas y meses como columnas
        df_transpuesto = df_mensual.set_index("Mes_Anio").T
        df_transpuesto.index.name = "variable"

        # Exportar
        ruta_transf = self.ruta_processed / "clima_costa_rica_datos_transformado.csv"
        df_transpuesto.to_csv(ruta_transf, encoding="utf-8-sig")
        print(f"💾 Archivo transformado y transpuesto guardado en: {ruta_transf}")

        return df_transpuesto

    def combinar_turismo_y_clima(self, nombre_turismo: str, nombre_clima_transformado: str) -> pd.DataFrame:
        """
        Combina el archivo de turismo mensual con el archivo de clima transpuesto.
        """
        df_turismo = self.cargar_csv(nombre_turismo, carpeta="processed")
        df_clima = self.cargar_csv(nombre_clima_transformado, carpeta="processed")

        # Convertir el clima al formato largo
        df_clima_long = df_clima.set_index("variable").T.reset_index().rename(columns={"index": "Mes_Anio"})

        if "Mes_Anio" in df_turismo.columns:
            df_comb = pd.merge(df_turismo, df_clima_long, on="Mes_Anio", how="left")
        else:
            print("⚠ El archivo de turismo no tiene columna 'Mes_Anio'; se concatenarán los datasets.")
            df_comb = pd.concat([df_turismo, df_clima_long], axis=1)

        ruta_comb = self.ruta_processed / "turismo_clima_combinado.csv"
        df_comb.to_csv(ruta_comb, index=False, encoding="utf-8-sig")
        print(f"✅ Archivo combinado turismo+clima guardado en: {ruta_comb}")

        return df_comb
