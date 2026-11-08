#Anàlisi dels experiments: llegeix resultats/<exp>.csv i genera
#   resultats/analisi.txt  -> mitjana (desviació) i t-test aparellat
#   resultats/figures/     -> gràfics de cada experiment
#
#Ús (des de code/):
#   python analisi.py          -> analitza tots els experiments que tinguin csv
#   python analisi.py traca    -> abans, executa HC i SA en una seed i guarda l'evolució de h (~1 min)
import csv
import math
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

DIR = Path(__file__).parent.parent / "resultats"
FIG = DIR / "figures"


# ======================= LECTURA =======================

def llegir(nom):
    #retorna les files del csv amb els números convertits, o None si no existeix
    path = DIR / f"{nom}.csv"
    if not path.exists():
        return None
    return [{k: _num(v) for k, v in f.items()} for f in csv.DictReader(open(path))]

def _num(v):
    try:
        return float(v)
    except ValueError:
        return v

def agrupa(files, *cols):
    #{valor de les columnes: [files]}
    g = defaultdict(list)
    for f in files:
        g[tuple(f[c] for c in cols) if len(cols) > 1 else f[cols[0]]].append(f)
    return dict(sorted(g.items()))

def per_seed(files, col):
    return {f["seed"]: f[col] for f in files}


# ======================= ESTADÍSTICA (analisi.txt) =======================

T_CRITICA = 2.262 #t de Student, 9 graus de llibertat (10 seeds), confiança del 95%
TEXT = []

def escriu(linia=""):
    print(linia)
    TEXT.append(linia)

def ms(files, col):
    #"mitjana (desviació)" d'una columna
    xs = [f[col] for f in files]
    return f"{mean(xs):.2f} ({stdev(xs):.2f})" if len(xs) > 1 else f"{xs[0]:.2f}"

def ttest(nom_a, files_a, nom_b, files_b, col="value"):
    #t-test aparellat: la mateixa seed és el mateix problema, així que comparem la diferència seed a seed
    a, b = per_seed(files_a, col), per_seed(files_b, col)
    d = [a[s] - b[s] for s in a if s in b]
    if stdev(d) == 0:
        escriu(f"  {col}: {nom_a} - {nom_b} = {mean(d):.2f} (sempre igual)")
        return
    t = mean(d) / (stdev(d) / math.sqrt(len(d)))
    conclusio = "significativa" if abs(t) > T_CRITICA else "no significativa"
    escriu(f"  {col}: {nom_a} - {nom_b} = {mean(d):.2f}, t = {t:.2f} -> diferència {conclusio}")

def resum(titol, grups, cols):
    escriu(f"\n=== {titol} ===")
    for clau, fs in grups.items():
        escriu(f"{clau} (n={len(fs)}): " + ", ".join(f"{c} = {ms(fs, c)}" for c in cols))

def estadistica():
    files = llegir("exp1")
    if files:
        g = agrupa(files, "operadors")
        resum("EXP 1: operadors (HC)", g, ["value", "temps", "passos"])
        ttest("Move+Swap", g["Move+Swap"], "Move", g["Move"])
        ttest("Move+Swap", g["Move+Swap"], "Move", g["Move"], "temps")

    files = llegir("exp2")
    if files:
        g = agrupa(files, "ini_sol_type")
        resum("EXP 2: solució inicial (HC)", g, ["value", "temps", "passos"])
        for a, b in ((1, 0), (1, 2)):
            ttest(f"ini{a}", g[a], f"ini{b}", g[b])
            ttest(f"ini{a}", g[a], f"ini{b}", g[b], "temps")

    hc = agrupa(llegir("exp2") or [], "ini_sol_type").get(1) #referència: HC amb l'estratègia 1

    files = llegir("exp3A")
    if files:
        g = agrupa(files, "k", "T_final")
        resum("EXP 3A: k i T_final (SA, limit 500.000)", g, ["value", "temps"])
        for (k, tf), fs in g.items():
            ttest(f"SA(k={k:g},Tf={tf:g})", fs, "HC", hc)

    files = llegir("exp3B")
    if files:
        g = agrupa(files, "limit")
        resum("EXP 3B: limit (SA)", g, ["value", "temps"])
        for limit, fs in g.items():
            ttest(f"SA({limit:.0f})", fs, "HC", hc)

    files = llegir("exp4")
    if files:
        resum("EXP 4: clients (40 centrals, HC)", agrupa([f for f in files if f["centrals"] == 40], "clients"), ["temps", "passos"])
        resum("EXP 4: centrals (1000 clients, HC)", agrupa([f for f in files if f["clients"] == 1000], "centrals"), ["temps", "passos"])

    files = llegir("exp5")
    if files:
        resum("EXP 5: penalització (solució inicial buida)", agrupa(files, "algorisme", "penalitzacio"),
              ["garantits_sense_servir", "profit", "temps"])

    files = llegir("exp6")
    if files:
        g = agrupa(files, "algorisme", "centrals_ABC")
        resum("EXP 6: centrals de tipus C", g, ["A_on", "B_on", "C_on", "profit", "temps"])
        for alg in ("HC", "SA"):
            for c in ("5-10-50", "5-10-75"):
                if (alg, c) in g and (alg, "5-10-25") in g:
                    for col in ("A_on", "B_on"):
                        ttest(f"{alg} {c}", g[(alg, c)], f"{alg} 5-10-25", g[(alg, "5-10-25")], col)

    files = llegir("expA")
    if files:
        resum("EXP A: ponderació w1 (HC)", agrupa(files, "w1"), ["profit", "lost_mw", "temps"])

    files = llegir("expB")
    if files:
        g = agrupa(files, "algorisme")
        resum("EXP B: HC vs SA", g, ["value", "temps"])
        if "HC" in g and "SA" in g:
            ttest("SA", g["SA"], "HC", g["HC"])
            ttest("SA", g["SA"], "HC", g["HC"], "temps")

    (DIR / "analisi.txt").write_text("\n".join(TEXT) + "\n", encoding="utf-8")


# ======================= GRÀFICS (resultats/figures) =======================

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import numpy as np

COLORS = {"HC": "#1f77b4", "SA": "#d62728"}

def desa(fig, nom):
    FIG.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIG / f"{nom}.png", dpi=200)
    plt.close(fig)

def boxplot(ax, dades, etiquetes, titol, ylabel, colors=None):
    #boxplot amb els 10 punts a sobre
    ax.boxplot(dades, tick_labels=etiquetes, widths=0.5, medianprops={"color": "black"})
    for i, d in enumerate(dades, 1):
        ax.scatter(np.full(len(d), i) + np.linspace(-0.08, 0.08, len(d)), d, s=12, alpha=0.6, zorder=3,
                   color=(colors[i - 1] if colors else "#555555"))
    ax.set_title(titol)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", alpha=0.3)

def linia(ax, xs, grups, col, **kw):
    #mitjana ± desviació d'una columna per a cada x
    v = [[f[col] for f in fs] for fs in grups]
    ax.errorbar(xs, [mean(y) for y in v], yerr=[stdev(y) if len(y) > 1 else 0 for y in v], marker="o", capsize=3, **kw)

def figura_comparacio(grups, ref, nom, titol, etiquetes=None, colors=None, pas="passos"):
    #3 panells: diferència de h respecte la referència (mateixa seed), temps i passos
    claus = list(grups)
    etiquetes = etiquetes or [str(c) for c in claus]
    href = per_seed(grups[ref], "value")
    difs = [[f["value"] - href[f["seed"]] for f in grups[c]] for c in claus]
    fig, axs = plt.subplots(1, 3, figsize=(12, 3.8))
    boxplot(axs[0], difs, etiquetes, f"h respecte {etiquetes[claus.index(ref)]} (mateixa seed)", "diferència de h (€)", colors)
    axs[0].axhline(0, color="grey", lw=0.8, ls="--")
    boxplot(axs[1], [[f["temps"] for f in grups[c]] for c in claus], etiquetes, "Temps d'execució", "temps (s)", colors)
    boxplot(axs[2], [[f[pas] for f in grups[c]] for c in claus], etiquetes, "Passos del HC" if pas == "passos" else pas, pas, colors)
    fig.suptitle(titol)
    desa(fig, nom)


def grafic_exp1():
    files = llegir("exp1")
    if not files: return
    figura_comparacio(agrupa(files, "operadors"), "Move", "exp1_operadors", "Experiment 1: Move vs Move+Swap (HC, 10 seeds)")


def grafic_exp2():
    files = llegir("exp2")
    if not files: return
    g = agrupa(files, "ini_sol_type")
    figura_comparacio(g, 1, "exp2_sol_inicial", "Experiment 2: estratègies de solució inicial (HC, Move+Swap)",
                      etiquetes=[f"estratègia {c:.0f}" for c in g])

    #h inicial vs h final (la h inicial no és al csv: la recalculem, és ràpid)
    from dataclasses import replace
    from experiments import escenaris
    from problem import EnergyNetworkProblem
    fig, ax = plt.subplots(figsize=(6, 4.2))
    for ini, fs in g.items():
        x, y = [], []
        for f in fs:
            e = EnergyNetworkProblem(replace(escenaris[int(f["seed"])], ini_sol_type=int(ini)))
            x.append(e.value(e.initial))
            y.append(f["value"])
        ax.scatter(x, y, label=f"estratègia {ini:.0f}", s=25)
    ax.set_xlabel("h de la solució inicial (€)")
    ax.set_ylabel("h de la solució final (€)")
    ax.set_title("Experiment 2: h inicial vs h final")
    ax.legend()
    ax.grid(alpha=0.3)
    desa(fig, "exp2_inicial_vs_final")


def grafic_exp3A():
    files, hc = llegir("exp3A"), llegir("exp2")
    if not files or not hc: return
    hc = per_seed([f for f in hc if f["ini_sol_type"] == 1], "value")
    g = agrupa(files, "k", "T_final")

    #mapa de calor: h mitjana del SA menys h del HC
    ks = sorted({c[0] for c in g})
    tfs = sorted({c[1] for c in g}, reverse=True)
    mat = np.full((len(ks), len(tfs)), np.nan)
    for (k, tf), fs in g.items():
        mat[ks.index(k), tfs.index(tf)] = mean(f["value"] - hc[f["seed"]] for f in fs)
    fig, ax = plt.subplots(figsize=(6.5, 5))
    im = ax.imshow(mat, cmap="RdBu", norm=TwoSlopeNorm(vcenter=0, vmin=np.nanmin(mat), vmax=max(np.nanmax(mat), 1)), aspect="auto")
    for i in range(len(ks)):
        for j in range(len(tfs)):
            ax.text(j, i, "no té sentit\n(T_final ≥ k)" if np.isnan(mat[i, j]) else f"{mat[i, j]:,.0f} €",
                    ha="center", va="center", fontsize=8, color="grey" if np.isnan(mat[i, j]) else "black")
    ax.set_xticks(range(len(tfs)), [f"{t:g}" for t in tfs])
    ax.set_yticks(range(len(ks)), [f"{k:g}" for k in ks])
    ax.set_xlabel("T_final")
    ax.set_ylabel("k (temperatura inicial)")
    ax.set_title("Experiment 3A: h mitjana del SA menys h del HC\n(limit = 500.000, 10 seeds)")
    fig.colorbar(im, ax=ax, label="diferència de h (€)")
    desa(fig, "exp3A_rejilla")

    #probabilitat d'acceptar un estat pitjor al llarg de les iteracions (com les figures 7.5/7.6 del pdf)
    millor = max(g, key=lambda c: mean(f["value"] for f in g[c]))
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True)
    t = np.linspace(0, 500_000, 2000)
    for ax, k in zip(axs, (millor[0], 100)):
        T = k * np.exp(-math.log(k / millor[1]) / 500_000 * t)
        for de, etq in ((0.001, "ΔE = -0,001 € (Swap petit)"), (0.01, "ΔE = -0,01 € (Swap típic)"), (0.1, "ΔE = -0,1 €"),
                        (1000, "ΔE = -1.000 € (deixar un client)")):
            ax.plot(t, np.exp(-de / T), label=etq)
        ax.set_title(f"k = {k:g}, T_final = {millor[1]:g}")
        ax.set_xlabel("iteració")
        ax.grid(alpha=0.3)
    axs[0].set_ylabel("P(acceptar)")
    axs[1].legend(fontsize=8)
    fig.suptitle("Probabilitat d'acceptar un estat pitjor, P = exp(ΔE / T(t)), amb T(t) = k·exp(-lam·t)")
    desa(fig, "exp3_prob_acceptacio")


def grafic_exp3B():
    files, hc = llegir("exp3B"), llegir("exp2")
    if not files or not hc: return
    hc = [f for f in hc if f["ini_sol_type"] == 1]
    href = per_seed(hc, "value")
    g = agrupa(files, "limit")
    Ls = list(g)
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.8))
    boxplot(axs[0], [[f["value"] - href[f["seed"]] for f in g[L]] for L in Ls], [f"{L:,.0f}" for L in Ls],
            "h del SA menys h del HC (mateixa seed)", "diferència de h (€)", [COLORS["SA"]] * len(Ls))
    axs[0].axhline(0, color="grey", lw=0.8, ls="--")
    axs[0].set_xlabel("limit (iteracions)")
    linia(axs[1], Ls, g.values(), "temps", color=COLORS["SA"], label="SA")
    axs[1].axhline(mean(f["temps"] for f in hc), color=COLORS["HC"], ls="--", label="HC (exp 2)")
    axs[1].set_xlabel("limit (iteracions)")
    axs[1].set_ylabel("temps (s)")
    axs[1].set_title("Temps d'execució (mitjana ± desv.)")
    axs[1].legend()
    axs[1].grid(alpha=0.3)
    fig.suptitle(f"Experiment 3B: SA amb k = {files[0]['k']:g}, T_final = {files[0]['T_final']:g}")
    desa(fig, "exp3B_limit")


def grafic_exp4():
    files = llegir("exp4")
    if not files: return
    fig, axs = plt.subplots(1, 2, figsize=(11, 4))
    for ax, (col, fix, val, etq) in zip(axs, (("clients", "centrals", 40, "clients (40 centrals)"),
                                             ("centrals", "clients", 1000, "centrals (1000 clients)"))):
        g = agrupa([f for f in files if f[fix] == val], col)
        xs = list(g)
        for x in xs:
            ax.scatter([x] * len(g[x]), [f["temps"] for f in g[x]], color="grey", s=8, alpha=0.4)
        linia(ax, xs, g.values(), "temps", color=COLORS["HC"], label="temps mitjà (± desv.)")
        if col == "clients":
            #referències quadràtica i cúbica que surten del primer punt (com la figura 7.4 del pdf)
            t0 = mean(f["temps"] for f in g[xs[0]])
            xx = np.linspace(xs[0], xs[-1], 100)
            ax.plot(xx, t0 * (xx / xs[0]) ** 2, ls="--", color="#2ca02c", label="referència quadràtica")
            ax.plot(xx, t0 * (xx / xs[0]) ** 3, ls=":", color="#ff7f0e", label="referència cúbica")
        ax.set_xlabel(etq)
        ax.set_ylabel("temps (s)")
        ax.set_title(f"Temps respecte el nombre de {col}")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)
    fig.suptitle("Experiment 4: HC, Move+Swap, estratègia inicial 1 (10 seeds)")
    desa(fig, "exp4_escalat")


def grafic_exp5():
    files = llegir("exp5")
    if not files: return
    g = agrupa(files, "algorisme", "penalitzacio")
    fig, axs = plt.subplots(1, 2, figsize=(11, 4))
    for alg in ("HC", "SA"):
        ps = [p for a, p in g if a == alg]
        if not ps: continue
        x = [max(p, 10) for p in ps] #eix log: la penalització 0 la dibuixem a 10
        for ax, col in zip(axs, ("garantits_sense_servir", "profit")):
            linia(ax, x, [g[(alg, p)] for p in ps], col, label=alg, color=COLORS[alg])
    for ax, etq in zip(axs, ("clients garantits sense servir", "benefici real (€)")):
        ax.set_xscale("log")
        ax.set_xlabel("penalització (€/MW garantit no servit, 0 dibuixat a 10)")
        ax.set_ylabel(etq)
        ax.grid(alpha=0.3)
        ax.legend()
    axs[0].set_title("Garantits sense servir (mitjana ± desv.)")
    axs[1].set_title("Benefici real de la solució")
    fig.suptitle("Experiment 5: penalització a la heurística partint de la solució buida")
    desa(fig, "exp5_penalitzacio")


def grafic_exp6():
    files = llegir("exp6")
    if not files: return
    g = agrupa(files, "algorisme", "centrals_ABC")
    algs = [a for a in ("HC", "SA") if any(k[0] == a for k in g)]
    cs = sorted({c for _, c in g}, key=lambda c: int(c.split("-")[2]))
    fig, axs = plt.subplots(1, 2, figsize=(11, 4))
    amp = 0.38
    for i, alg in enumerate(algs):
        cs_alg = [c for c in cs if (alg, c) in g]
        x = np.array([cs.index(c) for c in cs_alg]) + (i - (len(algs) - 1) / 2) * amp
        base = np.zeros(len(cs_alg))
        for tipus, color in (("A", "#4c72b0"), ("B", "#55a868"), ("C", "#c44e52")):
            v = np.array([mean(f[f"{tipus}_on"] for f in g[(alg, c)]) for c in cs_alg])
            axs[0].bar(x, v, amp * 0.95, bottom=base, color=color, label=f"tipus {tipus}" if i == 0 else None, edgecolor="white")
            base += v
        for xi, b in zip(x, base):
            axs[0].text(xi, b + 0.5, alg, ha="center", fontsize=8)
        linia(axs[1], [int(c.split("-")[2]) for c in cs_alg], [g[(alg, c)] for c in cs_alg], "temps", label=alg, color=COLORS[alg])
    axs[0].set_xticks(range(len(cs)), cs)
    axs[0].set_xlabel("centrals A-B-C")
    axs[0].set_ylabel("centrals enceses (mitjana)")
    axs[0].set_title("Centrals enceses per tipus")
    axs[0].legend()
    axs[1].set_xlabel("centrals de tipus C")
    axs[1].set_ylabel("temps (s)")
    axs[1].set_title("Temps d'execució (mitjana ± desv.)")
    axs[1].legend()
    axs[1].grid(alpha=0.3)
    fig.suptitle("Experiment 6: duplicar i triplicar les centrals de tipus C (1000 clients)")
    desa(fig, "exp6_centrals_C")


def grafic_expA():
    files = llegir("expA")
    if not files: return
    g = agrupa(files, "w1")
    x = [max(w, 0.001) for w in g] #eix log: w1 = 0 el dibuixem a 0,001
    fig, axs = plt.subplots(1, 3, figsize=(12, 3.8))
    for ax, col, etq in zip(axs, ("profit", "lost_mw", "temps"), ("benefici real (€)", "MW perduts", "temps (s)")):
        linia(ax, x, g.values(), col, color=COLORS["HC"])
        ax.set_xscale("log")
        ax.set_xlabel("w1 (0 dibuixat a 0,001)")
        ax.set_ylabel(etq)
        ax.grid(alpha=0.3)
    fig.suptitle("Experiment A: h = benefici - w1 · MW perduts (HC, mitjana ± desv.)")
    desa(fig, "expA_ponderacio")


def grafic_expB():
    files = llegir("expB")
    if not files: return
    g = agrupa(files, "algorisme")
    if "HC" in g and "SA" in g:
        figura_comparacio({"HC": g["HC"], "SA": g["SA"]}, "HC", "expB_hc_vs_sa", "Experiment B: HC vs SA (10 seeds)",
                          colors=[COLORS["HC"], COLORS["SA"]], pas="passos_o_iteracions")


class Traca:
    #embolcalla el problema i apunta la h de l'estat actual cada cop que l'algorisme en demana els successors
    def __init__(self, problem):
        self.p, self.h = problem, []
    def actions(self, state):
        self.h.append(self.p.value(state))
        return self.p.actions(state)
    def __getattr__(self, nom):
        return getattr(self.p, nom)


def calcula_traca(seed=8):
    #seed 8: és on el SA millora més el HC als exp 3A/3B; és un exemple, no la mitjana
    import random
    from aima.search import hill_climbing, simulated_annealing
    from experiments import escenaris, schedule
    from problem import EnergyNetworkProblem
    from problem_sa import EnergyNetworkProblemSA
    params = escenaris[seed]
    for nom, classe in (("hc", EnergyNetworkProblem), ("sa", EnergyNetworkProblemSA)):
        tr = Traca(classe(params))
        random.seed(params.seed)
        sol = hill_climbing(tr) if nom == "hc" else simulated_annealing(tr, schedule)
        tr.h.append(tr.p.value(sol))
        pas = 1 if nom == "hc" else 100 #del SA en guardem 1 de cada 100 iteracions
        with open(DIR / f"traca_{nom}.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["seed", "iteracio", "h"])
            for i in list(range(0, len(tr.h), pas)) + [len(tr.h) - 1]:
                w.writerow([seed, i, tr.h[i]])


def grafic_traca():
    hc, sa = llegir("traca_hc"), llegir("traca_sa")
    if not hc or not sa: return
    from experiments import schedule
    fig, axs = plt.subplots(1, 2, figsize=(12, 4), gridspec_kw={"width_ratios": [2, 1]})
    it = [f["iteracio"] for f in sa]
    axs[0].plot(it, [f["h"] for f in sa], color=COLORS["SA"], lw=0.8, label="SA (h de l'estat actual)")
    axs[0].axhline(hc[-1]["h"], color=COLORS["HC"], ls="--", label="h final del HC")
    axs[0].set_xlabel("iteració del SA")
    axs[0].set_ylabel("h (€)")
    axs[0].legend(loc="lower right")
    axs[0].grid(alpha=0.3)
    tw = axs[0].twinx()
    tw.plot(it, [schedule(i) for i in it], color="grey", lw=0.8, ls=":")
    tw.set_yscale("log")
    tw.set_ylabel("temperatura T (escala log, línia de punts)")
    axs[0].set_title("Simulated Annealing")
    axs[1].plot([f["iteracio"] for f in hc], [f["h"] for f in hc], marker=".", color=COLORS["HC"])
    axs[1].axhline(sa[-1]["h"], color=COLORS["SA"], ls="--", label="h final del SA")
    axs[1].set_xlabel("pas del HC")
    axs[1].set_ylabel("h (€)")
    axs[1].set_title("Hill Climbing")
    axs[1].legend(loc="lower right")
    axs[1].grid(alpha=0.3)
    fig.suptitle(f"Evolució de la heurística en una execució (seed {hc[0]['seed']:.0f}, estratègia inicial 1)")
    desa(fig, "evolucio_hc_sa")


if __name__ == "__main__":
    if "traca" in sys.argv:
        calcula_traca()
    estadistica()
    for grafic in (grafic_exp1, grafic_exp2, grafic_exp3A, grafic_exp3B, grafic_exp4, grafic_exp5, grafic_exp6,
                   grafic_expA, grafic_expB, grafic_traca):
        grafic()
    print(f"\nGuardat a {DIR / 'analisi.txt'} i {FIG}/")
