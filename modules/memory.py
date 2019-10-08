import random
import modules


class Memory(modules.Module):
    identifiers = ['memory']
    display_name = "Memory"
    manual_name = "Memory"
    help_text = "`{cmd} pos 2` or `{cmd} position 2` - press the button in the second position. `{cmd} lab 4` or `{cmd} label 4` - press the button labeled \"4\"."
    module_score = 4
    vanilla = True

    def __init__(self, bomb, ident):
        super().__init__(bomb, ident)
        self.buttons = list(range(1, 5))
        self.initialize()

    def initialize(self):
        self.stage = 0
        self.pressed_positions = []
        self.pressed_labels = []
        self.randomize()

    def randomize(self):
        self.display = random.randint(1, 4)
        random.shuffle(self.buttons)
        self.log(
            f"Randomized on stage {self.stage}. Display is {self.display}. Buttons: {' '.join(map(str, self.buttons))}")

    def get_svg(self, led):
        svg = (
            f'<svg viewBox="0 0 348 348" fill="#fff" stroke="none" stroke-linejoin="round" stroke-linecap="butt" stroke-miterlimit="10">'
            f'<path stroke="#000" stroke-width="2" d="M5 5h338v338h-338z"/>'
            f'<circle fill="{led}" stroke="#000" cx="298" cy="40.5" r="15" stroke-width="2"/>'
            f'<path fill="#000" stroke="#000" d="M30 70h225v129h-225z"/>'
            f'<path stroke="#000" d="M30 210h48v70h-48zm59 0h48v70h-48zm59 0h48v70h-48zm59 0h48v70h-48z"/>'
            f'<path fill="#000" stroke="#000" d="M276 70h52v210h-52z"/>'
            f'<text x="142.5" y="165" text-anchor="middle" style="font-size:64pt;font-family:sans-serif;">{self.display}</text>')

        for stage in range(5):
            fill = '#0f0' if self.stage > stage else '#fff'
            svg += f'<path fill="{fill}" stroke="{fill}" d="M287 {242 - stage * 38}h30v18h-30z"/>'

        for button in range(4):
            svg += f'<text fill="#000" x="{54 + button * 59}" y="260" text-anchor="middle" style="font-size:32pt;font-family:sans-serif;">{self.buttons[button]}</text>'

        svg += f'</svg>'
        return svg

    async def handle_press(self, author, position):
        solution = self.get_solution()
        self.log(f"Player pressed position {position}, expected {solution}")

        if position == solution:
            self.stage += 1
            self.pressed_positions.append(position)
            self.pressed_labels.append(self.buttons[position])

            if self.stage == 5:
                await self.handle_solve(author)
            else:
                self.randomize()
                await self.handle_next_stage(author)
        else:
            self.initialize()
            await self.handle_strike(author)

    def get_solution(self):
        self.log(
            f"Position history: {' '.join(map(str, self.pressed_positions))}")
        self.log(f"Label history: {' '.join(map(str, self.pressed_labels))}")

        if self.stage == 0:
            return [1, 1, 2, 3][self.display - 1]
        elif self.stage == 1:
            if self.display == 1:
                return self.buttons.index(4)
            elif self.display == 3:
                return 0
            else:
                return self.pressed_positions[0]
        elif self.stage == 2:
            if self.display == 1:
                return self.buttons.index(self.pressed_labels[1])
            elif self.display == 2:
                return self.buttons.index(self.pressed_labels[0])
            elif self.display == 3:
                return 2
            else:
                return self.buttons.index(4)
        elif self.stage == 3:
            if self.display == 1:
                return self.pressed_positions[0]
            elif self.display == 2:
                return 0
            else:
                return self.pressed_positions[1]
        else:
            return self.buttons.index(self.pressed_labels[[0, 1, 3, 2][self.display - 1]])

    @modules.check_solve_cmd
    async def cmd_position(self, author, parts):
        if len(parts) != 1 or not parts[0].isdigit():
            return await self.usage(author)

        position = int(parts[0]) - 1

        if position not in range(4):
            return await self.bomb.channel.send(f"{author.mention} There are only four positions: 1-4.")

        await self.handle_press(author, position)

    @modules.check_solve_cmd
    async def cmd_label(self, author, parts):
        if len(parts) != 1 or not parts[0].isdigit():
            return await self.usage(author)

        label = int(parts[0])

        if label not in self.buttons:
            return await self.bomb.channel.send(f"{author.mention} There are only four labels: 1-4.")

        await self.handle_press(author, self.buttons.index(label))

    COMMANDS = {
        "position": cmd_position,
        "pos": cmd_position,
        "label": cmd_label,
        "lab": cmd_label,
    }
