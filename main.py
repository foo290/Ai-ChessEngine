from gui.gui_manager import GuiManager
from gui.ui_effects import theme

if __name__ == '__main__':
    manager = GuiManager()
    manager.set_board_color(theme.dark_mode)
    manager.run_main_loop()
