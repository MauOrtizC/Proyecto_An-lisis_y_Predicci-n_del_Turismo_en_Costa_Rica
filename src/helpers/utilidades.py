import pandas as pd
from pathlib import Path


class Utilidades:
    """
    Versión segura: genera las filas del clima en el mismo orden de meses
    del archivo de turismo; los valores nunca quedan nulos por desalineación.
    """

    def __init__(self, ruta_data: str = "data"):
        self.ruta_raw = Path(ruta_data) / "raw"
        self.ruta_processed = Path(ruta_data) / "processed"
        self.ruta_processed.mkdir(parents=True, exist_ok=True)

    def cargar_csv(self, nombre_archivo: str, carpeta: str = "raw") -> pd.DataFrame:
        carpeta = self.ruta_raw if carpeta == "raw" else self.ruta_processed
        ruta = carpeta / nombre_archivo
        if not ruta.exists():
            raise FileNotFoundError(f"No se encontró {ruta}")
        return pd.read_csv(ruta)

    # ---------- transformar_clima ----------
    def transformar_clima(self, nombre_archivo_raw: str) -> pd.DataFrame:
        """
        Devuelve el clima en formato:
        variable, Jan-25, Feb-25, ...
        usando los datos del archivo bruto.
        """
        df = self.cargar_csv(nombre_archivo_raw, carpeta="raw")

        # convertir YYYY-MM a formato de texto de turismo
        df["Mes"] = pd.to_datetime(df["time"], format="%Y-%m").dt.strftime("%b-%y")

        # armar tres filas manualmente
        vars_clima = ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"]
        salida = pd.DataFrame({"variable": vars_clima})
        for _, fila in df.iterrows():
            mes = fila["Mes"]
            for v in vars_clima:
                salida.loc[salida["variable"] == v, mes] = fila[v]

        ruta = self.ruta_processed / "clima_costa_rica_datos_transformado.csv"
        salida.to_csv(ruta, index=False, encoding="utf-8-sig")
        print(f"💾 Clima transformado guardado: {ruta}")
        return salida

    # ---------- combinar_turismo_y_clima ----------
    def combinar_turismo_y_clima(self, nombre_turismo: str, nombre_clima_transformado: str) -> None:
        """
        🚨 Método FORZADO: concatena el archivo de clima debajo del turismo,
        pero omitiendo la primera línea de encabezados del clima.
        """
        ruta_turismo = self.ruta_processed / nombre_turismo
        ruta_clima = self.ruta_processed / nombre_clima_transformado
        ruta_out = self.ruta_processed / "turismo_clima_combinado.csv"

        if not ruta_turismo.exists() or not ruta_clima.exists():
            raise FileNotFoundError("❌ Confirma que ambos archivos existen en data/processed/")

        # Leer el archivo de turismo completo
        with open(ruta_turismo, "r", encoding="utf-8-sig") as f:
            turismo_text = f.read().strip()

        # Leer el archivo de clima y omitir su primera línea (encabezado)
        with open(ruta_clima, "r", encoding="utf-8-sig") as f:
            clima_lineas = f.readlines()
        # Aqui quitamos la primera linea
        clima_sin_header = "".join(clima_lineas[1:]).strip()

        # Unir turismo + clima (sin encabezado)
        combinado_texto = turismo_text + "\n" + clima_sin_header

        # Guardar el resultado
        with open(ruta_out, "w", encoding="utf-8-sig", newline="") as f:
            f.write(combinado_texto)

        print(f"✅ Archivo combinado (sin encabezados del clima) guardado correctamente en: {ruta_out}")
