# Librería de estilo compartida (`public/styles.css`)

Fecha: 2026-09-23
Estado: implementado — `lista.html`, `puntos.html`, `tecnica.html`, `fallos.html` y `mapa.html` ya usan este archivo.

## 1. Objetivo

Las 5 páginas de `public/` tenían cada una su propio `<style>` inline, con los mismos tokens de color y los mismos patrones visuales (topbar, tarjeta oscura, pills de vídeo, CTA con foto de fondo) repetidos con pequeñas variaciones accidentales entre página y página. Este refactor consolida eso en `public/styles.css`, sin cambiar el comportamiento ni el aspecto de ninguna página — es puro reordenamiento de CSS.

Páginas futuras deberían enlazar `styles.css` y usar las clases de aquí abajo antes de inventar un estilo nuevo.

**Familia estética:** data-dense / utilitaria — modo oscuro, texto pequeño, jerarquía por tamaño/peso más que por color, sin adornos. (Etiqueta propuesta para nombrar el estilo de un vistazo; confirmar o ajustar si no describe bien la intención.)

## 2. Cómo usarlo en una página nueva

```html
<head>
  <link rel="stylesheet" href="styles.css" />
  <style>
    /* solo lo que de verdad es específico de esta página */
  </style>
</head>
```

El `<link>` va **antes** del `<style>` local en el `<head>`: así, si una página necesita sobreescribir un valor puntual (p. ej. el padding de la topbar en `lista.html`), el `<style>` local gana por orden de cascada sin necesidad de subir especificidad ni usar `!important`.

## 3. Tokens (`:root`)

| Token | Valor | Uso |
|---|---|---|
| `--bg-dark` | `#16181d` | fondo de página |
| `--bg-dark-2` | `#1f2229` | tarjetas, dropdowns, chips |
| `--bg-dark-3` | `#2a2e37` | fondo de chip/pill sobre `--bg-dark-2` |
| `--accent` | `#8b7cf6` | acento principal (enlaces, iconos activos) — violeta, branding cerrado con TuCopilotoB (antes `#4285F4`) |
| `--lila` | `#8b7cf6` | alias de `--accent`, usado explícito en el CTA "última clase"; mismo color, branding ya cerrado |
| `--confirm` | `#34C7A3` | verde-menta — "ya repasado/confirmado" (icono, badges de estado) |
| `--border` | `#383d48` | borde de chip/pill/select |
| `--border-subtle` | `#23262e` | separador entre secciones (`.section-heading`) |
| `--text` | `#e7e9ee` | texto principal |
| `--text-muted` | `#c7ccd4` | texto secundario (cuerpo de tarjeta) |
| `--text-dim` | `#9aa0ab` | texto terciario (intros, subtítulos) |
| `--text-dimmer` | `#767c88` | metadatos, estado vacío |
| `--text-faint` | `#565c66` | fechas pequeñas, texto casi invisible |
| `--text-faintest` | `#6b7280` | labels uppercase de grupo |
| `--warn-bg` / `--warn-border` / `--warn-text` | `#2a2410` / `#4d3f1a` / `#e0c27a` | aviso tipo warning (`.aviso` en `fallos.html`) |
| `--shadow-topbar` | `0 2px 8px rgba(0,0,0,.35)` | sombra de la topbar |
| `--shadow-card` | `0 1px 4px rgba(0,0,0,.3)` | sombra de `.punto-card` |
| `--radius-lg` / `--radius-md` / `--radius-sm` / `--radius-pill` | `14px` / `12px` / `8px` / `999px` | radios de borde |
| `--font-sans` | `-apple-system, BlinkMacSystemFont, sans-serif` | tipografía |

Ninguno es un color nuevo: todos vienen de lo que ya se usaba en alguna de las 5 páginas antes de este refactor.

## 4. Componentes

### Base de página
`html, body` y `main` llevan el fondo, color de texto, tipografía y el contenedor centrado a `max-width: 640px` que usan `lista/puntos/tecnica/fallos`. `mapa.html` es la excepción: necesita ocupar el viewport completo sin scroll (el mapa de Leaflet lo maneja), así que añade `height`/`overflow`/`flex` encima de esta base en su propio `<style>`, en vez de usar `<main>`.

### `.topbar` + `.topbar-row`
`.topbar` da el "chrome" común de cabecera: fondo, sombra, `position: sticky`, padding base. `.topbar-row` es el modificador para el layout en fila (título a la izquierda, enlace/controles a la derecha) que usan `puntos.html`, `tecnica.html` y `fallos.html`:

```html
<div id="topbar" class="topbar topbar-row">
  <h1>Título</h1>
  <a href="lista.html" class="topbar-link">← Mis clases</a>
</div>
```

`lista.html` usa solo `.topbar` (título + subtítulo apilados, sin fila), con su padding propio en el `<style>` local. `mapa.html` no usa ninguna de las dos: su topbar no es sticky (vive dentro de un layout de columna flex de página completa) y tiene necesidades de z-index/padding propias — pero sí reutiliza `.topbar-link` para el enlace de vuelta.

### `.topbar-link`
El enlace de "← Mis clases" que aparece en las 4 páginas que no son home. Color de acento, sin subrayado, sin salto de línea.

### `.card`
Tarjeta oscura base: `background: var(--bg-dark-2)`, `border-radius: var(--radius-md)`, `padding: 14px 16px`. **No** incluye sombra ni margin — cada uso los añade porque legítimamente varían (`.punto-card` en `puntos.html` tiene sombra y `margin-bottom`; el dropdown de resultados de `lista.html` tiene `margin-top` y `max-height` en su lugar, sin sombra).

### `.cta-thumb`
CTA con foto de fondo + degradado + texto encima, usado 3 veces en `lista.html`. Incluye el degradado (`::after`), el contenedor `.contenido` y `.titulo`. El `.label` de dentro se combina con `.label-upper` (ver abajo) más una opacidad propia por uso.

```html
<a class="cta-thumb" href="destino.html" style="background-image:url('...');">
  <div class="contenido">
    <div class="label-upper label">Categoría</div>
    <div class="titulo">Texto del CTA →</div>
  </div>
</a>
```

### `.pill`
Chip pequeño de fuente/vídeo (▶ Nombre del canal), usado en `tecnica.html` y `fallos.html`. Antes se llamaba `.video-pill` en cada archivo por separado; ahora es una clase genérica.

### `.label-upper`
Primitiva de "label uppercase pequeño": mayúsculas, `letter-spacing: .05em`, `font-weight: 700`, `font-size: 10.5px`. Se combina con una segunda clase específica del contexto para el color/opacidad/tamaño exacto, que sí varía legítimamente entre usos (texto blanco con opacidad sobre foto vs. texto gris sobre fondo sólido vs. 11px en el CTA lila). Ejemplos reales: `class="label-upper label"` (cta-thumb/cta-ultima), `class="label-upper grupo-label"` (buscador de home).

### `.section-heading`
Encabezado de sección con separador superior (uppercase, color de acento, `border-top`), usado por `h2.categoria` (`tecnica.html`) y `h2.zona` (`fallos.html`). El `margin` se queda en cada página porque difiere (28px vs 26px) y no es visualmente significativo compartirlo.

### `.empty-state`
Estado vacío/error de carga: texto centrado, atenuado. Se añade como clase adicional al `id="vacio"` que cada página ya usa desde JS (`getElementById('vacio')`) — no lo sustituye.

### `.badge-count` (sin uso todavía)
Círculo con número, pensado como "badge de recuento". **Aviso**: al auditar las 5 páginas no se encontró ningún patrón de círculo+número ya existente en las tarjetas CTA de home (solo hay un contador de texto plano, `#contador`, en `puntos.html`). Se define aquí con los tokens ya existentes por si el pedido original se refería a algo pendiente de construir, pero no se ha aplicado en ninguna página — confirmar con Ilaria antes de usarlo, en vez de asumir dónde debería ir.

## 5. Qué se queda deliberadamente fuera

- Los colores por zona (`ZONA_COLORS` en `lista.html`/`puntos.html`, los `color` de cada capa en `mapa.html`) son identificadores categóricos ligados a datos, no parte del sistema de diseño — se quedan como objetos JS en cada página.
- El CSS específico de Leaflet, del reproductor de `mapa.html` (controles, flecha de navegación, panel de copiloto) y del buscador de `lista.html` se queda en el `<style>` local de cada página: es genuinamente específico de esa página, no un patrón repetido.
- Al migrar `lista.html` se eliminó el bloque `#navlinks` (chip de navegación con fondo/borde): no tenía ningún elemento correspondiente en el HTML de la página (código muerto de una iteración anterior), así que no se migró a ningún sitio.

## 6. Do / Don't

- **Do** usar los tokens de `:root` para cualquier color/radio/sombra nuevo; **don't** escribir un valor hex o `px` suelto en un `<style>` local si ya existe un token equivalente.
- **Do** añadir una clase nueva a `styles.css` cuando el mismo patrón visual se repite en 2+ páginas; **don't** duplicar reglas de `.card`, `.pill`, `.topbar`, etc. con variaciones accidentales dentro del `<style>` local de una página.
- **Do** dejar en el `<style>` local lo que es genuinamente específico de una página (Leaflet, el reproductor de `mapa.html`, el buscador de `lista.html`); **don't** intentar generalizar algo que solo se usa una vez.
- **Do** actualizar esta tabla de tokens en el mismo commit que cambia un valor en `:root`; **don't** dejar que este documento quede desactualizado respecto a `styles.css` (ver el fix de `--accent`/`--lila`/`--confirm` de este mismo pase).
