from modules.base import Module, noparts, check_solve_cmd
from modules.wires import Wires
from modules.button import Button
from modules.keypad import Keypad

VANILLA_MODULES = {
	"wires": Wires,
	"button": Button,
	"keypad": Keypad
}

MODDED_MODULES = {
}

async def cmd_modules(channel, author, parts):
	list_ = lambda d: ', '.join(f"`{x}`" for x in d)
	await channel.send(f"Available modules:\nVanilla: {list_(VANILLA_MODULES)}\nModded: {list_(MODDED_MODULES)}")
