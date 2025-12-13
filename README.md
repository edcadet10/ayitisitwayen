# Ayiti Sitwayen

**Ranfòse angajman sivik nan Ayiti** | **Strengthening civic engagement in Haiti**

## About

Ayiti Sitwayen is a research and action project using social media technology and machine learning to strengthen active citizenship in Haiti. This website serves as the public-facing platform for our research and campaign.

## Website

- **Production**: https://ayitisitwayen.org
- **Staging**: https://ayiti-sitwayen.vercel.app

## Features

- Bilingual content (Haitian Creole / English)
- Responsive design (mobile-first)
- Research documentation
- Contact form integration
- Haiti flag color scheme (Blue & Red)

## Technology Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Hosting**: Vercel
- **Domain**: Ayitisitwayen.org
- **Form Backend**: Formspree (to be configured)

## Local Development

1. Clone this repository
2. Open `index.html` in your browser
3. No build process required - it's pure HTML/CSS/JS!

## Deployment

This site is automatically deployed to Vercel when you push to the `main` branch.

### Deploy to Vercel (First Time)

1. Push this code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Click "Import Project"
4. Connect your GitHub repository
5. Click "Deploy"
6. Done! Your site will be live at `[your-project].vercel.app`

### Connect Custom Domain

1. In Vercel dashboard, go to your project
2. Click "Settings" → "Domains"
3. Add `ayitisitwayen.org`
4. Follow instructions to update your DNS settings at your domain registrar

## File Structure

```
Ayiti_Sitwayen_Website/
├── index.html          # Main HTML file
├── styles.css          # All styles
├── script.js           # JavaScript functionality
├── README.md           # This file
├── .gitignore         # Git ignore file
└── vercel.json        # Vercel configuration
```

## Customization

### Update Team Member

Edit the Team section in `index.html`:

```html
<div class="team-member">
    <div class="member-photo">
        <div class="photo-placeholder">👤</div>
    </div>
    <h3 class="member-name">Your Name</h3>
    <p class="member-role">Your Role</p>
    <p class="member-bio">Your bio here...</p>
</div>
```

### Update Contact Email

1. Sign up at [Formspree.io](https://formspree.io)
2. Create a new form
3. Copy your form endpoint URL
4. Replace `YOUR_FORM_ID` in `index.html` line 318:

```html
<form class="contact-form" action="https://formspree.io/f/YOUR_FORM_ID" method="POST">
```

### Add Social Media Links

Update the social links in the Contact section (around line 346):

```html
<div class="social-links">
    <a href="https://facebook.com/ayitisitwayen" target="_blank">Facebook</a>
    <a href="https://instagram.com/ayitisitwayen" target="_blank">Instagram</a>
    <a href="https://tiktok.com/@ayitisitwayen" target="_blank">TikTok</a>
</div>
```

## Language Toggle

The website supports bilingual content. Users can switch between Haitian Creole and English by clicking the language toggle button in the navigation.

All translatable content uses `data-ht` and `data-en` attributes:

```html
<h2 data-ht="Konsènan Pwojè a" data-en="About the Project">
    Konsènan Pwojè a
</h2>
```

## Contributing

This is a research project website. If you'd like to contribute or report issues, please contact us at contact@ayitisitwayen.org

## License

© 2025 Ayiti Sitwayen. All rights reserved.

## Contact

- **Email**: contact@ayitisitwayen.org
- **Research Email**: research@ayitisitwayen.org
- **Partnerships**: partnerships@ayitisitwayen.org

---

**Ayiti Sitwayen** | Renforcer l'engagement civique en Haïti
