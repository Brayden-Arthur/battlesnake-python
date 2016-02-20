import bottle
import os

currentPlan = 0


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.get('/')
def index():
    head_url = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    return {
        'color': '#00ff00',
        'head': head_url
    }

def run():

def food():

def attack():


@bottle.post('/start')
def start():
    data = bottle.request.json

    # TODO: Do things with data

    return {
        'taunt': 'INFERNAL DINOSAUR'
    }


@bottle.post('/move')
def move():
    move = ''
    data = bottle.request.json
    if(health < 15):
        food(move)

    # TODO: Do things with data


    return {
        'move': 'north',
        'taunt': 'battlesnake-python!'
    }

#protect the coins,
#f99aee30-ec8b-4c28-b8c0-49df0e73080b
#us
#mostly ignore food until < 70 hitpoints
#
@bottle.post('/end')
def end():
    data = bottle.request.json

    # TODO: Do things with data

    return {
        'taunt': 'battlesnake-python!'
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
