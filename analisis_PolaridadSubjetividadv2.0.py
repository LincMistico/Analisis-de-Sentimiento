import pandas as pd
from textblob import TextBlob
from googletrans import Translator
from tkinter import Tk, filedialog
import os
import time

# Inicializa el traductor
translator = Translator()

def traducir_y_analizar(texto):
    try:
        traduccion = translator.translate(texto, src='es', dest='en').text
        blob = TextBlob(traduccion)
        return blob.sentiment.polarity, blob.sentiment.subjectivity
    except Exception as e:
        print(f"\nError al analizar texto: {e}")
        return None, None

def analizar_columna(df, columna, ruta_original):
    polaridades = []
    subjetividades = []
    total_comentarios = len(df[columna])
    procesados = 0
    inicio_tiempo = time.time()
    nombre_archivo_final = f"{os.path.splitext(ruta_original)[0]}_polarizado.csv"
    
    print(f"\n🔍 Analizando columna: {columna}")
    print(f"📊 Total de comentarios a procesar: {total_comentarios:,}")
    print(f"💾 Archivo de salida: {nombre_archivo_final}\n")
    
    for i, texto in enumerate(df[columna]):
        if pd.isna(texto):
            polaridades.append(None)
            subjetividades.append(None)
        else:
            pol, sub = traducir_y_analizar(str(texto))
            polaridades.append(pol)
            subjetividades.append(sub)
        
        procesados = i + 1
        
        # Mostrar progreso cada 100 comentarios o en el último
        if procesados % 100 == 0 or procesados == total_comentarios:
            porcentaje = (procesados / total_comentarios) * 100
            tiempo_transcurrido = time.time() - inicio_tiempo
            comentarios_por_segundo = procesados / max(1, tiempo_transcurrido)
            
            print(f"\r🔄 Progreso: {procesados:,}/{total_comentarios:,} ({porcentaje:.1f}%) | "
                  f"Velocidad: {comentarios_por_segundo:.1f} coments/seg | "
                  f"Tiempo: {tiempo_transcurrido/60:.1f} min", end="", flush=True)
        
        # Guardar progreso cada 5000 comentarios o al finalizar
        if procesados % 5000 == 0 or procesados == total_comentarios:
            df_progreso = df.iloc[:procesados].copy()
            df_progreso[f'{columna}_Polaridad'] = polaridades[:procesados]
            df_progreso[f'{columna}_Subjetividad'] = subjetividades[:procesados]
            
            # Para las columnas que aún no se han procesado, mantenerlas intactas
            for otra_col in [c for c in df.columns if c != columna and f'{c}_Polaridad' not in df_progreso.columns]:
                df_progreso[otra_col] = df[otra_col].iloc[:procesados]
            
            df_progreso.to_csv(nombre_archivo_final, index=False)
    
    return df_progreso if 'df_progreso' in locals() else df

def seleccionar_archivo_csv():
    root = Tk()
    root.withdraw()
    archivo = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    return archivo

def main():
    print("=== ANALIZADOR DE SENTIMIENTOS ===")
    print("Versión con guardado progresivo cada 5000 comentarios\n")
    
    ruta_csv = seleccionar_archivo_csv()
    if not ruta_csv:
        print("❌ No se seleccionó ningún archivo.")
        return
    
    try:
        df = pd.read_csv(ruta_csv)
    except Exception as e:
        print(f"❌ Error al leer el archivo CSV: {e}")
        return

    columnas_a_analizar = []
    for col in ['Comentario', 'Titulo_Video', 'Descripcion_Video']:
        if col in df.columns:
            columnas_a_analizar.append(col)
        else:
            print(f"⚠️  Columna no encontrada en el CSV: {col}")

    if not columnas_a_analizar:
        print("❌ No hay columnas válidas para analizar.")
        return

    nombre_archivo_final = f"{os.path.splitext(ruta_csv)[0]}_polarizado.csv"
    
    for col in columnas_a_analizar:
        df = analizar_columna(df, col, ruta_csv)
    
    print(f"\n\n✅ Análisis completado. Archivo final guardado como: {nombre_archivo_final}")
    print("🎉 Proceso terminado con éxito!")

if __name__ == "__main__":
    main()