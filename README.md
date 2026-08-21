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
