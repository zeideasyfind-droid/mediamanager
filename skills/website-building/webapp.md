---
name: website-building/webapp
description: Build production-grade web applications — SaaS products, dashboards, admin panels, e-commerce stores, and brand experiences. Covers compact type scale, navigation architecture, data density, state management, component architecture, and dashboard layout rules.
---

# Web Application Design

Build production-grade web applications -- SaaS products, dashboards, admin panels, e-commerce stores, brand experiences, and interactive tools.

**Mandatory shared foundations (if not already loaded):** the Design Tokens section and the Design System Proof section in `skills/website-building/SKILL.md`.

**Dashboard-specific rules are in the Dashboard section below.** Load that file for any data-dense interface.

---

### Art Direction by Product Type

| Product Type | Concept-Driven Direction | Token Starting Points |
|---|---|---|
| **SaaS / productivity** | A writing tool is calm and typographic. A project management tool is structured and efficient. A design tool is visual and spacious. Match personality to purpose. | Neutral surfaces. 1 accent. Body font that matches the product's character. |
| **Dashboard / analytics** | Finance dashboards demand precision and sobriety. Marketing dashboards can be warmer and more visual. The data's domain sets the tone. | Sans-serif + monospace for data. High-contrast. Load the Dashboard section below. |
| **E-commerce** | Luxury goods: muted surfaces, serif display, restrained accent. Kids' toys: warm, bright, rounded. Outdoor gear: earthy tones, rugged sans-serif. | Warm palette derived from product category. Strong CTA contrast. |
| **Brand experience** | A music streaming brand differs from an architecture studio. Derive everything from the brand. | Display font at `--text-xl` in-app; `--text-2xl` ONLY for marketing/landing hero sections. 1-2 custom accent hues. Theatrical motion. |
| **Admin panel** | Utilitarian, clear, efficient. A healthcare admin panel feels different from a developer tools panel. | Inter or DM Sans (loaded via CDN, not system fonts). Functional color only. Dense layout. |

See the Design Tokens section in `skills/website-building/SKILL.md` for size floors and color restraint rules.

---

## Web App Type Scale — Keep It Compact

**Web application interfaces should never have oversized typography.** Unlike informational sites where a dramatic hero heading sets the editorial tone, web apps communicate through density, clarity, and structure. Big display text wastes space that should show data, controls, or content.

| Element | Token | Notes |
|---|---|---|
| **Page title** | `--text-xl` | **The largest heading in a web app.** ONE per page. |
| **Section heading** | `--text-lg` | Card headers, sidebar sections, table group labels. |
| **Body text** | `--text-base` | The standard for all UI copy. |
| **Buttons, nav, links** | `--text-sm` | Interactive elements, sidebar items. |
| **Labels, badges, metadata** | `--text-xs` | Tiny helper text, timestamps, status badges. 12px floor. |

**Never use `--text-2xl`, `--text-3xl`, or `--text-hero` in a web app.** Those dramatic sizes exist for informational sites and landing pages only (see `skills/website-building/informational.md`). If a heading feels too small at `--text-xl`, the issue is usually hierarchy and weight — try a heavier font weight or more spacing around it, not a bigger size.

**Brand experience / marketing pages** are the one exception: if a web app contains a marketing landing section (e.g., a product homepage before login), that section follows informational site rules and can use `--text-2xl` for ONE hero moment. The application UI itself stays compact.

---

## What Makes a Great Web Application

### 1. Clarity Over Cleverness

- **Labels > icons.** Clear text labels outperform icon-only buttons.
- **Show state.** Always communicate: What data am I showing? Is it loading? Is it stale?
- **Progressive disclosure.** Essential controls first. Advanced options reveal on demand.
- See the Design Taste section in `skills/website-building/SKILL.md` for one-primary-action-per-view, polish, and delight guidance.

### 2. Performance is the Feature

- **Optimistic updates.** Update UI immediately. Confirm server success in background. Rollback only on failure.
- **Skeleton loaders, not spinners.** See the Design Taste section in `skills/website-building/SKILL.md`.
- **Core Web Vitals:** LCP < 2.0s (< 1.5s for dashboards), INP < 150ms, CLS < 0.05.
- **Lazy-load below the fold.** Use `content-visibility: auto` for off-screen content.
- **Cache aggressively.** Use in-memory state with stale-while-revalidate patterns.

### 3. Navigation is Architecture

- **Sidebar for primary navigation.** Persistent context, scales to many items. Collapsible to icons on narrow viewports.
- **Top bar for secondary actions.** User menu, search, notifications, breadcrumbs.
- **Breadcrumbs for deep hierarchies.** Mandatory when 3+ levels deep.
- **Command palette (Cmd+K).** Build from scratch.
- **URL reflects state.** Every view, filter, and selected item representable in the URL.

### 4. Data Density Done Right

- **KPIs at the top, trends in the middle, details at the bottom.** See the Dashboard section below.
- **Tables:** sorting, filtering, sticky headers, row hover states, inline actions, keyboard navigation.
- **Filters above content.** Always visible, always showing what's applied.
- **Numbers need context.** Up 12% vs last week, $142K / $200K target.
- **Animate value changes.** CSS `@property` counter animation.

### 5. Polish in the Details

- **Undo over confirmation dialogs.** "Item deleted. [Undo]" > "Are you sure?"
- **Keyboard shortcuts for power users.** Document in a shortcut modal (press `?`).
- **Toast for background, inline for context.** Toasts for confirmations. Errors inline next to the trigger.
- **Every state is a designed state.** Loading, empty, error, partial data, stale, offline.

---

## Best Practices by App Type

### SaaS Products & Dashboards

- **Sidebar navigation** with collapsible sections and pinnable items
- **Dark mode as first-class** -- many dashboard users work in low-light environments
- **Simulated real-time** -- use timers and in-memory state for live-feeling data. "Last updated: 2m ago" for non-live data
- **Export everything** -- CSV, PDF, image for every chart and table
- **Role-based views** -- admin vs member vs viewer with different permissions
- **Onboarding checklist** -- persistent progress tracker for new users

### E-Commerce & Online Stores

- **Product pages:** Hero image (zoomable, multi-angle), price, "Add to Cart" above the fold, shipping info, reviews
- **Fast checkout.** Guest checkout always. Auto-fill. 3 steps max: Cart > Shipping > Payment
- **Faceted search** with real-time results. Filter by price, category, rating, availability
- **Cart state.** In-memory only — no persistence available (no storage, no backend)
- **Trust signals.** Secure checkout badge, return policy, shipping estimates, reviews, payment logos
- **Mobile shopping.** Sticky "Add to Cart", swipeable images, Apple Pay / Google Pay

### Brand Experiences & Marketing Apps

- **Scroll-driven narrative.** GSAP ScrollTrigger for pinned sections, scrubbing, parallax
- **Full-screen immersive sections.** Hero moments with video, animation, or interactive 3D
- **Micro-interactions that reward exploration.** Hover effects, parallax, cursor-following
- **Performance despite richness.** Lazy-load heavy content. Intersection Observer. Compress media
- **Responsive storytelling.** Pinned horizontal scroll on desktop becomes vertical stack on mobile

---

## State Management Guide

All state is client-side. Use the simplest vanilla JS approach for each.

| Use Case | Approach |
|---|---|
| API / fetched data | `fetch()` + in-memory cache object |
| Forms | Vanilla form handling + JS validation |
| App state (theme, prefs) | JS variables or a simple state object |
| URL / routing | `location.hash` routing |

---

## Component Architecture

**Atoms** → Button, Input, Badge, Avatar, Tooltip. **Molecules** → Search bar, KPI card, Form field. **Organisms** → Data table, Sidebar, Settings panel. **Templates** → Dashboard (sidebar+header+main), Settings (tabs+form), List/detail.

---

## Authentication & Authorization

- **Login:** centered single-column form. Email/password + social + magic link. Registration starts with email only (progressive).
- **Permissions:** don't show UI elements the user can't use (no disabled buttons). Graceful errors: "You don't have permission. [Request access]" — not a raw 403.

---

## Responsive Web App Patterns

### Sidebar Behavior
| Viewport | Sidebar State |
|---|---|
| > 1024px | Expanded with labels |
| 768-1024px | Collapsed to icons only |
| < 768px | Hidden, accessible via hamburger or swipe-from-left |

---

## Expert Intake

Ask: app type? users? core workflow? data types? auth? real-time? tech preferences? reference apps?

**Default (minimal input):** Sidebar nav, Satoshi 14px (Fontshare), 12-13px labels, Nexus palette, 1 accent, dashboard layout (the Dashboard section below). See "The Fallback: Clean & Swiss" in `SKILL.md`.

**Key shared files:** `shared/04-motion.md`, `shared/08-css-and-tailwind.md`, `shared/12-charts-and-dataviz.md`, the Dashboard section below.

---

# Dashboard & Data-Dense Interface Design

**Mandatory shared foundations (if not already loaded):** the Design Tokens section and the Design System Proof section in `skills/website-building/SKILL.md`.

Dashboards are the most common source of broken, unusable layouts. Follow these rules strictly.

---

## Dashboard Typography & Voice

**Typography:** Use sans-serif exclusively for all UI elements — navigation, labels, data, buttons, table headers, form fields. Serif is only acceptable in a dashboard logo or decorative brand mark. Data values and numbers must use `font-variant-numeric: tabular-nums lining-nums;` so columns align and digits don't shift width.

**Logo:** When building a dashboard, generate the logo as an inline SVG. Aim for a Paul Rand-inspired aesthetic — geometric, reducible to a single shape or letterform, minimal color (one accent + black/white). The logo should work at 24px and 200px. Avoid gradients, bevels, or illustration-style complexity.

**Copy:** Dashboard copy should be active voice, concise, and scannable. Aim for a maximum of 7 words per label or sentence. Write like a control panel, not a novel:
- "Export CSV" not "Click here to export your data as a CSV file"
- "3 items need review" not "There are 3 items that are currently awaiting your review"
- "Updated 2m ago" not "This data was last updated 2 minutes ago"

---

## Layout Architecture

**The golden pattern — full-viewport, no body scroll:**
```css
html, body { height: 100%; overflow: hidden; margin: 0; }

.dashboard {
  display: grid;
  grid-template-columns: auto 1fr;
  grid-template-rows: auto 1fr;
  height: 100dvh;
}

.sidebar {
  grid-row: 1 / -1;
  overflow-y: auto;
  overscroll-behavior: contain; /* CRITICAL */
}

.header {
  grid-column: 2;
  position: sticky; top: 0;
  z-index: 10;
}

.main {
  grid-column: 2;
  overflow-y: auto;
  overscroll-behavior: contain; /* CRITICAL */
}
```

---

## The Nested Scroll Rule

**There must be exactly ONE primary scroll region.** This is non-negotiable.

- The `<body>` should have `overflow: hidden` on dashboard layouts. Only `.main` scrolls.
- Every scrollable container must have `overscroll-behavior: contain` to prevent scroll chaining to parent elements.
- Sidebars should be fully visible without scrolling when possible. If they must scroll, they scroll independently with `overscroll-behavior: contain`.
- **Never nest a scrollable table inside a scrollable card inside a scrollable main area.** If a table overflows, the table's container scrolls horizontally while the main area handles vertical scroll.
- Modals: set `body { overflow: hidden }` when open, restore when closed.

---

## Information Hierarchy

Follow the **inverted pyramid model**:

1. **Top**: KPIs and status (the "are we on track?" line) — high-contrast cards, upper-left placement
2. **Middle**: Trends and comparisons (charts, sparklines) that explain movement
3. **Bottom**: Detail tables with sortable columns, pagination, and drill-down links

Rules:
- **Filters above content**, not hidden in sidebars. Always show what's applied.
- **Group related metrics** — separate unrelated ones with space, not lines.
- **Maximum 5-7 KPI cards** visible at once. More creates analysis paralysis.
- **Sticky table headers**: `thead { position: sticky; top: 0; z-index: 1; }`
- **Skeleton screens must match real layout** — if the skeleton has 3 bars and the content has 5 lines, you've broken the illusion.

---

## Data Visualization Rules

- **Animate number changes** — values should count up/down, not snap.
- **Delta indicators**: arrow + percentage + color (green up / red down / gray flat)
- **Sparklines in table rows** to show trends at a glance
- **Don't refresh everything simultaneously** — stagger data updates to avoid visual chaos
- **Don't rely on color alone** — always pair color with icons, labels, or patterns for accessibility

---

## Performance for Dense UIs

```css
/* Skip rendering off-screen content */
.card-grid > * {
  content-visibility: auto;
  contain-intrinsic-size: 0 200px;
}
```

`content-visibility: auto` tells the browser to skip layout/paint for off-screen elements. For dashboards with 50+ cards or long tables, this is a massive performance win (95%+ browser support).
