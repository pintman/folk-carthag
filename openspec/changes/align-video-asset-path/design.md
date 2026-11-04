# Design

## Context

Siehe proposal.md – Why (Bestandsaufnahme Upstream). Relevant für den Ansatz:

- Upstream `audio.folk` (`resolveSoundPath`) nutzt `[pwd]` als Folk-Verzeichnis und
  `[info hostname]` als Host; `boot.folk` verwendet denselben Hostnamen für
  `user-programs/<host>/*.folk`. Folk läuft auf carthag mit `pwd` = `/home/folk/folk`.
- `boot.folk` lädt nur `user-programs/<host>/*.folk` (keine Unterordner), `fswatch.folk`
  ignoriert alles ohne Endung `.folk` → Videodateien in `user-programs/carthag/video/`
  werden weder geladen noch lösen sie Reloads aus.
- `sync.sh` spiegelt `user-programs/carthag/` mit `--delete` ins Repo; ein Unterordner
  `video/` wird damit automatisch gesichert.

## Goals / Non-Goals

**Goals:**
- Suchreihenfolge identisch zu Audio (Ordnername `video` analog zu `audio`).
- Fehlermeldung, aus der hervorgeht, wo gesucht wurde.

**Non-Goals:**
- Gemeinsame Resolver-Bibliothek für Audio/Bilder/Video (würde Upstream-Änderung
  erfordern).
- Übergangs-Fallback auf `~/folk-videos/`.

## Decisions

- **Ordnername `video/` (Singular)**: spiegelt `audio/` im Upstream. Alternative
  `videos/` verworfen – wäre wieder eine eigene Konvention.
- **Kein `~/folk-videos/`-Fallback**: Nutzerentscheidung; ein harter Schnitt hält die
  Auflösung gleich zu Audio. Bestehende Videos werden einmalig umgezogen.
- **Resolver lokal in `video.folk`** als kleine Prozedur nach Muster von
  `resolveSoundPath`: absolut (`/…`) → unverändert; sonst Kandidatenliste
  `[pwd]/user-programs/[info hostname]/video/<name>`, `[pwd]/video/<name>`, erster
  existierender gewinnt; keiner → Fehler mit allen Kandidaten. Abweichung zu Audio:
  Audio prüft absolut erst zuletzt und meldet nur den Namen; für Video ist „absolut
  zuerst“ gleichwertig (ein `/…`-Pfad kann in den Kandidaten nicht vorkommen) und die
  Meldung aussagekräftiger.
- **Repo-Umzug per `git mv folk-videos user-programs/carthag/video`**: History bleibt
  erhalten, keine erneute Aufnahme der ~8,7 MB.

## Risks / Trade-offs

- [Karten mit relativem Namen finden ihr Video nicht, solange carthag nicht umgezogen
  ist] → Umzug auf carthag im selben Arbeitsschritt wie das Deployen von `video.folk`.
- [Karten mit absolutem Pfad `/home/folk/folk-videos/…` brechen] → vor Umzug auf carthag
  `grep -l folk-videos ~/folk-data/program/*.folk` prüfen und betroffene Programme
  auf relative Namen umstellen.
- [Nächstes `sync.sh` vor Umzug auf carthag löscht `user-programs/carthag/video/` im
  Repo (rsync `--delete`)] → Reihenfolge: erst carthag umziehen, dann `sync.sh`;
  notfalls aus git-History wiederherstellbar.
- [Große Videos blähen das Repo auf] → akzeptiert; README weist darauf hin, nur kurze
  Beispielclips abzulegen.

## Migration Plan

1. `video.folk` im Repo anpassen, `folk-videos/` → `user-programs/carthag/video/`.
2. Sobald carthag erreichbar: `grep` nach `folk-videos` in `~/folk-data/program/`,
   dann `mkdir -p ~/folk/user-programs/carthag/video && mv ~/folk-videos/* …/video/`,
   `rmdir ~/folk-videos`, neues `video.folk` per rsync übertragen (fswatch lädt neu).
3. `./sync.sh` – erwartet: keine Änderungen an `video/`.

Rollback: `git revert`, Dateien auf carthag zurück nach `~/folk-videos/` verschieben.
