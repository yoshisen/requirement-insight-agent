# agents/orchestration

synthetic consumer agents に対する prompt 実行を扱う層です。

- prompt builder
- structured output parser
- retry-aware execution
- local placeholder / external provider の差異吸収

この層は provider の実装詳細を知らず、structured request / response 契約だけに依存する想定です。