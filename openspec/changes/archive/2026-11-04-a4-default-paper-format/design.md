# Design

## Context

Upstream definiert in `builtin-programs/print/print.folk` die Formate `letter`, `a4` und `indexcard`. Alle Verbraucher fragen das Format mit `QueryOne! paper format /./ is the default paper format -default letter` ab:

- `print/print.folk:233`: Web-Editor-Druck
- `print/print.folk:369`: `lpr -o media=…`, ohne `-default`
- `editor/print-editor.folk:10,41`: Editor-Druck und Vorschau
- `calibrate/calibration-board.folk:57`: Kalibrierblatt

Auf carthag gibt es keinen solchen Claim, deshalb greift `letter`. User-Programme in `user-programs/carthag/` lädt Folk beim Start. Mit `folk-patches/fswatch-user-programs.patch` werden sie bei Änderungen neu geladen.

## Goals / Non-Goals

**Goals:**
- A4 als Standard nur über einen Claim in einem eigenen User-Programm festlegen.

**Non-Goals:**
- Upstream-Default von `letter` auf `a4` ändern.
- Bestehende Programme 0–12 automatisch umrechnen oder neu drucken.
- Standarddrucker einrichten. Das ist ein eigenes Thema, die Datei kann ihn später aufnehmen.

## Decisions

1. **Eigenes User-Programm `paper-format.folk`.** Statt Web-Setup (`hold/web__setup.folk`) oder Patch.
   - Versioniert und lesbar, `sync.sh` und die Restore-Anleitung decken es schon ab.
   - Web-Setup: Es funktioniert auch, aber die Einstellung ist dort in serialisierten Einträgen versteckt.
   - Patch: Er widerspricht dem Ziel „keine Upstream-Änderung“ und muss nach jedem Update erneut angewendet werden.
2. **`Claim` statt `Assert`.** Der Claim lebt, solange das Programm geladen ist. Entfernt man die Datei, gilt wieder `letter`, ohne dass Zustand zurückbleibt.
3. **Alte Programme bleiben unverändert.** Ihre `meta.folk`-Geometrie passt zu dem Letter-PS, mit dem sie erzeugt wurden. Wer sie auf A4 korrekt nutzen will, druckt sie neu.

## Risks / Trade-offs

- [Zweiter Claim, etwa zusätzlich im Web-Setup, lässt `QueryOne!` scheitern] → Beim Einrichten prüfen, dass nur `paper-format.folk` das Format festlegt.
- [Alte Letter-Programme liegen auf A4-Papier mit leicht versetzter Projektion] → README-Hinweis, bei Bedarf neu drucken.
- [Eine vorhandene Druck-Kalibrierung (`the calibrated print scale/translation`) wurde mit Letter gemessen] → Prüfen, ob sie existiert. Falls ja, mit A4-Kalibrierblatt neu messen.
- [Manueller Druck aus dem PDF mit „An Seite anpassen“ skaliert] → Im README „Tatsächliche Größe / 100 %“ empfehlen.

## Migration Plan

1. Datei anlegen und nach carthag rsyncen, wie in der README unter „Wiederherstellen“ beschrieben.
2. Wird sie nicht automatisch neu geladen, Folk neu starten.
3. Rollback: Datei löschen. Danach gilt wieder `letter`.
