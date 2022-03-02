from config import ASSETS_PATH
import PySimpleGUI as sg
import webbrowser
import pathlib
import database

database.setup()

sg.theme(database.get_theme())

menu_def = [
    ["File", ["New (CTRL+N)", "Open (CTRL+O)", "Open Recent", [*[f"{file}::recent_file" for file in database.get_recent_files(True)], "---", "Clear recently opened"], 
        "---", "Save (CTRL+S)", "Save as (CTRL+SHIFT+S)", "---", "Exit (CTRL+SHIFT+Q)"]],
    ["Settings", ["Preferences"]],
    ["Help", ["About..."]]
]

btn_colors = {
    "blue": {"button_color": ("white", "blue")},
    "red": {"button_color": ("white", "red")},
    "yellow": {"button_color": ("black", "yellow")}
}

text_colors = database.get_text_colors()

layout = [
    [sg.Menu(menu_def, key="-MENU-")],
    [sg.Multiline(font=("monospace", 9), text_color=text_colors["text"], background_color=text_colors["background"], 
        key="-TEXT-", expand_x=True, expand_y=True, enable_events=True)],
    [sg.Text("New file", key="-FILE_NAME-")]
]

window = sg.Window("New file - PyNotepad", layout, size=(1000, 500), margins=(0, 0), finalize=True, return_keyboard_events=True,
resizable=True, enable_close_attempted_event=True)

window.bind("<Control-KeyPress-n>", "CTRL+N")
window.bind("<Control-KeyPress-N>", "CTRL+N")
window.bind("<Control-KeyPress-o>", "CTRL+O")
window.bind("<Control-KeyPress-O>", "CTRL+O")
window.bind("<Control-KeyPress-r>", "CTRL+R")
window.bind("<Control-KeyPress-R>", "CTRL+R")
window.bind("<Control-KeyPress-s>", "CTRL+S")
window.bind("<Control-KeyPress-S>", "CTRL+S")
window.bind("<Control-Shift-s>", "CTRL+SHIFT+S")
window.bind("<Control-Shift-S>", "CTRL+SHIFT+S")
window.bind("<Control-Shift-q>", "CTRL+SHIFT+Q")
window.bind("<Control-Shift-Q>", "CTRL+SHIFT+Q")

current_file = None
editing = False
about_window = None
preferences_window = None
close_window = None

# UTILS #
def unsaved_changes_question():
    question = sg.popup_yes_no("Do you want to exit without saving changes to this file?", title="Unsaved changes")
    return question

def update_recent_file_list():
    menu_def[0][1][3] = [*[f"{file}::recent_file" for file in database.get_recent_files(True)], "---", "Clear recently opened"]
    window["-MENU-"].update(menu_def)

# WINDOWS AND ACTIONS #
def new_file():
    global current_file, editing

    if editing:
        question = unsaved_changes_question()
        if question == "No":
            return
    
    current_file = None
    editing = None

    window.set_title("New file - PyNotepad")
    window["-TEXT-"].update("")
    window["-FILE_NAME-"].update("New file")

def open_file(filename: str=None):
    global current_file
    global editing

    if not filename:
        filename = sg.popup_get_file("", no_window=True)

        if type(filename) == tuple:
            return
    
    if filename and editing:
        question = unsaved_changes_question()
        if question == "No":
            return
    
    file = None
    try:
        file = pathlib.Path(filename)
        window["-TEXT-"].update(file.read_text())
    except FileNotFoundError:
        sg.popup_error("The file does not exists", title="Error")
    except UnicodeDecodeError:
        sg.popup_error("The file is written in a format not supported by the editor", title="Error")
    else:
        window.set_title(f"{file.name} - PyNotepad")
        window["-FILE_NAME-"].update(file.name)
        
        current_file = filename

        database.add_recent_file(filename)
        update_recent_file_list()

        editing = False 

def save_file(content: str):
    global current_file, editing

    if current_file:
        file = pathlib.Path(current_file)
        window.set_title(f"{file.name} - PyNotepad")
        file.write_text(content)

        editing = False
    else:
        save_file_as(content)

def save_file_as(content: str):
    global current_file, editing

    filename = sg.popup_get_file("", title="Save file", no_window=True, save_as=True)

    if filename and type(filename) != tuple:
        file = pathlib.Path(filename)

        file.write_text(content)

        window.set_title(f"{file.name} - PyNotepad")
        window["-FILE_NAME-"].update(file.name)

        editing = False

        database.add_recent_file(filename)
        update_recent_file_list()

        current_file = filename

def open_about_window():
    global about_window, logo_layout

    urls = {
        "github": "https://github.com/DAFEX6390/python-notepad",
        "pysimplegui": "https://pysimplegui.readthedocs.io"
    }

    link_cfg = {"text_color": "blue", "justification": "center", "expand_x": True, "pad": (20, 15),
        "font": ("Helvetica", 12, "underline"), "enable_events": True}

    logo_layout = [
        [sg.Image(filename=f"{ASSETS_PATH}/icon.png"), sg.Text("PyNotepad", font=(sg.DEFAULT_FONT, 20, "bold"))]
    ]   

    about_layout = [
        [sg.Column(logo_layout, justification="center")],
        [sg.Text("Notepad written in python using PySimpleGUI", justification="center", expand_x=True ,font=(sg.DEFAULT_FONT, 10, "bold"))],
        [sg.Text("Github", tooltip=urls["github"], key="GITHUB", **link_cfg), sg.Text("PySimpleGUI", tooltip=urls["pysimplegui"], key="PSG", **link_cfg)]
    ]

    about_window = sg.Window("About - PyNotepad", about_layout, size=(500, 210), modal=True, resizable=False)

    while True:
        event, _ = about_window.read()

        if event == sg.WIN_CLOSED:
            break

        if event == "GITHUB":
            webbrowser.open(urls["github"])
        
        if event == "PSG":
            webbrowser.open(urls["pysimplegui"])
    about_window.close()
    about_window = None

def open_preferences_window():
    global text_colors, preferences_window

    btn_color_cfg = {"pad": (None, 5), "size":(30, 1)}

    text_color_layout = [
        [sg.Text("Preview:")],
        [sg.Multiline("I love chocolat", disabled=True, text_color=text_colors["text"], background_color=text_colors["background"], size=(None, 5), expand_x=True, key="-TEXT_PREVIEW-")],
        [sg.Text(text_colors["background"], expand_x=True, justification="center", key="-BG_COLOR-"), sg.Text(text_colors["text"], expand_x=True, justification="center", key="-TEXT_COLOR-")],
        [sg.ColorChooserButton("Background", **btn_color_cfg, target=(2,0)), sg.ColorChooserButton("Text", **btn_color_cfg, target=(2,1))],
        [sg.Column([[sg.Button("Preview", size=(10, 1), key="-TEXT_COLOR_PREVIEW-"), sg.Button("Save", size=(10, 1), key="-TEXT_COLOR_SAVE-"),
            sg.Button("Reset default", size=(10,1), key="-TEXT_COLOR_RESET_DEFAULT-")]], 
            element_justification="center", pad=(None, 20), expand_x=True)]
    ]

    theme_layout = [
        [sg.Text(f"Current theme: {database.get_theme()}")],
        [sg.Listbox(sg.list_of_look_and_feel_values(), size=(20, 5), key="-APP_THEME-"), sg.Button("Ok", size=(10, 1), pad=(100, None), key="-APP_THEME_OK-")],
    ]

    preferences_layout = [
        [sg.TabGroup([[sg.Tab("Text color", text_color_layout,), sg.Tab("Application theme", theme_layout)]], expand_x=True, expand_y=True)]
    ]

    preferences_window = sg.Window("Preferences - PyNotepad", preferences_layout, size=(500, 300),modal=True, resizable=False)

    while True:
        event, _ = preferences_window.read()

        if event == sg.WIN_CLOSED:
            break

        if event in ("-TEXT_COLOR_PREVIEW-"):
            background = preferences_window["-BG_COLOR-"].get()
            text_color = preferences_window["-TEXT_COLOR-"].get()

            if background in ("None", None):
                preferences_window["-TEXT_PREVIEW-"].update(background_color="white")
                preferences_window["-BG_COLOR-"].update("white")
            
            elif text_color in ("None", None):
                preferences_window["-TEXT_PREVIEW-"].update(text_color="black")
                preferences_window["-TEXT_COLOR-"].update("black")
            
            else:
                preferences_window["-TEXT_PREVIEW-"].update(background_color=background, text_color=text_color)
        
        if event in ("-TEXT_COLOR_SAVE-"):
            background = preferences_window["-BG_COLOR-"].get()
            text_color = preferences_window["-TEXT_COLOR-"].get()

            if background in ("None", None):
                preferences_window["-TEXT_PREVIEW-"].update(background_color="white")
                preferences_window["-BG_COLOR-"].update("white")
            
            elif text_color in ("None", None):
                preferences_window["-TEXT_PREVIEW-"].update(text_color="black")
                preferences_window["-TEXT_COLOR-"].update("black")

            preferences_window["-TEXT_PREVIEW-"].update(background_color=background,text_color=text_color)

            database.set_text_colors((background, text_color))
            text_colors = database.get_text_colors()
            window["-TEXT-"].update(background_color=background,text_color=text_color)

        if event in ("-TEXT_COLOR_RESET_DEFAULT-"):
            preferences_window["-TEXT_PREVIEW-"].update(background_color="white")
            preferences_window["-BG_COLOR-"].update("white")
            preferences_window["-TEXT_PREVIEW-"].update(text_color="black")
            preferences_window["-TEXT_COLOR-"].update("black")

            database.set_text_colors(("white", "black"))
            text_colors = database.get_text_colors()
            window["-TEXT-"].update(background_color="white", text_color="black")

        if event == "-APP_THEME_OK-":
            database.set_theme(preferences_window["-APP_THEME-"].get()[0])
            sg.popup_ok("Changes will be applied when restarting the editor")
    preferences_window.close()
    preferences_window = None

def open_close_window(content):
    global editing, close_window

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
        close_window = None
    else:
        return True


while True:
    event, values = window.read(timeout=1)

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

    if event in ("Exit (CTRL+SHIFT+Q)", "CTRL+SHIFT+Q", sg.WIN_CLOSE_ATTEMPTED_EVENT):
        close = open_close_window(values["-TEXT-"])

        if close:
            for win in (about_window, preferences_window, close_window):
                if win is not None:
                    win.close()
            break
            
    if event in ("New (CTRL+N)", "CTRL+N"):
        new_file()

    if event in ("Open (CTRL+O)", "CTRL+O"):
        open_file()

    if event in ("Save (CTRL+S)", "CTRL+S"):
        save_file(values["-TEXT-"])
        
    if event in ("Save as (CTRL+SHIFT+S)", "CTRL+SHIFT+S"):
        save_file_as(values["-TEXT-"])

    if event.endswith("::recent_file"):
        filename = event.replace("::recent_file", "")
        open_file(filename)

    if event == "Clear recently opened":
        database.clear_recent_files()
        update_recent_file_list()

    if event == "Preferences":
        open_preferences_window()

    if event == "About...":
        open_about_window()
window.close()

