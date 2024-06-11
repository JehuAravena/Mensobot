import google.generativeai as genai
import time as t
import Constants
import textwrap
import pathlib
import discord
import asyncio
import codecs
import random
import string

from discord.ext import commands

genai.configure(api_key=Constants.google_API_key)
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 1048576,
    "response_mime_type": "text/plain",
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]
model = genai.GenerativeModel(
    model_name="gemini-1.0-pro-latest",
    safety_settings=safety_settings,
    generation_config=generation_config,
)

chateando = False
testmode = False
canalChat = Constants.canalChat
canalTest = Constants.canalTest
respuestaLargaTxt = "respuestaLarga.txt"
despedidas = ["adios", "adiós"]
chats = {}
orden_chats = []

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

if pathlib.Path(__file__).name == "chatbot_test.py":
    testmode = True

if testmode:
    print("DEBUG: Modo test activado")
else:
    print("DEBUG: Modo test desactivado")


def cambiar_modelo(modelo):
    if modelo == "1":
        model = genai.GenerativeModel(
            model_name="gemini-1.0-pro-latest",
            safety_settings=safety_settings,
            generation_config=generation_config,
        )
    elif modelo == "2":
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest",
            safety_settings=safety_settings,
            generation_config=generation_config,
        )
    elif modelo == "3":
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro-latest",
            safety_settings=safety_settings,
            generation_config=generation_config,
        )
    return model


def gen_id_chat():
    while True:
        car = string.ascii_uppercase + string.digits
        id_chat = "".join(random.choices(car, k=4))
        if len(chats) >= 8:
            chat_viejo = orden_chats.pop(0)
            del chats[chat_viejo]
        if id_chat not in chats:
            chats[id_chat] = []
            orden_chats.append(id_chat)
            print(f"DEBUG: Se creó un chat con ID: {id_chat}")
            return id_chat


# ---------------------------- Eventos ----------------------------


@bot.event
async def on_ready():
    print(f"DEBUG: Bot listo como {bot.user.name} - {bot.user.id}")


@bot.command()
async def ping(ctx):
    print(f"DEBUG: Comando ping ejecutado por {ctx.author}")
    await ctx.send("Pong!")


@bot.command()
async def ayuda(ctx):
    print(f"DEBUG: Comando ayuda ejecutado por {ctx.author}")
    try:
        await ctx.author.send(Constants.mensaje_ayuda)
        await ctx.send("`Mensaje de ayuda enviado`")
    except Exception as e:
        print(f"DEBUG: se detectó un error en el comando ayuda")
        print(f"DEBUG: {e}")
        await ctx.send("`No se pudo enviar el mensaje de ayuda`")


@bot.command()
async def lista(ctx):
    print(f"DEBUG: Comando lista ejecutado por {ctx.author}")
    try:
        if len(chats) == 0:
            await ctx.send("`No hay chats activos`")
            return
        mensaje = "Chats activos: \n"
        for chat in orden_chats:
            mensaje += "`" + chat + "`\n"
        await ctx.send(mensaje)
    except Exception as e:
        print(f"DEBUG: se detectó un error en el comando lista")
        print(f"DEBUG: {e}")
        await ctx.send("`No se pudo mostrar la lista de chats`")


@bot.command()
async def comandos(ctx):
    print(f"DEBUG: Comando comandos ejecutado por {ctx.author}")
    try:
        await ctx.send("Los comandos disponibles son:")
        await ctx.send(
            """
                        `!chat` - Inicia un chat con Mensobot
                        `!gemini` - Inicia un chat con Gemini
                        `!continuar` - Continúa un chat que se haya cerrado
                        `!modelo` - Cambia el modelo de chat
                        `!lista` - Muestra los chats activos
                        `!comandos` - Muestra esta lista de comandos
                        `!ping` - Prueba de conexión
                        `!ayuda` - Un pequeño tutorial para usar el bot
            """
        )
    except Exception as e:
        print(f"DEBUG: se detectó un error en el comando comandos")
        print(f"DEBUG: {e}")
        await ctx.send("No se pudo mostrar la lista de comandos")


@bot.command()
async def modelo(ctx):
    print(f"DEBUG: Comando modelo ejecutado por {ctx.author}")
    try:
        canalLlamada = ctx.channel.id
        global model
        if chateando:
            await ctx.send(
                "`No puedes cambiar el modelo mientras un chat está en curso`"
            )
            return
        await ctx.send("Selecciona el modelo que deseas usar:")
        menu = await ctx.send(
            "```1. gemini-1.0-pro           (Básico) \n2. gemini-1.5-flash-latest  (Ágil) \n3. gemini-1.5-pro-latest    (Potente)```"
        )
        await ctx.send("`Modelo Actual: " + model.model_name + "`")
        while True:
            try:
                message = await bot.wait_for("message", timeout=60)
                if ctx.channel.id != message.channel.id:
                    print(
                        f"DEBUG: se detectó un mensaje en un canal distinto al llamado"
                    )
                    continue
                if ctx.author != message.author:
                    print(
                        f"DEBUG: se detectó un mensaje de un usuario distinto al llamado"
                    )
                    continue
                else:
                    if message.content not in ["1", "2", "3"]:
                        await menu.edit(content="`No se seleccionó ningún modelo`")
                        print(
                            f"DEBUG: se ingresó {message.content} en lugar de un modelo"
                        )
                        return
                    else:
                        print(f"DEBUG: Modelo seleccionado: {message.content}")
                        break
            except Exception as e:
                print(f"DEBUG: se detectó un error en el tiempo de espera")
                print(f"DEBUG: {e}")
                await menu.edit(content="`No se seleccionó ningún modelo`")
                return
        model = cambiar_modelo(message.content)
        await ctx.send("`Modelo cambiado con éxito`")
        print(f"DEBUG: Modelo cambiado a {model.model_name} por {ctx.author}")
    except Exception as e:
        print(f"DEBUG: se detectó un error en el comando modelo")
        print(f"DEBUG: {e}")
        await ctx.send("`No se pudo cambiar el modelo`")


@bot.command()
async def chat(ctx):
    print(f"DEBUG: Comando chat ejecutado por {ctx.author}")
    global chateando
    if ctx.channel.id != canalChat and ctx.channel.id != canalTest:
        await ctx.send(
            "`No puedes usar este comando en este canal, ve a`" + "<#" + canalChat + ">"
        )
        return
    try:
        if chateando:
            await ctx.send(Constants.mensobot_chateando)
            return
        print(f"DEBUG: Se inicializó mensobot para el usuario {ctx.author}")
        chat_id = gen_id_chat()
        await ctx.send("Chat iniciado con el ID: `" + chat_id + "`")
        mensaje = await ctx.send("*`Llamando al gatito...`*")
        chats[chat_id] = model.start_chat(history=[])
        chat = chats[chat_id]
        personalidad = Constants.mensobot_prompt
        print(f"DEBUG: se ha seteado la personalidad")
        try:
            await mensaje.edit(content=(chat.send_message(personalidad)).text)
        except Exception as e:
            print(f"DEBUG: se detectó un error en la respuesta")
            print(f"DEBUG: {e}")
            await ctx.send("`No se pudo iniciar el chat`")
            if "quota" in str(e):
                response = Constants.mensobot_init_quota
                await mensaje.edit(content=response)
                await ctx.send("`Chat cerrado`")
                chateando = False
                return
            return
        chateando = True
        while True:
            try:
                message = await bot.wait_for("message", timeout=300)
            except Exception as e:
                print(
                    f"DEBUG: se detectó un error en el tiempo de espera por parte del usuario"
                )
                print(f"DEBUG: {e}")
                await ctx.send("El chat ha sido cerrado por inactividad.")
                chateando = False
                break
            if message.author == ctx.author:
                if message.content.lower() in despedidas:
                    print(f"DEBUG: {ctx.author} cerró el chat")
                    mensaje = await ctx.send("*`Despidiéndose...` *:wave:")
                    await mensaje.edit(content=chat.send_message("despidete").text)
                    await ctx.send("Chat cerrado")
                    chateando = False
                    print(f"DEBUG: chat finalizado")
                    break
            try:
                if message.channel.id != (canalChat and canalTest):
                    continue
                if message.author == bot.user:
                    print(
                        f"DEBUG: el bot se detectó a si mismo {message.author} = {bot.user}"
                    )
                    continue
                else:
                    mensaje = await ctx.send(
                        "*`Pensando respuesta para "
                        + str(message.author)
                        + "...`*   :thinking:"
                    )
                    response = chat.send_message(
                        str(message.author) + " dice " + message.content
                    )
                    print(f"DEBUG: {message.author} envió un mensaje")
                    await mensaje.edit(content=response.text)
                    print(f"DEBUG: mensobot respondió")
            except Exception as e:
                print(f"DEBUG: se detectó un error en la respuesta")
                print(f"DEBUG: {e}")
                if "quota" in str(e):
                    response = Constants.mensobot_err_quota
                    await mensaje.edit(content=response)
                    await ctx.send("Chat cerrado")
                    chateando = False
                    break
                elif "fewer in length" in str(e):
                    f = codecs.open(respuestaLargaTxt, "w", "utf-8")
                    f.write(response)
                    f.close()
                    response = Constants.mensobot_err_length
                    await mensaje.edit(content=response)
                    await ctx.send(file=discord.File(respuestaLargaTxt))
                else:
                    response = Constants.mensobot_chat_err
                    await mensaje.edit(content=response)
    except Exception as e:
        print(f"DEBUG: se detectó un error en el comando chat")
        print(f"DEBUG: {e}")
        response = Constants.mensobot_crit_err
        chateando = False
        await ctx.send(response)


@bot.command()
async def gemini(ctx):
    print(f"DEBUG: Comando gemini ejecutado por {ctx.author}")
    global chateando
    print(f"DEBUG: Comando gemini")
    if ctx.channel.id != canalChat and ctx.channel.id != canalTest:
        await ctx.send(
            "`No puedes usar este comando en este canal, ve a`" + "<#" + canalChat + ">"
        )
        return
    print(f"DEBUG: Se inicializó gemini ai para el usuario {ctx.author}")
    try:
        if chateando:
            await ctx.send(
                "`No puedes iniciar un chat con gemini mientras un chat está en curso`"
            )
            return
        chat_id = gen_id_chat()
        await ctx.send("Chat iniciado con el ID: `" + chat_id + "`")
        mensaje = await ctx.send("*`Inicializando gemini...`*")
        chats[chat_id] = model.start_chat(history=[])
        chat = chats[chat_id]
        personalidad = """
                        Tu nombre es Gemini
                        Por favor responde con un saludo para comenzar
                        ahora mismo estás hablando con: """, str(
            ctx.author
        )
        print(f"DEBUG: se ha seteado la personalidad")
        try:
            await mensaje.edit(content=(chat.send_message(personalidad)).text)
        except Exception as e:
            print(f"DEBUG: se detectó un error en la respuesta")
            print(f"DEBUG: {e}")
            await ctx.send("`No se pudo iniciar gemini`")
            if "quota" in str(e):
                response = "Este modelo ha excedido su cuota de consultas, por favor, intenta mañana o cambia el modelo con `!modelo` para llamar a Gemini"
                await mensaje.edit(content=response)
                await ctx.send("`Chat cerrado`")
                chateando = False
                return
            return
        chateando = True
        while True:
            try:
                message = await bot.wait_for("message", timeout=300)
            except Exception as e:
                print(
                    f"DEBUG: se detectó un error en el tiempo de espera por parte del usuario"
                )
                print(f"DEBUG: {e}")
                await ctx.send("El chat ha sido cerrado por inactividad.")
                chateando = False
                break
            if message.author == ctx.author:
                if message.content.lower() in despedidas:
                    print(f"DEBUG: {ctx.author} cerró el chat")
                    mensaje = await ctx.send("*`Cerrando gemini...`*")
                    await mensaje.edit(content=chat.send_message("despidete").text)
                    await ctx.send("Chat cerrado")
                    chateando = False
                    print(f"DEBUG: chat finalizado")
                    break
            try:
                if message.channel.id != (canalChat and canalTest):
                    continue
                if message.author == bot.user:
                    print(
                        f"DEBUG: el bot se detectó a si mismo {message.author} = {bot.user}"
                    )
                    continue
                else:
                    mensaje = await ctx.send(
                        "*`Generando respuesta para "
                        + str(message.author)
                        + "...`*   :hourglass_flowing_sand:"
                    )
                    response = (
                        chat.send_message(
                            str(message.author) + " dice " + message.content
                        )
                    ).text
                    print(f"DEBUG: {message.author} envió un mensaje")
                    await mensaje.edit(content=response)
                    print(f"DEBUG: gemini ai respondió")
            except Exception as e:
                print(f"DEBUG: se detectó un error en la respuesta")
                print(f"DEBUG: {e}")
                if "quota" in str(e):
                    response = "La cuota de consultas se ha excedido, por favor, intenta mañana o cambia el modelo con `!modelo` para seguir usando Gemini"
                    await mensaje.edit(content=response)
                    await ctx.send("`Chat cerrado`")
                    chateando = False
                    break
                elif "fewer in length" in str(e):
                    f = codecs.open(respuestaLargaTxt, "w", "utf-8")
                    f.write(response)
                    f.close()
                    response = "La respuesta generada es muy larga para enviarla como mensaje, pero puedes descargarla aquí:"
                    await mensaje.edit(content=response)
                    await ctx.send(file=discord.File(respuestaLargaTxt))
                else:
                    response = "No puedo responder a eso"
                    await mensaje.edit(content=response)
    except Exception as e:
        print(f"DEBUG: se detectó un error en el comando gemini")
        print(f"DEBUG: {e}")
        response = constants.mensobot_crit_err
        chateando = False
        await ctx.send(response)


@bot.command()
async def continuar(ctx):
    print(f"DEBUG: Comando continuar ejecutado por {ctx.author}")
    global chateando
    if ctx.channel.id != canalChat and ctx.channel.id != canalTest:
        await ctx.send(
            "`No puedes usar este comando en este canal, ve a`" + "<#" + canalChat + ">"
        )
        return
    try:
        if chateando:
            await ctx.send(
                "`No puedes continuar un chat mientras un chat está en curso`"
            )
            return
        await ctx.send("Ingresa el ID del chat que deseas continuar:")
        while True:
            try:
                message = await bot.wait_for("message", timeout=60)
                if ctx.channel.id != message.channel.id:
                    print(
                        f"DEBUG: se detectó un mensaje en un canal distinto al llamado"
                    )
                    continue
                if ctx.author != message.author:
                    print(
                        f"DEBUG: se detectó un mensaje de un usuario distinto al llamado"
                    )
                    continue
                else:
                    chat_id = message.content
                    if chat_id not in chats:
                        await mensaje.edit(content="`ID de chat no encontrado`")
                        print(f"DEBUG: ID de chat no encontrado")
                        return
                    else:
                        chat = chats[chat_id]
                        print(f"DEBUG: Chat encontrado con ID: {chat_id}")
                        break
            except Exception as e:
                print(f"DEBUG: se detectó un error en el tiempo de espera")
                print(f"DEBUG: {e}")
                await mensaje.edit(content="`No se ingresó ningún ID de chat`")
                return
        await ctx.send("Chat encontrado con el ID: `" + chat_id + "`")
        print(f"DEBUG: Se continuó el chat con ID: {chat_id}")
        chat = chats[chat_id]
        personalidad = str(ctx.author) + " ha vuelto"
        print(f"DEBUG: se ha seteado la personalidad")
        try:
            mensaje = await ctx.send(chat.send_message(personalidad).text)
        except Exception as e:
            print(f"DEBUG: se detectó un error en la respuesta")
            print(f"DEBUG: {e}")
            await ctx.send("`No se pudo continuar el chat`")
            if "quota" in str(e):
                response = "Este modelo ha excedido su cuota de consultas, por favor, intenta mañana o cambia el modelo con `!modelo` para seguir hablando"
                await mensaje.edit(content=response)
                await ctx.send("`Chat cerrado`")
                chateando = False
                return
            return
        chateando = True
        while True:
            try:
                message = await bot.wait_for("message", timeout=300)
            except Exception as e:
                print(
                    f"DEBUG: se detectó un error en el tiempo de espera por parte del usuario"
                )
                print(f"DEBUG: {e}")
                await ctx.send("El chat ha sido cerrado por inactividad.")
                chateando = False
                break
            if message.author == ctx.author:
                if message.content.lower() in despedidas:
                    print(f"DEBUG: {ctx.author} cerró el chat")
                    mensaje = await ctx.send("*`Despidiéndose...` *:wave:")
                    await mensaje.edit(content=chat.send_message("despidete").text)
                    await ctx.send("Chat cerrado")
                    chateando = False
                    print(f"DEBUG: chat finalizado")
                    break
            try:
                if message.channel.id != (canalChat and canalTest):
                    continue
                if message.author == bot.user:
                    print(
                        f"DEBUG: el bot se detectó a si mismo {message.author} = {bot.user}"
                    )
                    continue
                else:
                    mensaje = await ctx.send(
                        "*`Pensando respuesta para "
                        + str(message.author)
                        + "...`*   :thinking:"
                    )
                    response = chat.send_message(
                        str(message.author) + " dice " + message.content
                    )
                    print(f"DEBUG: {message.author} envió un mensaje")
                    await mensaje.edit(content=response.text)
                    print(f"DEBUG: mensobot respondió")
            except Exception as e:
                print(f"DEBUG: se detectó un error en la respuesta")
                print(f"DEBUG: {e}")
                if "quota" in str(e):
                    response = "Se ha excedido la cuota de consultas, por favor, intenta mañana o cambia el modelo con `!modelo` para seguir hablando"
                    await mensaje.edit(content=response)
                    await ctx.send("Chat cerrado")
                    chateando = False
                    break
                elif "fewer in length" in str(e):
                    f = codecs.open(respuestaLargaTxt, "w", "utf-8")
                    f.write(response)
                    f.close()
                    response = "La respuesta generada es muy larga para enviarla como mensaje, pero puedes descargarla aquí:"
                    await mensaje.edit(content=response)
                    await ctx.send(file=discord.File(respuestaLargaTxt))
                else:
                    response = "No puedo responder a eso"
                    await mensaje.edit(content=response)
    except Exception as e:
        print(f"DEBUG: se detectó un error en el comando continuar")
        print(f"DEBUG: {e}")
        response = Constants.mensobot_crit_err
        chateando = False
        await ctx.send(response)


if testmode:
    bot.run(Constants.discord_test_token)
else:
    bot.run(Constants.discord_token)
