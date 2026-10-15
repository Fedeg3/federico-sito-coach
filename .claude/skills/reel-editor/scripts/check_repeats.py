#!/usr/bin/env python3
"""Controllo parole ripetute (obbligatorio prima della consegna).

Whisper "pulisce" le ripetizioni ("e per… e per decidere", "nel campione… nel campione"):
per trovarle ritrascrive in modo letterale le due parti attorno a OGNI pausa accorciata
(stesso clip, pezzi non contigui) e attorno a ogni giunta fra clip, e segnala le parole
che durano troppo nel montato (spesso nascondono una ripetizione).

Uso: python3 -I check_repeats.py <work>   (dopo `reel.py cut` e `reel.py words`)
Leggi l'output: se le prime parole di DOPO ripetono le ultime di PRIMA, sposta il taglio.
"""
import json, subprocess, sys
from faster_whisper import WhisperModel

W = sys.argv[1]
m = WhisperModel('large-v3-turbo', device='cpu', compute_type='int8', download_root=f'{W}/wmodels')
P = "Esitazioni e ripetizioni trascritte parola per parola: e e, per per, il il."


def tr(f, a, b):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{max(a, 0):.2f}', '-to', f'{b:.2f}', '-i', f,
                    '-ac', '1', '-ar', '16000', f'{W}/_chk.wav'])
    s, _ = m.transcribe(f'{W}/_chk.wav', language='it', vad_filter=False,
                        condition_on_previous_text=False, initial_prompt=P)
    return ' '.join(x.text.strip() for x in s)


pcs = json.load(open(f'{W}/pieces.json'))
print('== Pause accorciate e giunte (PRIMA | DOPO)')
for p, q in zip(pcs, pcs[1:]):
    if p[0] == q[0] and q[1] - p[2] <= 0.05:
        continue                                   # stesso flusso continuo: niente taglio
    before = tr(f'{W}/raw/{p[0]}.mp4', p[2] - 1.6, p[2])
    after = tr(f'{W}/raw/{q[0]}.mp4', q[1], q[1] + 1.6)
    print(f'{p[0]} {p[2]:.2f} | {q[0]} {q[1]:.2f}   PRIMA: {before!r:48} DOPO: {after!r}')

print('\n== Parole troppo lunghe nel montato (possibili ripetizioni nascoste)')
w = json.load(open(f'{W}/rough_words.json'))
for x, y in zip(w, w[1:]):
    t = x[2].strip(); gap = y[0] - x[0]
    if gap > max(0.9, 0.12 * len(t.strip('.,?!')) + 0.55) and not any(ch.isdigit() for ch in t):
        print(f'{x[0]:7.2f}s  {t!r} dura {gap:.2f}s → riascolta {x[0]-1:.1f}–{y[0]+1:.1f}s')
