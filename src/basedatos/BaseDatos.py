# src/basedatos/BaseDatos.py

import pyodbc
import pandas as pd
from pathlib import Path


class BaseDatos:
    def __init__(self, server, database, username, password, driver="ODBC Driver 17 for SQL Server"):
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.driver = driver
        self.conn = None

    def conectar(self):
        try:
            conn_str = (
                f"DRIVER={{{self.driver}}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"UID={self.username};"
                f"PWD={self.password};"
            )
            self.conn = pyodbc.connect(conn_str)
            print("✅ Conexión exitosa a la base de datos.")
        except Exception as e:
            print(f"❌ Error al conectar a la base de datos: {e}")

    def ejecutar_consulta(self, query):
        """Ejecuta una consulta SQL y devuelve un DataFrame."""
        if not self.conn:
            self.conectar()

        try:
            df = pd.read_sql(query, self.conn)
            return df
        except Exception as e:
            print(f"❌ Error ejecutando consulta: {e}")
            return pd.DataFrame()

    def exportar_csv(self, df, nombre_archivo, encoding="utf-8-sig"):
        """Exporta el DataFrame a una ruta fija en tu máquina local"""
        ruta_raw = Path(r"C:\Proyecto_Análisis_y_Predicción_del_Turismo_en_Costa_Rica\data\raw")

        ruta_raw.mkdir(parents=True, exist_ok=True)
        file_path = ruta_raw / f"{nombre_archivo}.csv"

        df.to_csv(file_path, index=False, encoding=encoding)
        print(f"✅ Archivo CSV exportado correctamente en: {file_path}")
