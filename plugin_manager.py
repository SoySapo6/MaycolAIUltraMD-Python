import logging
import importlib
import os
import sys
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Get the absolute path to the directory containing this file
_MANAGER_DIR = os.path.dirname(os.path.abspath(__file__))

# Ensure the plugin directory is in the Python path
_PLUGIN_DIR = os.path.join(_MANAGER_DIR, "py_plugins")
sys.path.append(_PLUGIN_DIR)

class PluginChangeHandler(FileSystemEventHandler):
    def __init__(self, manager):
        self.manager = manager

    def on_modified(self, event):
        if event.src_path.endswith(".py") and not os.path.basename(event.src_path).startswith("__"):
            plugin_name = os.path.basename(event.src_path)[:-3]
            logging.warning(f"PLUGIN MODIFIED: {plugin_name}.py, reloading...")
            self.manager.reload_plugin(plugin_name)

    def on_created(self, event):
        if event.src_path.endswith(".py") and not os.path.basename(event.src_path).startswith("__"):
            plugin_name = os.path.basename(event.src_path)[:-3]
            logging.info(f"PLUGIN NEW: {plugin_name}.py, loading...")
            self.manager.load_plugin(plugin_name)

    def on_deleted(self, event):
        if event.src_path.endswith(".py") and not os.path.basename(event.src_path).startswith("__"):
            plugin_name = os.path.basename(event.src_path)[:-3]
            logging.warning(f"PLUGIN DELETED: {plugin_name}.py, unloading...")
            self.manager.unload_plugin(plugin_name)


class PluginManager:
    def __init__(self, plugin_folder="py_plugins"):
        # Make the plugin folder path absolute
        self.plugin_folder = os.path.join(_MANAGER_DIR, plugin_folder)
        self.plugins = {}
        if not os.path.exists(self.plugin_folder):
            os.makedirs(self.plugin_folder)

    def load_plugin(self, plugin_name):
        try:
            module = importlib.import_module(plugin_name)

            # Store module and its metadata
            self.plugins[plugin_name] = {
                'module': module,
                'command': getattr(module, 'COMMAND', None),
                'help': getattr(module, 'HELP', ''),
                'tags': getattr(module, 'TAGS', ['uncategorized'])
            }
            logging.info(f"-> PLUGIN LOADED: {plugin_name}")
        except Exception as e:
            logging.error(f"PLUGIN LOAD FAILED: {plugin_name} - {e}")

    def load_all_plugins(self):
        logging.info("Loading all plugins...")
        for filename in os.listdir(self.plugin_folder):
            if filename.endswith(".py") and not filename.startswith("__"):
                plugin_name = filename[:-3]
                self.load_plugin(plugin_name)
        logging.info(f"-> LOADED {len(self.plugins)} plugins.")

    def reload_plugin(self, plugin_name):
        if plugin_name in self.plugins:
            try:
                module = importlib.reload(self.plugins[plugin_name]['module'])

                # Update module and its metadata
                self.plugins[plugin_name] = {
                    'module': module,
                    'command': getattr(module, 'COMMAND', None),
                    'help': getattr(module, 'HELP', ''),
                    'tags': getattr(module, 'TAGS', ['uncategorized'])
                }
                logging.info(f"-> PLUGIN RELOADED: {plugin_name}")
            except Exception as e:
                logging.error(f"PLUGIN RELOAD FAILED: {plugin_name} - {e}")
        else:
            self.load_plugin(plugin_name)

    def unload_plugin(self, plugin_name):
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            logging.info(f"-> PLUGIN UNLOADED: {plugin_name}")

    def watch_plugins(self):
        event_handler = PluginChangeHandler(self)
        observer = Observer()
        observer.schedule(event_handler, self.plugin_folder, recursive=False)

        thread = threading.Thread(target=observer.start)
        thread.daemon = True
        thread.start()

        logging.info("Watching for plugin changes...")
        return observer
