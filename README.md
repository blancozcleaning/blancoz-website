# Blancoz Cleaning - website

The five-page Blancoz Cleaning site: Home, Our Company, Services, Contact, and the
credentials page.

**Live:** https://blancozcleaning.github.io/blancoz-website/

The `blancoz.cleaning` domain does **not** point here yet. Repointing it is a change at
the domain registrar and is the remaining step to make this the real site.

## Files

| File | What it is |
| --- | --- |
| `index.html` | The published page, ~55KB. Safe to edit by hand, see below. |
| `blancoz-site-template.html` | The same page with `__IMG_*__` placeholders instead of image data. Edit this, not `index.html`. |
| `img/` | The 24 photographs, as real files with search-friendly names. Not base64, because Google Images cannot index a data URI. |
| `build_site.py` | Rebuilds `index.html` from the template: copies the photos into `img/` and substitutes every `__IMG_*__` placeholder. One command, does the lot. |
| `.nojekyll` | Stops GitHub Pages running the file through Jekyll. |

## Rebuilding after a copy change

1. Edit `blancoz-site-template.html`.
2. Run `python3 build_site.py`. It writes `index.html` for you, images and all.
3. Commit and push. GitHub Pages redeploys automatically.

Vercel serves the same page from `~/code/blancoz-vercel-deploy`, so a change is not
everywhere until that is deployed too.

## Design decisions worth keeping

- Strictly black, white and grey. The photographs are rendered in mono, so the
  photography is the only colour on the page. That is the brand rule, not a preference.
- Archivo for display and interface, Newsreader for body copy. The serif signals
  "family owned since 2008" and separates Blancoz from every competitor's generic
  sans-serif site.
- The credentials render as a hairline ledger strip rather than badges, because the
  compliance evidence is the product: Labour Hire Authority licence, police-checked
  staff, Working With Children Checks, $20M public liability, WorkCover.
- Theme-aware light and dark, with tokens defined on bare `:root` so the default
  "system" state works rather than falling through to an unstyled page.
- No numbered eyebrows on the services. They are not a sequence, so numbering them
  would be decoration pretending to be information.

## Known gap

The site publishes no ABN. The correct one is **59 169 925 616**, and as of 20 August 2026
the structure is confirmed legitimate: Blancoz Pty Ltd (ACN 650 655 860) acts as trustee
for the Blancoz Trust, and the ABN is a trust ABN. That is normal and not a discrepancy.

Still open before an ABN goes in the footer: **"Blancoz Cleaning" does not appear on the
Business Names Register** against that ABN (the only name registered there is "Actions
Drive Results"). Publishing an ABN beside an unregistered trading name invites the
question. Settle the business name first, then add the ABN.

## Editing the site by hand

`index.html` is the file the world sees, and it is safe to edit directly in the GitHub web editor.

`build_site.py` regenerates `index.html` from `blancoz-site-template.html`, so a careless rebuild
could overwrite hand edits. It cannot: after each build the script records a checksum in
`.index.build.sha256`, and it refuses to run if `index.html` no longer matches. If you edit
`index.html`, the next build stops and tells you to port the change into the template first.

## The header logotype is a generated transparent PNG

`assets/logotype.jpg` is a black wordmark on a solid white plate. Placed in the header
it shows as a white box, and the `mix-blend-mode` that used to hide it does not work,
because the header's `backdrop-filter` isolates the element from what is behind it.

`make_transparent_logo.py` cuts a real transparent PNG from that JPEG with a luminance
key: white to fully transparent, black to fully opaque, the greys in between to matching
partial alpha. That preserves the antialiased edges and opens the counters inside the
letters and the crescent inside the mark. It upscales 3x first, because the source is
only 331x107 and the header renders it at 64px on 2-3x phone screens.

Re-run it only if `assets/logotype.jpg` is ever replaced:

```
python3 make_transparent_logo.py   # writes assets/logotype-transparent.png
python3 build_site.py              # copies it into img/blancoz-cleaning-logo.png
```

Because the PNG is genuinely transparent, dark mode needs nothing but `filter:invert(1)`.

## A defect class worth knowing about in this stylesheet

Twice now a section has "looked wrong" and the cause was a CSS selector that never
matched, not a value that needed tuning:

- `.ledger > div` was styled, but the markup is `.ledger > li > div`, so the credentials
  strip had no column padding and no dividers at all.
- The mobile header rules sat BEFORE the base `.brand` / `nav.main` rules they were meant
  to override. Equal specificity means source order wins, so every declaration in that
  media query was dead and the nav wrapped into two lopsided rows on a phone.

Before adjusting a value, confirm the selector actually matches. `make_transparent_logo.py`
and `build_site.py` are checked; the stylesheet is worth a sweep.

## Deploying

GitHub Pages redeploys itself on push. Vercel does not, and it is served from a
separate staging directory (`~/code/blancoz-vercel-deploy`) rather than a checkout.

Use `./deploy_vercel.sh`. It mirrors rather than copies: images the current build no
longer produces are removed from the staging directory before the deploy. Copying
alone leaves renamed or dropped photos sitting there, publicly reachable, long after
GitHub Pages has correctly started 404ing them. That has already happened twice.

```
python3 build_site.py
git add -A && git commit && git push     # GitHub Pages
./deploy_vercel.sh                       # Vercel
```

Always `git fetch` and check `origin/main` before rebuilding. Juan edits `index.html`
directly in the GitHub web editor, and `index.html` is generated, so an unported hand
edit is silently destroyed by the next build. The checksum guard in `build_site.py`
catches local edits; it cannot see edits that only exist on the remote.
