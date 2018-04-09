"""
Endpoints of API blueprint.

Game is created through POST.
PATCH and GET methods are based on the presence of JWT acquired after game creation.
This reduces validation of game.id and player.name which are simply encoded into token passed in header.
"""
import jwt
from flask import current_app

from app.api import bp, ApiException, ApiResult
from app.api.models import Game, Board, Player
from app.api.schemas import schemas
from app.api.utils import api_schema, token_required


@bp.route('/games/', methods=['POST'])
@api_schema(schemas['/games/']['POST'])
def create_game(name, grid):
    g = Game.get_new_game()

    try:
        b = Board(grid)
    except ValueError as e:
        raise ApiException(str(e))

    p = Player(name=name, board=b)
    g.join(p)

    g.save_to_db()
    current_app.logger.info(f'Player {name} joined game {g.id}')

    token = jwt.encode({'game_id': g.id, 'name': name}, current_app.config['SECRET_KEY'])

    return ApiResult({'token': token.decode()})  # pierscin: token decoded from byte string to string


@bp.route('/games/', methods=['PATCH'])
@api_schema(schemas['/games/']['PATCH'])
@token_required
def make_move(token_data, x, y):
    game_id, name = token_data['game_id'], token_data['name']

    g = Game.query.get(game_id)

    return ApiResult({'result': g.shoot(x, y)})


@bp.route('/games/', methods=['GET'])
@token_required
def game_status(token_data):
    g = Game.query.get(token_data['game_id'])

    name = token_data['name']

    asking, other = (g.current, g.other) if g.current.name == name else (g.other, g.current)

    return ApiResult({'state': g.state,
                      'your_board': asking.board.grid,
                      'enemy_board': other.board.enemy_view()})
