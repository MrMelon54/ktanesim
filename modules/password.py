from string import ascii_lowercase as abc
from wand.image import Image
import modules
import random
import cairosvg


class Password(modules.Module):
    identifiers = ['password']
    display_name = "Password"
    manual_name = "Password"
    help_text = "`{cmd} cycle 3` - cycle the third column. `{cmd} cycle 1 3 5`, `{cmd} cycle 135` - cycle multiple columns. `{cmd} cycle` - cycle all columns. `{cmd} submit water` - try to submit a word. "
    module_score = 2
    vanilla = True

    WORDS = [
        "about", "after", "again", "below", "could",
        "every", "first", "found", "great", "house",
        "large", "learn", "never", "other", "place",
        "plant", "point", "right", "small", "sound",
        "spell", "still", "study", "their", "there",
        "these", "thing", "think", "three", "water",
        "where", "which", "world", "would", "write",
    ]

    def __init__(self, bomb, ident):
        super().__init__(bomb, ident)
        self.solution = random.choice(Password.WORDS)
        self.positions = [0] * 5
        self.log(f"Solution: {self.solution}")
        self.spinners = [list(abc) for _ in range(5)]
        self.cycle = None

        for match in self.get_matches():
            if match == self.solution:
                continue

            wrong_positions = [pos for pos in range(
                5) if match[pos] != self.solution[pos]]
            position = random.choice(wrong_positions)
            self.log(
                f"Removing false match by modifying column {position}: {match}")
            self.spinners[position].remove(match[position])

        for position in range(5):
            self.spinners[position].remove(self.solution[position])
            self.spinners[position] = random.sample(self.spinners[position], 5)
            self.spinners[position].append(self.solution[position])
            random.shuffle(self.spinners[position])

        assert list(self.get_matches()) == [self.solution]
        spinners_str = '\n'.join(''.join(map(str, x))
                                 for x in zip(*self.spinners))
        self.log(f"Spinners:\n\n{spinners_str}")

    def get_matches(self):
        for word in Password.WORDS:
            if self.can_set_word(word):
                yield word

    def can_set_word(self, word):
        for position, letter in enumerate(word):
            if letter not in self.spinners[position]:
                return False
        return True

    def get_image(self, led):
        svg = ('<svg viewBox="0 0 348 348" fill="none" stroke="none" stroke-width="2" stroke-linecap="butt" stroke-linejoin="round" stroke-miterlimit="10">'
               '<path stroke="#000" fill="#fff" d="M5 5h338v338h-338z"/>'
               f'<circle fill="{led}" stroke="#000" cx="298" cy="40.5" r="15"/>'
               '<path stroke="#000" d="M124 289h100v40h-100z"/>'
               '<text fill="#000" text-anchor="middle" x="174" y="317" style="font-family:sans-serif;font-size:16pt;">SUBMIT</text>'
               '<path fill="#000" stroke="#000" d="M44 99h260v150h-260zM74 80l3 5h-6zm50 0l3 5h-6zm50 0l3 5h-6zm50 0l3 5h-6zm50 0l3 5h-6zM74 268l3-5h-6zm50 0l3-5h-6zm50 0l3-5h-6zm50 0l3-5h-6zm50 0l3-5h-6z"/>'
               '<path fill="#fff" d="M50 105h48v138h-48zm50 0h48v138h-48zm50 0h48v138h-48zm50 0h48v138h-48zm50 0h48v138h-48z"/>')

        for pos, letters, index in zip(range(5), self.spinners, self.positions):
            x = 74 + pos * 50
            svg += (f'<circle cx="{x}" cy="83" r="9" stroke="#000"/>'
                    f'<circle cx="{x}" cy="265" r="9" stroke="#000"/>'
                    f'<text fill="#000" text-anchor="middle" x="{x}" y="188" style="font-family:sans-serif;font-size:28pt;">{letters[index].upper()}</text>')
        svg += '</svg>'
        return cairosvg.svg2png(svg.encode())

    def render(self, strike):
        if self.solved:
            return self.get_image('#0f0'), 'render.png'

        led = '#f00' if strike else '#fff'

        if self.cycle is None:
            return self.get_image('#f00' if strike else '#fff'), 'render.png'

        with Image() as im:
            for column in self.cycle:
                first = True
                for _ in range(6):
                    modules.gif_append(im, self.get_image(
                        led), 200 if first else 100)
                    first = False
                    self.positions[column] = (self.positions[column] + 1) % 6

            return modules.gif_output(im)

    @modules.check_solve_cmd
    async def cmd_submit(self, author, parts):
        if len(parts) != 1 or len(parts[0]) != 5 or not parts[0].isalpha():
            return await self.usage(author)

        word = parts[0].lower()
        for position, letter in enumerate(word):
            if letter in self.spinners[position]:
                self.positions[position] = self.spinners[position].index(
                    letter)
            else:
                return await self.handle_unsubmittable(author)

        if self.solution == word:
            return await self.handle_solve(author)
        else:
            return await self.handle_strike(author)

    @modules.check_solve_cmd
    async def cmd_cycle(self, author, parts):
        columns = []
        for part in parts:
            if not part.isdigit():
                return await self.bomb.channel.send(f"{author.mention} Specify columns with numbers please, not with whatever `{part}` is.")

            for digit in part:
                if int(digit) not in range(1, 6):
                    return await self.bomb.channel.send(f"{author.mention} There's no column {digit}, there's only 1, 2, 3, 4, and 5.")
                columns.append(int(digit) - 1)

        if not columns:
            columns = list(range(5))

        self.log(f"Cycling columns: {' '.join(map(str, columns))}")
        self.cycle = columns
        await self.do_view(author.mention)
        self.cycle = None

    COMMANDS = {
        "submit": cmd_submit,
        "cycle": cmd_cycle,
    }
