# Hero Images for Neighborhood Pages

## Overview
Hero images appear at the top of each neighborhood micro-site page, showing bikes or scooters in context within that neighborhood.

## Image Specifications

- **Format**: JPG (recommended for photos) or PNG
- **Dimensions**: 1200px × 280px minimum (for desktop), 1200px × 200px minimum (for mobile)
- **Aspect ratio**: Wide format (4.3:1 or wider)
- **File size**: < 500KB (optimize for web)
- **Subject**: Bike or scooter in the neighborhood (street view, not branded)

## CSS Filter Applied

All hero images are processed with a CSS filter to genericize them (remove branding):

```css
filter: grayscale(75%) contrast(110%) brightness(115%) blur(1.5px);
opacity: 0.85;
```

This achieves:
1. **Desaturation (75%)** - Removes brand colors (Veo green, Spin orange, etc.)
2. **Contrast boost (110%)** - Keeps vehicle shape visible and readable
3. **Brightness increase (115%)** - Reduces intense detail/texture
4. **Slight blur (1.5px)** - Obscures stickers, logos, fine details
5. **Reduced opacity (85%)** - Softens the overall appearance

## Required Images

The following image files are needed in this directory:

| Neighborhood | Filename | Status |
|---|---|---|
| Bexley | `bexley.jpg` | ⏳ Needed |
| Downtown | `downtown.jpg` | ⏳ Needed |
| Dublin | `dublin.jpg` | ⏳ Needed |
| Grandview Heights | `grandview-heights.jpg` | ⏳ Needed |
| Harrison West | `harrison-west.jpg` | ⏳ Needed |
| Italian Village | `italian-village.jpg` | ⏳ Needed |
| Marble Cliff | `marble-cliff.jpg` | ⏳ Needed |
| Short North | `short-north.jpg` | ⏳ Needed |
| OSU | `osu.jpg` | ⏳ Needed |
| Upper Arlington | `upper-arlington.jpg` | ⏳ Needed |
| Victorian Village | `victorian-village.jpg` | ⏳ Needed |

## Implementation Notes

- Images are optional: if an image is missing or fails to load, the hero section silently hides via `onerror` handler
- The page layout remains responsive and functional without hero images
- All images use the same filter settings for visual consistency across neighborhoods

## Sourcing Tips

- Look for street-level photos of bike/scooter usage in each neighborhood
- Avoid branded vehicles (Veo/Spin logos must not be recognizable) — use the filter as reference
- Crop to wide aspect ratio; prioritize showing the neighborhood context over close-ups
- Sunset/golden hour lighting often works well with the desaturation filter
