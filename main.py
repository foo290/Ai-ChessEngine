from gui.gui_manager import GuiManager
from gui.ui_effects import theme

if __name__ == '__main__':
    manager = GuiManager()
    manager.turn_on_color_flips()
    manager.run_main_loop()
