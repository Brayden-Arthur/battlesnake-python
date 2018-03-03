import bottle
import os
import random
import heapq

import signal
from contextlib import contextmanager

class TimeoutException(Exception):
    pass

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException, "Timed out!"
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

taunts = ["\"eval(",
            "[Object object]",
            "42",
            "); DROP TABLE SNAKES",
            "420 blaze it",
            "\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"
            "#yolo",
            "potato",
            "Casting Pyroblast",
            "CLICK TO WIN FREE CRUISE!!!!!",
            "no bombs now",
            "Find hot snakes in your area ;)",
            "My Anaconda Don't",
            "harambe died for nothing",
            "I want Trump for food",
            ".",
            ]

pyro = ["Casting Pyroblast",
        'Casting Pyroblast - 4.0',
        'Casting Pyroblast - 3.0',
        'Casting Pyroblast - 2.0',
        'Casting Pyroblast - 1.0',
        'BOOOOOM!!!!!']

ticker = "bootlesnook"

def tauntPyro():
	tr = tauntSeq(pyro)
	while True:
		yield tr.next()

def tauntSeq(taunts):
	i = 0
	while True:
		yield taunts[i]
		i = i + 1
		if i >= len(taunts):
			i = 0

def tauntTicker(str):
	 i = 0
	 j = len(str)
	 while True:
		yield str[i:j if j > i else len(str)] + str[0:j+1 if i > j else 0]
		i = i + 1
		j = j + 1
		if i > len(str):
			i = 0
		if j > len(str):
			j = 0

tp = tauntPyro()
ts = tauntSeq(taunts)
tt = tauntTicker(ticker)

#call with tt.next()


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
    def __init__(self, id, name, coords, health):
        self.id = id
        self.name = name
        self.head = SnakePart(self, True)
        self.body = SnakePart(self, False)
        self.health = health
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
            self.baseDanger = 5.0
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
    mysnakeid = ""
    snakes = {}
    food = Food()
    coin = Coin()
    wall = Wall()
    #danger = Danger()

def isLegalTile(tile):
    print(tile)
    return isinstance(tile, Danger) or isinstance(tile, Food) or isinstance(tile, Coin)

def getSnake(data):
    snek = data['you']
    for snake in data['snakes']['data']:
        if(snake['id'] == snek['id']):
            return snake
    return None

def getHead(data):
    snek = data['you']
    head = []
    for snake in data['snakes']['data']:
        if(snake['id'] == snek['id']):
            head = snake['body']['data'][0]
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
        getNearbyTiles(grid, nearby, 1, 8);
        for t in nearby:
            danger += grid[t[1]][t[0]].val * 2 * (0.2 ** t[2])
        return (danger / len(nearby))
    else:
        return 1000000.0

def addDanger(d1, d2):
    return d1 + d2

def inbounds(x, y, map):
    if (y < 0):
        return False
    if (y >= len(map)):
        return False
    if (x < 0):
        return False
    if (x >= len(map[0])):
        return False
    return True


def dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def dfs(start, end, map):
    visited = {}
    heap = [(20, start, None)] #lookatposition, myLoc, parent
    iter = 0

    while (len(heap) > 0):
        nextData = heapq.heappop(heap)
        nextPoint = nextData[1]

        iter += 1
        if (iter >= 3000):
            return None

        for dd in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
            pp = [dd[0] + nextPoint[0], dd[1] + nextPoint[1]]

            if (pp[0] == end[0] and pp[1] == end[1]):
                return (0, pp, nextData)

            if (not inbounds(pp[0], pp[1], map)):
                continue
            if (not isLegalTile(map[pp[1]][pp[0]])):
                continue

            addedTuple = (dist(pp, end), pp, nextData)
            #print("Adding point {} {} - value {}".format(addedTuple[1][0], addedTuple[1][1], addedTuple[0]))
            cost = visited.get(nextPoint[0] + nextPoint[1] * 1j, 0) + 1
            if (visited.get(pp[0] + pp[1] * 1j, 100000000) < cost):
                continue
            visited[pp[0] + pp[1] * 1j] = cost
            heapq.heappush(heap, addedTuple)

    return None





def getMap(data):
    grid = [[Danger(0) for x in range(data["width"])] for y in range(data["height"])]
    width = data['width']
    height = data['height']
    for snake in data['snakes']['data']:
        snakeobj =  Snake(snake['id'], snake['name'], snake['body']['data'], snake['health'])
        Map.snakes[snake['id']] = snakeobj
        hasBeenHead = False
        for coord in snake['body']['data']:
            snakepart = None
            if hasBeenHead:
                snakepart = snakeobj.body
            else:
                snakepart = snakeobj.head
            grid[coord['y']][coord['x']] = snakepart
            hasBeenHead = True

    for wall in data.get('walls', []):
        grid[wall[1]][wall[0]] = Map.wall

    for food in data['food']['data']:
        grid[food['y']][food['x']] = Food()
        grid[food['y']][food['x']].val = (grid[food['y']][food['x']].val * 2000) / (data['you']['health'])

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


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json

    # TODO: Do things with data
    return {
        'color': "green",
        'name': 'KING DODONGO',
        'taunt': 'INFERNAL DINOSAUR',
        'head_url': 'https://media.giphy.com/media/SA9s1XbFctROo/giphy.gif',
        'tail_type': "block-bum",
        'head_type': "smile",
        'secondary-colour': 'yellow'
    }

def emergencyFoodCalc(data, head, snake, map):
    move = None
    if (snake['health'] < 25):
        print("Need food now!")
        food = data.get('food', [])
        pathing_point = [0,0]
        if (len(food) > 0):
            pathing_point = min(food, key = lambda foodPoint: dist(head, foodPoint))
        else:
            pathing_point = [data['width'] // 2, data['height'] // 2]

        moveinfo = dfs(head, pathing_point, map)

        if (moveinfo == None or moveinfo[2] == None):
            print("No path to food found")
            return None

        while(moveinfo[2] != None and  moveinfo[2][2] != None):
            moveinfo = moveinfo[2]
            #print(moveinfo)

        pp = moveinfo[1]
        if (pp[0] == head[0] + 1 and pp[1] == head[1]):
            move = 'right'
        elif (pp[0] == head[0] - 1 and pp[1] == head[1]):
            move = 'left'
        elif (pp[0] == head[0] and pp[1] == head[1] - 1):
            move = 'up'
        elif (pp[0] == head[0] and pp[1] == head[1] + 1):
            move = 'down'
        else:
            print("WOAH!!!!! THIS IS A BUG")
            print("head {} {}".format(head[0], head[1]))
            move = 'down'
    return move

def calc():
    print('start of move block***********')
    data = bottle.request.json
    head = getHead(data)
    move_dict = {}
    snake = getSnake(data)
    map = getMap(data)
    move = 'up'

    foodmove = emergencyFoodCalc(data, head, snake, map)
    if (foodmove != None):
        print("Emergency food move {}".format(foodmove))
        return {
            'move': foodmove,
            'taunt': 'I NEED FOOD'
        }


    west = getDanger(head['x'] - 1,head['y'], map)
    east = getDanger(head['x'] + 1,head['y'], map)
    north = getDanger(head['x'],head['y'] - 1 , map)
    south = getDanger(head['x'],head['y'] + 1 , map)

    print("DANGER==> N:",north,"S:",south,"W:",west,"E:",east)

    direction = [(north, 'up'), (east, 'right'), (west, 'left'), (south, 'down')]
    move_dict['move'] = min(direction, key=lambda x: x[0])[1]

    move_dict['taunt'] = ts.next()
    print("move_dict:",move_dict)
    return move_dict

@bottle.post('/move')
def move():
    with time_limit(1):
        return calc()



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
