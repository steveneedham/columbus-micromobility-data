# Field Ledger Design System

Version 1.0 · July 2026

Field Ledger is the independent design system for **Columbus Micromobility Data**, the public-data-only observer project connecting Columbus 311 requests, published GBFS vehicle positions, and mobility-policy boundaries. It is derived from Steven Needham’s working principles—editorial restraint, evidence-first communication, systems thinking, accessibility, and care for public context—but it is not a visual copy of his personal portfolio.

Steven is the author. Field Ledger is the publication.

The living visual reference is [`design-system.html`](./design-system.html).

## Relationship to the parent practice

### Inherited

- Evidence before promotion
- Clear operational and civic context
- Generous whitespace and restrained composition
- Accessible, privacy-conscious presentation
- Documentary photography and specific language
- Durable artifacts that can be printed, framed, or cited

### Distinct

- **Newsreader**, **IBM Plex Sans**, and **IBM Plex Mono** replace the portfolio type trio.
- A daylight Columbus field palette replaces the portfolio’s dark-first amber/teal system.
- Color represents **signal and flow**, not “operations versus systems.”
- The visual language resembles a field ledger or working publication, not a personal homepage.
- Authorship appears in colophons and source notes rather than dominating headlines.

## Concept

**Observations become decisions. Decisions become interventions. Interventions leave evidence.**

Field Ledger presents public observations as a record that can be inspected. The system should feel like a hybrid of an urban field notebook, a source ledger, and a carefully edited civic-data journal.

The project is an informed outside observer. It is not affiliated with, endorsed by, or built from internal data belonging to the City of Columbus, Veo, Spin, or any current or former employer.

## Mark

The Field Ledger mark is a compact ledger page crossed by a signal line and a river-flow node. Its rectangular construction distinguishes it from Steven’s route-and-hub personal mark while preserving the shared preference for hairline geometry and meaningful nodes.

## Principles

1. **Editorial restraint** — use hierarchy, rhythm, language, and rules before decoration.
2. **Evidence boundaries** — distinguish observations, heuristics, inferences, and conclusions.
3. **Signal and flow** — terracotta marks decisions and exceptions; river blue marks evidence and movement.
4. **Public-source traceability** — show source, capture time, extraction state, and limitation.
5. **Durable form** — favor timeless typography, real photography, and simple composition.
6. **Independent observer** — communicate informed outside observation, never institutional authority.

## Color

| Token | Value | Use |
|---|---:|---|
| `--ledger-paper` | `#F3F0E8` | Primary page surface |
| `--source-sheet` | `#FBFAF6` | Raised evidence and source surface |
| `--ledger-panel` | `#E8E4DA` | Quiet section background |
| `--field-rule` | `#C8C2B5` | Hairline structure |
| `--ledger-ink` | `#202A2E` | Primary text |
| `--field-note` | `#5D696D` | Supporting text |
| `--signal-brick` | `#A94728` | Cautions, exceptions, interpretation |
| `--signal-brick-dim` | `#D49A83` | Non-text signal rails |
| `--river-ink` | `#236A73` | Sources, movement, traceable evidence |
| `--river-wash` | `#9CC6C9` | Non-text evidence rails and fills |
| `--night-map` | `#172126` | Map context and rare dark evidence panels |

Warm ledger paper is the default canvas. Night map is reserved for maps and occasional evidence contexts; it must not become a site-wide background. Terracotta and river blue are semantic accents, not decorative alternatives. Never use color alone to communicate status.

## Typography

- **Newsreader**: display headings and reflective editorial statements. Weights 400–500.
- **IBM Plex Sans**: body copy, explanations, navigation, and interface text.
- **IBM Plex Mono**: timestamps, sources, metrics, field status, tags, and structural labels.

Use sentence case for prose. Uppercase is limited to compact mono labels. Italic display type is reserved for one meaningful phrase, not general decoration.

## Layout and spacing

- Default page gutter: `clamp(1.5rem, 7vw, 6rem)`.
- Reading measure: 58–68 characters.
- Section interval: `5–7rem`.
- Component interval: `2–2.6rem`.
- Micro spacing: `0.35–0.9rem`.
- Use 1px hairline rules and whitespace instead of card walls.
- Tags may use `3px`.
- Source sheets may use `8–12px` radius when they behave like inserted documents.
- Do not introduce a dark hero merely to resemble the parent portfolio.

## Core components

### Field header

Project title, one-sentence purpose, and a mono metadata row for place, period, evidence state, or edition. Use a thin signal-brick rule.

### Public-source record

A timestamp or sequence number, concise title, direct observation, source note, and optional evidence link. River light indicates a traceable public source, not independent verification of every upstream claim.

### Observer finding

A direct observation followed by its classification and evidence boundary. Example: “Four or more published vehicles appear within roughly 20 metres” may be labeled as a proximity review signal, never a confirmed pile-up or violation.

### Timeline stop

No card. Use a node, title, one evidence-rich sentence, 1–4 tags, and an optional source link.

### Tags

Transparent background, 1px rule, 3px radius, mono uppercase label. Tags name methods, locations, or evidence classes; they do not make claims.

### Source note

IBM Plex Mono at a readable small size. Include source, capture time, sanitization state, and known limitations.

### Ledger insert

A warm-paper section for long-form analysis, diagrams, methods, or conclusions. Keep the same quiet hierarchy as the night-field shell.

## Voice

Write like a careful outside observer creating a record another person may need to inspect later.

- Prefer concrete verbs: observed, published, compared, documented, flagged, traced.
- State source and timeframe when relevant.
- Include defensible quantities.
- Hedge honestly: “roughly,” “representative,” or “source-limited.”
- Separate observation from inference.
- Do not infer intent, fault, compliance, or current conditions from a single snapshot.
- Avoid hype, generic innovation language, emoji, and exclamation points.

### Preferred terms

- 311 request
- published vehicle position
- proximity flag
- review signal
- policy-boundary intersection
- partial snapshot
- source-limited

Avoid “violation,” “pile-up,” “live fleet,” or “confirmed incident” unless the evidence directly establishes that description.

## Authorship

- Use “Columbus Micromobility Data” as the product name and Field Ledger as its design-system name.
- Credit “Steven Needham, Columbus, Ohio” in the colophon, methodology, and source notes.
- Do not place Steven’s name in every component or heading.
- The project can circulate and be cited without needing the personal portfolio around it.

## Data and map components

### Snapshot status

Show fetch timestamp, source-reported count, recovered count, extraction mode, and whether the display is complete or partial.

### Map layers

Use both color and geometry:

- 311 request: circle marker with priority label.
- Published GBFS vehicle: operator-neutral vehicle marker; operator may be named in text or filter controls.
- Proximity review signal: outlined ring with explicit “review signal” label.
- Policy boundary: patterned or dashed line with boundary type in the legend.

### Caveat panel

Place the evidence boundary near the title and repeat concise limitations at the point of interpretation. Do not hide the caveat solely in a footer or methodology page.

### Source link

Link to the public record or feed when available. Include capture time and explain when a source is dynamic or may have changed.

## Accessibility

- Maintain WCAG AA contrast: 4.5:1 for normal text and 3:1 for large text or essential graphical elements.
- Provide a visible 2px signal-brick focus ring with a 4px offset.
- Keep links identifiable without color alone.
- Aim for 44×44px interactive targets where practical.
- Support keyboard navigation, 200% zoom, and reflow.
- Honor `prefers-reduced-motion`.
- Write contextual alt text for documentary images.
- Pair all signal/flow colors with labels, shapes, or text.

## Motion

One reveal pattern is permitted: opacity with a 14px upward translation over 0.6 seconds. Avoid spring motion, bounce, parallax, or decorative loops. Documentary video is permitted only when muted beneath a legibility scrim.

## Imagery and diagrams

- Use real on-location documentary photography.
- Favor available light, field context, and imperfect evidence over staged polish.
- Avoid stock imagery and abstract AI illustration.
- Diagrams use rules, nodes, labels, and measured spacing.
- Icons use hairline strokes and simple geometry.
- Public mobility material remains operator-neutral unless attribution is required.

## Charts and graphics

Every chart or graphic should answer one clear question without requiring specialist interpretation.

### Default chart forms

- Horizontal bar chart for comparing a small number of categories.
- Dot plot when precise comparison matters more than area.
- Simple timeline for sequence or change over time.
- Small multiple only when the same measure must be compared across places or periods.
- Directly labeled map for geographic evidence.

Avoid 3D charts, donut charts with many segments, gauges, decorative dashboards, dual axes, unexplained color scales, and charts that exist only to fill space.

### Chart construction

- Use no more categories than a reader can scan comfortably.
- Label values directly when possible instead of requiring a legend.
- Begin quantitative bar axes at zero.
- Use ledger ink for context, river ink for traceable evidence, and signal brick for one caution or exception.
- Pair color with text, line style, or marker shape.
- Put the source, capture time, extraction status, and limitation immediately beneath the chart.
- State when values are illustrative, partial, approximate, or derived by a heuristic.
- Write a plain-language takeaway adjacent to the chart; do not make the reader reverse-engineer its purpose.

### Maps

- Default to only the layers required for the current question.
- Use different marker shapes as well as colors.
- Keep the legend close to the map.
- Distinguish published positions, public requests, policy geometry, and inferred proximity flags.
- Do not imply a current live condition when displaying a timestamped snapshot.

### Photography and imagery

- Use real Columbus street, curb, parking, mobility, and public-realm documentation.
- Captions answer: what is shown, where, when, and why it matters.
- Preserve documentary context; avoid dramatic color grading and shallow-focus lifestyle treatment.
- Never use stock scooter imagery as a substitute for evidence.
- Crop to clarify the subject without removing context needed to interpret it.
- Provide contextual alt text and remove private identifiers.

## Production checklist

- [ ] The artifact uses Field Ledger identity rather than copying the personal portfolio.
- [ ] Observations, inferences, and decisions are distinguishable.
- [ ] Evidence and claims have been checked.
- [ ] Sources and limitations are visible.
- [ ] Essential text meets contrast requirements.
- [ ] Keyboard focus is visible.
- [ ] Layout survives narrow screens and 200% zoom.
- [ ] Reduced-motion behavior is present.
- [ ] Images have useful alt text.
- [ ] Private or operationally sensitive data has been removed.
- [ ] Public-data-only and non-affiliation language is visible.
- [ ] Partial snapshots state both recovered and source-reported counts.
- [ ] Map colors are paired with shapes and text labels.
- [ ] Every chart answers one clear question.
- [ ] Values are directly labeled where practical.
- [ ] Source, timestamp, extraction state, and limitations sit beside the graphic.
- [ ] Imagery is documentary, contextual, and captioned.
- [ ] The artifact reads as a field publication, not marketing collateral.
