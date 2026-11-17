# AnimeChronicle

**El universo anime en un solo lugar.** Portal de noticias de anime con estética neón/otaku,
animaciones y efectos de sonido. Es el hermano de `Web-Noticias`, adaptado por completo
al contenido otaku: estrenos, series, películas, manga, videojuegos, eventos y comunidad,
con pestañas por género (shōnen, shōjo, isekai, mecha…).

- **Web:** https://mcad76.github.io/AnimeChronicle/
- **Repositorio:** https://github.com/Mcad76/AnimeChronicle

## Características

- **Portada visual:** hero con destacadas, rejillas por sección y tarjetas con brillo,
  elevación y entrada escalonada al cargar.
- **Radar de tendencias arriba del todo:** dos paneles enfrentados con lo más visto en España y en el mundo, calculado a partir de las menciones a franquicias en las noticias.
- **Pestañas por género:** cambia de shōnen a isekai y toda la portada se regenera al instante.
- **Páginas separadas:** el **archivo de noticias** (`archivo.html`) y el **glosario otaku** (`glosario.html`) tienen su propia página, con búsqueda, filtros y navegación propia.
- **Glosario otaku:** **225 términos clasificados en 10 categorías** (géneros, formatos, producción, arquetipos, poderes, jerga, cultura, expresiones, eventos y merchandising).
- **Sin publicidad:** los espacios de anuncios se han eliminado y se volverán a añadir cuando haya suficientes lectores.
- **Rejilla de tamaños mixtos:** una noticia grande y dos pequeñas por sección, como un diario, con ancho uniforme y adaptación a móvil.
- **Tipografía:** Chakra Petch para titulares y Barlow para el cuerpo, con Noto Sans JP para los kanjis.
- **Fondos y animaciones con personajes míticos originales** (arte vectorial propio, sin copyright):
  **28 héroes originales** (guerrero, espadachina, ninja, maga, mecha, samurái, pirata,
  cazador, bruja, cyborg, astronauta, gamer, vampiro, sirena, fénix…). Caen, suben y
  derivan por la pantalla con 4 peinados y 7 armas distintas, en lugar de flores o lunas,
  sobre un fondo de estrellas y escaneo CRT con logo de efecto glitch.
- **Golpe de ataque al abrir noticia:** aparece un personaje al azar que ejecuta su
  movimiento insignia con destello, sacudida de pantalla y un grito mítico
  (¡Rasengan!, ¡Bankai!, ¡Kamehameha!, ¡Ataque de los Titanes!…).
- **Voces otaku en lugar de pitidos:** cada pulsación dice una frase de anime mediante
  la voz del navegador (con respaldo WAV si no está disponible). Bucle synth opcional
  con ♪. Todo se puede silenciar con 🔊/🔇 y se recuerda la preferencia.
- **Vibración** en móvil al seleccionar noticias (cuando el dispositivo lo permite).
- **Todas las noticias llevan foto real**: se obtiene de la `og:image` del artículo o
  de la carátula oficial vía AniList. Se detecta y descarta el logotipo de Google News
  (que aparece cuando el artículo no tiene imagen) y se sustituye por la carátula del
  anime, película o juego del que habla la noticia.
- **Buscador** en portada y en el archivo, filtro por sección y contador de visitas.
- **SEO completo:** una página HTML real e indexable por noticia, JSON-LD `NewsArticle`,
  metadatos Open Graph y Twitter, `canonical`, `sitemap.xml` y `robots.txt`.
- **Enlazado interno** de 3 artículos relacionados y botones para compartir en
  WhatsApp, Telegram, X y Facebook.
- **Señales de respeto:** `prefers-reduced-motion` desactiva las animaciones para
  usuarios que lo piden, y el audio nunca se reproduce automáticamente.

## Noticias reales, actualizadas cada día

El portal **no depende del móvil**: un GitHub Action ejecuta `actualizar_noticias.py`
cada día a las 07:30 UTC. El script consulta fuentes RSS públicas:

- Anime News Network
- MyAnimeList
- Google News (español) por género y sección
- Bing News como respaldo con imagen

Clasifica cada noticia en sección y género, calcula una puntuación de relevancia,
descarga las fotos y regenera el archivo, las páginas estáticas y el sitemap.
Las noticias antiguas se conservan 45 días en `datos/historico.json`.

### Actualizar a mano

En la pestaña **Actions** → *Actualizar noticias* → **Run workflow**.

Si quieres añadir una noticia propia, edita `datos/noticias-manuales.json` en GitHub:

```json
{
  "noticias": [
    {
      "titulo": "Título de la noticia",
      "entradilla": "Resumen corto.",
      "cuerpo": ["Párrafo 1.", "Párrafo 2."],
      "sec": "estrenos",
      "genero": "shonen",
      "link": "https://...",
      "medio": "Redacción propia"
    }
  ]
}
```

Secciones válidas: `estrenos`, `series`, `peliculas`, `manga`, `videojuegos`, `eventos`, `comunidad`.
Géneros válidos: `todos`, `shonen`, `shojo`, `isekai`, `mecha`, `fantasia`, `accion`,
`romance`, `comedia`, `terror`.

### Publicar en GitHub Pages

**Settings → Pages → Source: Deploy from a branch → main → /(root) → Save.**
El archivo `.nojekyll` evita que GitHub ignore carpetas como `js/`.

> El repo debe ser público para usar GitHub Pages en el plan gratis.

## Estructura

```
AnimeChronicle/
├── .github/workflows/actualizar-noticias.yml   actualización diaria en la nube
├── actualizar_noticias.py                      descarga, clasifica y genera todo
├── generar_recursos.py                         crea sonidos WAV, fondos y personajes SVG
├── index.html                                  portada (radar, hero y secciones)
├── archivo.html                                archivo de noticias
├── glosario.html                               glosario otaku
├── css/styles.css                              tema neón + animaciones
├── js/
│   ├── news-data.js                            banco de noticias (generado)
│   ├── glosario.js                             225 términos clasificados
│   ├── sonidos.js                              motor de audio
│   ├── efectos.js                              personajes flotantes y ataque (páginas secundarias)
│   ├── archivo.js                              lógica del archivo
│   ├── glosario-page.js                        lógica del glosario
│   └── app.js                                  lógica de la portada
├── fondos/                                     estrellas, sakura, personajes y respaldos
├── sonidos/                                    efectos y BGL sintetizados
├── imagenes/                                   fotos de las noticias
├── noticias/                                   una página HTML por noticia
├── datos/
│   ├── historico.json                          histórico (generado)
│   └── noticias-manuales.json                  noticias escritas a mano
├── sitemap.xml / robots.txt                    SEO (generados)
└── README.md
```

Para regenerar los recursos visuales y sonoros:

```bash
python3 generar_recursos.py
```

## Pendiente de tu parte

- **Dominio propio**: comprarlo y añadir un `CNAME` en la raíz + configurarlo en
  Settings → Pages.
- **Canales de difusión**: crea el servidor de Discord / canal de Telegram y pon
  los enlaces en el diccionario `CANALES` de `actualizar_noticias.py`; mientras
  estén vacíos no se muestra el bloque «Únete a la comunidad».
- **Search Console**: registra la web y envía el `sitemap.xml` para acelerar la
  indexación.

## Cómo verlo

Publicado en **https://mcad76.github.io/AnimeChronicle/**

Solo para probar en local:

```bash
python3 -m http.server 8000
# y abre http://localhost:8000
```
