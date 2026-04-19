import pandas as pd
import os
import unicodedata


class GestorDatos:
    """
    Clase para gestión de archivos: carga, limpieza, combinación y exportación
    de datos relacionados con turismo (años o archivos individuales).
    """

    def __init__(self, ruta_base="../data"):
        self.ruta_raw = os.path.join(ruta_base, "raw")
        self.ruta_processed = os.path.join(ruta_base, "processed")
        os.makedirs(self.ruta_processed, exist_ok=True)

    # ----------------------------------------------------------
    # MÉTODOS DE CARGA Y LIMPIEZA
    # ----------------------------------------------------------
    def cargar_datos(self, nombre_archivo: str) -> pd.DataFrame:
        ruta = os.path.join(self.ruta_raw, nombre_archivo)

        if nombre_archivo.endswith(".csv"):
            df = pd.read_csv(ruta, encoding="utf-8", on_bad_lines="skip")
        elif nombre_archivo.endswith(".xlsx") or nombre_archivo.endswith(".xls"):
            df = pd.read_excel(ruta)
        elif nombre_archivo.endswith(".txt"):
            with open(ruta, "r", encoding="utf-8") as f:
                primera = f.readline()
            sep = ";" if ";" in primera else "\t" if "\t" in primera else ","
            df = pd.read_csv(ruta, sep=sep, encoding="utf-8", on_bad_lines="skip")
            ruta_csv = os.path.join(self.ruta_processed, os.path.splitext(nombre_archivo)[0] + ".csv")
            df.to_csv(ruta_csv, index=False, encoding="utf-8-sig")
            print(f"TXT convertido a CSV → {ruta_csv}")
        else:
            raise ValueError("Formato no soportado (solo CSV, Excel o TXT).")

        print(f"Archivo cargado: {nombre_archivo} ({df.shape[0]} filas, {df.shape[1]} columnas)")
        return df

    def limpiar_datos(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpia el DataFrame:
        - Reemplaza celdas vacías o con espacios en blanco por NaN.
        - Reemplaza NaN por 0.
        - Convierte columnas numéricas a tipo float o int.
        """
        # Reemplazar celdas vacías o solo con espacios por NaN
        df = df.replace(r'^\s*$', pd.NA, regex=True)

        # Reemplazar todos los NaN con 0
        df = df.fillna(0)

        # Intentar convertir columnas numéricas
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except Exception:
                pass

        print("Datos limpiados: valores nulos o vacíos reemplazados por 0.")
        return df

    # ----------------------------------------------------------
    # FUNCIONES INTERNAS
    # ----------------------------------------------------------
    def _normalizar_texto_simple(self, texto: str) -> str:
        """Convierte nombres en MAYÚSCULAS y sin tildes."""
        if not isinstance(texto, str):
            return texto
        texto = texto.strip().upper()
        texto = unicodedata.normalize("NFKD", texto).encode("ascii", errors="ignore").decode("utf-8")
        return texto

    def _convertir_mes_a_fecha(self, columnas, anio):
        """Convierte meses en formato MM-YYYY y totales con año."""
        mapa = {
            "Enero": "01", "Febrero": "02", "Marzo": "03", "Abril": "04", "Mayo": "05", "Junio": "06",
            "Julio": "07", "Agosto": "08", "Setiembre": "09", "Septiembre": "09", "Octubre": "10",
            "Noviembre": "11", "Diciembre": "12",
        }
        nuevas = {}
        for c in columnas:
            if c in mapa:
                nuevas[c] = f"{mapa[c]}-{anio}"
            elif "Total" in c:
                nuevas[c] = f"Total_{anio}"
        return nuevas

    # ----------------------------------------------------------
    # COMBINAR ARCHIVOS POR AÑO
    # ----------------------------------------------------------
    def combinar_datos_por_anio(self, archivo_2025: str, archivo_2026: str) -> pd.DataFrame:
        df2025 = self.limpiar_datos(self.cargar_datos(archivo_2025))
        df2026 = self.limpiar_datos(self.cargar_datos(archivo_2026))

        df2025["zona_norm"] = df2025["Zona_Pais"].astype(str).apply(self._normalizar_texto_simple)
        df2026["zona_norm"] = df2026["Zona_Pais"].astype(str).apply(self._normalizar_texto_simple)

        orden_original = df2025["zona_norm"].tolist()
        nombres_originales = df2025[["Zona_Pais", "zona_norm"]].copy()

        df2025.rename(columns=self._convertir_mes_a_fecha(
            [c for c in df2025.columns if c not in ["Zona_Pais", "zona_norm"]], 2025), inplace=True)
        df2026.rename(columns=self._convertir_mes_a_fecha(
            [c for c in df2026.columns if c not in ["Zona_Pais", "zona_norm"]], 2026), inplace=True)

        df = pd.merge(df2025.drop(columns=["Zona_Pais"]),
                      df2026.drop(columns=["Zona_Pais"]),
                      on="zona_norm", how="outer")

        df = pd.merge(df, nombres_originales, on="zona_norm", how="left")

        cols = ["Zona_Pais"] + [c for c in df.columns if c not in ["Zona_Pais", "zona_norm"]]
        df = df[cols]
        df.drop(columns=["zona_norm"], inplace=True, errors="ignore")

        df["Zona_Pais"] = pd.Categorical(df["Zona_Pais"], categories=nombres_originales["Zona_Pais"], ordered=True)
        df.sort_values("Zona_Pais", inplace=True)

        if "Total_2025" in df.columns:
            df["Total_2025"] = pd.to_numeric(df["Total_2025"], errors="coerce").fillna(0)
        if "Total_2026" in df.columns:
            df["Total_2026"] = pd.to_numeric(df["Total_2026"], errors="coerce").fillna(0)
        if "Total_2025" in df.columns and "Total_2026" in df.columns:
            df["Total"] = df["Total_2025"] + df["Total_2026"]

        order = [
            "Zona_Pais", "01-2025", "02-2025", "03-2025", "04-2025", "05-2025", "06-2025",
            "07-2025", "08-2025", "09-2025", "10-2025", "11-2025", "12-2025",
            "01-2026", "02-2026", "Total_2025", "Total_2026", "Total"
        ]
        df = df[[c for c in order if c in df.columns]]

        print("Archivos 2025 y 2026 combinados correctamente.")
        return df

    # ----------------------------------------------------------
    # NUEVO: PROCESAR ARCHIVOS INDIVIDUALES
    # ----------------------------------------------------------
    def procesar_archivo_individual(self, nombre_archivo: str, nombre_salida: str = None):
        """
        Procesa un archivo individual:
        - Elimina la columna 'id'.
        - Mueve la fila 'Total' al final.
        - Reemplaza valores vacíos o NA por 0.
        - Limpia nombres de columnas y zonas.
        - Renombra columnas tipo 'Ano2017' → '2017'.
        """

        # Cargar el archivo
        df = self.cargar_datos(nombre_archivo)
        df = self.limpiar_datos(df)

        # Eliminar la columna 'id' si existe
        if "id" in df.columns:
            df.drop(columns=["id"], inplace=True)
            print("📤 Columna 'id' eliminada.")

        # Normalizar columna de regiones
        if "Zona_Pais" in df.columns:
            df["Zona_Pais"] = df["Zona_Pais"].astype(str).apply(self._normalizar_texto_simple)

        # Reemplazar vacíos por 0 y convertir tipos
        df.replace(r'^\s*$', pd.NA, regex=True, inplace=True)
        df.fillna(0, inplace=True)
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass

        # Mover la fila 'Total' al final
        if "Zona_Pais" in df.columns:
            mask_total = df["Zona_Pais"].str.contains("TOTAL", case=False, na=False)
            df_total = df[mask_total]
            df = pd.concat([df[~mask_total], df_total], axis=0)
            print("📦 Fila 'Total' movida al final.")

        # Limpiar nombres de columnas y eliminar tildes
        nuevos_nombres = {}
        for col in df.columns:
            base = (
                unicodedata.normalize("NFKD", col)
                .encode("ascii", errors="ignore")
                .decode("utf-8")
                .strip()
                .replace(" ", "_")
                .replace("-", "_")
            )

            # Nueva regla: si comienza con "Ano" seguido de números → quitar "Ano"
            if base.lower().startswith("ano") and base[3:].isdigit():
                base = base[3:]  # quedará solo el año, ej. "2017"

            nuevos_nombres[col] = base

        df.rename(columns=nuevos_nombres, inplace=True)

        # Exportar archivo procesado
        if not nombre_salida:
            nombre_salida = os.path.splitext(nombre_archivo)[0] + "_procesado.csv"

        self.exportar_datos(df, nombre_salida)

        print(f"✅ Archivo procesado y exportado como: {nombre_salida}")
        print(f"Filas: {df.shape[0]}, Columnas: {df.shape[1]}")
        print(f"Columnas finales: {df.columns.tolist()}")
        return df

        # Exportar archivo procesado
        if not nombre_salida:
            nombre_salida = os.path.splitext(nombre_archivo)[0] + "_procesado.csv"

        self.exportar_datos(df, nombre_salida)

        print(f"✅ Archivo procesado y exportado como: {nombre_salida}")
        print(f"Filas: {df.shape[0]}, Columnas: {df.shape[1]}")
        return df

        # ----------------------------------------------------------
    def exportar_datos(self, df: pd.DataFrame, nombre_salida: str):
        ruta_salida = os.path.join(self.ruta_processed, nombre_salida)
        df.to_csv(ruta_salida, index=False, encoding="utf-8-sig")
        print(f"Archivo exportado correctamente en: {ruta_salida}")
