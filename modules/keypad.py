import random
import modules

class Keypad(modules.Module):
    identifiers = ['keypad']
    display_name = "Keypad"
    manual_name = "Keypad"
    help_text = "`{cmd} press 1 3 2 4` or `{cmd} press 1324` or `{cmd} press tl bl tr br`. Partial solutions allowed."
    module_score = 1
    vanilla = True

    BUTTONS = ['tl', 'tr', 'bl', 'br']

    def __init__(self, bomb, ident):
        super().__init__(bomb, ident)

        self.column = random.choice([
            ["q", "at", "lambda", "lightning", "kitty", "h", "mirrorc"],
            ["euro", "q", "mirrorc", "ce", "hollowstar", "h", "questionmark"],
            ["copyright", "eye", "ce", "k", "r", "lambda", "hollowstar"],
            ["six", "paragraph", "bt", "kitty", "k", "questionmark", "smiley"],
            ["pitchfork", "smiley", "bt", "normalc", "paragraph", "three", "fullstar"],
            ["six", "euro", "tracks", "ae", "pitchfork", "n", "omega"]])

        self.log(f"Precedence list: {' '.join(self.column)}")
        self.buttons = random.sample(self.column, 4)
        self.log(f"Buttons: {' '.join(self.buttons)}")
        self.led = ['#000'] * 4
        self.progress = 0
        self.solution = []

        for button in self.column:
            if button in self.buttons:
                self.solution.append(self.buttons.index(button))
        self.log(f"Solution: {' '.join(map(str, self.solution))}")

    def get_svg(self, led):
        return (f'<svg viewBox="0 0 348 348" fill="#fff" stroke-linecap="butt" stroke-linejoin="round" stroke-miterlimit="10" xmlns:xlink="http://www.w3.org/1999/xlink">'
            f'<path stroke="#000" stroke-width="2" d="M5 5h338v338h-338z"/>'
            f'<path stroke="#000" d="M38 96h100v100h-100zM144 96h100v100h-100zM38 202h100v100h-100zM144 202h100v100h-100z"/>'
            f'<circle fill="{led}" stroke="#000" cx="298" cy="40.5" r="15" stroke-width="2"/>'
            f'<image xlink:href="img/keypad/{self.buttons[0]}.png" width="90" height="90" x="43" y="105"/>'
            f'<image xlink:href="img/keypad/{self.buttons[1]}.png" width="90" height="90" x="149" y="105"/>'
            f'<image xlink:href="img/keypad/{self.buttons[2]}.png" width="90" height="90" x="43" y="211"/>'
            f'<image xlink:href="img/keypad/{self.buttons[3]}.png" width="90" height="90" x="149" y="211"/>'
            f'<path stroke="#000" fill="{self.led[0]}" stroke-width="2" d="M78 102h20v6h-20z"/>'
            f'<path stroke="#000" fill="{self.led[1]}" stroke-width="2" d="M184 102h20v6h-20z"/>'
            f'<path stroke="#000" fill="{self.led[2]}" stroke-width="2" d="M78 208h20v6h-20z"/>'
            f'<path stroke="#000" fill="{self.led[3]}" stroke-width="2" d="M184 208h20v6h-20z"/>'
            f'</svg>')

    @modules.check_solve_cmd
    async def cmd_press(self, author, parts):
        if not parts:
            return await self.usage(author)

        input_ = []
        for part in parts:
            part = part.lower()
            if part.isdigit():
                self.log(f"Digit input: {part}")
                for digit in part:
                    button = int(digit)
                    if button not in range(1, 5):
                        return await self.bomb.channel.send(f"{author.mention} There is no button {button}! There are four buttons: 1-4.")
                    input_.append(button - 1)
            elif part in Keypad.BUTTONS:
                self.log(f"Named input: {part}")
                input_.append(Keypad.BUTTONS.index(part))
            else:
                return await self.bomb.channel.send(f"{author.mention} No such button: `{part}`")

        self.log(f"Parsed input: {' '.join(map(str, input_))}")
        while input_ and not self.solved:
            press = input_.pop(0)
            expected = self.solution[self.progress]
            self.log(f"Stage {self.progress}, expected {expected}, got {press}")
            if expected == press:
                self.log("Correct button pressed")
                self.led[press] = '#0f0'
                self.progress += 1
                if self.progress == 4:
                    await self.handle_solve(author)
                    return
            else:
                if self.led[press] == '#0f0':
                    self.log(f"Button {press} has already been pressed, ignoring")
                else:
                    self.led[press] = '#f00'
                    await self.handle_strike(author)
                    self.led[press] = '#000'
                    return
        await self.do_view(author.mention)

    COMMANDS = {
        "press": cmd_press
    }
