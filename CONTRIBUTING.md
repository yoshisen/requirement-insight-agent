# Contributing

Requirement Insight Agent への貢献を歓迎します。
このリポジトリは **schema-first / safety-first / MVP-first** を前提に進めます。

## 開発の始め方

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e .[dev]
python -m requirement_insight_agent --help
```

## 基本ルール

- README.md を上位の説明仕様とする
- `docs/architecture.md` を実装構造の指針とする
- `docs/schema-spec.md` を schema の source of truth とする
- 実装前に schema と safety の整合を確認する

## 推奨フロー

1. issue または設計意図を明確にする
2. 変更が schema / docs / sample / tests のどこに影響するか確認する
3. 最小の変更で進める
4. 検証手順を残す
5. PR では assumptions と known limitations を明記する

## コード規約

- Python 3.11+ を前提とする
- 標準ライブラリ優先、依存追加は理由を明示する
- 型注釈を付ける
- MVP 段階では複雑な抽象化より分かりやすさを優先する
- deterministic output が必要な箇所は seed / config を明示する

## ドキュメント規約

- 設計変更時は README または docs を更新する
- schema 変更時は `schemas/` と `docs/schema-spec.md` を両方更新する
- 安全性に関わる変更時は `docs/safety.md` を更新する

## データ利用ポリシー

- 個人再構成につながるデータはコミットしない
- raw data は許諾を確認してから持ち込む
- sample data は再配布可能かつ説明可能なものだけにする
- provenance、license、allowed_use を欠落させない

## Pull Request Checklist

- [ ] 変更理由が明確である
- [ ] schema / docs / tests の必要な更新を行った
- [ ] data use と safety の観点を確認した
- [ ] 追加依存が最小限である
- [ ] MVP のスコープを不用意に広げていない