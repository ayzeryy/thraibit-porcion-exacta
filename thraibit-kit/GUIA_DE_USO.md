# ThraiBit — kit de marca para el hackathon

## Marca

- Equipo y marca: **ThraiBit**. Conservar la T y la B mayúsculas.
- Producto: **Porción Exacta**.
- Firma: **Porción Exacta, por ThraiBit**.
- Eslogan: **Cada porción cuenta.**
- Descripción: Control de porciones durante la preparación y conciliación de ingredientes al cierre del servicio.

## Qué archivo usar

| Destino | Archivo o carpeta |
|---|---|
| App o web sobre fondo claro | logos/thraibit-color.svg |
| App o web sobre fondo oscuro | logos/thraibit-blanco.svg |
| Nombre del producto en la app | logos/porcion-exacta.svg |
| PowerPoint, Canva, Figma | SVG para escalar; PNG si la plataforma no acepta SVG |
| Portada y cierre de diapositivas | presentacion/ |
| README de GitHub | social/github-banner-1280x640.png |
| Vista previa de enlaces | social/og-image-1200x630.png |
| Avatar de equipo | social/avatar-1080.png |
| Miniatura de video | video/miniatura-demo-1920x1080.png |
| Rótulo sobre video | video/rotulo-1920x240.png, transparente |
| Favicon e iconos instalables | app/ |
| Iconos de interfaz | ui/ |
| Colores para código | brand-tokens.css |

## Colores

| Color | HEX | Función |
|---|---|---|
| Azul oscuro | #142B3B | Texto, marca, navegación y fondos oscuros |
| Menta | #42D6B0 | Acentos, botones y confirmación |
| Blanco cálido | #F7F6F2 | Superficies y texto invertido |
| Ámbar | #F2B544 | Atención y ajustes pendientes |
| Rojo funcional | #B42318 | Errores; complemento de interfaz |

Usar texto azul oscuro sobre menta o ámbar. Evitar texto blanco pequeño sobre esos colores. Las alertas deben incluir palabras o iconos, no depender solo del color.

## Tipografía y construcción

Inter es la propuesta para la interfaz; se puede usar system-ui si no está instalada. Los archivos entregados usan letras convertidas a curvas desde DejaVu Sans para que sean portables: no requieren instalar fuentes ni las redistribuyen. Los SVG contienen vectores reales y no imágenes incrustadas. Son una reconstrucción vectorial limpia de la propuesta visual, con ajustes de tipografía y geometría para uso consistente; no un calco exacto de la imagen conceptual.

## Reglas rápidas

- Mantener las proporciones. No estirar ni añadir sombras al logo.
- Dejar un margen libre mínimo equivalente a la altura de la T alrededor del lockup al colocarlo junto a otros elementos.
- Para tamaños pequeños usar el símbolo o favicon, sin eslogan.
- Logo horizontal recomendado desde 180 px de ancho; eslogan desde 360 px.
- Los PNG de logos y símbolos tienen transparencia. Las portadas y banners incluyen fondo.
- Las portadas son imágenes de marca, no una presentación completa ni capturas de una aplicación funcional.
- No se incluyen logos de patrocinadores ni sellos que impliquen premio o aval oficial.

## Instalación web

Copiar el contenido del kit dentro de public/brand/ y agregar:

```html
<link rel="icon" href="/brand/app/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/brand/app/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="/brand/app/apple-touch-icon.png">
<link rel="manifest" href="/brand/app/site.webmanifest">
<meta name="theme-color" content="#142B3B">
```

El manifest asume esas rutas y start_url=/; ajustarlas si la app vive en un subdirectorio. Para Open Graph, usar la URL pública absoluta de social/og-image-1200x630.png.

## Mensaje de presentación

Somos ThraiBit. Creamos Porción Exacta para ayudar a los restaurantes a servir cantidades consistentes y explicar las diferencias de inventario al cerrar cada turno.
