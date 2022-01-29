# Python Notepad
Este es un bloc de notas simple escrito en python usando [PySimpleGUI](https://pypi.org/project/PySimpleGUI/)

![Captura](./images/screenshot.png)

# Instalación
```
git clone https://github.com/DAFEX6390/python-notepad.git

cd python-notepad

pip3 install -r requirements.txt

python3 src/main.py
```

# Crear un ejecutable usando [PyInstaller](https://pypi.org/project/pyinstaller/)

## En windows
```
pyinstaller --add-data src/assets/icon.png;assets src/main.py --windowed
```

## En linux
```
pyinstaller --add-data 'src/assets/icon.png:assets' src/main.py
```