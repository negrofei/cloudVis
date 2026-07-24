# POM OGIMET — Mapa estático Argentina SYNOP → AEROMET

Herramienta web **autocontenida** para compartir con el equipo: un solo archivo HTML con mapa interactivo (Plotly) y decodificación SYNOP al formato AEROMET (estilo SMN Argentina).

## Sin Python: usar el HTML que ya está en el repo

**No hace falta instalar nada** para usar la herramienta. El archivo ya está generado con **estaciones + SYNOP de las últimas horas embebidos** (funciona aunque OGIMET bloquee CORS desde `file://`):

1. Descargá [`index.html`](https://github.com/negrofei/cloudVis/blob/pom-ogimet/pom-ogimet/index.html) desde GitHub (botón **Download**).
2. Abrilo con **Chrome** o **Firefox**.
3. Clic en una estación → AEROMET al instante (datos embebidos). Si la red/proxy funciona, intenta actualizar en vivo.

**Zoom del mapa:** rueda del mouse o botones +/- en la barra de Plotly (arriba a la derecha del mapa).

**Horas en el selector:** el HTML embebe hasta **24 h** de SYNOP al generarse (`--embed-hours`). Si pedís 6 h en el selector, verás hasta 6 partes **si existen en esos datos embebidos**. No es un límite de 3 h fijo: el build anterior usaba solo 3 h embebidas.

**Actualización cada 2 minutos:**
- El navegador **intenta** consultar OGIMET en vivo cada 2 min (suele fallar por CORS desde `file://`).
- **Solución fiable:** regenerar el HTML en Colab (o GitHub Actions cada 2 min en [GitHub Pages](https://negrofei.github.io/cloudVis/)) con datos OGIMET frescos embebidos.

**Debug de red:** activá «Mostrar debug de red». Cadena: `selectStation()` → `refreshSelectedStation()` → `fetchSynops()` → `fetchText()`.

---

## Sin Python en tu PC: regenerar con Google Colab

Si querés un `index.html` nuevo (estaciones actualizadas u otra ventana horaria por defecto):

### Opción A — Notebook listo (recomendado)

1. Abrí **[build_colab.ipynb en Colab](https://colab.research.google.com/github/negrofei/cloudVis/blob/pom-ogimet/pom-ogimet/build_colab.ipynb)** (cuenta Google gratuita).
2. **Runtime → Run all** (o ejecutá celda por celda).
3. Al final se descarga `index.html`.

Para cambiar las horas por defecto, en la celda de `build.py` usá por ejemplo:

```python
!python build.py --hours 6
```

### Opción B — Pegar en un Colab vacío

```python
!git clone --depth 1 -b pom-ogimet https://github.com/negrofei/cloudVis.git
%cd cloudVis/pom-ogimet
!pip install -q requests
!python build.py --hours 3
```

Luego:

```python
from google.colab import files
files.download("index.html")
```

### Otras opciones online (menos necesarias)

| Servicio | Cómo |
|----------|------|
| **GitHub Codespaces** | Abrir el repo → crear codespace → terminal: `cd pom-ogimet && pip install requests && python build.py` |
| **Replit** | Importar repo, ejecutar `build.py` en la consola |
| **Binder** | Posible pero Colab es más directo para descargar el archivo |

---

## Con Python local (opcional)

```bash
cd pom-ogimet
pip install -r requirements.txt
python build.py
python build.py --hours 6
```

---

## Para tus compañeros

1. Enviarles `index.html` (mail, Drive, Teams).
2. Abrirlo en el navegador — **sin Python ni servidor**.
3. Clic en estación → AEROMET de las últimas N horas (campo configurable en la página).

## Formato AEROMET

| SYNOP (extracto) | AEROMET |
|------------------|---------|
| `87750 … 12965 13412 10086 20080 … 81360` | `BAHIA BLANCA 340/12KT 15KM 1Ac9900FT 09/08 Q1017.1` |

Campos: nombre · viento · visibilidad · nube (oktas+tipo+techo ft) · T/Td · QNH.

## Archivos

| Archivo | Descripción |
|---------|-------------|
| `index.html` | App lista para compartir (ya generada) |
| `build_colab.ipynb` | Generar `index.html` en Google Colab |
| `build.py` | Generador (Colab o PC con Python) |
| `synop_aeromet.js` | Decodificador SYNOP → AEROMET |
| `template.html` | Plantilla de la interfaz |
