# Vibecodeado con Gemini
import urllib.parse
import requests
import os

# --- CONFIGURACIÓN ---
ARCHIVO_ENLACES = 'files/enlaces-descarga-cuadrantes.txt'
URL_DESTINO_POST = 'https://centrodedescargas.cnig.es/CentroDescargas/descargaDir' 
PARAMETRO_A_EXTRAER = 'sec'
CARPETA_DESCARGAS = 'cnig'

# Crear la carpeta de descargas si no existe
os.makedirs(CARPETA_DESCARGAS, exist_ok=True)

def main():
    try:
        with open(ARCHIVO_ENLACES, 'r', encoding='utf-8') as archivo:
            enlaces = [linea.strip() for linea in archivo if linea.strip()]

        for enlace in enlaces:
            print(f"Descargando: {enlace}")

            # 1. Extraer parámetro de la URL
            parsed_url = urllib.parse.urlparse(enlace)
            parametros_url = urllib.parse.parse_qs(parsed_url.query)
            
            if PARAMETRO_A_EXTRAER in parametros_url:
                valor_id = parametros_url[PARAMETRO_A_EXTRAER][0]
                payload = {
                    'secuencial': valor_id,
                    'secDescDirLA': valor_id,
                    'codSerie': "PNOIR",
                }
                
                try:
                    # 2. Hacer POST con stream=True para no saturar la RAM
                    with requests.post(URL_DESTINO_POST, data=payload, stream=True, timeout=30) as r:
                        r.raise_for_status()
                        
                        content_disp = r.headers.get('Content-Disposition')
                        if content_disp and 'filename=' in content_disp:
                            nombre_archivo = content_disp.split('filename=')[1].strip('"')
                        else:
                            nombre_archivo = f"descarga_{valor_id}.dat"
                        
                        ruta_final = os.path.join(CARPETA_DESCARGAS, nombre_archivo)
                        
                        # 3. Escribir el archivo en el disco por fragmentos
                        with open(ruta_final, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    
                except requests.exceptions.RequestException as e:
                    print(f"    [Fallo] Error en la petición para {valor_id}: {e}")
            else:
                print(f"[-] No se encontró '{PARAMETRO_A_EXTRAER}' en {enlace}")

    except FileNotFoundError:
        print(f"Error: No se encontró '{ARCHIVO_ENLACES}'")

if __name__ == '__main__':
    main()
