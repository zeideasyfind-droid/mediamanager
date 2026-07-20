# Motion & Animation

Treat your interface as a physical space with unbreakable rules. Every element moves *from* somewhere *to* somewhere. Nothing just appears or disappears.

**Priority order:** Simplicity → Fluidity → Delight. You cannot polish a bad layout with animations.

**The Delight-Impact Curve:** The less frequently a feature is used, the more delightful it should be. Daily actions need efficiency with subtle touches. Rare moments deserve theatrical ones.

---

## CSS-Native Animation (Preferred for HTML/JS projects)

### Scroll-Driven Animations (CSS-only, replaces AOS/ScrollReveal)

**CRITICAL: Scroll reveals must NOT cause layout shift (CLS).** The animated element must occupy its final layout space from the start. Only animate visual properties (`opacity`, `clip-path`, `filter`) — never `transform: translateY()` on scroll-triggered elements, because the element visually occupies a different position during the animation while pushing content around.

```css
/* GOOD — opacity-only reveal. Element takes up its final space immediately. */
.fade-in {
  opacity: 1; /* Fallback: visible by default */
}

@supports (animation-timeline: scroll()) {
  .fade-in {
    opacity: 0;
    animation: reveal-fade linear both;  /* linear maps 1:1 to scroll progress — correct for scroll-driven */
    animation-timeline: view();
    animation-range: entry 0% entry 100%;
  }
}

@keyframes reveal-fade {
  to { opacity: 1; }
}

/* GOOD — clip-path reveal. Element is in place, just visually masked. */
.reveal-up {
  opacity: 1;
}

@supports (animation-timeline: scroll()) {
  .reveal-up {
    clip-path: inset(100% 0 0 0);  /* Masked from bottom — no layout shift */
    animation: reveal-clip linear both;
    animation-timeline: view();
    animation-range: entry 0% entry 100%;
  }
}

@keyframes reveal-clip {
  to { clip-path: inset(0 0 0 0); }
}
```

### @starting-style for Enter Animations (no JS)
```css
dialog[open] {
  opacity: 1; transform: scale(1);
  transition: opacity 0.3s cubic-bezier(0.16, 1, 0.3, 1),
              transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);

  @starting-style {
    opacity: 0; transform: scale(0.95);
  }
}
```

### CSS View Transitions for Page/Route Changes
```css
@view-transition { navigation: auto; }
::view-transition-old(root) { animation: fade-out 0.2s cubic-bezier(0.4, 0, 1, 1); }  /* exit curve */
::view-transition-new(root) { animation: fade-in 0.3s cubic-bezier(0.16, 1, 0.3, 1); }  /* golden curve */
```

### @property for Animatable Custom Properties
```css
@property --gradient-angle {
  syntax: '<angle>';
  initial-value: 0deg;
  inherits: false;
}
.gradient-border {
  --gradient-angle: 0deg;
  border-image: linear-gradient(var(--gradient-angle), var(--color-primary), var(--color-blue)) 1;
  animation: spin 3s linear infinite;  /* linear is correct for continuous rotation */
}
@keyframes spin { to { --gradient-angle: 360deg; } }
```

---

## Motion Library (for React projects)

When building with React, use the Motion library for physics-based spring animations, exit animations, and layout transitions.

**CDN for vanilla JS** (non-React projects):
```html
<script src="https://cdn.jsdelivr.net/npm/motion@latest/dist/motion.js"></script>
```

### Spring Presets

| Name | Config | Use For |
|---|---|---|
| Smooth | `damping: 30, stiffness: 200` | Default for most UI transitions |
| Gentle | `damping: 20, stiffness: 120` | Modals, overlays, cards |
| Snappy | `damping: 25, stiffness: 300` | Buttons, toggles, micro-interactions |
| Bouncy | `damping: 12, stiffness: 200` | Celebrations, playful elements |

**Duration-based alternative** (simpler, good for coordinated sequences):
```jsx
transition={{ duration: 0.4, bounce: 0.2 }}
```

### Key Patterns

```jsx
// AnimatePresence for exit animations
<AnimatePresence mode="wait">
  <motion.div
    key={currentView}
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -20 }}
    transition={{ type: "spring", damping: 25, stiffness: 200 }}
  />
</AnimatePresence>

// Shared element transitions with layoutId
<motion.div layoutId={`card-${id}`} transition={{ type: "spring", damping: 30, stiffness: 200 }} />

// Staggered reveals with variants
// NOTE: Use opacity-only for scroll-triggered reveals to avoid CLS.
// translateY is acceptable here because AnimatePresence controls when
// elements mount — they aren't shifting existing content.
const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.05, delayChildren: 0.1 } }
};
const item = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { type: "spring", damping: 25, stiffness: 200 } }
};

<motion.ul variants={container} initial="hidden" animate="show">
  {items.map(i => <motion.li key={i} variants={item} />)}
</motion.ul>
```

---

## Easing & Timing Reference

**The golden easing curve**: `cubic-bezier(0.16, 1, 0.3, 1)` — fast start, gentle settle. Default for entries (300-400ms), morphs (350-500ms), hover (180ms), numbers (400-800ms), page transitions (300ms). Use `cubic-bezier(0.4, 0, 1, 1)` for exits (200-250ms) only. Springs: smooth `damping:30, stiffness:200`, bouncy `damping:12, stiffness:200`. Stagger: 40-60ms/item. **Never `linear` for UI transitions** — exceptions: scroll-driven timelines and continuous rotation.

---

## Hover & Interactive States

**Cardinal rule: hover states are only for clickable elements.** Before adding `:hover`, ask: *does clicking this do something?* If no → no hover state. Buttons, links, clickable cards, nav items, toggles, icon buttons → yes. Headings, paragraphs, static cards, decorative containers, badges → never.

### The System Constant

```css
--transition-interactive: 180ms cubic-bezier(0.16, 1, 0.3, 1);
```

Apply to every element with a hover state. List properties individually — **never `transition: all`**.

```css
.btn {
  transition: background var(--transition-interactive),
              color var(--transition-interactive),
              box-shadow var(--transition-interactive),
              transform var(--transition-interactive);
}
.btn:hover  { transform: translateY(-1px); box-shadow: var(--shadow-md); }
.btn:active { transform: translateY(0); box-shadow: var(--shadow-sm); }

a { transition: color var(--transition-interactive), text-decoration-color var(--transition-interactive); }

.card[href], a.card {
  transition: box-shadow var(--transition-interactive), transform var(--transition-interactive), border-color var(--transition-interactive);
}
.card[href]:hover  { transform: translateY(-2px); box-shadow: var(--shadow-md); }
.card[href]:active { transform: translateY(0); }

.icon-btn { transition: color var(--transition-interactive), background var(--transition-interactive); }
input, textarea, select { transition: border-color var(--transition-interactive), box-shadow var(--transition-interactive); }
```

**Rules:** Pair hover with `:active` (hover lifts, active pushes down). `:focus-visible` same as hover + focus ring. Mobile (`@media (hover: none)`): `:active` only.

---

## Cursor States

`pointer` → clickable (buttons, links, cards, toggles). `default` → static. `grab`/`grabbing` → draggable. `not-allowed` → disabled (`opacity:0.5` + `pointer-events:none`). `zoom-in`/`zoom-out` → expandable images. `col-resize`/`row-resize` → resizable. Never `cursor:pointer` on non-interactive elements.

---

## GSAP SVG Plugins

GSAP's SVG plugins (DrawSVG, MorphSVG, MotionPath) are free and handle what CSS cannot — morphing between shapes with different point counts, drawing partial paths, and motion along curves.

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/DrawSVGPlugin.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/MorphSVGPlugin.min.js"></script>
<script>
  gsap.from('.logo-path', { drawSVG: '0%', duration: 1.5, ease: 'power3.out' });
  gsap.to('#circle', { morphSVG: '#star', duration: 1, ease: 'power2.inOut' });
  gsap.to('.dot', {
    motionPath: { path: '#curve', align: '#curve', alignOrigin: [0.5, 0.5] },
    duration: 3, ease: 'none', repeat: -1
  });
</script>
```

---

## Motion Rules (Summary)

No instant show/hide — everything animates. Shared elements morph between states. Directional consistency (right → enters from right, back → from left). Persistent elements stay put across transitions. Text changes morph (torph or crossfade). Only animate what changes. Loading states travel to where results appear. Stagger: 40-60ms per item. Scroll reveals: `opacity`/`clip-path`/`filter` only — never `translateY` (CLS). Respect `prefers-reduced-motion`.
