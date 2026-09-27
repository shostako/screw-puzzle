#!/usr/bin/env python3
"""Android 版のアイコンと起動画面を、キャラの原画(art/chara/face.png)から作って android/ に書く。

何度流しても同じ結果になる。原画を差し替えたら流し直してコミットする。
- アダプティブアイコン(Android 8 以降): 前景は顔まわりを 108dp の中央 72dp に置く。背景は色(values/ic_launcher_background.xml)
- 旧来のアイコン(ic_launcher.png は角丸の四角、ic_launcher_round.png は丸)
- 起動画面(splash.png): 木の色の地に、胸から上の絵を真ん中に置く。縦横と画面密度ごとに、Capacitor の雛形と同じ寸法で書く
"""
import os
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / 'android' / 'app' / 'src' / 'main' / 'res'
FACE = ROOT / 'art' / 'chara' / 'face.png'

ICON_BG = (255, 222, 150)                 # アイコンの地(暖かいクリーム色)
WOOD = (138, 74, 29)                       # 起動画面の地。ページの --wood と同じ
HEAD = (180, 40, 1100, 960)                # 顔まわり(prep_chara.py の smile と同じ切り出し)
DENS = {'mdpi': 1, 'hdpi': 1.5, 'xhdpi': 2, 'xxhdpi': 3, 'xxxhdpi': 4}
SPLASH = {                                 # Capacitor の雛形の寸法
    'port-mdpi': (320, 480), 'port-hdpi': (480, 800), 'port-xhdpi': (720, 1280), 'port-xxhdpi': (960, 1600), 'port-xxxhdpi': (1280, 1920),
    'land-mdpi': (480, 320), 'land-hdpi': (800, 480), 'land-xhdpi': (1280, 720), 'land-xxhdpi': (1600, 960), 'land-xxxhdpi': (1920, 1280),
}


def save(im, path):
    # 書き終えてから差し替える。一時ファイルは res の外に置く(ビルド中に res へ .tmp があると Gradle が止まる)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(suffix='.png', dir=ROOT / 'android')
    os.close(fd)
    im.save(tmp, 'PNG', optimize=True)
    os.replace(tmp, path)


def main():
    face = Image.open(FACE).convert('RGBA')
    head = face.crop(HEAD)
    for d, k in DENS.items():
        # 前景: 108dp の中央 72dp に顔まわり
        px = round(108 * k)
        fg = Image.new('RGBA', (px, px), (0, 0, 0, 0))
        h = round(72 * k)
        fg.alpha_composite(head.resize((h, h), Image.LANCZOS), ((px - h) // 2, (px - h) // 2))
        save(fg, RES / f'mipmap-{d}' / 'ic_launcher_foreground.png')
        # 旧来のアイコン: 48dp。地の上に顔まわり、角丸の四角と丸
        s = round(48 * k)
        base = Image.new('RGBA', (s, s), ICON_BG + (255,))
        base.alpha_composite(head.resize((s, s), Image.LANCZOS))
        for name, radius in (('ic_launcher', s * 0.22), ('ic_launcher_round', s / 2)):
            mask = Image.new('L', (s * 4, s * 4), 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, s * 4 - 1, s * 4 - 1), radius=radius * 4, fill=255)
            out = Image.new('RGBA', (s, s), (0, 0, 0, 0))
            out.paste(base, (0, 0), mask.resize((s, s), Image.LANCZOS))
            save(out, RES / f'mipmap-{d}' / f'{name}.png')
    # 起動画面: 短い辺の 55% の大きさで胸から上の絵
    for key, (w, h) in SPLASH.items():
        im = Image.new('RGBA', (w, h), WOOD + (255,))
        side = round(min(w, h) * 0.55)
        im.alpha_composite(face.resize((side, side), Image.LANCZOS), ((w - side) // 2, (h - side) // 2))
        save(im.convert('RGB'), RES / f'drawable-{key}' / 'splash.png')
    im = Image.new('RGBA', (480, 320), WOOD + (255,))
    im.alpha_composite(face.resize((176, 176), Image.LANCZOS), ((480 - 176) // 2, (320 - 176) // 2))
    save(im.convert('RGB'), RES / 'drawable' / 'splash.png')
    (RES / 'values' / 'ic_launcher_background.xml').write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
        '    <color name="ic_launcher_background">#%02X%02X%02X</color>\n'
        '    <color name="splash_background">#%02X%02X%02X</color>\n</resources>\n' % (ICON_BG + WOOD), encoding='utf-8')
    print('wrote icons and splash into', RES.relative_to(ROOT))


if __name__ == '__main__':
    main()
