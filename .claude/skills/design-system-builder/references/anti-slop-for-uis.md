# Anti-Slop for UIs

A catalogue of generic defaults that generative tools and default component libraries
converge on when a brief doesn't push against them. The fix is never "make it more
unique" in the abstract — it's naming which specific default crept in and replacing it
with something the `DESIGN.md` actually supports.

## Common defaults worth checking for

- **A stock teal or violet accent on white or near-black** — the single most common
  AI-generated default. Check the accent actually comes from `DESIGN.md`'s color section,
  not from whatever the model or library defaulted to.
- **Excessive container nesting** — cards inside cards inside padded sections, adding
  visual weight without adding hierarchy. Check whether each nested container earns its
  border/shadow/background, or whether spacing alone would do the job.
- **A serif display headline applied by default whenever "premium" or "editorial" comes
  up** — a real choice, not a reflex. If the brief's aesthetic family isn't editorial or
  literary, question the serif default.
- **Uniform rounded corners and drop shadows on every surface** — treat radius and
  elevation as a small, deliberate scale (e.g. 2–3 values used consistently), not a
  single default applied everywhere because the component library ships that way.
- **Generic centered-hero-with-gradient-and-floating-mockup composition** — worth
  questioning any time it appears without a specific reason tied to this product's actual
  content.
- **Placeholder icon soup** — a row of generic outline icons used to fill space rather
  than to communicate something specific. If an icon doesn't help someone find or
  understand something faster, it's decoration, and decoration should be a deliberate
  choice, not a filler.

## Where to check for this

Run this check right before calling UI work done, against the actual rendered screen —
not against the code. A default can look fine in isolation and still be the reason a
screen feels generic once several of these stack together.
