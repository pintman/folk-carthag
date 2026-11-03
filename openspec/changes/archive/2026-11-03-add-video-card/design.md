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
   *Nachtrag (Test auf carthag):* Handyvideos mit Rotations-Metadaten (90°/270°) meldet
   ffprobe mit kodierter Größe, ffmpeg dreht aber automatisch. Mit festem `scale=W:H`
   bliebe die Bytegröße zwar stimmig, das Bild wäre jedoch verzerrt. Daher zusätzlich
   `stream_side_data=rotation` abfragen und W/H bei ±90° tauschen. Ausgabeformat
   `-of default=nw=1` (Schlüssel=Wert) statt CSV, weil die Zahl der Felder variiert.
   Handtest: 10-s-Video ergibt exakt 10·25·640·360·3 Byte in ≈ 9,6 s.

3. **C-Reader für Prozess, Pipe und Puffer; Abfrage pro Clock-Tick.**
   *(Umgestellt während der Umsetzung – ursprünglich Einlesen in Jim.)*
   Eine kleine C-Bibliothek im User-Programm (`$cc extend $imageLib`) startet ffmpeg per
   `posix_spawnp` (stdin `/dev/null`, stdout in eine `pipe2(O_CLOEXEC)`, Pipe-Puffer per
   `F_SETPIPE_SZ` auf 1 MiB, stderr in eine Tempdatei, Signalmaske zurückgesetzt) und
   hält Lese-Ende, PID, einen Puffer für zwei Bilder und einen Bildzähler in einem
   Struct mit Mutex (`VideoReader*`). `videoPoll` liest nicht-blockierend alles
   Verfügbare, verwirft ältere Bilder und liefert das *neueste* vollständige als neues
   `Image` (3 Komponenten, `uniq` = Bildnummer) oder ein leeres. Aufgerufen pro Tick in
   `When the clock time is /t/` (~9 ms) im Wish-Body; neues Bild →
   `Hold! -key [list video $p $path frame] Claim $p has video frame $im
   -destructor [list $imageLib imageFree $im]`.
   *Warum nicht in Jim:* (a) Ein `while`-Leseloop im Wish-Body (Muster
   `unix-commands.folk`) endet nie; Folk räumt solche Matches nicht zuverlässig ab –
   beim Reload von `video.folk` und sogar beim Entfernen der Karte liefen alte
   Schleifen samt ffmpeg weiter und schrieben in denselben Hold (beobachtet: nicht
   monotone Bildnummern, verwaiste Prozesse). (b) Jim-Kanäle gehören dem
   Interpreter eines Worker-Threads; ein Clock-Tick-Body läuft in beliebigen Workern
   und könnte `$fd` nicht nutzen. (c) Jim ist mit UTF-8 gebaut, Binärdaten müssten mit
   Byte-Offsets in C geschnitten werden. Nebeneffekt: weniger Kopien → volle 25 fps
   (Jim-Variante: 11–18 fps).

4. **Endlosschleife macht ffmpeg (`-stream_loop -1`); EOF bedeutet Fehler.** Da ffmpeg
   nie regulär endet, ist EOF der Pipe immer ein Abbruch (Decoderfehler, Prozess weg).
   `videoTakeEof` meldet das genau einmal und sammelt den Prozess ein; der Tick-Body
   entfernt den Bild-Hold (Fenster weg) und hält ffmpegs stderr-Meldung als
   `$p has error …` (Hold, damit sie über den Tick hinaus bleibt) – kein Neustart.
   *Alternative:* ohne `-stream_loop` und Neustart bei EOF – mehr Logik, Startverzögerung
   an jedem Schleifenübergang.
   *Nachtrag (Test):* Gelöschte Dateien spielt ffmpeg weiter (Inode bleibt offen),
   gekürzte Dateien spielt es ohne Fehler bis zur Bruchstelle in Schleife – beides
   erzeugt kein EOF und damit keine Fehlermeldung; akzeptiert. Der EOF-Pfad selbst
   (ffmpeg per `kill -9` beendet) meldet den Fehler an der Karte, entfernt das Fenster
   und startet nicht neu.

5. **Lebensdauer an den Wish koppeln.** Alles hängt in einem
   `When /someone/ wishes /p/ plays video /path/ with /...options/`-Body (plus Kurzform
   ohne Optionen, die auf die Langform weiterleitet, analog `displays image`). Der Body
   endet nach dem Start sofort. `On unmatch` ruft `videoClose` (SIGTERM, bis 1 s auf
   Ende warten, sonst SIGKILL, `waitpid`; Puffer frei, Struct bleibt für evtl. noch
   laufende Ticks), löscht die stderr-Datei und entfernt Bild- und Fehler-Hold.
   Karte weg → Wish weg → Prozess beendet → Fenster verschwindet; erneutes Auflegen
   startet einen frischen Prozess (= von vorn). Ein Prozess pro (Karte, Pfad).
   *Test:* Entfernen, viermaliger Reload von `video.folk` (Body geändert) während der
   Wiedergabe: jeweils genau ein neuer Prozess pro Karte, keine Zombies/Waisen,
   Tempdateien aufgeräumt. Bei unverändertem Body bleibt das Match (und der Prozess)
   bestehen (Folk dedupliziert identische Statements).

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
   *Nachtrag (Test):* Ohne Weiteres flackert das Fenster: Beim Bildwechsel wird die alte
   Textur verworfen, bevor die neue geladen ist (4 von 30 Screenshots ohne Fenster).
   Texturladen und Zeichnen daher in `When -atomicallyWithKey [list video $p $path draw]`
   – das alte Bild bleibt, bis das neue konvergiert ist (danach 30/30 sichtbar).
   *Alternative:* `Wish $p displays image …` auf dem Blatt-Canvas – zeichnet nur innerhalb
   der Karte. *Alternative:* `Wish to draw an image onto $disp` – keine Drehung.
   Längenangaben (`30cm`, `0.3m`) per vorhandener Folk-Einheitenumrechnung parsen; falls
   keine passende Hilfsfunktion existiert, eigene kleine Umrechnung für `mm|cm|m`.

## Risks / Trade-offs

- [Kopie pro Bild und GPU-Upload pro Bild belasten Folk] → Größe auf 640 px Breite und
  25 fps begrenzt. *Gemessen (Task 4.2, Quer 640×360 + Hoch 640×1138, ~5 min):*
  24,5 / 23,7 fps; beide ffmpeg zusammen ~150 % CPU (von 800 %). Folk selbst zeigt
  schon ohne Video ~666 % (Worker drehen im Leerlauf) und mit Video ~565 % – Folk-CPU
  ist daher kein brauchbares Lastmaß. Hochformat ist mit 2,2 MB/Bild der teuerste Fall.
  *Tag-Erkennung (gedruckte Karte, je 20 s):* Kamera ~14,8 fps in allen Fällen;
  Vollbild-Erkennung 0 Videos 14,7/s (45 ms), 1 Video 14,3/s (48 ms), 3 Videos 11,7/s
  (60 ms); inkrementelle Verfolgung immer ~14,8/s (1–2 ms). Ein Video ist unkritisch,
  ab drei Videos werden neu aufgelegte Karten etwas später erkannt; liegende Karten
  folgen weiter flüssig.
- [Neue Textur pro Bild → Speicherwachstum, falls Freigabe verzögert] → Destructor am
  Hold gibt Image und Textur frei. *Gemessen:* RSS von folk über 3 min konstant
  (1 398 848 → 1 398 864 kB).
- [Folk-Tick langsamer als Video → Bildsprünge] → neuestes Bild gewinnt, Video bleibt
  zeitrichtig.
- [Zombie-/Waisenprozesse bei Absturz oder Reload] → `On unmatch` mit `videoClose`
  (siehe Decision 5, getestet); stirbt Folk, endet ffmpeg beim nächsten Schreiben per
  SIGPIPE. Kleines Leck: pro Wiedergabe bleibt das Reader-Struct (~100 Byte) stehen.
- [`-stream_loop` kann je nach Container am Schleifenübergang kurz ruckeln oder
  Zeitstempel springen lassen] → akzeptiert; im Schleifentest beobachten.
- [Fenster ragt über den Projektionsbereich hinaus] → akzeptiert; Nutzer wählt `side`.
- [Bei `side above` liegt das Fenster über einem Titel (`is titled`, 2 cm über der
  Karte; Fenster beginnt 1 cm darüber)] → akzeptiert; bei beschrifteten Karten andere
  Seite wählen.
- [Kurzes Erkennungs-Flackern der Karte startet Video neu] → akzeptiert (Spec: neu
  auflegen = von vorn); ggf. später `-keep` wie im display-saver.

## Migration Plan

1. `video.folk` nach `/home/folk/folk/user-programs/carthag/` kopieren (fswatch-Patch lädt
   es), `mkdir ~/folk-videos` und Testvideo ablegen.
2. Rollback: `video.folk` entfernen; laufende `ffmpeg`-Prozesse enden über
   `On unmatch`.

## Testhilfe

Ohne gedruckte Karten getestet über virtuelle Karten per Websocket
(`ws://carthag.local:4273/ws`, gleiche Statements wie der `/new`-Editor: `has quad`,
`has resolved geometry`, `has program code`) und Screenshots des Folk-Fensters per
`DISPLAY=:0 ffmpeg -f x11grab`. Projektion, Breite (Lineal), Seiten und Tag-Erkennung
unter Last danach mit einer gedruckten Karte geprüft.

## Open Questions

- Liefert `$poseLib project` für Punkte außerhalb der Karte dieselbe Genauigkeit wie für
  Titel/Fußnoten? (Erwartet ja; in Tasks visuell prüfen.)
  *Antwort (Test mit gedruckter Karte):* Ja – das Fenster sitzt so genau wie Titel und
  Editor-Umriss. Auf carthag ist die Kalibrierung derzeit um 1–2 cm (am Bildrand und
  bei schräger Karte mehr) versetzt; dann überlappen Fenster wie Titel teils die Karte.
