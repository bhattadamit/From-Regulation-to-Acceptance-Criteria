"""Multi-model analysis (3 models x 2 conditions x 3 provisions x 4 runs = 72 specifications; 4,032 obligation scores)."""
import os as _o, sys as _s
_o.chdir(_o.path.dirname(_o.path.dirname(_o.path.abspath(__file__)))); _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import json, numpy as np, pandas as pd
from scipy import stats
from inventory import inv

S = pd.read_csv("results/obligation_scores_long.csv", dtype={"provision": str})
M = pd.read_csv("results/file_meta.csv", dtype={"provision": str})
S["provision"] = S["provision"].replace({"1005.6": "1005.6", "1005.60": "1005.6"}); M["provision"] = M["provision"].replace({"1005.60": "1005.6"})
I = inv.set_index("id")
S = S.merge(inv[["id", "SCS", "exc", "modality", "notice", "category", "cited"]], on="id")
S["w"] = 1 + S.SCS
S["exception"] = ((S.exc == 1) | (S.modality == "X")).astype(int)
MODELS = ["ChatGPT 6", "Claude Sonnet 5.5", "Google Gemini (Hydrogen)"]
R = {}

def metr(d):
    lab = d.label; s = d.score
    pres = lab.isin(["F", "P"]).sum()
    return {"OR": pres / len(d), "WC": s.mean(), "RWC": (d.w * s).sum() / d.w.sum(),
            "EC": s[d.exception == 1].mean(), "NC": s[d.notice == 1].mean() if (d.notice == 1).any() else np.nan,
            "DR": (lab == "D").sum() / max(1, pres + (lab == "D").sum()),
            "F": (lab == "F").mean(), "P": (lab == "P").mean(), "M": (lab == "M").mean(), "D": (lab == "D").mean()}

# run-level (56 obligations per model x cond x run)
run = pd.DataFrame([dict(model=m, cond=c, run=r, **metr(g)) for (m, c, r), g in S.groupby(["model", "cond", "run"])])
run.to_csv("results/run_level_metrics.csv", index=False)
agg = run.groupby(["model", "cond"]).agg(["mean", "std"]).drop(columns="run", level=0)
R["model_cond"] = {f"{m}|{c}": {k: [float(agg.loc[(m, c), (k, "mean")]), float(agg.loc[(m, c), (k, "std")])] for k in ["OR", "WC", "RWC", "EC", "NC", "DR", "F", "P", "M", "D"]} for m, c in agg.index}
pooled = run.groupby("cond")[["OR", "WC", "RWC", "EC", "NC", "DR", "M", "D"]].agg(["mean", "std"])
R["pooled"] = {c: {k: [float(pooled.loc[c, (k, "mean")]), float(pooled.loc[c, (k, "std")])] for k in ["OR", "WC", "RWC", "EC", "NC", "DR", "M", "D"]} for c in ["C1", "C2"]}

# provision x model x cond
pv = S.groupby(["provision", "model", "cond"]).score.mean().unstack("cond")
R["prov_model"] = {f"{p}|{m}": [float(pv.loc[(p, m), "C1"]), float(pv.loc[(p, m), "C2"])] for p, m in pv.index}
pp = S.groupby(["provision", "cond"]).score.mean().unstack()
R["prov"] = {p: [float(pp.loc[p, "C1"]), float(pp.loc[p, "C2"])] for p in pp.index}

# category
cat = S.groupby(["category", "cond"]).score.mean().unstack().reset_index()
cat["n"] = cat.category.map(inv.category.value_counts()); cat["SCS"] = cat.category.map(inv.groupby("category").SCS.mean())
cat.to_csv("results/by_category.csv", index=False)
catm = S.groupby(["category", "model", "cond"]).score.mean().unstack(["model", "cond"]); catm.to_csv("results/by_category_model.csv")

# obligation-level means
ob = S.groupby(["id", "cond"]).score.mean().unstack(); ob = ob.join(I[["SCS", "exc", "modality", "notice", "cited", "category", "obligation", "provision"]])
ob["exception"] = ((ob.exc == 1) | (ob.modality == "X")).astype(int)
obm = S.groupby(["id", "model", "cond"]).score.mean().unstack("cond").reset_index()
ob.to_csv("results/obligation_means.csv")

# H1 grounding
T = {}
for m in MODELS:
    x = obm[obm.model == m]; w = stats.wilcoxon(x.C2, x.C1)
    T[f"wilcoxon_{m}"] = [float(w.statistic), float(w.pvalue), float((x.C2 - x.C1).mean())]
w = stats.wilcoxon(obm.C2, obm.C1); T["wilcoxon_pooled"] = [float(w.statistic), float(w.pvalue), float((obm.C2 - obm.C1).mean())]
rng = np.random.default_rng(20261120); d = (obm.C2 - obm.C1).values
boot = [rng.choice(d, len(d)).mean() for _ in range(10000)]; T["gain_CI"] = [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))]
T["n_obl_worse_C2"] = int((ob.C2 < ob.C1 - 1e-9).sum()); T["n_obl_better_C2"] = int((ob.C2 > ob.C1 + 1e-9).sum())

# OLS on file-level WC with HC3 SEs
F = S.groupby(["file", "model", "cond", "provision", "run"]).score.mean().reset_index().rename(columns={"score": "WC"})
X = pd.DataFrame({"const": 1.0, "C2": (F.cond == "C2").astype(float)})
for m in MODELS[1:]: X[f"m_{m[:6]}"] = (F.model == m).astype(float)
for p in ["1005.6", "229.10"]: X[f"p_{p}"] = (F.provision == p).astype(float)
for m in MODELS[1:]: X[f"C2x{m[:6]}"] = X.C2 * (F.model == m)
y = F.WC.values; Xv = X.values; XtXi = np.linalg.inv(Xv.T @ Xv); b = XtXi @ Xv.T @ y; e = y - Xv @ b
h = np.einsum("ij,jk,ik->i", Xv, XtXi, Xv); meat = Xv.T @ (Xv * (e ** 2 / (1 - h) ** 2)[:, None]); V = XtXi @ meat @ XtXi
se = np.sqrt(np.diag(V)); tval = b / se; dfree = len(y) - Xv.shape[1]; pval = 2 * stats.t.sf(abs(tval), dfree)
r2 = 1 - (e ** 2).sum() / ((y - y.mean()) ** 2).sum()
T["ols"] = {c: [float(b[i]), float(se[i]), float(pval[i])] for i, c in enumerate(X.columns)}; T["ols_r2"] = float(r2); T["ols_n"] = len(y)
F.to_csv("results/file_level_wc.csv", index=False)

# H2 complexity, H3 exceptions
for c in ["C1", "C2"]:
    r, p = stats.spearmanr(ob.SCS, ob[c]); T[f"spearman_{c}"] = [float(r), float(p)]
    a, bb = ob[ob.exception == 1][c], ob[ob.exception == 0][c]; u = stats.mannwhitneyu(a, bb)
    T[f"mw_exc_{c}"] = [float(u.statistic), float(u.pvalue), float(a.mean()), float(bb.mean())]
    a, bb = ob[ob.notice == 1][c], ob[ob.notice == 0][c]; u = stats.mannwhitneyu(a, bb)
    T[f"mw_notice_{c}"] = [float(u.statistic), float(u.pvalue), float(a.mean()), float(bb.mean())]
for m in MODELS:
    x = obm[obm.model == m].merge(inv[["id", "SCS"]], on="id")
    for c in ["C1", "C2"]:
        r, p = stats.spearmanr(x.SCS, x[c]); T[f"spearman_{c}_{m}"] = [float(r), float(p)]
# low/high SCS
med = ob.SCS.median(); T["SCS_median"] = float(med)
for c in ["C1", "C2"]:
    T[f"lowSCS_{c}"] = float(ob[ob.SCS <= med][c].mean()); T[f"highSCS_{c}"] = float(ob[ob.SCS > med][c].mean())

# H4 examiner (Reg E, structural + coverage)
E = ob[ob.provision != "229.10"]
u = stats.mannwhitneyu(E[E.cited == 1].SCS, E[E.cited == 0].SCS)
ctn = pd.crosstab(E.notice, E.cited).values; fn = stats.fisher_exact(ctn)
ctx = pd.crosstab(E.exception, E.cited).values; fx = stats.fisher_exact(ctx)
X4 = {"n": len(E), "n_cited": int(E.cited.sum()), "SCS_cited": float(E[E.cited == 1].SCS.mean()), "SCS_uncited": float(E[E.cited == 0].SCS.mean()),
      "mw_SCS": [float(u.statistic), float(u.pvalue)], "notice_ct": ctn.tolist(), "fisher_notice": [float(fn[0]), float(fn[1])],
      "exc_ct": ctx.tolist(), "fisher_exc": [float(fx[0]), float(fx[1])],
      "notice_cited": int(E[(E.notice == 1)].cited.sum()), "notice_n": int((E.notice == 1).sum()),
      "exc_cited": int(E[E.exception == 1].cited.sum()), "exc_n": int((E.exception == 1).sum())}
for c in ["C1", "C2"]:
    a, bb = E[E.cited == 1][c], E[E.cited == 0][c]; uu = stats.mannwhitneyu(a, bb)
    X4[f"cov_{c}"] = [float(a.mean()), float(bb.mean()), float(uu.statistic), float(uu.pvalue)]
R["examiner"] = X4

# run-to-run stability: Fleiss kappa over 4 runs per model x cond (categories F,P,M,D)
def fleiss(mat):
    n = mat.sum(1)[0]; N = len(mat); p = mat.sum(0) / (N * n)
    Pi = ((mat ** 2).sum(1) - n) / (n * (n - 1)); Pb = Pi.mean(); Pe = (p ** 2).sum()
    return (Pb - Pe) / (1 - Pe) if Pe < 1 else 1.0
stab = {}
for (m, c), g in S.groupby(["model", "cond"]):
    piv = g.pivot_table(index="id", columns="run", values="label", aggfunc="first")
    mat = np.array([[(row == k).sum() for k in "FPMD"] for row in piv.values])
    stab[f"{m}|{c}"] = {"fleiss": float(fleiss(mat)), "identical": float((piv.nunique(1) == 1).mean())}
R["stability"] = stab

# failure modes
fm = S.groupby(["model", "cond"]).label.value_counts().unstack(fill_value=0)
R["labels"] = {f"{m}|{c}": fm.loc[(m, c)].to_dict() for m, c in fm.index}
R["distortions"] = S[S.label == "D"].groupby(["id", "model", "cond"]).size().reset_index().to_dict(orient="records")

# residual gaps in C2 and biggest C1 gaps (pooled across models)
R["c2_gaps"] = ob.sort_values("C2").head(8)[["C1", "C2", "SCS", "category"]].reset_index().to_dict(orient="records")
R["c1_gaps"] = ob.sort_values("C1").head(10)[["C1", "C2", "SCS", "category"]].reset_index().to_dict(orient="records")

# verbosity
FM = F.merge(M[["file", "words", "scenarios"]], on="file")
for c in ["C1", "C2"]:
    x = FM[FM.cond == c]; r, p = stats.spearmanr(x.words, x.WC); T[f"words_WC_{c}"] = [float(r), float(p)]
R["length"] = FM.groupby(["model", "cond"])[["words", "scenarios"]].mean().round(0).reset_index().to_dict(orient="records")

# robustness
rb = {}
for name, pw in [("strict", 0), ("base", .5), ("lenient", 1)]:
    sc = S.label.map({"F": 1, "P": pw, "M": 0, "D": 0})
    rb[name] = [float(sc[S.cond == "C1"].mean()), float(sc[S.cond == "C2"].mean())]
rb["holdout_run1"] = [float(S[(S.run == 1) & (S.cond == "C1")].score.mean()), float(S[(S.run == 1) & (S.cond == "C2")].score.mean())]
rb["holdout_runs2_4"] = [float(S[(S.run > 1) & (S.cond == "C1")].score.mean()), float(S[(S.run > 1) & (S.cond == "C2")].score.mean())]
for m in MODELS:
    x = S[S.model != m]; rb[f"drop_{m}"] = [float(x[x.cond == "C1"].score.mean()), float(x[x.cond == "C2"].score.mean())]
for p in ["1005.11", "1005.6", "229.10"]:
    x = S[S.provision != p]; rb[f"drop_{p}"] = [float(x[x.cond == "C1"].score.mean()), float(x[x.cond == "C2"].score.mean())]
rb["validation_corrected"] = None
R["robust"] = rb
R["tests"] = T
R["validation"] = json.load(open("results/validation.json"))
json.dump(R, open("results/summary2.json", "w"), indent=1, default=float)
print(json.dumps({k: R[k] for k in ["pooled", "tests", "examiner", "stability", "labels", "robust"]}, indent=1, default=float))
print(pv.round(3)); print(cat.round(3)); print(ob.sort_values("C2").head(8)[["C1", "C2", "SCS"]]); print(ob.sort_values("C1").head(10)[["C1", "C2", "SCS"]])
print(R["distortions"]); print(R["length"])
