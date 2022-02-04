# Python Notepad
Este es un bloc de notas simple escrito en python usando [PySimpleGUI](https://pypi.org/project/PySimpleGUI/)

![Demostración](images/demonstration.gif)

Todas las capturas de pantalla estan en [screenshots.md](screenshots.md)

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

# Alternativa a PyInstaller
Si no te gusta usar un montón de comandos, puedes usar [psgcompiler](https://github.com/PySimpleGUI/psgcompiler) para compilar el programa usando una interfaz simple y amigable