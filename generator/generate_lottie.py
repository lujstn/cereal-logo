#!/usr/bin/env python3
"""Single source of truth for the Cereal balloon-inflate logo animation.

Parses cereal.svg, builds each timing take as Lottie JSON, then fans the output
out across the whole monorepo: the shared assets folder, a manifest, the local
preview page, and every platform package (React, React Native, SwiftUI, Android).
Re-run this after any change to a take and every consumer stays in sync.

The published component ships the three takes in PUBLISHED_MODES; `classic` is
kept for the preview but not distributed.

Tweak VARIANTS / INFLATE_ANCHORS / INFLATE_BOUNCE and re-run.
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
SVG_FILE = HERE / "cereal.svg"
ASSETS = ROOT / "assets"
PACKAGES = ROOT / "packages"

# Single source of truth for the version: the root package.json.
VERSION = json.loads((ROOT / "package.json").read_text())["version"]

# Takes distributed in the cross-platform component (order defines the tab/enum order).
PUBLISHED_MODES = ["flow", "split", "bloom"]

SCALE = 4.0
OFFSET = (30.0, 24.0)
COMP_W, COMP_H = 480, 160
FPS = 60
INK = [0.2, 0.2, 0.2, 1]  # #333333

LETTER_NAMES = ["C", "e1", "r", "e2", "a", "l"]

# Frames after a letter starts inflating that its haptic tap lands (near the pop peak).
HAPTIC_LAND = 8


# ---------------------------------------------------------------- SVG parsing

NUM = r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?"
TOKENS = re.compile(rf"([MmLlHhVvCcSsQqTtZz])|({NUM})")


class PathBuilder:
    def __init__(self):
        self.subpaths = []
        self.v, self.i, self.o = [], [], []

    def move_to(self, p):
        self.flush(False)
        self.v, self.i, self.o = [list(p)], [[0.0, 0.0]], [[0.0, 0.0]]

    def line_to(self, p):
        self.v.append(list(p))
        self.i.append([0.0, 0.0])
        self.o.append([0.0, 0.0])

    def curve_to(self, c1, c2, p):
        cur = self.v[-1]
        self.o[-1] = [c1[0] - cur[0], c1[1] - cur[1]]
        self.v.append(list(p))
        self.i.append([c2[0] - p[0], c2[1] - p[1]])
        self.o.append([0.0, 0.0])

    def close(self):
        if len(self.v) > 1:
            dx = self.v[-1][0] - self.v[0][0]
            dy = self.v[-1][1] - self.v[0][1]
            if dx * dx + dy * dy < 1e-6:
                self.i[0] = self.i[-1]
                self.v.pop(), self.i.pop(), self.o.pop()
        if self.v:
            self.subpaths.append({"v": self.v, "i": self.i, "o": self.o, "c": True})
        self.v, self.i, self.o = [], [], []

    def flush(self, closed):
        if len(self.v) > 1:
            self.subpaths.append({"v": self.v, "i": self.i, "o": self.o, "c": closed})
        self.v, self.i, self.o = [], [], []


def parse_path(d):
    tokens = [(m.group(1), m.group(2)) for m in TOKENS.finditer(d)]
    pos = 0

    def read(n):
        nonlocal pos
        vals = [float(tokens[pos + k][1]) for k in range(n)]
        pos += n
        return vals

    b = PathBuilder()
    cur = (0.0, 0.0)
    start = (0.0, 0.0)
    last_c2 = None
    last_q = None
    cmd = None

    while pos < len(tokens):
        if tokens[pos][0]:
            cmd = tokens[pos][0]
            pos += 1
        elif cmd in ("M", "m"):
            cmd = "L" if cmd == "M" else "l"
        rel = cmd.islower()
        op = cmd.upper()

        def pt(x, y):
            return (cur[0] + x, cur[1] + y) if rel else (x, y)

        if op == "M":
            x, y = read(2)
            cur = start = pt(x, y)
            b.move_to(cur)
            last_c2 = last_q = None
        elif op == "L":
            x, y = read(2)
            cur = pt(x, y)
            b.line_to(cur)
            last_c2 = last_q = None
        elif op == "H":
            (x,) = read(1)
            cur = (cur[0] + x if rel else x, cur[1])
            b.line_to(cur)
            last_c2 = last_q = None
        elif op == "V":
            (y,) = read(1)
            cur = (cur[0], cur[1] + y if rel else y)
            b.line_to(cur)
            last_c2 = last_q = None
        elif op in ("C", "S"):
            if op == "C":
                x1, y1, x2, y2, x, y = read(6)
                c1 = pt(x1, y1)
            else:
                x2, y2, x, y = read(4)
                c1 = (2 * cur[0] - last_c2[0], 2 * cur[1] - last_c2[1]) if last_c2 else cur
            c2 = pt(x2, y2)
            end = pt(x, y)
            b.curve_to(c1, c2, end)
            cur, last_c2, last_q = end, c2, None
        elif op in ("Q", "T"):
            if op == "Q":
                qx, qy, x, y = read(4)
                q = pt(qx, qy)
            else:
                q = (2 * cur[0] - last_q[0], 2 * cur[1] - last_q[1]) if last_q else cur
            end = pt(x, y) if op == "Q" else pt(*read(2))
            c1 = (cur[0] + 2 / 3 * (q[0] - cur[0]), cur[1] + 2 / 3 * (q[1] - cur[1]))
            c2 = (end[0] + 2 / 3 * (q[0] - end[0]), end[1] + 2 / 3 * (q[1] - end[1]))
            b.curve_to(c1, c2, end)
            cur, last_q, last_c2 = end, q, None
        elif op == "Z":
            b.close()
            cur = start
            last_c2 = last_q = None
        else:
            raise ValueError(f"Unsupported command {cmd}")

    b.flush(False)
    return b.subpaths


def transform(subpaths):
    out = []
    for sp in subpaths:
        out.append({
            "v": [[round(x * SCALE + OFFSET[0], 3), round(y * SCALE + OFFSET[1], 3)] for x, y in sp["v"]],
            "i": [[round(x * SCALE, 3), round(y * SCALE, 3)] for x, y in sp["i"]],
            "o": [[round(x * SCALE, 3), round(y * SCALE, 3)] for x, y in sp["o"]],
            "c": sp["c"],
        })
    return out


def bbox(subpaths):
    xs, ys = [], []
    for sp in subpaths:
        n = len(sp["v"])
        segs = n if sp["c"] else n - 1
        for k in range(segs):
            a = sp["v"][k]
            e = sp["v"][(k + 1) % n]
            c1 = [a[0] + sp["o"][k][0], a[1] + sp["o"][k][1]]
            c2 = [e[0] + sp["i"][(k + 1) % n][0], e[1] + sp["i"][(k + 1) % n][1]]
            for j in range(9):
                t = j / 8
                mt = 1 - t
                xs.append(mt ** 3 * a[0] + 3 * mt * mt * t * c1[0] + 3 * mt * t * t * c2[0] + t ** 3 * e[0])
                ys.append(mt ** 3 * a[1] + 3 * mt * mt * t * c1[1] + 3 * mt * t * t * c2[1] + t ** 3 * e[1])
    return min(xs), min(ys), max(xs), max(ys)


# ------------------------------------------------------------- Lottie helpers

def static(v):
    return {"a": 0, "k": v}


def ease(ox, oy, ix, iy, dims=1):
    return ({"x": [ox] * dims, "y": [oy] * dims}, {"x": [ix] * dims, "y": [iy] * dims})


def anim(keyframes):
    out = []
    for t, v, e in keyframes:
        kf = {"t": t, "s": v}
        if e:
            kf["o"], kf["i"] = e
        out.append(kf)
    return {"a": 1, "k": out}


def shape_paths(subpaths):
    return [{"ty": "sh", "ks": {"a": 0, "k": {"i": sp["i"], "o": sp["o"], "v": sp["v"], "c": sp["c"]}}, "nm": "p"}
            for sp in subpaths]


def group(items, name):
    items = items + [{"ty": "tr", "p": static([0, 0]), "a": static([0, 0]), "s": static([100, 100]),
                      "r": static(0), "o": static(100), "nm": "tr"}]
    return {"ty": "gr", "it": items, "nm": name}


def fill(opacity=None):
    # r=1 is nonzero winding, matching the source SVG's default fill-rule. Even-odd
    # would hollow out the self-overlapping balloon terminals into white notches.
    return {"ty": "fl", "c": static(INK), "o": opacity or static(100), "r": 1, "nm": "fill"}


def layer(ind, name, ks, shapes, op):
    return {"ddd": 0, "ind": ind, "ty": 4, "nm": name, "sr": 1, "ks": ks, "ao": 0,
            "shapes": shapes, "ip": 0, "op": op, "st": 0, "bm": 0}


def document(name, layers, op):
    return {"v": "5.12.2", "fr": FPS, "ip": 0, "op": op, "w": COMP_W, "h": COMP_H,
            "nm": name, "ddd": 0, "assets": [], "layers": layers}


def anchored_ks(letter, opacity, scale, anchor=(0.5, 1.0), rotation=None):
    x0, y0, x1, y1 = letter["bbox"]
    fx, fy = anchor
    ax = round(x0 + fx * (x1 - x0), 2)
    ay = round(y0 + fy * (y1 - y0), 2)
    return {"o": opacity, "r": rotation or static(0),
            "p": static([ax, ay, 0]), "a": static([ax, ay, 0]), "s": scale}


# ----------------------------------------------------------------- variants

# Anchor per letter as (horizontal, vertical) bbox fractions: 0 = left/top, 1 = right/bottom.
INFLATE_ANCHORS = {
    "C": (0.5, 1.0),
    "e1": (0.0, 0.5),
    "r": (0.5, 1.0),
    "e2": (0.5, 0.0),
    "a": (0.5, 1.0),
    "l": (0.5, 1.0),
}

# Per-letter multiplier on the overshoot/squash bounce (1.0 = default elasticity,
# lower = tighter pop). Letters not listed use 1.0.
INFLATE_BOUNCE = {
    "r": 0.6,
}


def scale_bounce(vals, factor):
    return [round(100 + (v - 100) * factor) for v in vals]


# Each take defines the order the letters ignite in and the pacing between waves.
#   order  : wave rank per letter position (c e r e a l). Equal ranks fire together.
#   stagger: frames between one wave and the next.
#   beats  : frame offsets for overshoot / squash / rebound / settle within a letter.
START = 6
BEATS = (13, 22, 30, 38)

# Frames kept after the final letter lands before the comp ends. Deliberately short:
# consumers reveal on the finish callback, so a long tail here becomes a dead pause on
# launch. The comp ends just after the last keyframe settles, not on a static wordmark.
SETTLE = 4
VARIANTS = {
    "classic": {
        "label": "Classic", "desc": "the original pace, letters pop left to right one after another",
        "order": [0, 1, 2, 3, 4, 5], "stagger": 7, "beats": BEATS,
    },
    "flow": {
        "label": "Flow", "desc": "same pop speed, tighter stagger so the wave rolls through",
        "order": [0, 1, 2, 3, 4, 5], "stagger": 5, "beats": BEATS,
    },
    "split": {
        "label": "Split", "desc": "c leads, then a and e burst in together, and r e l complete the word",
        "order": [0, 1, 2, 3, 1, 4], "stagger": 6, "beats": BEATS,
    },
    "bloom": {
        "label": "Bloom", "desc": "ignites in the centre and blooms outward to both ends",
        "order": [2, 1, 0, 0, 1, 2], "stagger": 6, "beats": BEATS,
    },
}
VARIANT_ORDER = ["classic", "flow", "split", "bloom"]


def build_inflate(letters, key):
    cfg = VARIANTS[key]
    order, stagger = cfg["order"], cfg["stagger"]
    b1, b2, b3, b4 = cfg["beats"]
    # The last letter to fire lands its final keyframe at START + max(order)*stagger + b4;
    # end the comp SETTLE frames after that so nothing rests on a finished-but-static word.
    op = START + max(order) * stagger + b4 + SETTLE
    layers = []
    for idx, letter in enumerate(letters):
        t0 = START + order[idx] * stagger
        anchor = INFLATE_ANCHORS[letter["name"]]
        # Overshoot stretches along the growth direction: sideways for edge-middle
        # anchors, vertically for top or bottom anchors.
        sideways = anchor[1] == 0.5
        over = [124, 112] if sideways else [112, 124]
        squash = [92, 104] if sideways else [104, 92]
        settle = [98, 103]
        bounce = INFLATE_BOUNCE.get(letter["name"], 1.0)
        if bounce != 1.0:
            over, squash, settle = (scale_bounce(v, bounce) for v in (over, squash, settle))
        opacity = anim([(t0, [0], ease(0.33, 0, 0.67, 1)), (t0 + 4, [100], None)])
        scale = anim([
            (t0, [0, 0, 100], ease(0.5, 0.0, 0.15, 1.0, 3)),
            (t0 + b1, over + [100], ease(0.35, 0, 0.25, 1, 3)),
            (t0 + b2, squash + [100], ease(0.4, 0, 0.3, 1, 3)),
            (t0 + b3, settle + [100], ease(0.4, 0, 0.3, 1, 3)),
            (t0 + b4, [100, 100, 100], None),
        ])
        ks = anchored_ks(letter, opacity, scale, anchor)
        shapes = [group(shape_paths(letter["subpaths"]) + [fill()], letter["name"])]
        layers.append(layer(idx + 1, letter["name"], ks, shapes, op))
    return document(f"Cereal - inflate ({key})", layers, op)


# ------------------------------------------------------------------ preview

PREVIEW_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cereal balloon inflate</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.12.2/lottie.min.js"></script>
<style>
  :root { --bg: #ffffff; --panel: #fafafa; --ink: #333; --line: #e6e6e6; --muted: #8a8a8a; --accent: #333; }
  body.cream { --bg: #fff6ec; --panel: #fffdf9; --line: #efe2d1; --muted: #a08b70; }
  body.dark  { --bg: #1c1c1e; --panel: #2a2a2c; --ink: #f2f2f2; --line: #3a3a3c; --muted: #9a9a9e; --accent: #f2f2f2; }
  * { box-sizing: border-box; }
  body { margin: 0; padding: 36px 20px 72px; background: var(--bg); color: var(--ink);
         font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
         transition: background .25s; }
  h1 { text-align: center; font-size: 22px; margin: 0 0 4px; }
  p.sub { text-align: center; margin: 0 0 26px; color: var(--muted); font-size: 13.5px; }
  .wrap { max-width: 760px; margin: 0 auto; }

  .tabs { display: flex; gap: 6px; justify-content: center; margin-bottom: 20px; flex-wrap: wrap; }
  .tabs button { flex: 1 1 160px; max-width: 200px; border: 1px solid var(--line); background: var(--panel);
                 color: var(--ink); border-radius: 12px; padding: 11px 10px; cursor: pointer;
                 text-align: center; transition: all .15s; }
  .tabs button b { display: block; font-size: 13.5px; margin-bottom: 2px; }
  .tabs button small { color: var(--muted); font-size: 10.5px; line-height: 1.3; display: block; }
  .tabs button.active { border-color: var(--accent); box-shadow: inset 0 0 0 1px var(--accent); }

  .stageWrap { background: var(--panel); border: 1px solid var(--line); border-radius: 18px;
               padding: 8px; transition: background .25s; }
  .stage { width: 100%; aspect-ratio: 3 / 1; }
  .stage svg { width: 100%; height: 100%; display: block; }
  body.dark .stage svg path { fill: #f2f2f2 !important; }

  .timeline { display: flex; align-items: center; gap: 12px; margin: 16px 2px 4px; }
  input[type=range] { flex: 1; accent-color: var(--accent); height: 4px; cursor: pointer; }
  .time { font-variant-numeric: tabular-nums; font-size: 12px; color: var(--muted); min-width: 92px; text-align: right; }

  .controls { display: flex; justify-content: center; gap: 8px; margin-top: 14px; flex-wrap: wrap; }
  .controls button { border: 1px solid var(--line); background: var(--panel); color: var(--ink);
           border-radius: 9px; padding: 8px 15px; font-size: 13px; cursor: pointer; min-width: 44px; }
  .controls button:hover { border-color: var(--muted); }
  .controls .seg { display: inline-flex; border: 1px solid var(--line); border-radius: 9px; overflow: hidden; }
  .controls .seg button { border: 0; border-radius: 0; }
  .controls .seg button.on { background: var(--accent); color: var(--bg); }

  .caption { text-align: center; color: var(--muted); font-size: 13px; margin: 22px 0 0; }
  .caption b { color: var(--ink); }

  details { max-width: 760px; margin: 40px auto 0; border-top: 1px solid var(--line); padding-top: 20px; }
  summary { cursor: pointer; font-size: 14px; font-weight: 600; }
  details h3 { font-size: 13px; margin: 20px 0 6px; }
  pre { background: var(--panel); border: 1px solid var(--line); border-radius: 10px; padding: 14px 16px;
        overflow-x: auto; font-size: 12px; line-height: 1.5; }
  code { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
  kbd { background: var(--panel); border: 1px solid var(--line); border-bottom-width: 2px;
        border-radius: 5px; padding: 1px 6px; font-size: 11px; font-family: inherit; }
</style>
</head>
<body>
<div class="wrap">
  <h1>Cereal balloon inflate</h1>
  <p class="sub">Pick a take, watch it solo, scrub the timeline. <kbd>&larr;</kbd><kbd>&rarr;</kbd> switch &middot; <kbd>space</kbd> play/pause &middot; <kbd>R</kbd> replay</p>

  <div class="tabs" id="tabs"></div>

  <div class="stageWrap"><div class="stage" id="stage"></div></div>

  <div class="timeline">
    <input type="range" id="scrub" min="0" max="100" value="0" step="1">
    <span class="time" id="time">0.00s / 0.00s</span>
  </div>

  <div class="controls">
    <button id="playBtn" onclick="togglePlay()">Pause</button>
    <button onclick="replay()">Replay</button>
    <span class="seg">
      <button id="sp05" onclick="setSpeed(0.5)">0.5&times;</button>
      <button id="sp1" class="on" onclick="setSpeed(1)">1&times;</button>
    </span>
    <button id="loopBtn" onclick="toggleLoop()">Loop: on</button>
    <button onclick="cycleBg()">Background</button>
  </div>

  <p class="caption" id="caption"></p>
</div>

<details>
  <summary>Using the component (same three takes, every platform)</summary>
  <p style="color:var(--muted);font-size:13px;max-width:660px">Each platform ships a <code>CerealLogo</code> component with a <code>mode</code> of
  flow / split / bloom / random. It is plain Lottie JSON rendered by each platform's native Lottie player, so it looks identical everywhere and honours the OS reduced-motion setting.</p>

  <h3>React &middot; @lujstn/cereal-logo-react</h3>
  <pre><code>import { CerealLogo } from '@lujstn/cereal-logo-react';

&lt;CerealLogo mode="random" style={{ width: 240 }} /&gt;</code></pre>

  <h3>React Native &middot; @lujstn/cereal-logo-react-native</h3>
  <pre><code>import { CerealLogo } from '@lujstn/cereal-logo-react-native';

&lt;CerealLogo mode="split" style={{ width: 240, height: 80 }} /&gt;</code></pre>

  <h3>SwiftUI &middot; CerealLogo</h3>
  <pre><code>import CerealLogo

CerealLogo(.random)
    .frame(width: 240)</code></pre>

  <h3>Android Compose &middot; io.github.lujstn:cereal-logo</h3>
  <pre><code>import com.lujstn.cereal.logo.CerealLogo
import com.lujstn.cereal.logo.CerealLogoMode

CerealLogo(mode = CerealLogoMode.BLOOM)</code></pre>
  <p style="color:var(--muted);font-size:12.5px">Every package also takes <code>loop</code> and <code>speed</code>, and picks a fresh random take per mount when <code>mode</code> is <code>random</code>.</p>
</details>

<script>
const data = __DATA__;
const meta = __META__;
const order = __ORDER__;
const fps = data[order[0]].fr;

const stage = document.getElementById('stage');
const scrub = document.getElementById('scrub');
const timeEl = document.getElementById('time');
const captionEl = document.getElementById('caption');
const playBtn = document.getElementById('playBtn');
const loopBtn = document.getElementById('loopBtn');

let anim = null, current = null, speed = 1, looping = true, playing = true, scrubbing = false;

const tabs = document.getElementById('tabs');
order.forEach(key => {
  const b = document.createElement('button');
  b.id = 'tab-' + key;
  b.innerHTML = '<b>' + meta[key][0] + '</b><small>' + meta[key][1] + '</small>';
  b.onclick = () => select(key);
  tabs.appendChild(b);
});

function fmt(frame) { return (frame / fps).toFixed(2) + 's'; }

function select(key) {
  if (anim) anim.destroy();
  current = key;
  anim = lottie.loadAnimation({
    container: stage, renderer: 'svg', loop: looping, autoplay: true, animationData: data[key]
  });
  anim.setSpeed(speed);
  playing = true;
  anim.addEventListener('DOMLoaded', () => {
    scrub.max = Math.round(anim.totalFrames);
    timeEl.textContent = fmt(0) + ' / ' + fmt(anim.totalFrames);
  });
  anim.addEventListener('enterFrame', () => {
    if (scrubbing) return;
    scrub.value = anim.currentFrame;
    timeEl.textContent = fmt(anim.currentFrame) + ' / ' + fmt(anim.totalFrames);
  });
  order.forEach(k => document.getElementById('tab-' + k).classList.toggle('active', k === key));
  captionEl.innerHTML = '<b>' + meta[key][0] + '</b> &middot; ' + meta[key][1];
  updatePlayBtn();
}

function updatePlayBtn() { playBtn.textContent = playing ? 'Pause' : 'Play'; }
function togglePlay() { if (!anim) return; playing = !playing; playing ? anim.play() : anim.pause(); updatePlayBtn(); }
function replay() { if (!anim) return; anim.goToAndPlay(0, true); playing = true; updatePlayBtn(); }

function setSpeed(v) {
  speed = v; if (anim) anim.setSpeed(v);
  document.getElementById('sp05').classList.toggle('on', v === 0.5);
  document.getElementById('sp1').classList.toggle('on', v === 1);
}
function toggleLoop() {
  looping = !looping; if (anim) anim.loop = looping;
  loopBtn.textContent = 'Loop: ' + (looping ? 'on' : 'off');
  if (looping && anim) { anim.goToAndPlay(0, true); playing = true; updatePlayBtn(); }
}

scrub.addEventListener('input', () => {
  scrubbing = true; playing = false; updatePlayBtn();
  anim.goToAndStop(Number(scrub.value), true);
  timeEl.textContent = fmt(Number(scrub.value)) + ' / ' + fmt(anim.totalFrames);
});
scrub.addEventListener('change', () => { scrubbing = false; });

const bgs = ['', 'cream', 'dark'];
let bgIdx = 0;
function cycleBg() { bgIdx = (bgIdx + 1) % bgs.length; document.body.className = bgs[bgIdx]; }

document.addEventListener('keydown', e => {
  if (e.target.tagName === 'INPUT') return;
  const i = order.indexOf(current);
  if (e.key === 'ArrowRight') { select(order[(i + 1) % order.length]); e.preventDefault(); }
  else if (e.key === 'ArrowLeft') { select(order[(i - 1 + order.length) % order.length]); e.preventDefault(); }
  else if (e.key === ' ') { togglePlay(); e.preventDefault(); }
  else if (e.key.toLowerCase() === 'r') { replay(); }
});

select(order[0]);
</script>
</body>
</html>
"""


def build_haptics(mode):
    # One tap per letter pop; letters that fire together merge into one stronger tap.
    cfg = VARIANTS[mode]
    order, stagger = cfg["order"], cfg["stagger"]
    chord_at = {}
    for idx in range(len(order)):
        t0 = START + order[idx] * stagger
        chord_at[t0] = chord_at.get(t0, 0) + 1
    times = sorted(chord_at)
    events = []
    for j, t0 in enumerate(times):
        chord = chord_at[t0]
        frac = j / (len(times) - 1) if len(times) > 1 else 0.5
        intensity = min(1.0, 0.65 + 0.2 * (chord - 1) + (0.15 if j == len(times) - 1 else 0))
        sharpness = 0.4 + 0.5 * frac
        events.append({
            "t": round((t0 + HAPTIC_LAND) / FPS, 4),
            "intensity": round(intensity, 3),
            "sharpness": round(sharpness, 3),
        })
    duration = round((max(times) + HAPTIC_LAND + 6) / FPS, 4)
    return {"duration": duration, "events": events}


def asset_name(mode, sep="-"):
    return f"cereal-inflate-{mode}.json".replace("-", sep)


def haptics_targets():
    return [
        PACKAGES / "react" / "src" / "assets" / "cereal-haptics.json",
        PACKAGES / "react-native" / "src" / "assets" / "cereal-haptics.json",
        PACKAGES / "apple" / "Sources" / "CerealLogo" / "Resources" / "cereal-haptics.json",
        PACKAGES / "android" / "src" / "main" / "res" / "raw" / "cereal_haptics.json",
    ]


# Where each published take is copied. Android raw resources require
# lowercase-underscore filenames, hence the separator override.
def sync_targets(mode):
    return [
        (PACKAGES / "react" / "src" / "assets" / asset_name(mode), "-"),
        (PACKAGES / "react-native" / "src" / "assets" / asset_name(mode), "-"),
        (PACKAGES / "apple" / "Sources" / "CerealLogo" / "Resources" / asset_name(mode), "-"),
        (PACKAGES / "android" / "src" / "main" / "res" / "raw" / asset_name(mode, "_"), "_"),
    ]


def main():
    svg = SVG_FILE.read_text()
    ds = re.findall(r'd="([^"]+)"', svg)
    letters = []
    for name, d in zip(LETTER_NAMES, reversed(ds)):
        subpaths = transform(parse_path(d))
        letters.append({"name": name, "subpaths": subpaths, "bbox": bbox(subpaths)})

    docs = {key: build_inflate(letters, key) for key in VARIANT_ORDER}

    ASSETS.mkdir(exist_ok=True)
    for stale in ASSETS.glob("cereal-inflate-*.json"):
        if stale.stem[len("cereal-inflate-"):] not in VARIANT_ORDER:
            stale.unlink()
    for key, doc in docs.items():
        blob = json.dumps(doc, separators=(",", ":"))
        (ASSETS / f"cereal-inflate-{key}.json").write_text(blob)
    print(f"assets/ : {', '.join(VARIANT_ORDER)}")

    haptics = {m: build_haptics(m) for m in PUBLISHED_MODES}

    manifest = {
        "name": "cereal",
        "version": VERSION,
        "fps": FPS,
        "width": COMP_W,
        "height": COMP_H,
        "modes": PUBLISHED_MODES,
        "labels": {m: VARIANTS[m]["label"] for m in PUBLISHED_MODES},
        "descriptions": {m: VARIANTS[m]["desc"] for m in PUBLISHED_MODES},
        "files": {m: asset_name(m) for m in PUBLISHED_MODES},
        "haptics": haptics,
    }
    (ASSETS / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("assets/manifest.json")

    haptics_blob = json.dumps(haptics, separators=(",", ":"))
    (ASSETS / "cereal-haptics.json").write_text(haptics_blob)
    for dest in haptics_targets():
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(haptics_blob)
    print("assets/cereal-haptics.json (+ synced into packages)")

    for mode in PUBLISHED_MODES:
        blob = json.dumps(docs[mode], separators=(",", ":"))
        for dest, _sep in sync_targets(mode):
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(blob)
    synced = ", ".join(t[0].relative_to(ROOT).parts[1] for t in sync_targets(PUBLISHED_MODES[0]))
    print(f"synced {len(PUBLISHED_MODES)} takes into packages: {synced}")

    data_js = "{" + ",".join(f'"{k}":' + json.dumps(docs[k], separators=(",", ":")) for k in VARIANT_ORDER) + "}"
    meta_js = json.dumps({k: [VARIANTS[k]["label"], VARIANTS[k]["desc"]] for k in VARIANT_ORDER})
    order_js = json.dumps(VARIANT_ORDER)
    preview = (PREVIEW_TEMPLATE
               .replace("__DATA__", data_js)
               .replace("__META__", meta_js)
               .replace("__ORDER__", order_js))
    (HERE / "preview.html").write_text(preview)
    print("generator/preview.html")


if __name__ == "__main__":
    main()
