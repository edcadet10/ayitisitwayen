# Country default and explicit language choice

Normal browser document navigation uses Vercel's IP-country header: `HT` selects
Haitian Creole; other or unknown countries select English. This applies to every
translated HTML section, article, candidate, directory and archive URL. Browser
language and GPS permissions do not determine the default.

An explicit language switch writes the `ayiti_lang` preference cookie (one year,
Secure, SameSite=Lax, site-wide path) and the existing localStorage preference.
The cookie takes priority over geography. The legacy script migrates previously
saved browser choices before redirecting, preventing country/preference loops.

Conditional temporary redirects require the standard `Sec-Fetch-Dest: document`
navigation header. Media, scripts, APIs, source catalogues, RSS and sitemaps are
not redirected. Native fetches retain the requested language URL and its HTML;
there is no user-agent or search-crawler allowlist. Both language versions keep
their existing canonical and reciprocal hreflang metadata.

The only HTML route without an English counterpart is the shared Haitian Creole
audio transcript. The language of a recording is explicitly labeled.

`python scripts/check-language-routing.py` checks the contract against every
paired sitemap URL, manual overrides, unknown countries, non-navigation fetches,
assets and redirect loops. Hosted browser verification checks real document
navigation, switches in all three script families, query/hash retention and
cross-section persistence. Simulated country inputs are distinguished from an
actual connection in Haiti; a VPN or proxy can change the detected country.

Primary references:

- https://vercel.com/docs/project-configuration/vercel-json
- https://vercel.com/docs/headers/request-headers
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Sec-Fetch-Dest
- https://developers.google.com/search/docs/specialty/international/locale-adaptive-pages
