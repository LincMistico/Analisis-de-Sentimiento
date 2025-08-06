import pandas as pd
from textblob import TextBlob
from googletrans import Translator
from tkinter import Tk, filedialog
import os

# Inicializa el traductor
translator = Translator()

def traducir_y_analizar(texto):
    try:
        traduccion = translator.translate(texto, src='es', dest='en').text
        blob = TextBlob(traduccion)
        return blob.sentiment.polarity, blob.sentiment.subjectivity
    except Exception as e:
        print(f"Error al analizar texto: {e}")
        return None, None

def analizar_columna(df, columna):
    polaridades = []
    subjetividades = []
    for texto in df[columna]:
        if pd.isna(texto):
            polaridades.append(None)
            subjetividades.append(None)
        else:
            pol, sub = traducir_y_analizar(str(texto))
            polaridades.append(pol)
            subjetividades.append(sub)
    df[f'{columna}_Polaridad'] = polaridades
    df[f'{columna}_Subjetividad'] = subjetividades
    return df

def seleccionar_archivo_csv():
    root = Tk()
    root.withdraw()
    archivo = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    return archivo

def guardar_csv(df, ruta_original):
    nombre, ext = os.path.splitext(ruta_original)
    nuevo_nombre = f"{nombre}_analizado.csv"
    df.to_csv(nuevo_nombre, index=False)
    print(f"\n✅ Archivo guardado como: {nuevo_nombre}")

def main():
    ruta_csv = seleccionar_archivo_csv()
    if not ruta_csv:
        print("No se seleccionó ningún archivo.")
        return
    
    df = pd.read_csv(ruta_csv)

    columnas_a_analizar = []
    for col in ['Comentario', 'Título del video', 'Descripción']:
        if col in df.columns:
            columnas_a_analizar.append(col)
        else:
            print(f"⚠️  Columna no encontrada en el CSV: {col}")

    if not columnas_a_analizar:
        print("❌ No hay columnas válidas para analizar.")
        return

    for col in columnas_a_analizar:
        print(f"🔍 Analizando columna: {col}")
        df = analizar_columna(df, col)

    guardar_csv(df, ruta_csv)

if __name__ == "__main__":
    main()
