# Presearch Office Brand Kit

This directory contains the canonical brand tokens and assets for Presearch Office Edition.

## Files

- `tokens.json` - Canonical source of truth for all brand tokens
- `tokens.css` - CSS custom properties (auto-generated)
- `tokens.scss` - SCSS variables and mixins (auto-generated)
- `assets/` - Logo variants, splash screens, and start center visuals

## Colors

### Primary
- **Presearch Blue**: `#2D8EFF`

### Text
- **Primary**: `#000000` (headlines, important text)
- **Secondary**: `#494949` (body text, descriptions)

### Backgrounds
- **Tint**: `#EAF3FF` (subtle blue tint for highlights)
- **Soft**: `#FAFBFC` (off-white for cards/panels)
- **Base**: `#FFFFFF` (pure white for main backgrounds)

### Blue Scale
Use for creating depth and hierarchy:

**Dark (for dark mode or strong accents):**
`#287FE5` → `#2471CC` → `#1F63B2` → `#1B5599` → `#16477F` → `#123866` → `#0D2A4C` → `#091C33` → `#040E19` → `#000000`

**Light (for light mode backgrounds and subtle elements):**
`#2D8EFF` → `#4299FF` → `#56A4FF` → `#6CAFFF` → `#81BBFF` → `#96C6FF` → `#ABD1FF` → `#C0DDFF` → `#D5E8FF` → `#EAF3FF` → `#FFFFFF`

## Typography

**Preferred**: Proxima Nova
**Fallback Stack**: Inter, Noto Sans, Arial, sans-serif

Note: Proxima Nova requires a license. Always include fallbacks.

## Usage

### CSS
```html
<link rel="stylesheet" href="tokens.css">

<button style="background: var(--pre-primary); color: var(--pre-bg-base);">
  Search with Presearch
</button>
```

### SCSS
```scss
@import 'tokens';

.button {
  @include presearch-button;
}

.card {
  @include presearch-card;
}

.accent-text {
  color: blue-light(1); // #2D8EFF
}
```

## Regenerating Tokens

After modifying `tokens.json`, run:
```bash
node tools/generate-tokens.js
```

## Do's and Don'ts

### Do
- Use `#2D8EFF` exactly for primary brand color
- Use `#494949` for body text (better readability than pure black)
- Include all fallback fonts when using Proxima Nova
- Test dark mode and high contrast variants

### Don't
- Modify generated CSS/SCSS files directly
- Use colors outside the defined scales
- Use pure black `#000000` for body text (reserve for headlines)
- Forget to include the font fallback stack

## Voice & Tone

Presearch embodies: **Community**, **Transparency**, **Privacy**

Keep messaging aligned with these values.
