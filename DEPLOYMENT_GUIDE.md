# 🚀 Deployment Guide: IngredientSight AI

This guide walks you through deploying your frontend on **Vercel** and backend on **Render**.

## 📁 Architecture Overview

- **Frontend**: React + Vite deployed on **Vercel**
- **Backend**: FastAPI + Python deployed on **Render**
- **Communication**: Frontend calls backend via HTTPS API endpoints

---

## 🔧 Prerequisites

1. GitHub account with your code pushed to a repository
2. Vercel account (https://vercel.com)
3. Render account (https://render.com)
4. API keys configured in `.env` file:
   - `GEMINI_API_KEY` or `GOOGLE_API_KEY`
   - `TAVILY_API_KEY` (recommended)
   - `GROQ_API_KEY` (optional)

---

## 🐘 Step 1: Deploy Backend to Render

### 1.1 Create Render Account
Go to https://render.com and sign up/login.

### 1.2 Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Select your repo

### 1.3 Configure Service Settings

**Basic Configuration:**
- **Name**: `ingredientsight-ai-backend` (or your preferred name)
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Root Directory**: Leave blank (or specify if your app is in a subdirectory)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python server.py`
- **Instance Type**: **Free** (for development/testing)

### 1.4 Add Environment Variables
Click **"Environment"** tab and add these variables:

```
GEMINI_API_KEY=your_actual_gemini_key_here
GOOGLE_API_KEY=your_actual_google_key_here  
TAVILY_API_KEY=your_actual_tavily_key_here
GROQ_API_KEY=your_actual_groq_key_here
SERVER_HOST=0.0.0.0
PORT=10000
```

**⚠️ IMPORTANT**: Make sure your `.env` values match these environment variables exactly!

### 1.5 Deploy
Click **"Create Web Service"**. Wait ~2-3 minutes for deployment to complete.

Once done, you'll get a URL like:
```
https://ingredientsight-ai-backend.onrender.com
```

Save this URL - you'll need it for Vercel configuration!

---

## 🎨 Step 2: Deploy Frontend to Vercel

### 2.1 Create Vercel Account
Go to https://vercel.com and sign up/login.

### 2.2 Import Your Project
1. Click **"Add New..."** → **"Project"**
2. Import your GitHub repository
3. Keep default settings:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `.` (same as repo)
   - **Build Command**: `npm run build`
   - **Install Command**: `npm install`
   - **Output Directory**: `dist`

### 2.3 Configure Environment Variables ⭐ CRITICAL STEP

Before deploying, you MUST set the backend URL:

1. Click **"Environment Variables"** section
2. Add a new variable:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://ingredientsight-ai-backend.onrender.com` 
     (Replace with YOUR actual Render backend URL)
   - **Environments**: Select `"Production"` and `"Preview"`

3. Click **"Apply"**

**Why this is important**: This tells your frontend where to find the backend API. Without it, your frontend will try to connect to `localhost:8000` which doesn't work in production.

### 2.4 Deploy
1. Click **"Deploy"**
2. Wait ~30 seconds for deployment
3. You'll get a URL like:
   ```
   https://ingredientsight-ai.vercel.app
   ```

---

## ✅ Step 3: Verify Everything Works

### 3.1 Test Your Frontend
1. Open your Vercel URL in browser
2. Navigate to Dashboard
3. Check the backend connection status (top right corner)

**Expected**: Green badge saying "Backend connected :port_number"

### 3.2 If You See "Backend not connected"

#### Check List:
- [ ] Is your Render backend running? Visit your Render URL directly
- [ ] Does `VITE_API_URL` match your Render URL exactly?
- [ ] Did you redeploy Vercel after setting `VITE_API_URL`?
- [ ] Are CORS settings correct on backend? (Already configured by default)

#### Debug Steps:
1. **Open Browser DevTools** (F12)
2. Go to **Network** tab
3. Try uploading an image
4. Look for failed requests and check:
   - Request URL matches your Render URL
   - CORS errors in console

### 3.3 Common Error Messages & Fixes

**Error**: "Backend not connected - localhost:8000"
**Fix**: Set `VITE_API_URL=https://your-render-app.onrender.com` in Vercel and redeploy

**Error**: "Failed to fetch" or "Network error"
**Fix**: 
1. Check Render backend logs for errors
2. Verify backend is accessible (visit Render URL in browser)
3. Ensure API keys are set correctly in Render

**Error**: "Pipeline execution failed"
**Fix**: Check Render backend logs for specific error message

---

## 🔍 Troubleshooting

### Backend Issues

#### Render shows "Crashed" or "Startup Failed"
1. Check Render dashboard → Logs
2. Common causes:
   - Missing API keys
   - Python dependency errors
   - Port conflicts

#### Can access Render URL but no response
Visit `https://your-backend.onrender.com/health` manually
Should return JSON with backend status

### Frontend Issues

#### Frontend loads but can't connect to backend
1. Verify `VITE_API_URL` in Vercel settings
2. Must start with `https://` - no trailing slash
3. Redeploy after changing environment variables

#### CORS errors
Your backend already has CORS configured (`server.py` line 57-63), should be automatic.

---

## 🔄 Updating After Changes

### Change Backend Code
1. Push changes to GitHub
2. Render automatically deploys on push to main branch
3. Wait 1-2 minutes
4. Test your Render URL

### Change Frontend Code  
1. Push changes to GitHub
2. Vercel automatically deploys on push
3. Each deploy creates a preview URL
4. Production update happens automatically

### Update Backend URL
If you change your Render service name:
1. Get new URL from Render dashboard
2. Update `VITE_API_URL` in Vercel Environment Variables
3. Redeploy Vercel project

---

## 📝 Quick Reference

### Render Backend Configuration
```yaml
Service Type:       Web Service
Build Command:      pip install -r requirements.txt
Start Command:      python server.py
Instance Type:      Free
Environment Vars:   GEMINI_API_KEY, TAVILY_API_KEY, etc.
URL Pattern:        https://<service-name>.onrender.com
```

### Vercel Frontend Configuration
```yaml
Framework:          Vite
Build Command:      npm run build
Output Directory:   dist
Environment Vars:   VITE_API_URL=https://backend.onrender.com
URL Pattern:        https://<project-name>.vercel.app
```

---

## 🛡️ Security Notes

1. **Never commit `.env` file** - it's gitignored ✓
2. **Use Render Environment Variables** for API keys (not .env file)
3. **Use Vercel Environment Variables** for `VITE_API_URL`
4. **Rotate keys** if they appear in git history

---

## 💰 Cost Considerations

### Render (Free Tier)
- ✅ Free web service available
- ⚠️ Sleep after 15 minutes of inactivity
- ⚠️ First load after sleep takes ~30-60 seconds
- ✅ Perfect for development/testing

### Vercel (Free Tier)
- ✅ Unlimited public projects
- ✅ Generous bandwidth limits
- ✅ Automatic HTTPS
- ✅ Global CDN

---

## 🎯 Next Steps

After successful deployment:
1. Test all dashboard features end-to-end
2. Share your Vercel URL with friends
3. Monitor Render logs for usage patterns
4. Consider upgrading Render instance if you get more traffic

---

## 📞 Support

If you encounter issues:
1. Check Render dashboard → Logs
2. Check Vercel dashboard → Deploy logs
3. Open browser DevTools → Console/Network tabs
4. Review README.md for troubleshooting tips

---

**Happy Deploying! 🚀**

Your IngredientSight AI platform is now live and serving cosmetic safety analyses worldwide!
