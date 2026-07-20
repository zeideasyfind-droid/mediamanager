---
name: website-building/game
description: Guide for building browser games — 3D (Three.js/WebGL) and 2D (Canvas). Covers sandbox constraints, art direction, game UI design systems, typography, image generation for game art, music, renderer setup, ECS architecture, Rapier physics, asset loading, post-processing, and performance.
---

# Three.js Game Development Skill

Build 3D browser games using Three.js. Use WebGL 2 rendering, Rapier for physics, ECS for architecture, and GLTF/GLB for assets. All games are static HTML/CSS/JS rendered inside a sandboxed iframe.

**Mandatory shared foundations (if not already loaded):** the Design Tokens section and the Design System Proof section in `skills/website-building/SKILL.md`.

---

## Sandbox Environment

Games run inside a sandboxed iframe with limited permissions. All code must work within these constraints.

### What Works
- **JavaScript, Canvas, WebGL 2** — fully functional
- **WebAssembly** — works when loaded from CDN (e.g., Rapier via esm.sh)
- **Web Audio API** — works, but AudioContext requires a user gesture (click/tap) to start
- **`<img>`, `<video>`, `<audio>` HTML elements** — load binary files correctly (the browser handles redirects)
- **CDN imports** — `fetch()` to external CDN URLs (esm.sh, jsdelivr, unpkg, gstatic) works fine
- **Keyboard, mouse, touch, gamepad events** — all standard DOM events work

### What Is Blocked
- **`fetch()` of local binary files** — the site proxy redirects `.glb`, `.wasm`, `.mp3`, `.png` etc. to an external origin, and these redirects fail in the sandbox due to CORS. **Load all binary assets from external CDN URLs, or use HTML elements** (`<img>`, `<audio>`) which bypass this restriction
- **localStorage / sessionStorage / IndexedDB** — blocked (opaque origin). Code containing these will fail. Use in-memory state only. No game saves
- **Pointer Lock API** — blocked. FPS-style mouse capture is unavailable. Use relative mouse movement (`movementX`/`movementY` on `mousemove` events) within the iframe instead
- **Fullscreen API** — blocked. Design the game to fill the iframe viewport
- **`alert()` / `confirm()` / `prompt()`** — blocked. Use in-game UI overlays instead
- **WebGPU** — may fail in opaque-origin iframes. Use WebGL 2 as the default renderer

### Asset Loading Strategy
Because `fetch()` fails for local binary files, follow this rule:

- **3D models, textures, audio, WASM** → load from external CDN URLs (Poly Pizza, Kenney, ambientCG, esm.sh, etc.)
- **HTML, CSS, JS, JSON, text files** → can be local (served inline by the proxy)
- **Generated images** (from `generate_image`) → use the returned URL directly in `<img>` elements or as texture sources, NOT `fetch()` + canvas. For Three.js textures from generated or searched image URLs, **always set `crossOrigin`** before `src` — external origins taint the canvas for WebGL unless CORS is explicitly requested:

```js
const img = new Image();
img.crossOrigin = 'anonymous';
img.src = 'https://example.com/generated-bg.png'; // use the URL returned by generate_image
img.onload = () => {
  const texture = new THREE.Texture(img);
  texture.needsUpdate = true;
  // use texture
};
```

Without `img.crossOrigin = 'anonymous'`, the cross-origin redirect silently taints the image — `texImage2D` fails and WebGL renders a black texture with no error.

---

## Art Direction

Before writing code, establish a cohesive art direction based on the game's subject matter, genre, and tone. Every visual decision — color palette, lighting, asset style, UI treatment, loading screens — should flow from this direction.

### Choosing a Direction
- **Analyze the game concept**: A horror game demands dark palettes, fog, and desaturated textures. A kids' puzzle game calls for bright primaries and rounded shapes. A sci-fi shooter needs neon accents, metallic materials, and volumetric lighting.
- **Pick a visual style**: Low-poly stylized, realistic PBR, pixel-art-inspired 3D, cel-shaded, voxel, neon/synthwave, hand-painted. Commit to one and maintain consistency.
- **Define a color palette**: Choose 3-5 core colors. Use one dominant, one accent, and neutrals. Apply consistently to environment, UI, and particles.
- **Match lighting to mood**: Warm directional light for adventure, cold blue ambient for horror, high-contrast rim lighting for action.
- **UI must match the game world**: Menu screens, HUD, loading screens, and game-over states should share the same palette and typographic style as the game itself.

### Generate Game Art with `generate_image`
Use the image generation tool to create custom art for the game. Do NOT use placeholder rectangles or skip visual assets — generate real art that matches the art direction.

**Always generate these assets:**
- **Title screen / splash image** — a hero image that establishes the game's visual identity
- **Loading screen background** — themed art shown during asset loading
- **Game-over / victory screen art** — emotional payoff images

**Generate when appropriate:**
- Skybox/environment concept art (use as reference for building the 3D scene)
- Character/enemy concept art (use as texture reference or 2D sprite overlays)
- UI background textures or patterns

**Prompting tips for game art:**
- Be specific about style: "low-poly isometric forest scene with warm sunset lighting, stylized"
- Include mood/atmosphere: "dark cyberpunk alley, neon reflections on wet pavement, moody"
- Specify aspect ratio: use `16:9` for backgrounds/loading screens, `1:1` for icons/thumbnails
- Reference the established art direction in every prompt for consistency

---

## Game UI Typography

**Read the Typography section in `skills/website-building/SKILL.md` for font selection, pairing rules, loading, and the blacklist.** All rules apply to games. Below adapts them to game-specific contexts.

### Rules

- **Two fonts max.** One display font for titles/game-over. One legible sans-serif for HUD/menus. Blacklist applies (no Papyrus, Comic Sans, Impact, Lobster, Roboto, Arial, Poppins).
- **Minimum sizes:** 12px tiny labels · 14px buttons/interactive UI · 16px body/dialog. Display fonts only at 24px+.
- **HUD numbers:** Use `font-variant-numeric: tabular-nums lining-nums` so digits don't shift. Clean sans at 14-16px.
- **Load from Google Fonts or Fontshare** — never browser defaults.

### Font-to-Genre Matching

| Genre | Display Font | HUD/Body Font |
|---|---|---|
| Fantasy/RPG | Serif (Cormorant, Playfair, Erode) | Sans (Satoshi, General Sans) |
| Sci-fi/Cyber | Geometric/mono (Cabinet Grotesk, JetBrains Mono) | Technical sans (Inter, Geist) |
| Horror | High-contrast serif (Boska, Instrument Serif) | Neutral sans (Switzer, Inter) |
| Casual/Puzzle | Rounded sans (Plus Jakarta Sans, Chillax) | Same family lighter |
| Retro/Pixel | Mono (Azeret Mono, Fira Code) | Same family |

### Text Rendering

Game UI is HTML/CSS overlaid on the canvas — standard web font rules apply:

```css
.game-ui { position:fixed; inset:0; pointer-events:none; z-index:10; font-family:var(--font-body); color:var(--color-text); }
.game-ui button, .game-ui [data-interactive] { pointer-events:auto; }
.hud-value { font-variant-numeric:tabular-nums lining-nums; font-size:14px; font-weight:600; }
.game-title { font-family:var(--font-display); font-size:clamp(2rem,6vw,4rem); line-height:1.1; }
```

For in-world 3D text (damage numbers, name tags), use `THREE.CanvasTexture` with a hidden 2D canvas drawing the same CSS-loaded font.

---

## Game Design System

Every game screen (HUD, menus, loading, dialogs, settings, game-over, title) must share a unified token system. **Read the Design Tokens section in `skills/website-building/SKILL.md` for token architecture and the Design System Proof section in `skills/website-building/SKILL.md` for the validation process.**

### Building the System

**1. Define tokens** adapted from the Design Tokens section in `skills/website-building/SKILL.md`:

```css
:root {
  --font-display: 'Cabinet Grotesk', sans-serif;
  --font-body: 'Satoshi', sans-serif;
  --color-bg: #0a0a0f;
  --color-surface: rgba(255,255,255,0.05);
  --color-border: rgba(255,255,255,0.12);
  --color-text: #e8e8ec;
  --color-text-muted: #8888a0;
  --color-primary: #4af0c0; /* accent: health, XP, CTAs */
  --color-danger: #ff4466;
  --color-warning: #ffaa22;
  --text-xs: 12px; --text-sm: 14px; --text-base: 16px;
  --text-lg: 20px; --text-xl: 28px; --text-2xl: 40px;
  --space-1: 4px; --space-2: 8px; --space-3: 12px;
  --space-4: 16px; --space-6: 24px; --space-8: 32px;
  --panel-blur: 12px; --panel-radius: 8px;
  --transition-ui: 200ms cubic-bezier(0.16, 1, 0.3, 1);
}
```

**2. Panel treatment** — semi-transparent with blur so the 3D scene shows through:

```css
.game-panel {
  background: var(--color-surface);
  backdrop-filter: blur(var(--panel-blur));
  border: 1px solid var(--color-border);
  border-radius: var(--panel-radius);
  padding: var(--space-4);
}
```

**3. Proof** — Render UI elements (HUD, menu, buttons, all type sizes) over a game scene. Verify contrast and cohesion before building. See the Design System Proof section in `skills/website-building/SKILL.md`.

### Component Patterns

| Component | Font | Size | Surface |
|---|---|---|---|
| HUD (score, health, timer) | `--font-body` | `--text-sm` | Transparent/subtle bg, tabular nums |
| Title screen | `--font-display` | `--text-2xl` | Background art |
| Menus (main, pause) | `--font-body` | `--text-sm` | `.game-panel` |
| Dialog / tutorial | `--font-body` | `--text-base` | `.game-panel` |
| Settings | `--font-body` | `--text-sm` / `--text-xs` | `.game-panel` |
| Game over / victory | `--font-display` | `--text-xl`–`--text-2xl` | Art + overlay |
| Loading | `--font-body` | `--text-sm` | Background art |
| Tooltip | `--font-body` | `--text-xs` | Small `.game-panel` |

### Contrast Safety

Text overlays on dynamic 3D scenes must always have a background treatment:
- Semi-transparent panel, text shadow, or dark vignette behind HUD text
- Minimum: `text-shadow: 0 1px 3px rgba(0,0,0,0.7), 0 0 8px rgba(0,0,0,0.3);`
- Verify HUD over both bright and dark scenes to check

### 2D Canvas Adaptation

Same tokens, but text drawn via `ctx.font` / `ctx.fillText`. Load fonts via CSS `<link>`, wait for `document.fonts.ready` before rendering:

```js
ctx.font = '600 14px Satoshi, sans-serif'; ctx.fillStyle = '#e8e8ec';
ctx.fillText(`Score: ${score}`, 16, 16);
ctx.font = '700 40px "Cabinet Grotesk", sans-serif'; ctx.textAlign = 'center';
ctx.fillText('GAME OVER', canvas.width/2, canvas.height/3);
```

---

## Music & Sound Design

Every game must include music and sound effects by default. Audio dramatically elevates the experience — never ship a silent game.

### Background Music (Required)
Source royalty-free music that matches the art direction:

| Source | Content | License | URL |
|--------|---------|---------|-----|
| **Pixabay Music** | Thousands of tracks by genre/mood | Royalty-free, no attribution | pixabay.com/music |
| **Freesound** | 500K+ sounds and music loops | CC0/CC-BY | freesound.org |
| **Incompetech** | Hundreds of tracks by Kevin MacLeod | CC-BY 3.0 | incompetech.com |
| **OpenGameArt** | Game-specific music and SFX | CC0/CC-BY | opengameart.org |

**Music selection principles:**
- Match the genre: ambient/atmospheric for exploration, uptempo for action, minimal for puzzles
- Loop seamlessly — choose tracks that loop or edit them to loop cleanly
- Keep file sizes reasonable: 128kbps MP3, 30-90 seconds for loops
- Include volume controls and a mute button in game settings

### Sound Effects (Required)
Add SFX for all player interactions: jumps, hits, pickups, UI clicks, explosions, ambient environment sounds. Source from Freesound, Kenney (kenney.nl/assets?t=audio), or OpenGameArt.

### Audio Implementation
Audio requires a user gesture to start. Show a "Click to Play" screen, then initialize audio on that interaction. Use `<audio>` elements for music (they bypass the binary fetch restriction) and Web Audio API for procedural SFX:

```js
// Music via <audio> element (bypasses fetch CORS issues)
function startMusic() {
  const audio = document.createElement('audio');
  audio.src = 'https://cdn.example.com/bgm.mp3'; // external CDN URL
  audio.loop = true;
  audio.volume = 0.4;
  audio.play();
  return audio;
}

// Procedural SFX via Web Audio API (no file downloads needed)
const audioCtx = new AudioContext();
function playSFX(freq = 440, duration = 0.1, type = 'square') {
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.type = type;
  osc.frequency.value = freq;
  gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
  osc.connect(gain).connect(audioCtx.destination);
  osc.start();
  osc.stop(audioCtx.currentTime + duration);
}

// Start on user interaction
document.addEventListener('click', () => {
  audioCtx.resume();
  startMusic();
}, { once: true });
```

For Three.js positional audio (3D spatialized sounds), use `THREE.PositionalAudio` with audio loaded from CDN URLs:
```js
const listener = new THREE.AudioListener();
camera.add(listener);
const sfx = new THREE.PositionalAudio(listener);
new THREE.AudioLoader().load('https://cdn.example.com/hit.mp3', (buffer) => {
  sfx.setBuffer(buffer);
  sfx.setRefDistance(20);
});
enemyMesh.add(sfx);
```

---

## Core Stack

### Renderer Setup
Use WebGL 2 renderer (WebGPU is blocked in sandboxed iframes):

```js
import * as THREE from 'three';

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
document.body.appendChild(renderer.domElement);
```

### Game Loop
Time-based with fixed-timestep physics, never frame-based:

```js
const clock = new THREE.Clock();
const FIXED_TIMESTEP = 1 / 60;
let accumulator = 0;

function gameLoop() {
  requestAnimationFrame(gameLoop);
  const delta = Math.min(clock.getDelta(), 0.1);
  accumulator += delta;
  while (accumulator >= FIXED_TIMESTEP) {
    updatePhysics(FIXED_TIMESTEP);
    updateGameLogic(FIXED_TIMESTEP);
    accumulator -= FIXED_TIMESTEP;
  }
  updateAnimations(delta);
  composer.render(); // or renderer.render(scene, camera)
}
requestAnimationFrame(gameLoop);
```

### Input Handling
Since Pointer Lock is unavailable, use relative mouse movement for camera control:

```js
let rotX = 0, rotY = 0;
renderer.domElement.addEventListener('mousemove', (e) => {
  if (e.buttons === 1) { // left mouse held
    rotY -= e.movementX * 0.002;
    rotX -= e.movementY * 0.002;
    rotX = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, rotX));
    camera.rotation.set(rotX, rotY, 0, 'YXZ');
  }
});
```

For touch devices, track touch delta similarly. For keyboard input, use standard `keydown`/`keyup` event listeners with a key state map.

---

## Architecture

### Entity Component System (ECS)
Use **Koota** (pmndrs) for complex games. Entities are IDs, traits hold data, systems process queries:

```js
import { createWorld, trait } from 'koota';
const world = createWorld();

const Position = trait({ x: 0, y: 0, z: 0 });
const Velocity = trait({ x: 0, y: 0, z: 0 });
const MeshRef = trait({ mesh: null });

const player = world.spawn(Position, Velocity, MeshRef);

function movementSystem() {
  world.query(Position, Velocity).each((e) => {
    const pos = e.get(Position), vel = e.get(Velocity);
    pos.x += vel.x; pos.y += vel.y; pos.z += vel.z;
  });
}
```

### State Management
Use **Zustand** for global game state (phase, score, settings). Keep game-world state in ECS and UI/menu state in Zustand. Do NOT use the `persist` middleware — it requires localStorage which is blocked.

---

## Physics

Use **Rapier** (`@dimforge/rapier3d-compat`) via CDN import — Rust/WASM, fast, full-featured. Do NOT use Cannon.js. The `-compat` variant loads WASM automatically; when imported from a CDN like esm.sh, the WASM fetch goes to the CDN (cross-origin with CORS), so it works in the sandbox.

```js
import RAPIER from '@dimforge/rapier3d-compat';
await RAPIER.init();

const world = new RAPIER.World({ x: 0, y: -9.81, z: 0 });

// Static ground
const groundBody = world.createRigidBody(RAPIER.RigidBodyDesc.fixed());
world.createCollider(RAPIER.ColliderDesc.cuboid(50, 0.1, 50), groundBody);

// Dynamic body
const playerBody = world.createRigidBody(
  RAPIER.RigidBodyDesc.dynamic().setTranslation(0, 5, 0)
);
world.createCollider(RAPIER.ColliderDesc.capsule(0.5, 0.3), playerBody);

function updatePhysics() {
  world.step();
  const pos = playerBody.translation();
  const rot = playerBody.rotation();
  playerMesh.position.set(pos.x, pos.y, pos.z);
  playerMesh.quaternion.set(rot.x, rot.y, rot.z, rot.w);
}
```

---

## Assets

### 3D Models (GLTF/GLB preferred)
Load models from external CDN URLs — not from local files (binary fetch fails in sandbox). No-login-required sources:

| Site | Content | License |
|------|---------|---------|
| **Poly Pizza** | 10K+ low-poly models | CC-BY/CC0 |
| **Kenney** | 40K+ game assets (2D/3D/audio) | CC0 |
| **Quaternius** | Low-poly game-ready models | CC0 |
| **itch.io** (3D tag) | Massive indie collection | Varies |
| **OpenGameArt** | Open source 2D/3D/audio | Varies |

### PBR Textures & HDRIs
- **ambientCG** / **Poly Haven** / **3Dtextures.me** — CC0, no login
- **Poly Haven HDRIs** — up to 16K resolution, CC0

### Loading Models from CDN

```js
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';

const draco = new DRACOLoader();
draco.setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.5.7/');

const loader = new GLTFLoader();
loader.setDRACOLoader(draco);

// Always use full CDN URLs for models, not local paths
loader.load('https://cdn.example.com/model.glb', (gltf) => {
  scene.add(gltf.scene);
  if (gltf.animations.length) {
    const mixer = new THREE.AnimationMixer(gltf.scene);
    gltf.animations.forEach((clip) => mixer.clipAction(clip).play());
  }
});
```

### Asset Optimization
- Use Draco-compressed GLTFs from asset sources
- Prefer KTX2/Basis Universal textures (75% GPU memory reduction)
- Keep textures at 1K-2K unless close-up detail is needed
- Choose stylized low-poly over high-poly realistic for browser performance
- Remove unused nodes/materials from loaded models

---

## Rendering

### Materials
- `MeshStandardMaterial` for PBR
- `MeshPhysicalMaterial` for clearcoat, transmission, sheen
- Normal maps to fake detail on low-poly surfaces
- Texture atlases to reduce draw calls

### Post-Processing
Use `EffectComposer` for Bloom, SSAO, Depth of Field, Color Grading, Vignette:

```js
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { SMAAPass } from 'three/examples/jsm/postprocessing/SMAAPass.js';

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
composer.addPass(new UnrealBloomPass(new THREE.Vector2(innerWidth, innerHeight), 0.5, 0.4, 0.85));
composer.addPass(new SMAAPass(innerWidth, innerHeight));
```

### Tone Mapping
- `ACESFilmicToneMapping` — cinematic, good default
- `ReinhardToneMapping` — softer, preserves highlights

---

## Performance

### Key Techniques
- **InstancedMesh** for repeated objects (trees, rocks, particles) — set matrices in a loop, update `instanceMatrix`
- **LOD** (`THREE.LOD`) — swap geometry detail by camera distance
- **Frustum culling** — manage `instancedMesh.count` to render only visible instances

### Rules
- Batch draw calls: fewer meshes with shared materials
- Cap `devicePixelRatio` at 2
- Use `renderer.info` to monitor draw calls and triangles
- Prefer low-poly stylized assets for consistent frame rates
- KTX2 textures to stay under browser GPU memory limits

---

## Testing & Debugging

**Read the Game Testing section below for the complete testing guide.** It covers:

- **Debug overlay** (required for every game) — FPS, frame time, draw calls, triangle count, memory. Visible for evaluation.
- **Video capture** — MediaRecorder API for recording gameplay to evaluate animations and physics.
- **Deterministic testing hooks** — `window.advanceTime(ms)`, `window.render_game_to_text()`, `window.simulateInput()` for reproducible, automated testing.
- **Performance profiling** — `renderer.info`, Performance API marks, CPU vs. GPU bottleneck identification, memory leak detection.
- **Common bug prevention** — Three.js resource disposal, animation frame leaks, event listener cleanup, z-fighting, audio context, GC stutter avoidance.
- **Sandbox testing** — defensive API usage, asset loading verification, pre-ship quality checklist.


**Shared files reference:** See `skills/website-building/SKILL.md` for the full shared file table. Key files for games: the Game Testing section below (mandatory), `shared/09-toolkit.md` (CDN/Three.js imports), the 2D Canvas section below (2D Canvas games).

---

# 2D Canvas Game Engineering

Engineering patterns for building 2D browser games with HTML5 Canvas API. Companion reference to `skills/website-building/game.md`.

**Mandatory shared foundations (if not already loaded):** the Design Tokens section and the Design System Proof section in `skills/website-building/SKILL.md`.

## Project Architecture

Four logical layers: Engine (game loop, rendering, input, audio), Game Logic (state machines, entity behaviors, rules), Data (configuration, levels, asset references), Visual (canvas drawing, sprite rendering, UI).

For single-file games (the default output), organize code in this order:
1. Constants and configuration
2. Utility functions (math, random, easing)
3. Core engine (game loop, input, audio)
4. Entity/component definitions
5. Game state and scene management
6. Initialization and startup

## The Game Loop

`requestAnimationFrame` with fixed timestep for physics, variable rendering:

```javascript
const TICK_RATE = 1000 / 60; // 60 updates per second
let lastTime = 0;
let accumulator = 0;

function gameLoop(timestamp) {
  const deltaTime = timestamp - lastTime;
  lastTime = timestamp;
  accumulator += deltaTime;
  // Fixed timestep updates (physics, game logic)
  while (accumulator >= TICK_RATE) {
    update(TICK_RATE / 1000); // pass seconds
    accumulator -= TICK_RATE;
  }
  // Variable timestep rendering
  const alpha = accumulator / TICK_RATE;
  render(alpha); // alpha for interpolation
  requestAnimationFrame(gameLoop);
}
requestAnimationFrame(gameLoop);
```

## Canvas Rendering

```javascript
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
ctx.imageSmoothingEnabled = false; // for pixel art

function render(alpha) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawBackground(ctx);
  // Draw game entities (sorted by z-order or y-position)
  entities.sort((a, b) => a.y - b.y);
  for (const entity of entities) {
    entity.draw(ctx, alpha);
  }
  drawUI(ctx); // always on top
}
```

## Sprite Animation

```javascript
class SpriteAnimation {
  constructor(image, frameWidth, frameHeight, frameCount, frameDuration) {
    this.image = image;
    this.frameWidth = frameWidth;
    this.frameHeight = frameHeight;
    this.frameCount = frameCount;
    this.frameDuration = frameDuration;
    this.currentFrame = 0;
    this.elapsed = 0;
  }

  update(dt) {
    this.elapsed += dt;
    if (this.elapsed >= this.frameDuration) {
      this.elapsed -= this.frameDuration;
      this.currentFrame = (this.currentFrame + 1) % this.frameCount;
    }
  }

  draw(ctx, x, y, flipX = false) {
    ctx.save();
    if (flipX) {
      ctx.scale(-1, 1);
      x = -x - this.frameWidth;
    }
    ctx.drawImage(
      this.image,
      this.currentFrame * this.frameWidth, 0,
      this.frameWidth, this.frameHeight,
      x, y, this.frameWidth, this.frameHeight
    );
    ctx.restore();
  }
}
```

## Input Handling

Track input state rather than responding to events directly:

```javascript
const Input = {
  keys: {},
  mouse: { x: 0, y: 0, down: false },
  justPressed: {},

  init(canvas) {
    document.addEventListener('keydown', (e) => {
      if (!this.keys[e.code]) this.justPressed[e.code] = true;
      this.keys[e.code] = true;
    });
    document.addEventListener('keyup', (e) => { this.keys[e.code] = false; });
    canvas.addEventListener('mousemove', (e) => {
      const rect = canvas.getBoundingClientRect();
      this.mouse.x = e.clientX - rect.left;
      this.mouse.y = e.clientY - rect.top;
    });
    canvas.addEventListener('mousedown', () => this.mouse.down = true);
    canvas.addEventListener('mouseup', () => this.mouse.down = false);
  },

  endFrame() { this.justPressed = {}; },
  isDown(code) { return !!this.keys[code]; },
  wasPressed(code) { return !!this.justPressed[code]; }
};
```

## Physics and Collision Detection

### Basic Physics with Euler Integration

```javascript
class PhysicsBody {
  constructor(x, y, w, h) {
    this.x = x; this.y = y; this.w = w; this.h = h;
    this.vx = 0; this.vy = 0; this.ax = 0; this.ay = 0;
    this.friction = 0.85;
    this.gravity = 980; // pixels/sec^2
    this.grounded = false;
  }

  update(dt) {
    this.vy += this.gravity * dt;
    this.vx += this.ax * dt;
    this.vy += this.ay * dt;
    this.x += this.vx * dt;
    this.y += this.vy * dt;
    this.vx *= this.friction;
    this.ax = 0; this.ay = 0;
  }
}
```

### AABB Collision Detection

```javascript
function aabbCollision(a, b) {
  return a.x < b.x + b.w && a.x + a.w > b.x &&
         a.y < b.y + b.h && a.y + a.h > b.y;
}

function resolveCollision(entity, obstacle) {
  const overlapX = Math.min(entity.x + entity.w - obstacle.x, obstacle.x + obstacle.w - entity.x);
  const overlapY = Math.min(entity.y + entity.h - obstacle.y, obstacle.y + obstacle.h - entity.y);
  if (overlapX < overlapY) {
    entity.x += (entity.vx > 0) ? -overlapX : overlapX;
    entity.vx = 0;
  } else {
    entity.y += (entity.vy > 0) ? -overlapY : overlapY;
    if (entity.vy > 0) entity.grounded = true;
    entity.vy = 0;
  }
}
```

### Circle Collision

```javascript
function circleCollision(a, b) {
  const dx = a.x - b.x, dy = a.y - b.y;
  return Math.sqrt(dx * dx + dy * dy) < a.radius + b.radius;
}
```

### Spatial Partitioning (for many entities)

```javascript
class SpatialGrid {
  constructor(cellSize) { this.cellSize = cellSize; this.cells = new Map(); }

  key(x, y) {
    return `${Math.floor(x / this.cellSize)},${Math.floor(y / this.cellSize)}`;
  }

  insert(entity) {
    const k = this.key(entity.x, entity.y);
    if (!this.cells.has(k)) this.cells.set(k, []);
    this.cells.get(k).push(entity);
  }

  query(x, y, radius) {
    const results = [], cs = this.cellSize;
    const minX = Math.floor((x - radius) / cs), maxX = Math.floor((x + radius) / cs);
    const minY = Math.floor((y - radius) / cs), maxY = Math.floor((y + radius) / cs);
    for (let cx = minX; cx <= maxX; cx++)
      for (let cy = minY; cy <= maxY; cy++) {
        const cell = this.cells.get(`${cx},${cy}`);
        if (cell) results.push(...cell);
      }
    return results;
  }

  clear() { this.cells.clear(); }
}
```

## Entity-Component Pattern

```javascript
class Entity {
  constructor(id) {
    this.id = id;
    this.components = {};
    this.active = true;
  }

  add(name, component) {
    this.components[name] = component;
    component.entity = this;
    return this;
  }

  get(name) { return this.components[name]; }
  has(name) { return name in this.components; }
}
```

## State Machines

```javascript
class StateMachine {
  constructor(owner) {
    this.owner = owner;
    this.states = {};
    this.current = null;
  }

  add(name, state) {
    this.states[name] = state;
    state.machine = this;
    state.owner = this.owner;
  }

  transition(name) {
    if (this.current) this.current.exit();
    this.current = this.states[name];
    this.current.enter();
  }

  update(dt) { if (this.current) this.current.update(dt); }
}
```

## Camera Systems

```javascript
class Camera {
  constructor(width, height) {
    this.x = 0; this.y = 0;
    this.width = width; this.height = height;
    this.smoothing = 0.1;
  }

  follow(target) {
    const targetX = target.x - this.width / 2;
    const targetY = target.y - this.height / 2;
    this.x += (targetX - this.x) * this.smoothing;
    this.y += (targetY - this.y) * this.smoothing;
  }

  clamp(worldWidth, worldHeight) {
    this.x = Math.max(0, Math.min(this.x, worldWidth - this.width));
    this.y = Math.max(0, Math.min(this.y, worldHeight - this.height));
  }

  apply(ctx) { ctx.translate(-Math.round(this.x), -Math.round(this.y)); }
}

// Parallax scrolling
function drawParallax(ctx, layers, camera) {
  for (const layer of layers) {
    const offsetX = camera.x * layer.speed;
    const x = -(offsetX % layer.width);
    ctx.drawImage(layer.image, x, 0);
    ctx.drawImage(layer.image, x + layer.width, 0);
  }
}
```

## Particle Systems (with Object Pooling)

```javascript
class Particle {
  constructor() { this.active = false; }

  init(x, y, vx, vy, life, color, size) {
    this.x = x; this.y = y; this.vx = vx; this.vy = vy;
    this.life = life; this.maxLife = life;
    this.color = color; this.size = size;
    this.active = true;
  }

  update(dt) {
    this.x += this.vx * dt;
    this.y += this.vy * dt;
    this.vy += 200 * dt;
    this.life -= dt;
    if (this.life <= 0) this.active = false;
  }

  draw(ctx) {
    const alpha = this.life / this.maxLife;
    ctx.globalAlpha = alpha;
    ctx.fillStyle = this.color;
    ctx.fillRect(this.x, this.y, this.size * alpha, this.size * alpha);
    ctx.globalAlpha = 1;
  }
}

class ParticlePool {
  constructor(size) { this.pool = Array.from({ length: size }, () => new Particle()); }

  emit(x, y, count, cfg) {
    let emitted = 0;
    for (const p of this.pool) {
      if (!p.active && emitted < count) {
        p.init(x, y, (Math.random() - 0.5) * cfg.spread, -Math.random() * cfg.speed,
          cfg.life + Math.random() * cfg.lifeVariance, cfg.color, cfg.size);
        emitted++;
      }
    }
  }

  update(dt) { for (const p of this.pool) if (p.active) p.update(dt); }
  draw(ctx) { for (const p of this.pool) if (p.active) p.draw(ctx); }
}
```

## Scene Management

```javascript
const SceneManager = {
  scenes: {},
  stack: [],

  register(name, scene) { this.scenes[name] = scene; },

  push(name, data) {
    const scene = this.scenes[name];
    this.stack.push(scene);
    if (scene.enter) scene.enter(data);
  },

  pop() {
    const scene = this.stack.pop();
    if (scene && scene.exit) scene.exit();
    return this.current;
  },

  replace(name, data) { this.pop(); this.push(name, data); },
  get current() { return this.stack[this.stack.length - 1]; },
  update(dt) { if (this.current) this.current.update(dt); },
  render(ctx) { if (this.current) this.current.render(ctx); }
};
```

## Tilemap Systems

```javascript
class Tilemap {
  constructor(data, tileSize) {
    this.data = data; // 2D array of tile IDs
    this.tileSize = tileSize;
    this.rows = data.length;
    this.cols = data[0].length;
  }

  getTile(col, row) {
    if (row < 0 || row >= this.rows || col < 0 || col >= this.cols) return 1;
    return this.data[row][col];
  }

  draw(ctx, camera, tileColors) {
    const ts = this.tileSize;
    const startCol = Math.floor(camera.x / ts), endCol = Math.ceil((camera.x + camera.width) / ts);
    const startRow = Math.floor(camera.y / ts), endRow = Math.ceil((camera.y + camera.height) / ts);
    for (let row = startRow; row <= endRow; row++) {
      for (let col = startCol; col <= endCol; col++) {
        const tile = this.getTile(col, row);
        if (tile === 0) continue;
        ctx.fillStyle = tileColors[tile] || '#888';
        ctx.fillRect(col * ts, row * ts, ts, ts);
      }
    }
  }

  isSolid(x, y) {
    return this.getTile(Math.floor(x / this.tileSize), Math.floor(y / this.tileSize)) !== 0;
  }
}
```

## Simple AI Patterns

```javascript
function patrol(entity, pointA, pointB, speed) {
  const target = entity.movingToB ? pointB : pointA;
  const dx = target.x - entity.x, dy = target.y - entity.y;
  const dist = Math.sqrt(dx * dx + dy * dy);
  if (dist < 5) { entity.movingToB = !entity.movingToB; }
  else { entity.vx = (dx / dist) * speed; entity.vy = (dy / dist) * speed; }
}

function chase(entity, target, speed) {
  const dx = target.x - entity.x, dy = target.y - entity.y;
  const dist = Math.sqrt(dx * dx + dy * dy);
  if (dist > 0) { entity.vx = (dx / dist) * speed; entity.vy = (dy / dist) * speed; }
}

function flee(entity, target, speed) { chase(entity, target, -speed); }

function hasLineOfSight(entity, target, tilemap) {
  const steps = 20;
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const x = entity.x + (target.x - entity.x) * t;
    const y = entity.y + (target.y - entity.y) * t;
    if (tilemap.isSolid(x, y)) return false;
  }
  return true;
}
```

## Procedural Generation

```javascript
// Cave/dungeon via cellular automata
function generateCaveMap(width, height, fillChance = 0.45, iterations = 5) {
  let map = Array.from({ length: height }, () =>
    Array.from({ length: width }, () => Math.random() < fillChance ? 1 : 0)
  );
  for (let i = 0; i < iterations; i++) {
    const newMap = map.map(row => [...row]);
    for (let y = 1; y < height - 1; y++) {
      for (let x = 1; x < width - 1; x++) {
        let neighbors = 0;
        for (let dy = -1; dy <= 1; dy++)
          for (let dx = -1; dx <= 1; dx++) {
            if (dx === 0 && dy === 0) continue;
            neighbors += map[y + dy][x + dx];
          }
        newMap[y][x] = neighbors > 4 ? 1 : neighbors < 4 ? 0 : map[y][x];
      }
    }
    map = newMap;
  }
  for (let y = 0; y < height; y++) { map[y][0] = 1; map[y][width - 1] = 1; }
  for (let x = 0; x < width; x++) { map[0][x] = 1; map[height - 1][x] = 1; }
  return map;
}
```

## Utility Functions

```javascript
const Utils = {
  lerp: (a, b, t) => a + (b - a) * t,
  clamp: (val, min, max) => Math.max(min, Math.min(max, val)),
  randRange: (min, max) => Math.random() * (max - min) + min,
  randInt: (min, max) => Math.floor(Math.random() * (max - min + 1)) + min,
  distance: (x1, y1, x2, y2) => Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2),
  angle: (x1, y1, x2, y2) => Math.atan2(y2 - y1, x2 - x1),
  easeOutQuad: (t) => t * (2 - t),
  easeInOutCubic: (t) => t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2,
  easeOutElastic: (t) => {
    const c4 = (2 * Math.PI) / 3;
    return t === 0 ? 0 : t === 1 ? 1
      : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1;
  },
  easeOutBounce: (t) => {
    const n1 = 7.5625, d1 = 2.75;
    if (t < 1 / d1) return n1 * t * t;
    if (t < 2 / d1) return n1 * (t -= 1.5 / d1) * t + 0.75;
    if (t < 2.5 / d1) return n1 * (t -= 2.25 / d1) * t + 0.9375;
    return n1 * (t -= 2.625 / d1) * t + 0.984375;
  }
};
```

---

# Game Testing & Development

Build games in small steps and validate every change. Treat each iteration as: implement → act → pause → observe → adjust.

## Workflow

1. **Pick a goal.** Define a single feature or behavior to implement.
2. **Implement small.** Make the smallest change that moves the game forward.
3. **Ensure integration points.** Provide a single canvas and `window.render_game_to_text` so the test loop can read state.
4. **Add `window.advanceTime(ms)`.** Strongly prefer a deterministic step hook so tests can advance frames reliably.
5. **Initialize progress.md.** If `progress.md` exists, read it first and confirm the original user prompt is recorded at the top (prefix with `Original prompt:`). Also note any TODOs and suggestions left by the previous agent. If missing, create it and write `Original prompt: <prompt>` at the top before appending updates.
6. **Verify controls and state (multi-step focus).** Exhaustively exercise all important interactions. For each, think through the full multi-step sequence it implies (cause → intermediate states → outcome) and verify the entire chain works end-to-end. Confirm `render_game_to_text` reflects the same state shown on screen. If anything is off, fix and rerun.
  Examples of important interactions: move, jump, shoot/attack, interact/use, select/confirm/cancel in menus, pause/resume, restart, and any special abilities or puzzle actions defined by the request. Multi-step examples: shooting an enemy should reduce its health; when health reaches 0 it should disappear and update the score; collecting a key should unlock a door and allow level progression.
7. **Check errors.** Review console errors and fix the first new issue before continuing.
8. **Reset between scenarios.** Avoid cross-test state when validating distinct features.
9. **Iterate with small deltas.** Change one variable at a time (frames, inputs, timing, positions) until stable.

## Test Checklist

Test any new features added for the request and any areas your logic changes could affect. Identify issues, fix them, and re-run the tests to confirm they're resolved.

Examples of things to test:

- Primary movement/interaction inputs (e.g., move, jump, shoot, confirm/select).
- Win/lose or success/fail transitions.
- Score/health/resource changes.
- Boundary conditions (collisions, walls, screen edges).
- Menu/pause/start flow if present.
- Any special actions tied to the request (powerups, combos, abilities, puzzles, timers).

## Test Artifacts to Review

- Latest `render_game_to_text` JSON output.
- Console error logs (fix the first new error before continuing).
Ensure everything that should be visible on screen is actually visible. Verify all newly added features. If something is missing, it is missing in the build. Fix and rerun in a tight loop until the text state looks correct. Once fixes are verified, re-test all important interactions and controls, confirm they work, and ensure your changes did not introduce regressions. If they did, fix them and rerun everything in a loop until interactions, text state, and controls all work as expected. Be exhaustive in testing controls; broken games are not acceptable.

## Core Game Guidelines

### Canvas + Layout

- Prefer a single canvas centered in the window.

### Visuals

- Keep on-screen text minimal; show controls on a start/menu screen rather than overlaying them during play.
- Avoid overly dark scenes unless the design calls for it. Make key elements easy to see.
- Draw the background on the canvas itself instead of relying on CSS backgrounds.

### Generated Art Assets

When using `generate_image` for game sprites, tiles, or UI elements, generate with transparent backgrounds to get PNGs with transparent backgrounds ready for compositing.

### Text State Output (render_game_to_text)

Expose a `window.render_game_to_text` function that returns a concise JSON string representing the current game state. The text should include enough information to play the game without visuals.

Minimal pattern:

```js
function renderGameToText() {
  const payload = {
    mode: state.mode,
    player: { x: state.player.x, y: state.player.y, r: state.player.r },
    entities: state.entities.map((e) => ({ x: e.x, y: e.y, r: e.r })),
    score: state.score,
  };
  return JSON.stringify(payload);
}
window.render_game_to_text = renderGameToText;
```

Keep the payload succinct and biased toward on-screen/interactive elements. Prefer current, visible entities over full history.
Include a clear coordinate system note (origin and axis directions), and encode all player-relevant state: player position/velocity, active obstacles/enemies, collectibles, timers/cooldowns, score, and any mode/state flags needed to make correct decisions. Avoid large histories; only include what's currently relevant and visible.

### Waiting for Game State

Use `waitForFunction` with `render_game_to_text` to wait for state transitions instead of blind timeouts:

```javascript
await page.waitForFunction(
  () => { try { return JSON.parse(window.render_game_to_text()).phase === 'racing'; } catch { return false; } },
  null, { timeout: 15000 }
);
```

### Time Stepping Hook

Provide a deterministic time-stepping hook so tests can advance the game in controlled increments. Expose `window.advanceTime(ms)` (or a thin wrapper that forwards to your game update loop) and have the game loop use it when present.

Minimal pattern:

```js
window.advanceTime = (ms) => {
  const steps = Math.max(1, Math.round(ms / (1000 / 60)));
  for (let i = 0; i < steps; i++) update(1 / 60);
  render();
};
```

### Fullscreen Toggle

- Use a single key (prefer `f`) to toggle fullscreen on/off.
- Allow `Esc` to exit fullscreen.
- When fullscreen toggles, resize the canvas/rendering so visuals and input mapping stay correct.

## Debug Overlay (Required)

Every game must include a performance overlay visible by default; only hide when the user explicitly requests a clean build.

### Three.js Debug HUD

```javascript
class DebugOverlay {
  constructor(renderer) {
    this.renderer = renderer;
    this.el = document.createElement('div');
    this.el.style.cssText = `
      position:fixed;top:0;left:0;z-index:99999;
      background:rgba(0,0,0,.75);color:#0f0;
      font:11px/1.5 monospace;padding:6px 10px;
      pointer-events:none;white-space:pre;
    `;
    document.body.appendChild(this.el);
    this.frames = 0;
    this.lastTime = performance.now();
    this.lastFrameTime = performance.now();
    this.frameTimes = [];
  }

  update() {
    const now = performance.now();
    this.frameTimes.push(now - this.lastFrameTime);
    this.lastFrameTime = now;
    this.frames++;

    if (now - this.lastTime >= 1000) {
      const fps = (this.frames * 1000) / (now - this.lastTime);
      const avg = this.frameTimes.reduce((a, b) => a + b, 0) / this.frameTimes.length;
      const max = Math.max(...this.frameTimes);
      const info = this.renderer?.info;

      const lines = [`FPS:${fps.toFixed(0)} Frame:${avg.toFixed(1)}ms (max ${max.toFixed(1)}ms)`];
      if (info) lines.push(`Draw:${info.render?.calls} Tri:${info.render?.triangles} Geo:${info.memory?.geometries} Tex:${info.memory?.textures}`);
      if (performance.memory) lines.push(`Heap:${(performance.memory.usedJSHeapSize/1048576).toFixed(1)}MB`);

      const warn = [];
      if (fps < 30) warn.push('⚠LOW FPS');
      if (info?.render?.calls > 200) warn.push('⚠DRAW CALLS');
      if (info?.memory?.geometries > 500) warn.push('⚠GEO LEAK');
      if (warn.length) lines.push(warn.join(' '));

      this.el.textContent = lines.join('\n');
      this.frames = 0; this.lastTime = now; this.frameTimes = [];
    }
  }
}
// Usage: const debug = new DebugOverlay(renderer); call debug.update() each frame
```

### 2D Canvas FPS Counter

```javascript
let _frames = 0, _last = performance.now(), _fps = 0, _ft = 0, _prev = 0;
function updateDebug() {
  _frames++; const n = performance.now(); _ft = n - (_prev||n); _prev = n;
  if (n - _last >= 1000) { _fps = (_frames*1000)/(n-_last); _frames=0; _last=n; }
}
function drawDebug(ctx) {
  ctx.save(); ctx.fillStyle='rgba(0,0,0,.75)'; ctx.fillRect(0,0,200,20);
  ctx.font='11px monospace'; ctx.fillStyle=_fps<30?'#f44':'#0f0';
  ctx.fillText(`FPS:${_fps.toFixed(0)} ${_ft.toFixed(1)}ms`,6,14); ctx.restore();
}
```

## Runtime Tweaking with lil-gui

Use **lil-gui** (`import GUI from 'https://esm.sh/lil-gui'`) for live parameter adjustment:

```javascript
const params = { gravity: 9.81, playerSpeed: 5, bloomStrength: 0.5, debugPhysics: false };
const gui = new GUI({ title: 'Settings' });
gui.add(params, 'gravity', 0, 20, 0.1);
gui.add(params, 'playerSpeed', 1, 20, 0.5);
gui.add(params, 'bloomStrength', 0, 2, 0.05);
gui.add(params, 'debugPhysics');
```

## Visual Evaluation

| When | Capture | Check |
|---|---|---|
| Initial load | Title/menu | Fonts loaded? Layout correct? Debug overlay showing? |
| Gameplay | Active scene | FPS 50+? Entities rendering? No z-fighting? HUD readable? |
| Interactions | Post-action | State change visible? Particles? Score updated? |
| Edge cases | Game over, pause | Design system consistent? Typography matches tokens? |
| Both sizes | 1280px + 375px | Responsive? Touch targets adequate? |

Checklist per evaluation:
- Rendering correct — all elements present and positioned
- FPS 50+ (below 30 = failure)
- No visual glitches (z-fighting, clipping, pop-in)
- UI text readable over scene (contrast safety from `skills/website-building/game.md`)
- Design tokens applied consistently
- Memory stable (not growing between checks)

## Performance Profiling

### Targets

| Metric | Target | Red Flag | Source |
|---|---|---|---|
| FPS | 60 | <30 | Debug overlay |
| Frame time | ≤16.67ms | >33ms | `performance.now()` delta |
| Draw calls | <100 mobile, <300 desktop | >500 | `renderer.info.render.calls` |
| Geometries | Stable | Growing | `renderer.info.memory.geometries` |
| Textures | Stable | Growing | `renderer.info.memory.textures` |
| JS Heap | Stable after warmup | Growing | `performance.memory` |

### renderer.info (Three.js)

Call `renderer.info.reset()` before rendering each frame — without it, counters accumulate across frames.

```javascript
function gameLoop() {
  requestAnimationFrame(gameLoop);
  renderer.info.reset();
  // ... update ...
  renderer.render(scene, camera);
  debug.update(); // reads per-frame stats
}
```

### CPU vs GPU Bottleneck

Halve canvas resolution (`renderer.setSize(w/2, h/2)`). FPS jumps → GPU-bound. No change → CPU-bound (game logic, physics, or draw calls).

### Memory Leak Detection

```javascript
setInterval(() => {
  const i = renderer.info;
  console.log(`[Mem] Geo:${i.memory.geometries} Tex:${i.memory.textures}`);
}, 10000);
```

If counts grow, you have a disposal leak. See Common Bugs below.

## Common Bugs

### Three.js Resource Disposal

Three.js does NOT garbage-collect GPU resources. Call `dispose()` on geometry, material, and textures when removing objects:

```javascript
function removeObject(obj) {
  obj.geometry?.dispose();
  const mats = Array.isArray(obj.material) ? obj.material : [obj.material].filter(Boolean);
  mats.forEach(m => { Object.values(m).forEach(v => v?.dispose?.()); m.dispose(); });
  obj.removeFromParent();
}
```

### Animation Frame Leaks

Always store the RAF ID: `rafId = requestAnimationFrame(animate)`. Cancel on cleanup: `cancelAnimationFrame(rafId)`.

### Event Listener Cleanup

Use `AbortController` for bulk removal:

```javascript
const ac = new AbortController();
window.addEventListener('resize', onResize, { signal: ac.signal });
window.addEventListener('keydown', onKey, { signal: ac.signal });
// Cleanup: ac.abort();
```

### Z-Fighting

Fixes in order: (1) offset geometry by 0.01 units, (2) tighten near/far planes (`near:0.1, far:1000` not `0.001/100000`), (3) `material.polygonOffset = true`, (4) logarithmic depth buffer (last resort).

### Audio Context

Resume on user gesture: `document.addEventListener('click', () => audioCtx.resume(), { once: true });`

### Physics Tunneling

Cap max velocity. Enable CCD in Rapier. Make collision bodies thicker than visual geometry.

### GC Stutters

Pre-allocate vectors/objects outside the game loop. Avoid `map()`, `filter()`, spread in hot paths. Use object pools for particles.

## Pre-Ship Checklist

**Performance:** 55+ fps avg · 30+ fps 1% low · draw calls <200 · stable memory · no GC stutters

**Visual:** All screens verified · no artifacts · UI readable over all backgrounds · fonts loaded · design tokens consistent

**Functional:** All actions work · AI/NPC correct · score/health tracked · game-over triggers · audio plays · no console errors

**Sandbox:** Loads in iframe · no localStorage refs · all assets from CDN · controls work without Pointer Lock · fills viewport

**Cleanup:** RAF IDs stored · listeners removable · Three.js resources disposed · no orphaned timers

## Progress Tracking
Create a `progress.md` file if it doesn't exist, and append TODOs, notes, gotchas, and loose ends as you go so another agent can pick up seamlessly.
If a `progress.md` file already exists, read it first, including the original user prompt at the top (you may be continuing another agent's work). Do not overwrite the original prompt; preserve it.
Update `progress.md` after each meaningful chunk of work (feature added, bug found, test run, or decision made).
At the end of your work, leave TODOs and suggestions for the next agent in `progress.md`.
