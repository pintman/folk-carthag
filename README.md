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
| `user-programs/` | Eigene Programme, die Folk beim Start lädt |

Nicht gesichert: `folk-data/trocr/` (TrOCR-Modell, wird neu geladen).

## Sichern

    ./sync.sh

Holt beide Ordner per rsync (`--delete`) und committet Änderungen automatisch.
Alte Stände bleiben in der git-History.

## Wiederherstellen

Folk auf carthag stoppen, dann:

    rsync -avz folk-data/     folk@carthag.local:/home/folk/folk-data/
    rsync -avz user-programs/ folk@carthag.local:/home/folk/folk/user-programs/

Bei neuer Hardware/geänderter Projektor- oder Kameraposition
neu kalibrieren statt `hold/calibration` zurückzuspielen.
