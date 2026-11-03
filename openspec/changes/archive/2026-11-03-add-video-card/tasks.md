# Tasks

## 1. Vorbereitung auf carthag

- [x] 1.1 `mkdir ~/folk-videos` auf carthag, kurzes Testvideo (z. B. 10–20 s, H.264-MP4 mit Tonspur, Querformat) und ein Hochformat-Video ablegen; prüfen: `ls ~/folk-videos` zeigt beide
- [x] 1.2 Befehle von Hand testen: `ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 ~/folk-videos/demo.mp4` liefert Breite/Höhe; `ffmpeg -nostdin -loglevel error -re -i ~/folk-videos/demo.mp4 -an -vf scale=640:360,fps=25 -f rawvideo -pix_fmt rgb24 - | wc -c` (ohne `-stream_loop`, damit er endet) ergibt ≈ Dauer·25·640·360·3 Byte und braucht ≈ Videodauer; Abweichungen in design.md nachtragen

## 2. Dekodieren und Bilder als Claim

- [x] 2.1 `user-programs/carthag/video.folk` anlegen: Kurzform `plays video /path/` → Langform `with …`; Pfadauflösung (relativ → `~/folk-videos/`, absolut unverändert), `file exists`-Prüfung mit Fehler per `Say $p has error`; prüfen: Karte mit `"gibtsnicht.mp4"` zeigt Fehler mit vollem Pfad, Folk läuft weiter (Spec „Datei fehlt“, „Relativer Name“, „Absoluter Pfad“)
- [x] 2.2 Größenermittlung per `ffprobe`, W×H selbst berechnen und als `scale=W:H` übergeben (max. 640 px Breite, gerade Maße, Seitenverhältnis erhalten), Fehler bei fehlendem Videostream; prüfen: Textdatei umbenannt zu `kaputt.mp4` erzeugt Fehler an der Karte, kein Fenster (Spec „Datei nicht abspielbar“)
- [x] 2.3 C-Funktion `frameFromBytes` (per `$cc extend $imageLib`) und Lese-Schleife: `open "|ffmpeg -nostdin -loglevel error -re -stream_loop -1 … -an … -f rawvideo -pix_fmt rgb24 -" rb` mit separat umgeleitetem stderr, non-blocking/binary, pro Clock-Tick lesen, neuestes vollständiges Bild als `Hold! -key [list video $p frame] Claim $p has video frame $im -destructor …`; prüfen: `http://carthag.local:4273/statements` zeigt sich ändernden Claim `… has video frame …`
- [x] 2.4 Endlosschleife und Abbruch: EOF von ffmpeg → Kanal schließen, stderr-Meldung als Fehler an der Karte, kein Neustart; prüfen: 10-s-Video läuft > 30 s durch, Übergang ohne längeren Hänger (Spec „Endlosschleife“); Videodatei während der Wiedergabe löschen/kürzen → Fehler an der Karte, keine Dauerschleife
- [x] 2.5 `On unmatch`: Kanal schließen, `SIGTERM` an PID; prüfen: Karte entfernen → `pgrep -c ffmpeg` = 0; `video.folk` speichern/neu laden → keine verwaisten Prozesse (Spec „Karte wird entfernt“)

## 3. Fenster neben der Karte

- [x] 3.1 Geometrie nach `title.folk`-Muster: Quad-Ecken in Display-Raum, Vektoren `u`/`v`, Fensterecken je `side` (Standard right) mit Abstand 1 cm und `width` (Standard 20 cm, Einheiten mm/cm/m), Projektion mit `$poseLib project`; prüfen: Fenster erscheint rechts neben der Karte ohne Überdeckung (Spec „Standardposition“)
- [x] 3.2 Zeichnen: `Wish the GPU loads image $im as texture` + `Wish the GPU draws pipeline "image" onto canvas <Display-Canvas> …` mit vier Ecken; prüfen: Video läuft sichtbar, Seitenverhältnis stimmt bei Quer- und Hochformat (Spec „Karte wird aufgelegt“, „Breite gewählt“ mit `width 30cm` per Lineal nachmessen)
- [x] 3.3 Optionen `side left|above|below` testen und Karte verschieben/drehen; prüfen: Fenster folgt und bleibt an der gewählten Seite (Spec „Seite gewählt“, „Karte wird gedreht oder verschoben“; beantwortet Open Question zur Projektionsgenauigkeit)
- [x] 3.4 Kein Ton: Video mit Tonspur abspielen; prüfen: keine Ausgabe an den Lautsprechern (Spec „Kein Ton“)
- [x] 3.5 README-Abschnitt „Videos abspielen“ unter „Eigene Programme schreiben“ (Wish-Syntax, Optionen, `~/folk-videos/`, unterstützte Formate, Einschränkungen: stumm, Neustart bei Neuauflegen, Videos nicht per `sync.sh` gesichert); prüfen: Beispiel aus README als Karte funktioniert

## 4. Integration und Last

- [x] 4.1 Zwei Karten mit verschiedenen Videos und zwei mit demselben Video gleichzeitig; Entfernen einer Karte; prüfen: unabhängige Wiedergabe, nur deren Prozess endet (Spec „Zwei Karten“)
- [x] 4.2 Last messen: 5 min Wiedergabe, `top` (CPU von folk und ffmpeg) und Speicher von folk vorher/nachher; prüfen: kein stetiges Speicherwachstum, Kamera-/Tag-Erkennung bleibt flüssig; Messwerte in design.md (Risiken) nachtragen
- [x] 4.3 `./sync.sh` ausführen; prüfen: `user-programs/carthag/video.folk` im Repo identisch mit carthag
