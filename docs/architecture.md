# Arquitectura inicial

Musubi separa cuatro capas deliberadamente pequeñas:

1. **CLI**: selecciona un perfil, valida entradas y renderiza un proyecto.
2. **Perfiles**: decisiones de entorno versionadas como TOML.
3. **Plantillas**: Zato 4.1, Enmasse, Caddy, servicios y operación.
4. **Proyecto generado**: artefacto autónomo que no depende del CLI en runtime.

El nudo de la marca también describe la arquitectura: las entradas pueden ser
sistemas, APIs o IA, pero la política, observabilidad y operación convergen en
un punto de integración controlado por Zato.

## Límites de esta versión

- La plantilla proporciona una base, no sustituye el diseño de alta
  disponibilidad del clúster Zato.
- El perfil `prod` exige fijar la imagen por digest al ejecutar validación
  estricta: `musubi validate . --strict`.
- Enmasse es la fuente versionada; cualquier cambio realizado en la UI debe
  exportarse y revisarse antes del despliegue.
