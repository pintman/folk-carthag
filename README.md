# folk-carthag

Backup der Folk-Installation auf `carthag.local`.

- `folk-data/` – Programme (`program/`), Zustand inkl. Kalibrierung (`hold/`)
- `user-programs/` – eigene Programme

Sichern: `./sync.sh` (rsync + automatischer Commit)

Wiederherstellen:

    rsync -avz folk-data/     folk@carthag.local:/home/folk/folk-data/
    rsync -avz user-programs/ folk@carthag.local:/home/folk/folk/user-programs/
