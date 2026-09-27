#!/usr/bin/env bash
# index.html は Artifact 形式（doctype / html / body を書かない）。
# これを単体で開けるページに包んで dist/index.html に出し、画像(assets/)を横に置く。
# GitHub Pages の配信、PR の CI、ローカル確認のすべてがこれを使う。
set -euo pipefail
cd "$(dirname "$0")/.."

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

{
  printf '<!doctype html>\n<html lang="ja">\n<meta charset="utf-8">\n'
  printf '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
  printf '<style>html, body { margin: 0; }</style>\n'
  printf '<link rel="icon" href="assets/chara/icon-192.png">\n<link rel="apple-touch-icon" href="assets/chara/icon-180.png">\n'
  cat index.html
  printf '</html>\n'
} > "$tmp/index.html"

# インラインスクリプトの構文チェック（src 付きの script は対象外）。実行はしない。
node -e '
  const fs = require("fs");
  const html = fs.readFileSync(process.argv[1], "utf8");
  const re = /<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g;
  let m, n = 0;
  while ((m = re.exec(html))) { new Function(m[1]); n++; }
  if (!n) { console.error("inline script not found"); process.exit(1); }
  console.log("syntax ok: " + n + " inline script(s)");
' "$tmp/index.html"

# ページが名前で読む画像がそろっているか（CHARA の表とアイコン）
missing=0
for f in $(grep -oE "[a-z-]+\.webp|icon-[0-9]+\.png" "$tmp/index.html" | sort -u); do
  [ -f "assets/chara/$f" ] || { echo "missing assets/chara/$f" >&2; missing=1; }
done
[ "$missing" = 0 ]

rm -rf dist
mkdir -p dist
cp "$tmp/index.html" dist/index.html
cp -r assets dist/assets
echo "wrote dist/index.html and dist/assets"
