# Tasks

## 1. Repo: Pfadauflösung und Umzug

- [ ] 1.1 `git mv folk-videos user-programs/carthag/video`; prüfen: `git status` zeigt nur Umbenennungen, `ls user-programs/carthag/video` enthält `demo.mp4`, `hoch.mp4`, `clip.webm`, `kaputt.mp4`, `nurton.mp4`, `tiere/katze.mp4`
- [ ] 1.2 `user-programs/carthag/video.folk`: Pfadauflösung (Zeile ~203) durch Resolver nach design.md ersetzen (absolut unverändert; sonst `[pwd]/user-programs/[info hostname]/video/<name>`, dann `[pwd]/video/<name>`; keiner → `error "video: Datei nicht gefunden: <name> (gesucht: <pfad1>, <pfad2>)"`), Kopfkommentar Zeile 6 anpassen; prüfen: `grep -n folk-videos user-programs/carthag/video.folk` liefert nichts
- [ ] 1.3 Resolver lokal mit `~/tmp/folk/vendor/jimtcl/jimsh` testen (Prozedur in Testskript kopieren, `pwd`/`info hostname` per Temp-Verzeichnis `user-programs/<host>/video/` und `video/` nachstellen); prüfen: Szenarien „Relativer Name“, „Relativer Name im allgemeinen Ordner“, „Host-Ordner hat Vorrang“, „Alter Ort wird ignoriert“, „Absoluter Pfad“ und „Datei fehlt“ (Meldung nennt beide Pfade) liefern das erwartete Ergebnis
- [ ] 1.4 README: Inhaltstabelle (Zeile `folk-videos/` → `user-programs/carthag/video/`, per `sync.sh` gesichert), Wiederherstellen-Abschnitt (rsync-Zeile für `folk-videos/` entfernen), Abschnitt „Videos abspielen“ (Suchreihenfolge, Beispiel mit absolutem Pfad ohne `folk-videos`, Hinweis „wird nicht gesichert“ ersetzen durch „wird mitgesichert, nur kurze Clips ablegen“, Beispielpfade); prüfen: `grep -n folk-videos README.md` liefert nichts
- [ ] 1.5 README „Ton & Musik“: Kommentar auf Upstream-Verhalten korrigieren (`user-programs/<rechner>/audio/`, dann `<folk>/audio/`, sonst absolut); prüfen: `grep -n "assets/sounds\|/sounds/" README.md` liefert nichts

## 2. carthag: Umzug und Deployment (carthag muss erreichbar sein)

- [ ] 2.1 Altlasten suchen: `ssh folk@carthag.local 'grep -l folk-videos ~/folk-data/program/*.folk ~/folk/user-programs/carthag/*.folk'`; Treffer auf relative Namen umstellen; prüfen: nur noch `video.folk` (alte Version) trifft
- [ ] 2.2 Dateien umziehen: `mkdir -p ~/folk/user-programs/carthag/video && mv ~/folk-videos/* ~/folk/user-programs/carthag/video/ && rmdir ~/folk-videos`; prüfen: `ls ~/folk-videos` schlägt fehl, `ls ~/folk/user-programs/carthag/video` zeigt alle Dateien
- [ ] 2.3 Neues `video.folk` übertragen: `rsync -avz user-programs/carthag/video.folk folk@carthag.local:/home/folk/folk/user-programs/carthag/`; prüfen: Folk-Log zeigt `fswatch: … video.folk updated, reloading.`
- [ ] 2.4 Am Tisch testen: Karten mit `"demo.mp4"`, `"tiere/katze.mp4"` spielen ab; `"gibtsnicht.mp4"` zeigt Fehler mit beiden durchsuchten Pfaden; Folk läuft weiter (Specs „Karte wird aufgelegt“, „Relativer Name“, „Datei fehlt“)
- [ ] 2.5 `./sync.sh` ausführen; prüfen: kein Commit bzw. keine Änderungen unter `user-programs/carthag/video/` (Repo und carthag identisch)

## Workflow follow-up

- Change archivieren (`/opsx:archive`), danach prüfen, dass `openspec/specs/video-playback/spec.md` den neuen Suchpfad enthält.
