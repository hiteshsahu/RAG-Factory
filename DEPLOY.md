## Deploying Raginator to AWS

### Architecture
- raginator.hiteshsahu.com     → AWS Amplify  (React UI)
- api.raginator.hiteshsahu.com → AWS App Runner (FastAPI)
- ChromaDB persisted on EFS

---

### Step 1 — Push to GitHub

Make sure your repo structure looks like this:
```
RAG-Factory/
├── raginator/        ← Python package
├── api/
│   └── main.py       ← FastAPI bridge
├── ui/               ← React frontend
│   ├── src/
│   └── package.json
├── Dockerfile
├── apprunner.yaml
└── amplify.yml
```

```bash
git add .
git commit -m "feat: add deployment config"
git push origin main
```

---

### Step 2 — Store your API key in AWS Secrets Manager

```bash
aws secretsmanager create-secret \
  --name raginator/mistral-api-key \
  --secret-string "your_mistral_api_key_here" \
  --region eu-central-1
```

Note the ARN — you'll need it in Step 3.

---

### Step 3 — Deploy backend to App Runner

1. Go to AWS Console → App Runner → Create service
2. Source: Container registry → Amazon ECR Public
   OR: Source code repository → GitHub → select RAG-Factory
3. Build settings:
    - Runtime: Python 3
    - Build command: `pip install -e ".[all]" && pip install fastapi uvicorn python-multipart`
    - Start command: `uvicorn api.main:app --host 0.0.0.0 --port 8080`
    - Port: 8080
4. Environment variables:
    - MISTRAL_API_KEY → from Secrets Manager (paste ARN)
    - CHROMA_PERSIST_DIR → /data/chroma
5. Health check:
    - Path: /health
    - Interval: 30s
6. Click Deploy

App Runner gives you a URL like:
https://abc123.eu-central-1.awsapprunner.com

---

### Step 4 — Point custom domain at App Runner

1. App Runner → your service → Custom domains
2. Add: api.raginator.hiteshsahu.com
3. AWS gives you a CNAME record to add in Route 53
4. Go to Route 53 → hiteshsahu.com → Add CNAME:
   api.raginator → abc123.eu-central-1.awsapprunner.com

Wait ~5 minutes for DNS propagation.

---

### Step 5 — Deploy frontend to Amplify

1. Go to AWS Amplify → New app → Host web app
2. Connect GitHub → select RAG-Factory repo
3. App settings:
    - App name: raginator
    - Branch: main
    - Build settings: use amplify.yml (already in repo)
4. Environment variables:
    - VITE_API_URL → https://api.raginator.hiteshsahu.com
5. Click Save and deploy

Amplify gives you:
https://main.randomstring.amplifyapp.com

---

### Step 6 — Point custom domain at Amplify

1. Amplify → your app → Domain management
2. Add domain: hiteshsahu.com
3. Subdomain: raginator → main branch
4. AWS automatically handles the SSL cert and Route 53 records

Result: https://raginator.hiteshsahu.com ✓

---

### Step 7 — Verify

```bash
# Backend health
curl https://api.raginator.hiteshsahu.com/health
# → {"status": "ok", "corpora": 0}

# Backend docs
open https://api.raginator.hiteshsahu.com/docs

# Frontend
open https://raginator.hiteshsahu.com
```

---

## Cost estimate (monthly)

| Service          | Tier          | Cost        |
|------------------|---------------|-------------|
| App Runner       | 0.5 vCPU/1GB  | ~$15-25/mo  |
| Amplify          | Free tier     | $0          |
| Secrets Manager  | 1 secret      | ~$0.40/mo   |
| Route 53         | Hosted zone   | $0.50/mo    |
| Data transfer    | ~10GB         | ~$1/mo      |
| **Total**        |               | **~$17-27** |

To keep it at $0 for a portfolio demo:
- Use App Runner's free tier (first 90 days)
- Or deploy to Render.com free tier instead of App Runner

---

## Cheaper alternative: Render.com

If you want $0 cost for a portfolio demo:

```bash
# render.yaml (add to repo root)
services:
  - type: web
    name: raginator-api
    runtime: python
    buildCommand: pip install -e ".[all]" && pip install fastapi uvicorn python-multipart
    startCommand: uvicorn api.main:app --host 0.0.0.0 --port 8080
    envVars:
      - key: MISTRAL_API_KEY
        sync: false   # set manually in Render dashboard
```

Then point api.raginator.hiteshsahu.com → Render URL via Route 53 CNAME.
Frontend still goes on Amplify — it's free.

---

## Pre-load Mistral docs corpus on startup

Add to `api/main.py` lifespan:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-load Mistral docs so the demo works immediately
    if os.getenv("PRELOAD_DEMO") == "true":
        print("Pre-loading Mistral docs corpus…")
        asyncio.create_task(_preload_demo())
    yield

async def _preload_demo():
    urls = ["https://docs.mistral.ai"]
    corpus_id = "demo"
    async for event in _run_pipeline(
        corpus_id=corpus_id,
        tmp_files=[],
        urls=urls,
        embed_provider="mistral",
        store_backend="chroma",
        chunk_strategy="recursive",
        llm_provider="mistral",
    ):
        print(event)   # logs to App Runner console
```

Set `PRELOAD_DEMO=true` in App Runner env vars.
Anyone who visits raginator.hiteshsahu.com can immediately ask questions
about Mistral docs — no file upload needed.
