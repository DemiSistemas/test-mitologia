# Test de mitología — Demigods ARG

Aplicación independiente de Streamlit.

## Archivos
- `app.py`: cuestionario, puntuación, ranking y guardado en Supabase.
- `requirements.txt`: dependencias.

## Secrets de Streamlit
En la app de Streamlit Community Cloud: **Settings → Secrets**. Usá las credenciales del proyecto de Supabase, no las subas a GitHub:

```toml
SUPABASE_URL = "https://TU-PROYECTO.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "TU_CLAVE_SECRETA"
```

Si una clave se expuso, revocala y generá otra. No la pegues en el código ni en el repositorio.

## Revisar el nombre de la columna
El código usa tabla `campistas`, columna del número `cirse` y columna de mitología `mitologia`. Confirmá el nombre técnico exacto en Supabase. Si es diferente, modificá esta constante al comienzo de `app.py`:

```python
MITOLOGIA_COLUMN = "mitologia"
```

El campo debe estar vacío o ser NULL antes de completar el test. El código actualiza únicamente esa columna de la fila cuyo `cirse` coincide.

## Subir a GitHub y desplegar
1. Descomprimí el ZIP.
2. Subí la carpeta `test-mitologia` a tu repositorio compartido.
3. En Streamlit Community Cloud creá una nueva app desde ese repositorio y configurá **Main file path** como `test-mitologia/app.py`.
4. Agregá los Secrets de Streamlit.
5. Probá con un número de Circe de prueba que exista y tenga la columna de mitología vacía.

## Empates
El orden fijo de desempate es: Griega, Romana, Nórdica, Egipcia. Los puntajes nunca se muestran; se presenta el ranking y el campista elige cuál guardar.
