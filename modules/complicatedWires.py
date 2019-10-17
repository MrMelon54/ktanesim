import random
import itertools
import enum
import modules
import edgework


class ComplicatedWires(modules.Module):
    identifiers = ['complicatedWires']
    display_name = "Complicated Wires"
    manual_name = "Complicated Wires"
    help_text = "`{cmd} cut 3` - cut the third wire. `{cmd} cut 1 4 6` - cut multiple wires. `{cmd} cut 146` - cut multiple wires, shorter. Wires are counted left to right, empty spaces excluded."
    module_score = 3

    @enum.unique
    class Color(enum.Enum):
        blue = "#00f"
        red = "#f00"
        white = "#fff"

    PATHS_UNCUT = [
        "m55.183594,73.0625 -5.96875,0.597656 c 1.652446,16.509105 -6.128906,33.805904 -6.128906,52.371094 0,21.07678 0.568469,43.28739 8.185546,63.59961 1.331273,3.55006 3.701096,6.19525 5.539063,8.61523 1.837967,2.41999 3.074391,4.46932 3.210937,6.51953 1.225156,18.39563 -10.351562,37.1942 -10.351562,58.11719 h 6 c 0,-18.56083 11.738513,-37.5147 10.339844,-58.51562 -0.269181,-4.04172 -2.428071,-7.1274 -4.419922,-9.75 -1.991852,-2.6226 -3.886727,-4.92711 -4.699219,-7.09375 -7.142932,-19.04783 -7.804688,-40.53241 -7.804687,-61.49219 0,-16.78337 7.965763,-34.305048 6.097656,-52.96875z",
        "m86.230469,69.636719 -2.226563,5.572265 c 3.834857,1.533657 5.377102,3.856568 6.123047,7.611328 0.745945,3.754761 0.261574,8.89871 -0.939453,14.574219 -2.402055,11.351019 -7.5128,24.593059 -8.46875,35.427739 -1.366517,15.48802 3.902182,30.41984 8.496094,44.86914 4.593911,14.44929 8.507042,28.34377 5.666015,41.77343 -0.940575,4.44615 -4.042214,8.73833 -7.333984,13.39063 -3.29177,4.6523 -6.807863,9.74342 -7.300781,16.1582 -0.320857,4.1756 2.248322,7.48703 5.09375,9.77344 2.845428,2.28641 6.224862,3.88454 9.011718,4.99805 l 2.22461,-5.57032 c -2.463196,-0.98418 -5.413354,-2.44564 -7.476563,-4.10351 -2.063208,-1.65787 -2.983388,-3.17532 -2.871093,-4.63672 0.339593,-4.41943 2.990216,-8.59218 6.216796,-13.15234 3.226581,-4.56017 6.996316,-9.4305 8.304688,-15.61524 3.23945,-15.31301 -1.190873,-30.28523 -5.816406,-44.83398 -4.625533,-14.54876 -9.451889,-28.74634 -8.236328,-42.52344 0.821767,-9.31386 5.805985,-22.64673 8.359375,-34.712891 1.276695,-6.03308 1.985265,-11.808695 0.957031,-16.984375 -1.028234,-5.175681 -4.227759,-9.793862 -9.783203,-12.015625z",
        "m120.60938,67.082031 0.49804,5.978516 c 4.26587,-0.354994 6.40225,1.129047 8.36719,4.525391 1.96493,3.396343 3.1526,8.876021 3.56445,15.197265 0.8237,12.642487 -1.21262,28.488657 -2.46094,39.011717 -1.40189,11.81775 4.62463,22.15509 10.41407,31.92578 5.78944,9.7707 11.36663,19.07419 11.19726,28.56836 -0.20773,11.64469 -5.69976,25.40505 -9.36133,38.82227 -1.83078,6.70861 -3.1962,13.3675 -3.01367,19.81445 0.18254,6.44695 2.01555,12.74309 6.48828,18.10938 l 4.60743,-3.8418 c -3.53694,-4.24353 -4.94291,-8.97173 -5.09766,-14.4375 -0.15475,-5.46577 1.04317,-11.60964 2.80469,-18.06445 3.52304,-12.90963 9.33372,-26.92526 9.57226,-40.29688 0.21093,-11.82354 -6.28534,-22.0286 -12.03515,-31.73242 -5.74982,-9.70382 -10.72888,-18.80524 -9.61914,-28.16016 1.23969,-10.45041 3.37762,-26.51929 2.49218,-40.109372 -0.44272,-6.795043 -1.58142,-13.010882 -4.35937,-17.8125 -2.77795,-4.801617 -7.80058,-8.01882 -14.05859,-7.498047z",
        "m155.36328,72.589844 -4.11133,4.36914 c 11.75385,11.059264 11.30106,31.809846 14.14063,50.007816 3.96137,25.3871 11.7207,50.0124 11.7207,74.77929 0,21.43636 -7.92455,46.43383 2.66797,67.64844 l 5.36719,-2.67969 c -9.16758,-18.36074 -2.03516,-42.17085 -2.03516,-64.96875 0,-26.00263 -7.92704,-50.92964 -11.79297,-75.70507 -2.69772,-17.28892 -1.5531,-39.898426 -15.95703,-53.451176z",
        "m196.48828,76.369141 -5.47656,2.453125 c 18.178,40.596954 36.05265,82.458164 41.14258,126.091794 2.35171,20.16027 -2.8418,41.14157 -2.8418,62.66797 h 6 c 0,-20.52618 5.3215,-41.75416 2.80078,-63.36328 -5.22559,-44.79666 -23.41918,-87.19053 -41.625,-127.849609z",
        "m218.76758,63.625 -4.88281,3.486328 c 11.34339,15.885821 27.56497,27.220753 36.00781,42.941402 14.39234,26.79868 7.50226,61.57603 13.80664,93.6836 4.3622,22.21613 17.87964,42.47321 15.02344,62.48242 l 5.93945,0.84766 c 3.2904,-23.051 -11.0577,-44.02079 -15.07617,-64.48633 C 263.61425,172.16687 270.9312,136.546 255.17773,107.21289 245.8248,89.79762 229.28124,78.348813 218.76758,63.625z",
    ]

    PATHS_CUT = [
        "m55.183594,73.0625 -5.96875,0.597656 c 1.652447,16.509104 -6.128907,33.805904 -6.128906,52.371094 0,12.99041 0.228254,26.40399 2.173828,39.54687 l 5.935546,-0.8789 c -1.868566,-12.62268 -2.109375,-25.74966 -2.109374,-38.66797 0,-16.78337 7.965763,-34.305048 6.097656,-52.96875 z m 1.707031,114.46094 -5.619141,2.10742 c 1.331273,3.55006 3.701096,6.19525 5.539063,8.61523 1.837967,2.41999 3.074391,4.46931 3.210937,6.51953 1.225156,18.39562 -10.351562,37.1942 -10.351562,58.11719 h 6 c 0,-18.56083 11.738514,-37.5147 10.339844,-58.51562 -0.269181,-4.04172 -2.428071,-7.1274 -4.419922,-9.75 -1.991852,-2.6226 -3.886728,-4.92711 -4.699219,-7.09375z",
        "m86.230469,69.636719 -2.226563,5.572265 c 2.581708,1.032491 4.028306,2.441833 5.029297,4.371094 1.000991,1.929261 1.483357,4.500197 1.458985,7.607422 -0.04874,6.214449 -2.16266,14.34445 -4.478516,22.55078 l 5.77539,1.63086 c 2.330352,-8.25769 4.644524,-16.663619 4.703126,-24.134765 0.0293,-3.735573 -0.513014,-7.296047 -2.132813,-10.417969 -1.619799,-3.121922 -4.388862,-5.683948 -8.128906,-7.179687 z M 80.71875,132.82227 c -1.366518,15.48802 3.902182,30.41984 8.496094,44.86914 4.593912,14.44929 8.507042,28.34377 5.666015,41.77343 -0.940575,4.44615 -4.042214,8.73833 -7.333984,13.39063 -3.29177,4.6523 -6.807863,9.74342 -7.300781,16.1582 -0.320856,4.1756 2.248322,7.48703 5.09375,9.77344 2.845427,2.28641 6.224863,3.88454 9.011718,4.99805 l 2.22461,-5.57032 c -2.463198,-0.98418 -5.413354,-2.44564 -7.476563,-4.10351 -2.063208,-1.65787 -2.983388,-3.17533 -2.871093,-4.63672 0.339593,-4.41944 2.990216,-8.59218 6.216796,-13.15234 3.226581,-4.56017 6.996316,-9.4305 8.304688,-15.61524 3.23945,-15.31302 -1.190873,-30.28523 -5.816406,-44.83398 -4.625533,-14.54876 -9.45189,-28.74634 -8.236328,-42.52344z",
        "m120.60938,67.082031 0.49804,5.978516 c 4.26587,-0.354994 6.40225,1.129048 8.36719,4.525391 1.96493,3.396342 3.1526,8.876021 3.56445,15.197265 0.8237,12.642487 -1.21263,28.488657 -2.46094,39.011717 -1.16475,9.81877 2.85207,18.65557 7.50782,26.92383 l 5.22851,-2.94336 c -4.47317,-7.94402 -7.70132,-15.50091 -6.77929,-23.27344 1.23969,-10.45041 3.37762,-26.51929 2.49218,-40.109372 -0.44272,-6.795043 -1.58142,-13.010883 -4.35937,-17.8125 -2.77795,-4.801617 -7.80058,-8.01882 -14.05859,-7.498047 z m 31.58007,125.207029 c -0.20773,11.6447 -5.69976,25.40505 -9.36133,38.82227 -1.83078,6.70861 -3.1962,13.3675 -3.01367,19.81445 0.18254,6.44695 2.01555,12.74309 6.48828,18.10938 l 4.60743,-3.8418 c -3.53694,-4.24353 -4.94291,-8.97173 -5.09766,-14.4375 -0.15475,-5.46577 1.04317,-11.60964 2.80469,-18.06445 3.52304,-12.90962 9.33372,-26.92525 9.57226,-40.29688z",
        "m155.36328,72.589844 -4.11133,4.36914 c 6.80114,6.399235 9.61633,15.891157 11.23438,26.468746 l 5.93164,-0.9082 C 166.72604,91.458969 163.69784,80.431887 155.36328,72.589844 Z m 15.95703,53.451176 -5.92773,0.92578 c 3.96137,25.3871 11.7207,50.01239 11.7207,74.77929 0,21.43636 -7.92455,46.43383 2.66797,67.64844 l 5.36719,-2.67969 c -9.16758,-18.36075 -2.03516,-42.17085 -2.03516,-64.96875 0,-26.00264 -7.92704,-50.92964 -11.79297,-75.70507z",
        "m196.48828,76.369141 -5.47656,2.453125 c 13.37913,29.879634 26.6061,60.447194 34.67383,91.898434 l 5.81054,-1.49023 C 223.2691,137.15833 209.88789,106.2945 196.48828,76.369141 Z m 41.625,127.849609 -5.95898,0.69531 c 2.35172,20.16026 -2.8418,41.14157 -2.8418,62.66797 h 6 c 0,-20.52618 5.32152,-41.75416 2.80078,-63.36328z",
        "m218.76758,63.625 -4.88281,3.486328 c 11.3434,15.88582 27.56496,27.220758 36.00781,42.941402 9.06802,16.88477 9.83522,36.88254 10.58398,57.46485 0.23517,6.46442 0.47623,12.97698 1.00391,19.45508 l 5.98047,-0.48828 c -0.51322,-6.30058 -0.75323,-12.72435 -0.98828,-19.18555 -0.7484,-20.57205 -1.36931,-41.60433 -11.29493,-60.08594 C 245.82478,89.797629 229.28124,78.348814 218.76758,63.625 Z m 50.81836,138.95508 -5.88672,1.15625 c 4.36221,22.21613 17.87964,42.47321 15.02344,62.48242 l 5.93945,0.84766 c 3.2904,-23.051 -11.0577,-44.02079 -15.07617,-64.48633z",
    ]

    def condB(self):
        return self.bomb.get_battery_count() >= 2

    def condC(self):
        return True

    def condD(self):
        return False

    def condP(self):
        return self.bomb.has_port(edgework.PortType.Parallel)

    def condS(self):
        return int(self.bomb.serial[-1]) % 2 == 0

    RULES = {
        # red blue led star
        (False, False, False, False): condC,
        (False, False, False, True):  condC,
        (False, False, True, False):  condD,
        (False, False, True, True):   condB,
        (False, True, False, False):  condS,
        (False, True, False, True):   condD,
        (False, True, True, False):   condP,
        (False, True, True, True):    condP,
        (True, False, False, False):  condS,
        (True, False, False, True):   condC,
        (True, False, True, False):   condB,
        (True, False, True, True):    condB,
        (True, True, False, False):   condS,
        (True, True, False, True):    condP,
        (True, True, True, False):    condS,
        (True, True, True, True):     condD,
    }

    def __init__(self, bomb, ident):
        super().__init__(bomb, ident)
        wire_count = random.randint(4, 9)
        if wire_count > 6:
            wire_count = 6
        self.positions = sorted(random.sample(range(6), wire_count))
        self.cut = [False] * wire_count
        self.should_cut = [False] * wire_count

        colorings = list(itertools.chain(ComplicatedWires.Color,
                                         itertools.combinations(ComplicatedWires.Color, 2)))
        self.wire_colors = []
        self.leds = []
        self.stars = []

        cut_combinations = self.get_cut_combinations()
        encountered_cut = False
        for index in range(wire_count):
            self.wire_colors.append(random.choice(colorings))
            self.leds.append(random.random() > 0.5)
            self.stars.append(random.random() > 0.5)
            if self.wire_to_rules(index) in cut_combinations:
                encountered_cut = True
                self.should_cut[index] = True
            self.log(
                f'Adding wire: {self.wire_to_string(-1)} - {"should cut" if self.should_cut[index] else "should NOT cut"}')

        if not encountered_cut:
            self.log('No wires to cut, overwriting a random wire...')
            index = random.randint(0, wire_count - 1)
            self.set_wire_rules(index, random.choice(cut_combinations))
            self.should_cut[index] = True

    def wire_to_string(self, index):
        color = self.wire_colors[index]
        if isinstance(color, tuple):
            color = f'{color[0].name}-{color[1].name}'
        else:
            color = color.name
        return f'{color}, {"LED" if self.leds[index] else "no LED"}, {"star" if self.stars[index] else "no star"}'

    def wire_to_rules(self, index):
        colors = self.wire_colors[index]
        if isinstance(colors, tuple):
            red = ComplicatedWires.Color.red in colors
            blue = ComplicatedWires.Color.blue in colors
        else:
            red = colors == ComplicatedWires.Color.red
            blue = colors == ComplicatedWires.Color.blue
        return (red, blue, self.leds[index], self.stars[index])

    def set_wire_rules(self, index, rules):
        red, blue, led, star = rules
        if red and blue:
            self.wire_colors[index] = (
                ComplicatedWires.Color.red, ComplicatedWires.Color.blue)
        elif red:
            self.wire_colors[index] = ComplicatedWires.Color.red
        elif blue:
            self.wire_colors[index] = ComplicatedWires.Color.blue
        else:
            self.wire_colors[index] = ComplicatedWires.Color.white
        self.leds[index] = led
        self.stars[index] = star
        self.log(
            f'Overwrote wire {index + 1} with {self.wire_to_string(index)}')

    def get_cut_combinations(self):
        combinations = []

        for combination, condition in ComplicatedWires.RULES.items():
            if condition(self):
                combinations.append(combination)

        return combinations

    def get_svg(self, led):
        needed_gradients = {
            coloring for coloring in self.wire_colors if isinstance(coloring, tuple)}

        svg = '<svg viewBox="0 0 348 348" fill="#fff" stroke="none" stroke-linecap="butt" stroke-linejoin="round" stroke-miterlimit="10">'
        if needed_gradients:
            svg += '<defs>'
            for gradient in needed_gradients:
                svg += f'<linearGradient id="{gradient[0].name}-{gradient[1].name}" x1="0%" x2="5%" y1="0%" y2="100%">'
                for percent in range(0, 100, 20):
                    svg += (f'<stop offset="{percent}%" stop-color="{gradient[0].value}"/>'
                            f'<stop offset="{percent + 10}%" stop-color="{gradient[0].value}"/>'
                            f'<stop offset="{percent + 10}%" stop-color="{gradient[1].value}"/>'
                            f'<stop offset="{percent + 20}%" stop-color="{gradient[1].value}"/>')
                svg += '</linearGradient>'
            svg += '</defs>'
        svg += ('<path stroke="#000" stroke-width="2" d="M5 5h338v388h-338z"/>'
                '<path stroke="#000" stroke-width="2" fill="#888" d="M29 29v58h224v-58zM29 250h274v74h-274z"/>'
                '<path stroke="#000" stroke-width="2" d="M29 58h224M29 279h274M39 284h29l5 5v29h-29l-5 -5zM83 284h29l5 5v29h-29l-5 -5zM127 284h29l5 5v29h-29l-5 -5zM171 284h29l5 5v29h-29l-5 -5zM215 284h29l5 5v29h-29l-5 -5zM259 284h29l5 5v29h-29l-5 -5z"/>'
                f'<circle fill="{led}" stroke="#000" cx="298" cy="40.5" r="15" stroke-width="2"/>')

        for position in range(6):
            if position in self.positions:
                color = "#fec" if self.leds[self.positions.index(
                    position)] else "#444"
            else:
                color = "#444"
            svg += f'<circle fill="{color}" r="8.5" cx="{50 + position * 35}" cy="43" stroke="#000" stroke-width="2"/>'

        for color, star, cut, position in zip(self.wire_colors, self.stars, self.cut, self.positions):
            path = (ComplicatedWires.PATHS_CUT if cut else ComplicatedWires.PATHS_UNCUT)[
                position]
            if isinstance(color, tuple):
                color_str = f'url(#{color[0].name}-{color[1].name})'
            else:
                color_str = color.value

            svg += f'<path stroke="#000" stroke-width="2" fill="{color_str}" d="{path}"/>'
            if star:
                svg += f'<path fill="#000" d="M{39 + position * 44} 284m6.5 15h8l2.5-8l2.5 8h8l-6.5 4.5l2.5 7.5l-6.5 -4.5l-6.5 4.5l2.5-7.5z"/>'
        svg += '</svg>'
        return svg

    @modules.check_solve_cmd
    async def cmd_cut(self, author, parts):
        if not parts:
            return await self.usage(author)

        parsed = []

        for part in parts:
            if not part.isdigit():
                return await self.usage(author)
            for digit in part:
                wire = int(digit) - 1
                if wire not in range(len(self.wire_colors)):
                    return await self.bomb.channel.send(f"{author.mention} There are only {len(self.wire_colors)} wires: 1-{len(self.wire_colors)}")
                parsed.append(wire)

        self.log(f'Parsed: {" ".join(map(str, parsed))}')

        for wire in parsed:
            if self.cut[wire]:
                self.log(f'Wire {wire + 1} has already been cut, ignoring')
            else:
                self.cut[wire] = True
                if self.should_cut[wire]:
                    if self.is_everything_done():
                        return await self.handle_solve(author)
                else:
                    return await self.handle_strike(author)

        await self.do_view(f"{author.mention} You seem to have missed some wire:")

    def is_everything_done(self):
        for cut, should_cut in zip(self.cut, self.should_cut):
            if should_cut and not cut:
                return False
        return True

    COMMANDS = {
        'cut': cmd_cut,
    }
