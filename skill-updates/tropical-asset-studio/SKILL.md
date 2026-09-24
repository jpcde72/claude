---
name: tropical-asset-studio
description: >
  Produce assets in jean-paul's Tropical Sunrise brand style across any media
  channel — slides, social cards, LinkedIn banners, email templates, web heroes,
  one-pagers, infographics, video title cards, charts and diagrams. Use whenever
  the user asks for a "tropical" asset, mentions "tropical sunrise", "sunrise
  delta", asks for jean-paul branded content in the premium/corporate/default
  style, or requests a chart, diagram, deck, post, banner or explainer "in the
  tropical look". Tropical is the hero/default sub-brand of the sunrise system.
---

# Tropical Asset Studio

You are producing assets in the **Tropical Sunrise** identity — the hero sub-brand
of jean-paul's sunrise-delta brand system. Mood: **radiant, fluid, high-energy.**
Dark-first, always. Energy comes from colour and flow, never clutter.

## Design tokens

```css
--violet:  #4B2E83;  /* 23°N — anchor, outermost */
--purple:  #7B3FAB;  /* 19°N — secondary deep accent */
--magenta: #C026A0;  /* 14°N — high-energy accent */
--coral:   #F05A28;  /* 10°N — primary warm accent, CTA */
--pink:    #F78DA7;  /*  5°N — secondary warm, softness */
--solar:   #FFCC00;  /*  0°  — brightest highlight, key stats */
--bg:      #0A0A0A;  /* background, dark-first always */
--panel:   #141414;  --line: #262626;
--ink:     #FFFFFF;  --ink2: #B0B0B0;
```

**The palette is a latitude sequence. Always use it in order violet → solar,
never shuffled.** One solar-yellow element per view — it marks the takeaway.

## Typography

| Role | Face | Rules |
|---|---|---|
| Display / titles / wordmark | **Fraunces** (Google) | 400 weight, italic for radiant moments; hero 64–96px; one gradient word (magenta→coral→solar clipped text) per headline max |
| Headings / body / stats | **Outfit** (Google) | body 300 @16–18px, headings 500, big stats 600 @44–80px |
| Kickers / labels / captions | **Space Mono** (Google) | always uppercase, 0.25–0.35em tracking, 10–13px |

Email/PPT fallbacks: Georgia italic / Helvetica / Courier New.
Wordmark: `jean-paul` — Fraunces italic, always lowercase.

## The mark and accent bar

- The mark is six layered sunrise-delta curves (real solar maths, latitudes
  23.44° → 0.8°N mapped violet → solar). Ready-made SVGs in `assets/`;
  regenerate variants with `scripts/generate_mark.py` (needs only stdlib).
- Always on dark. Keep line order intact. Let it sweep large and airy.
- **Latitude accent bar**: 6 equal segments (formal) or continuous gradient
  sweep (expressive), 4–8px tall, full width, top and/or bottom of every asset.

## Ideograms

10 SVGs in `assets/ideograms/` (horizon-sun, delta-curve, strategy-compass,
audience-horizons, signal-arcs, growth-sunrise, network-latitudes, idea-radiant,
flow-channels, focus-zenith). Style if drawing new ones: 64×64 viewBox, 3.5px
white strokes, rounded caps/joins, exactly one palette-colour accent, and a
sunrise-delta curve somewhere in the glyph. Use at 24–64px on dark panels.

## Diagram & chart language

- Dark canvas (#0A0A0A / #141414 panels), hairline #262626 grid, no borders
- Series colours in latitude order; prefer smooth curves/areas over columns
- Hero series gets a soft glow (blurred duplicate underneath)
- Solar yellow = the single takeaway element; coral = attention/CTA
- Space Mono axis labels, 10–11px caps
- Never: pie charts, 3D, red/green semantics, white chart grounds, >1 glow

## Channel recipes

- **Slides (16:9)**: #0A0A0A throughout. Title = full-bleed mark + white
  Fraunces italic. Stat slides = one huge Outfit-600 number, mono label in
  solar/coral. Dividers = gradient bar + heading. Airy — one idea per slide.
- **LinkedIn**: banner 1584×396 (template in assets); posts 1200×1500 dark
  cards (mono kicker → Fraunces hook → sweep bar at base); carousel: title
  card / stat cards / signature+coral CTA pill.
- **Email**: dark header + signature, white body (coral headings, #333 text)
  for deliverability, segmented bar dividers, dark footer.
- **Web**: dark hero, animated mark (curves draw left→right ~1.2s ease), cards
  on #141414 radius 14px, coral pill buttons, ghost = 1px magenta border.
- **Documents**: premium = dark pages; light/print variant = white ground,
  coral Fraunces headings, near-black Outfit body, segmented bar at top, mark
  only inside a dark panel (never recoloured on white).
- **Video**: mark draws outer-to-inner (violet first), titles rise 20px + fade,
  0.8–1.5s eased dawn-like motion, end frame = signature on black.

## Voice

Warm, radiant, confident. "We" in proposals, "I" in thought leadership. Active
voice. No jargon for jargon's sake, no hedging, no exclamation marks — the
colour provides the energy.

## Workflow

1. Identify the channel and pick the recipe above.
2. Pull ready-made assets from `assets/` rather than redrawing; regenerate
   sizes with the scripts when a new aspect ratio is needed.
3. Apply tokens + typography exactly; load fonts from Google Fonts.
4. Every asset carries the signature: sweep/segment bar + `jean-paul`.
5. Name files `jp-tropical-[asset-type]-[descriptor].[ext]`.
6. Before delivering, verify: palette in latitude order, dark-first, exactly
   one solar takeaway, airy spacing.
