# Tasks

## 1. Format festlegen

- [x] 1.1 `user-programs/carthag/paper-format.folk` mit `Claim paper format a4 is the default paper format` und kurzem Kommentar (Quelle der Formate: Upstream `print.folk`) anlegen; prüfen, dass die Datei im Repo liegt
- [x] 1.2 Prüfen, dass kein weiterer `default paper format`-Claim existiert (`grep -rn "default paper format"` in `folk-data/hold/` und `user-programs/` auf carthag), sonst entfernen
- [x] 1.3 Datei nach carthag rsyncen und ggf. Folk neu starten; im Web-Interface prüfen, dass das Statement `paper format a4 is the default paper format` vorhanden ist

## 2. Verhalten prüfen

- [x] 2.1 Testprogramm im Web-Editor drucken; prüfen, dass die neue `N.ps` `/PageSize [595 842]` enthält und `N.meta.folk` left + tagSize + right ≈ 210 mm ergibt
- [x] 2.2 Druckvorschau im Editor auf dem Tisch einschalten; prüfen, dass der Rahmen etwa 210 × 297 mm misst
- [x] 2.3 Prüfen, ob `the calibrated print scale` bzw. `translation` gesetzt ist; falls ja, mit A4-Kalibrierblatt neu messen und dann 2.1 wiederholen
- [x] 2.4 Gedrucktes Testblatt auf den Tisch legen; prüfen, dass die Projektion bündig zum Blatt sitzt (Ergebnis: Druckgeometrie stimmt, Versatz positionsabhängig → Kamera-Projektor-Kalibrierung, siehe TODO.md)

## 3. Dokumentation und Sicherung

- [x] 3.1 README: Abschnitt zum Papierformat (Datei, Rollback, alte Letter-Programme neu drucken, PDFs in 100 % drucken) ergänzen und `paper-format.folk` in der Inhaltstabelle erwähnen; prüfen, dass die Restore-Befehle unverändert passen
- [x] 3.2 `./sync.sh` ausführen; prüfen, dass `paper-format.folk` und das Testprogramm im Commit enthalten sind
