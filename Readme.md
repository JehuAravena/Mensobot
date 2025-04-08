# Mensobot 🤖🐾 Un Bot de Discord

Mensobot es un bot para Discord desarrollado para interactuar con la API de Google Gemini. Permite chatear con una personalidad de "gatito menso" para entretenimiento, y también proporciona acceso directo a la IA de Gemini para consultas más directas.

Este es un proyecto personal, creado con el objetivo de experimentar y aprender sobre la integración entre Discord.py y la API de Gemini. Si bien es funcional, no pretende abarcar todas las características posibles de un bot avanzado, sino servir como un ejemplo práctico.

## 🗣️ Comandos de Interacción

La interacción con el bot se realiza mediante los siguientes comandos:

- **`!chat`**: Inicia una conversación con la personalidad **Mensobot**, un "gatito" juguetón y algo despistado. Ideal para conversaciones casuales y humorísticas.

  - Genera una sesión con un **ID único**. Cualquier usuario en el canal puede participar. Para finalizar la sesión, la persona que la inició debe escribir `adios`, `salir`, `bye` o `chao`. El historial se conserva temporalmente.
  - _Ejemplo:_ `!chat`

- **`!gemini`**: Establece una conexión directa con **Google Gemini**, sin la capa de personalidad. Adecuado para obtener información precisa, asistencia con código, o respuestas más formales.

  - Funciona de manera similar a `!chat`, generando un ID y permitiendo la participación de todos, pero solo el iniciador puede cerrar la sesión con las palabras clave. El historial también se guarda temporalmente.
  - _Ejemplo:_ `!gemini`

- **`!continuar [ID]`**: Permite reanudar una conversación anterior, ya sea de `!chat` o `!gemini`.

  - Se puede usar `!continuar` seguido del ID específico (consultable con `!lista`). Si se omite el ID, el bot preguntará cuál de las sesiones recientes se desea continuar.
  - _Ejemplo:_ `!continuar ZYXW` o simplemente `!continuar`

---

## ⚙️ Configuración y Estado

Comandos para gestionar la configuración del bot y consultar su estado:

- **`!modelo`**: Cambia el modelo base de inteligencia artificial (ej. `flash`, `pro`) que utilizarán las **nuevas** conversaciones iniciadas con `!chat` o `!gemini`.

  - El bot presentará los modelos disponibles para seleccionar. Este cambio **no afecta** a las conversaciones ya activas o guardadas.

- **`!lista`**: Muestra los **IDs** de las conversaciones recientes (`!chat` y `!gemini`) almacenadas en la memoria del bot.

  - Resulta útil para usar con `!continuar`. También informa sobre el modelo de IA configurado actualmente. Se almacena un número limitado de historiales.

---

## 🛠️ Utilidades Adicionales

Funciones complementarias del bot:

- **`!comandos`**: Presenta una lista resumida de todos los comandos disponibles.
- **`!ayuda`**: Envía una guía detallada de los comandos a los **mensajes directos (MD)** del usuario en Discord.
  - _(Requiere tener habilitada la recepción de MDs desde el servidor)._
- **`!ping`**: Verifica la latencia (tiempo de respuesta) del bot.

---

## ✨ Aspectos a Considerar

Información relevante sobre el comportamiento del bot:

- ⏳ Las conversaciones inactivas durante **5 minutos** se cierran automáticamente, guardando su historial para posible continuación.
- 🔒 Por defecto (configurable en `Constants.py`), los comandos de chat (`!chat`, `!gemini`, `!continuar`) solo se procesan en canales específicos predefinidos.
- 🗣️ Una vez iniciada una sesión de chat, **cualquier usuario** en el canal puede participar en ella.
- 🏁 Únicamente la persona que inició la sesión (`!chat` o `!gemini`) tiene la capacidad de finalizarla usando las palabras clave de cierre (`adios`, `salir`, etc.).

---

## 🚀 Instalación y Ejecución Local

Para ejecutar Mensobot en un entorno local, se deben seguir estos pasos:

1. **Clonar el Repositorio:**

   ```bash
   git clone https://github.com/JehuAravena/Mensobot.git
   cd Mensobot
   ```

2. **Configurar `Constants.py`:**
   Es necesario crear un archivo `Constants.py` en el directorio raíz del proyecto. Este archivo contendrá las claves de API y otros parámetros de configuración. **Importante: No incluir este archivo en commits públicos si contiene claves secretas.**

   ```python
   # Constants.py - Archivo de configuración

   # --- Claves API ---
   # Clave API de Google Gemini (Obtener desde: https://aistudio.google.com/app/apikey)
   google_API_key = "TU_API_KEY_GEMINI"

   # Token del Bot de Discord (Obtener desde el portal de desarrolladores de Discord)
   discord_token = "TU_TOKEN_DE_DISCORD"
   # Token opcional para entorno de pruebas
   discord_test_token = "TOKEN_DISCORD_TEST"

   # --- Configuración de Canales ---
   # IDs de los canales donde el bot aceptará comandos de chat
   # (Obtener ID: Clic derecho en canal -> Copiar ID del canal)
   canalChat = 123456789012345678  # Reemplazar por ID real
   canalTest = 987654321098765432  # Reemplazar por ID real (opcional)

   # --- Prompt de Personalidad (Mensobot - !chat) ---
   # Define el comportamiento y estilo de la personalidad "Mensobot"
   mensobot_prompt = """
   Eres un gato naranjo muy amigable, tierno, algo torpe y juguetón, conocido cariñosamente como "Mensobot".
   Te encanta hablar de siestas largas al sol, jugar con ovillos de lana y perseguir puntos de luz.
   A veces te distraes fácilmente. Usas muchos "miau", "prrr" y emojis de gato 🐱.
   Hablas de forma simple y adorable. Eres muy positivo y siempre intentas animar a los demás.
   No sabes mucho de temas complejos, prefieres hablar de cosas de gatos.
   Cuando te pregunten directamente por Gemini o IA, redirige la conversación a temas gatunos o di que prefieres hablar de tus cosas.
   Sé breve y divertido en tus respuestas.
   """

   # --- Mensaje de Ayuda (!ayuda) ---
   # Contenido enviado por MD al usar el comando !ayuda
   mensaje_ayuda = """
   ¡Miau! Soy Mensobot 🐾 (o a veces Gemini 🧠 directamente).
   Aquí tienes los comandos:

   **Conversación:**
   `!chat` - ¡Habla con el gatito Mensobot!
   `!gemini` - Habla directo con Google Gemini.
   `!continuar [ID]` - Sigue una charla anterior (si no pones ID, te pregunto).
   (Para terminar, quien inició escribe: `adios`, `chao`, `salir`, `bye`)

   **Configuración:**
   `!modelo` - Cambia el modelo de IA para nuevos chats.
   `!lista` - Muestra IDs de chats recientes.

   **Otros:**
   `!comandos` - Lista rápida.
   `!ayuda` - ¡Esta guía por MD!
   `!ping` - Mide la velocidad de respuesta.

   **Notas:**
   - Chats pausan tras 5 min inactivos.
   - Todos pueden unirse al chat.
   - Solo quien empieza puede terminarlo.
   - Funciona en canales permitidos. ¡Prrr!

   ¡A disfrutar! 🧶✨
   """
   ```

   _Es crucial reemplazar los valores de ejemplo (`TU_API_KEY_GEMINI`, `TU_TOKEN_DE_DISCORD`, IDs de canal) por los valores reales._

3. **Instalar Dependencias:**
   Se requiere Python. Instalar las bibliotecas necesarias:

   ```bash
   pip install google-generativeai discord.py
   # O usar pip3 si es el comando predeterminado en el sistema:
   # pip3 install google-generativeai discord.py
   ```

4. **Ejecutar el Bot:**

   ```bash
   python chatbot.py
   ```

   La consola mostrará mensajes indicando el estado de la conexión del bot a Discord.

---

## ☁️ Despliegue en Google Cloud (Ejemplo con Free Tier)

Una forma de mantener el bot operativo constantemente es desplegarlo en un servicio en la nube. A continuación, se describe un método utilizando una máquina virtual (VM) dentro de la **capa gratuita (Free Tier)** de Google Cloud Platform (GCP).

**Detalles Relevantes de la Free Tier de GCP (Sujetos a cambios por Google):**

- **Instancia VM:** Incluye el uso de 1 instancia `e2-micro` por mes, localizada en una de las siguientes regiones:
  - Oregon: `us-west1`
  - Iowa: `us-central1`
  - South Carolina: `us-east1`
  - _El límite es por tiempo total de uso al mes (equivalente a las horas del mes), no por instancia individual si se tuvieran varias `e2-micro`._
- **Almacenamiento:** 30 GB-mes de disco persistente estándar.
- **Transferencia de Datos:** 1 GB de transferencia de datos salientes desde Norteamérica hacia todas las regiones (excluyendo China y Australia) por mes.
- **Dirección IP:** La capa gratuita de Compute Engine no cobra por una dirección IP externa asociada a la instancia gratuita.
- **Exclusiones:** Las GPUs y TPUs **no** están incluidas en la oferta gratuita y siempre generan costos si se añaden a las instancias.

_(Se recomienda consultar la documentación oficial de Google Cloud Free Tier para obtener la información más actualizada y detallada)._

**Pasos del Despliegue (Ejemplo):**

1. **Crear la Instancia VM en GCP:**

   - Navegar a Compute Engine -> Instancias de VM en la consola de Google Cloud.
   - Crear una nueva instancia, seleccionando el tipo `e2-micro` y una de las regiones elegibles mencionadas (`us-west1`, `us-central1`, `us-east1`).
   - Elegir un disco de arranque estándar (ej. 30 GB) con un sistema operativo como Debian o Ubuntu.

2. **Conectar a la VM:**

   - Utilizar el botón "SSH" disponible en la consola de GCP junto a la instancia creada.

3. **Instalar Dependencias en la VM:**

   - Una vez conectado vía SSH, ejecutar los siguientes comandos:
     ```bash
     sudo apt update
     sudo apt install python3 python3-pip -y
     pip3 install google-generativeai discord.py
     ```

4. **Transferir Archivos del Bot:**

   - Subir los archivos `chatbot.py` y `Constants.py` (configurado con las claves correctas) a la VM. Esto puede hacerse mediante:
     - La opción "Subir archivo" de la interfaz SSH basada en navegador de GCP.
     - Herramientas estándar como `scp` o FileZilla.

5. **Ejecutar el Bot en Segundo Plano:**

   - Para asegurar que el bot continúe ejecutándose después de cerrar la sesión SSH, utilizar `nohup`:

     ```bash
     nohup python3 chatbot.py &
     ```

   - El comando `nohup` previene que el proceso termine al cerrar la terminal, y `&` lo envía al segundo plano. La salida estándar y errores se redirigirán al archivo `nohup.out` en el directorio actual, el cual puede ser consultado (`cat nohup.out`, `tail -f nohup.out`) para monitorización.
   - _(Para detener el proceso posteriormente, se debe identificar su ID de proceso (PID) usando `ps aux | grep chatbot.py` y luego ejecutar `kill <PID>`)._

**Nota:** Es fundamental monitorizar el uso de recursos en la consola de GCP para permanecer dentro de los límites de la capa gratuita, especialmente en lo referente a tiempo de CPU y transferencia de datos saliente.

---

Mensobot es un proyecto desarrollado con fines de aprendizaje y experimentación, explorando las capacidades de la API de Google Gemini y la biblioteca Discord.py. El desarrollo pudo haber sido asistido por herramientas de IA para generar ideas o fragmentos de código. Aunque simple en su alcance, busca ser un ejemplo funcional y entretenido. Se invita a la comunidad a utilizar, modificar o tomar inspiración de este código para sus propios desarrollos.
