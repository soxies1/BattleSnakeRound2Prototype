import bottle
import os
import json
import random
import copy

import uuid
import sys


'''
Example Received Snake Object

{
    "id": "1234-567890-123456-7890",
    "name": "Well Documented Snake",
    "status": "alive",
    "message": "Moved up",
    "taunt": "Let's rock!",
    "age": 56,
    "health": 83,
    "coords": [ [1, 1], [1, 2], [2, 2] ,]
    "kills": 4,
    "food": 12,
    "gold": 2
}
'''

ourSnakeId = ""
ourName = str(uuid.uuid4())
snakes = []
originalDictionary = {}

def removeItemFromDictionary(key, dictionary):
    if not dictionary.get(key, None) is None:
        del dictionary[key]

def directionalCoordinate(direction, withRespectTo):
    x = withRespectTo[0]
    y = withRespectTo[1]
    if(direction == 'up'):
        return (x, y-1)
    elif(direction == 'down'):
        return (x, y+1)
    elif(direction == 'right'):
        return (x+1, y)
    elif(direction == 'left'):
        return (x-1, y)

def removeSnakeCollisions(ourSnake, otherSnakes, turnDictionary):
    # List all the available directions our snake can go
    options = ['up', 'left', 'down', 'right']
    canGo = list(options)

    # Our snakes head
    head = ourSnake['coords'][0]

    # ----- Other Snakes (Where head is going to go)/ Head collision detection ----
    for snake in otherSnakes:
        # Check if we're longer, if so continue
        if len(snake['coords']) < len(ourSnake['coords']):
            continue

        # Else, we have to check if we'd run into them and avoid those directions
        if (snake['coords'][0][0] - head[0] == 2) and (snake['coords'][0][1] == head[1]):
            if 'right' in canGo:
                canGo.remove('right')
        if (snake['coords'][0][0] - head[0] == -2) and (snake['coords'][0][1] == head[1]):
            if 'left' in canGo:
                canGo.remove('left')
        if (snake['coords'][0][1] - head[1] == 2) and (snake['coords'][0][0] == head[0]):
            if 'down' in canGo:
                canGo.remove('down')
        if (snake['coords'][0][1] - head[1] == -2) and (snake['coords'][0][0] == head[0]):
            if 'up' in canGo:
                canGo.remove('up')
        if ((snake['coords'][0][0] - head[0] == 1) and (snake['coords'][0][1] - head[1] == -1)):
            if 'right' in canGo:
                canGo.remove('right')
            if 'up' in canGo:
                canGo.remove('up')
        if ((snake['coords'][0][0] - head[0] == 1) and (snake['coords'][0][1] - head[1] == 1)):
            if 'right' in canGo:
                canGo.remove('right')
            if 'down' in canGo:
                canGo.remove('down')
        if ((snake['coords'][0][0] - head[0] == -1) and (snake['coords'][0][1] - head[1] == -1)):
            if 'left' in canGo:
                canGo.remove('left')
            if 'up' in canGo:
                canGo.remove('up')
        if ((snake['coords'][0][0] - head[0] == -1) and (snake['coords'][0][1] - head[1] == 1)):
            if 'left' in canGo:
                canGo.remove('left')
            if 'down' in canGo:
                canGo.remove('down')

    for dir in options:
        if not dir in canGo:
            removeItemFromDictionary(directionalCoordinate(dir, head), turnDictionary)

def getDirectionsCanGo(head, turnDictionary):
    canGo = []
    x = head[0]
    y = head[1]
    right = (x+1, y)
    left = (x-1, y)
    up = (x, y-1)
    down = (x, y+1)
    if right in turnDictionary.keys():
        canGo.append('right')
    if left in turnDictionary.keys():
        canGo.append('left')
    if up in turnDictionary.keys():
        canGo.append('up')
    if down in turnDictionary.keys():
        canGo.append('down')
    return canGo

def getUnvisitedNeighbor(node, otherNodes):
    x = node[0]
    y = node[1]
    right = (x+1, y)
    left = (x-1, y)
    up = (x, y-1)
    down = (x, y+1)
    if right in otherNodes.keys() and otherNodes[right] == False:
        return right
    elif left in otherNodes.keys() and otherNodes[left] == False:
        return left
    elif up in otherNodes.keys() and otherNodes[up] == False:
        return up
    elif down in otherNodes.keys() and otherNodes[down] == False:
        return down
    else:
        return None

def bfs(rootNode, otherNodes):
    queue = []
    queue.append(rootNode)
    otherNodes[rootNode] = True
    room = 0
    while len(queue) > 0:
        node = queue.pop(0)
        child = getUnvisitedNeighbor(node, otherNodes)
        while not child == None:
            otherNodes[child] = True
            queue.append(child)
            child = getUnvisitedNeighbor(node, otherNodes)
            room = room + 1

    return room

def getClosestFood(dirsFromHead, head, foods):
    head_x = head[0]
    head_y = head[1]
    minDist = 1000000
    minFood = []
    for food in foods:
        food_x = food[0]
        food_y = food[1]
        temp = abs(food_x - head_x) + abs(food_y - head_y)
        if temp < minDist:
            minDist = temp
            minFood = food

    minDist = 100000
    minDirs = []
    #minDir = dirsFromHead[random.randint(0, len(dirsFromHead)-1)]
    for dir in dirsFromHead:
        coords = directionalCoordinate(dir, head)
        x = coords[0]
        y = coords[1]
        min_food_x = minFood[0]
        min_food_y = minFood[1]
        temp = abs(min_food_x - x) + abs(min_food_y - y)
        if temp < minDist:
            minDist = temp
            minDirs = [dir]
        elif temp == minDist:
            minDirs.append(dir)

    #print("Min Dirs: ")
    #print(minDirs)
    if len(minDirs) == 1:
        return minDirs[0]
    else:
        return minDirs[random.randint(0, len(minDirs)-1)]



@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')

'''
Object recieved for /start
{
    "game": "hairy-cheese",
    "mode": "advanced",
    "turn": 0,
    "height": 20,
    "width": 30,
    "snakes": [
        <Snake Object>, <Snake Object>, ...
    ],
    "food": []
}
'''

def generateDictionary(board_width, board_height):
    for y in xrange(board_height):
        for x in xrange(board_width):
            originalDictionary[(x,y)] = False

@bottle.post('/start')
def start():
    data = bottle.request.json
    game_id = data['game_id']
    board_width = data['width']
    board_height = data['height']

    #initialize dictionary
    #print("Start called")
    generateDictionary(board_width, board_height)

    head_url = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    # TODO: Do things with data

    return {
        'color': '#00FF00',
        'taunt': '{} ({}x{})'.format(game_id, board_width, board_height),
        'head_url': head_url,
        'name': ourName
    }


'''
Recieved Move object for /move
{
    "game": "hairy-cheese",
    "mode": "advanced",
    "turn": 4,
    "height": 20,
    "width": 30,
    "snakes": [
        <Snake Object>, <Snake Object>, ...
    ],
    "food": [
        [1, 2], [9, 3], ...
    ]
}

'''

@bottle.post('/move')
def move():
    data = bottle.request.json

    mapWidth = data['width']
    mapHeight = data['height']

    currTaunt = 'meow'

    if(len(originalDictionary) < 1):
        generateDictionary(mapWidth, mapHeight)

    # make dictionary for open spaces this turn
    turnDictionary = originalDictionary.copy()

    #print("Turn dictionary: ")
    #print(turnDictionary)

    # remove spaces that are un available to move to
    #print("Snake data: ")
    #print(data['snakes'])


    ourSnake = {}
    otherSnakes = []
    for snake in data['snakes']:
        #print("snake name:")
        #print(snake['name'])
        #print("our snake name:")
        #print(ourName)
        if snake['name'] == ourName:
            ourSnake = snake
            #print("our snake: ")
            #print(ourSnake)
        else:
            otherSnakes.append(snake)
        for coord in snake['coords'][:-1]:
            #print("coords of snake:")
            #print(coord)
            x = coord[0]
            y = coord[1]
            if not turnDictionary.get((x, y), None) is None:
                del turnDictionary[(x, y)]
    #print(len(turnDictionary))
    headOfOurSnake = ourSnake['coords'][0]

    #print("length before remove head collision")
    #print(len(turnDictionary))
    removeSnakeCollisions(ourSnake, otherSnakes, turnDictionary)
    #print("length after remove head collision")
    #print(len(turnDictionary))


    currMove = "up"
    directionsCanGo = getDirectionsCanGo(headOfOurSnake, turnDictionary)
    #print("DirectionsCanGo")
    #print(directionsCanGo)
    if len(directionsCanGo) >= 2:
        #print("More then one move to choose from")
        maxSpaces = 0
        maxSpacesDir = 'up'
        dirsAndValues = {}
        for dir in directionsCanGo:
            availableSpotNodes = turnDictionary.copy()
            rootNode = directionalCoordinate(dir, headOfOurSnake)
            temp = bfs(rootNode, availableSpotNodes)
            #print("Room from bfs for dir -- " + dir + " -- :")
            #print(temp)
            dirsAndValues[dir] = temp
            if(temp > maxSpaces):
                maxSpaces = temp
                maxSpacesDir = dir
        dirsThatHaveMax = []
        for dir in dirsAndValues:
            #print("Dir in dirs and values:")
            #print(dir)
            if dirsAndValues[dir] == maxSpaces:
                dirsThatHaveMax.append(dir)
        if len(dirsThatHaveMax) == 1:
            currMove = maxSpacesDir
        else:
            currMove = getClosestFood(dirsThatHaveMax, headOfOurSnake, data['food'])
    elif len(directionsCanGo) == 1:
        #print("One move to choose from")
        currMove = directionsCanGo[0]
    else:
        #print("No moves to choose from")
        currMove = 'up'
    #print("CurrMove")
    #print (currMove)
    data = {'move': currMove, 'taunt': currTaunt}
    ret = json.dumps(data)

    return ret


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    port = '8080'
    if len(sys.argv) > 1:
        port = sys.argv[1]
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', port))