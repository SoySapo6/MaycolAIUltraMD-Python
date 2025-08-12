import asyncio
import logging
import re
from neonize.aioze.client import NewAClient
from neonize.aioze.events import MessageEv, ConnectedEv
from plugin_manager import PluginManager
from py_handler import handle_message
from colored import fg, attr
import pyfiglet

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

async def obtener_codigo_emparejamiento(cliente, numero_telefono):
    """Intenta obtener el código de emparejamiento usando diferentes métodos."""
    metodos = [
        'request_pairing_code',
        'requestPairingCode', 
        'get_pairing_code',
        'getPairingCode',
        'pairing_code',
        'generate_pairing_code'
    ]
    
    for metodo in metodos:
        if hasattr(cliente, metodo):
            try:
                func = getattr(cliente, metodo)
                logging.info(f"Intentando método: {metodo}")
                codigo = await func(numero_telefono)
                return codigo
            except Exception as e:
                logging.warning(f"Método {metodo} falló: {e}")
                continue
    
    # Si ningún método funciona, intentar conectar directamente
    logging.warning("No se pudo obtener código de emparejamiento automáticamente.")
    logging.info("Intenta conectar tu teléfono manualmente o usa el método QR.")
    return None

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
            opcion = await asyncio.to_thread(input, "> ")
        except EOFError:
            logging.error("Entrada interrumpida. Usando método QR por defecto.")
            opcion = '1'
            break

    cliente: NewAClient

    try:
        if opcion == '1':
            # Método QR - configuración más simple
            logging.info("Iniciando con método QR...")
            cliente = NewAClient("maycol_ai_bot_session.db")
            
        elif opcion == '2':
            # Método de código de emparejamiento
            cliente = NewAClient("maycol_ai_bot_session.db")

            numero_telefono = ""
            while not re.match(r'^\d{10,15}$', numero_telefono):
                try:
                    numero_telefono = await asyncio.to_thread(
                        input,
                        f"{fg('yellow')}Ingresa tu número de teléfono completo sin '+' o espacios (ej: 15551234567):{attr('reset')} "
                    )
                    numero_telefono = re.sub(r'[^\d]', '', numero_telefono)  # Limpiar número
                except EOFError:
                    logging.error("Entrada interrumpida.")
                    return

            logging.info(f"Solicitando código de emparejamiento para {numero_telefono}...")
            
            codigo_emparejamiento = await obtener_codigo_emparejamiento(cliente, numero_telefono)
            
            if codigo_emparejamiento:
                logging.info(f"{fg('magenta')}--- CÓDIGO DE EMPAREJAMIENTO ---{attr('reset')}")
                logging.info(f"Tu código de emparejamiento es: {fg('cyan')}{codigo_emparejamiento}{attr('reset')}")
                logging.info(f"{fg('magenta')}--------------------------------{attr('reset')}")
            else:
                logging.warning("No se pudo obtener código de emparejamiento. Cambiando a método QR.")
                
    except Exception as e:
        logging.error(f"Error al crear cliente: {e}")
        logging.info("Creando cliente con configuración básica...")
        cliente = NewAClient("maycol_ai_bot_session.db")

    # Inicializar gestor de plugins con manejo de errores
    try:
        plugin_manager = PluginManager()
    except Exception as e:
        logging.error(f"Error al inicializar PluginManager: {e}")
        logging.info("Continuando sin sistema de plugins...")
        plugin_manager = None

    # Definir manejadores de eventos
    @cliente.event
    async def al_conectar(_: NewAClient, evento: ConnectedEv):
        """Maneja el evento 'conectado'."""
        logging.info("🎉 ¡Bot conectado exitosamente!")
        logging.info(f"Conectado a la cuenta: {evento.device}")

    @cliente.event
    async def al_recibir_mensaje(cliente: NewAClient, evento: MessageEv):
        """Maneja mensajes entrantes delegando al manejador."""
        try:
            await handle_message(cliente, evento, plugin_manager)
        except Exception as e:
            logging.error(f"Error al manejar mensaje: {e}")

    # Cargar plugins y comenzar a observar (si están disponibles)
    if plugin_manager:
        try:
            plugin_manager.load_all_plugins()
            plugin_manager.watch_plugins()
            logging.info("Sistema de plugins cargado correctamente.")
        except Exception as e:
            logging.error(f"Error al cargar plugins: {e}")
            logging.info("Continuando sin plugins...")

    logging.info("Conectando a WhatsApp...")
    
    try:
        await cliente.connect()
    except Exception as e:
        logging.error(f"Error de conexión: {e}")
        logging.info("Reintentando conexión...")
        await asyncio.sleep(5)
        await cliente.connect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot detenido manualmente.")
    except Exception as e:
        logging.error(f"Error crítico: {e}")
        logging.info("El bot se cerrará.")
