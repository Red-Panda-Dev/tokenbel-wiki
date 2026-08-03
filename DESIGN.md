---
# Stable, reused design values. Evidence: static/css/input.css (@theme + @apply),
# layouts/partials/head.html (Manrope), layouts/**/*.html.
colors:
  brand: blue-600        # primary actions, active links, focus rings, blockquote border
  brand_hover: blue-700  # primary button hover bg
  brand_text_hover: blue-900
  page_bg: gray-50       # <body> background
  card_bg: white
  border: gray-300       # cards, header/footer bottom, section separators
  border_subtle: gray-100 # table cells, active-link hover bg
  body_text: gray-700    # descriptions, body prose, dates
  heading_text: black    # all headings
  code_bg: gray-900
typography:
  font_sans: Manrope, Inter, system-ui, ...  # @theme --font-sans; loaded in partials/head.html
  heading_weight: font-bold
  tracking: tracking-tight # used on every heading
rounded:
  default: rounded-lg    # every card, button, image, tag, input, icon chip
shadow:
  rest: shadow-md        # cards, buttons, header, footer
  hover: shadow-xl       # card hover only
---

# DESIGN.md

## Purpose

Design contract for AI agents changing UI in the TokenBel Wiki — pages, templates,
components, styles, and user-facing copy. Derive every visual decision from existing
Hugo templates (`layouts/`) and the Tailwind source (`static/css/input.css`).

Read alongside `AGENTS.md`, `ARCHITECTURE.md`, `layouts/AGENTS.md`, and
`content/AGENTS.md`. Those define build invariants; this file defines the visual
language and how to extend it consistently.

## Product feel

- Documentation wiki: calm, text-first, scannable — not a marketing site, not a dashboard.
- Card-based surfaces on a light gray (`gray-50`) canvas; white cards with a single blue accent.
- Restrained two-color palette: **blue** for action/emphasis, **gray** for structure and text. No other hues without semantic precedent.
- Generous touch targets (min `min-h-11` / 44px) and `rounded-lg` softness everywhere.
- Russian only (locale `ru-BY`); all UI strings and content are Russian.
- Server-rendered and useful by default; motion is subtle and guarded by `motion-reduce:transition-none`.
- Trustworthy, factual tone — dates ("Опубликовано / Обновлено") and sources are first-class.

## Canonical UI examples

- `layouts/_default/baseof.html` — page shell: `bg-gray-50`, fixed header, skip link, `<main id="main-content" class="container mx-auto mt-20">`, footer `mt-auto`.
- `layouts/home.html` — landing layout: hero card → section grid → recent updates → external links. Contract for hero params.
- `layouts/_default/single.html` — article page: breadcrumbs → header (title + description + dates) → `.article-content` → tag footer.
- `layouts/_default/list.html` — section index: subsection cards above article cards, with a `.wiki-empty-state` fallback.
- `layouts/404.html` — error/empty state pattern (keep strings `Страница не найдена`, `noindex, follow`).
- `layouts/partials/section-card.html` — the one reusable card variant (icon chip + title + description).
- `layouts/partials/header.html` — desktop nav + native `<details>` mobile menu (the only "interactive" component; no JS).
- `layouts/partials/page-dates.html` — canonical date presentation (format `02.01.2006`).
- `layouts/_markup/render-table.html` + `.article-content table` rules in `static/css/input.css` — table styling.
- `static/css/input.css` — the full design contract: `@theme`, semantic component classes, prose overrides.

## Layout rules

- Wrap every page body in `.page` (`flex w-full flex-col gap-2`). It is the universal vertical-rhythm container.
- Compose pages from `.wiki-card` sections stacked with the default `gap-2`; do not introduce free-floating content without a card.
- Section order: breadcrumbs → header (`.eyebrow` label + `h1` + description) → body → optional footer.
- Summary before details: every section/card leads with a short `text-gray-700` description, then detail.
- Use the container from `baseof.html` (`container mx-auto`); do not add a second max-width wrapper inside.
- Grids: `grid grid-cols-1 gap-2 md:grid-cols-2 lg:grid-cols-3` for card collections (see home sections). Single-column `grid gap-2` for article lists.
- Fixed header is `h-16`; pages clear it via `main.mt-20`. Never remove the `mt-20` offset.
- Footer is pinned with `mt-auto`; keep it last.

## Visual language

- **Colors**: use only the palette in the frontmatter. Blue (`blue-600`) is reserved for primary actions, links, focus rings, and the blockquote accent. Gray conveys structure/body. Headings are `text-black`. Never introduce green/red/amber for status unless a concrete existing precedent exists.
- **Typography**: headings are `font-bold tracking-tight text-black`; body/description is `text-gray-700`. Use `.eyebrow` (`text-xs font-bold tracking-widest uppercase`) as the small label above section titles.
- **Headings scale** (observed): hero `text-4xl sm:text-5xl`, page `text-3xl sm:text-4xl`, section `text-2xl`, card title `text-lg`, list item `text-base`, meta `text-xs`.
- **Radius**: `rounded-lg` for every surface — cards, buttons, images, tags, inputs, icon chips. Do not mix `rounded-md`/`rounded-xl`.
- **Borders**: `border-gray-300` for card edges and separators; `border-gray-100` for table cells and the active-link hover surface.
- **Shadows**: `shadow-md` at rest on cards/buttons/header/footer; `shadow-xl` only on card hover. Do not add elevation elsewhere.
- **Images**: article images are centered and responsive via the `.article-content p > img` rules; `max-h-100` cap; `rounded-lg`.
- Apply the frontmatter values through the semantic classes in `static/css/input.css` (`@apply`), not by scattering raw utilities — but when a one-off layout needs utilities, use the exact classes already in the templates.

## Components and patterns

All reusable component classes live in `static/css/input.css` and are the contract.

- `.wiki-card` — bordered white surface, `rounded-lg`, `shadow-md`, hover `shadow-xl`. States: default (rest), hover (shadow lifts). Use for every grouped content block.
- `.wiki-button-primary` — blue solid action, `min-h-11`. States: default → hover `bg-blue-700` → focus `ring-2 ring-blue-600`.
- `.wiki-button-secondary` — white bordered action, `min-h-11`. States: default → hover `bg-gray-100 text-black` → focus `ring-2 ring-gray-500 ring-offset-2`.
- `.active-a` — inline link: `text-blue-600` → hover `text-blue-900` → focus `ring-2 ring-blue-600`. Use for all in-content and card-title links.
- `.eyebrow` — uppercase tracking label above a heading.
- `.breadcrumbs` — `Главная / Раздел / Текущая`, with `aria-current="page"` on the last item.
- `.page-dates` — `Опубликовано … / Обновлено …` row.
- `.article-content` — `prose prose-gray` wrapper (typography plugin) with project overrides (tables, images, blockquote accent).
- `.article-footer` — `border-t border-gray-300 pt-2` block for post-content elements (tags).
- `.tag-list` — pill-style tag links (`rounded-lg border-gray-300`, hover `bg-gray-100`).
- `.wiki-empty-state` — dashed `border-gray-300`, `bg-gray-50`, explanatory copy.
- `.header_btn` — desktop nav item: default → hover `bg-gray-100` → focus `ring-2 ring-gray-400`; current page gets `aria-current="page"`.

When a new reusable component is needed, add a semantic class with `@apply` to `static/css/input.css` rather than repeating long utility strings across templates.

## Interaction rules

- This is a static Hugo site. **No JavaScript framework** — do not add client-only UI, fetch/AJAX, or hydration. Content must be fully useful in the server-rendered HTML.
- The only interactive widget is the mobile menu in `header.html`, built from a native `<details>`/`<summary>` with CSS-only open/close (`group-open:hidden`). Prefer this pattern over any JS for disclosure.
- All "interactions" are CSS transitions on hover/focus. Every transition must carry `motion-reduce:transition-none`.
- Buttons/links: real `<a>`/`<button>` elements, never divs; each has a visible `:focus` ring (`focus:outline-none focus:ring-2`).
- Loading states: none — pages are static. Do not fabricate spinners.
- Empty states: use `.wiki-empty-state` with a short Russian explanation (see `list.html`, `recent-pages.html`).

## Data display rules

- Dates: human format `02.01.2006` (DD.MM.YYYY) with a matching `datetime="YYYY-MM-DD"` attribute (see `page-dates.html`). Never use ISO strings or Git-derived dates (`enableGitInfo: false` — dates come only from front matter `date`/`lastmod`).
- External product links (dashboard, tokens, bonds, shares, GitHub) come from `site.Params.*` in `hugo.yaml` — reference those params, do not hardcode URLs.
- Financial/numeric data: this wiki is reference/documentation; when numbers appear, keep them inside `.article-content` prose or tables with units labeled in Russian. No live tickers.

## Tables and charts

- Tables in articles get full styling only inside `.article-content` (borders `border-gray-100`, uppercase `gray-100` thead, hover `bg-gray-100` rows). Render hook: `layouts/_markup/render-table.html` honors Markdown column alignment.
- Keep table density consistent: `text-sm`, `p-2` cells, as already defined — do not override per-table.
- No charts library exists. Do not introduce one without explicit approval.

## User-facing text

- Russian only. Interface and content strings are Russian; technical terms stay Russian where the product uses them.
- Button labels are imperative: `На главную`, `Открыть руководство`.
- Empty/error states are explanatory and calm: `Материалы этого раздела пока готовятся.`, `Возможно, адрес изменился или материал ещё не перенесён в новую wiki.`
- Avoid implementation/English jargon in UI text. Do not expose template variables, param names, or build terms to readers.
- Preserve these exact strings (checked by `make check`): `База знаний TokenBel` (home), `Страница не найдена` (404), plus `noindex, follow` on 404.

## Accessibility basics

- Skip link to `#main-content` is in `baseof.html`; keep `id="main-content"` on `<main>`.
- Each major section uses `aria-labelledby` pointing at its heading `id` (see home/list/single).
- Active navigation: `aria-current="page"` on current menu item and last breadcrumb.
- All interactive elements have visible 44px targets (`min-h-11` / `min-w-11`) and `:focus` rings — do not remove them.
- Icon-only controls carry `sr-only` labels or `aria-label` (see mobile menu `summary`).
- Decorative SVGs use `aria-hidden="true"`; meaningful images have descriptive `alt`.
- `motion-reduce:transition-none` is mandatory on every transition — preserve it.
- Never convey status by color alone (the palette has no status colors anyway).

## Do / Don't

Do:
- Reuse the semantic classes in `static/css/input.css` (`@apply`) for any repeated pattern.
- Keep the blue+gray palette and `rounded-lg` / `shadow-md`→`shadow-xl` conventions.
- Mirror the nearest existing template's structure (card → eyebrow+heading → description → body).
- Run `make css-build` after touching `input.css` or template utility classes, then commit both `output.css` and `tailwind.min.css`.
- Validate with `make check` and at 320px width before finishing.

Don't:
- Don't introduce a third color family, new radius, or new shadow scale.
- Don't add Sass/`.scss`, a JS framework, or client-side state.
- Don't build Tailwind class strings dynamically — every class must be a complete literal token.
- Don't link `output.css` in templates; only `tailwind.min.css` is wired in `partials/css.html`.
- Don't use `localhost` or ports in `canonical`/links — canonical domain is always `https://wiki.tokenbel.info/`.
- Don't commit new images into article bundles; use the `wiki-media` CDN marker (`upload:…`) per `content/AGENTS.md`.
- Don't break the `make check` strings or remove `noindex, follow` from 404.
- Don't redesign a whole page for a small change — extend the nearest existing pattern.

## When unsure

- Inspect the closest existing template (`single.html`, `list.html`, `home.html`, `section-card.html`) and copy its structure verbatim.
- Prefer an existing semantic class over inventing utilities; if none fits, add one `@apply` class to `static/css/input.css`.
- Keep diffs minimal and palette-literal; if a decision needs a new color, radius, or component, ask before introducing it.
- Rebuild CSS (`make css-build`) and run `make check` to confirm nothing invariant broke.
