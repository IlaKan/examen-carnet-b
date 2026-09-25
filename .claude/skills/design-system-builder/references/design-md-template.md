# DESIGN.md Template

A `DESIGN.md` is the approved, concrete translation of the brand brief into rules Claude
Code (or anyone) can follow without re-deriving taste each time. Write an original one per
product — a curated collection of other products' `DESIGN.md` files is reference material
for *structure and technique*, never a file to paste in and rename. Copying another
brand's file doesn't create this product's identity.

## Suggested structure

```markdown
# <Product> Design System

## Aesthetic family
Name one family (see aesthetic-families.md) and one sentence on why it fits the brief.

## Color
- Primary / accent / neutral scale, with hex values and intended use for each
- Explicit contrast requirements (e.g. minimum ratio for body text)
- What NOT to use as an accent, if the brief rules something out

## Typography
- Display / heading / body typefaces (one or two families max)
- Scale (sizes actually used, not an open-ended type scale)
- Weight usage rules (e.g. "never use a weight below 500 for body text")

## Spacing & layout
- Base spacing unit and the scale built from it
- Grid/container widths
- Rules for when to break the scale (ideally: never, without a stated reason)

## Components
- Per-component rules that matter (button states, card composition, form field style)
- Explicit reuse note: link to where these are actually implemented (e.g. `components/ui`)

## Composition
- How hierarchy is established (size, weight, color, spacing — not all four at once by default)
- Default page/section anatomy if there's a recurring pattern

## Responsive rules
- Breakpoints and what changes at each
- What's allowed to change (spacing, stacking) vs. what must stay constant (brand color, type family)

## Do / Don't
- A short, concrete list — "Do: use the primary accent for exactly one action per screen."
  "Don't: apply a drop shadow to more than one elevation level at a time."
```

## Keep it enforceable

Every rule should be specific enough that someone could look at a screen and say whether
it follows the rule or not. "Feel premium" is not enforceable; "use the primary accent for
exactly one action per screen" is. If a rule can't be checked against an actual screen,
rewrite it or cut it.
