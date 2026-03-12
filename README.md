# GearSpeed

ロードバイクのギア速度表ジェネレータ。
Pythonista 3（iOS）版および Web 版として動作します。

## デモ（Web 版）

**GitHub Pages:** https://masaakis.github.io/GearSpeed/

ブラウザからアクセスしてすぐに使えます。

## 概要

- フロントギア・リアギア構成・ホイールサイズ・タイヤ幅を入力して、ケイデンスごとの速度を計算し表形式で表示する。
- 速度・ギア比差をカラーグラデーションで視覚化。
- ダークモード自動対応（OS 設定に連動）。
- カセットプリセットの選択・ダウンロード。
- カスタムギアセットの保存・読み込み・エクスポート（localStorage）。
- 生成した表をクリップボードにコピーして共有。
- オフラインでのキャッシュは標準的なブラウザキャッシュに依存します。

## ファイル構成

```
GearSpeed/
├── docs/                        # Web/PWA 版（GitHub Pages 公開ディレクトリ）
│   ├── index.html               # UI（HTML）
│   ├── app.js                   # 計算・UI ロジック（JavaScript）
│   ├── style.css                # スタイルシート
│   ├── manifest.json            # マニフェスト(旧PWA用ファイル、現在は利用しない)
│   ├── service-worker.js        # （PWA用、削除しても構いません）
│   └── bike_speed_settings.json # カセットプリセット定義
├── gear_speed_backup.py         # オリジナルの Pythonista 版スクリプト（バックアップ）
└── README.md                    # このファイル
```

## 主要機能

### Web/PWA 版（`docs/`）

1. フロントギア（20〜60T）／ホイールサイズ（700c / 650c）／タイヤ幅設定
2. モード選択：全ギア（9〜51T）または カスタム入力
3. **カセットプリセット** — `bike_speed_settings.json` から読み込み、選択するだけでリアギアを自動入力
4. **プリセットダウンロード** — 現在のプリセット JSON をファイルとして保存
5. **カスタムギアセットの保存／読み込み** — ブラウザの localStorage に名前付きで保存・呼び出し
6. **カスタムギアセットのエクスポート** — `custom_gear_sets.json` としてダウンロード
7. "Generate" ボタンで速度表を生成（ケイデンス 70 / 80 / 90 / 100 / 110 rpm）
8. 速度・ギア比差をカラーグラデーションで表示
9. 表をクリップボードにコピー

### Pythonista 版（`gear_speed_backup.py`）

- iPhone/iPad 上の Pythonista 3 で動作するオリジナル版。
- `ui`, `console`, `dialogs`, `clipboard`, `objc_util` などの Pythonista 専用モジュールを使用。
- 現在はバックアップとして保存されています。

## 使い方

### Web 版

1. https://masaakis.github.io/GearSpeed/ をブラウザで開く。
2. 各パラメータを設定し「Generate」をタップ／クリック。
3. （任意）モバイルブラウザのメニューから「ホーム画面に追加」。

### Pythonista 版（ローカル実行）

1. Pythonista 3 を起動。
2. `gear_speed_backup.py` を開き、実行ボタンをタップ。

## 技術スタック

| 区分 | 内容 |
|------|------|
| Web フロントエンド | HTML / CSS / Vanilla JavaScript |
| (non-PWA) | シンプルな静的ページ |
| ホスティング | GitHub Pages（`docs/` ブランチ） |
| オリジナル版 | Python 3（Pythonista 3 on iOS） |

## ライセンス

MIT License

---

© 2026 MasaakiS
