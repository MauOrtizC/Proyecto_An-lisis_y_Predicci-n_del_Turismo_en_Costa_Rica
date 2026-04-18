import pandas as pd
import os
import unicodedata


class GestorDatos:
    """
    Clase para gestión de archivos: carga, limpieza, combinación y exportación
    de datos relacionados con turismo (2025–2026 o archivos individuales).
    """

    def __init__(self, ruta_base="../data"):
        self.ruta_raw = os.path.join(ruta_base, "raw")
        self.ruta_processed = os.path.join(ruta_base, "processed")
        os.makedirs(self.ruta_processed, exist_ok=True)

    # ----------------------------------------------------------
    # MÉTODOS PRINCIPALES DE CARGA Y LIMPIEZA
    # ----------------------------------------------------------
    def cargar_datos(self, nombre_archivo: str) -> pd.DataFrame:
        ruta = os.path.join(self.ruta_raw, nombre_archivo)

        if nombre_archivo.endswith(".csv"):
            df = pd.read_csv(ruta, encoding="utf-8", on_bad_lines="skip")
        elif nombre_archivo.endswith(".xlsx") or nombre_archivo.endswith(".xls"):
            df = pd.read_excel(ruta)
        elif nombre_archivo.endswith(".txt"):
            # Detección automática del separador
            with open(ruta, "r", encoding="utf-8") as f:
                primera_linea = f.readline()
            sep = ";" if ";" in primera_linea else "\t" if "\t" in primera_linea else ","
            df = pd.read_csv(ruta, sep=sep, encoding="utf-8", on_bad_lines="skip")
            # Convertir automáticamente a CSV
            ruta_csv = os.path.join(
                self.ruta_processed, os.path.splitext(nombre_archivo)[0] + ".csv"
            )
            df.to_csv(ruta_csv, index=False, encoding="utf-8-sig")
            print(f"TXT convertido a CSV → {ruta_csv}")
        else:
            raise ValueError("Formato no soportado (solo CSV, Excel o TXT).")

        print(
            f"Archivo cargado: {nombre_archivo} ({df.shape[0]} filas, {df.shape[1]} columnas)"
        )
        return df

    def limpiar_datos(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reemplaza valores nulos por 0."""
        df_limpio = df.fillna(0)
        print("Datos limpiados: valores nulos reemplazados por 0.")
        return df_limpio

    # ----------------------------------------------------------
    # MÉTODOS AUXILIARES INTERNOS
    # ----------------------------------------------------------
    def _normalizar_texto(self, texto: str) -> str:
        """Elimina tildes y convierte a minúsculas para comparación."""
        if not isinstance(texto, str):
            return texto
        texto = texto.strip().lower()
        texto = unicodedata.normalize("NFKD", texto).encode("ascii", errors="ignore").decode("utf-8")
        return texto

    def _convertir_mes_a_fecha(self, columnas, anio):
        """Convierte nombres de meses y totales en formato MM-YYYY."""
        mapa_meses = {
            "Enero": "01", "Febrero": "02", "Marzo": "03", "Abril": "04",
            "Mayo": "05", "Junio": "06", "Julio": "07", "Agosto": "08",
            "Setiembre": "09", "Septiembre": "09", "Octubre": "10",
            "Noviembre": "11", "Diciembre": "12",
        }

        nuevas_columnas = {}
        for col in columnas:
            if col in mapa_meses:
                nuevas_columnas[col] = f"{mapa_meses[col]}-{anio}"
            elif "Total" in col:
                nuevas_columnas[col] = f"Total_{anio}"
        return nuevas_columnas

    # ----------------------------------------------------------
    # MÉTODO PARA COMBINAR ARCHIVOS 2025 - 2026
    # ----------------------------------------------------------
    def combinar_datos_por_anio(
        self, archivo_2025: str, archivo_2026: str
    ) -> pd.DataFrame:
        """Combina los archivos 2025 y 2026 manteniendo nombres originales y orden correcto."""
        df2025 = self.limpiar_datos(self.cargar_datos(archivo_2025))
        df2026 = self.limpiar_datos(self.cargar_datos(archivo_2026))

        # generar columna normalizada en ambos
        df2025["zona_norm"] = df2025["Zona_Pais"].astype(str).apply(self._normalizar_texto)
        df2026["zona_norm"] = df2026["Zona_Pais"].astype(str).apply(self._normalizar_texto)

        # mantener el orden original basado en archivo 2025
        orden_original = df2025["zona_norm"].tolist()
        nombres_originales = df2025[["Zona_Pais", "zona_norm"]].copy()

        # renombrar columnas con formato MM-YYYY y Totales
        df2025.rename(
            columns=self._convertir_mes_a_fecha(
                [c for c in df2025.columns if c not in ["Zona_Pais", "zona_norm"]], 2025
            ),
            inplace=True,
        )
        df2026.rename(
            columns=self._convertir_mes_a_fecha(
                [c for c in df2026.columns if c not in ["Zona_Pais", "zona_norm"]], 2026
            ),
            inplace=True,
        )

        # combinar usando columna normalizada
        df = pd.merge(
            df2025.drop(columns=["Zona_Pais"]),
            df2026.drop(columns=["Zona_Pais"]),
            on="zona_norm",
            how="outer",
        )

        # restaurar nombres originales de Zona_Pais
        df = pd.merge(df, nombres_originales, on="zona_norm", how="left")

        # mover Zona_Pais al frente y eliminar zona_norm (si existe)
        cols = ["Zona_Pais"] + [
            c for c in df.columns if c != "Zona_Pais" and c != "zona_norm"
        ]
        df = df[cols]
        df.drop(columns=["zona_norm"], inplace=True, errors="ignore")

        # mantener el orden original
        df["Zona_Pais"] = pd.Categorical(
            df["Zona_Pais"], categories=nombres_originales["Zona_Pais"], ordered=True
        )
        df.sort_values("Zona_Pais", inplace=True)

        # convertir totales a numéricos
        if "Total_2025" in df.columns:
            df["Total_2025"] = pd.to_numeric(df["Total_2025"], errors="coerce").fillna(0)
        if "Total_2026" in df.columns:
            df["Total_2026"] = pd.to_numeric(df["Total_2026"], errors="coerce").fillna(0)

        # calcular columna Total (suma de ambos años)
        if "Total_2025" in df.columns and "Total_2026" in df.columns:
            df["Total"] = df["Total_2025"] + df["Total_2026"]

        # definir orden final de columnas
        columnas_ordenadas = [
            "Zona_Pais",
            "01-2025", "02-2025", "03-2025", "04-2025", "05-2025", "06-2025",
            "07-2025", "08-2025", "09-2025", "10-2025", "11-2025", "12-2025",
            "01-2026", "02-2026",
            "Total_2025", "Total_2026", "Total",
        ]
        columnas_finales = [c for c in columnas_ordenadas if c in df.columns]
        df = df[columnas_finales]

        print(
            "Archivos combinados correctamente con nombres restaurados y totales calculados."
        )
        return df

    # ----------------------------------------------------------
    # NUEVO MÉTODO - PROCESAR ARCHIVOS INDIVIDUALES
    # ----------------------------------------------------------
    def procesar_archivo_individual(self, nombre_archivo: str, nombre_salida: str = None):
        """
        Procesa un archivo individual: carga, limpia encabezados y exporta al directorio processed.
        Puede aplicarse a archivos históricos o agregados.
        """
        df = self.cargar_datos(nombre_archivo)
        df = self.limpiar_datos(df)

        # Normalizar encabezados (sin tildes y con guiones bajos)
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
            nuevos_nombres[col] = base
        df.rename(columns=nuevos_nombres, inplace=True)

        # Definir nombre de salida si no se especifica
        if not nombre_salida:
            nombre_salida = os.path.splitext(nombre_archivo)[0] + "_procesado.csv"

        self.exportar_datos(df, nombre_salida)
        print(f"Archivo individual procesado y exportado como: {nombre_salida}")
        return df

    # ----------------------------------------------------------
    # MÉTODO FINAL - EXPORTAR
    # ----------------------------------------------------------
    def exportar_datos(self, df: pd.DataFrame, nombre_salida: str):
        """Exporta un DataFrame al directorio processed en formato UTF-8-SIG."""
        ruta_salida = os.path.join(self.ruta_processed, nombre_salida)
        df.to_csv(ruta_salida, index=False, encoding="utf-8-sig")
        print(f"Archivo exportado correctamente en: {ruta_salida}")
