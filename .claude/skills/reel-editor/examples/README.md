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
