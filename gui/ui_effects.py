class Colors:
    NAVY_BLUE = (7, 54, 130)
    BLUE = (0, 97, 255)
    LIGHT_BLUE = (171, 203, 255)
    CYAN = (0, 242, 255)
    LIGHT_CYAN = (180, 217, 219)
    ORANGE = (255, 132, 0)
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

    def get_all_themes(self):
        self_remove = 'get_all_themes'
        all_themes = [i for i in dir(self) if not i.startswith('__') and i.islower()]
        all_themes.remove(self_remove)
        return all_themes

    @property
    def dark_mode(self):
        return [self.LIGHT_BLACK, self.DARK_BLACK]

    @property
    def navy(self):
        return [self.LIGHT_BLUE, self.NAVY_BLUE]

    @property
    def purple_pet(self):
        return [self.LIGHT_PURPLE, self.PURPLE]

    @property
    def eco_green(self):
        return [self.LIGHT_GREEN, self.GREEN]

    @property
    def sunset(self):
        return [self.LIGHT_ORANGE, self.ORANGE]

    @property
    def golden_flag(self):
        return [self.LIGHT_ORANGE, self.GOLD]

    @property
    def cyan_aroma(self):
        return [self.LIGHT_RED, self.CYAN]

    @property
    def red_handed(self):
        return [self.LIGHT_RED, self.MAROON]

    @property
    def default(self):
        return [Colors.WHITE, Colors.DARK_BLACK]


theme = Colors()
