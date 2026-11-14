#!/usr/bin/env python3
"""Apply the 50-player V44 roster expansion to the original V43 Android app before building."""
from pathlib import Path
import csv, json, re, unicodedata

root = Path(__file__).resolve().parent.parent
html_path = root / "app/src/main/assets/www/index.html"
csv_path = root / "v44/V44_NEW_50_PLAYERS.csv"
gradle_path = root / "app/build.gradle"
raw = html_path.read_text(encoding="utf8")
prefix = "window.__CareerEmbedded="
start = raw.index(prefix) + len(prefix)
end = raw.index(";</script>", start)
payload = json.loads(raw[start:end])
cat = payload["catalog"]
if cat["count"] != 570:
    raise SystemExit("Unexpected source version: expected 570 players")
ALIASES = {
    "Sophia Wilson": ["Sophia Smith"],
    "Cata Coll": ["Catalina Coll"],
    "Thiago Alcântara": ["Thiago"],
    "Juan Sebastián Verón": ["Juan Sebastian Veron"],
}
def slug(text):
    for a,b in [("ø","o"),("Ø","O"),("ł","l"),("ı","i"),("ß","ss"),("æ","ae")]:
        text=text.replace(a,b)
    return re.sub("[^a-z0-9]+","",unicodedata.normalize("NFKD",text).encode("ascii","ignore").decode().lower())
with csv_path.open(encoding="utf-8",newline="") as fh:
    rows = list(csv.DictReader(fh))
if len(rows) != 50:
    raise SystemExit("Expected exactly 50 new player records")
seen_ids = {e["id"] for e in cat["entries"]}
seen_names = {slug(e["name"]) for e in cat["entries"]}
new = []
for row in rows:
    name=row["Player"]
    uid="v44-"+slug(name)
    if uid in seen_ids or slug(name) in seen_names:
        raise SystemExit("Duplicate player: "+name)
    seen_ids.add(uid)
    seen_names.add(slug(name))
    clubs=[]
    for spec in row["Career_club_records"].split("; "):
        match = re.match(r"^(\d{4}(?:[–-](?:\d{4})?)?)\s+(.+)$",spec)
        if not match:
            raise SystemExit("Bad career clue "+name+": "+spec)
        years,club = match.groups()
        loan=club.endswith(" (loan)")
        if loan: club=club[:-7]
        clubs.append([years,club,loan,None])
    source=row["FBref_or_first_pass_source"].strip()
    aliases=ALIASES.get(name,[])
    e={"id":uid,"pack":"0004","name":name,"aliases":aliases,
       "tier":int(row["Tier"]),"clubs":len(clubs),
       "eras":sorted({int(c[0][:4])//10*10 for c in clubs}),
       "tags":["journey"] if len(clubs)>=5 else [],
       "review_status":"first-pass-reviewed-v44","preview":False,"category":row["Category"]}
    p={"id":uid,"name":name,"country":row["Country"],"position":row["Position"],
       "moment":row["Summary"],"detail":"Career chronology added in V44 first pass. League appearances await competition-specific verification.",
       "clubs":clubs,"tier":int(row["Tier"]),"aliases":aliases,"intl":"",
       "preview":False,"group":"V44 added footballers · "+row["Category"],
       "editorial":{"review_status":"V44_FIRST_PASS_SOURCE_REVIEW",
                    "source_verified":bool(source),"primary_source":source,
                    "supporting_sources":[],
                    "reviewed":"2026-11-13",
                    "independent_second_source_audit_complete":False,
                    "source_scope":"first-pass senior club chronology, not a verified league-appearance total",
                    "missing_appearance_fields":len(clubs),
                    "notes":"All 50 new records deliberately leave league appearance figures blank pending further checks.",
                    "stats_snapshot_warning":"Active transfers and club records need periodic review."}}
    cat["entries"].append(e)
    new.append(p)
payload["packs"]["0004"]=new
cat["release"]="44.0-fbref-roster-expansion-2026-11-13"
cat["count"]=len(cat["entries"])
cat["verified_count"]=cat["count"]
cat["preview_count"]=0
for gender in ("men","women"):
    count=sum(e["category"]==gender for e in cat["entries"])
    cat["category_counts"][gender]=count
    cat["reviewed_by_category"][gender]=count
assert cat["count"]==620 and len(new)==50
raw=raw[:start]+json.dumps(payload,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+raw[end:]
raw=raw.replace("version:'43.0'","version:'44.0'").replace("version:43,albumKnown","version:44,albumKnown")
raw=raw.replace("570 first-pass reviewed","620 first-pass reviewed")
raw=raw.replace("CAREER CLUES · V42","CAREER CLUES · V44")
raw=raw.replace("Guess the Footballer V43","Guess the Footballer V44")
if "cc.galaxy.v15." not in raw: raise SystemExit("Save namespace missing")
html_path.write_text(raw,encoding="utf8")
gradle=gradle_path.read_text(encoding="utf8")
gradle=gradle.replace("versionCode 43","versionCode 44").replace("versionName '43.0-beta'","versionName '44.0-beta'")
gradle_path.write_text(gradle,encoding="utf8")
print("V44 expanded roster to",cat["count"],"(",cat["category_counts"],")")
