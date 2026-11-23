"""Sensitivity: notation-tolerant signatures (D+1, Next BD) -- validation-informed, not used for primary results."""
import os as _o, sys as _s
_o.chdir(_o.path.dirname(_o.path.dirname(_o.path.abspath(__file__)))); _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import re, glob, os, json, pandas as pd
from scipy import stats
from inventory import inv
src=open("code/scoring.py").read()
src=src.replace('day after (the )?(banking )?day of (deposit|receipt))"','day after (the )?(banking )?day of (deposit|receipt)|\\bd ?\\+ ?1\\b|next bd\\b)"').replace('SD = r"(second business day','SD = r"(\\bd ?\\+ ?2\\b|second business day')
open("code/scoring_v21_sensitivity.py","w").write(src)
import scoring_v21_sensitivity as s21
PROV={"1005_11":"1005.11","1005_6":"1005.6","229_10":"229.10"}; rows=[]
for f in glob.glob("data/raw_outputs/*.txt"):
    n=os.path.basename(f); m=re.match(r"(.+?)_(\d)_(C[12])_REG (?:E|CC)_12_CFR_(\d+_\d+)",n)
    bl=s21.blocks(open(f,encoding="utf-8").read())
    for r in inv[inv.provision==PROV[m.group(4)]].itertuples():
        rows.append(dict(id=r.id,cond=m.group(3),prov=PROV[m.group(4)],score=s21.score(r.id,bl)[1]))
d=pd.DataFrame(rows)
out={"C1":d[d.cond=="C1"].score.mean(),"C2":d[d.cond=="C2"].score.mean(),"CC_C1":d[(d.prov=="229.10")&(d.cond=="C1")].score.mean(),"CC_C2":d[(d.prov=="229.10")&(d.cond=="C2")].score.mean()}
ob=d.groupby(["id","cond"]).score.mean().unstack().join(inv.set_index("id")[["SCS","cited","provision"]]); E=ob[ob.provision!="229.10"]
t={"rho_C1":list(map(float,stats.spearmanr(ob.SCS,ob.C1))),"rho_C2":list(map(float,stats.spearmanr(ob.SCS,ob.C2))),
   "cited_C1":[float(E[E.cited==1].C1.mean()),float(E[E.cited==0].C1.mean()),float(stats.mannwhitneyu(E[E.cited==1].C1,E[E.cited==0].C1).pvalue)]}
R=json.load(open("results/summary2.json")); R["robust"]["notation_v21"]={k:float(v) for k,v in out.items()}; R["robust"]["notation_v21_tests"]=t
json.dump(R,open("results/summary2.json","w"),indent=1); print(out,t)
