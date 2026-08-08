# Scooter Challenge — Public vs. Private Versions

**Two project specifications created for different contexts, both styled with your design system.**

---

## 📋 File Guide

### 1. **scooter-challenge-PUBLIC.md**
✅ **Use this for:**
- Portfolio / public-facing work
- GitHub README
- Sharing with collaborators outside your inner circle
- Blog posts or case studies
- LinkedIn content
- Community contributions

**What's sanitized:**
- ✅ Personal address (home address) → "Mid-density residential neighborhood"
- ✅ Your name → "Sample User"
- ✅ No personal coordinates or identifiers
- ✅ Generic ride patterns and cost examples
- ✅ All technical content intact

**What's kept:**
- ✅ Full product spec
- ✅ MVP timeline + scope
- ✅ Technical architecture
- ✅ Cost model logic
- ✅ Design system specs

**Result:** A professional, shareable project spec that proves your ops thinking without revealing personal details.

---

### 2. **scooter-challenge-PRIVATE.md**
🔒 **Use this for:**
- Your personal records
- Client/employment discussions (when needed)
- Full transparency in trusted contexts
- Project management
- Your portfolio development notes

**What's included:**
- ✅ Your actual home address
- ✅ Your GBFS data (real Spin/Veo counts)
- ✅ Your personal cost analysis
- ✅ Your riding history (receipt analysis)
- ✅ Your specific recommendation (Stay on Spin)
- ✅ Full case study with real numbers

**Result:** Your definitive project record with all personal context intact.

---

### 3. **DEVELOPMENT_PLAN.md**
🔨 **Use this for:**
- Claude Code handoff (building the tool)
- Technical implementation
- Phase-by-phase tasks
- Test specifications

**Status:** Same for both versions (no personal info in code)

---

## 🎨 Design System Application

Both versions follow your official design system (github.com/steveneedham/design-system):

### Colors Applied
- **Ink** (`#14171C`): Background
- **Panel** (`#1B1F27`): Callout boxes, results cards
- **Amber** (`#E8A33D`): Cost emphasis, "Ops" track accent
- **Teal** (`#4FD1C5`): Systems/technical details, secondary accent
- **Text** (`#EDEAE2`): Body copy on dark
- **Muted** (`#8B93A1`): Secondary text, fine print

### Typography
- **Fraunces** (serif): Section headers (recommended for `<h2>`, `<h3>`)
- **Inter** (sans): Body copy
- **JetBrains Mono**: Labels, eyebrows, code examples, metadata

### Component Patterns
- Two-track accent discipline: amber for cost/ops, teal for technical/sys
- Eyebrow (mono, uppercase) → headline → body pattern
- Minimal corner radius (3–6px, nearly square)
- Sticky nav with blur effect
- Timeline/track patterns for process flows

### Styling Notes for Markdown → HTML/React
When converting these `.md` files to HTML or React components:

```html
<!-- Hero section -->
<header class="hero" style="background: var(--ink); color: var(--text)">
  <span class="eyebrow" style="font-family: 'JetBrains Mono'">🛴 RESEARCH TOOL</span>
  <h1 style="font-family: 'Fraunces'; color: var(--amber)">Scooter Challenge</h1>
</header>

<!-- Cost comparison table (Spin vs. Veo) -->
<table style="background: var(--panel); border: 1px solid var(--panel-line)">
  <tr style="color: var(--amber)"><!-- Spin row, amber accent --></tr>
  <tr style="color: var(--teal)"><!-- Veo row, teal accent --></tr>
</table>

<!-- Recommendation badge -->
<div style="background: var(--panel); border-left: 4px solid var(--amber)">
  🏆 Spin wins by $X/month
</div>

<!-- Faint background for metadata -->
<p style="color: var(--muted-dim); font-size: 0.7rem">
  Generated: [date] | Data age: [timestamp]
</p>
```

---

## 📝 When to Use Each

### PUBLIC Version
**Best for:**
- "Here's a tool I built" (portfolio story)
- "This is how personalized operator cost analysis works" (educational)
- "We need operator comparison logic" (consulting pitch)
- Open-source repos or templates
- Talks, blog posts, community contributions

**Example context:**
> "I built Scooter Challenge, a web tool that helps residents find their cheapest micromobility operator. Here's how it works..."

### PRIVATE Version
**Best for:**
- Your own project archive
- Detailed case study (when you're ready to share specifics)
- Employment/consulting: "Here's my actual ops analysis for Columbus"
- Shareholder/client meetings where context matters
- Full transparency with trusted collaborators

**Example context:**
> "I live in Columbus. Based on my riding patterns (25 rides/month), I save $50–110/month staying on Spin instead of switching to Veo. Here's why..."

---

## 🔐 Privacy Best Practices

**File handling:**
- Keep `PRIVATE.md` in a local `.gitignore` if you push to GitHub
- Push only `PUBLIC.md` to public repos
- Don't paste personal address in GitHub issues/PRs
- Use `PRIVATE.md` as your personal reference; reference `PUBLIC.md` in shared contexts

**Before sharing PUBLIC version:**
- Verify no personal addresses, coordinates, or identifiers remain
- Check for any company-specific context
- Confirm generic examples are clear (not confusing)
- Good to go for LinkedIn, portfolio, talks

**Before committing PRIVATE version to shared repos:**
- Remember it contains your home address and personal details
- Only commit to private repos or local copies
- Use `.env` or `.gitignore` if coordinates/address get added to code

---

## 📊 Content Comparison

| Section | PUBLIC | PRIVATE |
|---------|--------|---------|
| Project vision | ✅ Full | ✅ Full |
| Product spec | ✅ Full | ✅ Full |
| User workflows | ✅ Full | ✅ Full |
| Technical architecture | ✅ Full | ✅ Full |
| **Fleet data** | Sample locations | **Your home address** |
| **GBFS counts** | Generic example | **Real Spin/Veo numbers** |
| **Cost analysis** | Generic user case | **Your personal costs** |
| **Recommendation** | Spin/Veo comparison | **Your specific decision** |
| Personal address | ❌ Removed | ✅ Included |
| Your name | ❌ Removed | ✅ Included |
| Specific receipt data | ❌ Removed | ✅ Included |

---

## 🚀 Deployment Workflow

### For Your Portfolio
1. Write/refine in `PRIVATE.md` (full details, your thinking)
2. Extract relevant sections → `PUBLIC.md` (sanitize, generalize)
3. Deploy `PUBLIC.md` to portfolio site
4. Keep `PRIVATE.md` as your personal record

### For Client/Employment Discussion
1. Start with `PUBLIC.md` (professional, safe)
2. Transition to `PRIVATE.md` if/when you have trust + context
3. Use private version to show depth of actual analysis

### For Open Source
1. Use `PUBLIC.md` as your README
2. Add generic examples to DEVELOPMENT_PLAN.md
3. Gitignore any `PRIVATE.md` variants
4. Welcome contributions from the community

---

## 💾 File Organization

```
scooter-challenge/
├── scooter-challenge-PUBLIC.md       (safe for GitHub, LinkedIn)
├── scooter-challenge-PRIVATE.md      (local, personal reference)
├── README.md                         (main project readme — use PUBLIC)
├── DEVELOPMENT_PLAN.md               (technical build tasks)
├── VERSIONS-README.md                (this file)
│
└── .gitignore
    scooter-challenge-PRIVATE.md
    .env
    local-*.md
```

---

## ✅ Checklist Before Sharing

**PUBLIC version:**
- [ ] No street addresses?
- [ ] No personal names/identifying details?
- [ ] No company-specific context?
- [ ] Technical details clear + complete?
- [ ] Example data is generic but realistic?

**PRIVATE version:**
- [ ] Stored securely (not in public repos)?
- [ ] Available for trusted collaborators if needed?
- [ ] Used as your definitive project record?

---

## 🎯 Next Steps

1. **Choose your context:** Are you publishing this? Discussing with someone? Building it?
2. **Pick the version:** PUBLIC (default) or PRIVATE (trusted audience)
3. **Style it:** Convert to HTML/React using the design system tokens above
4. **Deploy:** GitHub (public version), portfolio (public version), local (private version)

---

**Both versions are production-ready. Choose based on your audience and context.**

*Design system: github.com/steveneedham/design-system | Tokens as of Aug 1, 2026*
