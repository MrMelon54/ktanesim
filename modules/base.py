from urllib.parse import quote as urlencode
import io
import cairosvg
import discord
import asyncio
import leaderboard
import time
from wand.image import Image
from config import *
from modules import register_module

def noparts(func):
    async def wrapper(self, author, parts):
        if parts:
            await self.bomb.channel.send(f"{author.mention} Trailing arguments")
        else:
            await func(self, author)
    return wrapper

def check_solve_cmd(func):
    async def wrapper(self, author, parts):
        with await self.lock:
            if self.solved:
                await self.bomb.channel.send(f"{author.mention} {self} has already been solved.")
            elif self.claim and self.claim.id != author.id:
                await self.bomb.channel.send(f"{author.mention} {self} has been claimed by {self.claim}.")
            else:
                await func(self, author, parts)
    return wrapper

def gif_append(im, blob, delay):
    im.sequence.append(Image(blob=blob, format='png'))
    with im.sequence[-1] as frame:
        frame.delay = delay

def gif_output(im):
    im.type = 'optimize'
    im.format = 'gif'
    return im.make_blob(), 'render.gif'

class CommandConsolidator(type):
    def __new__(cls, clsname, superclasses, attributes):
        commands = {}
        for superclass in superclasses:
            if hasattr(superclass, 'COMMANDS'):
                commands.update(superclass.COMMANDS)

        if 'COMMANDS' in attributes:
            commands.update(attributes['COMMANDS'])

        attributes['COMMANDS'] = commands
        module = type.__new__(cls, clsname, superclasses, attributes)
        if clsname != 'Module':
            register_module(module)
        return module

class Module(metaclass=CommandConsolidator):
    strike_penalty = 6
    vanilla = False

    def __init__(self, bomb, ident):
        self._bomb = bomb
        self._ident = ident
        self._solved = False
        self.claim = None
        self.take_pending = None
        self.last_img = None
        self.log_data = []
        self.lock = asyncio.Lock()

    @property
    def bomb(self):
        return self._bomb

    @property
    def ident(self):
        return self._ident

    @property
    def solved(self):
        return self._solved

    def __str__(self):
        return f'{self.display_name} (#{self.ident})'

    def log(self, msg):
        entry = self.bomb.get_time_formatted(), msg
        self.log_data.append(entry)
        if DEBUG_MODE:
            print(self.log_entry_str(entry))

    def get_log(self):
        return '\n'.join(self.log_entry_str(entry) for entry in self.log_data)

    def log_entry_str(self, entry):
        time, message = entry
        return f'[{time}@{self}] {message}'

    def get_manual(self):
        return f"https://ktane.timwi.de/HTML/{urlencode(self.manual_name)}.html"

    def get_help(self):
        return self.help_text.format(cmd=f"{PREFIX}{self.ident}")

    def get_status(self):
        if self.solved:
            return f'solved by {self.claim}'
        elif self.claim:
            return f'claimed by {self.claim}'
        else:
            return 'unclaimed'

    async def usage(self, author):
        await self.bomb.channel.send(f"{author.mention} Unknown command. Try `view` or `claimview`. Module specific commands: {self.get_help()} Manual: {self.get_manual()}")

    async def handle_command(self, command, author, parts):
        if command not in self.COMMANDS:
            await self.usage(author)
        else:
            self.log(f"COMMAND: {command} {' '.join(parts)}")
            await self.COMMANDS[command](self, author, parts)

    async def handle_solve(self, author):
        self.log('module solved')
        self._solved = True
        if self.claim is None: self.claim = author
        leaderboard.record_solve(author, self.module_score)
        await self.do_view(f"{author.mention} solved {self}. {self.module_score} {'points have' if self.module_score > 1 else 'point has'} been awarded.")
        if self.bomb.get_solved_count() == len(self.bomb.modules):
            await self.bomb.bomb_end()

    async def handle_strike(self, author):
        self.log('strike!')
        self.bomb.strikes += 1
        leaderboard.record_strike(author, self.strike_penalty)
        await self.do_view(f"{self} got a strike. There {'has' if self.bomb.strikes == 1 else 'have'} been {self.bomb.strikes} {'strike' if self.bomb.strikes == 1 else 'strikes'} so far. -{self.strike_penalty} point{'s' if self.strike_penalty > 1 else ''} from {author.mention}", True)

    async def handle_unsubmittable(self, author):
        self.log('unsubmittable')
        penalty = self.module_score * 3 // 10
        if penalty == 0: penalty = 1
        leaderboard.record_penalty(author, penalty)
        await self.do_view(f"{author.mention} Please do not submit invalid answers. {penalty} {'points have' if penalty != 1 else 'point has'} been deducted.")

    async def handle_next_stage(self, author):
        self.log('rendering next stage')
        await self.do_view(f"{author.mention} Good! Next stage:")

    def render(self, strike):
        if self.solved:
            led = '#0f0'
        elif strike:
            led = '#f00'
        else:
            led = '#fff'

        # unsafe is needed to include bitmaps, and does not pose a security risk since the user has no control over the SVG
        return cairosvg.svg2png(self.get_svg(led).encode(), unsafe=True), 'render.png'

    @noparts
    async def cmd_view(self, author):
        await self.do_view(author.mention)

    async def do_view(self, text, strike=False):
        start_time = time.time()
        data, filename = await self.bomb.client.loop.run_in_executor(None, self.render, strike)
        end_time = time.time()
        print("Rendering took {:.2}s".format(end_time - start_time))
        descr = f"[Manual]({self.get_manual()}). {self.get_help()}" if not self.solved else ''
        embed = discord.Embed(title=str(self), description=descr)
        embed.set_image(url=f"attachment://{filename}")
        file_ = discord.File(io.BytesIO(data), filename=filename)
        send_task = asyncio.ensure_future(self.bomb.channel.send(text, file=file_, embed=embed))
        if self.last_img is not None:
            delete_task = asyncio.ensure_future(self.last_img.delete())
            self.last_img = (await asyncio.gather(send_task, delete_task))[0]
        else:
            self.last_img = (await asyncio.gather(send_task))[0]

    @noparts
    async def cmd_claim(self, author):
        if await self.do_claim(author):
            await self.bomb.channel.send(f"{author.mention} {self} is yours now.")

    async def do_claim(self, author):
        if self.solved:
            await self.bomb.channel.send(f"{author.mention} {self} has been solved already by {self.claim}.")
        elif self.claim is not None:
            if self.claim.id == author.id:
                await self.bomb.channel.send(f"{author.mention} You have already claimed {self}.")
            else:
                await self.bomb.channel.send(f"{author.mention} Sorry, {self} has already been claimed by {self.claim}. If you think they have abandoned it, you may type `{PREFIX}{self.ident} take` to ~~steal it from them like a pirate~~ take it over.")
        elif len(self.bomb.get_claims(author)) >= MAX_CLAIMS_PER_PLAYER:
            await self.bomb.channel.send(f"{author.mention} Sorry, you can only claim {MAX_CLAIMS_PER_PLAYER} modules at once. Try `{PREFIX}claims`.")
        else:
            self.claim = author
            return True
        return False

    @noparts
    async def cmd_claimview(self, author):
        if await self.do_claim(author):
            await self.do_view(f"{author.mention} {self} is yours now.")

    @noparts
    async def cmd_unclaim(self, author):
        if self.claim and self.claim.id == author.id:
            self.claim = None
            await self.bomb.channel.send(f"{author.mention} has unclaimed {self}")
        else:
            await self.bomb.channel.send(f"{author.mention} You have not claimed {self}, so you can't unclaim it.")

    @noparts
    async def cmd_player(self, author):
        if self.solved:
            await self.bomb.channel.send(f"{author.mention} {self} was solved by {self.claim}")
        else:
            await self.bomb.channel.send(f"{author.mention} {self} has been claimed by {self.claim}")

    @noparts
    async def cmd_take(self, author):
        if self.claim is None:
            await self.bomb.channel.send(f"{author.mention} {self} is not claimed by anybody. Type `{PREFIX}{self.ident} claim` to claim it.")
        elif self.claim.id == author.id:
            await self.bomb.channel.send(f"{author.mention} You already claimed this module.")
        elif self.take_pending is not None:
            await self.bomb.channel.send(f"{author.mention} {self.take_pending} has already issued a `take` command.")
        else:
            self.take_pending = author
            msg = await self.bomb.channel.send(f"{self.claim.mention} {author} wants to take {self}. React with {TAKE_REACT} within {TAKE_TIMEOUT} seconds to confirm you are still working on the module")
            await msg.add_reaction(TAKE_REACT)
            try:
                await self.bomb.client.wait_for('reaction_add', timeout=TAKE_TIMEOUT, check=lambda reaction, user: reaction.emoji == TAKE_REACT and user == self.claim and reaction.message.id == msg.id)
            except asyncio.TimeoutError:
                await self.bomb.channel.send(f"{author.mention} {self} is now yours.")
                self.claim = author
            else:
                await self.bomb.channel.send(f"{self.claim.mention} confirms he is still working on {self}.")
            self.take_pending = None

    COMMANDS = {
        "view": cmd_view,
        "claim": cmd_claim,
        "unclaim": cmd_unclaim,
        "claimview": cmd_claimview,
        "cv": cmd_claimview,
        "take": cmd_take
    }
