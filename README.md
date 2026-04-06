# CompuTrabajo Scraper (Refactored)

Un scraper avanzado y modular para extraer ofertas de empleo de CompuTrabajo utilizando una arquitectura orientada a objetos (OOP) en Python.

## 🚀 Características
- **Arquitectura de Clases**: Separación limpia entre gestión de red (`ScraperManager`), extracción de datos (`DataExtractor`) y coordinación del flujo (`JobScraperApp`).
- **Resiliencia con Tenacity**: Implementación de reintentos con espera exponencial (*exponential backoff*) para manejar límites de peticiones (errores 429) y caídas temporales del servidor.
- **Gestión de Sesiones**: Usa `requests.Session` para mayor eficiencia y persistencia de cabeceras en las peticiones.
- **Filtrado Personalizado**: Lógica integrada para omitir empresas no deseadas (ej. BairesDev) y evitar duplicados.
- **Exportación Robusta**: Guarda los resultados en un archivo CSV utilizando codificación `utf-8-sig` para garantizar la compatibilidad con Microsoft Excel.
- **Logging Profesional**: Sustitución de `print` por el módulo `logging` para trazabilidad en tiempo real.

## 🛠️ Requisitos
Asegúrate de tener instaladas las siguientes librerías:
```bash
pip install requests beautifulsoup4 pandas tenacity
```

## 📋 Uso
1. Configura el template de la URL en la sección `if __name__ == "__main__":` en `main.py`.
2. Ejecuta el script:
```bash
python main.py
```
3. Los resultados se guardarán automáticamente en `ofertas_refactorizadas.csv`.

## 📦 Estructura del Código
- **ScraperManager**: Gestiona la conectividad HTTP, cabeceras (User-Agent) y la lógica de reintento.
- **DataExtractor**: Encapsulado de la lógica de parsing con BeautifulSoup para extraer títulos, empresas y ubicaciones.
- **JobScraperApp**: Clase orquestadora que maneja la paginación, el filtrado y el guardado de datos.

## 📝 Notas de Versión (Refactoring Senior)
- Migración de script procedural a patrón de Agentes/Clases.
- Optimización de manejo de errores (timeouts y códigos de estado HTTP).
- Soporte completo para caracteres especiales en la exportación de archivos.
