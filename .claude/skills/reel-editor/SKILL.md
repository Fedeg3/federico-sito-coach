---
name: reel-editor
description: Monta i reel Instagram di Federico partendo dai suoi clip grezzi (selfie verticali) e dal copione - tagli, scelta delle riprese, sottotitoli, titoli del copione, zoom dinamici, audio, caption. Usa questo skill ogni volta che Federico dice di aver caricato clip/video per un reel, chiede di "montare", "editare", "fare il reel", "mettere i sottotitoli", o incolla un copione tipo «REEL #N» con blocchi temporizzati (gancio, studio, CTA...).
---

# Reel editor: montaggio dei reel di Federico

Federico (coach di mental training per sportivi over 40/50) gira i reel in selfie, un clip per blocco del copione, e li carica in una cartella **REELS** su Google Drive. Tu consegni l'MP4 pronto da pubblicare più la caption. Il primo reel montato così (#11 «Datti del tu») gli ha fatto risparmiare circa 2 ore; lo stile qui sotto è quello approvato.

## Prerequisiti (verifica subito, prima di tutto il resto)

1. **Rete**: l'ambiente cloud deve consentire `drive.usercontent.google.com`, `drive.google.com`, `huggingface.co`, `*.huggingface.co`, `*.hf.co`, `fonts.googleapis.com`, `fonts.gstatic.com`. Se una chiamata dà 403 dal proxy, spiega a Federico: claude.ai/code → icona nuvola sopra la casella dei messaggi → ingranaggio sull'ambiente → Network access **Custom** → spunta "Also include default list…" → aggiungi i domini.
2. **Drive**: il connettore Drive serve solo a trovare gli ID dei file (`search_files` con `mimeType contains 'video/'` e data recente). NON scaricare i video col connettore (base64 troppo grande): usa `reel.py download`. La cartella deve essere condivisa "Chiunque abbia il link – Visualizzatore" (dal Mac: tasto destro → **Share with Google Drive**, non lo "Share…" di Apple).
3. **Tool**: `pip install faster-whisper`; ffmpeg è già presente. Font Montserrat Black/ExtraBold in `<work>/fonts`:
   `curl -sS -A "Mozilla/4.0" "https://fonts.googleapis.com/css?family=Montserrat:800,900"` → scarica i .ttf indicati. Il nome di famiglia che libass riconosce è `Montserrat Thin Black`.

## Flusso

Script: `scripts/reel.py` (stile in `style.json`, esempio completo in `examples/`). Cartella di lavoro di default `/tmp/reel`.

1. `reel.py download ID:nome ...`: usa come nome l'orario del clip (es. `VID_20261003_101817.mp4` → `101817`).
2. `reel.py transcribe`: stampa la trascrizione parola per parola con i tempi, più i silenzi di ogni clip.
3. **Confronta con il copione** e scrivi `edl.json` = lista `[clip, inizio, fine, blocco]` in ordine di copione. Qui c'è il lavoro vero:
   - Federico spesso **ripete una frase nello stesso clip** (partenza falsa, seconda ripresa). Se tra due parole c'è un buco di secondi o la trascrizione salta, ritrascrivi quel tratto da solo per capire cosa dice. Tieni la ripresa più fluida.
   - Se il copione aggiornato accorcia un blocco (es. togliere esempi) e il clip ha la versione lunga, taglia le frasi in più invece di chiedere di rigirare.
   - Le frasi del copione che **non sono state registrate** non si possono inventare: segnalale a Federico a fine lavoro.
4. `reel.py cut edl.json`: rough cut e `pieces.json` con il piano degli zoom. Poi `reel.py words` per ritrascrivere il montato: **rileggi il testo** e verifica che ogni giunta suoni naturale.
5. Scrivi `overlays.json` = `[inizio, fine, "TESTO"]` sulla timeline del montato, usando i tempi di `rough_words.json`. Markup: `{Y}` giallo, `{W}` bianco, `\n` a capo, `{STRIKE}…{/STRIKE}` barrato. Poi `reel.py ass overlays.json`.
6. `reel.py render --name ReelNN_Titolo` e `reel.py preview <secondi...> --src <work>/ReelNN_Titolo.mp4`: guarda il contact sheet (Read sull'immagine) e controlla posizione dei testi, zoom e volto.
7. `reel.py export --name ReelNN_Titolo --outdir <scratchpad>`: versione da ~28 MB per SendUserFile (limite 30 MB). Instagram ricomprime comunque. Invia anche `ReelNN_caption.txt`.

## Regole di stile (approvate da Federico)

**Montaggio**
- Ordine = copione. Pause interne accorciate (restano 0,12 s per lato). Il gancio parte dalla prima sillaba, senza aria iniziale.
- **Zoom in/out frequenti mentre parla** (richiesta dopo il Reel #11): ogni blocco riparte con un push-in lento; poi il ciclo è punch fisso → pull-out lento → largo statico. I pezzi più lunghi di 6 s vengono spezzati per avere un movimento circa ogni 4 s. Valori in `style.json` → `zoom` (push 1.10, punch 1.12, volto al 40% dell'altezza). Zoom delicati: è un coach over 50, non un gamer.

**Sottotitoli**
- Maiuscolo, Montserrat Black 82, bianco con bordo nero, 2–3 parole per blocco, parole chiave in giallo (`&H00D7FF&`).
- **Posizione: sul petto, sotto la bocca** (`margin_v` 290). Nel Reel #11 erano a 400 e coprivano la bocca: non risalire sopra 300. Controlla sempre nei fotogrammi con zoom punch.
- Correggi a mano le parole sbagliate da Whisper (`subs.fixes`), ma non cambiare quello che Federico ha detto davvero.

**Titoli del copione** (le righe in MAIUSCOLO o tra `backtick` nel copione)
- Riquadro scuro in alto (`margin_v` 240), sopra la tettoia/il cielo, Montserrat Black 70, chiave in giallo.
- Il gancio ha sempre un titolo dal primo fotogramma (es. «DATTI DEL TU»), così il reel ferma lo scroll.
- I numeri dello studio compaiono quando lui li dice. CTA: `SCRIVI {Y}«PAROLA»` quando lo dice.
- Se una frase del copione non è stata detta, adatta il titolo a ciò che dice davvero e segnalalo.

**Audio**: highpass 80 Hz, compressore leggero, loudnorm −14 LUFS / −1,5 dBTP. Musica solo se Federico fornisce il brano (diritti).

**Caption**: italiano, tono di Federico (diretto, onesto sui limiti degli studi), 2 CTA (domanda nei commenti + parola chiave), 8–10 hashtag ciclismo/sport over 50/mental coach. Non inventare dettagli che non ha detto (es. il mezzo, i tempi).

## Consegna e messaggio finale

In italiano e conciso: cosa hai tagliato e perché (soprattutto le riprese scartate), le scelte che deve confermare, le frasi del copione mancanti, e le prossime azioni (guardare, correggere, pubblicare, rimettere privata la cartella). Non modificare il reel dopo la consegna se Federico non lo chiede.
