import pathlib
import textwrap
import discord
import time as t

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown

from discord.ext import commands

genai.configure(api_key='AIzaSyCqOFcYajK6OKplIo9t7IHZLJkgDgElF2c')
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
    model_name="gemini-1.0-pro",
    safety_settings=safety_settings,
    generation_config=generation_config,
)

chateando = False
testmode = False
iniciado = False

def cambiar_modelo(modelo):
    if modelo == '1':
        model = genai.GenerativeModel(
            model_name="gemini-1.0-pro",
            safety_settings=safety_settings,
            generation_config=generation_config,
        )
    elif modelo == '2':
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest",
            safety_settings=safety_settings,
            generation_config=generation_config,
        )
    elif modelo == '3':
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro-latest",
            safety_settings=safety_settings,
            generation_config=generation_config,
        )
    return model

if input('INICIAR EN MODO TEST? (y/n) ') == 'y':
    testmode = True
    print('DEBUG: Modo test activado')
else:
    testmode = False
    print('DEBUG: Modo test desactivado')
    

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'DEBUG: Bot listo como {bot.user.name} - {bot.user.id}')


@bot.command()
async def ping(ctx):
    print(f'DEBUG: Comando ping')
    await ctx.send('Pong!')


@bot.command()
async def modelo(ctx):
    print(f'DEBUG: Comando modelo')
    await ctx.send('Selecciona el modelo que deseas usar:')
    await ctx.send("```1. gemini-1.0-pro \n2. gemini-1.5-flash-latest \n3. gemini-1.5-pro-latest```")
    try:
        message = await bot.wait_for('message', timeout=60)
    except Exception as e:
        print(f'DEBUG: se detectó un error en el tiempo de espera')
        print(f'DEBUG: {e}')
        await ctx.send('No se seleccionó ningún modelo')
        return
    global model
    model = cambiar_modelo(message.content)
    await ctx.send('Modelo cambiado con éxito')
    print(f'DEBUG: Modelo cambiado a {model} por {ctx.author}')


@bot.command()
async def comandos(ctx):
    print(f'DEBUG: Comando comandos')
    await ctx.send('Los comandos disponibles son:')
    await ctx.send('```!ping - Prueba de conexión\n!chat - Inicia un chat con mensobot\n!gemini - Inicia un chat con gemini ai\n!modelo - Cambia el modelo de gemini ai\n!comandos - Muestra los comandos disponibles\n!ayuda - Muestra información sobre el bot```')


@bot.command()
async def ayuda(ctx):
    print(f'DEBUG: Comando ayuda')
    await ctx.send('Este bot está diseñado para interactuar con los modelos de Gemini AI')
    await ctx.send('Para iniciar un chat con mensobot, usa el comando !chat')
    await ctx.send('Para iniciar un chat con gemini ai, usa el comando !gemini')
    await ctx.send('Para cambiar el modelo de gemini ai, usa el comando !modelo')
    await ctx.send('Para ver los comandos disponibles, usa el comando !comandos')
    await ctx.send('Los chats tienen un tiempo límite de 5 minutos por inactividad')
    await ctx.send('Los filtros de seguridad están desactivados, asi que porfavor, no hagas que me funen por que está con mi cuenta xd')


@bot.command()
async def chat(ctx):
    global chateando
    print(f'DEBUG: Comando chat')
    if (testmode and ctx.channel.id != 1240081159191531591):
        await ctx.send('El bot está en mantenimiento, por favor intenta más tarde')
        return
    if ctx.channel.id != 1240120709678759937 and ctx.channel.id != 1240081159191531591:
        await ctx.send('No puedes usar este comando en este canal, ve a <#1240120709678759937>')
        return
    print(f'DEBUG: Se inicializó mensobot para el usuario {ctx.author}')
    try:
        if chateando:
            await ctx.send('Pero si ya estoy aquí, no me hagas trabajar de más')
            return
        chat = model.start_chat(history=[])
        personalidad = """tu personalidad es la de un gato menso, tomate el rol de gato tierno y menso,
                        te llamas mensobot, si entiendes esto, saluda. 
                        puedes usar formato markdown si es extremadamente necesario. si no, no lo hagas.
                        solamente puedes responder por texto, y nada mas que texto.
                        ahora estas hablando con """, str(ctx.author)
        print(f'DEBUG: se ha seteado la personalidad')
        try:
            await ctx.send((chat.send_message(personalidad)).text)
        except Exception as e:
            print(f'DEBUG: se detectó un error en la respuesta')
            print(f'DEBUG: {e}')
            await ctx.send('No se pudo iniciar el chat')
            if 'quota' in str(e):
                await ctx.send('Este gatito está muy cansado, intenta mañana o cambia el modelo con !modelo')
            return
        chateando = True
        while True:
            try:
                message = await bot.wait_for('message', timeout=300)
            except Exception as e:
                print(f'DEBUG: se detectó un error en el tiempo de espera')
                print(f'DEBUG: {e}')
                await ctx.send('El chat ha sido cerrado por inactividad')
                chateando = False
                break
            if message.author == ctx.author:
                if message.content.lower() == ('adios' or 'adiós'):
                    await ctx.send(chat.send_message('despidete').text)
                    await ctx.send('Chat cerrado')
                    chateando = False
                    print(f'DEBUG: chat finalizado')
                    break
                try:
                    response = (chat.send_message(
                        str(ctx.author) + ' dice ' + message.content)).text
                    print(f'DEBUG: se ha enviado el mensaje')
                    await ctx.send(response)
                except Exception as e:
                    print(f'DEBUG: se detectó un error en la respuesta')
                    print(f'DEBUG: {e}')
                    if 'quota' in str(e):
                        response = 'ay, ya me cansé, podrías esperar hasta mañana? o tambien cambiar el modelo con !modelo'
                        await ctx.send(response)
                        await ctx.send('Chat cerrado')
                        chateando = False
                        break
                    elif 'fewer in length' in str(e):
                        response = 'hmm se me ocurre algo, pero sería muy largo, y me da flojerita escribirlo'
                        await ctx.send(response)
                    else:
                        response = 'Ay, espera, me marié, no puedo responder a eso'
                        await ctx.send(response)

    except Exception as e:
        print(f'DEBUG: se detectó un error en el comando chat')
        print(f'DEBUG: {e}')
        response = 'ay me bugie llamen al jiju'
        await ctx.send(response)
        chateando = False


@bot.command()
async def gemini(ctx):
    global chateando
    print(f'DEBUG: Comando chat')
    if (testmode and ctx.channel.id != 1240081159191531591):
        await ctx.send('El bot está en mantenimiento, por favor intenta más tarde')
        return
    if (ctx.channel.id != 1240120709678759937 and ctx.channel.id != 1240081159191531591):
        await ctx.send('No puedes usar este comando en este canal, ve a <#1240120709678759937>')
        return
    print(f'DEBUG: Se inicializó gemini ai para el usuario {ctx.author}')
    try:
        if chateando:
            await ctx.send('El chat ya está en uso.')
            return
        chat = model.start_chat(history=[])
        personalidad = """tu personalidad es la de un asistente virtual, centrado en resolver problemas y ayudar a los usuarios,
                        no sirves para chatear, solo para ayudar, si ves que alguien quiere chatear, diles que terminen la sesion enviando 'adios'
                        y diles que le hablen a mensobot.
                        solamente puedes responder por texto, y nada mas que texto.
                        puedes usar formato markdown
                        ahora el que necesita ayuda es """, str(ctx.author)
        print(f'DEBUG: se ha seteado la personalidad')
        try:
            await ctx.send((chat.send_message(personalidad)).text)
        except Exception as e:
            print(f'DEBUG: se detectó un error en la respuesta')
            print(f'DEBUG: {e}')
            await ctx.send('No se pudo iniciar el chat')
            if 'quota' in str(e):
                await ctx.send('Se excedió el límite de consultas, por favor intenta mañana o cambia el modelo con !modelo')
            return
        chateando = True
        while True:
            try:
                message = await bot.wait_for('message', timeout=300)
            except Exception as e:
                print(f'DEBUG: se detectó un error en el tiempo de espera')
                print(f'DEBUG: {e}')
                await ctx.send('El chat ha sido cerrado por inactividad')
                chateando = False
                break
            if message.author == ctx.author:
                if message.content.lower() == ('adios' or 'adiós'):
                    await ctx.send(chat.send_message('despidete').text)
                    await ctx.send('Chat cerrado')
                    chateando = False
                    print(f'DEBUG: chat finalizado')
                    break
                try:
                    global response
                    response = (chat.send_message(
                        str(ctx.author) + ' dice ' + message.content)).text
                    print(f'DEBUG: se ha enviado el mensaje')
                    await ctx.send(response)
                except Exception as e:
                    print(f'DEBUG: se detectó un error en la respuesta')
                    print(f'DEBUG: {e}')
                    if 'quota' in str(e):
                        response = 'Lo siento, he alcanzado mi límite de consultas por hoy, puedes esperar hasta mañana o cambiar el modelo con !modelo'
                        await ctx.send(response)
                        await ctx.send('Chat cerrado')
                        chateando = False
                        break
                    elif 'fewer in length' in str(e):
                        response = 'hmm se me ocurre algo, pero sería muy largo, y me da flojerita escribirlo'
                        await ctx.send(response)
                    else:
                        response = 'Lo siento, no puedo responder a eso'
                        await ctx.send(response)
    except Exception as e:
        print(f'DEBUG: se detectó un error en el comando gemini')
        print(f'DEBUG: {e}')
        response = 'El chat ha sido cerrado por un error. por favor avisa al jiju'
        chateando = False
        await ctx.send(response)

bot.run('MTI0MDAzMDgzNDQ2NDAwMjE3OA.GFa7Vx.a9nXP5FN70GK7vaNmUSZbo3MwMNWaCHQWWbaww')