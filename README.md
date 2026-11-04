# folk-carthag

Backup der [Folk](https://folk.computer)-Installation auf `carthag.local`.

## Was ist Folk?

Folk ist ein Physical-Computing-System: Ein Projektor und eine Kamera machen
einen Tisch oder eine Wand zur Oberfläche. Programme werden auf Papier
gedruckt, über AprilTags erkannt und reagieren auf ihre Lage im Raum.
Technisch ist Folk eine reaktive Datenbank aus Statements (`Claim`, `Wish`,
`When`) mit einer Tcl-basierten Sprache (Jim Tcl + C).

- Quellcode: <https://github.com/FolkComputer/folk>
- Auf carthag: Repo unter `/home/folk/folk`, Start mit `make start`
  (bzw. systemd-Service)
- Webinterface: `http://carthag.local:4273` (Editor, Kalibrierung, Setup)

## Inhalt

| Pfad | Inhalt |
|---|---|
| `folk-data/program/` | Gedruckte Programme: `N.folk` (Code), `N.meta.folk` (Metadaten), `N.pdf`/`N.ps` (Druckvorlage) |
| `folk-data/hold/` | Persistierter Zustand: `calibration` (Kamera/Projektor), `web__setup.folk` (Setup), `print.folk` |
| `user-programs/carthag/` | Eigene Programme von carthag, die Folk beim Start lädt (andere Hosts nicht gesichert), u. a. `paper-format.folk` (A4 als Papierformat) |
| `user-programs/carthag/video/` | Videos für `video.folk`, per `sync.sh` mitgesichert |
| `folk-patches/` | Lokale Patches am Folk-Quellcode (z. B. deutsche Tastatur), Anleitung jeweils im Patch-Kopf |

Nicht gesichert: `folk-data/trocr/` (TrOCR-Modell, wird neu geladen).

## Sichern

    ./sync.sh

Holt die drei Ordner per rsync (`--delete`) und committet Änderungen automatisch.
Alte Stände bleiben in der git-History.

## Wiederherstellen

Folk auf carthag stoppen, dann:

    rsync -avz folk-data/     folk@carthag.local:/home/folk/folk-data/
    rsync -avz user-programs/carthag/ folk@carthag.local:/home/folk/folk/user-programs/carthag/
    rsync -avz folk-patches/  folk@carthag.local:/home/folk/folk-patches/

Patches danach im Folk-Repo anwenden:

    cd ~/folk && git apply ~/folk-patches/deutsche-tastatur.patch

Bei neuer Hardware/geänderter Projektor- oder Kameraposition
neu kalibrieren statt `hold/calibration` zurückzuspielen.

## Papierformat

Folk druckt auf carthag in A4. Festgelegt in `user-programs/carthag/paper-format.folk`:

    Claim paper format a4 is the default paper format

- Gilt für Druck aus Web-Editor und Tisch-Editor, Druckvorschau,
  Kalibrierblatt und `lpr` (`-o media=a4`). Folk-Quellcode bleibt unverändert,
  kein Patch nötig.
- Nur hier festlegen: Ein zweiter Claim (z. B. im Web-Setup) lässt die Abfrage scheitern.
- Rollback: Datei löschen, dann gilt wieder Upstream-Standard `letter`.
- Alte Programme (`folk-data/program/0–12`) sind im Letter-Format gedruckt.
  Auf A4-Papier sitzt die Projektion leicht versetzt, bei Bedarf neu drucken.
- PDFs von Hand in **tatsächlicher Größe / 100 %** drucken, nicht „An Seite anpassen“.
- Nach Formatwechsel Druck-Kalibrierung (`calibrated print scale/translation`)
  mit A4-Kalibrierblatt neu messen.

## Eigene Programme schreiben: Was Folk mitbringt

Diese Seite zeigt, was die mitgelieferten Programme (`builtin-programs/`)
für eigene Folk-Programme bereitstellen. Ein Programm ist ein Stück Code
auf einem Blatt Papier mit AprilTag. `$this` ist immer das eigene Blatt.

### Grundprinzip

- `Claim …` – eine Aussage machen: `Claim $this is cool`
- `Wish …` – etwas wünschen, ein anderes Programm erfüllt es:
  `Wish $this is outlined blue`
- `When … { … }` – auf Aussagen reagieren; `/name/` ist eine Variable:
  `When /someone/ is cool { … }`
- Mehrere Bedingungen mit `&` verknüpfen:
  `When $this points up at /p/ & /p/ is cool { … }`

### Ein neues Programm anlegen

1. Web-Oberfläche öffnen: `http://<folk-rechner>:4273/new`.
2. Code eingeben, mit Ctrl/Cmd+S speichern, mit Ctrl/Cmd+P drucken.
3. Gedrucktes Blatt unter Kamera/Projektor legen – das Programm läuft.

**Programme am Tisch bearbeiten:** Tastatur (mit eigenem Tag) unter das
Blatt legen, sodass sie nach oben darauf zeigt. Es erscheint ein Editor.

| Taste | Wirkung |
|---|---|
| Ctrl+S | Speichern (Programm läuft sofort mit neuem Code) |
| Ctrl+P | Neu drucken |
| Ctrl+Z / Ctrl+Y | Rückgängig / Wiederholen |
| Ctrl+C / X / V | Kopieren / Ausschneiden / Einfügen |
| Ctrl+R | Änderungen verwerfen |
| Ctrl+- / Ctrl+= | Schrift kleiner / größer |
| Ctrl+B | Erstellt ein neues leeres Programm (Blank) |

Geänderte Programme zeigen „(edited …)“ als Titel.

### Beschriften & Hervorheben

```tcl
Wish $this is labelled "Hallo Welt"      ;# Text mitten auf dem Blatt
Wish $this is outlined green             ;# farbiger Rahmen
Wish $this is titled "Überschrift"       ;# Text über dem Blatt
Wish $this is footnoted "Fußnote"        ;# Text unter dem Blatt
Wish $this is left-margined "links"      ;# bzw. right-margined
Wish $this is filled red                 ;# Blatt einfärben
```

### Formen & Text zeichnen

Koordinaten beziehen sich auf das eigene Blatt. Längen brauchen eine
Einheit (`mm`, `cm`, `m`) oder sind relativ (`50%`).

```tcl
Wish $this draws a circle
Wish $this draws a circle with radius 2cm color red filled true
Wish $this draws a rect with width 5cm height 2cm offset {right 50%}
Wish $this draws a triangle with radians 0.5 color yellow
Wish $this draws a shape with sides 7 radius 3cm
Wish $this draws text "Hallo" with position {10% 20%} scale 1cm color white
Wish $this draws a polyline {{0cm 0cm} {5cm 2cm} {8cm 0cm}} with dashed true
Wish $this draws a polygon {{0cm 0cm} {4cm 0cm} {2cm 3cm}} with color blue
```

- Formen: `circle`, `rect`, `triangle`, `square`, `pentagon` …
  `octagon`, oder beliebig viele Ecken via `sides`.
- Position: `position {x y}`, `x … y …`, oder `offset {right 3cm}` /
  `{up 50%}` relativ zur Blattmitte.
- Weitere Optionen: `color`, `filled`, `thickness`, `radians`, `layer`.
- Farben: Namen wie `red`, `green`, `blue`, `yellow`, `white`.

### Bilder, GIFs, Shader

```tcl
Wish $this displays image "katze.png"        ;# aus ~/folk-images/
Wish $this displays image "/pfad/zu/bild.jpg"
Wish $this draws sprite "lauf.png" with frames 8 columns 4 fps 12
Wish $this draws toy shader { … GLSL im ShaderToy-Stil … }
```

JPEG, PNG und GIF (animiert) werden unterstützt.

### Videos abspielen

Eigenes Programm `user-programs/carthag/video.folk` (nicht Teil von Folk). Das Video
erscheint in einem Fenster neben der Karte und wandert mit, wenn die Karte verschoben
oder gedreht wird.

```tcl
Wish $this plays video "demo.mp4"                    ;# aus user-programs/carthag/video/, rechts
Wish $this plays video "tiere/katze.mp4" with side below width 30cm
Wish $this plays video "/home/folk/clip.webm" with side left
```

- `side`: `right` (Standard), `left`, `above`, `below`.
- `width`: Fensterbreite in `mm`, `cm` oder `m` (Standard `20cm`); die Höhe ergibt
  sich aus dem Seitenverhältnis.
- Relative Namen werden wie bei Audio gesucht: zuerst in
  `~/folk/user-programs/<rechner>/video/`, dann in `~/folk/video/`; der erste Treffer
  gilt. Absolute Pfade bleiben unverändert. Alles, was `ffmpeg` dekodieren kann (MP4/H.264, WebM,
  MKV, MOV …); Hochkant-Handyvideos werden richtig gedreht.
- Fehlende oder kaputte Dateien: Fehlermeldung an der Karte (bei fehlender Datei mit
  allen durchsuchten Pfaden).
- Einschränkungen: stumm, Endlosschleife ohne Pause/Spulen; Karte weg = Stopp,
  neu auflegen = von vorn. Dekodiert wird auf max. 640 px Breite bei 25 fps
  (unter Last weniger).
- `user-programs/carthag/video/` wird per `sync.sh` mitgesichert – nur kurze Clips
  ablegen, damit das Repo klein bleibt.
- Beispiele unter `user-programs/carthag/video/`: `demo.mp4` (quer), `hoch.mp4` (hochkant),
  `tiere/katze.mp4`, `clip.webm`; zum Testen der Fehlermeldungen `kaputt.mp4`
  (keine Videodatei) und `nurton.mp4` (nur Ton).

### Mit anderen Blättern interagieren

```tcl
# Zeigen: Ist ein anderes Blatt über meinem?
When $this points up at /p/ {
    Wish $p is labelled "Ich werde angezeigt"
}
# Richtung: up, down, left, right; optional Reichweite:
When $this points right with length 0.5 at /p/ { … }

# Linie mit Pfeil zu einem anderen Blatt (user-programs/carthag/connections.folk)
# $p = ID des Zielblatts, z. B. aus `When … /p/` oder direkt eine Tag-Nummer
When $this points right at /p/ {
    Wish $this is connected to $p from right to left color red width 4
}
Wish $this is connected to 45001                         ;# festes Zielblatt
Wish $this is dynamically connected to 45001 color green ;# wandernde Pfeile
# Ankerpunkte: centroid, top, bottom, left, right, topleft, topright, …

# Zeit (Sekunden) für Animationen
When the clock time is /t/ {
    Wish $this is labelled [clock format [expr {int($t)}] -format %T]
}
```

### Kamera & Erkennung

```tcl
# Kamerabild des eigenen Blatts anzeigen
When $this has camera slice /slice/ {
    Wish $this displays camera slice $slice
}
# Umrisse von Gezeichnetem auf dem Blatt erkennen lassen
Wish $this has contours
```

Optional (benötigen installierte ML-Modelle): Objektverfolgung (SAM2),
Texterkennung (CRAFT, TrOCR), Bildvergleich (DINOv2), Laserpointer-
Erkennung (`Wish to detect laser blobs`).

### Ton & Musik

```tcl
Wish to play audio drums.wav    ;# aus user-programs/<rechner>/audio/, dann <folk>/audio/
Wish to play audio /pfad/zu/datei.mp3
```

WAV, FLAC und MP3. `music.folk` bindet zusätzlich TidalCycles an.

### Rechner & Außenwelt

```tcl
# Befehl ausführen, Ausgabe zeilenweise erhalten
Wish $this runs Unix command "ls" with arguments [list "-l"]
When $this has Unix output lines /lines/ {
    Wish $this is labelled [join $lines \n]
}

# Eigene Webseite unter http://<folk-rechner>:4273/hallo
Wish the web server handles route "/hallo" with handler {
    html { <h1>Hallo aus Folk</h1> }
}
```

### Fehler finden

- Bei einem Fehler blinkt der Rahmen des Blatts rot, die Meldung steht
  als Titel darüber (Warnungen: gelb).
- Web-Oberfläche (`http://<folk-rechner>:4273/`): Liste aller Programme,
  aktuelle Statements (`/statements`), Kamerabild (`/camera`),
  erkannte Blätter (`/quads`), Programmcode (`/program/<id>`).

### Beispiele

`builtin-programs/demos.folk` enthält kleine Startbeispiele (Tags
45000–45008): Beschriften, Zeigen, Uhrzeit, Kamerabild.
