import pandas as pd
from tkinter import filedialog, Tk
import os

# Diccionario oficial de categorías de YouTube
categorias_youtube = {
    1:  "Film & Animation",
    2:  "Autos & Vehicles",
    10: "Music",
    15: "Pets & Animals",
    17: "Sports",
    18: "Short Movies",
    19: "Travel & Events",
    20: "Gaming",
    21: "Videoblogging",
    22: "People & Blogs",
    23: "Comedy",
    24: "Entertainment",
    25: "News & Politics",
    26: "Howto & Style",
    27: "Education",
    28: "Science & Technology",
    29: "Nonprofits & Activism",
    30: "Movies",
    31: "Anime/Animation",
    32: "Action/Adventure",
    33: "Classics",
    34: "Comedy (Movies)",
    35: "Documentary",
    36: "Drama",
    37: "Family",
    38: "Foreign",
    39: "Horror",
    40: "Sci-Fi/Fantasy",
    41: "Thriller",
    42: "Shorts",
    43: "Shows",
    44: "Trailers"
}

# Función para seleccionar archivo
def seleccionar_csv():
    root = Tk()
    root.withdraw()
    return filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])

def procesar_categoria():
    archivo = seleccionar_csv()
    if not archivo:
        print("❌ No se seleccionó ningún archivo.")
        return

    try:
        df = pd.read_csv(archivo)

        if 'Categoria_ID' not in df.columns:
            print("❌ La columna 'Categoria_ID' no existe en el archivo.")
            return

        # Convertir a numérico por seguridad
        df['Categoria_ID'] = pd.to_numeric(df['Categoria_ID'], errors='coerce')
        # Crear nueva columna con nombre de categoría
        df['Categoria_Nombre'] = df['Categoria_ID'].map(categorias_youtube)
        # Eliminar la columna original
        df = df.drop(columns=['Categoria_ID'])

        # Guardar archivo con el mismo nombre
        df.to_csv(archivo, index=False, encoding='utf-8-sig')
        print(f"✅ Archivo actualizado y guardado: {archivo}")

    except Exception as e:
        print(f"⚠️ Error procesando el archivo: {e}")

# Ejecutar
if __name__ == "__main__":
    procesar_categoria()
