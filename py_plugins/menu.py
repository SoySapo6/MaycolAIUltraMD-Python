import logging

COMMAND = "menu"
HELP = "Displays the command menu."
TAGS = ['main']

# This is a bit of a hack. The handler passes the plugin_manager to the `handle_message`
# function, but not to the plugins themselves. For a menu plugin that needs access
# to the list of all other plugins, we need a way to get it.
# A proper solution might involve a more sophisticated dependency injection system,
# but for now, we'll have the handler pass it as a special argument if the
# command is 'menu'. This requires a small change to the handler.
# Let's assume for now the handler is modified to pass it.

async def execute(m, args, plugin_manager=None):
    """
    Generates and displays a categorized menu of all available commands.
    """
    if not plugin_manager:
        return "Error: Could not access the plugin manager."

    # Group plugins by tag
    categories = {}
    for name, plugin_info in plugin_manager.plugins.items():
        if not plugin_info['tags'] or not plugin_info['help']:
            continue

        for tag in plugin_info['tags']:
            if tag not in categories:
                categories[tag] = []

            # Add the command and its help text
            command = plugin_info.get('command', name)
            help_text = plugin_info.get('help', 'No description').split('\n')[0] # First line of help
            categories[tag].append(f".{command} - {help_text}")

    # Format the menu
    menu_text = "🤖 *Available Commands* 🤖\n\n"

    sorted_tags = sorted(categories.keys())

    for tag in sorted_tags:
        menu_text += f"╭─━━━ *{tag.upper()}* ━━━╮\n"
        for command_help in categories[tag]:
            menu_text += f"│ {command_help}\n"
        menu_text += "╰─━━━━━━━━━━━━━╯\n\n"

    return menu_text.strip()
