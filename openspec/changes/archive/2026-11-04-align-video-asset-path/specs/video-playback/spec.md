# Spec Delta

## MODIFIED Requirements

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
