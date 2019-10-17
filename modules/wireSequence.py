import random
import itertools
import enum
import modules
import edgework


class WireSequence(modules.Module):
    identifiers = ['wireSequence']
    display_name = "Wire Sequence"
    manual_name = "Wire Sequence"
    help_text = "`{cmd} cut 7` - cut wire 7. `{cmd} down`, `{cmd} d` - go to the next panel. `{cmd} up`, `{cmd} u` - go back to the previous panel. `{cmd} cut 1 3 d` - cut mutiple wires and continue."
    module_score = 4

    @enum.unique
    class Color(enum.Enum):
        red = "#f00"
        blue = "#00f"
        black = "#000"

    RULES = {
        Color.red: [{2}, {1}, {0}, {0, 2}, {1}, {0, 2}, {0, 1, 2}, {0, 1}, {1}],
        Color.blue: [{1}, {0, 2}, {1}, {0}, {1}, {1, 2}, {2}, {0, 2}, {0}],
        Color.black: [{0, 1, 2}, {0, 2}, {1}, {0, 2}, {1}, {1, 2}, {0, 1}, {2}, {2}],
    }

    PATHS_UNCUT = {
        (0, 0): "m 125.13854,98.813083 -0.0102,5.987437 110.90849,0.18126 0.0102,-5.987438 z",
        (0, 1): "m 127.00048,97.767359 -3.47859,5.083901 109.64552,72.63119 3.48062,-5.08591 z",
        (0, 2): "m 129.53502,99.238202 -4.65119,3.578928 105.32434,140.16172 4.6512,-3.58087 z",

        (1, 0): "m 127.22803,174.78975 -3.49156,-5.08365 110.05422,-72.62761 3.4936,5.08566 z",
        (1, 1): "m 125.05355,168.88342 -0.0102,5.98744 110.90849,0.18126 0.0102,-5.98744 z",
        (1, 2): "m 126.70868,167.63502 -3.49156,5.08365 110.05423,72.62761 3.4936,-5.08566 z",

        (2, 0): "m 233.39689,100.10766 -108.46288,139.99505 4.8193,3.70926 108.46287,-139.99506 z",
        (2, 1): "m 126.37656,245.93829 -3.49156,-5.08365 110.05423,-72.62761 3.4936,5.08566 z",
        (2, 2): "m 126.15868,237.19896 -0.01,6 108.79297,0.18164 0.01,-6 z",
    }

    PATHS_CUT = {
        (0, 0): "m 170.063,98.899922 -44.92446,-0.08649 v -3.49e-4 l -0.0102,5.987437 44.93466,0.19343 z m 20.278,6.100858 45.69583,-0.0186 0.0102,-5.987438 -45.70603,-0.08903 z",
        (0, 1): "m 185.50472,143.90982 47.66269,31.57263 3.48062,-5.08591 -47.6446,-31.43119 z m -10.23625,-14.07064 -48.26799,-32.071821 -3.47859,5.083901 48.37564,32.04491 z",
        (0, 2): "m 184.97163,182.77974 45.23654,60.19911 4.6512,-3.58087 -45.20169,-60.22656 z m -7.82191,-20.22949 -47.6147,-63.312048 -4.65119,3.578928 47.57337,63.30888 z",

        (1, 0): "m 175.08766,142.95297 -47.85963,31.83678 -3.49156,-5.08365 47.79483,-31.54104 z m 10.44371,-13.92758 48.25932,-31.9469 3.4936,5.08566 -48.13157,31.75874 z",
        (1, 1): "m 169.86073,168.95672 -44.80718,-0.0733 -0.0102,5.98744 44.7423,0.0724 z m 24.98627,6.02774 41.10484,0.0677 0.0102,-5.98744 -41.11497,-0.0672 z",
        (1, 2): "m 186.1344,214.2394 47.13695,31.10688 3.4936,-5.08566 -47.40858,-31.0675 z m -10.96829,-14.62756 -48.45743,-31.97682 -3.49156,5.08365 48.65914,32.03903 z",

        (2, 0): "m 189.62979,166.397 48.58639,-62.58009 -4.81929,-3.70925 -48.58051,62.70377 z m -17.70146,13.04927 -46.99432,60.65644 4.8193,3.70926 47.07207,-60.58177 z",
        (2, 1): "m 175.99116,213.22973 -49.6146,32.70856 -3.49156,-5.08365 49.669,-32.77784 z m 8.85538,-13.2651 48.09269,-31.7376 3.4936,5.08566 -48.16212,31.88838 z",
        (2, 2): "m 186.5774,243.29985 48.36425,0.0807 0.01,-6 -48.37365,-0.0809 z m -13.41046,-6.02241 -47.00826,-0.0785 -0.01,6 47.01838,0.18422 z",
    }

    def __init__(self, bomb, ident):
        super().__init__(bomb, ident)
        self.current_page = 0
        self.solved_pages = 0

        # This is how the game generates these wires. Please don't ask me about this code.
        self.wires = []
        for color in WireSequence.Color:
            for _ in range(9):
                self.wires.append((color, random.randint(0, 2)))
        # replicating an off-by-one error
        self.wires = random.sample(self.wires, 10)
        self.wires += [None] * 3
        random.shuffle(self.wires)
        # if the first page is empty, all the other pages will be full
        if self.wires[:3].count(None) == 3:
            self.wires[random.randint(0, 2)] = self.wires[3]
            self.wires[3] = None

        self.wires.pop()  # remove the additional wire caused by the off-by-one error

        self.should_cut = [False] * 12
        self.cut = [False] * 12
        counts = {}
        for index, wire in enumerate(self.wires):
            if wire is None:
                continue
            color, to = wire
            if color not in counts:
                counts[color] = 0
            self.should_cut[index] = to in WireSequence.RULES[color][counts[color]]
            counts[color] += 1

            should_cut = "cut" if self.should_cut[index] else "don't count"
            self.log(f"Wire {index + 1} to {'ABC'[to]} is the {counts[color]}. {color.name} wire - {should_cut}")

    def get_svg(self, led):
        svg = (
            f'<svg viewBox="0 0 348 348" fill="#fff" stroke-width="2" stroke-linejoin="round" stroke-linecap="butt" stroke-miterlimit="10" xmlns="http://www.w3.org/2000/svg">'
            f'<path stroke="#000" d="M5 5h338v338h-338z"/>'
            f'<path stroke="#000" d="M74 74h200v200h-200zM129 19h90v40h-90zM129 288h90v40h-90z"/>'
            f'<circle fill="{led}" stroke="#000" cx="298" cy="40.5" r="15"/>'
            f'<path fill="#000" d="M158 39l16-10 16 10h-8v10h-16v-10zM158 308l16 10 16-10h-8v-10h-16v10z"/>'
            f'<path fill="#000" stroke="#000" d="M283 74h52v254h-52z"/>')

        for i in range(4):
            color = "#0f0" if self.solved_pages > i else "#fff"
            svg += f'<path fill="{color}" stroke="{color}" d="M294 {273 - 55 * i}h30v21h-30z"/>'

        if self.solved:
            svg += f'<path stroke="#000" d="M74 174h200"/>'
        else:
            for i in range(3):
                wire_index = self.current_page * 3 + i

                svg += (
                    f'<text x="104" y="{114 + 70 * i}" text-anchor="middle" fill="#000" style="font-family:sans-serif;font-size:24pt;">{wire_index + 1}</text>'
                    f'<text x="249" y="{114 + 70 * i}" text-anchor="middle" fill="#000" style="font-family:sans-serif;font-size:24pt;">{"ABC"[i]}</text>')

                wire = self.wires[wire_index]
                if wire is not None:
                    color, to = wire
                    path = WireSequence.PATHS_CUT[i,
                                                  to] if self.cut[wire_index] else WireSequence.PATHS_UNCUT[i, to]
                    svg += f'<path fill="{color.value}" stroke="#000" d="{path}"/>'

        svg += f'</svg>'
        return svg

    @modules.check_solve_cmd
    @modules.noparts
    async def cmd_up(self, author):
        if self.current_page == 0:
            return await self.do_view(f"{author.mention} This is the first panel already!")
        self.current_page -= 1
        return await self.do_view(author.mention)

    @modules.check_solve_cmd
    @modules.noparts
    async def cmd_down(self, author):
        return await self.do_down(author)

    async def do_down(self, author):
        begin = 3 * self.current_page
        end = begin + 3
        page_should_cut = self.should_cut[begin:end]
        page_cut = self.cut[begin:end]
        for index, should_cut, cut in zip(range(begin, end), page_should_cut, page_cut):
            if should_cut and not cut:
                self.log(f"Didn't cut wire {index + 1}!")
                return await self.handle_strike(author)

        self.current_page += 1
        if self.solved_pages < self.current_page:
            self.solved_pages = self.current_page

        if self.current_page >= 4:
            return await self.handle_solve(author)
        else:
            return await self.do_view(author.mention)

    @modules.check_solve_cmd
    async def cmd_cut(self, author, parts):
        wires_to_cut = []
        go_to_next_page = False
        for part in parts:
            if go_to_next_page:
                return await self.bomb.channel.send(f"{author.mention} Trailing arguments")

            if part.isdigit():
                wire = int(part)

                if wire not in range(1, 12 + 1):
                    return await self.do_view(f"{author.mention} Wires are numbered 1-12. What on earth does wire {wire} mean?")

                wire -= 1
                first_on_page = 3 * self.current_page
                end_range = first_on_page + 3

                if wire not in range(first_on_page, end_range):
                    return await self.do_view(f"{author.mention} Wire {wire + 1} is not on this panel. The wires on this panel are numbered {first_on_page + 1}-{end_range}.")

                if self.wires[wire] is None:
                    return await self.do_view(f"{author.mention} There is no wire connected to {wire + 1}!")

                if self.cut[wire]:
                    return await self.do_view(f"{author.mention} Wire {wire + 1} has already been cut!")

                if wire in wires_to_cut:
                    return await self.bomb.channel.send(f"{author.mention} Wait, am I supposed to cut wire {wire + 1} twice?")

                wires_to_cut.append(wire)
            elif part in ['d', 'down']:
                go_to_next_page = True
            else:
                return await self.bomb.channel.send(f"{author.mention} What does `{part}` mean?")

        for wire in wires_to_cut:
            self.log(f"Cutting wire {wire + 1}")
            self.cut[wire] = True
            if not self.should_cut[wire]:
                return await self.handle_strike(author)

        if go_to_next_page:
            return await self.do_down(author)
        else:
            return await self.do_view(author.mention)

    COMMANDS = {
        'cut': cmd_cut,
        'down': cmd_down,
        'd': cmd_down,
        'up': cmd_up,
        'u': cmd_up,
    }
