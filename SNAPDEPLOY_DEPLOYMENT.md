# SnapDeploy Deployment Guide

## Overview

This project deploys as **two separate containers** on SnapDeploy:
- **Backend** (Python/FastAPI) — root directory: `/backend`
- **Frontend** (Next.js) — root directory: `/frontend/web`

Both services use existing Dockerfiles in the repo.

---

## Step 1: Create SnapDeploy Account

1. Go to https://snapdeploy.dev/register
2. Sign up with GitHub (recommended) or email
3. Verify your email if required

---

## Step 2: Connect GitHub Repository

1. Go to **Dashboard → Settings → GitHub Integration**
2. Click **"Connect GitHub"**
3. Authorize SnapDeploy in the GitHub OAuth popup
4. Select repository: `DUTCHKEM-VENTURES-VOICE-AGENT-V3`

---

## Step 3: Deploy Backend Service

### Create Project
1. Click **"New Project"** or **"Deploy"**
2. Select your repository: `DUTCHKEM-VENTURES-VOICE-AGENT-V3`
3. **Root Directory**: `/backend`
4. Click **"Deploy"**

### Configure Environment Variables
Go to **Dashboard → your backend project → Settings → Environment Variables** and add:

| Variable | Value |
|----------|-------|
| `DEBUG` | `false` |
| `SECRET_KEY` | *(auto-generate or use: `dutchkem-prod-secret-key-2026`)* |
| `JWT_SECRET` | *(auto-generate or use: `dutchkem-jwt-secret-2026`)* |
| `DATABASE_URL` | `sqlite:///./dutchkem.db` |
| `MONGODB_URL` | *(leave empty or use external MongoDB if needed)* |
| `REDIS_URL` | `rediss://default:gQAAAAAAAtmpAAIgcDFkNzI0YWJmNzI5ZDY0ZmJjODU4ZTVkNDNiNWM2N2QyYQ@hip-walrus-186793.upstash.io:6379` |
| `CORS_ORIGINS` | `["https://YOUR-frontend-domain.snapdeploy.app"]` |
| `ENCRYPTION_KEY` | *(auto-generate or use: `dutchkem-encryption-key-2026`)* |

### Note on CORS_ORIGINS
After deploying the frontend, replace `YOUR-frontend-domain.snapdeploy.app` with the actual frontend URL.

---

## Step 4: Deploy Frontend Service

### Create Project
1. Click **"New Project"** again
2. Select same repository: `DUTCHKEM-VENTURES-VOICE-AGENT-V3`
3. **Root Directory**: `/frontend/web`
4. Click **"Deploy"**

### Configure Environment Variables
Go to **Dashboard → your frontend project → Settings → Environment Variables** and add:

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | `https://YOUR-backend-domain.snapdeploy.app` |

### Note on NEXT_PUBLIC_API_URL
After deploying the backend, replace `YOUR-backend-domain.snapdeploy.app` with the actual backend URL.

---

## Step 5: Update CORS Origins

Once both services are deployed:
1. Go to **Backend project → Settings → Environment Variables**
2. Update `CORS_ORIGINS` with the actual frontend URL:
   ```
   ["https://dutchkem-frontend-xxxxx.snapdeploy.app"]
   ```
3. The backend will auto-restart with the new CORS configuration

---

## Step 6: Verify Deployment

### Backend Health Check
```
https://YOUR-backend-domain.snapdeploy.app/health
```
Should return: `{"status": "healthy"}`

### Frontend
```
https://YOUR-frontend-domain.snapdeploy.app
```
Should load the Dutchkem Voice Agent UI

---

## Free Tier Limits

- **10 deploys per day** (across all projects)
- **512 MB RAM** per container
- **0.25 vCPU** per container
- **Auto-sleep** after 45 minutes of inactivity
- **Auto-wake** on incoming traffic (10-30 seconds)

---

## Troubleshooting

### Build Fails
- Check **Dashboard → your project → Logs** for build errors
- Ensure Dockerfile paths are correct (backend uses `requirements/production.txt`)

### Frontend Can't Connect to Backend
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check `CORS_ORIGINS` includes the frontend URL
- Ensure backend `/health` endpoint is responding

### Environment Variables Not Working
- SnapDeploy auto-restarts containers when env vars change
- Check **Logs** for any configuration errors
- Verify variable names match exactly (case-sensitive)

---

## Cost

**Free tier**: $0/month (10 deploys/day, auto-sleep)
**Always-On**: $12/month per container (no sleep)

For a production setup, consider Always-On for the backend to avoid cold starts.
