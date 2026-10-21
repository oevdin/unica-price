"""Собирает index.html из app_src.html + data.json + imgs.json"""
import json, sys, os
d=os.path.dirname(os.path.abspath(__file__))
src=open(os.path.join(d,'app_src.html')).read()
data=json.load(open(os.path.join(d,'data.json')))
imgs=json.load(open(os.path.join(d,'imgs.json')))
out=src.replace('/*DATA*/null',json.dumps(data,ensure_ascii=False)).replace('/*IMGS*/null',json.dumps(imgs))
dst=sys.argv[1] if len(sys.argv)>1 else os.path.join(d,'index.html')
open(dst,'w').write('<!doctype html>\n<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body>\n'+out+'\n</body></html>\n')
print('built',dst,os.path.getsize(dst)//1024,'KB')
