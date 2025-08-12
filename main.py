import asyncio
import logging
import re
from neonize.aioze.client import NewAClient
from neonize.aioze.events import MessageEv, ConnectedEv, QRCodeEv
from plugin_manager import PluginManager
from py_handler import handle_message
from colored import fg, attr
import pyfiglet
import qrcode
import sys

def mostrar_banner():
    """Muestra un banner de inicio genial."""
    color = fg('yellow')
    reset = attr('reset')
    color_autor = fg('cyan')

    # Generar arte ASCII
    arte_ascii = pyfiglet.figlet_format("MaycolAIUltraMD", font="block")

    # Mostrar banner
    print(f"{color}{arte_ascii}{reset}")
    print(f"{color_autor}                 Hecho por Maycol                           {reset}")
    print()

def configurar_logging():
    """Configura el logging con colores."""
    class FormateadorColoreado(logging.Formatter):
        COLORES = {
            'WARNING': fg('yellow'),
            'INFO': fg('green'),
            'DEBUG': fg('blue'),
            'CRITICAL': fg('red'),
            'ERROR': fg('red')
        }

        def format(self, record):
            mensaje_log = super().format(record)
            color = self.COLORES.get(record.levelname)
            if color:
                return f"{color}{mensaje_log}{attr('reset')}"
            return mensaje_log

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(FormateadorColoreado('%(levelname)s: %(message)s'))
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(handler)

def mostrar_qr_en_terminal(codigo_qr):
    """Muestra el código QR en la terminal usando caracteres ASCII."""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=1,
            border=1,
        )
        qr.add_data(codigo_qr)
        qr.make(fit=True)
        
        # Imprimir QR en terminal
        print(f"\n{fg('cyan')}═══════════════════════════════════════════{attr('reset')}")
        print(f"{fg('yellow')}        ESCANEA ESTE CÓDIGO QR CON WHATSAPP{attr('reset')}")
        print(f"{fg('cyan')}═══════════════════════════════════════════{attr('reset')}")
        qr.print_ascii(invert=True)
        print(f"{fg('cyan')}═══════════════════════════════════════════{attr('reset')}")
        print(f"{fg('green')}Abre WhatsApp > Dispositivos Vinculados > Vincular dispositivo{attr('reset')}")
        print(f"{fg('cyan')}═══════════════════════════════════════════{attr('reset')}\n")
        
    except Exception as e:
        logging.error(f"Error al mostrar QR: {e}")
        print(f"\n{fg('yellow')}CÓDIGO QR:{attr('reset')}")
        print(codigo_qr)
        print()

async def obtener_codigo_emparejamiento(cliente, numero_telefono):
    """Intenta obtener el código de emparejamiento usando diferentes métodos."""
    metodos_posibles = [
        ('request_pairing_code', numero_telefono),
        ('requestPairingCode', numero_telefono), 
        ('get_pairing_code', numero_telefono),
        ('getPairingCode', numero_telefono),
        ('pairing_code', numero_telefono),
        ('generate_pairing_code', numero_telefono),
        ('pair', numero_telefono),
        ('pair_phone', numero_telefono)
    ]
    
    for metodo, param in metodos_posibles:
        if hasattr(cliente, metodo):
            try:
                func = getattr(cliente, metodo)
                logging.info(f"Probando método: {metodo}")
                
                if asyncio.iscoroutinefunction(func):
                    codigo = await func(param)
                else:
                    codigo = func(param)
                    
                if codigo:
                    return codigo
                    
            except Exception as e:
                logging.warning(f"Método {metodo} falló: {e}")
                continue
    
    return None

async def manejar_entrada_usuario():
    """Maneja la entrada del usuario de forma asíncrona."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, sys.stdin.readline)

async def main():
    """Función principal para inicializar, configurar y ejecutar el bot."""
    mostrar_banner()
    configurar_logging()

    # --- Login Interactivo ---
    print("Por favor elige un método de inicio de sesión:")
    print(f"{fg('green')}1. Escanear Código QR{attr('reset')}")
    print(f"{fg('cyan')}2. Usar Código de Emparejamiento (Número de Teléfono){attr('reset')}")

    opcion = ""
    while opcion not in ['1', '2']:
        try:
            opcion = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            logging.info("Operación cancelada por el usuario.")
            return

    cliente: NewAClient

    try:
        # Crear cliente con configuración básica
        cliente = NewAClient("maycol_ai_bot_session.db")
        
        # Variable para controlar si ya estamos conectados
        conectado = False
        
        # Manejar eventos ANTES de la conexión
        @cliente.event
        async def on_qr_code(cliente: NewAClient, evento):
            """Maneja el evento del código QR."""
            nonlocal conectado
            if not conectado:
                logging.info("📱 Código QR recibido!")
                mostrar_qr_en_terminal(evento.code if hasattr(evento, 'code') else str(evento))

        @cliente.event  
        async def al_conectar(cliente: NewAClient, evento: ConnectedEv):
            """Maneja el evento 'conectado'."""
            nonlocal conectado
            conectado = True
            logging.info("🎉 ¡Bot conectado exitosamente!")
            logging.info(f"Conectado a la cuenta: {evento.device if hasattr(evento, 'device') else 'Dispositivo WhatsApp'}")

        @cliente.event
        async def al_recibir_mensaje(cliente: NewAClient, evento: MessageEv):
            """Maneja mensajes entrantes."""
            try:
                if plugin_manager:
                    await handle_message(cliente, evento, plugin_manager)
            except Exception as e:
                logging.error(f"Error al manejar mensaje: {e}")

        # Inicializar gestor de plugins
        plugin_manager = None
        try:
            plugin_manager = PluginManager()
            plugin_manager.load_all_plugins()
            plugin_manager.watch_plugins()
            logging.info("Sistema de plugins cargado correctamente.")
        except Exception as e:
            logging.error(f"Error al cargar plugins: {e}")
            logging.info("Continuando sin plugins...")

        if opcion == '1':
            # Método QR
            logging.info("Iniciando con método QR...")
            logging.info("Esperando código QR...")
            
        elif opcion == '2':
            # Método de código de emparejamiento
            numero_telefono = ""
            while not re.match(r'^\d{10,15}$', numero_telefono):
                try:
                    numero_telefono = input(
                        f"{fg('yellow')}Ingresa tu número completo sin '+' (ej: 51987654321): {attr('reset')}"
                    ).strip()
                    numero_telefono = re.sub(r'[^\d]', '', numero_telefono)
                except (EOFError, KeyboardInterrupt):
                    logging.info("Operación cancelada.")
                    return

            logging.info(f"Solicitando código para {numero_telefono}...")
            
            # Intentar obtener código de emparejamiento
            codigo = await obtener_codigo_emparejamiento(cliente, numero_telefono)
            
            if codigo:
                print(f"\n{fg('magenta')}╔══════════════════════════════════╗{attr('reset')}")
                print(f"{fg('magenta')}║     CÓDIGO DE EMPAREJAMIENTO     ║{attr('reset')}")
                print(f"{fg('magenta')}╠══════════════════════════════════╣{attr('reset')}")
                print(f"{fg('magenta')}║{attr('reset')}          {fg('cyan')}{codigo}{attr('reset')}            {fg('magenta')}║{attr('reset')}")
                print(f"{fg('magenta')}╚══════════════════════════════════╝{attr('reset')}")
                print(f"{fg('green')}Ingresa este código en WhatsApp{attr('reset')}\n")
            else:
                logging.warning("No se pudo obtener código de emparejamiento.")
                logging.info("Cambiando automáticamente a método QR...")

        # Conectar al cliente
        logging.info("Conectando a WhatsApp...")
        logging.info("⏳ Esperando autenticación...")
        
        # Iniciar la conexión
        await cliente.connect()
        
        # Mantener el bot corriendo
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logging.info("Bot detenido por el usuario.")
    except Exception as e:
        logging.error(f"Error crítico: {e}")
        logging.info("Reintentando en 5 segundos...")
        await asyncio.sleep(5)
        # Reintentar una vez
        try:
            await cliente.connect()
            while True:
                await asyncio.sleep(1)
        except Exception as e2:
            logging.error(f"Segundo intento falló: {e2}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("\n👋 Bot detenido manualmente.")
    except Exception as e:
        logging.error(f"Error fatal: {e}")
