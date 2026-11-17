#!/data/data/com.termux/files/usr/bin/bash
# Ejecuta el actualizador de AnimeChronicle (uso manual desde Termux).
DIR="/storage/emulated/0/Download/Opencode/AnimeChronicle"
PY="/data/data/com.termux/files/usr/bin/python3"
cd "$DIR" || exit 1
"$PY" "$DIR/actualizar_noticias.py" >> "$DIR/actualizar_noticias.log" 2>&1
