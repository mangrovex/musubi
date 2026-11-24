# Musubi

![Musubi](assets/brand/musubi-mark.png)

**Musubi** (結び) significa “nudo” o “unión”: sistemas, APIs e IA distintos
confluyen en un solo punto, se conectan de forma explícita y conservan su
identidad. El framework ofrece un punto de partida reproducible para proyectos
de integración sobre **Zato 4.1**.

## Inicio rápido

```bash
python -m pip install -e .
musubi profiles
musubi init pagos --profile dev --output ./pagos
musubi validate ./pagos
cd pagos && cp .env.example .env && docker compose up -d
```

## Qué incluye

- CLI sin dependencias de ejecución: `init`, `profiles`, `validate` y `doctor`.
- Plantilla Docker Compose con Zato 4.1 y Caddy.
- Configuración Enmasse y servicio inicial de salud.
- Perfiles `dev`, `stage` y `prod` con políticas progresivas.
- Sitio estático de presentación en `site/` y workflow de GitHub Pages.
- CI para Python 3.11/3.12, render de los tres perfiles y validación del sitio.

## Perfiles

| Perfil | Uso | TLS | Réplicas | Política de imagen |
|---|---|---:|---:|---|
| `dev` | desarrollo local | interno | 1 | etiqueta Zato 4.1 |
| `stage` | preproducción | automático | 1 | etiqueta configurable |
| `prod` | producción | automático | 2 | digest obligatorio con `--strict` |

Las plantillas fijan `zatosource/zato-4.1:latest` como valor inicial. En
producción debe reemplazarse por una referencia inmutable con digest.

## Estado

Estructura inicial `0.1.0`. La licencia aún debe ser elegida por el propietario
antes de publicar el paquete para terceros.
