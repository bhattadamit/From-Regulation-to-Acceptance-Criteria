"""Deterministic obligation-coverage scoring for LLM-generated Gherkin specifications (v2, multi-model).
Signatures were calibrated on run-1 outputs only and frozen before runs 2-4 were scored."""
import re

WORDNUM = {"one":1,"two":2,"three":3,"four":4,"five":5,"ten":10,"twenty":20,"thirty":30,
           "forty-five":45,"forty five":45,"sixty":60,"ninety":90}

def normalize(t):
    t = t.replace("\\", "").replace("**", "").replace("__", "").replace("`", "").replace("§", "")
    t = re.sub(r"[‐-―]", "-", t)
    t = t.replace("’", "'")
    for w, n in sorted(WORDNUM.items(), key=lambda x: -len(x[0])):
        t = re.sub(rf"\b{w}\s*\(\s*{n}\s*\)", str(n), t, flags=re.I)          # "ten (10)" -> 10
        t = re.sub(rf"\b{w}(?=[\s-]+(business|calendar|banking)?[\s-]*days?\b)", str(n), t, flags=re.I)
    t = re.sub(r"\b(\d+)\s*-\s*(?=(business|calendar|banking|day))", r"\1 ", t, flags=re.I)
    t = re.sub(r"\b(business|calendar|banking)\s*-\s*day", r"\1 day", t, flags=re.I)
    return t

START = re.compile(r"^\s*[#>*\-|\s]*(scenario outline|scenario template|scenario|example)\b[^:\n]{0,60}:", re.I)
END = re.compile(r"^\s*(feature\s*:|rule\s*:|#{1,6}\s|```|-{3,}\s*$|={3,}\s*$|\*{3,}\s*$)", re.I)

def blocks(text):
    """Return Gherkin scenario blocks (scenario line through Examples tables, ending at next scenario/heading/fence)."""
    out, cur = [], None
    for line in normalize(text).splitlines():
        if START.match(line):
            if cur: out.append("\n".join(cur))
            cur = [line]
        elif cur is not None:
            if END.match(line):
                out.append("\n".join(cur)); cur = None
            else:
                cur.append(line)
    if cur: out.append("\n".join(cur))
    return out

BD = lambda n: rf"\b{n} business days?\b"
CD = lambda n: rf"\b{n} (calendar )?days?\b"
ND = r"(next business day|next-business-day|\bt ?\+ ?1\b|(first|1st) business day|(?<!second )(?<!2nd )(?<!\d )\bbusiness day (after|following)|\b1 business day after|day after (the )?(banking )?day of (deposit|receipt)|\bd ?\+ ?1\b|next bd\b)"
SD = r"(\bd ?\+ ?2\b|second business day|2nd business day|\bt ?\+ ?2\b|\b2 business days? after)"
INPERSON = r"(in person|in-person|teller|employee|branch counter|at a branch)"

# id: (core [all must match], qualifiers [all must match for full credit], distortion pattern or None)
SIG = {
"O01":([r"unauthori[sz]ed", r"(incorrect|wrong|erroneous) (amount|electronic|eft|transfer)|incorrect eft|incorrect transfer", r"omit|omission|missing from|not (shown|reflected|included|appear)"],
       [r"computational|bookkeeping|math", r"terminal|atm", r"documentation|clarification"], None),
"O02":([r"balance", r"inquir|not (an |a )?(reg e )?error|exclu|not (treated|considered|classified)"], [r"tax|record-?keeping", r"duplicate"], None),
"O03":([CD(60), r"statement"], [r"first appear|on which the (alleged )?error|reflect|show|contain|in which"], None),
"O04":([r"\boral|orally|telephone|phone|verbal|call", r"notice|notif|dispute|claim|error"],
       [r"without (waiting|requiring)|start|begin|immediately|oral (or|and) written|regardless|not (wait|delay)|clock|timer|received"], None),
"O05":([r"name", r"account (number|identifier|no\b)"], [r"why|reason|type|date|amount"], None),
"O06":([r"written confirmation|confirm(ation)? in writing|written follow|confirm the (oral )?(notice|error) in writing", BD(10)], [r"address|inform|tell|notif|advis"], None),
"O07":([CD(60), r"clarification|requested (information|documentation|documents?)|information (the consumer )?requested|\(a\)\(1\)\(vii\)"],
       [r"(institution|bank|fi\b)[a-z ]{0,20}(sent|send|provid|transmit|mail)|after (sending|providing|transmit)|(sent|provided|transmitted|mailed) the (requested )?(information|documentation)"], None),
"O08":([BD(10), r"investigat|determin|resol"], [r"receipt|receiv|notice"], None),
"O09":([BD(3), r"result|report|notif|inform|outcome|determination|letter"], [], None),
"O10":([BD(1), r"correct"], [], None),
"O11":([CD(45), r"investigat|extend|period|deadline"], [r"provisional", BD(10)], None),
"O12":([r"provisional", r"interest"], [], None),
"O13":([r"\$50\b", r"withh|hold back|retain|less|minus|deduct|reduc|exclud", r"provisional"], [r"reasonable basis|1005\.6|unauthori"], None),
"O14":([r"written confirmation|confirm(ation)? in writing", r"provisional"],
       [r"(not|no|never|isn't|is not) (be )?(required|obligat|need|issue|post|grant|provide)|need not|exempt|waive|without (issuing|posting|provisional)|skip|suppress|not (owe|due)"], None),
"O15":([r"regulation t\b|reg t\b|margin account|securities (account|credit)"], [r"provisional"], None),
"O16":([BD(2), r"provisional"], [r"amount", r"date"], None),
"O17":([r"provisional", r"full use|use of (the )?(provisional(ly credited)? )?funds|access to (the )?funds|(funds|credit) (are |is |must be )?(fully )?available|without (restriction|hold)|not (place|put) a hold|no hold"], [], None),
"O18":([r"provisional", r"\bfinal"], [r"report|notif|inform|letter|result"], None),
"O19":([BD(20), CD(30)], [r"first deposit|new account|account (opening|was opened)|opened"], None),
"O20":([CD(90), r"not initiated within a state|outside (the )?(united states|u\.?s\.?|a state|any state)|foreign|international|cross-?border|out of state|initiated outside"], [], None),
"O21":([CD(90), r"point[- ]of[- ]sale|\bpos\b|debit card (purchase|transaction)"], [], None),
"O22":([CD(90), CD(30)], [r"first deposit|new account|account (opening|was opened)|opened"], None),
"O23":([r"own records|internal records|its records|review of (its|the institution's|the bank's|our) (own )?records|records review"], [r"third[- ]party|no agreement|without (an )?agreement|review"], None),
"O24":([r"explanation|explain", r"no error|different error|not (find|found|identify|determine|establish)[a-z]* .{0,20}error|error (was |did )?not (occur|found)|denied|deny|no-error"], [r"written|writing|letter"], None),
"O25":([r"document", r"request|right"], [r"reli|relied|used|basis|support", r"provide|copies|copy|furnish|send"], None),
"O26":([r"debit|revers|reclaim|claw|recover", r"provisional"], [r"date", r"amount", r"notif|notice|inform|letter"], None),
"O27":([BD(5), r"honou?r|overdraft|pay"], [r"overdraft", r"third[- ]part|preauthori|check|draft"], None),
"O28":([r"re-?assert|same error (again|previously)|previously (resolved|investigated|determined|closed)|repeat(ed)? (claim|dispute|error|notice)|duplicate (claim|dispute)|resubmi|reopen"], [r"\(a\)\(1\)\(vii\)|documentation|clarification|except|unless"], None),
"L01":([r"1005\.7|disclosure", r"liab"], [], None),
"L02":([r"accepted access device|access device .{0,60}(accepted|activated)|not (an )?accepted|unaccepted|accepted (card|device)"], [], None),
"L03":([r"means (to|of) identif|identif(y|ication) (of )?(the )?(consumer|cardholder|user)|(pin|signature|photograph|fingerprint|biometric).{0,60}identif"], [], None),
"L04":([BD(2), r"\$50\b"], [r"lesser|less than|\bmin\b|min\(|not (to )?exceed|whichever|up to|cap|maximum"], None),
"L05":([r"\$500\b"], [r"lesser|\bmin\b|min\(|whichever|not (to )?exceed|cap|maximum|up to", r"after .{0,30}2 business days?|beyond .{0,20}2 business|would not have occurred|prevent|later|late notice|untimely|not (within|timely)"], None),
"L06":([r"would not have occurred|prevent|could have been (stopped|avoided)|but for|had .{0,40}(notified|notice).{0,40}(timely|within)", BD(2)], [r"establish|prove|demonstrat|show|burden|evidence|document"], None),
"L07":([CD(60), r"statement", r"liab"], [r"would not have occurred|prevent|but for|could have been|had .{0,50}(notif|notice|report)"], r"unlimited|full amount|all (subsequent|later|future) transfers|100%"),
"L08":([CD(60), r"access device|card", r"\$50\b|\$500\b|\(b\)\(1\)|\(b\)\(2\)|2 business days?"], [], None),
"L09":([r"extenuating|extended travel|hospitali[sz]|extend(ed|s|ing)? .{0,40}(time|deadline|period|limit|window)"], [r"reasonable"], None),
"L10":([r"reasonably necessary|reasonable steps|whether or not .{0,60}(employee|person|staff|agent).{0,40}receiv|regardless of whether .{0,60}receiv|not actually receiv"], [], None),
"L11":([r"in person|in-person|branch", r"telephone|phone|call", r"writing|written|mail|letter"], [], None),
"L12":([r"written|writing|mail|letter", r"(when|time|date|upon|at the time|moment)\b.{0,40}(mail|sent|send|deliver|postmark|transmi)|(mail|sent|deliver|postmark|transmi)[a-z]* .{0,80}(date|effective|deemed|given|considered|counts|transmission)"], [], None),
"L13":([r"constructive|becomes aware|become aware|reasonable belief|aware of circumstances"], [], None),
"L14":([r"state law|account agreement|agreement .{0,40}(lower|less|zero|\$0)|zero[- ]liability|\$0 liability|lower liability|more favorable"], [r"lower|less|lesser|reduc|favorable|zero|\$0|not exceed"], None),
"C01":([r"\bcash", INPERSON, ND], [], None),
"C02":([r"\bcash", r"\batm|not (made )?in person|other than in person|night deposit|mail|non-?in-?person|remote", SD], [], None),
"C03":([r"electronic payment|\bach\b|wire|direct deposit|electronic (credit|transfer)", ND], [], None),
"C04":([r"finally collected|final(ly)? (settle|settlement|collect)|actually and finally|good funds|settled funds|final settlement"], [r"account (number|and amount)|information|amount to be credited|which account|identif"], None),
"C05":([r"treasury", ND], [r"payee|payable to|own account|named"], None),
"C06":([r"postal|money order|usps", ND], [INPERSON], None),
"C07":([r"federal reserve bank|federal home loan|fhlb|\bfrb\b", ND], [INPERSON], None),
"C08":([r"(state|local) government|government check|municipal|state or local", ND], [r"same state|in-state|within the (same )?state|same .{0,10}state", INPERSON, r"deposit slip|special slip|special deposit"], None),
"C09":([r"cashier|certified|teller'?s check", ND], [INPERSON, r"deposit slip|special slip|special deposit"], None),
"C10":([r"on-?us|same (bank|institution|branch)|drawn on (the|our|this|another) (branch|bank|institution)|another branch|same or another branch|drawn on (the )?(depositary|our own)", ND], [r"same state|check processing region|state or|same .{0,10}region"], None),
"C11":([r"\$275\b"], [r"aggregate|all .{0,25}accounts|combined|across|total|lesser"], None),
"C12":([r"not (deposited )?in person|other than in person|\batm|non-?in-?person|mobile|remote|mail", SD, r"cashier|certified|teller|money order|government|federal reserve|home loan|postal"], [], None),
"C13":([r"special deposit slip|special slip|deposit slip|deposit envelope|special envelope", r"requir|condition|must use|only if"], [], None),
"C14":([r"(provide|supply|make available|furnish|offer|give)[a-z]* .{0,60}(deposit slip|envelope|special slip)|(deposit slip|envelope|special slip)[a-z]* .{0,60}(provided|available|supplied|furnished)|how to (prepare|obtain)"], [r"reasonabl|available"], None),
}

UNION = {"O01","O02","L11"}   # enumerative obligations: elements may be spread across scenarios

def score(oid, bl):
    core, qual, dist = SIG[oid]
    if oid in UNION: bl = ["\n".join(bl)]
    hit = [b for b in bl if all(re.search(p, b, re.I) for p in core)]
    full = any(all(re.search(q, b, re.I) for q in qual) for b in hit)
    if hit and full:
        return "F", 1.0
    if dist:
        dhit = [b for b in bl if all(re.search(p, b, re.I) for p in core[:2]) and re.search(dist, b, re.I)]
        if dhit:
            return "D", 0.0
    if hit:
        return "P", 0.5
    return "M", 0.0
