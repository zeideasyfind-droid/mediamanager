# CSS & Tailwind

Modern CSS features, Tailwind CSS v4, and cutting-edge CSS.

---

## Tailwind CSS v4 (via CDN)

For rapid prototyping, use the Tailwind v4 Play CDN:
```html
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
```

Customize with `@theme` in a `<style type="text/tailwindcss">` block:
```html
<style type="text/tailwindcss">
  @theme {
    --color-brand: oklch(0.55 0.25 260);
    --font-display: 'Instrument Serif', 'Georgia', serif;
    --font-body: 'Work Sans', 'Helvetica Neue', sans-serif;
  }
</style>
```

Note: The CDN version does not support `@apply` or tree-shaking, but this is the standard approach for single-HTML projects.

**Tailwind v4 key features to use:**
- CSS-native `@theme` directives instead of `tailwind.config.js`
- `bg-linear-*` (renamed from `bg-gradient-to-*`), `bg-radial-*`, `bg-conic-*` for gradients
- Native container queries: `@container`, `@sm:`, `@lg:`
- `@starting-style` variant via `starting:` prefix
- 3D transform utilities: `rotate-x-*`, `rotate-y-*`, `perspective-*`
- Gradient interpolation modes for OKLCH/Oklab gradients
- Arbitrary values: `text-[clamp(1rem,3vw,2rem)]`, `grid-cols-[200px_1fr]`, `bg-[oklch(0.5_0.2_260)]`
- Arbitrary variants: `[&:nth-child(odd)]:bg-surface`, `[@supports(backdrop-filter:blur())]:backdrop-blur-md`
- Group and peer modifiers: `group-hover:opacity-100`, `peer-checked:translate-x-full`
- `has-*` variant: `has-[input:focus]:ring-2` — style parents based on child state
- `not-*` variant: `not-last:border-b` — apply styles to all but matching elements
- `motion-safe:` and `motion-reduce:` variants for respecting `prefers-reduced-motion`
- Dark mode: `dark:bg-surface` — automatic via `prefers-color-scheme` or manual with `[data-theme="dark"]` selector

**When using Tailwind, handle container queries, arbitrary properties, stateful variants, and responsive design entirely in markup.** Keep all styles in the single HTML file.

---

## Modern CSS Features (Well-Supported, Use Freely)

**90%+ support (use freely):** CSS Nesting, `oklch()`/`oklab()`, container queries, `@layer`, `@property`, `clamp()`, `color-mix()`, `:has()`, Popover API, `subgrid`, `content-visibility`, `text-wrap: balance`.

**80-90% (use with fallbacks):** Scroll-driven animations, view transitions, `@starting-style`, Anchor Positioning, `text-wrap: pretty`.

---

## Cutting-Edge CSS (Interop 2026)

Use with `@supports` fallbacks:

**`contrast-color()`** — auto-accessible text: `color: contrast-color(var(--color-primary))`. Safari first, cross-browser via Interop 2026.

**Advanced `attr()` typing** (Chrome 133+) — data attributes as CSS values:
```css
.chip { background-color: attr(data-color type(<color>)); }
.bar  { width: calc(attr(data-value type(<number>)) * 1%); }
```

**`shape()`** — responsive clip-paths with %, vw, calc (unlike pixel-only `path()`).

**`sibling-index()`** — CSS-only staggered animations: `animation-delay: calc(sibling-index() * 60ms)`.
