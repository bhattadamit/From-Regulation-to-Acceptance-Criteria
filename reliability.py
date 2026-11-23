import os as _o, sys as _s
_o.chdir(_o.path.dirname(_o.path.dirname(_o.path.abspath(__file__)))); _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import pandas as pd, numpy as np, json
from scipy import stats
from inventory_original import inv
X=pd.read_excel('data/coding/Second_Coder_Workbook_CoderB.xlsx',sheet_name=None)
b=X['3_Code_Obligations'].iloc[:,[0,4,5,6,7,8,9,10]]; b.columns=['id','modality','n_cond','n_time','n_money','exc','xref','notice']
e=X['4_Examiner_Mapping'].iloc[:,[0,4]]; e.columns=['id','cited']; e['cited']=(e.cited.str.strip().str.upper()=='Y').astype(int)
b=b.merge(e,on='id',how='left'); b['SCS']=b.n_cond+b.n_time+b.n_money+b.exc+b.xref
a=inv.set_index('id'); b=b.set_index('id').loc[a.index]
def kappa(x,y):
    cats=sorted(set(x)|set(y)); ct=pd.crosstab(pd.Categorical(x,cats),pd.Categorical(y,cats)).values; n=ct.sum()
    po=np.trace(ct)/n; pe=(ct.sum(1)*ct.sum(0)).sum()/n**2; return po,(po-pe)/(1-pe) if pe<1 else 1.0
def wkappa(x,y):  # quadratic weighted kappa for counts
    cats=sorted(set(x)|set(y)); k=len(cats); idx={c:i for i,c in enumerate(cats)}
    O=np.zeros((k,k)); [O.__setitem__((idx[i],idx[j]),O[idx[i],idx[j]]+1) for i,j in zip(x,y)]
    W=np.array([[(i-j)**2 for j in range(k)] for i in range(k)])/((k-1)**2 if k>1 else 1)
    Ex=np.outer(O.sum(1),O.sum(0))/O.sum(); return 1-(W*O).sum()/(W*Ex).sum()
def icc(x,y):  # ICC(2,1) absolute agreement
    M=np.c_[x,y].astype(float); n,k=M.shape; gm=M.mean()
    msr=k*((M.mean(1)-gm)**2).sum()/(n-1); msc=n*((M.mean(0)-gm)**2).sum()/(k-1)
    mse=((M-M.mean(1,keepdims=True)-M.mean(0,keepdims=True)+gm)**2).sum()/((n-1)*(k-1))
    return (msr-mse)/(msr+(k-1)*mse+k*(msc-mse)/n)
R={}
for c in ['modality','exc','xref','notice']:
    po,k=kappa(a[c].values,b[c].values); R[c]={'agree':po,'kappa':k}
for c in ['n_cond','n_time','n_money','SCS']:
    R[c]={'agree':float((a[c].values==b[c].values).mean()),'wkappa':float(wkappa(a[c].values,b[c].values)),'icc':float(icc(a[c].values,b[c].values)),
          'meanA':float(a[c].mean()),'meanB':float(b[c].mean())}
R['SCS']['spearman']=float(stats.spearmanr(a.SCS,b.SCS)[0])
E=a.index[a.provision!='229.10']; po,k=kappa(a.loc[E,'cited'].values,b.loc[E,'cited'].values); R['cited']={'agree':po,'kappa':k,'nA':int(a.loc[E,'cited'].sum()),'nB':int(b.loc[E,'cited'].sum())}
# robustness with coder B codes
S=pd.read_csv('results/obligation_scores_long.csv'); ob=S.groupby(['id','cond']).score.mean().unstack()
B=b.join(ob); B['exception']=((B.exc==1)|(B.modality=='X')).astype(int); B['provision']=a.provision
rb={}
for c in ['C1','C2']:
    r,p=stats.spearmanr(B.SCS,B[c]); rb[f'rho_{c}']=[float(r),float(p)]
    x,y=B[B.exception==1][c],B[B.exception==0][c]; rb[f'exc_{c}']=[float(x.mean()),float(y.mean()),float(stats.mannwhitneyu(x,y).pvalue)]
    x,y=B[B.notice==1][c],B[B.notice==0][c]; rb[f'notice_{c}']=[float(x.mean()),float(y.mean()),float(stats.mannwhitneyu(x,y).pvalue)]
BE=B.loc[E]
rb['SCS_cited']=[float(BE[BE.cited==1].SCS.mean()),float(BE[BE.cited==0].SCS.mean()),float(stats.mannwhitneyu(BE[BE.cited==1].SCS,BE[BE.cited==0].SCS).pvalue)]
ct=pd.crosstab(BE.notice,BE.cited).values; rb['fisher_notice']=list(map(float,stats.fisher_exact(ct))); rb['notice_ct']=ct.tolist()
ct=pd.crosstab(BE.exception,BE.cited).values; rb['fisher_exc']=list(map(float,stats.fisher_exact(ct))); rb['exc_ct']=ct.tolist()
for c in ['C1','C2']: rb[f'cov_cited_{c}']=[float(BE[BE.cited==1][c].mean()),float(BE[BE.cited==0][c].mean()),float(stats.mannwhitneyu(BE[BE.cited==1][c],BE[BE.cited==0][c]).pvalue)]
w=1+B.SCS; S2=S.merge(B[['SCS']].reset_index(),on='id')
rb['RWC_B']={c:float(((1+S2[S2.cond==c].SCS)*S2[S2.cond==c].score).sum()/(1+S2[S2.cond==c].SCS).sum()) for c in ['C1','C2']}
R['robust_B']=rb
# disagreement table
rows=[]
for i in a.index:
    for c in ['modality','n_cond','n_time','n_money','exc','xref','notice']+(['cited'] if i in E else []):
        if str(a.loc[i,c]).replace('.0','')!=str(b.loc[i,c]).replace('.0',''): rows.append({'id':i,'obligation':a.loc[i,'obligation'],'attribute':c,'coder_A':a.loc[i,c],'coder_B':b.loc[i,c],'coder_B_note':X['3_Code_Obligations'].set_index(X['3_Code_Obligations'].columns[0]).loc[i].iloc[-1] if c!='cited' else '', 'agreed_code':'','reason':''})
D=pd.DataFrame(rows); D.to_excel('results/disagreements_pre_reconciliation.xlsx',index=False)
R['n_disagreements']=len(D); R['by_attr']=D.attribute.value_counts().to_dict()
b.reset_index().to_csv('results/coder_B_codes.csv',index=False)
json.dump(R,open('results/reliability.json','w'),indent=1,default=float)
print(json.dumps(R,indent=1,default=float))
