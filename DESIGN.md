---
colors:
  primary: "#2563eb"
  primary_hover: "#1d4ed8"
  primary_light: "#1e40af"
  text: "#000000"
  text_secondary: "#374151"
  text_muted: "#6b7280"
  bg: "#f9fafb"
  bg_card: "#ffffff"
  border: "#d1d5db"
  border_light: "#e5e7eb"
typography:
  font_family: "Manrope, Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, sans-serif"
  locale: "ru-BY"
rounded:
  default: "0.5rem"
  card: "0.5rem"
spacing:
  unit: "0.5rem"
  card_padding: "0.5rem"
  card_padding_sm: "1rem"
  card_padding_md: "1.5rem"
  container: "1rem"
components:
  card: "wiki-card"
  button_primary: "wiki-button-primary"
  button_secondary: "wiki-button-secondary"
  link: "active-a"
  eyebrow: "eyebrow"
  breadcrumbs: "breadcrumbs"
  pagination: "wiki-pagination"
  empty_state: "wiki-empty-state"
  article: "article-content"
  tag_list: "tag-list"
  page_dates: "page-dates"
  header_btn: "header_btn"
---

# DESIGN.md

## Purpose

This file defines UI rules for AI agents working on the TokenBel Wiki repository. Use it when changing pages, templates, components, styles, forms, filters, charts, or user-facing copy. See `AGENTS.md` for repository-wide rules and `ARCHITECTURE.md` for system architecture.

## Product feel

- Documentation-like and data-focused knowledge base
- Calm, restrained, and trustworthy presentation
- Dense but scannable content layout
- Russian language only (`ru-BY` locale)
- Server-rendered static HTML — no client-side runtime
- Public wiki style, not app-like dashboard

## Canonical UI examples

- `layouts/_default/baseof.html` — page skeleton with header, main, footer
- `layouts/home.html` — hero section, section cards grid, recent pages
- `layouts/_default/list.html` — section listing with cards and pagination
- `layouts/_default/single.html` — article page with breadcrumbs, dates, tags
- `layouts/404.html` — error page with primary/secondary buttons
- `layouts/partials/header.html` — fixed header with logo, nav, mobile menu
- `layouts/partials/footer.html` — footer with external links
- `layouts/partials/section-card.html` — section card with icon, title, description
- `layouts/partials/recent-pages.html` — recent updates card list
- `layouts/partials/pagination.html` — pagination component
- `static/css/input.css` — Tailwind CSS 4 source with semantic component classes

## Layout rules

- Use `layouts/_default/baseof.html` as the single page skeleton
- Main content lives in a container with `mx-auto` and responsive padding
- Fixed header at top with `z-50`, `border-b`, `bg-white`, `shadow-md`
- Footer at bottom with `mt-auto` in the flex column
- Skip-to-content link fixed top-left with focus state
- Page content starts below header (`mt-20`) to avoid overlap
- Cards use consistent `wiki-card` class: white background, gray-300 border, rounded-lg, shadow-md
- Grid layouts prefer `grid-cols-1 md:grid-cols-2 lg:grid-cols-3` with `gap-2`
- Vertical rhythm uses `gap-2` between stacked elements
- Section headers use `eyebrow` for category labels above `h2` titles

## Visual language

- **Colors**: Primary blue-600 (`#2563eb`) for actions/links; blue-700/900 for hover/focus states; gray-300 for borders; gray-700 for secondary text; white for card backgrounds; black for headings
- **Typography**: Manrope (preferred) / Inter system stack; headings are `font-bold tracking-tight`; body text is `text-gray-700`; prose styling via `@tailwindcss/typography` plugin
- **Spacing**: Consistent `gap-2` between elements; cards use `p-2` (mobile) to `p-6` (desktop); container padding `px-4`
- **Borders/Radius**: `rounded-lg` for cards and buttons; `border border-gray-300` for card outlines
- **Shadows**: `shadow-md` for cards and header; `hover:shadow-xl` for card hover states
- **Icons**: SVG icons in section cards match `icon` enum values (`news`, `chart`, `guide`, `document`, `info`)
- **Transitions**: Subtle `transition` on interactive elements; `motion-reduce:transition-none` for accessibility

Token values are defined in frontmatter and implemented in `static/css/input.css`.

## Components and patterns

- **Cards** (`wiki-card`): White background, gray-300 border, rounded corners, shadow. Used for sections, articles, recent pages. Hover state adds `shadow-xl`
- **Buttons**: 
  - Primary (`wiki-button-primary`): Blue-600 background, white text, hover:bg-blue-700
  - Secondary (`wiki-button-secondary`): White background, gray-300 border, gray-700 text, hover:bg-gray-100
- **Links** (`active-a`): Blue-600, hover:text-blue-900, focus ring with blue-600
- **Eyebrow labels** (`eyebrow`): Uppercase, bold, tracking-widest, small text for section categories
- **Breadcrumbs** (`breadcrumbs`): Flex wrap, gray-700 text, slash separators
- **Pagination** (`wiki-pagination`): Centered, with previous/next links and numbered pages
- **Empty states** (`wiki-empty-state`): Dashed gray-300 border, gray-50 background, gray-700 text
- **Article content** (`article-content`): Prose styling with gray text, black headings, rounded images, bordered tables
- **Tags** (`tag-list`): Flex wrap, white background, gray-300 border, hover:bg-gray-100
- **Page dates** (`page-dates`): Small gray-700 text, published/updated timestamps

**Component states:**
- Links: default (blue-600), hover (blue-900), focus (ring-2 ring-blue-600)
- Buttons: default, hover (darker background), focus (ring-2)
- Cards: default, hover (shadow-xl)
- Pagination: current page uses `wiki-pagination-current` (blue-600 bg, white text), links use `wiki-pagination-link`
- Mobile nav: uses `<details>` with hamburger/close icons, absolute positioned dropdown

## Interaction rules

- Keep all content server-rendered and useful without JavaScript
- Use small client-side enhancements only for mobile menu toggle (native `<details>`)
- All interactive elements must be keyboard-reachable
- Focus states use `focus:ring-2` with appropriate color (blue-600 for primary, gray-500 for secondary)
- Skip-to-content link available at top-left, visible on focus
- Mobile navigation uses native HTML `<details>` — no JavaScript required
- Form preservation and validation are not applicable (static site with no forms)
- Loading states not applicable (fully static)

## Data display rules

- Dates use `DD.MM.YYYY` format (e.g., `02.01.2006`)
- Published/updated timestamps in `page-dates` partial use `time` elements with ISO dates
- Tables use `article-content` styling: bordered, gray-100 header background, hoverable rows
- Images are responsive with `max-w-full`, centered, rounded
- Linked images render as full-width containers
- Empty states use `wiki-empty-state` with helpful messages

## Forms, filters, and validation

- Not applicable — this is a static content site with no user input forms
- Filtering is done via Hugo taxonomies and section organization, not client-side

## Tables and charts

- Tables: Full width, bordered, with gray-100 header row background. Rows have hover background. Cells have padding. See `article-content` in `static/css/input.css` and `layouts/_markup/render-table.html`
- Charts: Not implemented in this static wiki; statistics are presented as Markdown tables or prose
- Use Markdown tables for data presentation — they render via `render-table.html`

## User-facing text

- All text must be in Russian (`ru-BY` locale)
- Use clear, direct language appropriate for financial/technical documentation
- Button labels: Use action-oriented text like "Открыть руководство", "На главную", "Перейти к TokenBel"
- Section labels: Use `eyebrow` for category indicators (e.g., "TokenBel Wiki", "Навигация", "Материалы")
- Error states: Use clear messages like "Страница не найдена", "Материалы этого раздела пока готовятся"
- Empty states: Use helpful messages like "Материалы появятся после переноса содержимого из текущей wiki"
- Avoid technical implementation terms in user-facing text

## Accessibility basics

- Use semantic HTML5 elements (`<header>`, `<main>`, `<footer>`, `<nav>`, `<article>`, `<section>`)
- All interactive elements are keyboard-reachable via tab order
- Visible focus indicators on all interactive elements (`focus:ring-2`)
- Skip-to-content link at top of page (`#main-content`)
- Avoid hover-only critical information — all content accessible via keyboard
- Use `aria-label` and `aria-current` appropriately in navigation
- Use `sr-only` for screen-reader-only text
- Maintain readable contrast: black text on white, blue-600 on white, gray-700 on white
- Mobile menu uses native `<details>` with proper labeling

## Do / Don't

Do:
- Reuse existing `wiki-*` semantic classes from `static/css/input.css`
- Follow the card-based layout pattern with `wiki-card`
- Use `gap-2` for consistent vertical spacing
- Use `rounded-lg` for card and button corners
- Use blue-600 for primary actions and links
- Use gray-300 borders and gray-700 text for secondary content
- Preserve the fixed header and container layout
- Keep Russian language throughout
- Use `eyebrow` for section category labels
- Run `make css-build` after changing `input.css` or templates

Don't:
- Introduce new colors without existing semantic precedent
- Add JavaScript frameworks or runtime scripts
- Use external Hugo themes or Sass/SCSS
- Redesign whole pages for small changes
- Change the canonical domain from `https://wiki.tokenbel.info/`
- Break the SEO contracts (home title, 404 text, canonical URLs)
- Use hover-only behavior for critical information
- Add animations to data-heavy content without purpose
- Dynamically generate Tailwind class names

## When unsure

- Inspect the nearest existing page or component in `layouts/`
- Follow the pattern used in `home.html`, `list.html`, or `single.html`
- Check `static/css/input.css` for semantic component classes
- Prefer existing `wiki-*` classes over new utility combinations
- Keep changes minimal and consistent with surrounding context
- Ask before introducing a new visual pattern or component variant
