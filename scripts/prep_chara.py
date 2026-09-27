#!/usr/bin/env python3
"""キャラの原画(art/chara/*.png)から、ゲームで読む軽い画像(assets/chara/)を作る。

何度流しても同じ結果になる。原画を差し替えたらこれを流し直してコミットする。
要るもの: Pillow(WebP 対応)。

- 全身の絵: 透明な余白を削って縦 540px の WebP。画面では最大 180px 前後で出すので、画素3倍の端末でも足りる
- 吹き出しの顔: 顔まわりの正方形を 144px の WebP。画面では 48px で出す
- アイコン: 胸から上の絵を 192px と 180px の PNG(ホーム画面に置いたときの印)
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'art' / 'chara'
OUT = ROOT / 'assets' / 'chara'

BODY_H = 540
FACE_PX = 144
# 顔まわりの切り出し位置(原画 1024x1536 の座標)。帽子の先と、ひらめきの電球まで入れる
FACES = {
    'idea': (0, 20, 940, 960),
    'oops': (100, 40, 940, 880),
}
BODIES = ('clear', 'good', 'oops', 'cry')


def trim(im):
    """ほぼ透明な画素(不透明度 8 以下)を除いた外接矩形で切る"""
    box = im.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()
    return im.crop(box)


def save_webp(im, path):
    tmp = path.with_suffix('.tmp')
    im.save(tmp, 'WEBP', quality=86, method=6)
    tmp.replace(path)                     # 書き終えてから差し替える


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name in BODIES:
        im = trim(Image.open(SRC / f'{name}.png').convert('RGBA'))
        w = round(im.width * BODY_H / im.height)
        save_webp(im.resize((w, BODY_H), Image.LANCZOS), OUT / f'{name}.webp')
    for name, box in FACES.items():
        im = Image.open(SRC / f'{name}.png').convert('RGBA').crop(box)
        save_webp(im.resize((FACE_PX, FACE_PX), Image.LANCZOS), OUT / f'{name}-face.webp')
    face = Image.open(SRC / 'face.png').convert('RGBA')
    for px in (192, 180):
        tmp = OUT / f'icon-{px}.tmp'
        face.resize((px, px), Image.LANCZOS).save(tmp, 'PNG', optimize=True)
        tmp.replace(OUT / f'icon-{px}.png')
    for p in sorted(OUT.iterdir()):
        print(f'{p.stat().st_size:>8}  {p.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
