import random
import modules


class Switches(modules.Module):
    identifiers = ['switches']
    display_name = "Switches"
    manual_name = "Switches"
    help_text = "`{cmd} flip 1 5 3 4 2 5 2` or `{cmd} flip 1534252`. Partial solutions allowed."
    module_score = 1

    def __init__(self, bomb, ident):
        super().__init__(bomb, ident)

        self.invalidPositions = "11011/10100/10000/01101/01100/01000/00111/00101/00011/00001".split("/")

        self.solution = "10000"
        while self.solution in self.invalidPositions:
            self.solution = ''.join([str(random.randint(0, 1)) for i in range(5)])

        self.switches = "10000"
        while self.switches in self.invalidPositions or self.switches == self.solution:
            self.switches = ''.join([str(random.randint(0, 1)) for i in range(5)])

        self.positionNames = ["up", "down"]

        self.log(f"Solution: {' '.join(map(lambda x:self.positionNames[int(x)],list(self.solution)))}")

    def generateSwitch(self, index):
        default = [[50.5, 174], [65.5, 174], [73, 234], [43, 234]]
        position = list(map(lambda x: [x[0] + 58 * index, x[1]], default))
        if self.switches[index] == "0":
            position[2][1] = 348 - position[2][1]
            position[3][1] = 348 - position[3][1]

        position = map(lambda x: map(lambda y: str(y), x), position)

        o = f'<circle stroke-width="2" stroke="#000" cx="{58*(index+1)}" cy="174" r="15" />'
        o += f'<circle stroke-width="2" stroke="#000" fill="{"#0f0" if self.solution[index]=="0" else "#fff"}" cx="{58*(index+1)}" cy="87" r="10" />'
        o += f'<circle stroke-width="2" stroke="#000" fill="{"#0f0" if self.solution[index]=="1" else "#fff"}" cx="{58*(index+1)}" cy="261" r="10" />'
        o += f'<polygon points="{" ".join(list(map(lambda x:",".join(x),position)))}" style="fill:black;stroke:black;stroke-width:2" />'

        return o

    def get_svg(self, led):
        return (f'<svg viewBox="0 0 348 348" fill="#fff" stroke-linecap="butt" stroke-linejoin="round" stroke-miterlimit="10" xmlns:xlink="http://www.w3.org/1999/xlink">'
                f'<path stroke="#000" stroke-width="2" d="M5 5h338v338h-338z"/>'
                f'<circle fill="{led}" stroke="#000" cx="298" cy="40.5" r="15" stroke-width="2"/>'

                f'{self.generateSwitch(0)}'
                f'{self.generateSwitch(1)}'
                f'{self.generateSwitch(2)}'
                f'{self.generateSwitch(3)}'
                f'{self.generateSwitch(4)}'

                f'</svg>')

    def flip_switch_by_index(self, index):
        splitSwitches = list(self.switches)
        splitSwitches[index] = "1" if splitSwitches[index] == "0" else "0"
        self.switches = "".join(splitSwitches)

    @modules.check_solve_cmd
    async def cmd_flip(self, author, parts):
        if not parts:
            return await self.usage(author)

        input_ = []

        for part in parts:
            if part.isdigit():
                for digit in part:
                    switch = int(digit)
                    if switch not in range(1, 6):
                        return await self.bomb.channel.send(f"{author.mention} There is no switch {switch}! There are five switches: 1-5.")
                    input_.append(switch - 1)
            else:
                return await self.bomb.channel.send(f"{author.mention} No such switch: `{part}`")

        while input_ and not self.solved:
            press = input_.pop(0)
            self.flip_switch_by_index(press)
            if self.switches in self.invalidPositions:
                self.flip_switch_by_index(press)
                await self.handle_strike(author)
                return
            if self.switches == self.solution:
                return await self.handle_solve(author)
        await self.do_view(author.mention)

    COMMANDS = {
        "flip": cmd_flip
    }
