import re, json, csv
R="/home/claude/reports/Каталог упражнений и программ тренировок.md"
L=open(R,encoding="utf-8").read().split("\n")
def sect(a,b): return "\n".join(L[a-1:b-1])
rows=[];cur=None;hdr=None
for i,l in enumerate(L,1):
    if 242<=i<709:
        m=re.match(r"### (3\.\d+)\. (.+)",l)
        if m: cur=m.group(1)+" "+m.group(2); continue
        if l.startswith("| id |"): hdr=[c.strip() for c in l.strip("|").split("|")]; continue
        if l.startswith("|") and hdr and not l.startswith("|---") and not l.startswith("| ---"):
            c=[x.strip() for x in re.split(r"(?<!\\)\|",l.strip()[1:-1])]
            if len(c)==len(hdr) and c[0]!="id":
                d=dict(zip(hdr,c)); d["group"]=cur; rows.append(d)
print(len(rows))
keys=["id","name_ru","name_en","Пат.","Осн. мышцы","Инв.","Ур.","Шаг","e1RM","group"]
ren={"Пат.":"pattern","Осн. мышцы":"muscles","Инв.":"equipment","Ур.":"level","Шаг":"step","e1RM":"e1rm"}
out=[]
for d in rows:
    o={ren.get(k,k):d.get(k,"") for k in keys}
    o["notes_flags"]=d.get("Замены / флаги") or d.get("Примечания / флаги") or ""
    out.append(o)
json.dump(out,open("/tmp/pkg/data/exercises.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
with open("/tmp/pkg/data/exercises.csv","w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
open("/tmp/pkg/data/progression_ladders_and_ru_names.md","w",encoding="utf-8").write(sect(709,796))
open("/tmp/pkg/data/programming_rules.md","w",encoding="utf-8").write(sect(796,950))
open("/tmp/pkg/data/programs_T01-T22.md","w",encoding="utf-8").write(sect(950,1254))
open("/tmp/pkg/data/safety_screening.md","w",encoding="utf-8").write(sect(1254,1324))
open("/tmp/pkg/data/data_schema.md","w",encoding="utf-8").write(sect(45,234))
open("/tmp/pkg/data/gaps_and_sources.md","w",encoding="utf-8").write(sect(1324,len(L)+1))
from collections import Counter
print(Counter(o["group"] for o in out))
