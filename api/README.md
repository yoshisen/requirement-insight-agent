# api

将来の API 層を置くディレクトリです。

MVP の優先順位は CLI が先で、API はその次です。
FastAPI などを導入する場合も、まず schema と service boundary を先に固めます。

## Current MVP Endpoints

- `GET /health`
- `POST /population/build`
- `POST /scenario/run`
- `POST /examples/tokyo-supermarket-launch/run`
- `GET /results/{artifact_name}`

## Run

```bash
python -m uvicorn api.app:app --reload
```