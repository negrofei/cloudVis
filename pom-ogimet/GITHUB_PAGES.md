# Publicar POM OGIMET en GitHub Pages (URL fija para todo el equipo)

**URL del mapa (cuando Pages esté activo):** https://negrofei.github.io/cloudVis/

---

## Paso 1 — Activar GitHub Pages (lo más importante)

1. Abrí https://github.com/negrofei/cloudVis/settings/pages  
2. En **Build and deployment** → **Source**:
   - Elegí **Deploy from a branch**
   - **Branch:** `gh-pages`
   - **Folder:** `/ (root)`
3. Clic en **Save**

En 1–2 minutos la URL debería funcionar. La rama `gh-pages` **ya existe** en el repo con `index.html` listo.

---

## Paso 2 — Activar GitHub Actions (para actualización automática)

Si en la pestaña **Actions** no ves workflows ni el botón **Run workflow**, suele ser porque Actions no está habilitado todavía.

### A) Primera vez en Actions

1. https://github.com/negrofei/cloudVis/actions  
2. Si aparece un cartel verde **「I understand my workflows, go ahead and enable them」** → hacé clic.  
3. Recargá la página.

### B) Encontrar el workflow y ejecutarlo

1. En el **menú izquierdo** de Actions, buscá **`pom-ogimet-pages`** (no en el centro de la pantalla).  
2. Hacé clic en ese nombre.  
3. A la **derecha**, arriba de la lista de ejecuciones, debería aparecer **「Run workflow」** (solo si tenés permisos de escritura en el repo).  
4. Dejá branch `main` → **Run workflow**.

**Enlace directo al workflow:**  
https://github.com/negrofei/cloudVis/actions/workflows/pom-ogimet-pages.yml

### C) Si no aparece «Run workflow»

| Causa | Qué hacer |
|-------|-----------|
| No sos admin/colaborador con escritura | Pedile al dueño del repo (`negrofei`) que ejecute el workflow o te dé acceso |
| Actions deshabilitado en el org | Settings → Actions → General → permitir acciones |
| Estás en un fork | Los workflows se ejecutan en el repo original, no en el fork |

**Mientras tanto:** la página en GitHub Pages **ya funciona** con los datos del último deploy; solo no se actualizará sola hasta que Actions corra.

---

## Paso 3 — Compartir con el equipo

**https://negrofei.github.io/cloudVis/**

Cualquier persona con el enlace puede abrirlo (repo público). No hace falta cuenta GitHub.

---

## Cómo se actualizan los datos

| Mecanismo | Frecuencia |
|-----------|------------|
| Workflow `pom-ogimet-pages` | Cada ~5 min (cuando Actions está activo) |
| Recarga de la página en Pages | Cada 2 min (automática) |

El workflow descarga SYNOP de OGIMET en el servidor de GitHub y regenera `index.html`.

---

## Regenerar manualmente (sin Actions)

[Notebook Colab](https://colab.research.google.com/github/negrofei/cloudVis/blob/main/pom-ogimet/build_colab.ipynb) → Run all → descargás `index.html`.
