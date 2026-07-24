# Publicar POM OGIMET en GitHub Pages (URL fija para todo el equipo)

Con GitHub Pages tenés **una sola URL** que el equipo abre en el navegador. No hace falta descargar `index.html` cada vez.

Los datos se **actualizan solos** cada ~2 minutos: un robot en GitHub descarga SYNOP de OGIMET, regenera el HTML y lo publica. La página se recarga sola.

---

## Cómo funciona (resumen)

```
GitHub Actions (cada 2 min)
    → python build.py (descarga OGIMET, embebe 24 h de SYNOP)
    → sube index.html a la rama gh-pages

Usuario abre en el navegador
    → https://negrofei.github.io/cloudVis/
    → la página se recarga cada 2 min con datos nuevos
```

OGIMET **no permite** consultas directas desde el navegador (CORS). Por eso la actualización “en vivo” la hace GitHub en el servidor, no el `index.html` en la PC de cada usuario.

---

## Pasos para activarlo (una sola vez)

### 1. Fusionar el código en `main`

Si todavía no fusionaste el PR de `pom-ogimet`, hacelo desde GitHub:

**Pull requests → [#4](https://github.com/negrofei/cloudVis/pull/4) → Merge**

(O desde terminal: `git checkout main && git merge pom-ogimet && git push`)

### 2. Activar GitHub Pages

1. Entrá al repo: https://github.com/negrofei/cloudVis  
2. **Settings** → menú izquierdo **Pages**  
3. En **Build and deployment**:
   - **Source:** `Deploy from a branch`
   - **Branch:** `gh-pages` → carpeta `/ (root)` → **Save**

> La rama `gh-pages` se crea sola la primera vez que corre el workflow. Si no existe todavía, pasá al paso 3 y volvé acá después.

### 3. Ejecutar el workflow la primera vez

1. Pestaña **Actions**  
2. Workflow **「POM OGIMET — rebuild pages」**  
3. **Run workflow** → **Run workflow** (botón verde)

Esperá 1–2 minutos. Debería aparecer la rama `gh-pages` con `index.html`.

### 4. Verificar la URL

Abrí en el navegador:

**https://negrofei.github.io/cloudVis/**

(Settings → Pages también muestra la URL cuando está activo.)

---

## Compartir con compañeros

| Tipo de repo | ¿Quién puede ver la página? |
|--------------|----------------------------|
| **Público** | Cualquiera con el enlace (no necesitan cuenta GitHub) |
| **Privado** | Solo colaboradores del repo (plan Free: Pages del repo privado son públicos en la práctica para la URL; en planes Team+ podés restringir) |

**Para el equipo:** mandales el link `https://negrofei.github.io/cloudVis/` por mail, Teams, Slack, etc. No instalan nada.

---

## Frecuencia de actualización

- El workflow está programado cada **2 minutos** (`cron: */2 * * * *`).
- GitHub a veces retrasa jobs programados unos minutos (límite de la plataforma).
- La página publicada en Pages usa `--auto-reload-page`: se **recarga sola** cada 2 min en el navegador.

Si querés menos carga en GitHub Actions, editá `.github/workflows/pom-ogimet-pages.yml` y cambiá el cron a `*/5 * * * *` (cada 5 min).

---

## Solución de problemas

| Problema | Qué hacer |
|----------|-----------|
| 404 en la URL | Verificar que `gh-pages` existe y Pages apunta a esa rama |
| Workflow no corre solo | El workflow debe estar en la rama **`main`** |
| Actions deshabilitadas | Settings → Actions → General → permitir workflows |
| Datos viejos | Actions → último run → ver si falló `build.py` (OGIMET caído) |

---

## Alternativa sin GitHub Pages

Seguir usando `index.html` local: regenerarlo en [Colab](https://colab.research.google.com/github/negrofei/cloudVis/blob/pom-ogimet/pom-ogimet/build_colab.ipynb) cuando necesiten datos frescos. Es manual; Pages es la opción “siempre encendida”.
