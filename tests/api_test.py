import jwt
from flask import json


def test_token_with_game_data_is_generated_after_posting_valid_data(app, test_client, session):
    grid = ('CCCCC.....'
        + 'BBBB......'
        + 'RRR.......'
        + 'SSS.......'
        + 'DD........'
        + '..........'
        + '..........'
        + '..........'
        + '..........'
        + '..........')

    player_name = 'some_name'

    ok_response = test_client.post('/api/games/',
                                   data=json.dumps(dict(name=player_name, grid=grid)),
                                   content_type='application/json')

    assert ok_response.status_code == 200

    token = json.loads(ok_response.get_data('token'))['token']
    token_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])

    assert token_data['name'] == player_name
    assert 'game_id' in token_data

