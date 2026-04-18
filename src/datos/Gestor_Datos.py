import pandas as pd
import os

class GestorDatos:
    """
    Clase para gestión de archivos: carga, limpieza, combinación y exportación
    de datos relacionados con turismo.
    """

    def __init__(self, ruta_base="../data"):
        self.ruta_raw = os.path.join(ruta_base, "raw")
        self.ruta_processed = os.path.join(ruta_base, "processed")
        os.makedirs(self.ruta_processed, exist_ok=True)

    def cargar_datos(self, nombre_archivo: str) -> pd.DataFrame:
        ruta = os.path.join(self.ruta_raw, nombre_archivo)

        if nombre_archivo.endswith(".csv"):
            df = pd.read_csv(ruta)
        elif nombre_archivo.endswith(".xlsx") or nombre_archivo.endswith(".xls"):
            df = pd.read_excel(ruta)
        elif nombre_archivo.endswith(".txt"):
            # Detección automática del separador
            with open(ruta, "r", encoding="utf-8") as f:
                primera_linea = f.readline()
            sep = ";" if ";" in primera_linea else "\t" if "\t" in primera_linea else ","
            df = pd.read_csv(ruta, sep=sep)
            ruta_csv = os.path.join(self.ruta_processed, os.path.splitext(nombre_archivo)[0] + ".csv")
            df.to_csv(ruta_csv, index=False)
            print(f"📝 TXT convertido a CSV → {ruta_csv}")
        else:
            raise ValueError("Formato no soportado (solo CSV, Excel o TXT).")

        print(f"✅ Archivo cargado: {nombre_archivo} ({df.shape[0]} filas, {df.shape[1]} columnas)")
        return df

    def limpiar_datos(self, df: pd.DataFrame) -> pd.DataFrame:
        df_limpio = df.fillna(0)
        print("🧹 Datos limpiados: valores nulos reemplazados por 0.")
        return df_limpio

    def _convertir_mes_a_fecha(self, columnas, anio):
        """Convierte nombres de meses en formato texto a MM-YYYY."""
        mapa_meses = {
            "Enero": "01",
            "Febrero": "02",
            "Marzo": "03",
            "Abril": "04",
            "Mayo": "05",
            "Junio": "06",
            "Julio": "07",
            "Agosto": "08",
            "Setiembre": "09",
            "Septiembre": "09",  # por si el archivo usa esta ortografía
            "Octubre": "10",
            "Noviembre": "11",
            "Diciembre": "12"
        }

        nuevas_columnas = {}
        for col in columnas:
            if col in mapa_meses:
                nuevas_columnas[col] = f"{mapa_meses[col]}-{anio}"
            elif "Total" in col:
                nuevas_columnas[col] = f"{col}{anio}"
        return nuevas_columnas

    def combinar_datos_por_anio(self, archivo_2025: str, archivo_2026: str) -> pd.DataFrame:
        # Cargar y limpiar
        df2025 = self.limpiar_datos(self.cargar_datos(archivo_2025))
        df2026 = self.limpiar_datos(self.cargar_datos(archivo_2026))

        # Convertir las columnas del 2025 a formato fecha
        columnas_mes_2025 = [c for c in df2025.columns if c != "Zona_Pais"]
        renames_2025 = self._convertir_mes_a_fecha(columnas_mes_2025, 2025)
        df2025 = df2025.rename(columns=renames_2025)

        # Convertir las columnas del 2026 a formato fecha
        columnas_mes_2026 = [c for c in df2026.columns if c != "Zona_Pais"]
        renames_2026 = self._convertir_mes_a_fecha(columnas_mes_2026, 2026)
        df2026 = df2026.rename(columns=renames_2026)

        # Combinar ambas tablas
        df_combinado = pd.merge(df2025, df2026, on="Zona_Pais", how="outer")

        print("🔗 Archivos 2025 y 2026 combinados correctamente con formato de fecha (MM-YYYY).")
        return df_combinado

    def exportar_datos(self, df: pd.DataFrame, nombre_salida: str):
        ruta_salida = os.path.join(self.ruta_processed, nombre_salida)
        df.to_csv(ruta_salida, index=False)
        print(f"📁 Archivo exportado correctamente en: {ruta_salida}")
