import bottle
import os
import random

tauntValue = 0
currentTaunt = ''
#Gettting the danger value for danger. Change value when needed
class Wall(object):
    def __init__(self):
        self.baseDanger = 0.7

    def __str__(self):
        return "W"

    def __repr__(self):
        return self.__str__()

#danger value for the food
class Food(object):
    def __init__(self):
        self.baseDanger = -0.4
        self.val = -0.4

    def __str__(self):
        return "F"

    def __repr__(self):
        return self.__str__()

class Coin(object):
    def __init__(self):
        self.baseDanger = -0.9
        self.val = -0.9
    def __str__(self):
        return "C"

    def __repr__(self):
        return self.__str__()
#when running out, run for the food
class Health(object):
    def __init__(self, id, name):
        pass
#move according to the danger
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
            if self.snake.id == Map.mysnakeid:
                self.baseDanger = 0
        else:
            self.baseDanger = 1.0
            if self.snake.id == Map.mysnakeid:
                self.baseDanger = 0.5

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

def isLegalTile(tile):
    return isinstance(tile, Danger) or isinstance(tile, Food) or isinstance(tile, Coin)

def getHead(data):
    snek = data['you']
    head = []
    for snake in data['snakes']:
        if(str(snake['id']) == str(snek)):
            head = snake['coords'][0]
    return head

def getNearbyTiles(grid, points, cur, total):
    if cur > total:
        return
    for point in filter(lambda p: p[2] == cur, points):
        dd = [[-1, 0], [1, 0], [0, -1], [0, 1]]
        for d in filter(lambda x: point[1]+x[0] >= 0 and point[1]+x[0] < len(grid[0]) and point[0]+x[1] >= 0 and point[0]+x[1] < len(grid), dd):
            tile = grid[point[1]+d[0]][point[0]+d[1]]
            if not isLegalTile(tile):
                continue
            if not any(filter((lambda p: p[0] == point[0]+d[1] and p[1] == point[1]+d[0]), points)):
                points.append((point[0]+d[1], point[1]+d[0], cur+1))
                getNearbyTiles(grid, points, cur+1, total)



def getDanger(x,y,grid):
    if y < 0 or y >= len(grid):
        return 1000000.0
    if x < 0 or x >= len(grid[y]):
        return 1000000.0
    tile =  grid[y][x]
    if isLegalTile(tile):
        danger = 0.0
        nearby = [(x,y,1)]
        getNearbyTiles(grid, nearby, 1, 5);
        for t in nearby:
            danger += grid[t[1]][t[0]].val * 2 * (0.2 ** t[2])
        return (danger / len(nearby))
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
        grid[coin[1]][coin[0]] = Coin()

    for food in data.get('food', []):
        grid[food[1]][food[0]] = Food()


    for y in range(len(grid)):
        for x in range(len(grid[y])):
            tile = grid[y][x]
            if isLegalTile(tile):
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
                if isLegalTile(tile):
                    tile.val = addDanger(tile.val, (0.5 ** hh) * 0.4)

    for ww in range((width - 2) // 2):
        for y in range(len(grid)):
            for x in [0, len(grid[y]) - 1 - ww]:
                tile = grid[y][x]
                if isLegalTile(tile):
                    tile.val = addDanger(tile.val, (0.5 ** ww) * 0.4)

    return grid

def getTaunt():
    global tauntValue
    global currentTaunt
    if(tauntValue % 3 == 0):
        currentTaunt = random.choice(["\"eval(",
                            "[Object object]",
                            "42",
                            "); DROP TABLE SNAKES",
                            "420 blaze it",
                            "#yolo",
                            "potato",
                            "Casting Pyroblast",
                            "CLICK TO WIN FREE CRUISE!!!!!",
                            "no bombs now",
                            "Find hot snakes in your area ;)",
                            "My Anaconda Don't",
                            ":ok_hand::eyes::fire::ok_hand::eyes: :100:NICE:100::fire::fire:FIRE:fire::fire:"])
    if(currentTaunt == 'Casting Pyroblast'):
        currentTaunt = 'Casting Pyroblast - 4.0'
        tauntValue = tauntValue + 1
        return currentTaunt
    if(currentTaunt == 'Casting Pyroblast - 4.0'):
        currentTaunt = 'Casting Pyroblast - 3.0'
        return currentTaunt
    if(currentTaunt == 'Casting Pyroblast - 3.0'):
        currentTaunt = 'Casting Pyroblast - 2.0'
        return currentTaunt
    if(currentTaunt == 'Casting Pyroblast - 2.0'):
        currentTaunt = 'Casting Pyroblast - 1.0'
        return currentTaunt
    if(currentTaunt == 'Casting Pyroblast - 1.0'):
        currentTaunt = 'BOOOOOM!!!!!'
        tauntValue = tauntValue + 2
        return currentTaunt
    tauntValue = tauntValue + 1
    return currentTaunt

@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json

    # TODO: Do things with data
    return {
        'color': 'green',
        'name': 'KING DODONGO',
        'taunt': 'INFERNAL DINOSAUR',
        'head_url': 'https://zeldawiki.org/images/8/82/HWL_VS_Link_Icon.png'
    }

@bottle.post('/move')
def move():
    print('start of move block***********')
    data = bottle.request.json
    head = getHead(data)
    map = getMap(data)
    print(head)
    move = 'up'
    west = getDanger(head[0] - 1,head[1], map)
    east = getDanger(head[0] + 1,head[1], map)
    north = getDanger(head[0],head[1] - 1 , map)
    south = getDanger(head[0],head[1] + 1 , map)
    print('values of  NEWS = ' + str(north) + ' ' + str(east) + ' ' +  str(south) + ' ' +  str(west))

    if(north < south):
        if(north < west):
            if(north < east):
                move = 'up'
                print('in north')
    if(south < west):
        if(south < east):
            move = 'down'
            print('in south')
    if(west < east):
        move = 'left'
        print('print west')
    else:
        move = 'right'
        print('in east')

    print(move)
    taunt = getTaunt()
    print('end of move block##############')
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
