# 🚀 IngredientSight AI Deployment Checklist

Use this checklist when deploying or troubleshooting your deployment.

---

## ✅ Backend (Render) Setup

- [ ] Created Render account at https://render.com
- [ ] Connected GitHub repository
- [ ] Created new Web Service
- [ ] Set Build Command: `pip install -r requirements.txt`
- [ ] Set Start Command: `python server.py`
- [ ] Added environment variables:
  - [ ] `GEMINI_API_KEY` or `GOOGLE_API_KEY`
  - [ ] `TAVILY_API_KEY`
  - [ ] `GROQ_API_KEY` (optional)
  - [ ] `SERVER_HOST=0.0.0.0`
  - [ ] `PORT=10000`
- [ ] Backend deployed successfully
- [ ] Backend URL accessible: `https://your-backend.onrender.com`
- [ ] Health check works: Visit `https://your-backend.onrender.com/health` in browser
- [ ] No errors in Render logs

---

## ✅ Frontend (Vercel) Setup

- [ ] Created Vercel account at https://vercel.com
- [ ] Imported GitHub repository
- [ ] Framework preset set to: `Vite`
- [ ] Build Command: `npm run build`
- [ ] Output Directory: `dist`
- [ ] **Environment Variable Added:**
  - [ ] `VITE_API_URL=https://your-backend.onrender.com` ⭐ **CRITICAL!**
  - [ ] Matches your Render backend URL exactly
  - [ ] No trailing slash `/`
  - [ ] Starts with `https://`
- [ ] Frontend deployed successfully
- [ ] Frontend URL accessible: `https://your-app.vercel.app`

---

## ✅ Testing & Verification

### Initial Connection Test
- [ ] Open Vercel frontend URL in browser
- [ ] Navigate to Dashboard
- [ ] See green badge: "Backend connected :10000" (or other port)
- [ ] Error message NOT showing

### Functional Test
- [ ] Drag & drop an image onto upload area
- [ ] Release file for upload
- [ ] Pipeline stages start executing: Upload → OCR → INCI → Research → Safety → Report
- [ ] Analysis completes successfully
- [ ] Results display correctly

### If Something Fails:
- [ ] Check Render logs for Python errors
- [ ] Check browser console for JavaScript errors (F12 → Console)
- [ ] Check Network tab for failed API requests (F12 → Network)
- [ ] Verify CORS not blocking requests
- [ ] Confirm API keys in Render dashboard

---

## 🐛 Troubleshooting Common Issues

### Issue: "Backend not connected" error persists

**Checklist:**
- [ ] Is `VITE_API_URL` set in Vercel environment variables?
- [ ] Does it match your Render URL exactly (no typos)?
- [ ] Did you redeploy after setting the variable?
- [ ] Try adding a comment to trigger a new Vercel deploy
- [ ] Clear browser cache (Ctrl+Shift+Delete) and reload

### Issue: API requests fail with network error

**Checklist:**
- [ ] Can you access Render URL directly in browser?
- [ ] Are API keys set correctly in Render?
- [ ] Check Render logs for startup errors
- [ ] Backend service hasn't crashed (green status in dashboard)
- [ ] Free tier Render service might have woken up from sleep (wait 30s)

### Issue: CORS errors in console

**Should be fixed automatically**, but verify:
- [ ] Server has CORS middleware enabled (line 57-63 in server.py)
- [ ] Using `*` origins (already configured)
- [ ] Browser DevTools shows no CORS errors

### Issue: Slow first response

**Normal behavior for Render free tier:**
- [ ] First request after 15min sleep takes ~30-60 seconds
- [ ] Subsequent requests fast (~2-5 seconds)
- [ ] Consider upgrading instance if needed

---

## 📝 Environment Variables Quick Reference

### Render Backend (.env / Environment Variables):
```bash
GEMINI_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here  
TAVILY_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
SERVER_HOST=0.0.0.0
PORT=10000
```

### Vercel Frontend (Settings > Environment Variables):
```javascript
VITE_API_URL=https://your-render-backend.onrender.com
```

---

## 🔍 Files Modified for Deployment

I updated these files to support dynamic backend URLs:
- [x] `src/components/Dashboard.tsx` - Dynamic API routing
- [x] `vite.config.ts` - Environment detection
- [x] `.env.example` - Deployment instructions
- [x] `.vercelignore` - Optimize frontend build

New documentation added:
- [x] `DEPLOYMENT_GUIDE.md` - Complete deployment walkthrough
- [x] `FIX_SUMMARY.md` - Quick fix reference

---

## 💡 Pro Tips

1. **Test locally first**: Run both servers locally before deploying
   ```bash
   # Terminal 1: Backend
   python server.py
   
   # Terminal 2: Frontend  
   npm run dev
   ```

2. **Use preview deployments**: Each push creates a preview URL to test changes

3. **Monitor usage**: 
   - Render: Dashboard → Your Service → Metrics
   - Vercel: Dashboard → Your Project → Analytics

4. **Enable auto-deploy**: Both platforms auto-deploy on git push to main

5. **Keep .env secure**: Never commit actual API keys to GitHub!

---

## 🎯 Success Criteria

Your deployment is successful when:
- [ ] Frontend loads without errors at your Vercel URL
- [ ] Backend badge shows green ("Backend connected")
- [ ] You can upload images successfully
- [ ] Pipeline completes and shows results
- [ ] Download reports work (.md and .json)
- [ ] No console errors in browser DevTools

---

## 🆘 Getting Help

If stuck:
1. Review Render dashboard logs
2. Review Vercel deploy logs
3. Check browser DevTools (Console + Network tabs)
4. Compare against this checklist
5. Read full guide: [`DEPLOYMENT_GUIDE.md`](./DEPLOYMENT_GUIDE.md)

---

**Happy deploying! 🎉**
