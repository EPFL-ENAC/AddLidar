## Design Philosophy

Build interfaces that feel calm, professional, and invisible. The UI should get out of the way and let content breathe. Prioritize clarity over decoration.

## Core Principles

- **Minimal chrome**: Reduce visual noise. No unnecessary borders, shadows, or colors
- **Generous spacing**: Use consistent padding (8px, 12px, 16px scale). When in doubt, add more whitespace
- **Subtle hierarchy**: Use font-weight and size (not color) for hierarchy. Reserve color for interactive elements
- **Quiet by default, expressive on interaction**: Elements reveal themselves on hover/focus

## Spacing & Layout

- Base unit: 4px (use multiples: 8, 12, 16, 24, 32)
- Sidebar width: 240-280px, collapsible to 48-64px (icon-only)
- Panel padding: 12-16px
- Gap between sections: 16-24px
- Border-radius: 6-8px for containers, 4px for buttons/inputs

## Colors

- Backgrounds: near-white (#fafafa, #f5f5f5) or near-black (#1a1a1a, #0f0f0f)
- Borders: very subtle (rgba(0,0,0,0.06) light / rgba(255,255,255,0.08) dark)
- Text: not pure black/white — use #1a1a1a / #e5e5e5
- Accent: single muted color, used sparingly (buttons, active states)
- Avoid: bright colors, heavy shadows, gradients (except subtle glass effects)

## Typography

- Font: system font stack (-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif)
- Sizes: 11-12px secondary, 13-14px body, 16-18px headings
- Weights: 400 regular, 500 medium (for emphasis), 600 semibold (headings only)
- Line-height: 1.4-1.5 for body text

## Interactive Elements

- Hover states: subtle background shift (opacity 0.04-0.08), not color change
- Active states: slightly darker background + optional left border accent
- Transitions: 150-200ms ease-out for all state changes
- Focus: visible but subtle ring (2px offset, muted color)
- Buttons: ghost/outline by default, filled only for primary actions

## Sidebar & Panels (specific)

- Section headers: uppercase, 11px, font-weight 500, muted color, letter-spacing 0.5px
- List items: full-width clickable area, 32-36px height, 8px padding
- Icons: 16-18px, stroke width 1.5-2px, muted until hovered
- Collapsible sections: subtle chevron, smooth height animation
- Scrollbar: thin (6-8px), only visible on hover

## What to Avoid

- Drop shadows heavier than 0 1px 3px rgba(0,0,0,0.08)
- Borders thicker than 1px
- Pure black (#000) or pure white (#fff)
- Uppercase text except for small labels
- Multiple accent colors
- Animations longer than 300ms
- Nested scroll areas when avoidable
