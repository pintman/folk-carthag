# video-playback Specification

## Purpose

Lässt eine gedruckte Folk-Karte ein Video abspielen, das als projiziertes Fenster
neben der Karte erscheint und mit der Karte mitwandert.

## Requirements

### Requirement: Karte spielt Video ab
Ein Folk-Programm SHALL mit `Wish $this plays video "<datei>"` die Wiedergabe einer
Videodatei auslösen. Solange die Karte erkannt wird, läuft das Video ohne Ton in
Originalgeschwindigkeit und beginnt nach dem Ende automatisch von vorn.

#### Scenario: Karte wird aufgelegt
- **WHEN** eine Karte mit `Wish $this plays video "demo.mp4"` unter Kamera und Projektor gelegt wird und `~/folk/user-programs/carthag/video/demo.mp4` existiert
- **THEN** erscheint innerhalb weniger Sekunden das laufende Video neben der Karte

#### Scenario: Endlosschleife
- **WHEN** das Video sein Ende erreicht und die Karte weiterhin liegt
- **THEN** beginnt die Wiedergabe erneut am Anfang

#### Scenario: Kein Ton
- **WHEN** ein Video mit Tonspur abgespielt wird
- **THEN** wird kein Ton ausgegeben

### Requirement: Wiedergabe endet mit der Karte
Wird die Karte nicht mehr erkannt oder der Wish entfernt, SHALL die Wiedergabe stoppen
und das Videofenster verschwinden. Beim erneuten Auflegen SHALL das Video von vorn
beginnen. Nach dem Stopp DÜRFEN keine Dekodierprozesse weiterlaufen.

#### Scenario: Karte wird entfernt
- **WHEN** die abspielende Karte vom Tisch genommen wird
- **THEN** verschwindet das Videofenster und auf carthag läuft kein Dekodierprozess für dieses Video mehr

#### Scenario: Karte wird wieder aufgelegt
- **WHEN** die Karte nach dem Entfernen erneut aufgelegt wird
- **THEN** startet das Video am Anfang

### Requirement: Videofenster neben der Karte
Das Video SHALL in einem rechteckigen Fenster neben der Karte erscheinen, das Position
und Drehung der Karte folgt und das Seitenverhältnis des Videos beibehält. Standard ist
rechts neben der Karte; per `with side <right|left|above|below>` ist die Seite und per
`width <länge>` (z. B. `30cm`) die Fensterbreite wählbar.

#### Scenario: Standardposition
- **WHEN** eine Karte `Wish $this plays video "demo.mp4"` ohne Optionen äußert
- **THEN** erscheint das Fenster rechts neben der Karte, ohne die Karte zu überdecken

#### Scenario: Seite gewählt
- **WHEN** eine Karte `Wish $this plays video "demo.mp4" with side below` äußert
- **THEN** erscheint das Fenster unterhalb der Karte

#### Scenario: Breite gewählt
- **WHEN** eine Karte `Wish $this plays video "demo.mp4" with width 30cm` äußert
- **THEN** ist das projizierte Fenster etwa 30 cm breit und so hoch, wie es das Seitenverhältnis des Videos ergibt

#### Scenario: Karte wird gedreht oder verschoben
- **WHEN** die abspielende Karte verschoben oder gedreht wird
- **THEN** folgt das Fenster der Karte und bleibt an derselben Seite ausgerichtet

### Requirement: Auflösung des Dateinamens
Ein relativer Dateiname SHALL wie bei Audio im Upstream-Folk aufgelöst werden: zuerst
in `user-programs/<host>/video/`, dann in `video/`, jeweils relativ zum
Folk-Verzeichnis (`/home/folk/folk`); `<host>` ist der Rechnername. Der erste Treffer
gilt. `~/folk-videos/` SHALL NOT durchsucht werden. Ein absoluter Pfad SHALL
unverändert verwendet werden.

#### Scenario: Relativer Name
- **WHEN** der Wish `plays video "tiere/katze.mp4"` lautet und `~/folk/user-programs/carthag/video/tiere/katze.mp4` existiert
- **THEN** wird `~/folk/user-programs/carthag/video/tiere/katze.mp4` abgespielt

#### Scenario: Relativer Name im allgemeinen Ordner
- **WHEN** der Wish `plays video "demo.mp4"` lautet, `~/folk/user-programs/carthag/video/demo.mp4` fehlt und `~/folk/video/demo.mp4` existiert
- **THEN** wird `~/folk/video/demo.mp4` abgespielt

#### Scenario: Host-Ordner hat Vorrang
- **WHEN** `demo.mp4` sowohl in `~/folk/user-programs/carthag/video/` als auch in `~/folk/video/` liegt
- **THEN** wird die Datei aus `~/folk/user-programs/carthag/video/` abgespielt

#### Scenario: Alter Ort wird ignoriert
- **WHEN** der Wish `plays video "demo.mp4"` lautet und die Datei nur in `~/folk-videos/` liegt
- **THEN** wird sie nicht gefunden und die Karte meldet „Datei fehlt“

#### Scenario: Absoluter Pfad
- **WHEN** der Wish `plays video "/home/folk/clip.webm"` lautet
- **THEN** wird `/home/folk/clip.webm` abgespielt

### Requirement: Fehler an der Karte melden
Ist die Datei nicht vorhanden oder nicht abspielbar, SHALL eine Fehlermeldung an der
Karte erscheinen (Folk-Fehleranzeige). Folk und andere Programme MÜSSEN dabei normal
weiterlaufen.

#### Scenario: Datei fehlt
- **WHEN** eine Karte `Wish $this plays video "gibtsnicht.mp4"` äußert
- **THEN** zeigt die Karte eine Fehlermeldung mit allen durchsuchten Pfaden und Folk läuft weiter

#### Scenario: Datei nicht abspielbar
- **WHEN** die angegebene Datei kein dekodierbares Video ist
- **THEN** zeigt die Karte eine Fehlermeldung, es wird kein Fenster angezeigt und Folk läuft weiter

### Requirement: Mehrere Videokarten gleichzeitig
Mehrere Karten SHALL gleichzeitig jeweils ihr eigenes Video abspielen können, auch
dieselbe Datei, unabhängig voneinander.

#### Scenario: Zwei Karten
- **WHEN** zwei Karten mit unterschiedlichen Videos aufgelegt sind
- **THEN** spielen beide Fenster ihr jeweiliges Video, und Entfernen einer Karte beendet nur deren Wiedergabe
