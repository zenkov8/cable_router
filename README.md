# Cable Router

Set up a virtual environment:
```bash
python -m venv .venv
```

Activate the virtual environment:
```bash
.venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Add the building JSON model file to data:
```bash
data/building.json
```

And the configuration file:
```bash
data/config.yaml
```

Run the program via main.py with arguments from \cable_router:
--model — path to the building JSON model
--source — cable source coordinates (x,y)
--target — cable target coordinates (x,y)

Command examples:
```bash
python .\src\main.py --model data\потолок_без_угла_и_вентиляции.json --source=-5500,500 --target=200,-500
python .\src\main.py --model data\потолок_без_угла_и_вентиляции_подлиннее.json --source=-5500,500 --target=200,-500
python .\src\main.py --model data\потолок_и_вентиляция.json --source=-1000,-1000 --target=-1000,5000
python .\src\main.py --model data\прямоуголный_потолок.json --source=-100,-100 --target=-1000,5000
python .\src\main.py --model data\скошеный_потолок_с_вырезом.json --source=-10000,6000 --target=5000,6000
python .\src\main.py --model data\скошеный_потолок_с_вырезом_и_вентиляции.json --source=-10000,-2000 --target=5000,6000
python .\src\main.py --model data\скошеный_потолок_с_вырезом_и_вентиляции_подлиннее.json --source=-10000,6000 --target=5000,6000
```

6. To run tests:
```bash
pytest
```

