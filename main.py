#!/usr/bin/env python3
import traceback
from configparser import ConfigParser

import tcod

import color
import exceptions
import setup_game
import input_handlers

config = ConfigParser()
config.read("config.ini")

font_name = config.get("fonts", "name")
font_size = int(config.get("fonts", "size"))

def save_game(handler: input_handlers.BaseEventHandler, filename: str) -> None:
    """If the current event handler has an active Engine then save it."""
    if isinstance(handler, input_handlers.EventHandler):
        handler.engine.save_as(filename)
        print("Game saved.")


def main() -> None:
    screen_width = 80
    screen_height = 50

    tileset = tcod.tileset.load_tilesheet(
        f"fonts/{font_name}", font_size, font_size , tcod.tileset.CHARMAP_CP437
    )

    handler: input_handlers.BaseEventHandler = setup_game.MainMenu()

    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset=tileset,
        title="The Dank Caves",
        vsync=True,
    ) as context:
        root_console = tcod.Console(screen_width, screen_height, order="F")
        try:
            while True:
                root_console.clear()
                handler.on_render(console=root_console)
                context.present(
                    root_console,
                    integer_scaling=True,
                    keep_aspect=True)

                try:
                    for event in tcod.event.wait():
                        context.convert_event(event)
                        handler = handler.handle_events(event)
                except Exception:  # Handle exceptions in game.
                    traceback.print_exc()  # Print error to stderr.
                    # Then print the error to the message log.
                    if isinstance(handler, input_handlers.EventHandler):
                        handler.engine.message_log.add_message(
                            traceback.format_exc(), color.error
                        )
        except exceptions.QuitWithoutSaving:
            raise
        except SystemExit:  # Save and quit.
            save_game(handler, "res/savegame.sav")
            raise
        except BaseException:  # Save on any other unexpected exception.
            save_game(handler, "res/savegame.sav")
            raise


if __name__ == "__main__":
    main()
