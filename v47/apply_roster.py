#!/usr/bin/env python3
"""V47: add 250 first-pass selected historical career records to V46 Android source."""
from pathlib import Path
import csv, json, re, unicodedata

root=Path(__file__).resolve().parent.parent
html_path=root/'app/src/main/assets/www/index.html'
csv_path=root/'v47/V47_NEW_250_PLAYERS.csv'
gradle_path=root/'app/build.gradle'
raw=html_path.read_text(encoding='utf-8')
start=raw.index('window.__CareerEmbedded=')+len('window.__CareerEmbedded=')
end=raw.index(';</script>',start)
data=json.loads(raw[start:end]); cat=data['catalog']
if cat['count']!=1250 or len(cat['entries'])!=1250:raise SystemExit('Expected V46 with 1250 records')
def slug(s):
    for a,b in [('ø','o'),('Ø','o'),('ł','l'),('ı','i'),('ß','ss'),('æ','ae')]:s=s.replace(a,b)
    return re.sub(r'[^a-z0-9]+','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
with csv_path.open(encoding='utf-8-sig',newline='') as fh: rows=list(csv.DictReader(fh))
if len(rows)!=250:raise SystemExit('Expected 250 V47 rows')
existing={slug(p['name']) for p in cat['entries']}; ids={p['id'] for p in cat['entries']}
new=[]
for i,r in enumerate(rows):
    name=r['Player']; uid='v47-'+slug(name)
    if slug(name) in existing or uid in ids:raise SystemExit('Duplicate player '+name)
    existing.add(slug(name));ids.add(uid)
    gender=r['Category']; tier=int(r['Tier'])
    if gender not in ('men','women') or tier not in (1,2,3):raise SystemExit('Bad category/tier '+name)
    clubs=[]
    for spec in r['Selected_club_spells'].split('; '):
        m=re.fullmatch(r'(\d{4}(?:[–-]\d{4})?) (.+)',spec.strip())
        if not m:raise SystemExit('Invalid career clue '+name+': '+spec)
        years,club=m.groups();clubs.append([years,club,False,None])
    if len(clubs)<2 or len(clubs)!=int(r['Num_spells']):raise SystemExit('Bad clubs '+name)
    aliases=['João Alves','Joao Alves'] if name=='João Alves de Assis Silva' else []
    pack='0009' if i<125 else '0010'
    cat['entries'].append({'id':uid,'pack':pack,'name':name,'aliases':aliases,'tier':tier,
        'clubs':len(clubs),'eras':sorted({int(v[0][:4])//10*10 for v in clubs}),
        'tags':['journey'] if len(clubs)>=5 else [],
        'review_status':'V47_FIRST_PASS_SELECTED_CLUBS_UNVERIFIED',
        'preview':False,'category':gender})
    new.append({'id':uid,'name':name,'country':r['Country'],'position':r['Position'],
        'moment':'A forgotten '+r['Country']+' '+r['Position'].lower()+' with selected spells at '+clubs[0][1]+' and '+clubs[-1][1]+'.',
        'detail':'V47 first-pass beta: these selected senior clubs are not a verified complete career. Dates, loan status and missing spells need further independent checking. Unverified appearance totals are blank.',
        'clubs':clubs,'tier':tier,'aliases':aliases,'intl':'','preview':False,
        'group':'V47 Forgotten Footballers · '+gender,
        'editorial':{'review_status':'V47_FIRST_PASS_SELECTED_CLUBS_UNVERIFIED',
        'source_verified':False,'primary_source':r['Source_url'],'supporting_sources':[],
        'reviewed':'2026-11-14','independent_second_source_audit_complete':False,
        'source_scope':'Selected senior clubs only, not complete independently verified history',
        'missing_appearance_fields':len(clubs),'loan_status_unverified':True,
        'notes':'Selected career years and other stops need checking before general release.',
        'stats_snapshot_warning':'Historical and present-day career data may need corrections.'}})
data['packs']['0009']=new[:125]; data['packs']['0010']=new[125:]
cat['count']=len(cat['entries']); cat['preview_count']=0
cat['verified_count']=620
cat['release']='47.0-forgotten-footballers-beta-2026-11-14'
cat['editorial_notice']=('1,500 playable footballers, including 250 new first-pass selected careers. Newer V45–V47 records lack independent historical verification. New unverified league appearances are blank.')
for gender in ('men','women'):
    cat['category_counts'][gender]=sum(v['category']==gender for v in cat['entries'])
assert cat['count']==1500 and cat['category_counts']=={'men':1203,'women':297}
assert sum(len(v) for v in data['packs'].values())==1500
assert sum(len(v['clubs']) for x in data['packs'].values() for v in x)==7890
before=raw[:start];after=raw[end:]
for x,y in [('Guess the Footballer V46','Guess the Footballer V47'),
('CAREER CLUES · V46','CAREER CLUES · V47'),
('Career Clues V46','Career Clues V47'),
('Android Beta V46','Android Beta V47'),
("version:'46.0'","version:'47.0'"),
('version:46,albumKnown','version:47,albumKnown'),
('1,250 footballers','1,500 footballers'),
('1250 footballers','1500 footballers'),
('1,250 PLAYABLE','1,500 PLAYABLE'),
('1,250 players','1,500 players'),
('Normal matches also include first-pass V45/V46 career clues','Normal matches also include first-pass V45/V46/V47 career clues')]:
    before=before.replace(x,y);after=after.replace(x,y)
raw=before+json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+after
if 'cc.galaxy.v15.' not in raw:raise SystemExit('Save key unexpectedly changed')
html_path.write_text(raw,encoding='utf-8')
gradle=gradle_path.read_text(encoding='utf-8')
gradle=gradle.replace('versionCode 46','versionCode 47')
gradle=gradle.replace("versionName '46.0-beta'","versionName '47.0-beta'")
gradle_path.write_text(gradle,encoding='utf-8')
print('V47 ready: 1500 players, 1203 men, 297 women, 7890 club clues.')
