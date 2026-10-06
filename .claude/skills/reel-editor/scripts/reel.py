#!/usr/bin/env python3
"""Pipeline di montaggio reel per Federico (Instagram 9:16).

Sottocomandi (tutti lavorano nella cartella --work, default /tmp/reel):
  download   ID:nome ...           scarica i clip da Drive (cartella condivisa "chiunque abbia il link")
  transcribe                       trascrive raw/*.mp4 con timestamp per parola -> words.json
  cut        edl.json              monta la rough cut (senza grafica) -> rough.mp4, pieces.json
  words                            ritrascrive rough.mp4 -> rough_words.json (verifica + timing sottotitoli)
  ass        overlays.json         genera reel.ass (sottotitoli + titoli)
  render     [--name NOME]         render finale con zoom dinamici, grafica, audio masterizzato
  export     [--name NOME]         versione <30 MB per invio in chat (two-pass)
  preview    t1 t2 ...             contact sheet dei fotogrammi ai secondi indicati -> preview.png
"""
import argparse, glob, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
STYLE = json.load(open(os.path.join(HERE, '..', 'style.json')))


def sh(*a, **k):
    return subprocess.run(list(a), check=True, **k)


def W(p):
    return os.path.join(ARGS.work, p)


# ---------------------------------------------------------------- download
def cmd_download(ids):
    os.makedirs(W('raw'), exist_ok=True)
    for item in ids:
        fid, name = item.split(':', 1)
        out = W(f'raw/{name}.mp4')
        sh('curl', '-sS', '-L', '-o', out, '-w', f'{name} %{{http_code}} %{{size_download}} %{{content_type}}\n',
           f'https://drive.usercontent.google.com/download?id={fid}&export=download&confirm=t')


# ---------------------------------------------------------------- whisper
def _model():
    from faster_whisper import WhisperModel
    return WhisperModel(STYLE['whisper_model'], device='cpu', compute_type='int8',
                        download_root=W('wmodels'), cpu_threads=os.cpu_count())


def _transcribe(m, path, prompt):
    segs, _ = m.transcribe(path, language='it', word_timestamps=True, beam_size=5, initial_prompt=prompt)
    return [[round(w.start, 2), round(w.end, 2), w.word] for s in segs for w in s.words]


def cmd_transcribe(prompt):
    m = _model(); out = {}
    for f in sorted(glob.glob(W('raw/*.mp4'))):
        n = os.path.basename(f)[:-4]
        out[n] = _transcribe(m, f, prompt)
        print(n, ' '.join(f'[{w[0]}]{w[2]}' for w in out[n]), flush=True)
        print('   silenzi:', _silences(f), flush=True)
    json.dump(out, open(W('words.json'), 'w'), ensure_ascii=False)


def cmd_words(prompt):
    ws = _transcribe(_model(), W('rough.mp4'), prompt)
    json.dump(ws, open(W('rough_words.json'), 'w'), ensure_ascii=False)
    print(' '.join(f'[{w[0]}]{w[2]}' for w in ws))


# ---------------------------------------------------------------- cut
def _silences(path, noise='-38dB', d=0.32):
    o = subprocess.run(['ffmpeg', '-nostats', '-i', path, '-af', f'silencedetect=noise={noise}:d={d}', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    s = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', o)]
    e = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', o)]
    return [(round(a, 2), round(b, 2)) for a, b in zip(s, e)]


def _pieces(edl):
    """EDL [clip, start, end, blocco] -> pezzi con le pause interne accorciate."""
    pieces, cache = [], {}
    pad = STYLE['pause_keep_s']
    for c, a, b, blk in edl:
        sil = cache.setdefault(c, _silences(W(f'raw/{c}.mp4')))
        cur = a
        for s, e in sil:
            if s > a and e < b:
                pieces.append([c, cur, s + pad, blk]); cur = e - pad
        pieces.append([c, cur, b, blk])
    return [p for p in pieces if p[2] - p[1] > 0.05]


def _zoom_plan(pieces):
    """Assegna a ogni pezzo un movimento di camera.
    Regola (richiesta di Federico): zoom in/out frequenti mentre parla, non solo sui jump cut.
    Ciclo: push-in lento -> punch fisso -> pull-out lento -> statico largo; si riparte a ogni blocco
    con un push-in. I pezzi lunghi (> long_piece_s) vengono spezzati per avere un movimento ogni ~4 s."""
    Z = STYLE['zoom']
    cycle = ['push', 'punch', 'pull', 'wide']
    out, prev_blk, k = [], None, 0
    for c, a, b, blk in pieces:
        segs = [(a, b)]
        if b - a > Z['long_piece_s']:
            n = int((b - a) // Z['target_shot_s']) or 1
            step = (b - a) / n
            segs = [(a + i * step, a + (i + 1) * step) for i in range(n)]
        for sa, sb in segs:
            if blk != prev_blk:
                k = 0
            out.append([c, round(sa, 3), round(sb, 3), blk, cycle[k % len(cycle)]])
            k += 1; prev_blk = blk
    return out


def _vf_zoom(mode, d):
    Z = STYLE['zoom']; fy = Z['face_y']
    if mode == 'wide':
        return 'scale=1080:1920'
    if mode == 'punch':
        z = Z['punch']
        return f'crop=iw/{z}:ih/{z}:(iw-ow)/2:(ih-oh)*{fy},scale=1080:1920'
    # zoom continuo con zoompan; upscale 2x prima per evitare il tremolio da arrotondamento dei pixel
    z0, z1 = (1.0, Z['push']) if mode == 'push' else (Z['push'], 1.0)
    n = max(int(d * 30), 1)
    zt = f'{z0}+({z1}-{z0})*min(in/{n}\\,1)'
    return (f"fps=30,scale=2160:3840,zoompan=z='{zt}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)*{fy}'"
            f":d=1:s=1080x1920:fps=30")


def _dur(a, b):
    """Durata del pezzo arrotondata a fotogrammi interi (30 fps): niente deriva dei sottotitoli."""
    return max(round((b - a) * 30), 1) / 30


def _render(plan, out, ass=None, final=False):
    """Un pezzo alla volta (poca RAM: un unico filtergraph con 25 trim va in OOM), poi concat."""
    import concurrent.futures as cf
    os.makedirs(W('parts'), exist_ok=True)
    tag = 'f' if final else 'r'

    def one(i):
        c, a, b, _, mode = plan[i]
        d = _dur(a, b)
        import hashlib  # pezzo già pronto con gli stessi parametri -> riuso (correzioni di testo veloci)
        h = hashlib.md5(json.dumps([c, a, b, mode, STYLE['zoom']]).encode()).hexdigest()[:8]
        p = W(f'parts/{tag}{i:03d}_{h}.mkv')
        if os.path.exists(p):
            return p
        sh('ffmpeg', '-v', 'error', '-y', '-ss', f'{a:.3f}', '-i', W(f'raw/{c}.mp4'), '-t', f'{d:.4f}',
           '-vf', f'{_vf_zoom(mode, d)},fps=30,setsar=1',
           '-af', f'afade=t=in:d=0.02,afade=t=out:st={max(d - 0.03, 0):.3f}:d=0.03,aresample=48000',
           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', '-pix_fmt', 'yuv420p',
           '-c:a', 'pcm_s16le', '-ac', '1', p)
        return p
    with cf.ThreadPoolExecutor(2) as ex:
        parts = list(ex.map(one, range(len(plan))))
    lst = W(f'parts/{tag}.txt')
    open(lst, 'w').write(''.join(f"file '{p}'\n" for p in parts))
    vpost = 'eq=contrast=1.04:saturation=1.08'
    if ass:
        vpost += f",subtitles={ass}:fontsdir={W('fonts')}"
    apost = ('highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,'
             'loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000')
    venc = (['-preset', 'slow', '-crf', '20', '-maxrate', '12M', '-bufsize', '24M'] if final
            else ['-preset', 'veryfast', '-crf', '22'])
    sh('ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-vf', vpost, '-af', apost,
       '-c:v', 'libx264', *venc, '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
       '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', out)


def cmd_cut(edl_path):
    edl = json.load(open(edl_path))
    pieces = _pieces(edl)
    plan = _zoom_plan(pieces)
    json.dump(plan, open(W('pieces.json'), 'w'))
    for p in plan:
        p[4] = 'wide'          # la rough cut serve solo per la trascrizione: niente zoom
    _render(plan, W('rough.mp4'))
    t, marks = 0, []
    for c, a, b, blk, _ in json.load(open(W('pieces.json'))):
        marks.append([round(t, 2), blk, c]); t += _dur(a, b)
    json.dump(marks, open(W('marks.json'), 'w'))
    print(f'{len(plan)} pezzi, durata {t:.1f}s'); print(marks)


# ---------------------------------------------------------------- ass
def _ts(t):
    return f'{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}'


def cmd_ass(ov_path, keywords=None, fix=()):
    S = STYLE['subs']; T = STYLE['titles']
    raw = json.load(open(W('rough_words.json')))
    fixes = dict(S.get('fixes', {}))
    fixes.update(dict(f.split('=', 1) for f in fix))
    ws = []
    for s, e, t in raw:
        t = t.strip()
        if t.startswith("'") and ws:
            ws[-1][1] = e; ws[-1][2] += t
        else:
            ws.append([s, e, fixes.get(t, t)])
    kw = S['keywords_regex'] if not keywords else S['keywords_regex'][:-2] + '|' + keywords + ')$'
    key = re.compile(kw, re.I)
    chunks, cur = [], []
    for i, w in enumerate(ws):
        cur.append(w)
        nxt = ws[i + 1] if i + 1 < len(ws) else None
        txt = ' '.join(x[2] for x in cur)
        if re.search(r'[.,?!]$', w[2]) or len(cur) >= S['max_words'] or len(txt) >= S['max_chars'] \
                or not nxt or nxt[0] - w[1] > 0.35:
            chunks.append(cur); cur = []
    Y, Wh = r'{\c&H00D7FF&}', r'{\c&HFFFFFF&}'
    ev = []
    for k, c in enumerate(chunks):
        st = c[0][0]
        en = min(c[-1][1] + 0.15, chunks[k + 1][0][0] if k + 1 < len(chunks) else c[-1][1] + 0.6)
        parts = []
        for w in c:
            t = w[2].upper().rstrip(',.')
            core = re.sub(r'[^\wÀ-ÿ]', '', t)
            parts.append(Y + t + Wh if key.match(core) else t)
        ev.append(f"Dialogue: 0,{_ts(st)},{_ts(en)},Sub,,0,0,0,,{{\\fad(40,0)}}{' '.join(parts)}")
    for a, b, t in json.load(open(ov_path)):
        t = t.replace('{Y}', Y).replace('{W}', Wh).replace('{STRIKE}', r'{\s1\alpha&H60&}') \
             .replace('{/STRIKE}', r'{\s0\alpha&H00&}').replace('\n', '\\N')
        ev.append(f'Dialogue: 1,{_ts(a)},{_ts(b)},Title,,0,0,0,,{{\\fad(120,80)}}{t}')
    hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,{STYLE['font']},{S['size']},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,1,0,1,7,3,2,80,80,{S['margin_v']},1
Style: Title,{STYLE['font']},{T['size']},&H00FFFFFF,&H00FFFFFF,&H28000000,&H28000000,0,0,0,0,100,100,1,0,3,22,0,8,60,60,{T['margin_v']},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    open(W('reel.ass'), 'w').write(hdr + '\n'.join(ev) + '\n')
    print(len(chunks), 'blocchi di sottotitoli,', len(ev) - len(chunks), 'titoli')


# ---------------------------------------------------------------- render/export
def cmd_render(name):
    plan = json.load(open(W('pieces.json')))
    out = W(f'{name}.mp4')
    _render(plan, out, ass=W('reel.ass'), final=True)
    print(out)


def cmd_export(name, outdir):
    src = W(f'{name}.mp4')
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', src],
                               capture_output=True, text=True).stdout)
    vk = int((28 * 8 * 1024) / dur - 140)          # ~28 MB totali, audio 128k
    vk = min(vk, 6000)
    out = os.path.join(outdir, f'{name}_IG.mp4')
    log = W('pass')
    sh('ffmpeg', '-v', 'error', '-y', '-i', src, '-c:v', 'libx264', '-preset', 'slower', '-b:v', f'{vk}k',
       '-pass', '1', '-passlogfile', log, '-an', '-f', 'null', '/dev/null')
    sh('ffmpeg', '-v', 'error', '-y', '-i', src, '-c:v', 'libx264', '-preset', 'slower', '-b:v', f'{vk}k',
       '-pass', '2', '-passlogfile', log, '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
       '-c:a', 'aac', '-b:a', '128k', out)
    print(out, os.path.getsize(out) // 1024 // 1024, 'MB')


def cmd_preview(times, src):
    src = src or W('rough.mp4')
    tiles = []
    for i, t in enumerate(times):
        p = W(f'_pv{i}.png'); tiles.append(p)
        sh('ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', src, '-frames:v', '1', '-vf', 'scale=288:-1', p)
    args = sum([['-i', p] for p in tiles], [])
    sh('ffmpeg', '-v', 'error', '-y', *args, '-filter_complex', f'hstack={len(tiles)}' if len(tiles) > 1 else 'null',
       W('preview.png'))
    print(W('preview.png'))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--work', default='/tmp/reel')
    sp = ap.add_subparsers(dest='cmd', required=True)
    sp.add_parser('download').add_argument('ids', nargs='+')
    for c in ('transcribe', 'words'):
        sp.add_parser(c).add_argument('--prompt', default=STYLE['whisper_prompt'])
    sp.add_parser('cut').add_argument('edl')
    p = sp.add_parser('ass'); p.add_argument('overlays')
    p.add_argument('--keywords', help='parole chiave extra in giallo, es. "test|giudizio"')
    p.add_argument('--fix', nargs='*', default=[], help='correzioni Whisper, es. domandi=domande')
    for c in ('render', 'export'):
        p = sp.add_parser(c); p.add_argument('--name', default='reel')
        if c == 'export':
            p.add_argument('--outdir', default='.')
    p = sp.add_parser('preview'); p.add_argument('times', nargs='+', type=float); p.add_argument('--src')
    ARGS = ap.parse_args()
    os.makedirs(ARGS.work, exist_ok=True)
    {'download': lambda: cmd_download(ARGS.ids),
     'transcribe': lambda: cmd_transcribe(ARGS.prompt),
     'words': lambda: cmd_words(ARGS.prompt),
     'cut': lambda: cmd_cut(ARGS.edl),
     'ass': lambda: cmd_ass(ARGS.overlays, ARGS.keywords, ARGS.fix),
     'render': lambda: cmd_render(ARGS.name),
     'export': lambda: cmd_export(ARGS.name, ARGS.outdir),
     'preview': lambda: cmd_preview(ARGS.times, ARGS.src)}[ARGS.cmd]()
