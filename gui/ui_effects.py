class Colors:
    NAVY_BLUE = (7, 54, 130)
    BLUE = (0, 97, 255)
    LIGHT_BLUE = (171, 203, 255)
    CYAN = (0, 242, 255)
    LIGHT_CYAN = (180, 217, 219)
    ORANGE = (242, 153, 0)
    LIGHT_ORANGE = (255, 211, 135)
    MAROON = (133, 25, 25)
    LIGHT_RED = (255, 117, 117)
    GOLD = (207, 155, 0)
    LIGHT_BLACK = (140, 140, 140)
    DARK_BLACK = (79, 79, 79)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    LAWN_GREEN = (101, 224, 0)
    GREEN = (49, 110, 0)
    LIGHT_GREEN = (196, 255, 148)
    PURPLE = (119, 13, 181)
    LIGHT_PURPLE = (230, 186, 255)

    @property
    def dark_mode(self):
        return [self.LIGHT_BLACK, self.DARK_BLACK]


theme = Colors()
