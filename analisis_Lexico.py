import pandas as pd
import tkinter as tk
from tkinter import filedialog
from collections import Counter
import re
import os

# --- FUNCIONES DE CARGA DE LÉXICOS ---
def cargar_lexico_afinn(ruta):
    df = pd.read_csv(ruta)
    return dict(zip(df['palabra'].str.lower(), df['puntuacion']))

def cargar_lexico_nrc(ruta):
    df = pd.read_csv(ruta)
    lexico = {}
    for _, row in df.iterrows():  # <-- Reparado
        palabra = row['palabra'].lower()
        sentimiento = row['sentimiento'].lower()
        if palabra not in lexico:
            lexico[palabra] = []
        lexico[palabra].append(sentimiento)
    return lexico

# --- TOKENIZADOR BÁSICO ---
def tokenizar(texto):
    return re.findall(r'\b\w+\b', str(texto).lower(), flags=re.UNICODE)

# --- ANÁLISIS AFINN ---
def puntaje_afinn(palabras, lexico_afinn):
    return sum(lexico_afinn.get(p, 0) for p in palabras)

# --- ANÁLISIS NRC ---
def contar_nrc(palabras, lexico_nrc):
    contador = Counter()
    for p in palabras:
        if p in lexico_nrc:
            for emocion in lexico_nrc[p]:
                contador[emocion] += 1
    return dict(contador)

# --- CARGAR ARCHIVO CSV CON INTERFAZ ---
def seleccionar_archivo():
    root = tk.Tk()
    root.withdraw()
    archivo = filedialog.askopenfilename(
        title="Selecciona el archivo CSV de entrada",
        filetypes=[("Archivos CSV", "*.csv")]
    )
    return archivo

# --- PROCESAMIENTO PRINCIPAL ---
def analizar_sentimientos():
    # Paso 1: seleccionar CSV
    archivo_entrada = seleccionar_archivo()
    if not archivo_entrada:
        print("No se seleccionó ningún archivo.")
        return

    df = pd.read_csv(archivo_entrada)

    # Paso 2: cargar léxicos
    lexico_afinn = cargar_lexico_afinn("lexico_afinn.csv")
    lexico_nrc = cargar_lexico_nrc("lexico_nrc.csv")

    # Contador global de palabras afinn encontradas
    contador_palabras_afinn = Counter()

    # Paso 3: columnas a analizar
    columnas = ['Comentario', 'Titulo_Video', 'Descripcion_Video', 'Tags' ]
    for col in columnas:
        afinn_scores = []
        nrc_emotions = []

        for texto in df[col].fillna(""):
            palabras = tokenizar(texto)

            # Contar ocurrencias de palabras AFINN encontradas
            for p in palabras:
                if p in lexico_afinn:
                    contador_palabras_afinn[p] += 1

            # Análisis de sentimiento
            afinn_scores.append(puntaje_afinn(palabras, lexico_afinn))
            resumen_nrc = contar_nrc(palabras, lexico_nrc)
            resumen_legible = ", ".join(f"{k}:{v}" for k, v in resumen_nrc.items())
            nrc_emotions.append(resumen_legible)

        df[f"{col}_afinn"] = afinn_scores
        df[f"{col}_nrc"] = nrc_emotions

    # Paso 4: guardar archivo principal
    base, ext = os.path.splitext(archivo_entrada)
    archivo_salida = f"{base}_sentimiento.csv"
    df.to_csv(archivo_salida, index=False, encoding='utf-8-sig')
    print(f"✅ Análisis completado. Archivo guardado como: {archivo_salida}")

    # Paso 5: exportar positivos y negativos encontrados
    palabras_positivas = {
        p: contador_palabras_afinn[p]
        for p in contador_palabras_afinn
        if lexico_afinn.get(p, 0) > 0
    }
    palabras_negativas = {
        p: contador_palabras_afinn[p]
        for p in contador_palabras_afinn
        if lexico_afinn.get(p, 0) < 0
    }

    # Guardar como CSV
    pd.DataFrame(palabras_positivas.items(), columns=["palabra", "frecuencia"])\
        .sort_values(by="frecuencia", ascending=False)\
        .to_csv("palabras_positivas.csv", index=False, encoding="utf-8-sig")

    pd.DataFrame(palabras_negativas.items(), columns=["palabra", "frecuencia"])\
        .sort_values(by="frecuencia", ascending=False)\
        .to_csv("palabras_negativas.csv", index=False, encoding="utf-8-sig")

    print("📄 Archivos adicionales guardados: palabras_positivas.csv y palabras_negativas.csv")

# Ejecutar
if __name__ == "__main__":
    analizar_sentimientos()
