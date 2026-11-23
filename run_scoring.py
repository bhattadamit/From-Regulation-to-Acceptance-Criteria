import os as _o, sys as _s
_o.chdir(_o.path.dirname(_o.path.dirname(_o.path.abspath(__file__)))); _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import os, re, glob, pandas as pd, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inventory import inv
from scoring import blocks, score
PROV = {"1005_11":"1005.11","1005_6":"1005.6","229_10":"229.10"}
rows, meta = [], []
for f in sorted(glob.glob("data/raw_outputs/*.txt")):
    n = os.path.basename(f)
    m = re.match(r"(.+?)_(\d)_(C[12])_REG (?:E|CC)_12_CFR_(\d+_\d+)", n)
    vendor_model, run, cond, rule = m.group(1), int(m.group(2)), m.group(3), PROV[m.group(4)]
    model = {"Claude_Sonnet 5.5":"Claude Sonnet 5.5","CHGPT_Chatgpt 6":"ChatGPT 6","Google_Hydrogen":"Google Gemini (Hydrogen)"}[vendor_model]
    txt = open(f, encoding="utf-8", errors="ignore").read()
    bl = blocks(txt)
    meta.append(dict(file=n, model=model, run=run, cond=cond, provision=rule, words=len(txt.split()), scenarios=len(bl)))
    for r in inv[inv.provision == rule].itertuples():
        lab, s = score(r.id, bl)
        rows.append(dict(file=n, model=model, run=run, cond=cond, provision=rule, id=r.id, label=lab, score=s))
os.makedirs("results", exist_ok=True)
S = pd.DataFrame(rows); M = pd.DataFrame(meta)
S.to_csv("results/obligation_scores_long.csv", index=False); M.to_csv("results/file_meta.csv", index=False)
print(M.groupby(["model","cond"])[["words","scenarios"]].agg(["mean","min"]).round(0))
print(S.groupby(["model","cond"]).score.mean().unstack().round(3))
