# mythen.io: the studio site

A small static site: a home for Kellan's games and the developer website ad networks check (AppLovin MAX, AdMob).
- No build step, no analytics, no cookies, no forms.
- Strata's own pages stay where they are, at kellanm.github.io/strata.

| File | What |
|---|---|
| `index.html` | Introduction, and Strata: what it is, three screenshots, "Coming soon on iPhone", Play on the web, contact |
| `privacy.html` | Privacy for the site and for Strata. It covers v1 (nothing collected) and, marked as future, the AppLovin MAX section AppLovin requires (their required sentence and link, opt-outs, ATT). Update it before ads ship |
| `terms.html` | Short terms of use (Apple's standard EULA plus a few lines). MAX's consent flow can link it |
| `support.html` | The email, plus a link to Strata's full help page, and "Report an ad" (Apple 2.5.18) |
| `app-ads.txt` | Comments only, until AppLovin gives the lines. **Must be served at `https://mythen.io/app-ads.txt` directly, not through a redirect** |
| `robots.txt` | Allows crawling, including `app-ads.txt` |
| `strata/` | The icon (the 3×3×3 stone on lime) and small copies of three store screenshots |

## Deployment plan (nothing changed yet; needs Kellan's approval)

**Recommendation: host the site directly on mythen.io, not by forwarding.** Forwarding (a registrar redirect to another URL) won't serve `app-ads.txt` at `https://mythen.io/app-ads.txt` itself. AppLovin allows only one redirect outside the root domain, and crawlers should get the file directly.

1. **A repo for the site,** e.g. `KellanM/mythen.io` (public; Kellan runs `gh repo create KellanM/mythen.io --public`). Copy this folder's contents to its root. Add a `CNAME` file containing `mythen.io`. Turn on GitHub Pages: Settings › Pages › Deploy from branch `main`, root.
2. **DNS for mythen.io:**
   - **Add only:**
     - apex `A` records 185.199.108.153, 185.199.109.153, 185.199.110.153 and 185.199.111.153;
     - optionally `AAAA` records 2606:50c0:8000::153, 2606:50c0:8001::153, 2606:50c0:8002::153 and 2606:50c0:8003::153;
     - `www` as a `CNAME` to `kellanm.github.io`.
   - **Leave every existing MX and TXT record exactly as it is** (support@mythen.io's mail, SPF, DKIM, DMARC and any verification records).
   - If the apex already has A/ALIAS/URL-forward records, those are what get replaced. List them for Kellan before changing anything.
3. **Turn on GitHub Pages' "Enforce HTTPS"** once the certificate is issued (minutes to an hour).
4. **Check:**
   - `https://mythen.io/` and `https://mythen.io/app-ads.txt` both return 200, the second as `text/plain`;
   - `www` redirects to the apex;
   - email to support@mythen.io still arrives.
5. **Later, with Strata v1.1 (ads):**
   - point the App Store listing's Marketing, Support and Privacy Policy URLs at mythen.io; Apple only lets them change with a new version, and ad crawlers read the domain from them;
   - register `mythen.io` in AppLovin (Account › General › Basic Info › Domain);
   - paste the app-ads.txt lines.

**Alternative:** host it on the existing Strata repo's Pages. Not recommended: a custom domain there would move the playable game to the domain root and break existing Home Screen installs.

## Open decisions (Kellan's)

- **Whose site is mythen.io: decided** (Kellan, 2026-10-28). It is Kellan's own: "Unsupervised Rock is Kellan Mythen", © Kellan Mythen. The family's Mythen LLC is not involved and must not be named. A new LLC for the studio is being considered. If it's formed, its exact legal name replaces the © line and becomes the App Store seller (an organisation account, with a D-U-N-S number). Do it before v1.1's ads earn money.
- **The App Store seller name** shown on Strata's listing (individual account: Kellan's name). Ad networks compare it with this site, so the site may need to name the person or company the store shows.
