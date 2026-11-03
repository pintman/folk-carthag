# Proposal

## Why

Folk auf carthag kann Bilder, animierte GIFs und Sprites projizieren, aber keine Videos.
Für Unterricht und Demos soll eine gedruckte Karte ein Video abspielen können – in einem
projizierten Fenster neben der Karte, damit die Karte selbst (Code, Tag) sichtbar bleibt.
Auf carthag sind ffmpeg und ffprobe installiert, Folk bringt selbst keine
Video-Unterstützung mit.

## What Changes

- Neues User-Programm `user-programs/carthag/video.folk`, das den Wish
  `Wish $this plays video "<datei>"` (optional `with side <right|left|above|below> width <länge>`)
  erfüllt:
  - Liegt die Karte, startet das Video; es läuft in Endlosschleife. Wird die Karte
    entfernt, stoppt die Wiedergabe; beim erneuten Auflegen beginnt sie von vorn.
  - Das Bild erscheint in einem Fenster neben der Karte (Standard: rechts), das Lage und
    Drehung der Karte mitmacht.
  - Wiedergabe stumm (kein Ton).
  - Videodateien liegen auf carthag in `~/folk-videos/` (relativer Name) oder werden per
    absolutem Pfad angegeben.
  - Fehlende oder nicht abspielbare Dateien führen zu einer Fehlermeldung an der Karte,
    Folk läuft weiter.
- Dekodierung über einen externen `ffmpeg`-Prozess, der Rohbilder (rgb24) liefert;
  Einlesen der Bilder per kleiner C-Bibliothek im User-Programm.
- README-Abschnitt „Videos abspielen“ in „Eigene Programme schreiben“.

Nicht im Umfang: Ton, Pause/Vor-/Zurückspulen, Fortsetzen an alter Position,
URLs/YouTube (yt-dlp), Sicherung von `~/folk-videos/` per `sync.sh`,
Hardware-Dekodierung.

## Capabilities

### New Capabilities
- `video-playback`: Abspielen von Videodateien, ausgelöst durch eine Karte, als
  projiziertes Fenster neben der Karte.

### Modified Capabilities
<!-- keine -->

## Impact

- Neue Datei: `user-programs/carthag/video.folk` (wird per `sync.sh` gesichert).
- carthag: neues Verzeichnis `~/folk-videos/`; nutzt das installierte Paket `ffmpeg`
  (`ffmpeg`, `ffprobe`). Keine weiteren Pakete, kein Folk-Patch.
- Last: Dekodierung (CPU) und eine Texturübertragung zur GPU pro Videobild.
- `README.md`.
