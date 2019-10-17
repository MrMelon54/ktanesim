import enum
import math
import random
import modules


class Maze(modules.Module):
    identifiers = ['maze']
    display_name = "Maze"
    manual_name = "Maze"
    help_text = "`{cmd} move up down left right`, `{cmd} move udlr` - make a series of moves."
    module_score = 2

    class Direction(enum.Flag):
        nothing = 0
        up = enum.auto()
        down = enum.auto()
        left = enum.auto()
        right = enum.auto()

    def parse(self, maze_string):
        lines = maze_string.strip().split('\n')
        self.grid = []
        self.markers = []
        for line in lines:
            cell_line = []
            for char in line:
                cell = Maze.Direction.nothing  # bits set have a wall
                if char in "─┌┐┬╴╷╶━┏┓┳╸╻╺":
                    cell |= Maze.Direction.up
                if char in "─└┘┴╴╵╶━┗┛┻╸╹╺":
                    cell |= Maze.Direction.down
                if char in "│┌└├╶╷╵┃┏┗┣╺╻╹":
                    cell |= Maze.Direction.left
                if char in "│┐┘┤╴╵╷┃┓┛┫╸╹╻":
                    cell |= Maze.Direction.right
                if char in "━┃┏┓┗┛┣┫┳┻╋╸╹╺╻":
                    self.markers.append((len(cell_line), len(self.grid)))
                cell_line.append(cell)
            self.grid.append(cell_line)

    MAZES = ["""
┌─┐┌─╴
┃┌┘└─┐
│└┐┌─┫
│╶┴┘╶┤
├─┐┌╴│
└╴└┘╶┘
""", """
╶┬╴┌┬╴
┌┘┌┘┗┐
│┌┘┌─┤
├┛┌┘╷│
│╷│┌┘│
╵└┘└─┘
""", """
┌─┐╷┌┐
╵╷│└┘│
┌┤│┌┐│
│││┃│┃
│└┘│││
└──┘└┘
""", """
┏┐╶──┐
││┌──┤
│└┘┌╴│
┃╶─┴─┤
├───┐│
└─╴╶┘╵
""", """
╶───┬┐
┌──┬┘╵
├┐╶┘┏┐
│└─┐╵│
│┌─┴╴│
╵└─━─┘
""", """
╷┌┐╶┳┐
│││┌┘│
├┘╵│┌┘
└┐┌┤│╷
┌┘╹│└┤
└──┘╶┘
""", """
┌━─┐┌┐
│┌╴└┘│
└┘┌╴┌┘
┌┐├─┘╷
│╵└─┐│
└━──┴┘
""", """
╷┌─┓┌┐
├┴╴└┘│
│┌──┐│
│└┓╶┴┘
│╷└──╴
└┴───╴
""", """
╷┌──┬┐
││┏╴││
├┴┘┌┘│
│╷┌┘╶┤
┃││┌┐╵
└┘└┘└╴
"""]

    def __init__(self, bomb, ident):
        super().__init__(bomb, ident)

        maze = random.choice(Maze.MAZES)
        self.parse(maze)
        self.visible_walls = ""
        self.position = random.randint(0, 5), random.randint(0, 5)
        while True:
            self.goal = random.randint(0, 5), random.randint(0, 5)
            if abs(self.position[0] - self.goal[0]) > 1 or abs(self.position[1] - self.goal[1]) > 1:
                break
        self.log(f"Goal: {self.goal}. Maze chosen:\n{maze}")

    def get_svg(self, led):
        svg = (
            f'<svg viewBox="0 0 348 348" fill="none" stroke="none" stroke-width="2" stroke-linecap="butt" stroke-linejoin="round" stroke-miterlimit="10">'
            f'<path stroke="#000" fill="#fff" d="M5 5h338v338h-338z"/>'
            f'<circle fill="{led}" stroke="#000" cx="298" cy="40.5" r="15"/>'
            f'<path fill="#000" stroke="#000" d="M59 59h230v230h-230zM44 148l-24 26 24 26zM304 148l24 26-24 24zM148 44l26-24 26 24zM148 304l26 24 26-24z"/>'
            f'<path fill="#444" d="M81 81h11v11h-11zm35 0h11v11h-11zm35 0h11v11h-11zm35 0h11v11h-11zm35 0h11v11h-11zm35 0h11v11h-11zm-175 35h11v11h-11zm35 0h11v11h-11zm35 0h11v11h-11zm35 0h11v11h-11zm35 0h11v11h-11zm35 0h11v11h-11zm-175 35h11v11h-11zm35 0h11v11h-11zm35 0h11v11h-11zm35 0h11v11h-11zm35 0h11v11h-11zm35 0h11v11h-11zm-175 35h11v11h-11zm35 0h11v11h-11zm35 0h11v11h-11zm35 0h11v11h-11zm35 0h11v11h-11zm35 0h11v11h-11zm-175 35h11v11h-11zm35 0h11v11h-11zm35 0h11v11h-11zm35 0h11v11h-11zm35 0h11v11h-11zm35 0h11v11h-11zm-175 35h11v11h-11zm35 0h11v11h-11zm35 0h11v11h-11zm35 0h11v11h-11zm35 0h11v11h-11zm35 0h11v11h-11z"/>'
            f'<path fill="#fff" d="M{81 + self.position[0] * 35} {81 + self.position[1] * 35}h11v11h-11z"/>'
            # hide the dot behind the goal triangle
            f'<path fill="#000" d="M{81 + self.goal[0] * 35} {81 + self.goal[1] * 35}h11v11h-11z"/>'
            f'<path stroke-width="6" stroke-linecap="square" stroke="#f00" d="{self.visible_walls}"/>')

        for marker in self.markers:
            svg += f'<circle stroke="#0f0" cx="{86 + marker[0] * 35}.5" cy="{86 + marker[1] * 35}.5" r="15"/>'

        goal_rotation = random.random() * math.pi * 2
        goal_x = 86.5 + self.goal[0] * 35
        goal_y = 86.5 + self.goal[1] * 35
        goal_ax = goal_x + math.cos(goal_rotation) * 12
        goal_ay = goal_y + math.sin(goal_rotation) * 12
        goal_bx = goal_x + math.cos(goal_rotation + 2 * math.pi / 3) * 12
        goal_by = goal_y + math.sin(goal_rotation + 2 * math.pi / 3) * 12
        goal_cx = goal_x + math.cos(goal_rotation + 4 * math.pi / 3) * 12
        goal_cy = goal_y + math.sin(goal_rotation + 4 * math.pi / 3) * 12

        svg += (f'<path fill="#f00" d="M{goal_ax} {goal_ay}L{goal_bx} {goal_by} {goal_cx} {goal_cy}"/>'
                f'</svg>')

        return svg

    @modules.check_solve_cmd
    async def cmd_move(self, author, parts):
        moves = []
        short_names = {x.name[:1]: x for x in Maze.Direction}
        for part in parts:
            try:
                moves.append(Maze.Direction[part])
            except KeyError:
                for letter in part:
                    try:
                        moves.append(short_names[letter])
                    except KeyError:
                        return await self.bomb.channel.send(f"{author.mention} Neither `{part}` nor `{letter}` is a valid direction!")

        self.log(f"Parsed: {' '.join(move.name for move in moves)}")
        for move in moves:
            self.log(f"Current position: {self.position}. Moving {move.name}")
            cell = self.grid[self.position[1]][self.position[0]]

            dx, dy = {
                Maze.Direction.up:    (0, -1),
                Maze.Direction.down:  (0, 1),
                Maze.Direction.left:  (-1, 0),
                Maze.Direction.right: (1, 0),
            }[move]

            newx, newy = self.position[0] + dx, self.position[1] + dy

            if newx not in range(6) or newy not in range(6):
                continue

            if cell & move:
                dx, dy, direction = {
                    Maze.Direction.up:    (69,  69,  'h'),
                    Maze.Direction.down:  (69,  104, 'h'),
                    Maze.Direction.left:  (69,  69,  'v'),
                    Maze.Direction.right: (104, 69,  'v'),
                }[move]

                self.visible_walls += f"M{dx + self.position[0] * 35} {dy + self.position[1] * 35}{direction}35"
                return await self.handle_strike(author)
            else:
                self.position = newx, newy

                if self.position == self.goal:
                    return await self.handle_solve(author)

        return await self.do_view(author.mention)

    COMMANDS = {
        "move": cmd_move,
    }
