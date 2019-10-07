import random
import cairosvg
import modules
from functools import lru_cache
from wand.image import Image

MORSE_CODE = {
    "a": ".-",
    "b": "-...",
    "c": "-.-.",
    "d": "-..",
    "e": ".",
    "f": "..-.",
    "g": "--.",
    "h": "....",
    "i": "..",
    "j": ".---",
    "k": "-.-",
    "l": ".-..",
    "m": "--",
    "n": "-.",
    "o": "---",
    "p": ".--.",
    "q": "--.-",
    "r": ".-.",
    "s": "...",
    "t": "-",
    "u": "..-",
    "v": "...-",
    "w": ".--",
    "x": "-..-",
    "y": "-.--",
    "z": "--..",
}

DOT_LENGTH = 45

class MorseCode(modules.Module):
    identifiers = ['morseCode']
    display_name = "Morse Code"
    manual_name = "Morse Code"
    help_text = "`{cmd} tx 3.545`, `{cmd} tx 545`, `{cmd} tx 3.545 MHz`, or `{cmd} transmit ...` to transmit on 3.545 MHz."
    module_score = 3
    vanilla = True

    WORDS = {
        "shell":  505,
        "halls":  515,
        "slick":  522,
        "trick":  532,
        "boxes":  535,
        "leaks":  542,
        "strobe": 545,
        "bistro": 552,
        "flick":  555,
        "bombs":  565,
        "break":  572,
        "brick":  575,
        "steak":  582,
        "sting":  592,
        "vector": 595,
        "beats":  600,
    }

    def __init__(self, bomb, ident):
        super().__init__(bomb, ident)

        self.wordset = MorseCode.WORDS
        self.word = random.choice(list(self.wordset.keys()))
        self.frequency = self.wordset[self.word]
        self.last_frequency = 505
        self.log(f"The word is {self.word}, with a frequency of 3.{self.frequency} MHz")

    def get_image(self, rx_led, solve_led):
        svg = (
            f'<svg viewBox="0 0 348 348" fill="#fff" stroke-linecap="butt" stroke-linejoin="round" stroke-miterlimit="10">'
            f'<path stroke="#000" stroke-width="2" d="M5 5h338v338h-338zM48 139h252v30h-252zm41 0v14m50-14v14m50-14v14m50-14v14m50-14v14m-225 16v-10m50 10v-10m50 10v-10m50 10v-10m50 10v-10M155 50h120M5 5l30 45M129 290h90v35h-90zM24 120h300v160h-300z"/>'
            f'<circle fill="{solve_led}" stroke="#000" cx="298" cy="40.5" r="15" stroke-width="2"/>'
            f'<path fill="#000" d="M64 187h220v72h-220z"/>'
            f'<ellipse cx="95" cy="50" rx="60" ry="15" fill="{"#ff0" if rx_led else "#fff"}" stroke="#000" stroke-width="2"/>'
            f'<path fill="#000" stroke="#000" stroke-width="2" d="M46 23h12v54h-12zM132 23h12v54h-12zM55 197l-22 26 22 26zM293 197l22 26-22 26zM{(self.last_frequency - 500) * 236 / 100 + 52} 134h9v40h-9z"/>'
            f'<text x="174" y="318" text-anchor="middle" fill="#000" style="font-size:20pt;font-family:sans-serif;">TX</text>'
            f'<text x="174" y="237" text-anchor="middle" style="font-size:28pt;font-family:sans-serif;">3.{self.last_frequency} MHz</text>'
            f'</svg>')
        return cairosvg.svg2png(svg.encode())

    def render(self, strike):
        if self.solved:
            return self.get_image(False, '#0f0'), 'render.png'

        led = '#f00' if strike else '#fff'

        on = self.get_image(True, led)
        off = self.get_image(False, led)

        with Image() as im:
            def add(frame, units):
                modules.gif_append(im, frame, units * DOT_LENGTH)

            for letter in self.word:
                add(off, 3)
                first_signal = True
                for signal in MORSE_CODE[letter]:
                    if not first_signal: add(off, 1)
                    first_signal = False
                    add(on, 3 if signal == '-' else 1)
            add(off, 4)

            return modules.gif_output(im)

    @modules.check_solve_cmd
    async def cmd_transmit(self, author, parts):
        if len(parts) == 0 or len(parts) > 2 or len(parts) == 2 and parts[1].lower() != "mhz":
            return await self.usage(author)

        freq = parts[0]
        if freq.startswith('3.'): freq = freq[2:]

        if not freq.isdigit() or len(freq) != 3 or (freq[0] != "5" or freq[-1] not in '25') and freq != "600":
            return await self.usage(author)

        freq = int(freq)
        freqs = sorted(list(self.wordset.values()))
        if freq not in freqs:
            if freq < freqs[0]:
                self.last_frequency = freqs[0]
            elif freq > freqs[-1]:
                self.last_frequency = freqs[-1]
            elif freq < self.last_frequency:
                # moving left
                self.last_frequency = max(f for f in freqs if f < freq)
            else:
                # moving right
                self.last_frequency = min(f for f in freqs if f > freq)
            return await self.handle_unsubmittable(author)

        self.last_frequency = freq

        if freq == self.frequency:
            await self.handle_solve(author)
        else:
            await self.handle_strike(author)

    COMMANDS = {
        "transmit": cmd_transmit,
        "tx": cmd_transmit,
    }
