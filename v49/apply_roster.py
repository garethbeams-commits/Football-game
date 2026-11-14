#!/usr/bin/env python3
"""V49: add 250 selected-club first-pass footballers to the V48 Android game."""
from pathlib import Path
import csv, json, re, unicodedata
root=Path(__file__).resolve().parent.parent
p=root/'app/src/main/assets/www/index.html'
g=root/'app/build.gradle'
raw=p.read_text(encoding='utf-8')
a=raw.index('window.__CareerEmbedded=')+len('window.__CareerEmbedded=')
b=raw.index(';</script>',a)
data=json.loads(raw[a:b]);cat=data['catalog']
if cat['count']!=1750: raise SystemExit(f'V49 requires V48 base (1750), found {cat["count"]}')
def slug(s):
    for x,y in [('ø','o'),('Ø','o'),('ł','l'),('ı','i'),('ß','ss'),('æ','ae'),('ð','d')]:s=s.replace(x,y)
    return re.sub(r'[^a-z0-9]+','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
with (root/'v49/V49_NEW_250_PLAYERS.csv').open(encoding='utf-8-sig',newline='') as fh:
    rows=list(csv.DictReader(fh))
if len(rows)!=250:raise SystemExit('Expected 250 rows')
names={slug(x['name']) for x in cat['entries']};ids={x['id'] for x in cat['entries']}
new=[];men=women=0
for i,r in enumerate(rows):
    name=r['Player'];key=slug(name);uid='v49-'+key
    if key in names or uid in ids:raise SystemExit('Duplicate '+name)
    if r['Category'] not in ('men','women'):raise SystemExit('Invalid gender '+name)
    names.add(key);ids.add(uid)
    if r['Category']=='men':men+=1
    else:women+=1
    clubs=[]
    for spec in r['Selected_club_spells'].split('; '):
        match=re.fullmatch(r'(\d{4}(?:[–-]\d{4})?) (.+)',spec)
        if not match:raise SystemExit(f'Invalid club spell: {name} {spec}')
        years,club=match.groups()
        clubs.append([years,club,False,None])
    if len(clubs)<2 or len(clubs)!=int(r['Num_spells']):raise SystemExit('Invalid club count '+name)
    if int(r['Tier'])!=3:raise SystemExit('Non-hard record '+name)
    pack='0013' if i<125 else '0014'
    cat['entries'].append({'id':uid,'pack':pack,'name':name,'aliases':[],
        'tier':3,'clubs':len(clubs),'eras':sorted({int(c[0][:4])//10*10 for c in clubs}),
        'tags':['journey'] if len(clubs)>=5 else [],
        'review_status':'V49_FIRST_PASS_SELECTED_CLUBS_UNVERIFIED','preview':False,'category':r['Category']})
    new.append({'id':uid,'name':name,'country':r['Country'],'position':r['Position'],
        'moment':f'A forgotten {r["Country"]} {r["Position"].lower()} with selected spells at {clubs[0][1]} and {clubs[-1][1]}.',
        'detail':'V49 first-pass beta: selected senior club stops, not a verified complete chronology. Dates, loans, omitted stops require review; league appearances are deliberately blank.',
        'clubs':clubs,'tier':3,'aliases':[],'intl':'','preview':False,
        'editorial':{'review_status':'V49_FIRST_PASS_SELECTED_CLUBS_UNVERIFIED',
          'source_verified':False,'primary_source':r.get('Source_url',''),
          'supporting_sources':[],'reviewed':'2026-11-14',
          'independent_second_source_audit_complete':False,
          'source_scope':'Selected senior clubs; not a complete independently verified history',
          'missing_appearance_fields':len(clubs),'loan_status_unverified':True,
          'notes':'First-pass chronology requires historical review.',
          'stats_snapshot_warning':'Active and older affiliations need confirmation.'},
        'group':'V49 Forgotten Footballers · '+r['Category']})
if (men,women)!=(190,60):raise SystemExit('Category mismatch')
data['packs']['0013']=new[:125];data['packs']['0014']=new[125:]
cat['count']=len(cat['entries']);cat['preview_count']=0;cat['verified_count']=620
cat['release']='49.0-2000-forgotten-first-pass-2026-11-14'
cat['editorial_notice']='2,000 playable players. V45–V49 first-pass selected club stops may be incomplete or misdated. New domestic appearance values deliberately blank. This is not a certified career database.'
for gender in ('men','women'):cat['category_counts'][gender]=sum(x['category']==gender for x in cat['entries'])
assert cat['count']==2000 and cat['category_counts']=={'men':1593,'women':407}
assert sum(len(x['clubs']) for pack in data['packs'].values() for x in pack)==9834
before=raw[:a];after=raw[b:]
for x,y in [
 ('Guess the Footballer V48','Guess the Footballer V49'),
 ('Career Clues V43','Career Clues V49'),
 ('CAREER CLUES · V48','CAREER CLUES · V49'),
 ('Career Clues V48','Career Clues V49'),
 ('Android Beta V48','Android Beta V49'),
 ("version:'48.0'","version:'49.0'"),
 ('version:48,albumKnown','version:49,albumKnown'),
 ('version:48,entries','version:49,entries'),
 ('1,750 footballers','2,000 footballers'),
 ('1750 footballers','2000 footballers'),
 ('1,750 PLAYABLE','2,000 PLAYABLE'),
 ('1750 PLAYABLE','2000 PLAYABLE'),
 ('1,750 players','2,000 players')
]:
    before=before.replace(x,y);after=after.replace(x,y)
final=before+json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+after
if 'cc.galaxy.v15.' not in final:raise SystemExit('Saved-progress namespace missing')
p.write_text(final,encoding='utf-8')
gradle=g.read_text(encoding='utf-8').replace('versionCode 48','versionCode 49').replace("versionName '48.0-beta'","versionName '49.0-beta'")
g.write_text(gradle,encoding='utf-8')
print('V49 built:',cat['count'],'players /',sum(len(x['clubs']) for x in new),'new selected club stops')
