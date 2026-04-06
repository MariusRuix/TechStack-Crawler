import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Configurar headers para simular un navegador
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Lista para almacenar todas las ofertas
todos_los_trabajos = []

# Iterar sobre las páginas (1 a 20) pero detenerse si no hay más páginas
for pagina in range(1, 21):
    #url = f"https://mx.computrabajo.com/trabajo-de-jr-en-remoto?p={pagina}"
    url = f"https://mx.computrabajo.com/trabajo-de-programador-en-remoto?p={pagina}"
    #url = f"https://mx.computrabajo.com/trabajo-de-auxiliar-en-remoto?p={pagina}"
    print(f"Extrayendo datos de la página {pagina}...")
    
    response = requests.get(url, headers=headers)
    
    # Verificar si la página no existe (404) o hay otro error
    if response.status_code == 404:
        print(f"🚨 No existe la página {pagina}. Terminando extracción.")
        break  # Salir del bucle si la página no existe
    elif response.status_code != 200:
        print(f"⚠️ Error en la página {pagina}: Código {response.status_code}. Continuando...")
        continue  # Saltar esta página pero seguir con la siguiente
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extraer información de cada oferta (ajusta según la estructura HTML actual)
    ofertas = soup.find_all('article', class_='box_offer')  # Clase puede variar
    
    # Si no hay ofertas en la página, terminar
    if not ofertas:
        print(f"📭 No se encontraron ofertas en la página {pagina}. Terminando extracción.")
        break
    
    for oferta in ofertas:
        titulo = oferta.find('h2', class_='fs18').text.strip() if oferta.find('h2', class_='fs18') else "Sin título"
        empresa = oferta.find('p', class_='fs16').text.strip() if oferta.find('p', class_='fs16') else "Sin empresa"
        ubicacion = oferta.find('span', class_='fs13').text.strip() if oferta.find('span', class_='fs13') else "Sin ubicación"
        
        if(empresa.find('BairesDev') == -1):
            todos_los_trabajos.append({
                "Página": pagina,
                "Título": titulo,
                "Empresa": empresa,
                "Ubicación": ubicacion
            })
    
    # Espera 2 segundos entre páginas para evitar bloqueos
    time.sleep(2)

# Guardar los datos recolectados (si hay resultados)
if todos_los_trabajos:
    df = pd.DataFrame(todos_los_trabajos)
    df.to_csv('ofertas_programador_paginacion.csv', index=False)
    print(f"✅ Datos guardados en 'ofertas_programador_paginacion.csv' (Total: {len(todos_los_trabajos)} ofertas).")
else:
    print("❌ No se encontraron ofertas en ninguna página.")