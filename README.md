# Pràctica de cerca local (ABIA): assignació de clients a centrals elèctriques

Hugo Andreu, Marie-Anne Boter i Anna Galstyan. Curs 2026-2027, quadrimestre de tardor.

## Estructura

- `code/`: implementació del problema, experiments i anàlisi
  - `parameters.py`: paràmetres d'una instància (`Params`)
  - `network_state.py`: representació de l'estat (`EnergyNetworkState`)
  - `operators.py`: operadors `Move` i `Swap`
  - `pre_processing.py`: matrius precalculades (subministrament, pèrdues, guany de cada client i cost d'encendre cada central)
  - `state_initializer.py`: estratègies de solució inicial 0, 1, 2 i 3 (solució buida)
  - `problem.py`: problema per al Hill Climbing (genera tots els successors) i heurística incremental
  - `problem_sa.py`: problema per al Simulated Annealing (genera un sol successor a l'atzar)
  - `experiments.py`: experiments 1 a 6, A i B
  - `resultats.py`: guarda cada execució a `resultats/<experiment>.csv`
  - `analisi.py`: estadística (`resultats/analisi.txt`) i gràfics (`resultats/figures/`)
  - `given.py`: accés al codi donat
- `given_code/`: codi donat per l'assignatura
- `resultats/`: CSV de cada experiment, `analisi.txt`, figures, logs i traces de l'evolució de HC i SA

## Execució

Cal Python 3 amb `aima` (2023.2.6), `numpy` i `matplotlib`. Des de `code/`:

```
python experiments.py 1 2 3A 3B 4 5 6 A B   # executa els experiments indicats
python analisi.py                          # genera analisi.txt i les figures a partir dels CSV
python analisi.py traca                    # a més, recalcula l'evolució de HC i SA (figura 7)
```

Cada experiment sobreescriu el seu CSV quan es torna a executar. Tots fan servir les seeds 0 a 9 i són reproduïbles.
Alguns triguen força: l'experiment 5 complet, unes dues hores, i la majoria dels altres, entre 10 i 50 minuts.
