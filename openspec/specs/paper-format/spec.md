# paper-format Specification

## Purpose

Legt fest, in welchem Papierformat Folk auf carthag Programme druckt und Druckvorschauen anzeigt, damit gedruckte Blätter zum verwendeten A4-Papier passen.

## Requirements

### Requirement: Neue Programme werden in A4 gedruckt
Folk auf carthag SHALL neu gedruckte Programme im Format A4 (595 × 842 pt, 210 × 297 mm) erzeugen. Das gilt für den Druck aus dem Web-Editor und aus dem Editor auf dem Tisch.

#### Scenario: Druck aus dem Web-Editor
- **WHEN** ein Programm im Web-Editor (`http://carthag.local:4273`) gedruckt wird
- **THEN** enthält die erzeugte `folk-data/program/N.ps` `/PageSize [595 842]`
- **AND** die Geometrie in `N.meta.folk` ergibt mit left + tagSize + right etwa 210 mm

#### Scenario: Druck aus dem Editor auf dem Tisch
- **WHEN** ein Programm über den projizierten Editor gedruckt wird
- **THEN** ist die erzeugte Druckvorlage A4

### Requirement: Druckvorschau zeigt A4
Die Druckvorschau des Editors auf dem Tisch SHALL ein Blatt im Seitenverhältnis und in der Größe von A4 anzeigen.

#### Scenario: Vorschau einschalten
- **WHEN** für einen Editor eine Druckvorschau gewünscht wird
- **THEN** ist der projizierte Vorschau-Rahmen 210 × 297 mm groß

### Requirement: Drucker erhält A4 als Medium
Wird über einen Standarddrucker per CUPS gedruckt, SHALL der Auftrag A4 als Medium anfordern.

#### Scenario: Druck über Standarddrucker
- **WHEN** ein Standarddrucker festgelegt ist und ein Programm gedruckt wird
- **THEN** wird `lpr` mit `-o media=a4` aufgerufen

### Requirement: Einstellung ohne Upstream-Änderung
Die Formatwahl SHALL vollständig in diesem Repo liegen, mit `sync.sh` gesichert und mit der README-Anleitung wiederhergestellt werden können. Der Folk-Quellcode bleibt unverändert.

#### Scenario: Folk-Update
- **WHEN** das Folk-Repo auf carthag auf einen neuen Upstream-Stand aktualisiert wird
- **THEN** bleibt A4 das Standardformat, ohne dass ein Patch erneut angewendet werden muss

#### Scenario: Wiederherstellung
- **WHEN** `user-programs/carthag/` laut README auf carthag zurückgespielt und Folk gestartet wird
- **THEN** ist A4 das Standardformat
