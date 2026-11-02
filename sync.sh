#!/bin/bash
# Sichert folk-data und user-programs von carthag in dieses Repo.
# Trailing slashes: Inhalt synchronisieren, nicht verschachteln.
set -euo pipefail
cd "$(dirname "$0")"

REMOTE=folk@carthag.local
FOLK_DATA=/home/folk/folk-data          # ggf. /home/folk/folk/folk-data
USER_PROGRAMS=/home/folk/folk/user-programs
PATCHES=/home/folk/folk-patches

rsync -avz --delete --exclude trocr/ "$REMOTE:$FOLK_DATA/"     ./folk-data/
rsync -avz --delete                  "$REMOTE:$USER_PROGRAMS/" ./user-programs/
rsync -avz --delete                  "$REMOTE:$PATCHES/"       ./folk-patches/

git add -A
if git diff --cached --quiet; then
    echo "Keine Änderungen."
else
    git commit -q -m "chore: Sync von carthag $(date '+%F %T')"
    echo "Commit erstellt."
fi
