# Mensobot

Mensobot es un bot de Discord que interactúa con la API de Google para chatear con un simpático "gatito menso". Este bot se creó principalmente para entretener y hablar un rato con amigos. Es un proyecto sencillo hecho "por los jajas" y no tiene todas las funcionalidades posibles debido a la falta de interés en implementarlas.

## Características

- **Chat con Mensobot**: Usa el comando `!chat` para hablar con Mensobot.
- **Chat con Gemini**: Usa el comando `!gemini` para hablar con un modelo de chat sin personalidad.
- **Cambio de modelo**: Usa el comando `!modelo` para cambiar entre distintos modelos de Google API.
- **Lista de chats activos**: Usa el comando `!lista` para ver los chats activos.
- **Continuar chat**: Usa el comando `!continuar` para retomar un chat anterior.
- **Comandos adicionales**: `!comandos` para ver todos los comandos disponibles y `!ping` para probar la conexión.

## Instalación

1. Clona este repositorio.

   ```bash
   git clone https://github.com/tuusuario/mensobot.git
   cd mensobot
   ```
2. Instala las dependencias necesarias.

   ```bash
   pip install discord.py google-api-python-client
   ```
3. Configura las constantes en `Constants.py` con tus claves API y otros valores necesarios.

   ```python
   google_API_key = "TU_CLAVE_DE_API"
   discord_token = "TU_TOKEN_DE_DISCORD"
   canalChat = ID_DEL_CANAL_CHAT
   canalTest = ID_DEL_CANAL_TEST
   mensaje_ayuda = "Mensaje de ayuda personalizado"
   mensobot_prompt = "Prompt personalizado para Mensobot"
   etc...
   ```
4. Ejecuta el bot.

   ```bash
   python mensobot.py
   ```

## Uso

### Comandos principales

- `!chat`: Inicia un chat con Mensobot.
- `!gemini`: Inicia un chat con el modelo Gemini.
- `!modelo`: Cambia el modelo de chat. Opciones disponibles:
  - `1`: gemini-1.0-pro-latest (Básico)
  - `2`: gemini-1.5-flash-latest (Rápido)
  - `3`: gemini-1.5-pro-latest (Potente)
- `!continuar`: Continúa un chat que se haya cerrado.
- `!lista`: Muestra los chats activos.
- `!comandos`: Muestra la lista de comandos disponibles.
- `!ping`: Prueba de conexión.
- `!ayuda`: Envía un mensaje de ayuda al usuario.

### Nota importante

- Mensobot no puede ver ni enviar imágenes debido a la falta de interés en implementar esta funcionalidad.
- Los filtros de contenido están desactivados, lo que permite hacer chistes con amigos sin que la IA filtre contenido ofensivo.

## Contribución

Este proyecto es solo por diversión y no se busca optimizar ni mejorar el código en su estado actual. Sin embargo, siéntete libre de forkearlo y hacer tus propias modificaciones.

## Referencias

- [Documentación de la API de Google Gemini](https://ai.google.dev/gemini-api/docs/get-started/tutorial?lang=python&hl=es-419)
