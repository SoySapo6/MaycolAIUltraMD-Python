from tinydb import TinyDB, Query

# Initialize the database
db = TinyDB('database.json', indent=4)
ttt_games = db.table('tictactoe_games')

# You can add helper functions here to interact with the database, for example:
# def get_game(room_id):
#     return ttt_games.get(doc_id=room_id)
#
# def update_game(room_id, data):
#     return ttt_games.update(data, doc_id=room_id)
#
# def create_game(data):
#     return ttt_games.insert(data)
#
# def delete_game(room_id):
#     return ttt_games.remove(doc_ids=[room_id])
