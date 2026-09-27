#!/usr/bin/env bash
# Android 版(Capacitor)に入れるページを www/ に作り、android/ へ写す。
# index.html は Artifact 形式(外部 CDN から Matter.js などを読む)なので、アプリ用には
#   - Matter.js と poly-decomp を node_modules から同梱し、
#   - 丸ゴシック(M PLUS Rounded 1c の 700 と 800)を @fontsource から同梱して、
# ネットにつながっていなくても遊べるようにする。バージョンは package.json で index.html と同じものに固定している。
# 端末のステータスバーとナビゲーションバーに重ならないよう、安全域のぶんだけ body に余白を取る。
# 前提: npm install 済み。最後に npx cap sync android を流す(android/ が無ければ先に npx cap add android)。
set -euo pipefail
cd "$(dirname "$0")/.."

FS=node_modules/@fontsource/m-plus-rounded-1c
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/vendor" "$tmp/fonts/files"

cp node_modules/matter-js/build/matter.min.js "$tmp/vendor/"
cp node_modules/poly-decomp/build/decomp.min.js "$tmp/vendor/"
cp "$FS"/files/m-plus-rounded-1c-*-700-normal.woff2 "$FS"/files/m-plus-rounded-1c-*-800-normal.woff2 "$tmp/fonts/files/"
cp -r assets "$tmp/assets"

node - "$tmp" "$FS" <<'EOF'
const fs = require('fs'), path = require('path');
const [out, fsDir] = process.argv.slice(2);
// フォント: 700 と 800 の CSS をつなぎ、woff(使わない古い形式)への参照を外す
const css = ['700', '800'].map(w => fs.readFileSync(path.join(fsDir, `${w}.css`), 'utf8')).join('\n')
  .replace(/,\s*url\([^)]*\.woff\) format\('woff'\)/g, '');
if (/\.woff\)/.test(css)) throw new Error('woff reference left in font css');
fs.writeFileSync(path.join(out, 'fonts/fonts.css'), css);
for (const m of css.matchAll(/url\(\.\/files\/([^)]+)\)/g))
  if (!fs.existsSync(path.join(out, 'fonts/files', m[1]))) throw new Error('missing font file ' + m[1]);

// ページ: 外部から読むものを同梱したものへ差し替える。差し替え先が見つからなければ失敗する
let html = fs.readFileSync('index.html', 'utf8');
const swaps = [
  ['<link rel="preconnect" href="https://fonts.googleapis.com">\n', ''],
  ['<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@700;800&display=swap">',
   '<link rel="stylesheet" href="fonts/fonts.css">'],
  ['<script src="https://cdnjs.cloudflare.com/ajax/libs/matter-js/0.19.0/matter.min.js"></script>',
   '<script src="vendor/matter.min.js"></script>'],
  ['<script src="https://cdn.jsdelivr.net/npm/poly-decomp@0.3.0/build/decomp.min.js"></script>',
   '<script src="vendor/decomp.min.js"></script>'],
];
for (const [from, to] of swaps) {
  if (!html.includes(from)) throw new Error('not found in index.html: ' + from.trim());
  html = html.replace(from, to);
}
const ext = html.match(/<(?:script|link)[^>]+(?:src|href)="https?:\/\/[^"]+"/g);
if (ext) throw new Error('external resource left: ' + ext.join(' '));
const head = [
  '<!doctype html>',
  '<html lang="ja">',
  '<meta charset="utf-8">',
  '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, user-scalable=no">',
  // Capacitor の SystemBars が --safe-area-inset-* を入れる(古い WebView は env() が正しくないため)。無ければ env() を使う
  '<style>',
  '  body {',
  '    box-sizing: border-box;',
  '    padding: var(--safe-area-inset-top, env(safe-area-inset-top, 0px)) var(--safe-area-inset-right, env(safe-area-inset-right, 0px))',
  '             var(--safe-area-inset-bottom, env(safe-area-inset-bottom, 0px)) var(--safe-area-inset-left, env(safe-area-inset-left, 0px));',
  '  }',
  '</style>',
].join('\n');
fs.writeFileSync(path.join(out, 'index.html'), head + '\n' + html + '</html>\n');
// インラインスクリプトの構文チェック(実行はしない)
let n = 0;
for (const m of html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)) { new Function(m[1]); n++; }
if (!n) throw new Error('inline script not found');
console.log('www: syntax ok, ' + fs.readdirSync(path.join(out, 'fonts/files')).length + ' font files');
EOF

rm -rf www
mv "$tmp" www
trap - EXIT
echo "wrote www/"
if [ -d android ]; then npx cap sync android; fi
