#!/usr/bin/env python3
"""V45: add 380 playable first-pass career records to the V44 Android source."""
from pathlib import Path
import csv, json, re, unicodedata
root=Path(__file__).resolve().parent.parent
html_path=root/"app/src/main/assets/www/index.html"
csv_path=root/"v45/V45_NEW_380_PLAYERS.csv"
gradle_path=root/"app/build.gradle"
raw=html_path.read_text(encoding="utf-8")
prefix="window.__CareerEmbedded="
start=raw.index(prefix)+len(prefix)
end=raw.index(";</script>",start)
data=json.loads(raw[start:end]);cat=data["catalog"]
if cat["count"]!=620 or len(cat["entries"])!=620:raise SystemExit("V45 expects V44 roster of 620")
def slug(text):
    for a,b in [("ø","o"),("ł","l"),("ı","i"),("ß","ss"),("æ","ae")]:text=text.replace(a,b)
    return re.sub("[^a-z0-9]+","",unicodedata.normalize("NFKD",text).encode("ascii","ignore").decode().lower())
ALIAS={"Éder Lopes":["Éder"],"Alfredo Di Stéfano":["Di Stefano"],"Johan Neeskens":["Neeskens"],
"Adriano Imperador":["Adriano Leite Ribeiro"],"John Obi Mikel":["Mikel John Obi"],
"Álvaro Negredo":["Negredo"],"Sofyan Amrabat":["Amrabat"],
"Caroline Graham Hansen":["Graham Hansen"],"Ferenc Puskás":["Puskas"],
"Gianfranco Zola":["Zola"],"Kelley O'Hara":["Kelley OHara"]}
with csv_path.open(encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f))
if len(rows)!=380:raise SystemExit("Expected exactly 380 additions; got "+str(len(rows)))
names={slug(p["name"]) for p in cat["entries"]}
ids={p["id"] for p in cat["entries"]}
records=[]
for i,row in enumerate(rows):
    name=row["Player"]; key=slug(name); uid="v45-"+key
    if key in names or uid in ids:raise SystemExit("Duplicate: "+name)
    names.add(key);ids.add(uid)
    clubs=[]
    for spec in row["Selected_club_spells"].split("; "):
        m=re.fullmatch(r"(\d{4}(?:[–-](?:\d{4})?)?)\s+(.+)",spec.strip())
        if not m:raise SystemExit("Bad career clue for "+name+": "+spec)
        years,club=m.groups()
        clubs.append([years,club,False,None])
    if len(clubs)!=int(row["Num_spells"]):raise SystemExit("Bad club-count "+name)
    tier=int(row["Tier"]);gender=row["Category"]
    if gender not in ("men","women") or tier not in (1,2,3):raise SystemExit("Bad category/tier "+name)
    pack="0005" if i<250 else "0006"
    aliases=ALIAS.get(name,[])
    cat["entries"].append({"id":uid,"pack":pack,"name":name,"aliases":aliases,"tier":tier,
     "clubs":len(clubs),"eras":sorted({int(c[0][:4])//10*10 for c in clubs}),
     "tags":["journey"] if len(clubs)>=5 else [],
     "review_status":"v45-selected-clubs-first-pass-unverified","preview":False,"category":gender})
    records.append({"id":uid,"name":name,"country":row["Country"],"position":row["Position"],
      "moment":row["Note"],
      "detail":"V45 first-pass beta: these are selected senior club spells and may omit other stops. Dates, loans and changing club affiliations require independent review; league appearance counts are deliberately blank.",
      "clubs":clubs,"tier":tier,"aliases":aliases,"intl":"","preview":False,
      "editorial":{"review_status":"V45_FIRST_PASS_SELECTED_CLUBS_UNVERIFIED",
       "source_verified":False,"primary_source":"","supporting_sources":[],
       "reviewed":"2026-11-14","independent_second_source_audit_complete":False,
       "source_scope":"selected known senior clubs; NOT necessarily a full career or verified chronology",
       "missing_appearance_fields":len(clubs),"loan_status_unverified":True,
       "notes":"First-pass playable record, not independently fact-checked. Club omissions, years and active transfers may require edits. League appearances remain null.",
       "stats_snapshot_warning":"2026 current teams and active careers require scheduled validation."},
      "group":"V45 thousand-player expansion · "+gender})
data["packs"]["0005"]=records[:250];data["packs"]["0006"]=records[250:]
cat["count"]=len(cat["entries"]);cat["release"]="45.0-thousand-player-first-pass-2026-11-14"
cat["preview_count"]=0;cat["verified_count"]=620
cat["editorial_notice"]=("1,000 playable footballers, including 380 NEW first-pass beta histories with selected senior clubs. "
 "New club records have not yet been independently two-source checked and may omit loan spells or other career stops. "
 "League appearance counts for these new entries remain blank; old unresolved figures and 29 holds have been preserved. "
 "This is a football guessing game, not a fully verified statistical database.")
for gender in ("men","women"):cat["category_counts"][gender]=sum(p["category"]==gender for p in cat["entries"])
if cat["count"]!=1000 or cat["category_counts"]!={"men":803,"women":197}:
    raise SystemExit("Bad V45 roster counts")
raw=raw[:start]+json.dumps(data,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+raw[end:]
for a,b in [
 ("CAREER CLUES · V44","CAREER CLUES · V45"),
 ("Guess the Footballer V44","Guess the Footballer V45"),
 ("Career Clues V44</title>","Career Clues V45</title>"),
 ("version:'44.0'","version:'45.0'"),
 ("version:44,albumKnown","version:45,albumKnown"),
 ("version:44,entries","version:45,entries"),
 ("570 footballers in the roster</strong><span>620 first-pass reviewed · 0 awaiting review","1,000 footballers in the roster</strong><span>620 existing · 380 new beta career histories"),
 ("Beta pool OFF · 620 first-pass reviewed","380 new first-pass histories playable"),
 ("+' source-reviewed · '+","+' legacy records · '+"),
 ("+' REVIEWED'","+' PLAYABLE'"),
 ("+' SOURCE-REVIEWED · '+","+' PLAYABLE · '+"),
 ("+' source-reviewed'","+' playable'"),
 ("' REVIEWED'","' PLAYABLE'"),
 ("570 first-pass reviewed","570 historical first-pass reviewed"),
 ("Only source-reviewed careers enter normal matches. You can change this selection any time.","Normal matches also include first-pass V45 career clues. New entries need historical verification."),
 ("Optional testing only. Provisional club lists may be incomplete or wrong; years, loan status and league appearances are intentionally blank. Beta results do not affect your personal records. Daily Mystery uses source-reviewed players only.","V45 first-pass footballers are playable in normal matches and count towards your results. Their selected club histories may be incomplete; missing league appearances remain blank. Daily Mystery keeps its existing player pool."),
 ('<span id="databaseCount">151 REVIEWED</span>','<span id="databaseCount">1,000 PLAYABLE</span>')
]:raw=raw.replace(a,b)
if "'cc.galaxy.v15.'" not in raw:raise SystemExit("Save namespace changed")
html_path.write_text(raw,encoding="utf-8")
gradle=gradle_path.read_text(encoding="utf-8")
gradle=gradle.replace("versionCode 44","versionCode 45").replace("versionName '44.0-beta'","versionName '45.0-beta'")
gradle_path.write_text(gradle,encoding="utf-8")
print("V45 added",len(records),"total",cat["count"],"categories",cat["category_counts"])
