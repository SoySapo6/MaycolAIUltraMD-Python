import logging
from .py_lib.simple import serialize_message

# A simple prefix for commands
PREFIX = "."

async def handle_message(client, event, plugin_manager):
    """
    Handles incoming messages, serializes them, and dispatches commands to plugins.
    """
    m = serialize_message(client, event)

    if not m.text or not m.text.startswith(PREFIX):
        return  # Not a command

    # Parse the command and arguments
    parts = m.text[len(PREFIX):].strip().split()
    command = parts[0].lower()
    args = parts[1:]

    logging.info(f"CMD: '{command}' from {m.sender}")

    # Find and execute the plugin
    for plugin_name, plugin_info in plugin_manager.plugins.items():
        if plugin_info['command'] == command:
            try:
                logging.info(f"-> PLUGIN: {plugin_name}")
                module = plugin_info['module']

                # Special case for the menu plugin to give it access to the manager
                if command == 'menu':
                    response = await module.execute(m, args, plugin_manager=plugin_manager)
                else:
                    response = await module.execute(m, args)

                if response:
                    await m.reply(response)
            except Exception as e:
                logging.error(f"PLUGIN ERROR: {plugin_name} - {e}")
                await m.reply(f"Error: {e}")
            return  # Stop after finding the command

    logging.warning(f"CMD NOT FOUND: '{command}'")
