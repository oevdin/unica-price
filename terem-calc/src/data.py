import pandas as pd, glob, json, re
f=glob.glob('price/*.xlsx')[0]
X=pd.read_excel(f,sheet_name=None,header=None)
raw=json.load(open('raw.json'))
def cl(v): return re.sub(r'\s+',' ',str(v)).strip() if pd.notna(v) else ''
def ckey(c):
    c=c.lower()
    if 'пвх' in c or 'пэт' in c: return 'ПВХ'
    if 'файн лайн 1' in c: return 'FL1'
    if 'файн лайн 2' in c: return 'FL2'
    if 'ясень' in c: return 'Ясень'
    if 'масло' in c: return 'Дуб масло'
    if 'дуб' in c: return 'Дуб'
    if 'орех' in c: return 'Орех'
    return 'Эмаль'
def nice_coat(c):
    c=c.replace('НАТУРАЛЬНЫЙ ШПОН','Шпон').replace('ЭМАЛЬ','Эмаль').replace(' Категория','').replace('ДУБ','Дуб').replace('ОРЕХ','Орех')
    c=c.replace('Эмаль глухое полотно','Эмаль').replace('Эмаль полотно со стеклом без декора','Эмаль, стекло без декора').replace('Эмаль полотно с фацетным стеклом','Эмаль, фацетное стекло')
    return c.strip()
def nice_model(m):
    m=re.sub(r' · [0-9.]+$','',m); m=m.replace('***','').replace('**','').replace('*','')
    return re.sub(r'\s+',' ',m).strip()
NAMES={'Дизайн (Юнит, Капричио...)':'Дизайн (Юнит, Капричио…)','Е-Дизайн (Степ, Подио, Лайн)':'Е-Дизайн (Степ, Подио, Лайн)'}
cols=[]
for t in raw:
    sh=t['sheet']; models={}
    for r in t['rows']:
        for m,p in r['prices'].items():
            mm=nice_model(m)
            models.setdefault(mm,[]).append({'c':nice_coat(r['coat']),'k':ckey(r['coat']),'p':round(p,2)})
    if not models: continue
    cols.append({'name':NAMES.get(sh,sh),'sheet':sh,'models':[{'n':k,'coats':v} for k,v in models.items()]})
# Эклектика manually
d=X['Эклектика']
cols.append({'name':'Эклектика','sheet':'Эклектика','models':[{'n':'Ансе (Anse)','coats':[{'c':'Эмаль Гладкая','k':'Эмаль','p':30725.25}]},{'n':'Арчи (Arche)','coats':[{'c':'Эмаль Гладкая','k':'Эмаль','p':30725.25}]},{'n':'Спейс (Space)','coats':[{'c':'Эмаль Гладкая','k':'Эмаль','p':36050.25}]}]})
# glass tables
for c in cols:
    d=X[c['sheet']]; g=[]
    for i in range(len(d)):
        row=[cl(v) for v in d.iloc[i]]
        if any(v.startswith('Модификация') for v in row[:3]):
            start=6 if c['sheet']!='Эклектика' else 4
            heads={j:row[j] for j in range(start,d.shape[1]) if row[j]}
            grp='';r=i+1
            while r<len(d):
                rr=[cl(v) for v in d.iloc[r]]
                if rr[0].startswith('Доплат') or rr[1].startswith('Доплат') or 'Варианты' in rr[1] or rr[0].startswith('Вид'): break
                if rr[0] or (c['sheet']=='Эклектика' and rr[1]): grp=rr[0] or rr[1]
                sub=rr[2] if c['sheet']!='Эклектика' else rr[3]
                col4=rr[4] if c['sheet']!='Эклектика' else ''
                for j,hn in heads.items():
                    v=d.iat[r,j]
                    if isinstance(v,(int,float)) and pd.notna(v) and v>100:
                        g.append({'m':nice_model(hn),'n':(grp+(' — '+sub if sub else '')+(' ('+col4+')' if col4 and len(col4)<40 else '')).strip(' —'),'p':round(float(v),2)})
                r+=1
                if r-i>30: break
    c['glass']=g
# погонаж
P=X['Погонаж']
def val(r,cc):
    v=P.iat[r,cc]; return round(float(v),2) if isinstance(v,(int,float)) and pd.notna(v) else None
KEYS={'ПВХ':10,'Эмаль':11,'FL1':12,'FL2':13,'Ясень':14,'Дуб':15,'Дуб масло':16,'Орех':17}
KQ={'ПВХ':33,'Эмаль':34,'FL1':35,'FL2':36,'Ясень':37,'Дуб':38,'Дуб масло':39,'Орех':40}
items=[]
def add(group,name,base,typ,rowmap,col,unit='шт.'):
    pr={k:val(r,col) for k,r in rowmap.items()}
    pr={k:v for k,v in pr.items() if v}
    if pr: items.append({'g':group,'n':name,'base':base,'t':typ,'pr':pr,'u':unit})
# typ: box | nal | dob
add('L','Короб L прямой 34×75',2120,'box',KEYS,2)
add('L','Короб L 45 усиленный 45×90',2400,'box',KEYS,3)
add('L','Наличник плоский Z 10×75',2150,'nal',KEYS,4)
add('L','Наличник плоский L 10×50',2150,'nal',KEYS,5)
add('L','Наличник плоский L 10×75',2150,'nal',KEYS,6)
add('L','Наличник плоский L 10×90',2150,'nal',KEYS,7)
add('L','Наличник плоский L 16×75',2150,'nal',KEYS,8)
add('L','Наличник плоский L 16×90',2150,'nal',KEYS,9)
add('L','Наличник плоский L 16×110',2150,'nal',KEYS,10)
add('L','Наличник фигурный WL 12×85',2400,'nal',KEYS,18)
for w,cc in [(100,11),(200,12),(300,13),(400,14),(500,15),(900,16)]: add('L',f'Добор (расширитель) L {w} мм',2120,'dob',KEYS,cc)
add('L','Планка притворная',2050,'other',KEYS,20)
add('Q','Короб Q 34×72',2120,'box',KQ,2)
add('Q','Наличник Q плоский 10×50',2150,'nal',KQ,3)
add('Q','Наличник Q плоский 10×90',2150,'nal',KQ,4)
add('Q','Наличник Q плоский 10×110',2400,'nal',KQ,5)
add('Q','Наличник Q плоский 10×150',2700,'nal',KQ,6)
add('Q','Короб RQ 34×69 (обратное открывание)',2120,'box',KQ,7)
add('Q','Наличник RQ 10×90',2150,'nal',KQ,8)
add('Q','Наличник RQ 10×110',2400,'nal',KQ,9)
add('Q','Наличник RQ 10×150',2700,'nal',KQ,10)
add('Q','Короб SQ 34×69',2700,'box',KQ,11)
add('Q','Наличник SQ 12×90',2700,'nal',KQ,12)
add('Q','Короб К 69 (компланарный)',2120,'box',KQ,13)
add('Q','Короб RK 36×69 (компланарный, обратный)',2700,'box',KQ,15)
add('Q','Переходник на Q погонаж 22×100',2120,'other',KQ,18)
FIG={'Эмаль':48}
for n,cc,b in [('Наличник фигурный Этна 16×85',2,2400),('Наличник фигурный Комо 16×90',3,2400),('Наличник фигурный ML 16×85',4,2400),('Наличник фигурный Арно 16×110',5,2700),('Наличник фигурный Степ 23×110',6,2700),('Наличник фигурный Лацио 16×110',7,2700),('Наличник фигурный Модерн 23×110',8,2400)]:
    add('Фигурные',n,b,'nal',FIG,cc)
add('Фигурные','Добор Лацио 100 мм',2120,'dob',FIG,10); add('Фигурные','Добор Лацио 200 мм',2120,'dob',FIG,11)
M={'Эмаль':61}
add('M','Короб M 34×72',2120,'box',M,2); add('M','Наличник M 15×85',2400,'nal',M,4); add('M','Добор M 100 мм',2120,'dob',M,7); add('M','Добор M 200 мм',2120,'dob',M,9)
# heights
H=X['Наценки за габариты']
def hv(s): 
    s=cl(s); m=re.search(r'(\d{4})',s); return int(m.group(1)) if m else None
groups={}
for start,name in [(4,'400–900'),(17,'450–950'),(30,'1000–1100')]:
    rows=[]
    for i in range(start,start+13):
        rows.append({'h':hv(H.iat[i,2]),'p':float(H.iat[i,3]) if pd.notna(H.iat[i,3]) else None,
                     'len':hv(H.iat[i,5]),'pb':float(H.iat[i,6]) if isinstance(H.iat[i,6],(int,float)) and pd.notna(H.iat[i,6]) else None,
                     'p24':float(H.iat[i,7]) if isinstance(H.iat[i,7],(int,float)) and pd.notna(H.iat[i,7]) else 0,
                     'p27':float(H.iat[i,8]) if isinstance(H.iat[i,8],(int,float)) and pd.notna(H.iat[i,8]) else 0})
    groups[name]=rows
out={'priceDate':'17.08.2026','collections':cols,'mold':items,'heights':groups}
json.dump(out,open('data.json','w'),ensure_ascii=False)
for c in cols: print(c['name'],len(c['models']),'glass',len(c['glass']))
print(len(items),'погонаж')
for g,r in groups.items(): print(g,[(x['h'],x['p'],x['len'],x['pb'],x['p24'],x['p27']) for x in r])
