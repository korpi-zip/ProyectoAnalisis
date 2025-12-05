# Analizador de Complejidad Algorítmica Híbrido

Este proyecto implementa una herramienta avanzada para el análisis automático de la complejidad temporal de algoritmos escritos en pseudocódigo. Utiliza un enfoque híbrido que combina análisis estático formal, memoización y asistencia de Inteligencia Artificial (Google Gemini) para resolver casos complejos.

## 🚀 Características Principales

*   **Análisis Híbrido:** Combina reglas matemáticas formales para estructuras estándar con análisis de IA para casos complejos (como ciclos dependientes).
*   **Memoización (Knowledge Base):** Sistema de persistencia que "aprende" de análisis previos, almacenando resultados para evitar re-cálculos y mejorar el rendimiento.
*   **Soporte de Pseudocódigo:** Parser personalizado para una gramática tipo Pascal (bucles `para`, `mientras`, condicionales `si`, procedimientos, etc.).
*   **Integración con Gemini:** Utiliza la API de Google Gemini 1.5 Flash para interpretar semánticamente estructuras que escapan al análisis estático tradicional.
*   **Métricas de Complejidad:** Calcula y reporta complejidad en notación Big O ($O$), Omega ($\Omega$) y Theta ($\Theta$).

## 📋 Requisitos

*   Python 3.8+
*   Clave de API de Google Gemini (para funciones avanzadas de IA)

## 🛠️ Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone <url-del-repositorio>
    cd ProyectoAnalisis
    ```

2.  **Crear un entorno virtual (recomendado):**
    ```bash
    python -m venv .venv
    # Windows
    .\.venv\Scripts\activate
    # Linux/Mac
    source .venv/bin/activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar Variables de Entorno:**
    Crea un archivo `.env` en la raíz del proyecto y agrega tu clave de API:
    ```env
    GEMINI_API_KEY=tu_clave_api_aqui
    ```

## ▶️ Uso

1.  **Colocar algoritmos:**
    Guarda tus archivos de pseudocódigo (`.txt`) en la carpeta `algorithms/`.

2.  **Ejecutar el analizador:**
    ```bash
    python -m src.main
    ```

3.  **Ver resultados:**
    La herramienta procesará todos los archivos en `algorithms/` y mostrará el análisis de complejidad en la consola.

## 📂 Estructura del Proyecto

```
ProyectoAnalisis/
├── algorithms/          # Archivos de prueba (.txt)
├── src/
│   ├── ai_engine.py     # Integración con Google Gemini
│   ├── analyzer.py      # Lógica central de análisis y recorrido AST
│   ├── knowledge_base.py # Gestión de memoización (JSON)
│   ├── main.py          # Punto de entrada
│   ├── models.py        # Definiciones de Nodos AST
│   └── parser.py        # Tokenizador y Parser Recursivo
├── knowledge_base.json  # Base de datos persistente (generada)
├── requirements.txt     # Dependencias de Python
├── .env                 # Configuración (API Key)
└── README.md            # Documentación
```

## 📄 Licencia

Este proyecto es de uso académico y educativo.
