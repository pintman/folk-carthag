# Design

## Context

- carthag: Folk-Repo `/home/folk/folk` (Stand `11121f5`), Jim Tcl, i7-8550U (8 Threads),
  Vulkan-Renderer. ffmpeg 6.1.1 mit `ffprobe` installiert (Ubuntu-Paket `ffmpeg`).
- Folk kennt keine Videos. Relevante Bausteine (alle in `builtin-programs/`):
  - `image/image-lib.folk`: `Image`-Struct (width, height, components, bytesPerRow,
    `uniq`, data), `imageNew`, `imageFree`; per `$cc extend $imageLib` in eigenen
    C-Bibliotheken nutzbar.
  - `camera/usb.folk`: Muster für Bildströme – pro Frame neues `Image`, veröffentlicht mit
    `Hold! -key … Claim … -destructor [list $imageLib imageFree $im]`.
  - `gpu/textures.folk`: `Wish the GPU loads image $im as texture` →
    `the GPU has loaded image $im as texture /gim/`, Textur wird mit dem Claim freigegeben.
  - `draw/image.folk`: GPU-Pipeline `"image"` mit vier frei wählbaren Eckpunkten `a b c d`
    (beliebiges Viereck, also auch gedreht). `Wish to draw an image onto …` selbst ist
    achsenparallel (ignoriert `radians`).
  - `gpu/canvases.folk`: Das Display hat `canvas` und `canvas projection` wie ein Blatt.
  - `decorations/title.folk`: Muster für Zeichnen *neben* einem Blatt – Quad-Ecken in
    Display-Raum (Meter, 3D) via `quadChange`, Projektion auf Projektor-Pixel via
    `$poseLib project`.
  - `unix-commands.folk`: Prozess per `open "|cmd" r`, non-blocking, `On unmatch` mit
    `kill`.
  - Fehleranzeige: `Say $p has error $e with info $opts` (wie in `draw/image.folk`).

## Goals / Non-Goals

**Goals:**
- Ein selbstständiges User-Programm `video.folk`, kein Folk-Patch, keine neuen Pakete.
- Bewährte Folk-Muster (Kamera-Frames, title.folk-Geometrie, unix-commands-Prozess)
  wiederverwenden.

**Non-Goals:**
- Volle Auflösung/Bildrate: Ziel ist ein flüssiges Vorschaufenster, nicht HD.
- Exakte A/V-Synchronisation (kein Ton).

## Decisions

1. **Dekodierung mit `ffmpeg` als Kindprozess, Rohbilder über stdout.**
   `ffmpeg -nostdin -loglevel error -re -stream_loop -1 -i <datei> -an
   -vf scale=W:H,fps=25 -f rawvideo -pix_fmt rgb24 -`.
   `-re` taktet in Echtzeit – Folk muss nicht selbst timen. `-stream_loop -1` spielt
   endlos, `-an` verwirft Ton. Feste Ausgabegröße W×H macht die Framegröße (W·H·3 Byte)
   bekannt.
   *Alternative:* `gst-launch-1.0` (ebenfalls installiert) – umständlichere Pipeline,
   keine eingebaute Schleife (Neustart-Logik nötig).
   *Alternative:* eigener Decoder per libav-C-FFI – mehr Code, Build-Abhängigkeiten.

2. **Videogröße vorab mit `ffprobe` ermitteln**
   (`ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0`),
   dann W×H selbst berechnen: maximal 640 px Breite, Seitenverhältnis erhalten, gerade
   Zahlen. W und H explizit als `scale=W:H` übergeben statt `scale=640:-2`, weil Folk die
   Bytegröße pro Bild exakt kennen muss und ffmpegs eigene Rundung nicht nachgebaut
   werden soll. Liefert ffprobe keinen Videostream → Fehler „nicht abspielbar“ an der
   Karte (Spec „Datei nicht abspielbar“). Datei vorher mit `file exists` prüfen → Fehler
   mit Pfad (Spec „Datei fehlt“).

3. **Einlesen in Jim, Umwandeln in `Image` per kleiner C-Funktion.**
   Prozess wie `unix-commands.folk` mit `open "|ffmpeg …" rb`, `fconfigure
   -blocking 0 -translation binary`. Pro Tick (`When the clock time is /t/`) alle
   verfügbaren Bytes lesen, in einem Puffer sammeln; ist mindestens ein vollständiges
   Bild da, das *neueste* vollständige Bild nehmen (ältere verwerfen, falls Folk
   hinterherhinkt). Eine C-Funktion `frameFromBytes {Jim_Obj* bytes int offset int w int h
   int uniq} Image` kopiert in ein neues `Image` (3 Komponenten, wie Kamera-RGB).
   Veröffentlichung: `Hold! -key [list video $p frame] Claim $p has video frame $im
   -destructor [list $imageLib imageFree $im]`, `uniq` = laufende Bildnummer.
   *Alternative:* Prozess und Lesen komplett in C (fork/exec, read in Image-Puffer) –
   spart Kopie über Jim-Strings; als Optimierung, falls Profiling es verlangt.

4. **Endlosschleife macht ffmpeg (`-stream_loop -1`); EOF bedeutet Fehler.** Da ffmpeg
   nie regulär endet, ist `eof $fd` immer ein Abbruch (Decoderfehler, Datei weg). Dann
   Kanal schließen, ffmpegs stderr-Meldung (separat umgeleitet und gelesen) als Fehler an
   der Karte melden – kein automatischer Neustart, keine Dauerschleife.
   *Alternative:* ohne `-stream_loop` und Neustart bei EOF – mehr Logik, Startverzögerung
   an jedem Schleifenübergang.

5. **Lebensdauer an den Wish koppeln.** Alles hängt in einem
   `When /someone/ wishes /p/ plays video /path/ with /...options/`-Body (plus Kurzform
   ohne Optionen, die auf die Langform weiterleitet, analog `displays image`).
   `On unmatch` schließt den Kanal und sendet `SIGTERM` an die PID (wie
   `unix-commands.folk`). Karte weg → Wish weg → Prozess beendet, Hold entfernt →
   Fenster verschwindet; erneutes Auflegen startet einen frischen Prozess (= von vorn).
   Ein Prozess pro (Karte, Pfad) → mehrere Karten unabhängig.

6. **Fenster neben der Karte über die `"image"`-GPU-Pipeline auf dem Display-Canvas.**
   Aus `$p has quad` die Ecken in Display-Raum (Meter) holen (wie `title.folk`), Kanten-
   Einheitsvektoren `u` (oben links→oben rechts) und `v` (oben links→unten links) bilden.
   Fensterbreite `width` (Standard 20 cm), Höhe = Breite·H/W, Abstand 1 cm. Ankerpunkt je
   `side` (right: rechts oben + Abstand·u; left: links oben − (Abstand+Breite)·u; below/
   above entsprechend über `v`), daraus vier Ecken, mit `$poseLib project` auf
   Projektor-Pixel. Dann
   `Wish the GPU draws pipeline "image" onto canvas $dispCanvas with arguments
   [list $res $surfaceToClip $gim $a $b $c $d]` nach `Wish the GPU loads image $im as
   texture`. Damit folgt das Fenster Verschiebung und Drehung.
   *Alternative:* `Wish $p displays image …` auf dem Blatt-Canvas – zeichnet nur innerhalb
   der Karte. *Alternative:* `Wish to draw an image onto $disp` – keine Drehung.
   Längenangaben (`30cm`, `0.3m`) per vorhandener Folk-Einheitenumrechnung parsen; falls
   keine passende Hilfsfunktion existiert, eigene kleine Umrechnung für `mm|cm|m`.

## Risks / Trade-offs

- [Kopie von ~0,7 MB pro Bild über Jim-Strings und GPU-Upload pro Bild belasten Folk] →
  Größe auf 640 px und 25 fps begrenzen; bei Rucklern Bildrate senken oder auf
  C-Reader (Decision 3, Alternative) umstellen. Messen in den Tasks.
- [Neue Textur pro Bild → Speicherwachstum, falls Freigabe verzögert] → Destructor am
  Hold gibt Image und Textur frei; Speicher in Tasks über einige Minuten beobachten.
- [Folk-Tick langsamer als Video → Bildsprünge] → neuestes Bild gewinnt, Video bleibt
  zeitrichtig.
- [Zombie-/Waisenprozesse bei Absturz oder Reload] → `On unmatch` + Prüfung mit
  `pgrep ffmpeg` in Tasks; ffmpeg beendet sich zusätzlich bei SIGPIPE.
- [`-stream_loop` kann je nach Container am Schleifenübergang kurz ruckeln oder
  Zeitstempel springen lassen] → akzeptiert; im Schleifentest beobachten.
- [Fenster ragt über den Projektionsbereich hinaus] → akzeptiert; Nutzer wählt `side`.
- [Kurzes Erkennungs-Flackern der Karte startet Video neu] → akzeptiert (Spec: neu
  auflegen = von vorn); ggf. später `-keep` wie im display-saver.

## Migration Plan

1. `video.folk` nach `/home/folk/folk/user-programs/carthag/` kopieren (fswatch-Patch lädt
   es), `mkdir ~/folk-videos` und Testvideo ablegen.
2. Rollback: `video.folk` entfernen; laufende `ffmpeg`-Prozesse enden über
   `On unmatch`.

## Open Questions

- Liefert `$poseLib project` für Punkte außerhalb der Karte dieselbe Genauigkeit wie für
  Titel/Fußnoten? (Erwartet ja; in Tasks visuell prüfen.)
