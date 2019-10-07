import modules
import random
import enum
import math

class Hexamaze(modules.Module):
    identifiers = ['hexamaze']
    display_name = "Hexamaze"
    manual_name = "Hexamaze"
    help_text = "Specify movements as clockface (`{cmd} move 12 2 6 4 8`), cardinal (`{cmd} move n ne s se sw`) or directions (`{cmd} move up upleft downright` or `{cmd} move u ul dr`)."
    module_score = 12

    class Marking(enum.Enum):
        hexagon = enum.auto()
        circle = enum.auto()
        triangle_left = enum.auto()
        triangle_right = enum.auto()
        triangle_up = enum.auto()
        triangle_down = enum.auto()

    MARKING_ROTATE = {
        Marking.hexagon:        Marking.hexagon,
        Marking.circle:         Marking.circle,
        Marking.triangle_left:  Marking.triangle_right,
        Marking.triangle_right: Marking.triangle_left,
        Marking.triangle_up:    Marking.triangle_down,
        Marking.triangle_down:  Marking.triangle_up,
    }

    MOVES = [(-1, 0), (0, -1), (1, -1), (1, 0), (0, 1), (-1, 1)]
    EDGES = [
        [(-x, -3 + x) for x in range(4)],
        [(x, -3) for x in range(4)],
        [(3, -x) for x in range(4)],
        [(x, 3 - x) for x in range(4)],
        [(-x, 3) for x in range(4)],
        [(-3, x) for x in range(4)],
    ]

    PAWN_COLORS = ['#f00', '#ff0', '#0f0', '#0cc', '#00f', '#f0f']

    MARKINGS = {
        (0, 0):   Marking.hexagon,
        (-8, 7):  Marking.triangle_left,
        (-5, 8):  Marking.hexagon,
        (5, -5):  Marking.circle,
        (-3, -3): Marking.triangle_down,
        (5, 3):   Marking.triangle_right,
        (-6, 1):  Marking.circle,
        (2, -7):  Marking.triangle_up,
        (-6, 4):  Marking.circle,
        (-9, 4):  Marking.hexagon,
        (-1, 5):  Marking.triangle_right,
        (6, -8):  Marking.triangle_left,
        (5, -1):  Marking.triangle_down,
        (2, 4):   Marking.circle,
        (3, -2):  Marking.hexagon,
        (-2, 8):  Marking.circle,
        (8, -4):  Marking.hexagon,
        (-3, 1):  Marking.triangle_up,
        (-1, -6): Marking.triangle_right,
    }

    WALLS = {
        (0, 0): [True, False, True], (0, -1): [False, True, False], (1, -1): [True, False, True], (2, -1): [False, False, False], (3, -1): [False, True, True], (4, -1): [False, True, True],
        (5, -1): [False, False, True], (6, -2): [False, True, True], (8, -3): [False, False, False], (9, -3): [False, True, True], (8, -2): [False, True, False], (7, -1): [True, False, True],
        (6, 0): [False, True, False], (5, 0): [False, True, False], (5, 1): [False, False, True], (6, 1): [True, True, False], (8, 0): [False, False, True], (8, -1): [True, False, False],
        (9, -2): [True, True, False], (10, -3): [True, True, False], (11, -3): [True, True, True], (10, -2): [False, True, False], (11, -2): [True, True, True], (10, -1): [True, False, False],
        (11, -1): [True, True, True], (10, 0): [True, True, False], (10, 1): [True, False, False], (9, 2): [True, True, True], (8, 3): [True, False, False], (8, 2): [False, True, True],
        (7, 3): [True, False, True], (6, 4): [True, False, True], (7, 4): [False, True, True], (6, 5): [True, True, False], (5, 6): [False, True, False], (4, 7): [True, False, True],
        (3, 8): [False, True, True], (1, 9): [True, True, False], (1, 10): [True, True, False], (0, 10): [True, False, True], (0, 9): [True, False, False], (1, 8): [True, True, False],
        (2, 7): [True, False, True], (2, 6): [True, False, True], (1, 6): [False, False, True], (-1, 7): [True, False, True], (-2, 8): [True, False, True], (-2, 9): [True, False, True],
        (-3, 10): [True, True, False], (-3, 11): [True, False, True], (-2, 11): [False, True, True], (-2, 10): [True, True, False], (-1, 9): [True, False, True], (-1, 8): [False, True, False],
        (0, 8): [True, False, True], (-1, 10): [True, False, True], (-1, 11): [True, False, True], (0, 11): [False, True, True], (-4, 11): [True, False, True], (-5, 11): [False, True, False],
        (-6, 11): [False, True, True], (-7, 11): [False, True, True], (-8, 11): [False, False, True], (-8, 10): [True, True, False], (-7, 9): [False, True, False], (-8, 9): [False, False, True],
        (-8, 8): [False, False, True], (-9, 8): [True, True, True], (-10, 8): [True, True, False], (-9, 7): [True, True, False], (-8, 6): [False, True, False], (-8, 7): [True, False, False],
        (-6, 6): [True, True, False], (-7, 7): [True, True, False], (-7, 8): [True, False, False], (-6, 7): [True, True, False], (-4, 6): [False, True, False], (-4, 7): [False, False, True],
        (-6, 8): [True, True, False], (-5, 8): [True, False, True], (-5, 9): [True, False, True], (-5, 10): [True, False, False], (-6, 10): [True, False, True], (-7, 10): [True, True, False],
        (-3, 9): [True, False, True], (-3, 8): [True, True, False], (-2, 7): [True, True, False], (-1, 6): [False, True, True], (-3, 7): [True, False, False], (-4, 8): [True, False, False],
        (-3, 6): [True, False, True], (-3, 5): [True, True, False], (-2, 4): [True, True, False], (0, 3): [False, False, True], (0, 4): [True, False, True], (1, 4): [True, False, True],
        (1, 5): [False, False, False], (2, 4): [True, False, True], (2, 3): [True, False, False], (4, 2): [False, False, True], (5, 2): [True, True, False], (4, 3): [True, True, False],
        (5, 3): [False, True, False], (6, 3): [True, False, True], (5, 4): [False, True, True], (4, 5): [False, False, True], (3, 5): [False, True, True], (2, 5): [False, True, False],
        (3, 4): [True, False, False], (3, 6): [True, False, True], (3, 7): [True, False, True], (5, 5): [False, True, True], (6, 2): [True, True, False], (8, 1): [False, True, True],
        (9, 1): [False, False, False], (9, 0): [True, False, True], (4, 1): [False, False, True], (4, 0): [False, True, True], (2, 1): [False, True, True], (3, 1): [False, True, True],
        (2, 2): [False, True, False], (1, 2): [True, False, True], (1, 1): [False, True, True], (0, 1): [True, False, False], (2, 0): [False, True, False], (0, 2): [False, False, True],
        (-2, 3): [True, True, False], (-3, 4): [True, True, False], (-4, 5): [False, True, False], (-5, 5): [True, False, False], (-4, 4): [True, True, False], (-3, 3): [True, True, False],
        (-4, 3): [True, False, False], (-5, 3): [True, False, False], (-5, 2): [True, False, True], (-6, 2): [False, False, True], (-6, 3): [False, False, True], (-7, 4): [True, True, False],
        (-6, 4): [False, False, False], (-7, 5): [False, True, False], (-8, 5): [False, False, True], (-10, 6): [True, False, False], (-11, 6): [True, False, True], (-11, 7): [False, False, True],
        (-11, 8): [True, False, False], (-11, 9): [True, False, True], (-11, 10): [True, False, True], (-11, 11): [True, True, False], (-9, 10): [False, False, True], (-9, 9): [False, True, True],
        (-10, 11): [True, True, False], (-9, 11): [True, True, True], (-11, 5): [True, True, False], (-10, 4): [True, True, False], (-11, 4): [True, True, False], (-10, 3): [True, True, False],
        (-10, 2): [True, False, False], (-11, 2): [True, True, True], (-10, 1): [True, False, True], (-10, 0): [True, False, True], (-10, -1): [True, True, True], (-9, -2): [True, True, False],
        (-7, -3): [False, True, True], (-6, -3): [False, True, True], (-5, -3): [False, False, False], (-4, -4): [True, True, True], (-3, -4): [False, False, False], (-4, -3): [True, True, False],
        (-5, -2): [True, True, False], (-5, -1): [False, False, False], (-4, -2): [True, True, False], (-2, -3): [False, False, True], (-1, -3): [False, False, True], (-1, -2): [False, False, True],
        (-2, -2): [False, True, True], (-4, -1): [True, True, False], (-3, -1): [False, True, True], (-2, -1): [False, True, True], (-1, -1): [False, False, False], (-1, 0): [False, False, True],
        (-3, 1): [False, True, True], (-2, 1): [False, True, True], (-1, 1): [False, False, True], (-2, 2): [True, True, False], (-4, 1): [True, False, True], (-4, 0): [False, True, True],
        (-6, 1): [False, True, False], (-7, 1): [True, True, False], (-6, 0): [False, True, False], (-7, 0): [False, True, True], (-7, -1): [False, True, True], (-8, -1): [False, True, True],
        (-9, -1): [True, True, True], (-7, -2): [False, True, True], (-6, -2): [False, True, False], (-6, -1): [False, False, True], (-9, 0): [True, True, True], (-8, 0): [False, True, True],
        (-9, 1): [True, True, False], (-9, 2): [True, False, True], (-9, 3): [True, False, True], (-8, 3): [False, True, True], (-8, 4): [False, False, True], (-7, 3): [False, True, True],
        (-7, 2): [False, True, True], (-8, 2): [True, False, True], (-3, 0): [False, True, True], (0, -2): [True, False, False], (1, -3): [True, False, True], (2, -4): [False, True, True],
        (3, -4): [False, True, True], (2, -3): [False, True, True], (3, -3): [False, True, True], (4, -3): [False, False, True], (4, -2): [False, False, False], (5, -3): [True, False, False],
        (5, -4): [True, False, False], (6, -4): [True, True, False], (7, -4): [True, True, False], (6, -3): [True, True, False], (8, -4): [False, True, False], (9, -5): [True, True, False],
        (10, -6): [True, True, False], (11, -7): [True, False, True], (11, -8): [False, True, False], (10, -7): [True, True, True], (9, -6): [False, True, False], (8, -5): [True, False, True],
        (8, -6): [True, True, False], (9, -7): [False, True, True], (7, -6): [True, False, False], (7, -7): [True, False, False], (8, -8): [True, True, True], (7, -8): [False, False, True],
        (8, -9): [False, True, True], (9, -9): [False, True, True], (10, -9): [False, True, False], (11, -9): [True, True, True], (11, -10): [False, True, True], (10, -10): [False, True, True],
        (9, -10): [False, False, True], (8, -10): [False, False, True], (8, -11): [True, True, True], (6, -10): [False, True, False], (5, -10): [True, True, False], (6, -11): [False, True, True],
        (5, -11): [False, True, True], (4, -11): [False, True, True], (3, -11): [False, True, False], (2, -10): [True, False, True], (3, -10): [True, True, True], (3, -9): [True, False, False],
        (4, -9): [True, False, False], (3, -8): [True, True, False], (2, -7): [True, True, False], (3, -7): [False, True, False], (5, -8): [False, False, True], (4, -7): [True, True, True],
        (3, -6): [True, False, False], (3, -5): [False, False, False], (4, -5): [False, False, False], (5, -6): [True, False, False], (6, -7): [True, False, True], (6, -8): [False, False, True],
        (6, -9): [True, True, False], (5, -7): [False, True, True], (6, -6): [True, False, True], (5, -5): [True, True, False], (4, -4): [False, False, False], (2, -5): [False, False, True],
        (1, -5): [False, True, True], (-1, -4): [True, False, True], (-1, -5): [False, True, True], (-2, -5): [True, False, True], (-1, -6): [False, False, False], (0, -7): [True, True, False],
        (-1, -7): [True, True, False], (1, -8): [False, True, False], (2, -9): [False, True, True], (1, -9): [False, False, False], (1, -10): [True, False, True], (1, -11): [True, True, True],
        (-1, -10): [True, True, False], (-1, -9): [True, False, False], (0, -9): [True, False, True], (-1, -8): [True, True, False], (-2, -7): [True, True, False], (-3, -6): [False, True, False],
        (-4, -5): [False, True, True], (-5, -5): [True, False, True], (-6, -5): [True, True, False], (-7, -4): [True, True, False], (-6, -4): [False, True, True], (-5, -6): [True, True, False],
        (-4, -7): [False, True, False], (-3, -8): [True, True, False], (-2, -8): [True, False, False], (-3, -7): [True, True, False], (-4, -6): [True, True, False], (-3, -5): [False, False, True],
        (2, -8): [True, False, False], (1, -7): [True, True, False], (1, -6): [False, False, False], (2, -6): [False, True, True], (-2, -4): [True, False, True], (0, -4): [True, False, True],
        (0, -3): [True, False, True], (10, -11): [False, True, True], (11, -11): [False, False, True], (9, -8): [True, True, False], (11, -6): [True, True, True], (10, -5): [True, True, False],
        (9, -4): [True, True, False], (10, -4): [False, True, False], (-11, 0): [False, True, False], (-11, 1): [True, True, False], (-11, 3): [True, False, False], (-6, 5): [True, True, False],
        (1, 3): [True, False, True], (0, 5): [False, False, True], (-1, 5): [False, True, True], (-2, 5): [False, True, False], (-8, 1): [True, False, True], (-8, -2): [True, True, True],
        (-9, 4): [True, True, True], (-5, 0): [True, True, False], (-5, 1): [True, False, True], (-9, 5): [True, True, True], (-10, 5): [True, False, True], (-9, 6): [True, True, True],
        (-7, 6): [True, True, False], (-10, 7): [True, True, False], (-5, 4): [True, True, False], (-12, 7): [True, True, True], (-12, 6): [True, True, True], (-12, 8): [True, True, True],
        (-12, 9): [True, True, True], (-10, 9): [True, True, True], (-5, 6): [True, True, False], (-5, 7): [False, True, True], (-6, 9): [True, False, True], (-8, 12): [True, False, True],
        (-9, 12): [True, True, True], (-4, 2): [True, False, True], (-3, 2): [True, True, False], (-4, 9): [True, True, False], (-2, 0): [False, True, True], (-4, 10): [True, False, True],
        (-5, -4): [False, True, True], (-8, -3): [True, False, True], (-3, -3): [True, True, True], (-3, -2): [True, False, True], (-1, 3): [False, True, True], (-1, 2): [True, False, True],
        (0, 6): [False, True, True], (-2, 6): [True, True, False], (-1, 4): [True, True, False], (-2, -6): [True, True, True], (0, -8): [True, True, True], (1, -2): [True, True, False],
        (0, -6): [False, True, True], (0, -5): [False, True, True], (1, -4): [True, False, True], (1, 0): [True, False, True], (0, 7): [True, False, True], (1, 7): [True, False, True],
        (-3, 12): [True, True, True], (-4, 12): [True, True, False], (-5, 12): [True, True, True], (-2, 12): [True, True, True], (-6, 12): [True, False, True], (3, 0): [False, True, True],
        (3, 2): [True, False, True], (3, 3): [True, False, True], (2, 8): [False, True, True], (-1, 12): [True, True, True], (2, -11): [True, True, True], (0, -10): [True, True, True],
        (0, -11): [False, True, True], (-2, -9): [True, True, True], (4, -6): [True, True, True], (2, -2): [True, False, True], (3, -2): [True, False, True], (1, 11): [True, True, True],
        (0, 12): [True, True, True], (2, 10): [True, True, True], (2, 9): [True, False, True], (3, 9): [False, True, True], (4, 8): [True, True, True], (4, -8): [True, True, True],
        (5, -9): [True, True, False], (4, -10): [True, True, True], (5, -2): [False, True, False], (6, -1): [False, True, True], (4, 4): [True, False, True], (4, 6): [False, True, True],
        (7, -9): [True, True, True], (6, -5): [True, True, False], (7, -5): [True, True, False], (7, -2): [False, True, True], (7, 2): [True, False, True], (7, -10): [True, True, True],
        (7, -3): [False, True, True], (7, 1): [True, False, True], (7, 0): [True, False, True], (9, -1): [True, False, True], (8, -7): [True, True, False], (10, -8): [False, True, False],
        (12, -10): [True, True, True], (12, -9): [True, True, True], (9, -11): [True, True, True], (12, -8): [True, True, True], (12, -11): [True, True, True], (12, -7): [True, True, True],
        (12, -6): [True, True, True], (11, -5): [True, True, True], (11, -4): [True, True, False], (12, -5): [True, True, True], (12, -4): [True, True, True], (12, -3): [False, True, True],
        (12, -2): [True, True, True], (12, -1): [True, True, True], (11, 0): [True, True, True], (-12, 5): [True, True, False], (-12, 10): [True, True, True], (-7, 12): [True, True, True],
        (5, 7): [True, False, True], (8, 4): [True, True, True], (7, 5): [True, True, True], (6, 6): [True, True, True], (9, 3): [True, True, True], (10, 2): [False, True, True],
        (11, 1): [True, True, True], (-12, 3): [True, True, True], (-12, 4): [True, True, True], (-12, 1): [True, True, True], (-12, 2): [True, True, True], (-10, 10): [True, True, True],
        (-10, 12): [True, True, True], (-11, 12): [True, True, True], (-12, 12): [True, True, True], (-12, 11): [True, True, False], (7, -11): [True, False, True], (12, 0): [True, True, True],
    }

    @staticmethod
    def get_neighbor(coords, direction):
        q, r = coords
        if direction == 0: q -= 1
        elif direction == 1: r -= 1
        elif direction == 2: q += 1; r -= 1
        elif direction == 3: q += 1
        elif direction == 4: r += 1
        elif direction == 5: q -= 1; r += 1
        return q, r

    @staticmethod
    def normalize_wall(coords, direction):
        if direction < 3:
            return coords, direction
        else:
            return Hexamaze.get_neighbor(coords, direction), direction % 3

    @staticmethod
    def big_has_wall(coords, direction):
        coords, direction = Hexamaze.normalize_wall(coords, direction)
        return Hexamaze.WALLS[coords][direction]

    @staticmethod
    def vertical_range(q, original):
        r_start = -original if q > 0 else -original - q
        r_end = original if q <= 0 else original - q
        return r_start, r_end

    @staticmethod
    def grid_iterate():
        for q in range(-3, 4):
            r_start, r_end = Hexamaze.vertical_range(q, 3)
            for r in range(r_start, r_end + 1):
                yield q, r

    @staticmethod
    def is_oob(coords):
        q, r = coords
        if q not in range(-3, 4): return True
        r_start, r_end = Hexamaze.vertical_range(q, 3)
        return r not in range(r_start, r_end + 1)

    def __init__(self, bomb, ident):
        super().__init__(bomb, ident)
        q = random.randint(-8, 8)
        r = random.randint(*Hexamaze.vertical_range(q, 8))
        self.maze_center = q, r
        self.maze_rotation = random.randint(0, 5)
        self.pawn_color = random.randint(0, 5)
        self.solution_edge = Hexamaze.EDGES[(self.maze_rotation + self.pawn_color) % 6]
        self.solution_directions = [(self.pawn_color + self.maze_rotation + x) % 6 for x in range(2)]
        self.visible_walls = set()

        position_options = set()

        for cell in Hexamaze.grid_iterate():
            if self.small2big(cell) not in Hexamaze.MARKINGS:
                position_options.add(cell)

        self.log(f"{len(position_options)} options")
        floodfill_queue = []
        floodfill_distances = {}

        # prevent straight-line solutions
        for edge_cell in self.solution_edge:
            for direction in self.solution_directions:
                if self.small_has_wall(edge_cell, direction): continue
                # prepare for the next stage of starting position pruning: save edge cells that are not surrounded by walls in the directions we care about
                if edge_cell not in floodfill_distances:
                    floodfill_distances[edge_cell] = 1
                    floodfill_queue.append(edge_cell)
                backwards = (direction + 3) % 6
                cell = edge_cell
                while not Hexamaze.is_oob(cell):
                    try:
                        position_options.remove(cell)
                    except KeyError:
                        pass

                    cell = self.can_move(cell, backwards)
                    if not cell: break

        self.log(f"{len(position_options)} options after straight-line pruning")

        # range-limited floodfill to make sure the solution is at least 4 steps long
        # floodfill_distances: a dictionary of {cell coordinates: how many steps would the solution have if the pawn was placed here}
        # floodfill_queue: a list of cells that we have explored, but didn't explore their neighbors

        while floodfill_queue:
            cell = floodfill_queue.pop(0)
            distance = floodfill_distances[cell]
            for neighbor in self.possible_moves(cell):
                # because floodfill_queue is a queue, the algorithm will never find a shorter path
                if neighbor in floodfill_distances: continue

                try:
                    position_options.remove(neighbor)
                except KeyError:
                    pass

                new_distance = distance + 1
                floodfill_distances[neighbor] = new_distance
                if new_distance < 3:
                    floodfill_queue.append(neighbor)

        self.log(f"{len(position_options)} options after solution length pruning")
        self.position = random.choice(list(position_options))
        self.log(f"Maze center: {self.maze_center!r}. "
            f"Maze rotation: {self.maze_rotation}. "
            f"Pawn color: {['red', 'yellow', 'green', 'cyan', 'blue', 'pink'][self.pawn_color]}. "
            f"Starting position: {self.position!r}. "
            f"Solution edge: {self.solution_edge!r}. "
            f"Solution directions: {self.solution_directions!r}.")

    def small2big(self, coords):
        q, r = coords
        if self.maze_rotation == 1: q, r = q + r, -q
        elif self.maze_rotation == 2: q, r = r, -q - r
        elif self.maze_rotation == 3: q, r = -q, -r
        elif self.maze_rotation == 4: q, r = -q - r, q
        elif self.maze_rotation == 5: q, r = -r, q + r
        return q + self.maze_center[0], r + self.maze_center[1]

    def small_has_wall(self, coords, direction):
        return Hexamaze.big_has_wall(self.small2big(coords), (direction - self.maze_rotation) % 6)

    def can_move(self, from_, direction):
        if self.small_has_wall(from_, direction):
            return False
        else:
            move = Hexamaze.MOVES[direction]
            return from_[0] + move[0], from_[1] + move[1]

    def possible_moves(self, from_):
        for direction in range(6):
            move = self.can_move(from_, direction)
            if move and not Hexamaze.is_oob(move): yield move

    EDGE = 23
    YSCALE = EDGE * math.sqrt(3) / 2
    XSCALE = EDGE * 3 / 2

    # precompute the border and buttons paths
    def generate_border(EDGE, XSCALE, YSCALE):
        sx = 174 - 5 * EDGE
        sy = 174 - 4 * YSCALE
        R = f"h{EDGE}"
        L = f"h-{EDGE}"
        UR = f"l{EDGE / 2}-{YSCALE}"
        UL = f"l-{EDGE / 2}-{YSCALE}"
        DR = f"l{EDGE / 2} {YSCALE}"
        DL = f"l-{EDGE / 2} {YSCALE}"
        return f"M{sx} {sy}" + f"{R}{UR}" * 3 + f"{R}{DR}" * 4 + f"{DL}{DR}" * 3 + f"{DL}{L}" * 4 + f"{UL}{L}" * 3 + f"{UL}{UR}" * 3 + f"{UL}z"
    BORDER_PATH = generate_border(EDGE, XSCALE, YSCALE)
    del generate_border

    def generate_buttons(EDGE, XSCALE, YSCALE):
        path = ""
        for button in range(6):
            angle = math.pi * button / 3
            cos = math.cos(angle)
            sin = math.sin(angle)
            ax = 174 + sin * (7 * YSCALE + 5) - cos * EDGE / 2
            ay = 174 - sin * EDGE / 2 - cos * (7 * YSCALE + 5)
            bx = cos * EDGE / 2 + sin * 7
            by = sin * EDGE / 2 - cos * 7
            cx = cos * EDGE / 2 - sin * 7
            cy = sin * EDGE / 2 + cos * 7
            path += f"M{ax} {ay}l{bx} {by} {cx} {cy}z"
        return path
    BUTTON_PATH = generate_buttons(EDGE, XSCALE, YSCALE)
    del generate_buttons

    def get_svg(self, led):
        def to_image_coords(cell):
            q, r = cell
            return 174 + q * Hexamaze.XSCALE, 174 + (q + 2 * r) * Hexamaze.YSCALE

        svg = ('<svg viewBox="0 0 348 348" fill="none" stroke-width="2" stroke-linejoin="round" stroke-linecap="butt" stroke-miterlimit="10" xmlns:xlink="http://www.w3.org/1999/xlink">'
            '<path stroke="#000" fill="#fff" d="M5 5h338v338h-338z"/>'
            f'<circle fill="{led}" stroke="#000" cx="298" cy="40.5" r="15"/>'
            f'<path id="display" stroke="#ccc" stroke-width="18" d="{Hexamaze.BORDER_PATH}"/>'
            f'<path stroke="#ccc" stroke-width="12" d="{Hexamaze.BUTTON_PATH}"/>'
            f'<path fill="#000" d="{Hexamaze.BORDER_PATH}{Hexamaze.BUTTON_PATH}"/>'
            '<clipPath id="clip">'
            '<use xlink:href="#display"/>'
            '</clipPath>'
            '<g clip-path="url(#clip)">')

        for cell in Hexamaze.grid_iterate():
            x, y = to_image_coords(cell)
            pawn = self.position == cell
            big_maze_coords = self.small2big(cell)
            MARKING_SCALE = 0.7
            if big_maze_coords in Hexamaze.MARKINGS:
                marking = Hexamaze.MARKINGS[big_maze_coords]
                # All markings have 120-degrees rotational symmetry
                if self.maze_rotation % 2 == 1:
                    marking = Hexamaze.MARKING_ROTATE[marking]
                if marking == Hexamaze.Marking.circle:
                    svg += f'<circle stroke="#fff" r="{Hexamaze.YSCALE * MARKING_SCALE}" cx="{x}" cy="{y}"/>'
                elif marking == Hexamaze.Marking.hexagon:
                    svg += (f'<path stroke="#fff" d="M{x - Hexamaze.EDGE * MARKING_SCALE / 2} {y - Hexamaze.YSCALE * MARKING_SCALE}'
                        f'h{Hexamaze.EDGE * MARKING_SCALE}'
                        f'l{Hexamaze.EDGE * MARKING_SCALE / 2} {Hexamaze.YSCALE * MARKING_SCALE}'
                        f'-{Hexamaze.EDGE * MARKING_SCALE / 2} {Hexamaze.YSCALE * MARKING_SCALE}'
                        f'h-{Hexamaze.EDGE * MARKING_SCALE}'
                        f'l-{Hexamaze.EDGE * MARKING_SCALE / 2}-{Hexamaze.YSCALE * MARKING_SCALE}z"/>')
                elif marking == Hexamaze.Marking.triangle_up:
                    svg += (f'<path stroke="#fff" d="M{x} {y - Hexamaze.YSCALE * MARKING_SCALE}'
                        f'l{Hexamaze.EDGE * MARKING_SCALE * 3 / 4} {Hexamaze.YSCALE * MARKING_SCALE * 3 / 2}'
                        f'h-{Hexamaze.EDGE * MARKING_SCALE * 3 / 2}z"/>')
                elif marking == Hexamaze.Marking.triangle_down:
                    svg += (f'<path stroke="#fff" d="M{x} {y + Hexamaze.YSCALE * MARKING_SCALE}'
                        f'l{Hexamaze.EDGE * MARKING_SCALE * 3 / 4}-{Hexamaze.YSCALE * MARKING_SCALE * 3 / 2}'
                        f'h-{Hexamaze.EDGE * MARKING_SCALE * 3 / 2}z"/>')
                elif marking == Hexamaze.Marking.triangle_left:
                    svg += (f'<path stroke="#fff" d="M{x - Hexamaze.YSCALE * MARKING_SCALE} {y}'
                        f'l{Hexamaze.YSCALE * MARKING_SCALE * 3 / 2} {Hexamaze.EDGE * MARKING_SCALE * 3 / 4}'
                        f'v-{Hexamaze.EDGE * MARKING_SCALE * 3 / 2}z"/>')
                elif marking == Hexamaze.Marking.triangle_right:
                    svg += (f'<path stroke="#fff" d="M{x + Hexamaze.YSCALE * MARKING_SCALE} {y}'
                        f'l-{Hexamaze.YSCALE * MARKING_SCALE * 3 / 2} {Hexamaze.EDGE * MARKING_SCALE * 3 / 4}'
                        f'v-{Hexamaze.EDGE * MARKING_SCALE * 3 / 2}z"/>')
                else:
                    assert False
            svg += f'<circle cx="{x}" cy="{y}" r="{6 if pawn else 4}" fill="{Hexamaze.PAWN_COLORS[self.pawn_color] if pawn else "#ccc"}"/>'

        wall_path = ""
        for cell, direction in self.visible_walls:
            x, y = to_image_coords(cell)
            if direction == 0:
                wall_path += f'M{x - Hexamaze.EDGE} {y}l{Hexamaze.EDGE / 2}-{Hexamaze.YSCALE}'
            elif direction == 1:
                wall_path += f'M{x - Hexamaze.EDGE / 2} {y - Hexamaze.YSCALE}h{Hexamaze.EDGE}'
            elif direction == 2:
                wall_path += f'M{x + Hexamaze.EDGE} {y}l-{Hexamaze.EDGE / 2}-{Hexamaze.YSCALE}'
            else:
                assert False
        svg += (f'<path stroke-linecap="round" stroke-width="4" stroke="#fff" d="{wall_path}"/>'
            '</g>'
            '</svg>')
        return svg

    MOVE_STRINGS = {
        '10': 0, 'nw': 0, 'upleft': 0, 'leftup': 0, 'ul': 0, 'lu': 0,
        '12': 1, 'n': 1, 'up': 1, 'u': 1,
        '2': 2, 'ne': 2, 'upright': 2, 'rightup': 2, 'ur': 2, 'ru': 2,
        '4': 3, 'se': 3, 'downright': 3, 'rightdown': 3, 'dr': 3, 'rd': 3,
        '6': 4, 's': 4, 'down': 4, 'd': 4,
        '8': 5, 'sw': 5, 'downleft': 5, 'leftdown': 5, 'dl': 5, 'ld': 5,
    }

    @modules.check_solve_cmd
    async def cmd_move(self, author, parts):
        moves = []
        for part in parts:
            try:
                moves.append(Hexamaze.MOVE_STRINGS[part])
            except KeyError:
                return await self.bomb.channel.send(f"{author.mention} Unknown direction: `{part}`.")
        self.log(f"Parsed: {moves!r}")
        for move in moves:
            self.log(f"Executing move: {move}")
            new_position = self.can_move(self.position, move)
            if new_position:
                if Hexamaze.is_oob(new_position):
                    if self.position in self.solution_edge and move in self.solution_directions:
                        self.position = new_position
                        return await self.handle_solve(author)
                    else:
                        self.log(f"Wrong edge!")
                        return await self.handle_strike(author)
                else:
                    self.position = new_position
            else:
                self.log("WALL!")
                if not Hexamaze.is_oob(Hexamaze.get_neighbor(self.position, move)):
                    self.visible_walls.add(Hexamaze.normalize_wall(self.position, move))
                return await self.handle_strike(author)
            self.log(f"Position: {self.position}")

        return await self.do_view(author.mention)

    COMMANDS = {
        "move": cmd_move,
    }
