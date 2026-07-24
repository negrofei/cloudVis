# POM OGIMET — Mapa estático Argentina SYNOP → AEROMET

Herramienta web **autocontenida** para compartir con el equipo: un solo archivo HTML con mapa interactivo (Plotly) y decodificación SYNOP al formato AEROMET (estilo SMN Argentina).

## Para quien genera el archivo (una vez, con Python)

```bash
cd pom-ogimet
pip install requests
python build.py
```

Esto crea `index.html` con las ~114 estaciones Argentina embebidas (coordenadas desde OGIMET, misma lógica que `fetch_stations_argentina` en cloudVis).

Opciones:

```bash
python build.py --hours 6          # ventana por defecto al abrir (3 h por defecto)
python build.py --output mapa.html
```

## Para tus compañeros (sin Python ni servidor)

1. Enviarles el archivo `index.html` (por mail, Drive, Teams, etc.).
2. Abrirlo con **Chrome** o **Firefox** (doble clic o arrastrar al navegador).
3. Clic en una estación → se descargan los SYNOP de OGIMET de las últimas N horas (configurable) y se muestra el **AEROMET** decodificado.

Los datos en vivo se obtienen desde [OGIMET](http://www.ogimet.com/cgi-bin/getsynop) en el navegador. Si el navegador bloquea la petición directa (CORS), se usa un proxy público de respaldo.

## Formato AEROMET

Ejemplo:

| SYNOP (extracto) | AEROMET |
|------------------|---------|
| `87750 … 12965 13412 10086 20080 … 81360` | `BAHIA BLANCA 340/12KT 15KM 1Ac9900FT 09/08 Q1017.1` |

Campos: nombre · viento · visibilidad · nube significativa (oktas+tipo+techo ft) · T/Td · QNH.

## Regenerar estaciones

Las coordenadas se fijan al ejecutar `build.py`. Si cambia el listado OGIMET, volver a correr el script y redistribuir el HTML.

## Archivos

| Archivo | Descripción |
|---------|-------------|
| `build.py` | Genera `index.html` con estaciones embebidas |
| `synop_aeromet.js` | Decodificador SYNOP → AEROMET |
| `template.html` | Plantilla de la app |
| `index.html` | Salida lista para compartir (generada) |
