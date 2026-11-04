# Proposal

## Why

Folk druckt Programme auf carthag im US-Letter-Format (`/PageSize [612 792]`), weil kein Standard-Papierformat festgelegt ist und Upstream dann auf `letter` zurückfällt. Benutzt wird hier aber A4-Papier. Upstream bringt A4 schon mit (`builtin-programs/print/print.folk`), es fehlt nur die lokale Auswahl.

## What Changes

- Neues User-Programm `user-programs/carthag/paper-format.folk` mit `Claim paper format a4 is the default paper format`.
- Damit nutzen Druck aus dem Web-Editor, Druck aus dem Editor auf dem Tisch, Druckvorschau, Kalibrierblatt und `lpr` (`-o media=a4`) automatisch A4.
- README: Hinweis auf das Papierformat und darauf, dass alte Letter-Programme neu gedruckt werden sollten.
- Keine Änderung am Folk-Quellcode (Upstream) und kein neuer Patch in `folk-patches/`.

## Capabilities

### New Capabilities
- `paper-format`: Papierformat, in dem Folk auf carthag Programme und Druckvorschauen erzeugt.

### Modified Capabilities

## Impact

- Betroffen: nur `user-programs/carthag/` und `README.md` in diesem Repo.
- Laufzeit: Upstream-Programme `print.folk`, `print-editor.folk` und `calibration-board.folk` lesen den Claim. Sie werden nicht geändert.
- Bestehende Programme `folk-data/program/0–12` bleiben Letter. Ihre Geometrie in `*.meta.folk` geht von 215,9 mm Blattbreite aus.
- Annahme: Ob über `lpr` oder von Hand aus dem PDF gedruckt wird, ist offen. Der Claim wirkt in beiden Fällen auf das erzeugte PS/PDF.
