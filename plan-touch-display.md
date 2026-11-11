# folk-carthag – Digitaler Touch-Tisch

Recherche und Konzept für einen selbstgebauten Multitouch-Tisch, der Dateien anzeigt, Textbearbeitung erlaubt und Drag & Drop von Inhalten unterstützt.

---

## 1. Ausgangslage: Touch unter Linux

Interaktive Displays (z. B. **Prowise Touchscreen**) und günstige **IR-Touchrahmen** melden Touch per USB als Standard-**USB-HID-Multitouch**-Gerät. Linux unterstützt das ohne Treiber (`hid-multitouch` + `libinput`).

**Checkliste**

- Touch-USB-Kabel (meist Typ B) zusätzlich zu HDMI anschließen. Es muss der Touch-Port sein, der zum gewählten HDMI-Eingang gehört.
- Erkennung prüfen:
  ```bash
  lsusb
  sudo libinput list-devices | grep -i -A5 touch
  sudo evtest            # Gerät wählen, Board antippen
  dmesg | tail           # direkt nach dem Einstecken
  ```
- Touch dem richtigen Bildschirm zuordnen:
  - X11: `xinput map-to-output <ID> HDMI-1`
  - niri: `input { touch { map-to-output "HDMI-A-1" } }`
  - allgemein: udev-Regel mit `LIBINPUT_CALIBRATION_MATRIX`
- Wird das Gerät nicht erkannt: VID:PID manuell an `hid-multitouch` übergeben (siehe Arch-Wiki).
- Prowise-Software: Presenter läuft im Browser. Native Tools (Screen Share, Updater) gibt es nur für Windows/macOS.

---

## 2. Vorbild: Grant Custers Tabletop-Computer

Quelle: [My tabletop computer setup](https://feed.grantcuster.com/post/2026-11-03-10-51-03-my-tabletop-computer-setup) (Nov. 2026)

**Hardware**

- Hisense-Fernseher 55" als Display
- IR-Touchrahmen 43", in den TV-Rahmen eingelassen. Bündige Oberfläche, günstiger als kapazitiv, erkennt aber schon knapp über der Fläche.
- entspiegelnde Schutzfolie 50" und Plexiglas (1/8") als oberste Schicht
- Mini-PC, Unterkonstruktion aus Sperrholz

**Software**

- Linux (Distribution nicht genannt)
- [niri](https://github.com/niri-wm/niri) (Wayland-Compositor), um Bild und Touch nur auf den vom Rahmen abgedeckten Teilbereich zu legen
- kein spezieller Touch-Treiber (Plug-and-Play)
- Demos: <https://tabletop.grantcuster.com>

**Repos** ([github.com/GrantCuster](https://github.com/GrantCuster))

| Repo | Inhalt |
|---|---|
| [tabletop-demos](https://github.com/GrantCuster/tabletop-demos) | statische Demo-Galerie (Videos aus Bluesky-Posts), Vite + TypeScript |
| [tabletop](https://github.com/GrantCuster/tabletop) | Webcam-Bilder anzeigen/zuschneiden, React + TypeScript + Vite |
| [feed-grantcuster-com](https://github.com/GrantCuster/feed-grantcuster-com) | Code seines Feeds/Blogs |

Ein Repo mit niri-Konfiguration oder Dotfiles wurde nicht gefunden.

---

## 3. Anforderungen

- Dateien anzeigen (Bilder, Video, PDF, Text)
- Text bearbeiten und speichern
- Inhalte per Drag & Drop frei verschieben, drehen, skalieren
- mehrere Personen gleichzeitig, von allen Tischseiten

---

## 4. Hardware-Optionen

| Option | Vorteile | Nachteile |
|---|---|---|
| TV + IR-Touchrahmen + Glas/Plexi | günstig, groß | Rahmen bündig einlassen, Touch reagiert knapp über der Fläche |
| vorhandenes Prowise-Board liegend | Touch und Bild fertig | Gewicht, Lüftung, Garantie bei liegendem Betrieb klären |

**Rechner:** Mini-PC mit Intel N100/N150 reicht für Web-Apps. Für 3D lieber Ryzen mit stärkerer iGPU.

---

## 5. Software-Varianten

### Variante A: Standard-Desktop (schnell, wenig Code)

- **GNOME unter Wayland**: beste Touch-Unterstützung und als einziges eine eingebaute Bildschirmtastatur
- Nautilus (Dateien), GNOME Text Editor, Papers/Evince (PDF), Loupe (Bilder)
- Drag & Drop zwischen Apps geht, ist aber nicht auf einen Tisch ausgelegt
- wirkt eher wie ein großes Tablet

### Variante B: eigene Canvas-Web-App (empfohlen)

Alle Inhalte liegen als frei bewegliche Karten auf einer Fläche.

| Ebene | Empfehlung |
|---|---|
| OS | Debian 13 oder Fedora |
| Compositor | **cage** (Kiosk, eine App im Vollbild) oder **niri** |
| Laufzeit | Chromium im Kiosk-Modus: `chromium --kiosk --ozone-platform=wayland --touch-events=enabled <URL>` |
| Autostart | Autologin + systemd-User-Service mit cage |
| Canvas | **Excalidraw** (MIT) oder **Konva.js**/PixiJS (selbst gebaut). Alternative **tldraw**: für Produktivbetrieb Lizenzschlüssel nötig, kostenlose Hobby-Lizenz für nicht-kommerzielle Nutzung, mit Wasserzeichen und Prüfung der Anfrage |
| Bilder/Video | native `<img>` / `<video>` |
| PDF | **pdf.js** |
| Texteditor | **CodeMirror 6** (Code/Markdown) oder **TipTap** (formatierter Text) |
| Backend | **FastAPI** (Python) oder Fastify (Node): Ordner auflisten, Dateien ausliefern, speichern. Neue Dateien erkennen mit watchdog/chokidar |
| Layout speichern | Positionen der Karten als JSON im Backend |
| Dateien auf den Tisch bringen | Netzwerkordner (SMB/Nextcloud), USB-Stick per Auto-Mount oder QR-Code zum Upload vom Handy |
| Build | Vite + TypeScript |

**Architektur**

```
┌────────────── Tisch (Mini-PC) ──────────────┐
│ cage → Chromium (Kiosk)                     │
│   └─ Canvas-App (Vite/TS)                   │
│       ├─ Karten: Bild | Video | PDF | Text  │
│       ├─ Pointer Events (Multitouch)        │
│       └─ Bildschirmtastatur (in der App)    │
│              │ HTTP/WebSocket               │
│ Backend (FastAPI)                           │
│   ├─ /files     Ordner listen/ausliefern    │
│   ├─ /save      Text speichern              │
│   ├─ /layout    Kartenpositionen (JSON)     │
│   └─ Watcher    neue Dateien → WebSocket    │
│              │                              │
│ Datenordner ← SMB / USB / Handy-Upload      │
└─────────────────────────────────────────────┘
```

---

## 6. Stolperfallen

1. **Die HTML5-Drag-&-Drop-API funktioniert per Touch unter Linux unzuverlässig.** Verschieben mit Pointer Events selbst umsetzen (Canvas-Bibliotheken tun das bereits).
2. **Bildschirmtastatur:** Chromium bringt unter Linux keine mit.
   - mit cage/niri: **wvkbd** oder **squeekboard**
   - besser für den Tisch: Tastatur in der App (z. B. **simple-keyboard**), drehbar und frei platzierbar
   - pragmatisch: Bluetooth-Tastatur
3. **Mehrere Personen:** jede Berührung über `pointerId` getrennt verfolgen
4. **Keine feste Leserichtung:** Karten drehbar machen, Bedienelemente auf alle Seiten verteilen
5. **Browser-Gesten abschalten:** `touch-action: none`, `contextmenu` unterdrücken, Zoom des Browsers verhindern
6. **Große Bedienelemente** (mindestens 15 mm), keine Hover-Effekte
7. **IR-Rahmen:** reagiert knapp über der Fläche. Rahmen bündig einbauen, keine Gegenstände auf dem Tisch abstellen.

---

## 7. Entwicklung

- Vite-Dev-Server mit `npm run dev -- --host` auf dem Laptop starten, den Tisch-Browser auf diese Adresse zeigen lassen. Änderungen erscheinen dann sofort auf dem Tisch (Hot Reload).
- Fernzugriff auf den Tisch per SSH.
- Touch am Laptop testen: Chrome DevTools → Device Toolbar (simuliert nur Einzeltouch, für Multitouch echtes Gerät nutzen).

---

## 8. Mögliche Aufteilung als Unterrichtsprojekt (FIAE/ITA)

| Team | Aufgabe |
|---|---|
| Infrastruktur | Linux, cage/Kiosk, Autostart, Touch-Zuordnung |
| Backend | FastAPI: Dateien, Speichern, Layout, Watcher/WebSocket |
| Canvas | Karten, Multitouch-Gesten (verschieben, drehen, zoomen) |
| Viewer/Editor | PDF, Bild, Video, CodeMirror/TipTap |
| Eingabe | Bildschirmtastatur in der App, drehbar |
| Hardware | Rahmen, Glas, Unterkonstruktion |

---

## Quellen

- [Arch Wiki – Multitouch displays](https://wiki.archlinux.org/title/Multitouch_Displays)
- [Grant Custer – My tabletop computer setup](https://feed.grantcuster.com/post/2026-11-03-10-51-03-my-tabletop-computer-setup)
- [Tabletop demos](https://tabletop.grantcuster.com/)
- [GrantCuster auf GitHub](https://github.com/GrantCuster)
- [niri](https://github.com/niri-wm/niri)
- [tldraw – FAQ](https://tldraw.dev/faq) · [tldraw – License key](https://tldraw.dev/sdk-features/license-key)
