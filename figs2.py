import os as _o, sys as _s
_o.chdir(_o.path.dirname(_o.path.dirname(_o.path.abspath(__file__)))); _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import pandas as pd, numpy as np, json, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":9})
S=pd.read_csv("results/obligation_scores_long.csv",dtype={"provision":str}); S["provision"]=S.provision.replace({"1005.60":"1005.6"})
MOD=["ChatGPT 6","Claude Sonnet 5.5","Google Gemini (Hydrogen)"]; LAB={"ChatGPT 6":"GPT-6","Claude Sonnet 5.5":"Claude\nSonnet 5.5","Google Gemini (Hydrogen)":"Gemini 4\nHydrogen"}
C1c,C2c="#9DB4CC","#2F5D8A"
# Fig1
fig,ax=plt.subplots(figsize=(7.2,2.7)); ax.axis("off")
boxes=[("Regulatory\ntext\n12 CFR 1005.6,\n1005.11, 229.10",0.0),("Obligation\ninventory\n(n = 56),\ncoding, SCS",0.205),
       ("72 LLM specs\n3 models x\n2 prompts x\n4 runs",0.41),("Deterministic\naudit\n(4,032 scores)\nF / P / M / D",0.615),("Metrics,\ntests and\nrobustness",0.82)]
for t,x in boxes:
    ax.add_patch(FancyBboxPatch((x,0.37),0.16,0.46,boxstyle="round,pad=0.01",fc="#EEF3F8",ec="#2F5D8A",lw=1.1)); ax.text(x+0.08,0.60,t,ha="center",va="center",fontsize=8)
for i in range(4):
    x=boxes[i][1]+0.165; ax.annotate("",xy=(x+0.037,0.60),xytext=(x,0.60),arrowprops=dict(arrowstyle="->",color="#2F5D8A"))
ax.add_patch(FancyBboxPatch((0.615,0.0),0.365,0.22,boxstyle="round,pad=0.01",fc="#FFF6E5",ec="#B07A1A",lw=1))
ax.text(0.797,0.11,"External evidence: Federal Reserve\nexaminer-cited Reg E violation categories",ha="center",va="center",fontsize=7.4)
ax.add_patch(FancyBboxPatch((0.205,0.0),0.365,0.22,boxstyle="round,pad=0.01",fc="#EEF6EE",ec="#3B7A3B",lw=1))
ax.text(0.387,0.11,"Manual adjudication of a stratified\nsample (n = 36) for scorer validity",ha="center",va="center",fontsize=7.4)
ax.annotate("",xy=(0.90,0.35),xytext=(0.90,0.235),arrowprops=dict(arrowstyle="->",color="#B07A1A"))
ax.annotate("",xy=(0.69,0.35),xytext=(0.50,0.235),arrowprops=dict(arrowstyle="->",color="#3B7A3B"))
ax.set_xlim(-0.01,1); ax.set_ylim(-0.02,0.88); plt.tight_layout(); [plt.savefig(f"figures/Figure_1.{e}",dpi=600) for e in ("tiff","pdf","png")]; plt.close()
# Fig2: provision panels
run=S.groupby(["provision","model","cond","run"]).score.mean().reset_index()
fig,axs=plt.subplots(1,3,figsize=(7.2,2.6),sharey=True)
for ax,(p,t) in zip(axs,[("1005.11","Reg E 1005.11 (error resolution)"),("1005.6","Reg E 1005.6 (liability)"),("229.10","Reg CC 229.10 (availability)")]):
    x=np.arange(3)
    for k,(c,col) in enumerate([("C1",C1c),("C2",C2c)]):
        g=run[(run.provision==p)&(run.cond==c)].groupby("model").score.agg(["mean","std"]).reindex(MOD)
        ax.bar(x+(k-0.5)*0.38,g["mean"],0.38,yerr=g["std"],capsize=2,color=col,label={"C1":"C1 title-only","C2":"C2 text-grounded"}[c],error_kw=dict(lw=.7))
    ax.set_xticks(x); ax.set_xticklabels([LAB[m] for m in MOD],fontsize=7.5); ax.set_title(t,fontsize=8.5); ax.set_ylim(0,1.08)
    for s in ["top","right"]: ax.spines[s].set_visible(False)
axs[0].set_ylabel("Weighted completeness (Eq. 4)"); fig.legend(*axs[0].get_legend_handles_labels(),frameon=False,fontsize=7.5,loc="upper center",ncol=2,bbox_to_anchor=(0.5,1.0))
plt.tight_layout(rect=(0,0,1,0.92)); [plt.savefig(f"figures/Figure_2.{e}",dpi=600) for e in ("tiff","pdf","png")]; plt.close()
# Fig3 category
cat=pd.read_csv("results/by_category.csv").sort_values("C1")
fig,ax=plt.subplots(figsize=(6.4,3.0)); y=np.arange(len(cat))
ax.barh(y-0.19,cat.C1,0.38,color=C1c,label="C1 title-only"); ax.barh(y+0.19,cat.C2,0.38,color=C2c,label="C2 text-grounded")
ax.set_yticks(y); ax.set_yticklabels([f"{c} (n={int(n)})" for c,n in zip(cat.category,cat.n)]); ax.set_xlim(0,1.05)
ax.set_xlabel("Mean weighted coverage, pooled over three models and four runs"); ax.legend(frameon=False,loc="upper center",bbox_to_anchor=(0.5,1.13),ncol=2,fontsize=8)
for s in ["top","right"]: ax.spines[s].set_visible(False)
plt.tight_layout(); [plt.savefig(f"figures/Figure_3.{e}",dpi=600) for e in ("tiff","pdf","png")]; plt.close()
# Fig4 risk map: 2 x 2 quadrants (examiner citation x title-only coverage)
import sys; sys.path.insert(0,"."); from inventory import inv as _inv
ob=pd.read_csv("results/obligation_means.csv",dtype={"provision":str}).drop(columns=["notice","cited"],errors="ignore").merge(_inv[["id","notice","cited"]],on="id"); E=ob[ob.provision!="229.10"]
fig,ax=plt.subplots(figsize=(6.4,4.2)); j=np.random.default_rng(3)
Q={(0,1):("#F2F2F2","Well specified, not cited","Lower priority"),(0,0):("#EAF1F8","Specification risk","Dropped by ungrounded LLMs; rarely examined"),
   (1,1):("#FBEDEA","Execution risk","Specified well; failed in operations"),(1,0):("#F6E3F0","Dual risk","Dropped by LLMs and cited by examiners")}
for (cx,hy),(col,t1,t2) in Q.items():
    x0=-0.5+cx; y0=0 if hy==0 else 0.5; hgt=0.5 if hy==0 else 0.68
    ax.add_patch(plt.Rectangle((x0,y0),1,hgt,color=col,zorder=0))
    n=int(((E.cited==cx)&((E.C1>=0.5)==bool(hy))).sum())
    ty=1.165 if hy else 0.493
    ax.text(x0+0.5,ty,f"{t1} (n = {n})",ha="center",va="top",fontsize=8,weight="bold",color="#333333")
    ax.text(x0+0.5,ty-0.04,t2,ha="center",va="top",fontsize=6.8,color="#555555")
for cited in (0,1):
    for nt,mk in [(0,"o"),(1,"^")]:
        x=E[(E.cited==cited)&(E.notice==nt)]
        ax.scatter(cited+j.uniform(-.36,.36,len(x)),np.clip(x.C1,0.01,0.37 if False else 1),c="#B5442C" if cited else C2c,marker=mk,s=38,edgecolor="white",lw=.4,zorder=3)
ax.axvline(0.5,color="#555555",lw=1); ax.axhline(0.5,color="#555555",lw=1,ls="--")
ax.set_xticks([0,1]); ax.set_xticklabels([f"Not examiner-cited (n = {int((E.cited==0).sum())})",f"Examiner-cited (n = {int((E.cited==1).sum())})"])
ax.set_xlim(-0.5,1.5); ax.set_ylim(0,1.18); ax.set_yticks([0,0.2,0.4,0.6,0.8,1.0]); ax.set_ylabel("Mean C1 coverage (3 models x 4 runs)")
from matplotlib.lines import Line2D
ax.legend(handles=[Line2D([],[],marker="^",ls="",color="grey",label="Consumer-notice duty"),Line2D([],[],marker="o",ls="",color="grey",label="Other obligation"),Line2D([],[],ls="--",color="#555555",label="Coverage threshold 0.5")],frameon=False,fontsize=7.5,loc="upper center",bbox_to_anchor=(0.5,1.09),ncol=3)
for s_ in ["top","right"]: ax.spines[s_].set_visible(False)
plt.tight_layout(); [plt.savefig(f"figures/Figure_4.{e}",dpi=600) for e in ("tiff","pdf","png")]; plt.close()
