# Laboratorio de Baterías

Laboratorio interactivo en Streamlit sobre **materiales utilizados en baterías y almacenamiento de energía**
(Ingeniería de Materiales, Grupo 05, semestre 2027-1).

## Secciones
- Funcionamiento de la celda de ion-litio (carga / descarga)
- Calculadora de capacidad teórica (ley de Faraday)
- Mapa voltaje vs. capacidad y tabla comparativa de cátodos
- Estructuras cristalinas 3D (laminar, espinela, olivino) y tiempo de difusión
- Ánodos: grafito, titanato, silicio y expansión de volumen
- Simulador de celda (cátodo + ánodo + temperatura)
- Selección de material según la aplicación
- Procesamiento (calcinación, calandrado) y obtención de materias primas
- Quiz

## Ejecutar localmente

**Windows:** instala Python 3.10 o más nuevo desde https://www.python.org/downloads/
(marca "Add Python to PATH") y haz doble clic en `iniciar_windows.bat`.

**macOS / Linux:**
```bash
pip install -r requirements.txt
streamlit run Interactivo.py
```

Funciona en Chrome, Edge, Firefox y Safari. El tema claro está fijado en `.streamlit/config.toml`
para que se vea igual aunque el sistema esté en modo oscuro.

Las curvas de descarga, los coeficientes de difusión y las calificaciones cualitativas son aproximaciones con fines didácticos.
