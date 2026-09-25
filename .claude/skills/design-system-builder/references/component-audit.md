# Component Audit

Before adding a new component, check what already exists. A design system erodes fastest
through near-duplicate components that each drifted slightly from the shared rule.

## Before creating anything new

1. Search the project's component directory (e.g. `components/ui` for a shadcn/ui-based
   project) for something that already does this job, or almost does.
2. If something close exists, extend or compose it rather than starting fresh — a new
   variant/prop is usually cheaper than a parallel component, and keeps one source of
   truth for the underlying markup and states.
3. If nothing close exists, build it against the current `DESIGN.md`, and add it to the
   shared component directory rather than inlining one-off styled markup in a page/feature
   file. A component used more than once belongs in the shared library; one truly used
   once can stay local, but say so explicitly rather than defaulting to local out of
   habit.

## Signs the audit step was skipped

- Two components that render almost the same thing with slightly different spacing or
  color, added in different sessions.
- A page with inline styles that duplicate an existing component's states (hover, focus,
  disabled) instead of reusing it.
- A new component that doesn't reference `DESIGN.md` at all — no stated reason its colors,
  spacing, or type differ from the system.

## When using shadcn/ui specifically

Treat the installed primitives as a base layer, not the final visual output — shadcn/ui's
own defaults (spacing, radius, shadow) are a starting point that `DESIGN.md` should
override deliberately where the brief calls for something different. An unmodified
default is fine when the brief has no opinion; it's a problem when the brief clearly wants
something else and the default was never actually revisited.
