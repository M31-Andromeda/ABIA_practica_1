#Guarda cada execució dels experiments com una fila de resultats/<experiment>.csv
import csv
from pathlib import Path

DIR = Path(__file__).parent.parent / "resultats"
_oberts = set() #experiments ja començats en aquesta execució

def guardar(experiment, fila):
    DIR.mkdir(exist_ok=True)
    path = DIR / f"{experiment}.csv"
    nou = experiment not in _oberts #la primera fila de cada execució sobreescriu el csv antic
    _oberts.add(experiment)
    with open(path, "w" if nou else "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fila.keys())
        if nou:
            writer.writeheader()
        writer.writerow(fila)
