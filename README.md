# ネジ外し工房

色合わせ＋待機スロット型のねじ外しパズル。ブラウザで遊べ、同じ中身を包んだ Android 版もある。

- 物理は [Matter.js](https://brm.io/matter-js/)。板はねじ1本になると支点でぶら下がり、0本で落ちる
- ステージはステージ番号を種にした乱数で生成する。生成時に手順を探索して、解けることを確かめた盤面だけを出す
- 3D 版は [screw-puzzle-3d](https://github.com/shostako/screw-puzzle-3d)

## 遊ぶ

https://shostako.github.io/screw-puzzle/

スマホのブラウザで開ける。ホーム画面に追加すればアプリのように起動できる。

## ルール

- 上に色つきの箱が2つ並ぶ。ねじをタップすると、同じ色で空きのある箱に入る。3本で満杯になると箱は消え、次の箱が出る
- 合う箱が無いねじは待機スロット（5個）へ入る。新しい箱が出ると、スロットの同じ色のねじは自動で移る
- 上の板に少しでも隠れているねじは外せない。深い階層の板は見えない、または影しか見えない
- 全部の箱を埋めればクリア。スロットが満杯で入れられるねじが無くなれば詰み
- 困ったら左上の電球でヒント、詰んだら「解ける所まで戻る」で解ける局面まで戻れる。どちらも使うとクリアの星が減る
- 上部のサイコロからは、難しさを選んで毎回ちがう盤面で遊べる

## Android 版

[Capacitor](https://capacitorjs.com/) で `index.html` を包んだもの（`android/`）。Matter.js とフォントは同梱するので、オフラインでも遊べる。ストアには公開していない。

要るもの: Node 22、JDK 21、Android SDK（platform 36、build-tools 36.0.0）。

```
export JAVA_HOME=/path/to/jdk-21 ANDROID_HOME=/path/to/Android/Sdk
npm ci
npm run app:apk      # → android/app/build/outputs/apk/debug/app-debug.apk
```

- できる APK はビルドした PC のデバッグ鍵で署名される。別の PC で作った APK は上書きインストールできない（入れ直すと端末に残した進み具合が消える）
- 端末へは `adb install -r android/app/build/outputs/apk/debug/app-debug.apk` で入れる。USB でつながない場合は APK を端末へ送って開く（初回は「提供元不明のアプリ」の許可が要る）

## 開発

- ゲーム本体は `index.html` 1枚と、キャラの画像 `assets/chara/`。`index.html` は `<!doctype>` や `<html>` を持たない断片なので、単体で開くページは次で作る

  ```
  bash scripts/build.sh    # → dist/index.html（assets/ も横に写す）
  ```

  インラインスクリプトの構文と、画像がそろっているかも検査する。`dist/` をローカルの HTTP サーバで開いて確かめる
- キャラの原画は `art/chara/`（ChatGPT で作った透過 PNG）。ゲームで読む軽い画像は `python3 scripts/prep_chara.py` が作る。Android のアイコンと起動画面は `python3 scripts/android_res.py`
- CI は PR ごとに `scripts/build.sh` を通し、Android のデバッグ APK まで組み立てる（Actions の成果物として 14 日残る）
- master へ push すると GitHub Pages に自動で配信される

仕組み（盤面の生成、解けることの保証、板の動きの見積もり、詰みの判定）と、決めごと・確認状況・次にやる候補は [docs/DEV_NOTES.md](docs/DEV_NOTES.md) にまとめてある。
