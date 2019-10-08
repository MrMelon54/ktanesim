import modules
import random


class ConnectionCheck(modules.Module):
    identifiers = ['connectionCheck']
    display_name = "Connection Check"
    manual_name = "Connection Check"
    help_text = "Submit an answer with `{cmd} submit red green true false` - top left first, then top right, bottom left, bottom right. You can also use any of: `yes no y n t f r g`. Spaces between single letters are optional."
    module_score = 6

    GRAPHS = {}
    for code, graph in [
        ('7HPJ', {(1, 2), (2, 3), (1, 3), (4, 6), (5, 6), (5, 7), (4, 7)}),
        ('34XYZ', {(1, 4), (1, 2), (1, 6), (2, 3), (2, 4), (4, 7), (6, 7), (7, 8), (6, 8), (5, 6)}),
        ('SLIM', {(1, 2), (1, 3), (1, 6), (2, 6), (3, 6), (3, 4), (4, 6), (5, 6), (4, 5), (4, 8), (4, 7), (5, 7), (7, 8)}),
        ('15BRO', {(1, 7), (1, 2), (2, 7), (6, 7), (5, 6), (5, 7), (4, 8), (3, 8), (3, 4)}),
        ('8CAKE', {(1, 3), (2, 4), (3, 6), (1, 2), (3, 4), (3, 7), (4, 7), (5, 7), (7, 8), (4, 5), (3, 8), (5, 8), (1, 8), (1, 6), (2, 6), (4, 6)}),
        ('9QVN', {(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (1, 8), (2, 7), (3, 6), (2, 6), (3, 7), (1, 4), (5, 8)}),
        ('20DGT', {(1, 3), (3, 5), (5, 7), (2, 7), (2, 4), (4, 6), (6, 8), (3, 7), (4, 7), (4, 8), (1, 2), (5, 6)}),
        ('6WUF', {(2, 3), (3, 8), (3, 5), (3, 6), (4, 5), (4, 7), (4, 8), (5, 7), (5, 6), (7, 8), (2, 8), (6, 7), (1, 6), (1, 7), (1, 2), (2, 7)}),
    ]:
        for letter in code:
            GRAPHS[letter] = graph

    def __init__(self, bomb, ident):
        super().__init__(bomb, ident)
        pairs = []
        for a in range(1, 9):
            for b in range(a + 1, 9):
                pairs.append((a, b))
        self.pairs = random.sample(pairs, 4)
        self.swap = [random.random() > 0.5 for _ in range(4)]
        self.on = [random.random() > 0.5 for _ in range(4)]
        self.log(f"Pairs: {self.pairs!r}")
        numbers = sum(map(list, self.pairs), [])
        batteries = self.bomb.get_battery_count()
        self.log(f"Batteries: {batteries}")
        if len(set(numbers)) == 8:
            self.log("All numbers are distinct")
            letter = self.bomb.serial[-1]
        elif numbers.count(1) > 1:
            self.log("There's more than one '1'")
            letter = self.bomb.serial[0]
        elif numbers.count(7) > 1:
            self.log("There's more than one '7'")
            letter = self.bomb.serial[-1]
        elif numbers.count(2) >= 3:
            self.log("There are exactly three '2's")
            letter = self.bomb.serial[1]
        elif 5 not in numbers:
            self.log("There is no 5 on the module")
            letter = self.bomb.serial[4]
        elif numbers.count(8) == 2:
            self.log("There are exactly two '8's")
            letter = self.bomb.serial[2]
        elif batteries > 6 or not batteries:
            self.log("More than 6 batteries or none")
            letter = self.bomb.serial[-1]
        else:
            self.log("1-6 batteries rule")
            letter = self.bomb.serial[batteries - 1]

        self.log(f"Letter: {letter}")
        graph = ConnectionCheck.GRAPHS[letter]
        self.expected = [pair in graph for pair in self.pairs]
        self.log(f"Expected: {self.expected!r}")

    def get_svg(self, led):
        svg = ('<svg viewBox="0 0 348 348" fill="#fff" stroke-width="2" stroke-linejoin="round" stroke-linecap="butt" stroke-miterlimit="10">'
               '<path stroke="#000" d="M5 5h338v338h-338z"/>'
               f'<circle fill="{led}" stroke="#000" cx="298" cy="40.5" r="15"/>'
               '<path stroke="#000" d="M38 45h200v60h-200z"/>'
               '<text text-anchor="middle" fill="#000" style="font-family:sans-serif;font-size:28pt;" x="138" y="89">CHECK</text>')

        for x, y, pair, swap, on in zip([18, 180, 18, 180], [144, 144, 243, 243], self.pairs, self.swap, self.on):
            if swap:
                b, a = pair
            else:
                a, b = pair

            svg += (f'<path stroke="#000" d="M{x} {y}h150v60h-150z"/>'
                    f'<path stroke="#000" fill="{"#0f0" if on else "#f00"}" d="M{x + 54} {y}h42v60h-42z"/>'
                    f'<text text-anchor="middle" fill="#000" style="font-family:sans-serif;font-size:32pt;" x="{x + 27}" y="{y + 46}">{a}</text>'
                    f'<text text-anchor="middle" fill="#000" style="font-family:sans-serif;font-size:32pt;" x="{x + 123}" y="{y + 46}">{b}</text>')
        svg += '</svg>'
        return svg

    @modules.check_solve_cmd
    async def cmd_submit(self, author, parts):
        parsed = []
        for part in parts:
            part = part.lower()
            if part in ['green', 'true', 'yes']:
                parsed.append(True)
            elif part in ['red', 'false', 'no']:
                parsed.append(False)
            else:
                for char in part:
                    if char in 'gty':
                        parsed.append(True)
                    elif char in 'rfn':
                        parsed.append(False)
                    else:
                        if part == char:
                            return await self.bomb.channel.send(f"{author.mention} What does `{part}` mean? Please use `g`, `t`, `y`, `r`, `f`, or `n`.")
                        else:
                            return await self.bomb.channel.send(f"{author.mention} What does `{char}` mean? Or did you mean `{part}`? Either way, please use `green`, `true`, `yes`, `red`, `false`, `no`, `g`, `t`, `y`, `r`, `f`, or `n`.")
        self.log(f"Parsed: {parsed!r}")
        if parsed:
            if len(parsed) > 4:
                return await self.bomb.channel.send(f"{author.mention} I need only 4 answers, and you gave me {len(parsed)}! That's way too much!")
            elif len(parsed) < 4:
                return await self.bomb.channel.send(f"{author.mention} Sorry, I only got {len(parsed)} out of 4 answers. Could you please repeat your solution to me?")
            else:
                self.on = parsed

        if self.on == self.expected:
            return await self.handle_solve(author)
        else:
            return await self.handle_strike(author)

    COMMANDS = {
        'submit': cmd_submit,
    }
