"""Сводит озвучку (vo/*.wav) с записью экрана (raw.webm) по меткам marks.json -> instruction.mp4"""
import json, subprocess
M = json.load(open('marks.json'))
args = ['ffmpeg', '-y', '-i', 'raw.webm']
flt = []
for i, (k, t) in enumerate(M):
    args += ['-i', f'vo/{k}.wav']
    ms = int(t * 1000)
    flt.append(f'[{i+1}:a]adelay={ms}|{ms},aresample=48000[a{i}]')
flt.append(''.join(f'[a{i}]' for i in range(len(M))) + f'amix=inputs={len(M)}:normalize=0:dropout_transition=0,loudnorm=I=-16:TP=-1.5:LRA=11[aout]')
args += ['-filter_complex', ';'.join(flt), '-map', '0:v', '-map', '[aout]', '-c:v', 'libx264', '-crf', '22',
         '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', '-shortest', 'instruction.mp4']
subprocess.run(args, check=True)
