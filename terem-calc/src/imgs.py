import re,os,json,base64,io
import numpy as np
from PIL import Image
X='price/unzipped/'
wb=open(X+'xl/workbook.xml').read(); rels=open(X+'xl/_rels/workbook.xml.rels').read()
rid={}
for m in re.finditer(r'<Relationship [^>]*>',rels):
  t=m.group(0); rid[re.search(r'Id="([^"]+)"',t).group(1)]=re.search(r'Target="([^"]+)"',t).group(1)
SHEETS=['Порте','Порте 4Ал','Слот','Дуэт','Ветро','Твист','Фьюжн','Элеганс','Сиена','Савона','Модерн','Бергамо','Беллуно','Неоклассик','Россо','Е-Классик','Стандарт','Амелия','Дизайн (Юнит, Капричио...)','Юнит Слот','Бриз','Е-Дизайн (Степ, Подио, Лайн)','Эклектика','Жалюзи']
def crops(path):
  im=Image.open(path).convert('L'); a=np.array(im); h,w=a.shape
  dark=a<200; rows=dark.any(axis=1)
  if not rows.any(): return []
  top=np.where(rows)[0][0]
  gaps=[y for y in range(top,h) if not rows[y]]
  bottom=gaps[0] if gaps else h
  cols=dark[top:bottom].any(axis=0); segs=[];s=None
  for x in range(w):
    if cols[x] and s is None: s=x
    if not cols[x] and s is not None:
      if x-s>15: segs.append((s,x))
      s=None
  if s is not None: segs.append((s,w))
  out=[]
  for k,(x0,x1) in enumerate(segs):
    c=im.crop((x0,top,x1,bottom)); r=c.height/c.width
    if 1.6<r<3.6 and c.height>120:
      lx0=(segs[k-1][1]+x0)//2 if k>0 else 0
      lx1=(x1+segs[k+1][0])//2 if k+1<len(segs) else w
      lab=im.crop((lx0,bottom,lx1,h))
      la=np.array(lab)<160
      if la.any():
        ys=np.where(la.any(axis=1))[0]; xs=np.where(la.any(axis=0))[0]
        lab=lab.crop((max(0,xs[0]-2),max(0,ys[0]-2),xs[-1]+3,ys[-1]+3))
      else: lab=None
      out.append((c,lab))
  return out
res={}
for sh in SHEETS:
  r=re.search(r'<sheet name="'+re.escape(sh)+r'"[^>]*r:id="(rId\d+)"',wb).group(1)
  f='xl/'+rid[r].replace('/xl/','')
  rf=os.path.join(X,os.path.dirname(f),'_rels',os.path.basename(f)+'.rels')
  if not os.path.exists(rf): continue
  media=[]
  for dr in re.findall(r'Target="([^"]*drawing[^"]*)"',open(rf).read()):
    p=os.path.normpath(os.path.join(os.path.dirname(f),dr)); pr=os.path.join(X,os.path.dirname(p),'_rels',os.path.basename(p)+'.rels')
    # order by anchor row
    xml=open(X+p).read(); mp={}
    for m in re.finditer(r'<Relationship [^>]*>',open(pr).read()):
      t=m.group(0); mp[re.search(r'Id="([^"]+)"',t).group(1)]=re.search(r'Target="([^"]+)"',t).group(1)
    for a in re.findall(r'<xdr:(?:twoCellAnchor|oneCellAnchor).*?</xdr:(?:twoCellAnchor|oneCellAnchor)>',xml,re.S):
      fr=re.search(r'<xdr:row>(\d+)</xdr:row>',a); e=re.search(r'r:embed="([^"]+)"',a)
      if e: media.append((int(fr.group(1)),os.path.basename(mp[e.group(1)])))
  seen=[];lst=[]
  for row,mfile in sorted(media):
    if mfile in seen or mfile in('image38.jpeg',) or not os.path.exists(X+'xl/media/'+mfile): continue
    seen.append(mfile)
    im=Image.open(X+'xl/media/'+mfile)
    if im.width<100 or im.height<150: continue
    for c,lab in crops(X+'xl/media/'+mfile):
      c=c.resize((max(1,round(c.width*200/c.height)),200),Image.LANCZOS)
      b=io.BytesIO(); c.save(b,'PNG',optimize=True); e={'d':base64.b64encode(b.getvalue()).decode()}
      if lab is not None and lab.height>5:
        if lab.height>28: lab=lab.resize((max(1,round(lab.width*28/lab.height)),28),Image.LANCZOS)
        b=io.BytesIO(); lab.save(b,'PNG',optimize=True); e['l']=base64.b64encode(b.getvalue()).decode()
      lst.append(e)
  res[sh]=lst
  print(sh,len(lst))
json.dump(res,open('imgs.json','w'))
print(os.path.getsize('imgs.json')//1024,'KB')
# contact sheet for checking
