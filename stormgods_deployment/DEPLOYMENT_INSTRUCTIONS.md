# StormBuster Deployment Instructions for stormgods.us

## 🚀 Quick Deploy Options

### Option 1: Vercel (Recommended)
1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Deploy to Vercel:**
   ```bash
   cd stormgods_deployment
   vercel login
   vercel
   ```

3. **Configure Domain:**
   ```bash
   vercel domains add stormgods.us
   vercel domains add www.stormgods.us
   ```

### Option 2: Netlify (Easiest)
1. Go to https://app.netlify.com/drop
2. Drag the entire `stormgods_deployment` folder
3. Get instant URL
4. Add custom domain: stormgods.us

### Option 3: Railway
1. Go to https://railway.app
2. Connect GitHub repository
3. Upload this folder as new project
4. Set domain: stormgods.us

### Option 4: Heroku
1. Install Heroku CLI
2. Create new app: `heroku create stormgods-app`
3. Deploy: `git push heroku main`

## 🔧 Environment Variables

Set these in your hosting platform:

```
SPOKEO_EMAIL=bolison10@gmail.com
SPOKEO_PASSWORD=your_password
STRIPE_PUBLIC_KEY=your_stripe_public_key
STRIPE_SECRET_KEY=your_stripe_secret_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
FLASK_ENV=production
DOMAIN=stormgods.us
```

## 📱 Features Included

- ✅ **Storm Damage Assessment**
- ✅ **Property Search Engine**
- ✅ **AI Chat Integration** (ChatGPT, Claude, Gemini)
- ✅ **Lead Generation Pipeline**
- ✅ **Vendor Registration System**
- ✅ **Subscription Management**
- ✅ **Interactive Hail Maps**
- ✅ **Results Roofing Integration**

## 🌐 DNS Configuration

Your domain stormgods.us should point to:
- **Vercel:** 76.76.21.21 (A record)
- **Netlify:** Use their nameservers
- **Railway:** Use their domain settings

## 🎯 Post-Deployment

1. **Test the application:** https://stormgods.us
2. **Verify AI chat:** Test all AI providers
3. **Check property search:** Test Spokeo integration
4. **Test vendor registration:** Verify form submission
5. **Test subscription:** Verify Stripe integration

## 📞 Support

- **CEO:** Buster Olison
- **Lead Developer:** William Costigan
- **Phone:** (972) 818-2441
- **Email:** busterolison@results-roofing.com

---

**StormBuster - Weather Damage Lead Generation**
*"Let us take it from here - fast & easy"*
