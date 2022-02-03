import dateutil.parser
import webbrowser
import PySimpleGUI as sg
import pathlib
from config import ASSETS_PATH
import database
database.create_tables()

sg.theme("Default1")
menu_def = [
    ["File", [
        "New (CTRL+N)", 
        "Open (CTRL+O)", 
        "Recent (CTRL+E)", 
        "---", 
        "Save (CTRL+S)", 
        "Save as (CTRL+SHIFT+S)",
        "---",
        "Exit (CTRL+SHIFT+Q)"]
    ],
    ["Help", ["About..."]]
]

layout = [
    [sg.Menu(menu_def, tearoff=False, key="-MENU-")],
    [sg.Multiline(expand_x=True, expand_y=True, key="-TEXT-",  enable_events=True)],
    [sg.Text("New file", key="-FILE_NAME-")]
]

window = sg.Window("New File - PyNotepad", layout, resizable=True, margins=(0, 0), size=(1200, 600), 
    finalize=True, enable_close_attempted_event=True)
window.bind("<Control-KeyPress-o>", "CTRL-O")
window.bind("<Control-KeyPress-O>", "CTRL-O")
window.bind("<Control-KeyPress-e>", "CTRL-E")
window.bind("<Control-KeyPress-E>", "CTRL-E")
window.bind("<Control-KeyPress-s>", "CTRL-S")
window.bind("<Control-KeyPress-S>", "CTRL-S")
window.bind("<Control-Shift-s>", "CTRL+SHIFT-S")
window.bind("<Control-Shift-S>", "CTRL+SHIFT-S")
window.bind("<Control-Shift-q>", "CTRL+SHIFT-Q")
window.bind("<Control-Shift-Q>", "CTRL+SHIFT-Q")

current_file = None

editing = False

def new_file():
    global current_file
    global editing

    if editing:
        question = sg.popup_yes_no(f"Do you want to exit without saving changes to this file?", title="Unsaved changes")

        if question == "Yes":
            current_file = None
            editing = False

            window.set_title("New File - PyNotepad")
            window["-TEXT-"].update("")
            window["-FILE_NAME-"].update("New file")
    else:
        current_file = None
        editing = False

        window.set_title("New File - PyNotepad")
        window["-TEXT-"].update("")
        window["-FILE_NAME-"].update("New file")

def open_file(filename: str=None):
    global current_file
    global editing

    if filename:
        if editing:
            question = sg.popup_yes_no(f"Do you want to exit without saving changes to this file?", title="Unsaved changes")

            if question == "No":
                return
        file = None
        try:
            file = pathlib.Path(filename)
            window["-TEXT-"].update(file.read_text())
        except FileNotFoundError:
            sg.popup("The file does not exists", title="Error")
        except UnicodeDecodeError:
            sg.popup("The file is written in a format not supported by the editor", title="Error")
        else:
            window.set_title(f"{file.name} - PyNotepad")
            window["-FILE_NAME-"].update(file.name)
        
            editing = False

            database.add_file(str(file))

            current_file = str(file)
    else:
        filename = sg.popup_get_file("Open file", no_window=True)

        if filename:
            if editing:
                question = sg.popup_yes_no(f"Do you want to exit without saving changes to this file?", title="Unsaved changes")

                if question == "No":
                    return
            file = None

            try:
                file = pathlib.Path(filename)
                window["-TEXT-"].update(file.read_text())
            except FileNotFoundError:
                sg.popup("The file does not exists", title="Error")
            except UnicodeDecodeError:
                sg.popup("The file is written in a format not supported by the editor", title="Error")
            else:
                window.set_title(f"{file.name} - PyNotepad")
                window["-FILE_NAME-"].update(file.name)

                editing = False

                database.add_file(str(file))

                current_file = str(file)

def save_file(content):
    global current_file
    global editing

    if current_file:
        file = pathlib.Path(current_file)

        window.set_title(f"{file.name} - PyNotepad")
        file.write_text(content)

        editing = False
    else:
        current_file = save_file_as(content)

def save_file_as(content):
    global current_file
    global editing
    
    filename = sg.popup_get_file("", title="Save file", no_window=True, save_as=True)

    if filename:
        file = pathlib.Path(filename)

        file.write_text(content)

        window.set_title(f"{file.name} - PyNotepad")
        window["-FILE_NAME-"].update(file.name)

        editing = False

        database.add_file(str(file))

        current_file = filename

def open_recent_files_window():
    content = [[file[0], dateutil.parser.parse(file[1]).strftime("%d/%m/%Y")] for file in database.get_recently_files()]
    
    recently_used_layout = [
        [sg.Text("File:")],
        [sg.Input(disabled=True, expand_x=True, key="-FILE_SELECTION-")],
        [sg.Table(content, ["File", "Modifield"], auto_size_columns=False, col_widths=(70, 10), justification="left",expand_x=True,
            expand_y=True, enable_click_events=True, key="-TABLE-")],
        [sg.Button("Open", button_color=("white", "blue"), disabled=True, key="-OPEN-"), 
            sg.Button("Cancel", button_color=("white", "red"), key="-EXIT-"),
            sg.Button("Delete recent files", key="-CLEAR_LIST-")]
    ]

    recently_used_window = sg.Window("Recently opened", recently_used_layout, size=(800, 400), modal=True)

    recently_file = None

    while True:
        event, _ = recently_used_window.read()

        if event in (sg.WIN_CLOSED, "-EXIT-"):
            break

        if event == "-OPEN-":
            open_file(recently_file[0])
            break

        if event == "-CLEAR_LIST-":
            database.delete_files()
            content = database.get_recently_files()

            recently_file = None

            recently_used_window["-TABLE-"].update(content, select_rows=[])
            recently_used_window["-OPEN-"].update(disabled=True)
            recently_used_window["-FILE_SELECTION-"].update("")

        if isinstance(event, tuple) and (event[0] == "-TABLE-" and event[1] == "+CICKED+"):
            print(True)
            if event[2] and event[2][0] != None and event[2][0] >= 0:
                recently_file = content[event[2][0]]
                recently_used_window["-OPEN-"].update(disabled=False)
                recently_used_window["-FILE_SELECTION-"].update(f"{recently_file[0]}")
            else:
                recently_file = None
                recently_used_window["-TABLE-"].update(select_rows=[])
                recently_used_window["-OPEN-"].update(disabled=True)
                recently_used_window["-FILE_SELECTION-"].update("")
    recently_used_window.close()

def open_about_window():
    logo_layout = [
        [sg.Image(filename=f"{ASSETS_PATH}/icon.png"), sg.Text("PyNotepad", font=(sg.DEFAULT_FONT, 20, "bold"))]
    ]

    link_cfg = {"text_color": "blue", "pad": (20, 15), "justification": "center", "expand_x": True, "enable_events": True,
        "font": (sg.DEFAULT_FONT, 12, "underline")}

    urls = {
        "github": "https://github.com",
        "pysimplegui": "https://pysimplegui.readthedocs.io/en/latest/"
    }

    about_window_layout = [
        [sg.Column(logo_layout, justification="center")],
        [sg.Text("Notepad written in python using PySimpleGUI", justification="center", expand_x=True,font=(sg.DEFAULT_FONT, 10, "bold"))],
        [sg.Text("Github", tooltip=urls["github"], **link_cfg), sg.Text("PySimpleGUI", tooltip=urls["pysimplegui"], **link_cfg)]
    ]

    about_window = sg.Window("About", about_window_layout, size=(500, 210))

    while True:
        event, _ = about_window.read()

        if event == sg.WIN_CLOSED:
            break

        if event == "Github":
            webbrowser.open(urls["github"])

        if event == "PySimpleGUI":
            webbrowser.open(urls["pysimplegui"])
    about_window.close()

def close_window(content):
    global editing

    if editing:
        close_window_layout = [
            [sg.Text("You have unsaved changes Are you sure you want to exit?")],
            [sg.Button("Close and don't save", key="-CLOSE-"), sg.Button("Cancel", key="-CANCEL-"), sg.Button("Save", key="-SAVE-")]
        ]

        close_window = sg.Window("Close without saving", close_window_layout, modal=True)

        while True:
            event, _ = close_window.read()

            if event in (sg.WIN_CLOSED, "-CANCEL-"):
                break

            if event == "-CLOSE-":
                return True

            if event == "-SAVE-":
                save_file(content)
                return True
        close_window.close()
    else:
        return True

while True:
    event, values = window.read(timeout=1)

    if event in (sg.WIN_CLOSE_ATTEMPTED_EVENT, "Salir (CTRL+SHIFT+Q)", "CTRL+SHIFT-Q"):
        close = close_window(values["-TEXT-"])

        if close:
            break

    if event == "-TEXT-":
        if not current_file:
            if len(values["-TEXT-"]) > 0:
                editing = True
        else:
            if len(pathlib.Path(current_file).read_text()) != len(values["-TEXT-"]):
                editing = True

        if editing:
            if current_file:
                file_data = pathlib.Path(current_file)
                if file_data.read_text() != values["-TEXT-"]:
                    window.set_title(f"* {file_data.name} - PyNotepad")
                else:
                    editing = False
                    window.set_title(f"{file_data.name} - PyNotepad")

    if event in ("New (CTRL+N)", "CTRL-N"):
        new_file()

    if event in ("Open (CTRL+O)", "CTRL-O"):
        open_file()

    if event in ("Recent (CTRL+E)", "CTRL-E"):
        open_recent_files_window()

    if event in ("Save (CTRL+S)", "CTRL-S"):
        save_file(values["-TEXT-"])
    
    if event in ("Save as (CTRL+SHIFT+S)", "CTRL+SHIFT-S"):
        save_file_as(values["-TEXT-"])

    if event == "About...":
        open_about_window()

window.close()