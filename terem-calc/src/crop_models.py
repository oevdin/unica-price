"""Вырезает отдельные двери из картинки-линейки коллекции.
usage: python3 crop_models.py strip.jpg outdir
Сохраняет outdir/door_0.png, door_1.png ... слева направо (без подписей)."""
import sys, os
from PIL import Image
import numpy as np
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
im = Image.open(src).convert('L'); a = np.array(im)
h, w = a.shape
dark = a < 200
# строки с рисунком: ищем нижнюю границу дверей (подписи отделены пустой полосой)
rows = dark.any(axis=1)
# первая длинная пустая полоса снизу вверх отделяет подписи
ys = np.where(rows)[0]; top = ys[0]
gaps = [y for y in range(top, h) if not rows[y]]
door_bottom = gaps[0] if gaps else h
body = dark[top:door_bottom]
cols = body.any(axis=0)
segs, start = [], None
for x in range(w):
    if cols[x] and start is None: start = x
    if not cols[x] and start is not None:
        if x - start > 15: segs.append((start, x))
        start = None
if start is not None: segs.append((start, w))
for i, (x0, x1) in enumerate(segs):
    im.crop((x0, top, x1, door_bottom)).save(f'{out}/door_{i}.png')
    print(i, x0, x1, door_bottom - top)
