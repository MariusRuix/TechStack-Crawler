import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ScraperManager:
    """
    Gestiona la sesión de red, las peticiones HTTP y el sistema de reintentos.
    """
    def __init__(self, base_headers=None):
        self.session = requests.Session()
        self.headers = base_headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.session.headers.update(self.headers)

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.exceptions.RequestException, requests.exceptions.HTTPError)),
        before_sleep=lambda retry_state: logger.info(f"Reintentando... (Intento {retry_state.attempt_number})")
    )
    def fetch_page(self, url):
        """
        Realiza una petición GET con lógica de reintento exponencial (tenacity).
        """
        response = self.session.get(url, timeout=10)
        
        # Lanzar excepción para códigos 4xx o 5xx (excepto 404 para manejo controlado)
        if response.status_code == 429:
            logger.warning("Rímite de peticiones alcanzado (429).")
            response.raise_for_status()
        
        if response.status_code == 404:
            return None
        
        response.raise_for_status()
        return response.text

class DataExtractor:
    """
    Encargado del parseo de HTML y extracción de datos específicos.
    """
    @staticmethod
    def parse_job_offers(html_content):
        """
        Recibe HTML y devuelve una lista de ofertas procesadas.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        raw_offers = soup.find_all('article', class_='box_offer')
        
        jobs = []
        for offer in raw_offers:
            # Extraer y limpiar datos con fallbacks seguros
            title = offer.find('h2', class_='fs18')
            company = offer.find('p', class_='fs16')
            location = offer.find('span', class_='fs13')
            
            job_data = {
                "Título": title.text.strip() if title else "Sin título",
                "Empresa": company.text.strip() if company else "Sin empresa",
                "Ubicación": location.text.strip() if location else "Sin ubicación"
            }
            jobs.append(job_data)
            
        return jobs

class JobScraperApp:
    """
    Clase principal que coordina el flujo de scraping.
    """
    def __init__(self, search_url_template):
        self.scraper = ScraperManager()
        self.extractor = DataExtractor()
        self.url_template = search_url_template
        self.results = []

    def run(self, max_pages=20):
        logger.info(f"Iniciando proceso de scraping (máximo {max_pages} páginas)...")
        
        for p in range(1, max_pages + 1):
            url = self.url_template.format(page=p)
            logger.info(f"Procesando página {p}: {url}")
            
            try:
                html = self.scraper.fetch_page(url)
                
                if html is None:
                    logger.info(f"Página {p} no encontrada (404). Deteniendo.")
                    break
                
                page_jobs = self.extractor.parse_job_offers(html)
                
                if not page_jobs:
                    logger.info(f"No hay más ofertas en la página {p}. Deteniendo.")
                    break
                
                # Filtrar BairesDev (mantenido según script original)
                filtered_jobs = [
                    {**job, "Página": p} 
                    for job in page_jobs 
                    if 'BairesDev' not in job['Empresa']
                ]
                
                self.results.extend(filtered_jobs)
                logger.info(f"Página {p}: {len(filtered_jobs)} ofertas extraídas.")
                
                # Respetar tiempo de espera entre peticiones
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error crítico en página {p}: {e}")
                continue

        self.save_results()

    def save_results(self, filename='ofertas_refactorizadas.csv'):
        if self.results:
            df = pd.DataFrame(self.results)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            logger.info(f"✅ Éxito: {len(self.results)} ofertas guardadas en {filename}")
        else:
            logger.error("❌ No se encontraron datos para guardar.")

if __name__ == "__main__":
    # Template para la búsqueda
    SEARCH_URL = "https://mx.computrabajo.com/trabajo-de-programador-en-remoto?p={page}"
    
    app = JobScraperApp(SEARCH_URL)
    app.run(max_pages=20)