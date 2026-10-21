import pandas as pd, glob, json, re, sys
f=glob.glob('price/*.xlsx')[0]
SHEETS=['Порте','Порте 4Ал','Слот','Дуэт','Ветро','Твист','Фьюжн','Элеганс','Сиена','Савона','Модерн','Неоклассик','Россо','Е-Классик','Стандарт','Амелия','Дизайн (Юнит, Капричио...)','Юнит Слот','Бриз','Е-Дизайн (Степ, Подио, Лайн)','Эклектика','Жалюзи','Арочные двери']
def cl(v): return re.sub(r'\s+',' ',str(v)).strip() if pd.notna(v) else ''
out=[]
for sh in SHEETS:
    d=pd.read_excel(f,sheet_name=sh,header=None)
    for i in range(len(d)):
        if cl(d.iat[i,0])=='Вид покрытия' and 'Вид' in cl(d.iat[i,5]) :
            # section title above
            title=''
            for k in range(i-1,max(i-4,-1),-1):
                t=cl(d.iat[k,1]) or cl(d.iat[k,0])
                if t: title=t;break
            cols={}
            for j in range(6,d.shape[1]):
                h=cl(d.iat[i,j])
                sub=cl(d.iat[i+1,j]) if i+1<len(d) else ''
                if h: cols[j]=(h,sub)
                elif sub and cols: pass
            r=i+1; group=''
            rows=[]
            while r<len(d):
                c0,c1,c5=cl(d.iat[r,0]),cl(d.iat[r,1]),cl(d.iat[r,5])
                nums={j:d.iat[r,j] for j in cols if isinstance(d.iat[r,j],(int,float)) and pd.notna(d.iat[r,j]) and d.iat[r,j]>500}
                if c5!='Полотно' and not nums:
                    if r>i+2: break
                    r+=1; continue
                if c0: group=c0
                coat=(group+' '+c1).strip() if c1 else group
                rows.append({'coat':coat,'h':cl(d.iat[r,4]),'w':cl(d.iat[r,3]),'prices':{cols[j][0]+(' · '+cols[j][1] if cols[j][1] and cols[j][1] not in('','-') else ''):float(v) for j,v in nums.items()}})
                r+=1
            out.append({'sheet':sh,'title':title,'rows':rows})
json.dump(out,open('raw.json','w'),ensure_ascii=False,indent=1)
for t in out:
    print('##',t['sheet'],'|',t['title'],'|',len(t['rows']))
    for r in t['rows'][:30]: print('   ',r['coat'],'|',r['h'],'|',{k[:40]:round(v) for k,v in r['prices'].items()})
