import pandas as pd
INV = [
("O01","1005.11","(a)(1)","Recognise the seven covered error types","M",0,0,0,0,1,0,"Scope"),
("O02","1005.11","(a)(2)","Exclude balance inquiries, tax/record-keeping requests and duplicate-copy requests","X",0,0,0,1,0,0,"Scope"),
("O03","1005.11","(b)(1)(i)","Notice timely if received <=60 days after statement on which error first appears","M",1,1,0,0,0,0,"Trigger"),
("O04","1005.11","(b)(1)","Accept oral as well as written notices of error","M",0,0,0,0,0,0,"Trigger"),
("O05","1005.11","(b)(1)(ii)-(iii)","Notice identifies name/account and reason (type, date, amount where possible)","M",2,0,0,1,0,0,"Trigger"),
("O06","1005.11","(b)(2)","Written confirmation: inform consumer and give address at oral notice; 10 business days","P",1,1,0,0,0,1,"Trigger"),
("O07","1005.11","(b)(3)","Documentation-based notice timely <=60 days after information sent","M",1,1,0,1,0,0,"Trigger"),
("O08","1005.11","(c)(1)","Investigate and determine within 10 business days","M",0,1,0,0,0,0,"Timing"),
("O09","1005.11","(c)(1)","Report results within 3 business days of completion","M",0,1,0,0,0,1,"Notice"),
("O10","1005.11","(c)(1)","Correct error within 1 business day of determination","M",0,1,0,0,0,0,"Remedy"),
("O11","1005.11","(c)(2)","Up to 45 days only if provisional credit within 10 business days","P",1,2,0,0,0,0,"Timing"),
("O12","1005.11","(c)(2)(i)","Provisional credit includes applicable interest","M",1,0,0,0,0,0,"Remedy"),
("O13","1005.11","(c)(2)(i)","May withhold up to $50 for unauthorized EFT (reasonable basis; 1005.6(a) met)","X",2,0,1,1,1,0,"Exception"),
("O14","1005.11","(c)(2)(i)(A)","No provisional credit if required written confirmation not received in 10 business days","X",2,1,0,1,0,0,"Exception"),
("O15","1005.11","(c)(2)(i)(B)","No provisional credit for accounts subject to Regulation T","X",1,0,0,1,1,0,"Exception"),
("O16","1005.11","(c)(2)(ii)","Notify amount and date of provisional credit within 2 business days","M",1,1,0,0,0,1,"Notice"),
("O17","1005.11","(c)(2)(ii)","Give full use of provisionally credited funds","M",1,0,0,0,0,0,"Remedy"),
("O18","1005.11","(c)(2)(iv)","Report results incl. notice that provisional credit is final","M",1,1,0,0,0,1,"Notice"),
("O19","1005.11","(c)(3)(i)","20 business days for EFTs within 30 days of first deposit","X",1,2,0,1,0,0,"Timing"),
("O20","1005.11","(c)(3)(ii)(A)","90 days for EFTs not initiated within a state","X",1,1,0,1,0,0,"Timing"),
("O21","1005.11","(c)(3)(ii)(B)","90 days for point-of-sale debit card transactions","X",1,1,0,1,0,0,"Timing"),
("O22","1005.11","(c)(3)(ii)(C)","90 days for EFTs within 30 days of first deposit","X",1,2,0,1,0,0,"Timing"),
("O23","1005.11","(c)(4)","Own-records review suffices for third-party transfers without agreement","P",2,0,0,1,1,0,"Scope"),
("O24","1005.11","(d)(1)","Written explanation of findings (no error / different error)","M",1,0,0,0,0,1,"Notice"),
("O25","1005.11","(d)(1)","Note right to request documents; provide copies promptly","M",1,0,0,0,0,1,"Notice"),
("O26","1005.11","(d)(2)(i)","Notify date and amount of debit of provisional credit","M",1,0,0,0,0,1,"Notice"),
("O27","1005.11","(d)(2)(ii)","Notify 5-business-day honouring of items without overdraft fee","M",1,1,0,0,0,1,"Notice"),
("O28","1005.11","(e)","No further duty on reassertion, except after (a)(1)(vii) information","X",1,0,0,1,1,0,"Scope"),
("L01","1005.6","(a)","Liability only if 1005.7(b)(1)-(3) disclosures given","M",1,0,0,0,1,0,"Liability"),
("L02","1005.6","(a)","Access device must be an accepted access device","M",1,0,0,0,0,0,"Liability"),
("L03","1005.6","(a)","Institution provided means to identify the consumer","M",1,0,0,0,0,0,"Liability"),
("L04","1005.6","(b)(1)","Notice within 2 business days: lesser of $50 or prior transfers","M",1,1,1,0,0,0,"Liability"),
("L05","1005.6","(b)(2)","Later notice: lesser of $500 or ($50 tier + later preventable transfers)","M",1,1,2,0,0,0,"Liability"),
("L06","1005.6","(b)(2)(ii)","Institution must establish later transfers were preventable","M",1,1,0,0,0,0,"Liability"),
("L07","1005.6","(b)(3)","60-day statement rule: only later preventable transfers","M",2,1,0,0,0,0,"Liability"),
("L08","1005.6","(b)(3)","Access-device tiers also apply under the statement rule","M",1,0,0,0,1,0,"Liability"),
("L09","1005.6","(b)(4)","Extend time limits for extenuating circumstances","M",1,0,0,1,0,0,"Exception"),
("L10","1005.6","(b)(5)(i)","Notice given when reasonable steps taken","M",1,0,0,0,0,0,"Trigger"),
("L11","1005.6","(b)(5)(ii)","Notice in person, by telephone or in writing","M",0,0,0,0,0,0,"Trigger"),
("L12","1005.6","(b)(5)(iii)","Written notice effective when mailed or sent","M",1,0,0,0,0,0,"Trigger"),
("L13","1005.6","(b)(5)(iii)","Constructive notice","P",1,0,0,1,0,0,"Trigger"),
("L14","1005.6","(b)(6)","Lower state-law or agreement liability prevails","M",1,0,0,1,1,0,"Exception"),
("C01","229.10","(a)(1)","Cash in person: next business day","M",1,1,0,0,0,0,"Availability"),
("C02","229.10","(a)(2)","Cash not in person: second business day","M",1,1,0,0,0,0,"Availability"),
("C03","229.10","(b)(1)","Electronic payments: next business day after receipt","M",1,1,0,0,0,0,"Availability"),
("C04","229.10","(b)(2)","Receipt = finally collected funds plus account/amount information","M",2,0,0,0,0,0,"Scope"),
("C05","229.10","(c)(1)(i)","US Treasury checks to payee account: next business day","M",1,1,0,0,0,0,"Availability"),
("C06","229.10","(c)(1)(ii)","USPS money orders, in person: next business day","M",2,1,0,0,0,0,"Availability"),
("C07","229.10","(c)(1)(iii)","Federal Reserve Bank / FHLB checks, in person: next business day","M",2,1,0,0,0,0,"Availability"),
("C08","229.10","(c)(1)(iv)","State/local government checks (same state, in person, slip): next business day","M",4,1,0,0,1,0,"Availability"),
("C09","229.10","(c)(1)(v)","Cashier's, certified, teller's checks (in person, slip): next business day","M",3,1,0,0,1,0,"Availability"),
("C10","229.10","(c)(1)(vi)","On-us checks, same state or check-processing region: next business day","M",2,1,0,0,0,0,"Availability"),
("C11","229.10","(c)(1)(vii)","Lesser of $275 or aggregate other-check deposits: next business day","M",1,1,1,0,0,0,"Availability"),
("C12","229.10","(c)(2)","Qualifying checks not in person: second business day","X",2,1,0,1,1,0,"Availability"),
("C13","229.10","(c)(3)(i)","Bank may require special deposit slip","P",1,0,0,0,0,0,"Scope"),
("C14","229.10","(c)(3)(ii)","If required, provide slip or inform how; reasonably available","M",1,0,0,0,0,1,"Notice"),
]
cols = ["id","provision","paragraph","obligation","modality","n_cond","n_time","n_money","exc","xref","notice","category"]
inv = pd.DataFrame(INV, columns=cols)
inv['SCS']=inv.n_cond+inv.n_time+inv.n_money+inv.exc+inv.xref
CITED={'O04','O08','O09','O10','O11','O12','O16','O17','O18','O24','O25','O26','O27','L06','L07'}
inv['cited']=inv.id.isin(CITED).astype(int)
# ---- apply reconciled codes agreed by the two coders (reconciled_codes.csv); unresolved items keep coder A's code
import os as _os
_rc = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "data", "coding", "reconciled_codes.csv")
if _os.path.exists(_rc):
    for _r in pd.read_csv(_rc).itertuples():
        _v = _r.agreed_code
        if _r.attribute in ("modality",): inv.loc[inv.id == _r.ID, "modality"] = str(_v).strip()
        else: inv.loc[inv.id == _r.ID, _r.attribute] = int(float(_v))
    inv["SCS"] = inv.n_cond + inv.n_time + inv.n_money + inv.exc + inv.xref
    inv["cited"] = inv["cited"].astype(int)
