# Ornevo Design System — Token Quick Reference

## Source of Truth
`~/projects/ornevo/ornevo-website/ornevo-design/DESIGN.md` — master design reference
`~/projects/ornevo/ornevo-website/wp-content/themes/ornevo/assets/src/styles/_tokens.css` — CSS tokens

## Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--ornevo-primary` | `#0D4F4A` | Brand anchor — hero bg, CTAs, headers |
| `--ornevo-secondary-01` | `#103229` | Deep forest — card bg on dark, hover states |
| `--ornevo-secondary-02` | `#3E8F87` | Medium teal — active states, highlights |
| `--ornevo-accent-blue` | `#4EC0DE` | Sky blue — focus rings, UI flash |
| `--ornevo-accent-pressed` | `#1C6C80` | Darker teal-cyan — pressed borders |
| `--ornevo-cream` | `#F2EDE3` | Warm cream — alternating section bg |
| `--ornevo-text-dark` | `#0F1720` | Charcoal — primary text on light |
| `--ornevo-neutral-01` | `#FFFFFF` | White — default surface |
| `--ornevo-teal-light` | `#E8F5F4` | Very light teal — subtle wash |
| `--ornevo-on-dark-accent` | `#82C4BF` | Light teal — small accent text on dark |
| `--ornevo-on-dark-accent-lg` | `#5EAAA4` | Light teal — large bold em-text on dark |
| `--ornevo-on-forest-accent` | `#7ABFBA` | Light teal — headings on forest bg |
| `--ornevo-muted-text` | `#4A6860` | Secondary text, captions |
| `--ornevo-text-on-dark` | `#F2EDE3` | Cream — subtitles on dark sections |
| `--ornevo-border-light` | `#D1D5DB` | Input borders |
| `--ornevo-bg-soft` | `#F3F8F7` | Card backgrounds |

## Section Color Schemes

| Section Type | Background | Text | Subtitles |
|-------------|------------|------|-----------|
| Dark teal | `--ornevo-primary` (#0D4F4A) | `--ornevo-neutral-01` (white) | `--ornevo-cream` (#F2EDE3) |
| Cream | `--ornevo-cream` (#F2EDE3) | `--ornevo-text-dark` (#0F1720) | `--ornevo-muted-text` |
| Near-black footer | `--ornevo-text-dark` (#0F1720) | white | `--ornevo-cream` |

## Typography

| Role | Font | Weight | Fallback |
|------|------|--------|----------|
| H1-H3 headings | Inter | 700 | Arial, sans-serif |
| Body | DM Sans | 400 | Calibri, sans-serif |
| Buttons/CTAs | DM Sans | 500 | Calibri, sans-serif |

### Type Scale
```css
--ornevo-fs-h1: clamp(2.5rem, 5vw, 5.5rem);
--ornevo-fs-h2: clamp(1.75rem, 3.5vw, 3rem);
--ornevo-fs-h3: clamp(1.25rem, 2.5vw, 2rem);
--ornevo-fs-body: clamp(0.9375rem, 1vw, 1.0625rem);
--ornevo-fs-button: 0.9375rem;
```

### Google Fonts Load
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">
```

## Spacing & Layout
```css
--ornevo-section-padding-y: clamp(3rem, 6vw, 5rem);
--ornevo-section-padding-x: clamp(1rem, 4vw, 2.5rem);
--ornevo-container-max: 1320px;
--ornevo-content-max: 880px;
```

## Border Radius
```css
--ornevo-radius-pill: 9999px;  /* buttons, CTAs */
--ornevo-radius-card: 48px;    /* cards */
--ornevo-radius-md: 16px;      /* tags */
```

## Buttons
- Dark sections: primary = white bg + teal text; secondary = white border + white text
- Light sections: primary = teal bg + white text; secondary = teal border + teal text
- All: pill (9999px), DM Sans 500, 0.9375rem, padding 0.875rem 1.75rem

## Cards on dark: bg #103229, 48px radius, white text
## Cards on light: bg white, 48px radius, border #D1D5DB, #0F1720 text

## Focus
- `2px solid #4EC0DE` (accent-blue) on all interactive elements

## Anti-patterns (from DESIGN.md)
- No generic SaaS gradients (purple/violet)
- No 3-column icon grids with colored circles
- No centered-everything layout
- No stock photography (real portraits only)
- No emoji — use text or inline SVG icons
- `system-ui` not used as display font
