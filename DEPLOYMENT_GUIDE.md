# 🚀 Deployment Guide - Transport Delay Predictor

## Project Structure

This project has **3 main components**:
1. **Frontend** (Static HTML/CSS/JS) - Can deploy to Netlify/Vercel
2. **Backend** (FastAPI/Python) - Needs Python hosting
3. **ML Pipeline** (Python scripts) - Runs on backend server

## Recommended Deployment Options

### Option 1: Split Deployment (Recommended) ⭐

**Frontend → Vercel/Netlify**  
**Backend → Render/Railway/Heroku**

#### Why This Works Best:
- ✅ Vercel/Netlify excel at static sites (fast CDN)
- ✅ Render/Railway support Python/FastAPI natively
- ✅ Easy to scale each component independently
- ✅ Free tiers available for both

#### Setup Steps:

**1. Deploy Frontend to Vercel:**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd /home/jmr0xd/Workspace/frontAI
vercel
```

**2. Deploy Backend to Render:**
- Go to https://render.com
- Create new "Web Service"
- Connect GitHub repo
- Set:
  - **Build Command:** `cd backend && pip install -r requirements.txt`
  - **Start Command:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  - **Environment:** Python 3

**3. Update Frontend API URL:**
- In Vercel, add environment variable:
  - `API_BASE_URL=https://your-backend.onrender.com`
- Or update `js/api.js` to use production URL

---

### Option 2: Full-Stack on Render ⭐⭐

**Everything → Render**

#### Why This Works:
- ✅ Single platform for everything
- ✅ Native Python support
- ✅ Can serve static files from FastAPI
- ✅ Simpler deployment

#### Setup Steps:

**1. Modify FastAPI to serve static files:**
```python
# In backend/app/main.py
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="../", html=True), name="static")
```

**2. Deploy to Render:**
- Create new "Web Service"
- Build: `pip install -r backend/requirements.txt`
- Start: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

### Option 3: Vercel (Frontend) + Railway (Backend)

**Similar to Option 1, but Railway for backend**

Railway advantages:
- ✅ Very easy setup
- ✅ Auto-detects Python projects
- ✅ Free tier with $5 credit/month

---

## Quick Comparison

| Platform | Frontend | Backend | Best For |
|----------|----------|---------|----------|
| **Vercel** | ✅ Excellent | ⚠️ Serverless only | Static sites |
| **Netlify** | ✅ Excellent | ⚠️ Serverless only | Static sites |
| **Render** | ✅ Good | ✅ Excellent | Full-stack Python |
| **Railway** | ✅ Good | ✅ Excellent | Full-stack, easy setup |
| **Heroku** | ✅ Good | ✅ Good | Legacy, paid now |

---

## My Recommendation: **Option 1 (Vercel + Render)**

### Why?
1. **Vercel** = Best performance for static frontend
2. **Render** = Free tier, easy Python deployment
3. **Separation** = Easier to debug and scale

### Quick Start:

**Frontend (Vercel):**
```bash
npm i -g vercel
vercel
# Follow prompts, point to root directory
```

**Backend (Render):**
1. Go to render.com
2. New Web Service → Connect GitHub
3. Settings:
   - **Root Directory:** `backend`
   - **Build:** `pip install -r requirements.txt`
   - **Start:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables from `.env.example`

**Update Frontend:**
- Add `API_BASE_URL` in Vercel environment variables
- Or create `vercel.json`:
```json
{
  "env": {
    "API_BASE_URL": "https://your-backend.onrender.com"
  }
}
```

---

## Need Help?

I can help you:
1. ✅ Set up Vercel deployment
2. ✅ Set up Render backend
3. ✅ Configure API URLs
4. ✅ Create deployment configs

Just let me know which option you prefer!

