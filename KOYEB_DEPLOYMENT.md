# Koyeb Deployment Guide

## Overview

Koyeb is a serverless platform with a **free tier** that includes:
- **1 free service** (0.1 vCPU, 256MB RAM, 2GB SSD)
- **Scale-to-zero** (no charges when idle)
- **No credit card required**
- **GitHub integration** for auto-deploy

⚠️ **Important:** Free tier = **1 service only**. You'll need to choose which to deploy first:
- **Option A:** Deploy backend only (API accessible, no frontend)
- **Option B:** Deploy frontend only (UI works, but needs backend URL)
- **Option C:** Upgrade to paid tier ($5.49/mo) for both services

---

## Step 1: Prepare Backend for Koyeb

### Create Procfile
Koyeb uses `Procfile` to know how to start your app.

```bash
# File: backend/Procfile
web: gunicorn config.app:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT --access-logfile - --error-logfile -
```

### Create runtime.txt
```bash
# File: backend/runtime.txt
python-3.12.3
```

---

## Step 2: Deploy Backend on Koyeb

### Option A: Git-Driven Deployment (Recommended)

1. Go to **https://app.koyeb.com**
2. Click **"Create App"**
3. Select **"Git"** tab
4. Connect your GitHub account (already done)
5. Select repository: **`dutchkemsystems/dutchkem-voice-agent-v3`**
6. Configure:
   - **Name:** `dutchkem-backend`
   - **Branch:** `master`
   - **Work directory:** `backend` ← **IMPORTANT: Set this!**
   - **Builder:** `Python`
7. Add **Environment Variables** (see below)
8. Click **"Deploy"**

### Environment Variables (Backend)

Add these in the Koyeb dashboard under "Environment Variables":

| Variable | Value |
|----------|-------|
| `DEBUG` | `false` |
| `SECRET_KEY` | `dutchkem-prod-S3cret-K3y-2026` |
| `JWT_SECRET` | `dutchkem-jwt-S3cret-2026` |
| `DATABASE_URL` | `sqlite:///./dutchkem.db` |
| `REDIS_URL` | `rediss://default:gQAAAAAAAtmpAAIgcDFkNzI0YWJmNzI5ZDY0ZmJjODU4ZTVkNDNiNWM2N2QyYQ@hip-walrus-186793.upstash.io:6379` |
| `CORS_ORIGINS` | `["*"]` (update later with frontend URL) |
| `ENCRYPTION_KEY` | `dutchkem-enc-2026` |

### Option B: Docker Deployment

If you prefer Docker:

1. Same steps as above, but:
   - **Builder:** `Dockerfile`
   - **Dockerfile:** `backend/Dockerfile`
2. Koyeb will use your existing Dockerfile

---

## Step 3: Deploy Frontend on Koyeb

### ⚠️ Free Tier Limitation

Koyeb free tier = **1 service only**. You have two options:

**Option 1: Deploy Frontend Instead of Backend**
- Follow same steps as backend, but:
  - **Work directory:** `frontend/web`
  - **Builder:** `Node.js`
  - **Build command:** `pnpm install && pnpm build`
  - **Start command:** `pnpm start`

**Option 2: Use Vercel for Frontend (Free)**
- Deploy frontend on **Vercel** (unlimited free deploys)
- Deploy backend on **Koyeb** (1 free service)
- This is the **recommended approach** for free tier

---

## Step 4: Recommended Free Setup

### Backend → Koyeb (Free)
### Frontend → Vercel (Free)

This gives you both services running for $0.

### Vercel Frontend Setup

1. Go to **https://vercel.com**
2. Import GitHub repo: `dutchkemsystems/dutchkem-voice-agent-v3`
3. Configure:
   - **Framework:** Next.js
   - **Root directory:** `frontend/web`
   - **Build command:** `pnpm build`
   - **Output directory:** `.next`
4. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = `https://YOUR-KOYEB-BACKEND-URL.koyeb.app`
5. Deploy

---

## Step 5: Verify Deployment

### Backend Health Check
```
https://YOUR-KOYEB-URL.koyeb.app/health
```
Expected: `{"status": "healthy"}`

### Frontend (if using Vercel)
```
https://YOUR-VERCEL-URL.vercel.app
```
Expected: Dutchkem Voice Agent UI

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Build fails** | Check Work directory is set correctly |
| **Port error** | Koyeb sets `$PORT` automatically; don't hardcode port |
| **CORS error** | Update `CORS_ORIGINS` with actual frontend URL |
| **Scale-to-zero** | Free tier scales to zero after inactivity; first request takes ~5s |

---

## Cost Summary

| Service | Platform | Cost |
|---------|----------|------|
| Backend | Koyeb | Free (1 service, 0.1 vCPU, 256MB) |
| Frontend | Vercel | Free (100GB bandwidth/mo) |
| **Total** | | **$0/month** |

---

## Upgrade Path

If you need both services on Koyeb:
- **Nano tier:** $5.49/mo (1 vCPU, 512MB RAM)
- **Additional services:** ~$5.49/mo each
