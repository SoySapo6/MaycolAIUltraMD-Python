import time
from ..py_lib.tictactoe import TicTacToe
from ..db import ttt_games, Query

COMMAND = "ttt"
HELP = "Starts a game of Tic-Tac-Toe.\nUsage: .ttt <room name>"
TAGS = ['game']

async def execute(m, args):
    """
    Handles Tic-Tac-Toe game creation and joining.
    """
    room_name = ' '.join(args)
    if not room_name:
        return "Please provide a room name to start or join a game.\nExample: .ttt my_game"

    Game = Query()

    # Check if the player is already in a game
    player_in_game = ttt_games.search(
        (Game.player_x == m.sender) | (Game.player_o == m.sender)
    )
    if player_in_game:
        return "You are already in a game."

    # Find a waiting room with the specified name
    room = ttt_games.get(
        (Game.state == 'WAITING') & (Game.name == room_name)
    )

    if room:
        # Join an existing game
        await m.reply("A player has joined! Starting the game.")

        game_instance = TicTacToe(room['player_x'], m.sender)

        # Update the room in the database
        ttt_games.update({
            'player_o': m.sender,
            'state': 'PLAYING',
            'game_data': { # Store the game state
                'x_board': game_instance.x_board,
                'o_board': game_instance.o_board,
                'current_turn_is_o': game_instance.current_turn_is_o,
                'turns': game_instance.turns
            }
        }, doc_ids=[room.doc_id])

        # Render the board
        board_array = game_instance.render()
        board_emojis = [
            {'X': '❎', 'O': '⭕', '1': '1️⃣', '2': '2️⃣', '3': '3️⃣', '4': '4️⃣', '5': '5️⃣', '6': '6️⃣', '7': '7️⃣', '8': '8️⃣', '9': '9️⃣'}[v]
            for v in board_array
        ]

        board_str = (
            f"{''.join(board_emojis[0:3])}\n"
            f"{''.join(board_emojis[3:6])}\n"
            f"{''.join(board_emojis[6:9])}"
        )

        turn_player_jid = game_instance.current_turn

        response_text = (
            f"🎮 TIC-TAC-TOE 🎮\n\n"
            f"❎ = @{room['player_x'].split('@')[0]}\n"
            f"⭕ = @{m.sender.split('@')[0]}\n\n"
            f"{board_str}\n\n"
            f"It's @{turn_player_jid.split('@')[0]}'s turn."
        )

        # This is a simplification. The original bot sent messages to both chats.
        # For now, we reply in the current chat.
        # Mentioning users would require a modification to the reply function.
        await m.reply(response_text)

    else:
        # Create a new game
        game_instance = TicTacToe(m.sender, None)

        new_game = {
            'name': room_name,
            'player_x': m.sender,
            'player_o': None,
            'state': 'WAITING',
            'game_data': {
                'x_board': game_instance.x_board,
                'o_board': game_instance.o_board,
                'current_turn_is_o': game_instance.current_turn_is_o,
                'turns': game_instance.turns
            },
            'created_at': time.time()
        }
        ttt_games.insert(new_game)

        return (
            f"*🕹 TIC-TAC-TOE 🎮*\n\n"
            f"Waiting for a second player to join room '{room_name}'.\n"
            f"To join, another player can type: .ttt {room_name}"
        )
