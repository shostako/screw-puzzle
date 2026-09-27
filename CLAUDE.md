# screw-puzzle

スマホで流行っているねじ外しパズル（色合わせ＋待機スロット型）の自作。最終目標は Android アプリ。今はブラウザで遊べる試作段階（`index.html` とキャラの画像）。

## 最初に読むもの

- `README.md`: ルール、実装の仕組み、公開ページの URL、**次にやる候補**

## 方針

- このディレクトリは純粋なゲーム開発の作業場。技術と設計の話だけをする
- 試作は `index.html` と、キャラの画像 `assets/chara/`（原画は `art/chara/`、`scripts/prep_chara.py` が作る）。Artifact へは画像を `files` で一緒に公開する。`index.html` は Artifact のページ規約（`<!doctype>`/`<html>`/`<body>` を書かない、外部スクリプトは cdnjs など許可された CDN のみ）に従っている。単体で開けるページは `bash scripts/build.sh` が `dist/index.html` に包み、`assets/` を横に写して出す（インラインスクリプトの構文チェックと、画像のそろいのチェックつき）。ローカル確認もこれを使う
- 配信は2系統: Artifact（Claude から公開）と GitHub Pages（master への push で `deploy-pages.yml` が自動配信）
- 変更はブランチを切って PR。PR では CI（build.sh）が走り、Codex が自動レビューする。再レビューは `@claude`（`claude.yml`）
- 公開ページの更新は、この会話で公開していなければ README の URL を `url` に渡して再公開する
- 変更したら、公開ページをスマホで触って確かめるのはユーザー。こちらは画面が崩れていないことと JS エラーが無いことまでを確認し、手触りは確認していないと正直に言う
- 独立リポジトリ（GitHub: shostako/screw-puzzle、public。2026-09-27 に private から切り替え）。2026-09-27 に lab から履歴ごと切り出した。`~/ClaudeCode` の親リポからはホワイトリスト方式で除外されている
- 作業ログはこのリポの `logs/yyyy-MM.md` に書く
- 「同期して」の対象（git-sync の manifest に category 3 で登録済み）
