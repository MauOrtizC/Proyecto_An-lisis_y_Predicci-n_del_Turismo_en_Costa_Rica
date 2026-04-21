import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error
import matplotlib.pyplot as plt
import seaborn as sns


class ModeloML:
    """
    Clase ModeloML
    ------------------------
    Carga, transforma, entrena modelos y simula escenarios climáticos
    para la predicción de turismo mensual.
    """

    def __init__(self, ruta_archivo='../data/processed/turismo_clima_combinado.csv'):
        self.ruta_archivo = ruta_archivo
        self.df = None
        self.df_modelo = None
        self.modelos = {}
        self.scaler = StandardScaler()
        self.rf = None
        self.resultados = None

    # ----------------------  CARGA DE DATOS  ----------------------
    def cargar_datos(self):
        try:
            df = pd.read_csv(self.ruta_archivo, sep=None, engine='python', skip_blank_lines=True)
        except Exception:
            df = pd.read_csv(self.ruta_archivo, sep=',', skip_blank_lines=True)

        if 'Zona_Pais' not in df.columns:
            raise KeyError("El archivo no contiene la columna 'Zona_Pais'")

        df = df[df['Zona_Pais'].notna() & (df['Zona_Pais'] != '0')]
        self.df = df.reset_index(drop=True)
        print(f"✅ Datos cargados correctamente: {df.shape}")
        return self.df

    # ----------------------  TRANSFORMACIÓN  ----------------------
    def transformar_datos(self):
        if self.df is None:
            raise ValueError("Primero ejecute cargar_datos()")

        df_clima = self.df[self.df['Zona_Pais'].isin(['temperature_2m_max', 'temperature_2m_min', 'precipitation_sum'])]
        df_turismo = self.df[~self.df['Zona_Pais'].isin(['temperature_2m_max', 'temperature_2m_min', 'precipitation_sum'])]

        df_turismo_long = df_turismo.melt(id_vars='Zona_Pais', var_name='Mes', value_name='Turistas')
        df_clima_long = df_clima.melt(id_vars='Zona_Pais', var_name='Mes', value_name='Valor')
        df_clima_pivot = df_clima_long.pivot_table(index='Mes', columns='Zona_Pais', values='Valor').reset_index()
        df_merged = df_turismo_long.merge(df_clima_pivot, on='Mes', how='left')

        df_merged = df_merged[df_merged['Mes'].str.match(r'^\d{2}-\d{4}$', na=False)]
        df_merged['Año'] = df_merged['Mes'].str[-4:].astype(int)
        df_merged['Mes_Num'] = df_merged['Mes'].str[:2].astype(int)

        features = ['Zona_Pais', 'Mes_Num', 'Año', 'temperature_2m_max', 'temperature_2m_min', 'precipitation_sum']
        df_modelo = df_merged[features + ['Turistas']].copy()
        df_modelo = pd.get_dummies(df_modelo, columns=['Zona_Pais'], drop_first=True)

        self.df_modelo = df_modelo
        print(f"✅ Transformación lista: {df_modelo.shape}")
        return df_modelo

    # ----------------------  ENTRENAMIENTO  ----------------------
    def entrenar_modelos(self, test_size=0.2, random_state=42):
        if self.df_modelo is None:
            raise ValueError("Primero ejecute transformar_datos()")

        X = self.df_modelo.drop('Turistas', axis=1)
        y = self.df_modelo['Turistas']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        reg = LinearRegression().fit(X_train_scaled, y_train)
        knn = KNeighborsRegressor(n_neighbors=5).fit(X_train_scaled, y_train)
        rf = RandomForestRegressor(n_estimators=100, random_state=random_state).fit(X_train, y_train)

        self.rf = rf
        self.modelos = {'reg': reg, 'knn': knn, 'rf': rf}

        cv_lr = cross_val_score(reg, X_train_scaled, y_train, cv=5)
        cv_knn = cross_val_score(knn, X_train_scaled, y_train, cv=5)
        cv_rf = cross_val_score(rf, X_train, y_train, cv=5)

        resultados = pd.DataFrame({
            'Modelo': ['Regresión Lineal', 'KNN', 'Random Forest'],
            'R2_Test': [
                reg.score(X_test_scaled, y_test),
                knn.score(X_test_scaled, y_test),
                rf.score(X_test, y_test)
            ],
            'RMSE_Test': [
                np.sqrt(mean_squared_error(y_test, reg.predict(X_test_scaled))),
                np.sqrt(mean_squared_error(y_test, knn.predict(X_test_scaled))),
                np.sqrt(mean_squared_error(y_test, rf.predict(X_test)))
            ],
            'CV_Promedio': [np.mean(cv_lr), np.mean(cv_knn), np.mean(cv_rf)]
        })

        self.resultados = resultados
        print("✅ Modelos entrenados y evaluados.")
        return resultados

    # ----------------------  GUARDAR MODELO  ----------------------
    def guardar_modelo(self, nombre='modelo_turismo_RF.pkl'):
        if self.rf is None:
            raise ValueError("Primero entrene los modelos antes de guardar.")
        ruta = os.path.join('../models', nombre)
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        joblib.dump(self.rf, ruta)
        print(f"💾 Modelo RandomForest guardado en: {ruta}")

    # ----------------------  SIMULAR FUTURO  ----------------------
    def simular_futuro(self, año=2026, mes_inicio=3, mes_fin=12, clima_scenario='normal'):
        if self.rf is None:
            raise ValueError("Debe entrenar el modelo antes de simular escenario futuro.")
        zonas = [z for z in self.df['Zona_Pais'].unique() if not z.startswith('temp')]
        clima_mean = self.df_modelo[['temperature_2m_max', 'temperature_2m_min', 'precipitation_sum']].mean()
        factores = {
            'normal': (1.0, 0.0),
            'lluvias_altas': (2.0, 0.0),
            'sequía': (0.5, 0.0),
            'calor_extremo': (1.0, 5.0)
        }
        f_precip, f_temp = factores.get(clima_scenario, (1.0, 0.0))
        meses_futuros = [f"{str(m).zfill(2)}-{año}" for m in range(mes_inicio, mes_fin + 1)]

        df_futuro = []
        for zona in zonas:
            for mes in meses_futuros:
                df_futuro.append({
                    'Zona_Pais': zona,
                    'Mes': mes,
                    'Año': año,
                    'Mes_Num': int(mes[:2]),
                    'temperature_2m_max': clima_mean['temperature_2m_max'] + np.random.uniform(3, 6) + f_temp,
                    'temperature_2m_min': clima_mean['temperature_2m_min'] + np.random.uniform(1, 3),
                    'precipitation_sum': clima_mean['precipitation_sum'] * np.random.uniform(1.5, 2.5) * f_precip
                })

        df_futuro = pd.DataFrame(df_futuro)
        df_futuro = pd.get_dummies(df_futuro, columns=['Zona_Pais'], drop_first=True)
        cols_modelo = self.df_modelo.drop('Turistas', axis=1).columns
        for col in cols_modelo:
            if col not in df_futuro.columns:
                df_futuro[col] = 0
        df_futuro = df_futuro[cols_modelo]

        pred = self.rf.predict(df_futuro)
        df_result = pd.DataFrame({'Mes': meses_futuros * len(zonas), 'Pred_Turistas': pred})
        df_result['Mes_Date'] = pd.to_datetime(df_result['Mes'], format='%m-%Y')

        print(f"🔮 Escenario '{clima_scenario}' simulado exitosamente ({mes_inicio}-{mes_fin} {año}).")
        return df_result

    # ----------------------  GRAFICAR RESULTADOS ----------------------
    def graficar_prediccion(self, df_pred, escenario):
        sns.set(style="whitegrid")
        plt.figure(figsize=(10,6))
        sns.lineplot(data=df_pred, x='Mes_Date', y='Pred_Turistas', marker='o')
        plt.title(f"Predicción de Turismo - Escenario: {escenario}")
        plt.ylabel("Turistas estimados")
        plt.xlabel("Mes")
        plt.xticks(rotation=45)
        plt.show()
