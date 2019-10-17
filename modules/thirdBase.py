from modules.whosOnFirst import WhosOnFirst


class ThirdBase(WhosOnFirst):
    identifiers = ['thirdBase']
    display_name = "Third Base"
    manual_name = "Third Base"
    help_text = "`{cmd} push 8i99` or `{cmd} press 66i8` to push a button."
    module_score = 6
    transform = 'rotate(180 174 174)'

    def button_replace_values(self, v):
        return v.replace('0', 'O').replace('1', 'I')

    DISPLAY_WORDS = {
        "NHXS": 2, "IH6X": 1, "XI8Z": 5, "I8O9": 1, "XOHZ": 5, "H68S": 2,
        "8OXN": 4, "Z8IX": 3, "SXHN": 5, "6NZH": 2, "H6SI": 5, "6O8I": 3,
        "NXO8": 3, "66I8": 4, "S89H": 4, "SNZX": 5, "9NZS": 3, "8I99": 5,
        "ZHOX": 3, "SI9X": 3, "SZN6": 0, "ZSN8": 5, "HZN9": 4, "X9HI": 3,
        "IS9H": 2, "XZNS": 5, "X6IS": 1, "8NSZ": 5,
    }

    PRECEDENCE = {
        "XI8Z": ["NHXS", "I8O9", "XOHZ", "6O8I", "6NZH", "66I8", "H6SI", "Z8IX", "XI8Z", "SXHN", "H68S", "8OXN", "IH6X", "NXO8"],
        "H68S": ["6NZH", "I8O9", "NHXS", "6O8I", "SXHN", "H6SI", "IH6X", "8OXN", "NXO8", "XI8Z", "Z8IX", "XOHZ", "66I8", "H68S"],
        "SXHN": ["Z8IX", "8OXN", "NXO8", "H68S", "XOHZ", "XI8Z", "H6SI", "NHXS", "IH6X", "6NZH", "66I8", "I8O9", "SXHN", "6O8I"],
        "Z8IX": ["NXO8", "H6SI", "I8O9", "6O8I", "Z8IX", "66I8", "XI8Z", "IH6X", "SXHN", "XOHZ", "6NZH", "8OXN", "NHXS", "H68S"],
        "IH6X": ["8OXN", "H6SI", "I8O9", "6O8I", "NHXS", "Z8IX", "SXHN", "66I8", "6NZH", "XOHZ", "NXO8", "H68S", "IH6X", "XI8Z"],
        "NHXS": ["I8O9", "H6SI", "8OXN", "6O8I", "H68S", "XOHZ", "66I8", "XI8Z", "IH6X", "NHXS", "6NZH", "Z8IX", "SXHN", "NXO8"],
        "XOHZ": ["8OXN", "XOHZ", "6NZH", "IH6X", "XI8Z", "Z8IX", "6O8I", "SXHN", "I8O9", "H68S", "NXO8", "NHXS", "66I8", "H6SI"],
        "8OXN": ["XI8Z", "IH6X", "6NZH", "XOHZ", "I8O9", "NHXS", "H6SI", "SXHN", "66I8", "Z8IX", "8OXN", "6O8I", "NXO8", "H68S"],
        "6NZH": ["H6SI", "6NZH", "H68S", "SXHN", "6O8I", "NHXS", "Z8IX", "XOHZ", "8OXN", "NXO8", "66I8", "XI8Z", "I8O9", "IH6X"],
        "H6SI": ["NHXS", "IH6X", "XI8Z", "66I8", "SXHN", "NXO8", "XOHZ", "H6SI", "6O8I", "6NZH", "8OXN", "Z8IX", "I8O9", "H68S"],
        "6O8I": ["Z8IX", "XI8Z", "I8O9", "XOHZ", "IH6X", "66I8", "SXHN", "NXO8", "6NZH", "6O8I", "H6SI", "H68S", "8OXN", "NHXS"],
        "I8O9": ["6O8I", "SXHN", "H68S", "NHXS", "8OXN", "IH6X", "NXO8", "I8O9", "6NZH", "XI8Z", "Z8IX", "66I8", "XOHZ", "H6SI"],
        "NXO8": ["8OXN", "SXHN", "Z8IX", "I8O9", "NHXS", "6NZH", "H68S", "66I8", "XOHZ", "NXO8", "IH6X", "XI8Z", "H6SI", "6O8I"],
        "66I8": ["H6SI", "6O8I", "NHXS", "XI8Z", "66I8", "I8O9", "IH6X", "8OXN", "Z8IX", "6NZH", "H68S", "XOHZ", "SXHN", "NXO8"],
        "9NZS": ["8NSZ", "8I99", "ZHOX", "HZN9", "IS9H", "SNZX", "SZN6", "XZNS", "SI9X", "9NZS", "ZSN8", "X6IS", "X9HI", "S89H"],
        "8I99": ["ZHOX", "IS9H", "X6IS", "SNZX", "SI9X", "X9HI", "ZSN8", "XZNS", "9NZS", "S89H", "HZN9", "8NSZ", "SZN6", "8I99"],
        "ZHOX": ["ZSN8", "8I99", "SNZX", "ZHOX", "IS9H", "SZN6", "8NSZ", "S89H", "HZN9", "9NZS", "SI9X", "XZNS", "X6IS", "X9HI"],
        "HZN9": ["9NZS", "HZN9", "SZN6", "IS9H", "ZSN8", "8I99", "S89H", "ZHOX", "SI9X", "SNZX", "8NSZ", "X9HI", "X6IS", "XZNS"],
        "SZN6": ["X9HI", "S89H", "SZN6", "SNZX", "SI9X", "8NSZ", "ZHOX", "XZNS", "HZN9", "X6IS", "IS9H", "ZSN8", "8I99", "9NZS"],
        "S89H": ["SNZX", "8NSZ", "IS9H", "SI9X", "HZN9", "SZN6", "ZSN8", "X9HI", "S89H", "9NZS", "X6IS", "XZNS", "8I99", "ZHOX"],
        "SNZX": ["SNZX", "ZHOX", "8I99", "9NZS", "X9HI", "XZNS", "ZSN8", "IS9H", "8NSZ", "X6IS", "HZN9", "SZN6", "S89H", "SI9X"],
        "ZSN8": ["SZN6", "S89H", "8I99", "HZN9", "IS9H", "ZSN8", "X9HI", "9NZS", "SNZX", "X6IS", "ZHOX", "8NSZ", "XZNS", "SI9X"],
        "SI9X": ["9NZS", "XZNS", "HZN9", "ZHOX", "S89H", "X9HI", "ZSN8", "X6IS", "8I99", "SNZX", "SZN6", "IS9H", "SI9X", "8NSZ"],
        "X9HI": ["8NSZ", "SNZX", "IS9H", "SI9X", "ZHOX", "SZN6", "HZN9", "XZNS", "X6IS", "9NZS", "S89H", "8I99", "ZSN8", "X9HI"],
        "IS9H": ["SI9X", "SNZX", "ZSN8", "ZHOX", "XZNS", "8NSZ", "IS9H", "X6IS", "X9HI", "8I99", "SZN6", "HZN9", "S89H", "9NZS"],
        "XZNS": ["8I99", "S89H", "X9HI", "ZSN8", "9NZS", "SZN6", "8NSZ", "SI9X", "HZN9", "IS9H", "XZNS", "SNZX", "ZHOX", "X6IS"],
        "8NSZ": ["8I99", "X9HI", "X6IS", "HZN9", "9NZS", "XZNS", "SNZX", "SZN6", "8NSZ", "S89H", "SI9X", "IS9H", "ZHOX", "ZSN8"],
        "X6IS": ["HZN9", "IS9H", "S89H", "SZN6", "XZNS", "X9HI", "ZSN8", "SI9X", "SNZX", "9NZS", "X6IS", "8NSZ", "8I99", "ZHOX"],
    }

    BUTTON_GROUPS = [list(PRECEDENCE)]
