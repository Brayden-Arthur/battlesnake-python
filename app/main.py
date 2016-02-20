import bottle
import os

class Wall(object):
    def __str__(self):
        return "W"

    def __repr__(self):
        return self.__str__()
        
class Food(object):
    def __str__(self):
        return "F"

    def __repr__(self):
        return self.__str__()
        
class Coin(object):
    def __str__(self):
        return "C"

    def __repr__(self):
        return self.__str__()
        
class Snake(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.head = SnakePart(self, True)
        self.body = SnakePart(self, False)
    
    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()
        
class SnakePart(object):
    def __init__(self, snake, ishead):
        self.snake = snake
        self.ishead = ishead
    
    def __str__(self):
        headstr = ""
        if self.ishead:
            headstr = "(H)"
        else:
            headstr = "(B)"
        return self.snake.__str__() + headstr
    
    def __repr__(self):
        return self.__str__()


class Map(object):
    empty = ""
    mysnakeid = "f99aee30-ec8b-4c28-b8c0-49df0e73080b"
    snakes = {}
    food = Food()
    coin = Coin()
    wall = Wall()

    
def getmap(data):
    grid = [[Map.empty for x in range(data["width"])] for y in range(data["height"])]
    
    for snake in data['snakes']:
        snakeobj =  Snake(snake['id'], snake['name'])
        Map.snakes[snake['id']] = snakeobj
        hasBeenHead = False
        for coord in snake['coords']:
            snakepart = None
            if hasBeenHead:
                snakepart = snakeobj.body
            else:
                snakepart = snakeobj.head
            grid[coord[1]][coord[0]] = snakepart
            hasBeenHead = True
            
    for wall in data.get('walls', []):
        grid[wall[1]][wall[0]] = Map.wall
        
    for coin in data.get('gold', []):
        grid[coin[1]][coin[0]] = Map.coin

    for food in data.get('food', []):
        grid[food[1]][food[0]] = Map.food
    
    return grid
    

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


@bottle.post('/start')
def start():
    data = bottle.request.json

    # TODO: Do things with data

    return {
        'taunt': 'battlesnake-python!'
    }


@bottle.post('/move')
def move():
    data = bottle.request.json

    # TODO: Do things with data
    print getmap(data)
    return {
        'move': 'north',
        'taunt': 'battlesnake-python!'
    }


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
#    print getmap({
#        'height': 4,
#        'width': 3,
#        'snakes': [
#            {
#                'id': "somesnake",
#                'name': 'Snake name',
#                'status': 'alive',
#                'coords': [
#                    [1, 1], [1, 2]
#                ]
#            }
#        ],
#        'walls' : [
#            [2,2],
#            [2,3]
#        ],
#        'food': [
#            [0,0]
#        ],
#        'gold': [
#            [1,0]
#        ]
#    })
