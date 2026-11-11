# Esempio: Reel #11 «Datti del tu» (3 ottobre 2026)

- `reel11_edl.json`: tagli sugli 8 clip. Note: in `102401` la prima ripresa si interrompe (si tiene da 7,45 s) e la frase "ti parli come un allenatore" è tolta perché il copione corto la eliminava; in `102436` i primi 3 s sono una partenza falsa; in `102504` sono tolti i tre esempi e si usa la seconda ripresa di "quando arriva il punto duro".
- `reel11_overlays.json`: titoli sulla timeline del montato (109,5 s).
- `reel11_caption.txt`: caption pubblicata.
- Feedback di Federico: "risultato spettacolare". Da migliorare: più zoom in/out, sottotitoli più in basso (erano sulla bocca). Entrambi già applicati in `style.json`.

# Esempio: Reel #12 «Lascio spazio ai giovani» (6 ottobre 2026)

- 7 clip puliti, senza ripetizioni: un pezzo per blocco; domanda e CTA 2 nello stesso clip.
- `ass` lanciato con `--keywords "test|giudizio|rispetto|colpa|guardato|saggezza|giovani" --fix domandi=domande test=TEST test,=TEST,`; poi "te lo mando" corretto a mano in "te le mando" in rough_words.json (su richiesta di Federico). Titolo d'apertura ingrandito con `{\fs92}` senza virgolette: Federico vuole il titolo del reel ben visibile all'inizio.
- Inquadratura diversa (siepe, volto più in alto): titoli e sottotitoli con lo stile standard funzionano lo stesso.

# Esempio: Reel #13 «Quanto veloce cammini» (11 ottobre 2026)

- Gancio girato camminando, all'aperto (senza i segni di nastro suggeriti dal copione).
- `092007`: falsa partenza ("…scrivimi qui sotto quanto e—"), tenuta la seconda ripresa da 6,05 s. Tolto "Allora," in `091755`.
- Whisper sul montato aveva perso "Nel 1999 hanno": il pezzo audio era intatto, corretto a mano in `rough_words.json` dopo una ritrascrizione mirata. Sempre verificare i buchi della trascrizione prima di toccare i tagli.
- Inquadratura più stretta: titoli coprivano la fronte con lo zoom → `margin_v` dei titoli portato a 170 (sed su `reel.ass`).

# Esempio: Reel #14 «Male che vada…» (14 ottobre 2026)

- 7 clip puliti. Tolto "Allora," iniziale in `120030` (gli capita spesso a inizio clip: toglilo).
- Sottotitoli corretti a mano: "fallici"→"fallisci", "i due ricercatrici"→"le due", "te lo mando" (esercizi)→"te li mando".
- Titolo di copertina dato da Federico: "MALE CHE VADA… / È UNA TRAPPOLA" (`{\fs92}`, dal primo fotogramma).
- Inquadratura molto stretta → titoli a `margin_v` 170.

# Esempio: Reel #15 «I cruciverba non bastano» (14 ottobre 2026)

- Cartella Drive "Viaggio Cina – Reel 15-18" con clip di più reel + Google Docs (copione, testi a schermo, caption, copertina): leggi i Docs con `read_file_content` e usa la caption di Federico così com'è.
- Clip mescolati con "Storie" caricate per errore: escluse per contenuto (racconto del viaggio "Speriamo bene", "Grazie a tutti", file `_bsl` già verticali e duplicati) e un clip-segnaposto "prova di registrazione per il reel 16".
- `170846` (90 s): partenza falsa a inizio clip e prima ripresa di "Alla fine la memoria…" balbettata → tenuta la seconda (68,6 s).
- "scrivi in memoria" (Whisper) → "SCRIVI MEMORIA".

# Esempi: Reel #16, #17, #18 (15 ottobre 2026)

- #16: blocco ACHIEVE rigirato il giorno dopo con un'altra maglia → raggruppati i clip nuovi in un unico tratto (usata anche la nuova ripresa di "Come me lo spiego io"). La frase "Uno di questi è l'udito" non è stata registrata: coperta dal titolo «LANCET 2024 · 14 FATTORI / UNO È L'UDITO».
- #17: `112040` con due riprese interne (Holt-Lunstad e "perché non la chiami?", "Chi si faceva vivo"): tenute le seconde.
- #18: "e li mando" → "TE LI MANDO".
- Nuovo stile copertina `{COVER}` (Anton nero su bianco, al posto del font "Strong" di Edits).
- #16 rivisto su segnalazione di Federico: "Nel campione… nel campione complessivo" (tolto `111544` 11,0–12,5) e "e per… e per decidere" (`171855` diviso in 0–5,95 + 7,80–). #17: tolti 0,7 s di rumore prima del gancio. Da qui nasce `scripts/check_repeats.py`.

# Esempio: Reel #19 «La sera prima di partire volevo rinunciare» (2 novembre 2026)

- Nuovo modo di girare: treppiede, volto in basso, parete bianca sopra → `style_override.json` nella cartella di lavoro: sottotitoli in alto (`align` 8, `margin_v` 560) e zoom puntati più in basso (`face_y` 0.62).
- Federico NON vuole il titolo di copertina (lo aggiunge lui): niente `{COVER}`, primi 3 s senza titoli in alto.
- Sottotitoli karaoke (`ass --karaoke`): ogni parola diventa gialla quando la pronuncia.
- "non devi guidare" era un errore di Whisper: la trascrizione letterale dà "deve". Tolto "Allora," iniziale.

# Esempio: Reel #20 «Entri in una stanza e non sai più perché» (7 novembre 2026)

- Più dinamico (49 pezzi in 2:08), viso schiarito con `grade`, copertina a 3 frasi dentro la zona sicura, popup della copertina del quaderno da "Martedì esce il mio quaderno" a "te lo mando appena esce".
- Tagli fini: "Poi ~~parte~~ la parte onesta" (il primo taglio lasciava la coda di "parte", sentita come "dalla": controlla sempre la trascrizione del montato), "più ~~di~~ una porta", "~~Ovvio,~~ parlane". Whisper aveva inventato un "Grazie." finale: rimosso da `rough_words.json`.
- Controllo zona sicura: `ffmpeg -ss 1 -i REEL.mp4 -frames:v 1 -vf "drawbox=y=0:w=iw:h=270:color=red@0.25:t=fill,drawbox=y=ih-480:w=iw:h=480:color=red@0.25:t=fill" safe.png`.

# Esempio: Reel #22 «Sabato compio 70 anni» (11 novembre 2026) — primo con b-roll
- Brief .md di Federico (su Drive) + teleprompter. 5 clip parlati (frontale 1080p) + 8 b-roll (posteriore 4K, `rotation -90`; Whisper ci "sente" frasi inventate: ignorale).
- `brolls.json`: `[{clip, out_start, out_end, src_start, grade, blur:[[x,y,w,h]]}]` sulla timeline finale: la voce continua, il video passa al b-roll (zoom lento). Mai b-roll su numeri, battute chiave e "Avrei potuto dire: ormai".
- Dati personali: targhe visibili dalla finestra → `blur` sulla fascia della finestra (0,0,1080,760). Komoot non usato: mostra 18 km (contraddice "oltre 100 km") e la zona di casa.
- Bilanciamento del bianco caldo (parete Cr 132 / Cb 117, viso Cr 152): `colorbalance` verso il blu + `curves` → viso Y 119→134, Cr 145; parete quasi neutra.
- Copertina «70 / ormai?» con `{\fs220}`/`{\fs96}` dentro `{COVER}`, numeri grandi «1», «2», «3» 1 s e «1 2 3» su "Tre volte". `REEL22_copertina.jpg` = fotogramma senza sottotitoli (ass con la sola copertina).
