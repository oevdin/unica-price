"""Озвучка реплик из script.py голосом Piper ru_RU-irina-medium -> vo/<ключ>.wav и vo/dur.json
Голос: https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-ru_RU-irina-medium.tar.bz2
Установка: pip install piper-tts"""
import subprocess, json, os, sys
exec(open('script.py').read())
M = sys.argv[1] if len(sys.argv) > 1 else 'vits-piper-ru_RU-irina-medium/ru_RU-irina-medium.onnx'
os.makedirs('vo', exist_ok=True); dur = {}
for k, t in S:
    subprocess.run(['python3', '-m', 'piper', '-m', M, '-f', f'vo/{k}.wav', '--sentence_silence', '0.3'], input=t.encode(), check=True)
    dur[k] = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'vo/{k}.wav']).strip())
json.dump(dur, open('vo/dur.json', 'w'))
