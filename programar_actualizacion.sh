#!/data/data/com.termux/files/usr/bin/bash
# Programa la actualización diaria a las 07:30 mediante cron de Termux.
DIR="/storage/emulated/0/Download/Opencode/AnimeChronicle"
LANZADOR="/data/data/com.termux/files/home/bin/actualizar-animechronicle"

mkdir -p "$(dirname "$LANZADOR")"
cat > "$LANZADOR" <<EOF
#!/data/data/com.termux/files/usr/bin/bash
cd "$DIR" || exit 1
/data/data/com.termux/files/usr/bin/python3 "$DIR/actualizar_noticias.py" >> "$DIR/cron.log" 2>&1
EOF

chmod +x "$LANZADOR" "$DIR/actualizar_noticias.py" "$DIR/actualizar_diario.sh"

TMP="/data/data/com.termux/files/usr/tmp/cron-animechronicle.tmp"
(crontab -l 2>/dev/null | grep -v 'actualizar-animechronicle') > "$TMP"
echo "30 7 * * * $LANZADOR >> \"$DIR/cron.log\" 2>&1" >> "$TMP"
crontab "$TMP"
rm -f "$TMP"

pgrep -x crond >/dev/null 2>&1 || crond
echo "Actualización diaria de AnimeChronicle programada a las 07:30."
crontab -l
