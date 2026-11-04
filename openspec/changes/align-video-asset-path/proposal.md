# Proposal

## Why

Videos liegen bisher in `~/folk-videos/` – außerhalb von Folk, ohne Bezug zum Rechner
und ohne Sicherung durch `sync.sh`. Upstream-Folk (`c9aef30`) legt hostspezifische
Medien für `audio.folk` dagegen neben die eigenen Programme in
`user-programs/<host>/audio/`. Video soll sich genauso verhalten, damit eigene
Programme und ihre Medien an einem Ort liegen und gemeinsam gesichert werden.

Bestandsaufnahme Upstream (zur Einordnung):

| Medium | Suchreihenfolge für relative Namen |
|---|---|
| Audio (`builtin-programs/audio.folk`) | `<folk>/user-programs/<host>/audio/` → `<folk>/audio/` → Name unverändert (absolut) |
| Bilder (`builtin-programs/draw/image.folk`) | `~/folk-images/` → `<folk>/` |
| Video (eigenes `video.folk`, heute) | `~/folk-videos/` |

`<folk>` = Arbeitsverzeichnis von Folk (`/home/folk/folk`), `<host>` = `info hostname`.
Upstream ist also selbst nicht einheitlich; Vorbild für Video ist Audio, weil es
hostspezifisch ist und unter `user-programs/` liegt. Der Kommentar in `audio.folk`
nennt fälschlich `assets/sounds/` bzw. `…/sounds/`; unser README hat das übernommen.

## What Changes

- **BREAKING** `video.folk` sucht relative Namen in
  `<folk>/user-programs/<host>/video/`, dann `<folk>/video/`; `~/folk-videos/` wird
  nicht mehr durchsucht. Absolute Pfade bleiben unverändert.
- Fehlermeldung bei fehlender Datei nennt alle durchsuchten Pfade.
- Repo: `folk-videos/` zieht nach `user-programs/carthag/video/` um; damit sichert
  `sync.sh` die Videos automatisch mit (rsync `--delete` über `user-programs/carthag/`).
- carthag: Inhalt von `~/folk-videos/` nach `~/folk/user-programs/carthag/video/`
  verschieben, `~/folk-videos/` danach entfernen.
- README: Video-Abschnitt, Inhaltstabelle und Wiederherstellen-Anleitung anpassen;
  Audio-Pfade auf das tatsächliche Upstream-Verhalten korrigieren
  (`user-programs/<rechner>/audio/` bzw. `<folk>/audio/`).
- Nicht enthalten: Änderungen an Upstream (`audio.folk`-Kommentar, Bilder-Pfad),
  Umzug von `~/folk-images/`.

## Capabilities

### New Capabilities
<!-- keine -->

### Modified Capabilities
- `video-playback`: Requirement „Auflösung des Dateinamens“ – neue Suchreihenfolge
  nach Audio-Vorbild statt `~/folk-videos/`; Szenario „Karte wird aufgelegt“ verweist
  auf den neuen Ort; „Datei fehlt“ nennt die durchsuchten Pfade.

## Impact

- `user-programs/carthag/video.folk` (Pfadauflösung, Kopfkommentar)
- `folk-videos/` → `user-programs/carthag/video/` (git mv, ~8,7 MB, keine Neuaufnahme)
- `README.md`
- carthag: Dateiumzug; bestehende Karten mit absolutem Pfad unter
  `/home/folk/folk-videos/` funktionieren danach nicht mehr und müssen angepasst werden
- `sync.sh` bleibt unverändert; fswatch ignoriert Nicht-`.folk`-Dateien, `boot.folk`
  lädt nur `user-programs/<host>/*.folk` – Videodateien lösen also keine Reloads aus
