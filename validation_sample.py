import os as _o, sys as _s
_o.chdir(_o.path.dirname(_o.path.dirname(_o.path.abspath(__file__)))); _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import pandas as pd, re, glob
from scoring import blocks, SIG
from inventory import inv
S=pd.read_csv("results/obligation_scores_long.csv"); S=S[S.run>1]
S["grp"]=S.label.map({"F":"F","P":"PD","D":"PD","M":"M"})
samp=S.groupby("grp",group_keys=False).apply(lambda g:g.sample(12,random_state=20261120)).reset_index(drop=True)
samp.to_csv("results/validation_sample.csv",index=False)
ob=inv.set_index("id").obligation
for i,r in samp.iterrows():
    bl=blocks(open("data/raw_outputs/"+r.file,encoding="utf-8").read())
    core=SIG[r.id][0]
    hits=sorted(bl,key=lambda b:-sum(bool(re.search(p,b,re.I)) for p in core))[:2]
    print(f"\n#{i} {r.id} [{ob[r.id]}] {r.model[:6]} {r.cond} r{r.run}")
    for b in hits: print("   >",re.sub(r"\s+"," ",b)[:420])
