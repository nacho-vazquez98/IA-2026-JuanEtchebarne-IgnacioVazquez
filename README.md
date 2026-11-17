# IA-2026-JuanEtchebarne-IgnacioVazquez

## Entornos de desarrollo

Acrobot y Connect Four tienen configuraciones de Poetry independientes. Ambos declaran Python `>=3.9,<3.13`. Los archivos `poetry.lock` se generaron con Poetry 2.1.1 y cada proyecto guarda su entorno en su propia carpeta `.venv/`.

Para instalar más adelante, ejecutá estos comandos desde la raíz del repositorio en PowerShell, sin un entorno virtual activo:

```powershell
Push-Location Acrobot
poetry install
Pop-Location

Push-Location ConnectFour
poetry install
Pop-Location
```

Ejecutá `poetry run` desde la carpeta del proyecto correspondiente. Para abrir un notebook desde el editor, seleccioná el intérprete de la `.venv` de ese proyecto.
