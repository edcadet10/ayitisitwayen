# Ayiti Sitwayen - Deployment Guide

## 🚀 Deploy to GitHub + Vercel (Step-by-Step)

### Step 1: Push to GitHub

1. **Initialize Git Repository**
   ```bash
   cd C:/Users/jcade/Ayiti_Sitwayen_Website
   git init
   git add .
   git commit -m "Initial commit: Ayiti Sitwayen website"
   ```

2. **Create GitHub Repository**
   - Go to [github.com](https://github.com)
   - Click "New Repository"
   - Name: `ayiti-sitwayen-website`
   - Description: "Official website for Ayiti Sitwayen campaign"
   - Keep it Public or Private (your choice)
   - DON'T initialize with README (we already have one)
   - Click "Create Repository"

3. **Push to GitHub**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/ayiti-sitwayen-website.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy to Vercel

1. **Sign Up for Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "Sign Up"
   - Choose "Continue with GitHub"
   - Authorize Vercel to access your GitHub

2. **Import Project**
   - Click "Add New Project"
   - Find `ayiti-sitwayen-website` in your repository list
   - Click "Import"

3. **Configure Project**
   - Project Name: `ayiti-sitwayen` (or keep default)
   - Framework Preset: **Other** (it's plain HTML)
   - Root Directory: `./` (default)
   - Build Command: Leave empty
   - Output Directory: Leave empty
   - Install Command: Leave empty

4. **Deploy**
   - Click "Deploy"
   - Wait 30-60 seconds
   - Done! Your site is live at `https://ayiti-sitwayen.vercel.app`

### Step 3: Connect Custom Domain (ayitisitwayen.org)

1. **Add Domain in Vercel**
   - In your Vercel project dashboard
   - Go to "Settings" → "Domains"
   - Add domain: `ayitisitwayen.org`
   - Add www subdomain: `www.ayitisitwayen.org`

2. **Update DNS at Your Domain Registrar**

Vercel will show you DNS records to add. It will look like this:

**For ayitisitwayen.org:**
```
Type: A
Name: @
Value: 76.76.21.21
```

**For www.ayitisitwayen.org:**
```
Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

**Where to add these:**
- If you bought domain at Namecheap: Dashboard → Domain List → Manage → Advanced DNS
- If you bought at GoDaddy: My Products → DNS → Manage Zones
- If you bought at Google Domains: DNS → Custom records

3. **Wait for DNS Propagation**
   - Usually takes 5-30 minutes
   - Can take up to 48 hours in rare cases
   - Vercel will automatically verify and issue SSL certificate

4. **Done!**
   - Your site will be live at `https://ayitisitwayen.org`
   - Automatic HTTPS (SSL certificate)
   - Automatic redirects (www → non-www or vice versa)

---

## 📧 Set Up Contact Form

### Option 1: Formspree (Recommended - FREE)

1. **Sign Up**
   - Go to [formspree.io](https://formspree.io)
   - Sign up with email

2. **Create Form**
   - Click "New Form"
   - Name it "Ayiti Sitwayen Contact"
   - Copy your form endpoint: `https://formspree.io/f/YOUR_FORM_ID`

3. **Update index.html**
   - Find line 318 in `index.html`
   - Replace `YOUR_FORM_ID` with your actual form ID

4. **Test**
   - Submit a test message from your live site
   - Check your email - you should receive the form submission

### Option 2: EmailJS (Alternative - FREE)

1. Go to [emailjs.com](https://www.emailjs.com/)
2. Create account
3. Set up email service
4. Create template
5. Get Service ID, Template ID, Public Key
6. Update `script.js` with EmailJS integration code

---

## 🔄 Update Website After Deployment

**Every time you make changes:**

1. **Edit files** locally
2. **Test locally** (open `index.html` in browser)
3. **Commit changes**:
   ```bash
   git add .
   git commit -m "Update: description of what you changed"
   git push
   ```
4. **Automatic deployment**: Vercel detects the push and auto-deploys (30 seconds)

---

## ✅ Post-Deployment Checklist

After your site is live, check these:

- [ ] Site loads at `https://ayitisitwayen.org`
- [ ] SSL certificate shows (padlock icon in browser)
- [ ] Language toggle works (HT ↔ EN)
- [ ] All navigation links work
- [ ] Contact form submits successfully
- [ ] Mobile responsive (test on phone)
- [ ] All social media links updated (currently placeholder)
- [ ] Team member info added (currently placeholder)
- [ ] Formspree form ID updated (currently `YOUR_FORM_ID`)

---

## 🔐 Set Up Professional Emails

### Option 1: Google Workspace (Recommended - $6/month)

1. Go to [workspace.google.com](https://workspace.google.com)
2. Start free trial
3. Verify domain ownership
4. Create emails:
   - contact@ayitisitwayen.org
   - research@ayitisitwayen.org
   - partnerships@ayitisitwayen.org

### Option 2: Zoho Mail (FREE for 5 users)

1. Go to [zoho.com/mail](https://www.zoho.com/mail/)
2. Sign up for free plan
3. Add domain
4. Verify ownership
5. Create email addresses

### Option 3: Email Forwarding (FREE)

If you bought domain at Namecheap/GoDaddy:
1. Set up email forwarding in domain control panel
2. Forward all @ayitisitwayen.org emails to your personal Gmail
3. Reply from Gmail (less professional, but free)

---

## 📊 Add Analytics (Optional)

### Google Analytics

1. Go to [analytics.google.com](https://analytics.google.com)
2. Create account and property
3. Get tracking ID (G-XXXXXXXXXX)
4. Add to `<head>` of `index.html`:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

---

## 🎨 Customize for Your Needs

### Update Team Section

In `index.html`, find the Team section (around line 285):

```html
<div class="team-member">
    <div class="member-photo">
        <div class="photo-placeholder">👤</div>
    </div>
    <h3 class="member-name">[Your Name]</h3>
    <p class="member-role" data-ht="Chèchè Prensipal" data-en="Principal Researcher">
        Chèchè Prensipal
    </p>
    <p class="member-bio" data-ht="[Your bio in Creole]" data-en="[Your bio in English]">
        [Your bio]
    </p>
</div>
```

### Add Social Media Links

In `index.html`, find Contact section (around line 346):

```html
<div class="social-links">
    <a href="https://facebook.com/ayitisitwayen" target="_blank">Facebook</a>
    <a href="https://instagram.com/ayitisitwayen" target="_blank">Instagram</a>
    <a href="https://tiktok.com/@ayitisitwayen" target="_blank">TikTok</a>
</div>
```

---

## ❓ Troubleshooting

### Site not loading after deployment
- Wait 5 minutes (DNS propagation)
- Clear browser cache (Ctrl+Shift+R)
- Check Vercel deployment logs

### Custom domain not working
- Verify DNS records are correct
- Wait up to 48 hours for DNS propagation
- Use [whatsmydns.net](https://www.whatsmydns.net/) to check propagation

### Contact form not working
- Check Formspree form ID is correct
- Check email spam folder
- Try different email address

### SSL certificate error
- Vercel auto-issues SSL - just wait 5-10 minutes
- If persists after 1 hour, contact Vercel support

---

## 📞 Need Help?

- **Vercel Docs**: https://vercel.com/docs
- **GitHub Docs**: https://docs.github.com
- **Formspree Docs**: https://help.formspree.io

---

## 🎯 Next Steps After Deployment

1. **Test everything** (checklist above)
2. **Fill in TikTok Research API application** with website URL
3. **Update all campaign materials** with website link
4. **Share on social media**
5. **Add to email signature**
6. **Include in funding proposals**

---

**Your website is ready to go! 🚀**

Live URL: https://ayitisitwayen.org (once DNS configured)
Staging URL: https://ayiti-sitwayen.vercel.app (available immediately)
