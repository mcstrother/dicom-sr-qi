import os
import sys

def main():
    folder_name = os.path.dirname(os.getcwd())
    if not folder_name in sys.path:
        sys.path.append(folder_name)
    from srqi.gui import main as gui_main
    gui_main.main()

if __name__ == "__main__":
    main()


