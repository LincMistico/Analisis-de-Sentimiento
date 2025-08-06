import pandas as pd
from textblob import TextBlob
from googletrans import Translator
from tkinter import Tk, filedialog
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import numpy as np

# Configuración inicial
MAX_WORKERS = os.cpu_count() * 2  # Aprovechamos los núcleos del CPU
CHUNK_SIZE = 100  # Procesamiento por lotes para mejor manejo de memoria

# Inicializa el traductor (versión más estable)
translator = Translator(service_urls=['translate.google.com'])

def traducir_y_analizar(texto):
    """Función optimizada para traducción y análisis de sentimiento"""
    if pd.isna(texto) or not str(texto).strip():
        return None, None
    
    try:
        # Intenta primero analizar en español (evita traducción si no es necesaria)
        try:
            blob = TextBlob(str(texto))
            if blob.detect_language() == 'en':
                return blob.sentiment.polarity, blob.sentiment.subjectivity
        except:
            pass
        
        # Si no es inglés, traduce
        traduccion = translator.translate(str(texto), src='es', dest='en').text
        blob = TextBlob(traduccion)
        return blob.sentiment.polarity, blob.sentiment.subjectivity
    except Exception as e:
        print(f"\n⚠️ Error en texto: '{texto[:50]}...' - {str(e)[:100]}")
        return None, None

def procesar_lote(textos):
    """Procesa un lote de textos en paralelo"""
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(traducir_y_analizar, texto) for texto in textos]
        resultados = []
        for future in as_completed(futures):
            resultados.append(future.result())
    return resultados

def analizar_columna(df, columna):
    """Función optimizada con procesamiento por lotes y paralelización"""
    textos = df[columna].astype(str).tolist()
    polaridades = []
    subjetividades = []
    
    # Procesamiento por lotes con barra de progreso
    for i in tqdm(range(0, len(textos), CHUNK_SIZE), desc=f"Analizando {columna}"):
        lote = textos[i:i + CHUNK_SIZE]
        resultados = procesar_lote(lote)
        pol, sub = zip(*resultados) if resultados else ([], [])
        polaridades.extend(pol)
        subjetividades.extend(sub)
    
    df[f'{columna}_Polaridad'] = np.array(polaridades, dtype=np.float32)
    df[f'{columna}_Subjetividad'] = np.array(subjetividades, dtype=np.float32)
    return df

def seleccionar_archivo_csv():
    """Interfaz para seleccionar archivo optimizada"""
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    archivo = filedialog.askopenfilename(
        title="Seleccione archivo CSV",
        filetypes=[("CSV files", "*.csv"), ("Todos los archivos", "*.*")]
    )
    root.destroy()
    return archivo

def guardar_csv(df, ruta_original):
    """Función de guardado optimizada"""
    nombre, ext = os.path.splitext(ruta_original)
    nuevo_nombre = f"{nombre}_analizado.csv"
    
    # Optimización para archivos grandes
    if len(df) > 100000:
        df.to_csv(nuevo_nombre, index=False, chunksize=10000)
    else:
        df.to_csv(nuevo_nombre, index=False)
    
    print(f"\n✅ Análisis completado. Resultados guardados en:\n{nuevo_nombre}")

def main():
    print("=== Analizador de Sentimiento Optimizado ===")
    print(f"Configuración: {MAX_WORKERS} hilos de trabajo | Lotes de {CHUNK_SIZE} textos")
    
    ruta_csv = seleccionar_archivo_csv()
    if not ruta_csv:
        print("Operación cancelada: No se seleccionó ningún archivo.")
        return
    
    try:
        # Carga optimizada del CSV
        df = pd.read_csv(ruta_csv, dtype='string', on_bad_lines='warn')
        print(f"\n📊 Archivo cargado: {len(df)} registros | Columnas: {list(df.columns)}")
        
        # Columnas a analizar (con flexibilidad)
        
        columnas_a_analizar = []
        for col in ['Comentario', 'Título_Video', 'Descripción_Video']:
            if col in df.columns:
                columnas_a_analizar.append(col)
            
        if not columnas_a_analizar:
            print("\n❌ No se encontraron columnas de texto para analizar.")
            print("Sugerencia: Renombre sus columnas para incluir 'comentario', 'titulo' o 'descripcion'")
            return
        
        print(f"\n🔍 Columnas seleccionadas para análisis: {columnas_a_analizar}")
        
        # Análisis en paralelo
        for col in columnas_a_analizar:
            df = analizar_columna(df, col)
        
        # Guardar resultados
        guardar_csv(df, ruta_csv)
        
    except Exception as e:
        print(f"\n❌ Error crítico: {str(e)}")
        print("Posibles soluciones:")
        print("1. Verifique que el archivo sea un CSV válido")
        print("2. Asegúrese de tener permisos de lectura/escritura")
        print("3. Intente con un archivo más pequeño para probar")

if __name__ == "__main__":
    main()