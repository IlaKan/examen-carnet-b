# Diseño: mapa de rutas y puntos críticos del examen práctico (Barcelona)

Fecha: 2026-09-22
Estado: pendiente de aprobación de Ilaria

## 1. Objetivo

Pasar del MVP estático actual (un `index.html` con Leaflet cargando `data.js`/`tracks.js` a mano) a un producto que escale más allá de una clase:

- Grabar y **acumular** cada clase real (GPX de Open GPX Tracker) sin perder ninguna.
- Poder elegir una ruta desde un listado, filtrando por **zona** (criterio principal) y por **fecha** (secundario).
- Repasar cada ruta con **infraestructura real** (semáforos, stops, cedas, pasos de peatones, carriles bici/bus, obras) superpuesta, más las notas propias de la clase.
- Usarlo desde el iPhone, en cualquier sitio, sin depender de que el Mac esté encendido.
- Que siga funcionando igual de bien con 30+ clases grabadas que con 1.

No objetivo de esta versión (aparcado explícitamente, YAGNI):
- Tracks de otras personas (p.ej. Guillem) — solo los de Ilaria.
- Edición en vivo desde el navegador/iPhone (no hay backend).
- Categorización estructurada de las notas manuales (texto libre basta).
- Cobertura de obras fuera de Barcelona ciudad (l'Hospitalet no tiene fuente automática localizada).

## 2. Arquitectura general

Sitio estático (HTML + JS + JSON, sin servidor propio ni base de datos), publicado gratis en GitHub Pages. Dos partes:

- **El sitio**: lo que se abre desde el iPhone o el Mac. Dos páginas: `lista.html` y `mapa.html`.
- **El script de ingesta**: se corre en el Mac de Ilaria cada vez que termina una clase. Convierte un `.gpx` nuevo en los archivos que el sitio necesita, y publica (git commit + push).

## 3. Estructura del repositorio y qué se publica

```
/                           (repo git, NO se publica entero)
├── CLAUDE.md                — trabajo interno, NUNCA se sube a git (.gitignore)
├── skill-examen-...md       — igual, NUNCA se sube (.gitignore)
├── gpx/                     — .gpx originales sin procesar, NUNCA se suben (.gitignore)
├── docs/superpowers/specs/  — specs de diseño (este archivo), sí se comitea, no se publica como web
├── scripts/
│   ├── nueva_clase.py       — ingesta: gpx -> archivos del sitio + publica
│   └── corregir_infra.py    — añade/corrige infraestructura mal etiquetada en OSM
└── public/                  — ESTO es lo único que GitHub Pages sirve como web
    ├── lista.html
    ├── mapa.html
    ├── data/
    │   ├── points.json          (68 puntos críticos, hoy data.js)
    │   ├── zones.json            (hoy zonas.js, vacío hasta confirmar nombres)
    │   └── tracks/
    │       ├── index.json        (id, nombre, fecha, zona(s), duración — alimenta la lista)
    │       ├── <id>.json         (puntos con lat/lng/timestamp + metadata)
    │       ├── <id>-osm.json     (infraestructura OSM cacheada para esa ruta)
    │       ├── <id>-obras.json   (obras de Open Data BCN cacheadas para esa ruta)
    │       └── <id>-overrides.json (tus correcciones manuales a la capa OSM, si las hay)
```

**Por qué**: el repo tiene que ser público para que GitHub Pages sea gratis, pero eso no significa que todo el contenido del repo tenga que ser público — solo `public/` se sirve como web. `CLAUDE.md`, los `.gpx` en crudo y los apuntes internos se quedan solo en tu Mac, nunca llegan a GitHub. Así se cumple lo que ya decidiste (sin nombre de tu compañero, sin exponer más de lo necesario) sin tener que pagar por un repo privado.

¿Esto encaja, o prefieres otra forma de separar "lo público" de "lo interno"?

## 4. Capa de datos

- **`data/points.json`**: los 68 puntos críticos del catálogo HoyVoy (migración directa de `data.js`).
- **`data/zones.json`**: catálogo de zonas (migración de `zonas.js`, sigue vacío hasta que confirmes nombres reales).
- **`data/tracks/index.json`**: un array ligero, uno por clase — `{id, nombre, fecha, zonas: [...], duracion_min}`. Es lo único que carga `lista.html`, así que aunque haya 100 clases, la lista sigue siendo rápida.
- **`data/tracks/<id>.json`**: la clase completa — cada punto con `[lat, lng, timestamp]` (no solo `[lat,lng]` como ahora, para poder animar la reproducción con velocidad real), más metadata (conductor, fuente, verificación geográfica, duración).
- **`data/tracks/<id>-osm.json`**: infraestructura de OpenStreetMap para el área de esa ruta, pre-cargada una vez al procesar el GPX (no en cada visita). Ver tabla de la sección 6.
- **`data/tracks/<id>-obras.json`**: obras activas/recientes de Open Data Barcelona cerca de esa ruta, mismo criterio de pre-carga.
- **`data/tracks/<id>-overrides.json`**: solo existe si has corregido algo con `corregir_infra.py` — puntos añadidos a mano o marcados como "esto no existe/está mal".

## 5. Frontend — dos páginas

### `lista.html`
- Filtro por zona (chips o dropdown) y por fecha (más recientes primero por defecto).
- Cada clase es una tarjeta: nombre, fecha, duración, zona(s) → enlace a `mapa.html?track=<id>`.
- Carga solo `data/tracks/index.json`, nunca las rutas completas — rápido incluso con muchas clases.

### `mapa.html?track=<id>`
- Línea de la ruta completa, tenue, siempre visible como referencia.
- **Reproducción animada** (la razón por la que existe esta sección): coche 🚗 que avanza según el timestamp real, línea "recorrida hasta ahora" en rojo, controles de play/pausa y slider para saltar a cualquier punto. Resuelve el problema real que viste hoy: en una ruta con tramos repetidos en los dos sentidos, ninguna línea estática sin animar puede mostrar la dirección sin ambigüedad.
- **Checkboxes por capa**: semáforos / stops / cedas / pasos de peatones / carril bici / carril bus / obras / tus notas — cada una se puede mostrar u ocultar por separado, para no saturar el mapa.
- Los 68 puntos críticos del catálogo que caigan cerca de esta ruta, con su nota.
- Tus notas manuales del GPX de esa clase (waypoints con toque largo).

¿Esta división en dos páginas y este set de controles del mapa te sirve, o cambiarías algo antes de que lo construyamos?

## 6. Capa de infraestructura — fuente por elemento

| Elemento | Fuente | Automático/Manual | Fiabilidad conocida |
|---|---|---|---|
| Semáforos | OpenStreetMap (`highway=traffic_signals`), vía Overpass API | Automático | Alta |
| Stops | OpenStreetMap (`highway=stop`) | Automático | Media — puede faltar alguno |
| Cedas el paso | OpenStreetMap (`highway=give_way`) | Automático | Media |
| Pasos de peatones | OpenStreetMap (`highway=crossing`) | Automático | Alta |
| Carril bici | OpenStreetMap (`highway=cycleway`, `cycleway=lane/track`) | Automático | Alta en Barcelona |
| Carril bus | OpenStreetMap (`busway`, `lanes:bus`) | Automático | Media — varias convenciones a la vez |
| Obras | Open Data Barcelona, dataset "Obres a l'espai públic", JSON, actualización diaria, gratis sin token | Automático | Alta en Barcelona ciudad — **sin cobertura en l'Hospitalet y otros municipios**, hueco conocido |
| Tus notas / dificultad de conducción | Tus waypoints del GPX (toque largo, como ya haces) | Manual | — |
| Correcciones a la capa OSM (algo que falta o está mal) | `corregir_infra.py`, corres tú el script, sin depender de mí | Manual, vía script | — |

Overpass API y Open Data Barcelona se consultan **una sola vez por clase**, al procesar el GPX, y el resultado se guarda como archivo fijo — nunca se piden en vivo cuando estás repasando, así funciona rápido y sin depender de que esos servicios estén disponibles en ese momento.

## 7. Script de ingesta (`scripts/nueva_clase.py`)

Lo corres tú, en el Mac, cada vez que terminas una clase:

```bash
python3 scripts/nueva_clase.py "ruta/al/archivo.gpx"
```

Pasos internos:
1. Parsear el GPX (puntos + timestamp real de cada uno + waypoints si los añadiste).
2. Detectar la(s) zona(s): comparar contra los 68 puntos de `points.json` por cercanía (igual que hicimos con la lista de Guillem, tolerancia 60m, misma que usamos entonces). Si no hay ningún punto del catálogo cerca (como pasó hoy con "zona franca"), el script te pregunta el nombre a mano.
3. Pedir a Overpass (OpenStreetMap) la infraestructura del área de esa ruta.
4. Pedir a Open Data Barcelona las obras activas/recientes de esa área.
5. Escribir `<id>.json`, `<id>-osm.json`, `<id>-obras.json`, y actualizar `index.json`.
6. `git add` + `commit` + `push` → GitHub Pages publica solo, normalmente en 1-2 minutos.

**Manejo de errores**: si Overpass u Open Data Barcelona no responden, la clase se guarda igual, pero esa capa queda marcada explícitamente como "no disponible esta vez" — nunca se deja vacía sin explicación, para no confundir "no hay nada aquí" con "no lo pudimos comprobar".

## 8. Script de corrección (`scripts/corregir_infra.py`)

Para cuando OSM tiene algo mal o falta algo y tú lo ves en la calle:

```bash
python3 scripts/corregir_infra.py
```

Flujo: te pregunta qué clase/track, qué tipo de elemento, la ubicación (puedes pegar un link de Google Maps o las coordenadas), y una nota opcional. Escribe `<id>-overrides.json` y publica. Independiente de mí — lo corres cuando quieras.

## 9. Despliegue

GitHub Pages, sirviendo desde `public/`. Gratis, sin login para verla (solo con el link), sin nombre de tu compañero ni contenido interno.

**Corrección durante la implementación (2026-09-22)**: GitHub Pages en modo "Deploy from a branch" solo permite servir desde `/` o `/docs`, no desde una carpeta arbitraria como `/public` — esto se descubrió al intentar activarlo, no se había verificado antes de escribir la spec. Se usó en su lugar el modo "GitHub Actions" (`.github/workflows/pages.yml`), que sí publica cualquier carpeta — `public/` sigue siendo la única que se publica, `docs/` (specs y planes) sigue sin publicarse. Repo: https://github.com/IlaKan/examen-carnet-b — sitio: https://ilakan.github.io/examen-carnet-b/

## 10. Primera prueba real

En cuanto esté montado, el primer test es reprocesar el GPX de hoy ("zona franca") por el pipeline nuevo — ya sabemos qué esperar (zona sin match en el catálogo, pregunta manual de nombre, track visible con animación) porque ya lo vimos a mano.

## 11. Huecos y riesgos conocidos (dicho explícitamente, no escondido)

- Obras: sin cobertura fuera de Barcelona ciudad.
- Stops / cedas / carril bus de OSM: cobertura "media", puede faltar alguno — por eso existe `corregir_infra.py`.
- La numeración/nombre coloquial de zonas ("Les Corts", "Zona Franca") sigue sin resolverse con la autoescuela — este proyecto no lo arregla, solo lo documenta mejor (ver CLAUDE.md).
- El animado usa el timestamp real del GPX tal cual, sin suavizar — si el GPS dio un salto raro en algún punto, se verá en la reproducción tal cual pasó, no se oculta.
