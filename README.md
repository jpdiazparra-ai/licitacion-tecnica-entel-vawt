# Licitación técnica consolidada

Vista independiente de Streamlit para revisar e imprimir solo la pestaña **licitación técnica consolidada**, manteniendo el panel lateral izquierdo de parámetros.

Configuración base de la versión publicada:

- Generador fijo: `GDG-860 - 10 kW`.
- Recurso/SCADA fijo: `assets/MG888.csv`.
- Vista reducida a Entel consolidado, sin descargas integrales del dashboard general.

Archivo principal:

```bash
app_licitacion_consolidada.py
```

Ejecución local:

```bash
streamlit run app_licitacion_consolidada.py --server.address 127.0.0.1 --server.port 8515
```
