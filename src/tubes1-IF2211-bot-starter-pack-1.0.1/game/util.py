from .models import Position
from game.models import Board, Position

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

def get_direction(current_x, current_y, dest_x, dest_y):
    delta_x = clamp(dest_x - current_x, -1, 1)
    delta_y = clamp(dest_y - current_y, -1, 1)
    if delta_x != 0:
        delta_y = 0
    return (delta_x, delta_y)

def position_equals(a: Position, b: Position):
    return a.x == b.x and a.y == b.y

def count_distance(current_x, current_y, dest_x, dest_y):
    delta_x = dest_x - current_x
    delta_y = dest_y - current_y
    return (abs(delta_x) + abs(delta_y))

def find_teleport(current_position, board: Board):
    teleport = [t for t in board.game_objects if (t.type=="TeleportGameObject")]
    list_teleport = []
    for position in teleport :
        distance = count_distance(current_position.x, current_position.y, position.position.x, position.position.y)
        list_teleport.append([distance,position.position])
    return list_teleport

def find_red_button(current_position, board: Board):
    button = [b for b in board.game_objects if (b.type=="DiamondButtonGameObject")]
    list_button = []
    for position in button :
        distance = count_distance(current_position.x, current_position.y, position.position.x, position.position.y)
        list_button.append([distance, position.position])
    return list_button

def find_red_diamond(current_position, board: Board):
    red_diamond = [r for r in board.game_objects if (r.type == "DiamondGameObject" and r.properties.points == 2)]
    list_red_diamond = []
    for position in red_diamond :
        distance = count_distance(current_position.x, current_position.y, position.position.x, position.position.y)
        list_red_diamond.append([distance, position.position])
    return list_red_diamond

def find_blue_diamond(current_position, board: Board):
    blue_diamond = [b for b in board.game_objects if (b.type == "DiamondGameObject" and b.properties.points == 1)]
    list_blue_diamond = []
    for position in blue_diamond :
        distance = count_distance(current_position.x, current_position.y, position.position.x, position.position.y)
        list_blue_diamond.append([distance, position.position])
    return list_blue_diamond

def find_diamond(current_position, board: Board):
    diamond = [d for d in board.game_objects if d.type == "DiamondGameObject"]
    list_diamond = []
    for position in diamond :
        distance = count_distance(current_position.x, current_position.y, position.position.x, position.position.y)
        list_diamond.append([distance, position.position])
    return list_diamond

def calc_distance(obj1, obj2):
    return abs(obj1.x - obj2.x) + abs(obj1.y - obj2.y)

def find_densest(diamonds, eps=1, min_samples=3):
    clusters = []
    visited = set()
    noise = set()

    def neighbors(diamond):
        return [other for other in diamonds if calc_distance(diamond.position, other.position) <= eps]

    for diamond in diamonds:
        if diamond.id in visited:
            continue
        visited.add(diamond.id)
        neighbor_diamonds = neighbors(diamond)
        if len(neighbor_diamonds) < min_samples:
            noise.add(diamond.id)
        else:
            cluster = []
            clusters.append(cluster)
            cluster.append(diamond)
            for neighbor in neighbor_diamonds:
                if neighbor.id in noise:
                    cluster.append(neighbor)
                    noise.remove(neighbor.id)
                if neighbor.id not in visited:
                    visited.add(neighbor.id)
                    more_neighbors = neighbors(neighbor)
                    if len(more_neighbors) >= min_samples:
                        neighbor_diamonds.extend(more_neighbors)
                    if neighbor not in cluster:
                        cluster.append(neighbor)
    return clusters

def getAllTeleporterSorted(board,current_position):
    teleport = [x for x in board.game_objects if (x.type == "TeleportGameObject")]
    
    # Group teleporters by their pair_id
    teleport_groups = {}
    for teleporter in teleport:
        pair_id = teleporter.properties.pair_id
        if pair_id not in teleport_groups:
            teleport_groups[pair_id] = []
        teleport_groups[pair_id].append(teleporter)

    # Sort each group of teleporters by their distance to the bot and store the distance
    sorted_teleport_groups = {}
    for pair_id, teleporters in teleport_groups.items():
        sorted_teleporters = sorted([(teleporter.position, abs(current_position.x - teleporter.position.x) + abs(current_position.y - teleporter.position.y)) for teleporter in teleporters], key=lambda t: t[1])
        sorted_teleport_groups[pair_id] = sorted_teleporters

    # Sort the sorted_teleport_groups dictionary based on the distance of the nearest teleporter in each group
    sorted_teleport_groups = dict(sorted(sorted_teleport_groups.items(), key=lambda item: item[1][0][1]))

    return sorted_teleport_groups

def findDistanceByBotAndBase(object,base,current_position):
    x = []
    y = []

    for position in object:
        posX = abs(base.x  - position.position.x)
        posY = abs(base.y - position.position.y)
        distance = (abs(base.x  - position.position.x) + abs(base.y - position.position.y))
        x.append([distance,position.position,[posX,posY],position.properties.points])
        posX = abs(current_position.x  - position.position.x)
        posY = abs(current_position.y - position.position.y)
        distance1 = (abs(current_position.x  - position.position.x) + abs(current_position.y - position.position.y))
        y.append([distance1,position.position,[posX,posY],position.properties.points])

    return x,y