import bottle
import os
import random

class Wall(object):
    def __init__(self):
        self.baseDanger = 0.2

    def __str__(self):
        return "W"

    def __repr__(self):
        return self.__str__()


class Food(object):
    def __init__(self):
        self.baseDanger = -0.75
        self.val = -0.75

    def __str__(self):
        return "F"

    def __repr__(self):
        return self.__str__()

class Coin(object):
    def __init__(self):
        self.baseDanger = 0.1
    def __str__(self):
        return "C"

    def __repr__(self):
        return self.__str__()

class Health(object):
    def __init__(self, id, name):
        pass

class Danger(object):
    def __init__(self, dangerVal):
        self.val = dangerVal
        self.baseDanger = 0

    def __str__(self):
        return str(self.val)

    def __repr__(self):
        return self.__str__()


class Snake(object):
    def __init__(self, id, name, coords):
        self.id = id
        self.name = name
        self.head = SnakePart(self, True)
        self.body = SnakePart(self, False)
        self.coords = coords
    def __str__(self):
        return self.name
    def __repr__(self):
        return self.__str__()

class SnakePart(object):
    def __init__(self, snake, ishead):
        self.snake = snake
        self.ishead = ishead
        if ishead:
            self.baseDanger = 3.0
        else:
            self.baseDanger = 1.0

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
    #danger = Danger()

def getHead():
    snake = Map.snakes[Map.mysnakeid]
    return snake.coords[0]

def getDanger(x,y,grid):
    if y < 0 or y >= len(grid):
        print "invalid y"
        return 1000000.0
    if x < 0 or x >= len(grid[y]):
        return 1000000.0
        
    tile = grid[y][x]
    if isinstance(tile, Danger) or isinstance(tile, Food):
        return tile.val
    else:
        return 1000000.0

def addDanger(d1, d2):
    return d1 + d2


def getMap(data):
    grid = [[Danger(0) for x in range(data["width"])] for y in range(data["height"])]
    width = data['width']
    height = data['height']

    for snake in data['snakes']:
        snakeobj =  Snake(snake['id'], snake['name'], snake['coords'])
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
        grid[food[1]][food[0]] = Food()


    for y in range(len(grid)):
        for x in range(len(grid[y])):
            tile = grid[y][x]
            if isinstance(tile, Danger) or isinstance(tile, Food):
                for d in [[-1, 0], [1, 0], [0, 1], [0, -1]]:
                    yy = d[0] + y
                    xx = d[1] + x
                    if yy < 0 or yy >= len(grid) or xx < 0 or xx >= len(grid[y]):
                        continue

                    addedDanger = grid[yy][xx].baseDanger
                    tile.val = addDanger(tile.val, addedDanger)

    for hh in range((height - 2) // 2):
        for y in [0, len(grid) - 1 - hh]:
            for x in range(len(grid[y])):
                tile = grid[y][x]
                if isinstance(tile, Danger):
                    tile.val = addDanger(tile.val, (0.5 ** hh) * 0.4)

    for ww in range((width - 2) // 2):
        for y in range(len(grid)):
            for x in [0, len(grid[y]) - 1 - ww]:
                tile = grid[y][x]
                if isinstance(tile, Danger):
                    tile.val = addDanger(tile.val, (0.5 ** ww) * 0.4)

    return grid

def getTaunt():
    return random.choice(["\"eval(", 
                            "UNDEFINED",
                            "42",
                            ";DROPTABLE SNAKES",
                            "420 blaze it",
                            "#yolo",
                            "potato",
                            "Casting Pyroblast - 4.9s",
                            "no bombs now",
                            "\\",
                            ":ok_hand::eyes::fire::ok_hand::eyes: :100:NICE:100::fire::fire:FIRE:fire::fire:"])

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
        'taunt': 'INFERNAL DINOSAUR'
    }

@bottle.post('/move')
def move():
    data = bottle.request.json
    map = getMap(data)
    move = 'north'
    head = getHead()
    west = getDanger(head[0] - 1,head[1], map)
    east = getDanger(head[0] + 1,head[1], map)
    north = getDanger(head[0],head[1] - 1 , map)
    south = getDanger(head[0],head[1] + 1 , map)

    lowestDanger = min(north,south,east,west)
    if(lowestDanger == north):
        move = 'north'
    elif(lowestDanger == south):
        move = 'south'
    elif(lowestDanger == east):
        move = 'east'
    if(lowestDanger == west):
        move = 'west'
        
    taunt = getTaunt()
        
    print "%f %f %f %f %f" % (north, south, west, east, lowestDanger)

    return {
        'move': move,
        'taunt': taunt
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

#
# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
    #print getmap({
    #    'height': 4,
    #    'width': 4,
    #    'snakes': [
    #        {
    #            'id': Map.mysnakeid,
    #            'name': 'Snake name',
    #            'status': 'alive',
    #            'coords': [
    #                [1, 1], [1, 2]
    #            ]
    #        },
    #        {
    #            'id': 'lol',
    #            'name': 'lol snake',
    #            'status': 'alive',
    #            'coords': [
    #                [2,1], [3, 1]
    #            ]
    #        }
    #    ],
    #    'walls' : [
    #        [2,2],
    #        [2,3]
    #    ],
    #    'food': [
    #        [0,0]
    #    ],
    #    'gold': [
    #        [1,0]
    #    ]
    #})
    #print getHead()
