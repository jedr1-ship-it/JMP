"""Build municipality-month panel from CNMH OMC case files and produce proposal figures.
Usage: python3 -I build_panel_and_figs.py <datadir> <figdir> <deriveddir>
"""
import sys, warnings
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
warnings.filterwarnings("ignore")

datadir, figdir, derdir = sys.argv[1], sys.argv[2], sys.argv[3]

# ---------- style ----------
fams = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams.update({
    "font.family": "TeX Gyre Heros" if "TeX Gyre Heros" in fams else "DejaVu Sans",
    "font.size": 9, "axes.titlesize": 9.5, "axes.labelsize": 9, "legend.fontsize": 8,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#52514e", "axes.labelcolor": "#0b0b0b", "xtick.color": "#52514e", "ytick.color": "#52514e",
    "axes.grid": True, "grid.color": "#e6e5e1", "grid.linewidth": 0.6, "axes.axisbelow": True,
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.bbox": "tight", "savefig.pad_inches": 0.04,
})
C = {"PARA": "#2a78d6", "GUE": "#eb6834", "EST": "#1baf7a", "POSD": "#eda100", "NI": "#8a8984"}
LAB = {"PARA": "Paramilitares", "GUE": "Guerrilla", "EST": "Agentes del Estado", "POSD": "Posdesmovilización", "NI": "No identificado / otro"}

# ---------- load ----------
cols = ["ID Caso", "Año", "Mes", "Día", "Código DANE de Municipio", "Municipio", "Departamento", "Región",
        "Presunto Responsable", "Descripción Presunto Responsable", "Total de Víctimas del Caso", "Latitud", "Longitud"]
ma = pd.read_excel(f"{datadir}/CMasacres_202503.xlsx")[cols]; ma["tipo"] = "MA"
as_ = pd.read_excel(f"{datadir}/CAsesionatosSelectivos_202503.xlsx")[cols]; as_["tipo"] = "AS"
df = pd.concat([ma, as_], ignore_index=True)
df = df.rename(columns={"Año": "year", "Mes": "month", "Código DANE de Municipio": "muni", "Total de Víctimas del Caso": "victims",
                        "Presunto Responsable": "resp", "Región": "region", "Departamento": "depto", "Municipio": "muni_name"})
def grp(r):
    if r in ("GRUPO PARAMILITAR", "AGENTE DEL ESTADO - GRUPO PARAMILITAR"): return "PARA"
    if r in ("GRUPO POSDESMOVILIZACIÓN", "AGENTE DEL ESTADO - GRUPO POSDESMOVILIZACIÓN"): return "POSD"
    if r == "GUERRILLA": return "GUE"
    if r == "AGENTE DEL ESTADO": return "EST"
    return "NI"
df["grp"] = df["resp"].map(grp)
df["muni"] = df["muni"].astype(str).str.zfill(5)
df = df[(df.year >= 1985) & (df.year <= 2015)].copy()

# ---------- annual national series ----------
ann = df.groupby(["year", "grp"])["victims"].sum().unstack(fill_value=0)
ann.to_csv(f"{derdir}/cnmh_annual_victims_by_responsible.csv")
fig, ax = plt.subplots(figsize=(5.6, 3.0))
ax.axvspan(2003.85, 2006.65, color="#eda100", alpha=0.12, lw=0)
ax.text(2005.25, ann.max().max() * 0.97, "Desmovilizaciones\nAUC (nov-03 a ago-06)", ha="center", va="top", fontsize=7.5, color="#52514e")
for g in ["PARA", "GUE", "EST", "POSD", "NI"]:
    if g in ann: ax.plot(ann.index, ann[g], color=C[g], lw=2, label=LAB[g])
ax.set_xlim(1985, 2015); ax.set_ylabel("Víctimas de masacres y asesinatos selectivos"); ax.set_xlabel("")
ax.legend(frameon=False, ncol=2, loc="upper left")
fig.savefig(f"{figdir}/fig1_victimas_anuales.pdf"); plt.close(fig)

# ---------- monthly municipality panel ----------
m = df[(df.month >= 1) & (df.month <= 12)].copy()
m["ym"] = m.year * 12 + (m.month - 1)
panel = m.groupby(["muni", "ym", "grp"])["victims"].sum().unstack(fill_value=0).reset_index()
panel["year"] = panel.ym // 12; panel["month"] = panel.ym % 12 + 1
panel.to_csv(f"{derdir}/cnmh_muni_month_victims.csv", index=False)

# ---------- event study around demobilization by CNMH subregion ----------
zones = [  # region, label, demob (year, month), clean
    ("CATATUMBO", "Catatumbo (B. Catatumbo, dic-04)", (2004, 12), True),
    ("CENTRO DEL VALLE", "Centro del Valle (B. Calima, dic-04)", (2004, 12), True),
    ("MONTES DE MARIA", "Montes de María (jul-05)", (2005, 7), True),
    ("ORIENTE ANTIOQUEÑO", "Oriente antioqueño (H. de Granada, ago-05)", (2005, 8), True),
    ("PIEDEMONTE LLANERO", "Piedemonte llanero (Centauros, sep-05)", (2005, 9), True),
    ("NORDESTE ANTIOQUEÑO", "Nordeste antioqueño (BCB, dic-05)", (2005, 12), True),
    ("SUR DE BOLIVAR", "Sur de Bolívar (BCB, ene-06)", (2006, 1), True),
    ("SIERRA NEVADA DE SANTA MARTA", "Sierra Nevada (Tayrona/Norte, feb-mar-06)", (2006, 3), True),
    ("SERRANIA DEL PERIJA", "Serranía del Perijá (B. Norte, mar-06)", (2006, 3), True),
    ("VALLE DE ABURRA", "Medellín (Cacique Nutibara, nov-03)*", (2003, 11), False),
    ("URABA", "Urabá (Bananero nov-04 / Élmer Cárdenas 06)*", (2004, 11), False),
    ("ALTO SINU Y SAN JORGE", "Córdoba (B. Córdoba, ene-05)*", (2005, 1), False),
]
mz = m[m.grp.isin(["PARA", "POSD"])]
rows = []
fig, axes = plt.subplots(4, 3, figsize=(7.2, 7.4), sharex=True)
for ax, (reg, lab, (dy, dm), clean) in zip(axes.flat, zones):
    s = mz[mz.region == reg].groupby("ym")["victims"].sum()
    d0 = dy * 12 + (dm - 1)
    idx = np.arange(d0 - 36, d0 + 37)
    s = s.reindex(idx, fill_value=0)
    t = idx - d0
    sm = pd.Series(s.values).rolling(3, center=True, min_periods=1).mean().values
    pre = s[(t >= -12) & (t <= -1)].mean(); post = s[(t >= 1) & (t <= 12)].mean()
    rows.append({"region": reg, "demob": f"{dy}-{dm:02d}", "clean": clean, "pre12_mean": pre, "post12_mean": post,
                 "ratio_post_pre": post / pre if pre > 0 else np.nan, "munis": mz[mz.region == reg].muni.nunique()})
    ax.fill_between(t, 0, s.values, color="#dbe7f7", lw=0)
    ax.plot(t, sm, color=C["PARA"], lw=1.8)
    ax.axvline(0, color="#0b0b0b", lw=0.8, ls="--")
    ax.set_title(lab, loc="left", fontsize=8, color="#0b0b0b" if clean else "#52514e")
    ax.text(0.98, 0.9, f"pre {pre:.1f} → post {post:.1f}/mes", transform=ax.transAxes, ha="right", va="top", fontsize=7, color="#52514e")
    ax.set_xlim(-36, 36)
for ax in axes[-1]: ax.set_xlabel("Meses desde la desmovilización del bloque")
for ax in axes[:, 0]: ax.set_ylabel("Víctimas/mes")
fig.text(0.01, 0.005, "* Zonas con 'post' contaminado por grupos posdesmovilización. Series: víctimas de masacres y asesinatos selectivos atribuidas a paramilitares y posdesmovilización (CNMH-OMC, corte mar-2025); media móvil de 3 meses.", fontsize=6.5, color="#52514e")
fig.tight_layout(rect=(0, 0.02, 1, 1))
fig.savefig(f"{figdir}/fig2_event_study_desmovilizacion.pdf"); plt.close(fig)
pd.DataFrame(rows).to_csv(f"{derdir}/zones_pre_post.csv", index=False)

# ---------- entry timing: first paramilitary massacre by municipality ----------
pm = df[(df.grp == "PARA") & (df.tipo == "MA") & (df.year.between(1990, 2006))]
first = pm.groupby("muni")["year"].min()
fig, axes = plt.subplots(1, 2, figsize=(6.2, 2.5))
vc = first.value_counts().sort_index()
axes[0].bar(vc.index, vc.values, color=C["PARA"], width=0.8)
axes[0].set_title("Año de la primera masacre paramilitar\n(municipios con ≥1 masacre 1990-2006)", loc="left")
axes[0].set_ylabel("Municipios"); axes[0].set_xlim(1989.5, 2006.5)
demob = {"2003-11": 1, "2003-12": 1, "2004-11": 1, "2004-12": 4, "2005-01": 2, "2005-02": 1, "2005-06": 1, "2005-07": 2, "2005-08": 3,
         "2005-09": 3, "2005-10": 1, "2005-12": 3, "2006-01": 3, "2006-02": 3, "2006-03": 2, "2006-04": 3, "2006-08": 1}
dk = list(demob.keys()); dv = list(demob.values())
x = [int(k[:4]) * 12 + int(k[5:]) - 1 for k in dk]
axes[1].bar(x, dv, color=C["POSD"], width=0.9)
ticks = [2003 * 12 + 10, 2004 * 12 + 5, 2004 * 12 + 11, 2005 * 12 + 5, 2005 * 12 + 11, 2006 * 12 + 5]
axes[1].set_xticks(ticks); axes[1].set_xticklabels(["nov-03", "jun-04", "dic-04", "jun-05", "dic-05", "jun-06"])
axes[1].set_title("Actos de desmovilización colectiva AUC\n(OACP, 35 fechados de 38)", loc="left"); axes[1].set_ylabel("Actos")
fig.tight_layout(); fig.savefig(f"{figdir}/fig3_entrada_y_salida_escalonadas.pdf"); plt.close(fig)

# ---------- cohort dose by age window ----------
nat = m[m.grp == "PARA"].groupby("ym")["victims"].sum()
nat = nat.reindex(np.arange(1985 * 12, 2016 * 12), fill_value=0)
windows = {"In utero (−9 a −1 m)": (-9, -1), "0–2 años": (0, 35), "3–5 años": (36, 71), "6–10 años": (72, 131)}
cohorts = range(1988, 2009)
dose = pd.DataFrame(index=cohorts, columns=windows.keys(), dtype=float)
for c in cohorts:
    b = c * 12 + 6  # born July
    for w, (a, z) in windows.items():
        idx = np.arange(b + a, b + z + 1)
        idx = idx[(idx >= nat.index.min()) & (idx <= nat.index.max())]
        dose.loc[c, w] = nat.loc[idx].sum() / (len(idx) / 12) if len(idx) else np.nan
dose.to_csv(f"{derdir}/cohort_dose_by_window.csv")
fig, ax = plt.subplots(figsize=(5.6, 3.0))
wc = ["#8a8984", C["PARA"], C["GUE"], C["EST"]]
for (w, col) in zip(windows.keys(), wc):
    ax.plot(dose.index, dose[w], color=col, lw=2, label=w)
ax.set_xlabel("Cohorte de nacimiento"); ax.set_ylabel("Víctimas paramilitares/año (nacional)\nmientras el niño tenía esa edad")
ax.legend(frameon=False, ncol=2, loc="upper right"); ax.set_xlim(1988, 2008)
fig.savefig(f"{figdir}/fig4_dosis_por_cohorte_y_ventana.pdf"); plt.close(fig)

# ---------- stats for slides ----------
sub = df[df.year.between(1997, 2002)]
out = {
 "munis_total_in_file": df.muni.nunique(),
 "munis_para_massacre_1997_2002": sub[(sub.grp == "PARA") & (sub.tipo == "MA")].muni.nunique(),
 "munis_para_AS_1997_2002": sub[(sub.grp == "PARA") & (sub.tipo == "AS")].muni.nunique(),
 "para_victims_1997_2002": int(sub[sub.grp == "PARA"].victims.sum()),
 "para_victims_2003_2006": int(df[df.year.between(2003, 2006) & (df.grp == "PARA")].victims.sum()),
 "posd_victims_2007_2010": int(df[df.year.between(2007, 2010) & (df.grp == "POSD")].victims.sum()),
 "all_victims_1997_2002": int(sub.victims.sum()),
}
top = sub[sub.grp == "PARA"].groupby("region")["victims"].sum().sort_values(ascending=False)
out["share_top10_regions_para_1997_2002"] = float(top.head(10).sum() / top.sum())
pd.Series(out).to_csv(f"{derdir}/stats_for_slides.csv")
print(pd.Series(out)); print(pd.DataFrame(rows).round(2).to_string()); print(dose.round(0).to_string())
