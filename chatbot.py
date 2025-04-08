import google.generativeai as genai
from google.generativeai import types
import Constants  # Constants.py
import discord
from discord.ext import commands
import asyncio
import pathlib
import textwrap
import random
import string
import codecs  # evita que salgan simbolos raros


try:
    if not Constants.google_API_key or Constants.google_API_key == "TU_API_KEY_GEMINI":
        raise ValueError("API Key de Google Gemini no configurada en Constants.py")
    genai.configure(api_key=Constants.google_API_key)
    print("DEBUG: API Key de Gemini configurada.")
except AttributeError:
    print(
        "ERROR FATAL: Versión de 'google-generativeai' incompatible. Reinstala: pip install --upgrade google-generativeai"
    )
    exit()
except ValueError as ve:
    print(f"ERROR FATAL: {ve}")
    exit()
except Exception as e:
    print(f"ERROR FATAL: No se pudo configurar Gemini: {e}")
    exit()


generation_config_dict = {
    "temperature": 0.8,  # mas alto es mas aleatorio
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}
safety_settings = [
    # sin filtros es mas chistoso
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


try:
    modelo_gemini_global = genai.GenerativeModel(
        "gemini-2.0-flash",
        safety_settings=safety_settings,
        generation_config=types.GenerationConfig(**generation_config_dict),
    )
    print(f"DEBUG: Modelo Gemini inicializado: {modelo_gemini_global.model_name}")
except Exception as e_model:
    print(f"ERROR FATAL: No se pudo inicializar el modelo Gemini: {e_model}")
    exit()


chateando = False
testmode = True if pathlib.Path(__file__).name == "chatbot_test.py" else False
try:
    canalChat = Constants.canalChat
    canalTest = Constants.canalTest
except AttributeError:
    print("ERROR FATAL: 'canalChat' y/o 'canalTest' no definidos en Constants.py")
    exit()
respuestaLargaTxt = "respuestaLarga.txt"
despedidas = [
    "adios",
    "adiós",
    "chao",
    "bye",
    "salir",
    "terminar",
]  # aqui añadir las que quieran
chats = {}
orden_chats = []
LIMITE_CHATS_GUARDADOS = 10


intents = discord.Intents.default()
intents.message_content = True
try:
    DISCORD_TOKEN = (
        Constants.discord_test_token if testmode else Constants.discord_token
    )
    if not DISCORD_TOKEN or DISCORD_TOKEN.startswith("TU_TOKEN"):
        raise ValueError(
            f"Token de Discord ({'test' if testmode else 'producción'}) no configurado."
        )
except AttributeError:
    print(f"ERROR FATAL: Token de Discord no definido en Constants.py")
    exit()
except ValueError as ve:
    print(f"ERROR FATAL: {ve}")
    exit()

bot = commands.Bot(command_prefix="!", intents=intents)
print(f"DEBUG: Modo test {'activado' if testmode else 'desactivado'}.")


def gen_id_chat():
    while True:
        id_chat = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
        if len(orden_chats) >= LIMITE_CHATS_GUARDADOS:
            chat_viejo_id = orden_chats.pop(0)
            if chat_viejo_id in chats:
                del chats[
                    chat_viejo_id
                ]  # no se si esta bien implementado asi pero funciona asi que era
                print(f"DEBUG: Historial viejo eliminado - ID: {chat_viejo_id}")
        if id_chat not in chats:
            chats[id_chat] = {"history": []}
            orden_chats.append(id_chat)
            print(f"DEBUG: Chat creado - ID: {id_chat}")
            return id_chat


async def enviar_respuesta(ctx_or_msg, texto_respuesta, archivo_txt):
    target = (
        ctx_or_msg.channel
        if isinstance(ctx_or_msg, commands.Context)
        else ctx_or_msg.channel
    )
    try:
        if not texto_respuesta:
            await target.send("🤔")
            return
        if len(texto_respuesta) <= 2000:
            await target.send(texto_respuesta)
        else:
            print("DEBUG: Respuesta larga, enviando como archivo.")
            with codecs.open(archivo_txt, "w", encoding="utf-8") as f:
                f.write(texto_respuesta)
            await target.send(
                "📄 **Respuesta larga.** Ver archivo:", file=discord.File(archivo_txt)
            )
            try:
                pathlib.Path(archivo_txt).unlink()
            except OSError as e:
                print(f"WARN: No se pudo borrar {archivo_txt}: {e}")
    except discord.HTTPException as e:
        print(f"ERROR al enviar mensaje: {e.status} - {e.text}")
        await target.send("❌ Error enviando respuesta.")
    except Exception as e:
        print(f"ERROR en enviar_respuesta: {e}")
        await target.send("❌ Error inesperado procesando respuesta.")


@bot.event
async def on_ready():
    print(f"DEBUG: Bot listo: {bot.user.name}")
    await bot.change_presence(activity=discord.Game(name="!ayuda"))


@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! 🏓 ({bot.latency * 1000:.2f} ms)")


@bot.command()
async def ayuda(ctx):
    try:
        ayuda_txt = (
            Constants.mensaje_ayuda
            + "\n\n**Comandos:** `!chat`, `!gemini`, `!continuar [ID]`, `!modelo`, `!lista`, `!comandos`, `!ping`"
        )
        await ctx.author.send(ayuda_txt)
        await ctx.send(f"📩 Guía enviada por DM, {ctx.author.mention}!")
    except discord.Forbidden:
        await ctx.send(f"❌ No puedo enviarte DMs, {ctx.author.mention}.")
    except AttributeError:
        await ctx.send("❌ Falta 'mensaje_ayuda' en Constants.py.")
    except Exception as e:
        print(f"ERROR Ayuda: {e}")
        await ctx.send("❌ Error enviando ayuda.")


@bot.command()
async def lista(ctx):
    global modelo_gemini_global
    if not orden_chats:
        await ctx.send("💤 No hay historiales guardados.")
        return
    lista_desc = [f"• `{cid}`" for cid in reversed(orden_chats) if cid in chats]
    if not lista_desc:
        await ctx.send("💤 No hay historiales guardados.")
        return
    mod_corto = modelo_gemini_global.model_name.replace("-latest", "").split("/")[
        -1
    ]  # mucho texto
    embed = discord.Embed(
        title="Historiales Recientes",
        description=f"Modelo Nuevos Chats: **{mod_corto}**\n\n"
        + "\n".join(lista_desc)
        + f"\n\nSe guardan **{LIMITE_CHATS_GUARDADOS}**.",
        color=discord.Color.green(),
    )
    await ctx.send(embed=embed)


@bot.command()
async def comandos(ctx):
    embed = discord.Embed(title="Comandos", color=discord.Color.blue())
    embed.add_field(
        name="💬 IA",
        value="`!chat`: Chat con Mensobot.\n`!gemini`: Chat directo.\n`!continuar [ID]`: Reanuda chat.",
        inline=False,
    )
    embed.add_field(
        name="⚙️ Config",
        value="`!modelo`: Cambia modelo IA.\n`!lista`: Muestra IDs guardados.",
        inline=False,
    )
    embed.add_field(
        name="🛠️ Utils",
        value="`!ping`: Latencia.\n`!ayuda`: Ayuda por DM.\n`!comandos`: Esta lista.",
        inline=False,
    )
    await ctx.send(embed=embed)


@bot.command()
async def modelo(ctx):
    global modelo_gemini_global
    if chateando:
        await ctx.send("⛔ No mientras hay chat activo.")
        return

    modelos = {
        "1": ("gemini-2.0-flash-lite", "2.0 Flash Lite (Básico)"),
        "2": ("gemini-2.0-flash", "2.0 Flash (Intermedio)"),
        "3": ("gemini-2.5-pro-preview-03-25", "2.5 Pro (Avanzado)"),
    }

    actual_n = modelo_gemini_global.model_name
    actual_d, actual_k = "Desconocido", "2"
    for k, (n, d) in modelos.items():
        if n == actual_n:
            actual_d, actual_k = d, k
            break

    desc = f"Modelo actual: **{actual_d}**. Elige nuevo modelo:\n" + "\n".join(
        [f"{k}: {d}" for k, (_, d) in modelos.items()]
    )
    embed = discord.Embed(
        title="Selección Modelo IA", description=desc, color=discord.Color.purple()
    )
    msg_sel = await ctx.send(embed=embed)

    def check(m):
        return (
            m.author == ctx.author and m.channel == ctx.channel and m.content in modelos
        )

    try:
        msg_usr = await bot.wait_for("message", timeout=30.0, check=check)
        nuevo_n, nuevo_d = modelos[msg_usr.content]
        sysi = getattr(modelo_gemini_global, "system_instruction", None)
        modelo_gemini_global = genai.GenerativeModel(
            model_name=nuevo_n,
            generation_config=types.GenerationConfig(**generation_config_dict),
            safety_settings=safety_settings,
            system_instruction=sysi,
        )
        await ctx.send(f"✅ Modelo actualizado a: **{nuevo_d}**")
        print(f"DEBUG: Modelo global -> {nuevo_n} por {ctx.author}")
        try:
            await msg_sel.delete()
            await msg_usr.delete()
        except:
            pass
    except asyncio.TimeoutError:
        await msg_sel.edit(
            embed=discord.Embed(title="Tiempo Agotado", color=discord.Color.orange()),
            delete_after=10,
        )
    except Exception as e:
        print(f"ERROR Modelo: {e}")
        await ctx.send("❌ Error al cambiar modelo.")


async def _gestionar_sesion_chat(
    ctx, *, chat_id_param=None, usar_prompt_mensobot=False
):
    global chateando, modelo_gemini_global, chats, orden_chats, generation_config_dict, safety_settings

    if chateando:
        await ctx.send("⏳ Ya hay un chat activo. Espera a que termine.")
        return
    chateando = True
    chat_id = None
    es_continuacion = False
    canal_del_chat = ctx.channel
    autor_original = ctx.author

    try:
        if chat_id_param:  # continuar
            chat_id = chat_id_param.upper()
            if chat_id not in chats:
                await ctx.send(f"❌ ID no encontrado `{chat_id}`.")
                chateando = False
                return
            es_continuacion = True
            if chat_id in orden_chats:
                orden_chats.remove(chat_id)
            orden_chats.append(chat_id)
            print(f"DEBUG: Continuando chat ID: {chat_id} por {autor_original}")
        else:  # nuevo
            chat_id = gen_id_chat()
            print(f"DEBUG: Iniciando chat ID: {chat_id} por {autor_original}")

        historial_actual = chats[chat_id]["history"]
        modelo_para_sesion = modelo_gemini_global
        system_instruction = None
        tipo_chat_log = "gemini"
        mensobot_prompt_existe = hasattr(Constants, "mensobot_prompt")

        if usar_prompt_mensobot and not es_continuacion:  # !chat
            if mensobot_prompt_existe:
                try:
                    system_instruction = (
                        Constants.mensobot_prompt
                        + f"\n\nUsuario Inicial: {autor_original.name}"
                    )
                    modelo_para_sesion = genai.GenerativeModel(
                        model_name=modelo_gemini_global.model_name,
                        generation_config=types.GenerationConfig(
                            **generation_config_dict
                        ),
                        safety_settings=safety_settings,
                        system_instruction=system_instruction,
                    )
                    print(f"DEBUG: Usando instrucción de sistema para chat {chat_id}.")
                    tipo_chat_log = "mensobot"
                except Exception as e_sys:
                    print(
                        f"WARN: No se pudo aplicar instrucción de sistema a {chat_id} (Error: {e_sys}). Usando modelo estándar."
                    )
                    modelo_para_sesion = modelo_gemini_global
                    tipo_chat_log = "gemini"
            else:
                print(
                    f"WARN: 'mensobot_prompt' no definido en Constants.py para chat {chat_id}. Usando chat Gemini estándar."
                )

        try:
            sesion_chat = modelo_para_sesion.start_chat(history=historial_actual)
        except Exception as e_start:
            print(f"ERROR iniciando sesión de chat para {chat_id}: {e_start}")
            await ctx.send("❌ No se pudo inicializar la sesión de chat con la IA.")
            if not es_continuacion and chat_id in chats:
                if chat_id in orden_chats:
                    orden_chats.remove(chat_id)
                del chats[chat_id]
            raise e_start

        modelo_usado_corto = modelo_para_sesion.model_name.replace("-latest", "").split(
            "/"
        )[-1]
        if not es_continuacion:
            await ctx.send(
                f"Iniciando chat **{tipo_chat_log}** con `{modelo_usado_corto}`.\n**ID:** `{chat_id}`\n\n__{autor_original.mention} inició, ¡cualquiera puede hablar! Solo {autor_original.mention} puede cerrarlo con 'adios'.__"
            )
        else:
            await ctx.send(
                f"**Reanudando chat** `{chat_id}` (Modelo: `{modelo_usado_corto}`).\n\n__{autor_original.mention}, el chat continúa. Cualquiera puede hablar, solo tú puedes cerrarlo.__"
            )

        while True:
            try:
                mensaje_usuario = await bot.wait_for(
                    "message",
                    timeout=300.0,  # 5 min
                    check=lambda m: m.channel == canal_del_chat
                    and not m.content.startswith("!")
                    and not m.author.bot,
                )

                contenido = mensaje_usuario.content

                if (
                    contenido.lower() in despedidas
                    and mensaje_usuario.author == autor_original
                ):
                    print(
                        f"DEBUG: Chat {chat_id} terminado por el autor original {mensaje_usuario.author}."
                    )
                    async with ctx.typing():
                        try:
                            exception_names = [
                                name
                                for name in dir(genai)
                                if "Exception" in name or "Error" in name
                            ]
                            print(
                                f"DEBUG: Available exception types in genai: {exception_names}"
                            )

                            resp_fin = await sesion_chat.send_message_async(
                                "Despídete amablemente."
                            )
                            await enviar_respuesta(
                                mensaje_usuario, resp_fin.text, respuestaLargaTxt
                            )
                        except Exception as e_fin:
                            print(f"WARN: Problema despedida {chat_id}: {e_fin}")
                            if (
                                "stopped" in str(e_fin).lower()
                                or "block" in str(e_fin).lower()
                            ):
                                await mensaje_usuario.channel.send("¡Hasta luego!")
                            else:
                                raise e_fin
                        except Exception as e_gen_fin:
                            print(f"ERROR despedida {chat_id}: {e_gen_fin}")
                            await mensaje_usuario.channel.send("¡Nos vemos!")
                    await mensaje_usuario.channel.send(
                        f"**Chat `{chat_id}` finalizado y guardado.**"
                    )
                    chats[chat_id]["history"] = sesion_chat.history
                    break

                async with ctx.typing():
                    try:
                        contenido_formateado = f"{str(mensaje_usuario.author)} dice: {contenido}"  # para que sepa con quien habla
                        respuesta = await sesion_chat.send_message_async(
                            contenido_formateado
                        )
                        await enviar_respuesta(
                            mensaje_usuario, respuesta.text, respuestaLargaTxt
                        )
                        chats[chat_id]["history"] = sesion_chat.history
                    except Exception as e:
                        err = str(e).lower()
                        if "stopped" in err or "stop" in err:
                            print(f"WARN: Generación detenida {chat_id}: {e}")
                            txt = getattr(getattr(e, "response", None), "text", None)
                            await enviar_respuesta(
                                mensaje_usuario,
                                (txt or "") + "\n\n⚠️ *(Respuesta cortada)*",
                                respuestaLargaTxt,
                            )
                        elif "block" in err or "safety" in err:
                            print(f"WARN: Prompt bloqueado {chat_id}: {e}")
                            await mensaje_usuario.channel.send(
                                "❌ Mensaje bloqueado por seguridad."
                            )
                        elif "quota" in err or "resource_exhausted" in err:
                            print(f"ERROR Chat {chat_id}: Cuota.")
                            await mensaje_usuario.channel.send(
                                "⚠️ Límite de uso alcanzado, se recomienda cambiar de modelo."
                            )
                            chats[chat_id]["history"] = sesion_chat.history
                            break
                        elif "api_key_not_valid" in err:
                            print(f"ERROR FATAL {chat_id}: API Key inválida.")
                            await mensaje_usuario.channel.send(
                                "❌ Error crítico API Key."
                            )
                            break
                        else:
                            print(f"ERROR Respuesta {chat_id}: {e}")
                            await mensaje_usuario.channel.send(
                                "❌ Error generando respuesta."
                            )

            except asyncio.TimeoutError:
                print(f"DEBUG: Chat {chat_id} cerrado por inactividad.")
                await canal_del_chat.send(
                    f"⏳ Chat `{chat_id}` cerrado y guardado por inactividad."
                )
                if "sesion_chat" in locals():
                    chats[chat_id]["history"] = sesion_chat.history
                break
            except Exception as e_loop:
                print(f"ERROR Bucle chat {chat_id}: {e_loop}")
                await canal_del_chat.send(f"❌ Error inesperado en chat `{chat_id}`.")
                if "sesion_chat" in locals():
                    chats[chat_id]["history"] = sesion_chat.history
                break

    except Exception as e_outer:
        print(f"ERROR grave sesión {chat_id if chat_id else 'desconocido'}: {e_outer}")
        await ctx.send(f"⛔ Error grave al gestionar la sesión.")

    finally:
        chateando = False
        print(
            f"DEBUG: Estado chateando = False (final de _gestionar_sesion_chat para {chat_id if chat_id else 'fallido'})"
        )


@bot.command(name="chat")
async def comando_chat_mensobot(ctx):
    if ctx.channel.id not in [canalChat, canalTest]:
        m = getattr(bot.get_channel(canalChat), "mention", f"ID:{canalChat}")
        await ctx.send(f"🔒 Usa este comando en {m}")
        return
    await _gestionar_sesion_chat(ctx, usar_prompt_mensobot=True)  # !chat


@bot.command(name="gemini")
async def comando_chat_gemini(ctx):
    if ctx.channel.id not in [canalChat, canalTest]:
        m = getattr(bot.get_channel(canalChat), "mention", f"ID:{canalChat}")
        await ctx.send(f"🔒 Usa este comando en {m}")
        return
    await _gestionar_sesion_chat(ctx)


@bot.command(name="continuar")
async def comando_continuar_chat(ctx, chat_id_a_continuar: str = None):
    if ctx.channel.id not in [canalChat, canalTest]:
        m = getattr(bot.get_channel(canalChat), "mention", f"ID:{canalChat}")
        await ctx.send(f"🔒 Usa este comando en {m}")
        return

    chat_id_final = None
    if chat_id_a_continuar:
        chat_id_final = chat_id_a_continuar
    else:  # pedir id
        if not orden_chats:
            await ctx.send("💤 No hay IDs recientes.")
            return
        lista_desc = [f"• `{cid}`" for cid in reversed(orden_chats) if cid in chats]
        if not lista_desc:
            await ctx.send("💤 No hay IDs recientes.")
            return
        embed = discord.Embed(
            title="Continuar Chat",
            description="Escribe ID:\n" + "\n".join(lista_desc),
            color=discord.Color.gold(),
        )
        msg_sel = await ctx.send(embed=embed)

        def check(m):
            return (
                m.author == ctx.author
                and m.channel == ctx.channel
                and not m.content.startswith("!")
                and m.content.upper() in chats
            )

        try:
            resp = await bot.wait_for("message", timeout=30.0, check=check)
            chat_id_final = resp.content
            await msg_sel.delete()
            await resp.delete()
        except asyncio.TimeoutError:
            await msg_sel.edit(
                embed=discord.Embed(
                    title="Tiempo Agotado", color=discord.Color.orange()
                ),
                delete_after=10,
            )
            return
        except Exception as e:
            print(f"ERROR seleccion {e}")
            await ctx.send("❌ Error seleccionando.")
            return

    if chat_id_final:
        await _gestionar_sesion_chat(ctx, chat_id_param=chat_id_final)


if __name__ == "__main__":
    try:
        print("INFO: Iniciando bot...")
        bot.run(DISCORD_TOKEN)
    except discord.LoginFailure:
        print("ERROR FATAL: Token de Discord inválido.")
    except Exception as e:
        print(f"ERROR FATAL al iniciar: {e}")
