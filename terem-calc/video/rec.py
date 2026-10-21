import time, os, glob, shutil
from playwright.sync_api import sync_playwright
import os; U='file://'+os.path.abspath('../index.html')
W,H=1440,900
INJ=r"""
(()=>{
const st=document.createElement('style');st.textContent=`
@font-face{font-family:"Onest";src:local("Inter"),local("Inter Regular");font-weight:400}
@font-face{font-family:"Onest";src:local("Inter Medium");font-weight:500}
@font-face{font-family:"Onest";src:local("Inter SemiBold");font-weight:600}
@font-face{font-family:"Onest";src:local("Inter Bold");font-weight:700}
#vcap{position:fixed;left:50%;bottom:28px;transform:translateX(-50%);z-index:9999;background:rgba(17,18,20,.94);color:#fff;font:600 25px/1.35 Inter,sans-serif;padding:16px 26px 16px 22px;border-radius:16px;max-width:1000px;display:flex;gap:16px;align-items:center;box-shadow:0 12px 40px rgba(0,0,0,.35);transition:opacity .3s}
#vcap .st{background:#43d19f;color:#0b1f17;font-size:16px;font-weight:700;padding:5px 10px;border-radius:8px;white-space:nowrap;letter-spacing:.04em}
#vcap .sm{display:block;font-weight:400;font-size:19px;color:#c7cdd2;margin-top:3px}
#vring{position:fixed;z-index:9998;border:3px solid #43d19f;border-radius:12px;box-shadow:0 0 0 6px rgba(67,209,159,.25);pointer-events:none;transition:all .35s ease;opacity:0}
#vcur{position:fixed;z-index:10000;width:22px;height:22px;margin:-3px 0 0 -3px;pointer-events:none;transition:transform .08s}
#vcur.dn{transform:scale(.8)}
#vfull{position:fixed;inset:0;z-index:10001;background:#131517;color:#eceef0;display:flex;flex-direction:column;justify-content:center;padding:0 140px;gap:22px;font-family:Inter,sans-serif;transition:opacity .5s}
#vfull .e{color:#43d19f;font-weight:700;letter-spacing:.18em;font-size:20px;text-transform:uppercase}
#vfull .t{font-family:"DejaVu Serif",Georgia,serif;font-size:76px;line-height:1.05;max-width:1100px}
#vfull .s{font-size:28px;color:#b8bec4;max-width:1000px;line-height:1.4}
#vfull .b{position:absolute;left:140px;bottom:60px;font-size:20px;color:#8e949a}#vfull .b b{color:#8f9bff}
`;document.head.appendChild(st);
const c=document.createElement('div');c.id='vcap';c.style.opacity=0;document.body.appendChild(c);
const r=document.createElement('div');r.id='vring';document.body.appendChild(r);
const cur=document.createElement('div');cur.id='vcur';cur.innerHTML='<svg viewBox="0 0 24 24" width="22" height="22"><path d="M3 2l17 9-7.5 1.8L9 20z" fill="#131517" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>';cur.style.left='720px';cur.style.top='450px';document.body.appendChild(cur);
addEventListener('mousemove',e=>{cur.style.left=e.clientX+'px';cur.style.top=e.clientY+'px'},true);
addEventListener('mousedown',()=>cur.classList.add('dn'),true);addEventListener('mouseup',()=>cur.classList.remove('dn'),true);
let tgt=null;function place(){if(!tgt){r.style.opacity=0;return}const b=tgt.getBoundingClientRect();r.style.left=(b.left-8)+'px';r.style.top=(b.top-8)+'px';r.style.width=(b.width+16)+'px';r.style.height=(b.height+16)+'px';r.style.opacity=1}
addEventListener('scroll',place,true);setInterval(place,120);
window.V={cap(step,t,sm){c.innerHTML=(step?`<span class="st">${step}</span>`:'')+`<span>${t}${sm?`<span class="sm">${sm}</span>`:''}</span>`;c.style.opacity=1},
 nocap(){c.style.opacity=0},hl(sel){tgt=sel?document.querySelector(sel):null;place()},
 full(e,t,s,b){let f=document.getElementById('vfull');if(!f){f=document.createElement('div');f.id='vfull';document.body.appendChild(f)}f.style.opacity=1;f.innerHTML=`<div class="e">${e}</div><div class="t">${t}</div><div class="s">${s}</div>${b?`<div class="b">Разработано <b>UNICADigital</b></div>`:''}`},
 unfull(){const f=document.getElementById('vfull');if(f){f.style.opacity=0;setTimeout(()=>f.remove(),600)}}};
})();
"""
with sync_playwright() as p:
    b=p.chromium.launch()
    # prepare clean state
    ctx0=b.new_context(viewport={'width':W,'height':H}); pg0=ctx0.new_page(); pg0.goto(U); pg0.evaluate('localStorage.clear()'); ctx0.close()
    import json
    DUR=json.load(open('vo/dur.json'))
    ctx=b.new_context(viewport={'width':W,'height':H},record_video_dir='raw',record_video_size={'width':W,'height':H},color_scheme='light')
    T0=time.monotonic()
    pg=ctx.new_page(); pg.goto(U); pg.wait_for_timeout(600)
    pg.evaluate(INJ)
    pg.evaluate("document.querySelector('#newCalc').click()")
    pg.evaluate("window.scrollTo(0,0)")
    w=lambda ms: pg.wait_for_timeout(ms)
    MARK=[]; cur={'k':None,'t':0}
    def seg(k):
        if cur['k']:
            need=DUR[cur['k']]+0.5-(time.monotonic()-cur['t'])
            if need>0: w(int(need*1000))
        if k: cur['k']=k; cur['t']=time.monotonic(); MARK.append((k,cur['t']-T0))
    def cap(step,t,sm=''): pg.evaluate('([a,b,c])=>V.cap(a,b,c)',[step,t,sm])
    def hl(sel): pg.evaluate('s=>V.hl(s)',sel)
    def see(sel): pg.evaluate("s=>document.querySelector(s).scrollIntoView({behavior:'smooth',block:'center'})",sel); w(700)
    def move(sel):
        bb=pg.locator(sel).first.bounding_box(); pg.mouse.move(bb['x']+bb['width']/2,bb['y']+bb['height']/2,steps=25); w(150)
    def click(sel): move(sel); pg.mouse.down(); w(90); pg.mouse.up(); w(250)
    def typ(sel,text,clear=True):
        click(sel)
        if clear: pg.fill(sel,'')
        pg.locator(sel).first.type(text,delay=60); w(250)
    def sel_opt(sel,**kw): move(sel); hl(sel); w(400); pg.select_option(sel,**kw); w(600)
    seg('intro'); pg.evaluate("V.full('Видео-инструкция','Калькулятор дверей Терем','Как посчитать заказ по прайсу и отдать клиенту эскиз с расчётом в PDF',true)")
    seg('price'); pg.evaluate("V.unfull()"); w(600); cap('Шапка','Сначала проверьте дату прайса','Расчёт всегда идёт по прайсу, указанному здесь'); hl('.pill'); move('.pill')
    seg('client'); cap('Шаг 1','Заполните данные клиента','Они попадут в шапку документа'); hl('#form section.step')
    typ('#m_client','Иванов Алексей'); typ('#m_phone','+996 555 123 456'); typ('#m_obj','ЖК Ала-Тоо, кв. 45'); typ('#m_num','125')
    seg('markup'); cap('Шаг 1','Моя наценка — 10% по умолчанию','Скидку клиенту ставьте только по согласованию'); hl('#m_markup'); move('#m_markup')
    seg('model'); see('#d0_coll'); cap('Шаг 2','Выберите коллекцию и позицию в прайсе','По позиции берётся цена полотна'); sel_opt('#d0_coll',value='Е-Классик'); sel_opt('#d0_model',index=0)
    seg('pic'); see('.door .pics'); cap('Шаг 2','Нажмите на рисунок нужной модели','Именно он будет на эскизе в документе'); hl('.door .pics'); w(1200); click('.door .pics [data-pic="2"]')
    seg('coat'); see('#d0_coat'); cap('Шаг 2','Покрытие и цвет','Цвет пишется словами — он идёт в документ'); hl('#d0_coat'); w(900); typ('#d0_colorTxt','белый')
    seg('size'); see('#d0_W'); cap('Шаг 2','Размер полотна в миллиметрах','Наценку за высоту программа добавит сама'); hl('#d0_W'); typ('#d0_W','700'); hl('#d0_H'); typ('#d0_H','2500')
    seg('stab'); see('#dw0'); cap('Шаг 2','Выше 2350 мм — стабилизатор добавлен автоматически','Красные подсказки под дверью нужно прочитать'); hl('#dw0')
    seg('sys'); see('#d0_sys'); cap('Погонаж','Короб и наличник подбираются по системе','Стандартная система L — как в комплектах прайса'); hl('#d0_sys'); move('#d0_sys')
    seg('wall'); sel_opt('#d0_nalSel',label='фигурный ML 16×85'); cap('Погонаж','Введите толщину стены — добор подберётся сам','Стена 200 − короб 75 = 125 мм → добор 200 мм'); hl('#d0_wall'); typ('#d0_wall','200'); hl('#dm0')
    seg('doc'); cap('Документ','Документ для клиента обновляется сразу','Эскиз, позиции и итог — без валюты'); pg.evaluate("window.scrollTo({top:0,behavior:'smooth'})"); w(800); hl('#paperbox'); pg.mouse.move(980,520,steps=30); w(1800)
    pg.evaluate("window.scrollTo({top:650,behavior:'smooth'})"); w(2600); pg.evaluate("window.scrollTo({top:0,behavior:'smooth'})")
    seg('door2'); see('#addDoor'); cap('Несколько дверей','«+ Добавить дверь» копирует последнюю','Меняйте только то, что отличается'); hl('#addDoor'); w(700); click('#addDoor'); w(700)
    see('#d1_coll'); sel_opt('#d1_coll',value='Фьюжн'); see('#d1_H'); hl('#d1_H'); typ('#d1_H','2100'); typ('#d1_qty','3')
    seg('collapse'); see('#doors .door:nth-child(2) .dh'); cap('Несколько дверей','Нажмите на заголовок, чтобы свернуть карточку','Видны модель, размер и сумма'); hl('#doors .door:nth-child(2) .dh'); w(600); click('#doors .door:nth-child(2) .dh'); w(500); see('#doors'); hl('#doors')
    seg('extras'); see('#addExtra'); cap('Шаг 3','Фурнитура, доставка, монтаж — своими строками','Галочка «С наценкой» добавит вашу наценку'); hl('#addExtra'); w(600); click('#addExtra'); w(300)
    typ('#e0_n','Ручка с магнитным замком'); typ('#e0_u','компл.'); typ('#e0_q','4'); typ('#e0_p','4500'); hl('#extras')
    seg('free'); click('#addExtra'); typ('#e1_n','Доставка до объекта'); typ('#e1_q','1'); typ('#e1_p','0'); cap('Шаг 3','Цена 0 — в документе будет «бесплатно»','')
    seg('result'); pg.evaluate("window.scrollTo({top:0,behavior:'smooth'})"); w(800); cap('Шаг 4','Итог для клиента и кнопка «Скачать PDF»','Ниже — сумма по прайсу без наценки, только для вас'); hl('.sum'); move('#savePdf')
    seg('hist'); cap('История','«В историю» — сохранить расчёт','Его можно открыть и изменить позже'); hl('#saveHist'); click('#saveHist'); w(1500); hl('#tabHist'); click('#tabHist'); w(600); hl('#histList')
    seg('end'); click('#tabCalc'); hl(None); pg.evaluate('V.nocap()'); w(600)
    pg.evaluate("V.full('Готово','Клиент → двери → доп. позиции → проверка → PDF','Перед отправкой сверьте дату прайса, рисунок, размеры и погонаж',true)")
    seg(None); w(1200)
    vid=pg.video.path(); ctx.close(); b.close()
    shutil.copy(vid,'raw.webm')
    json.dump(MARK,open('marks.json','w')); print(MARK)
