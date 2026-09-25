---
name: design-system-builder
description: Establish and maintain a consistent visual/component design system for a product's UI — brand brief, an approved DESIGN.md, and real component implementation — so Claude Code edits and builds UI that stays consistent instead of drifting session to session. Use when the user asks for a design system, a DESIGN.md, brand-consistent UI work, or explicitly invokes this skill before building/reviewing app UI.
---

# Design System Builder

A repeatable, project-agnostic workflow for keeping one product's UI visually and
structurally consistent over time: a brand brief captures positioning and tone, an
approved `DESIGN.md` turns that into concrete visual/interaction rules, and real
components implement those rules. Claude Code then consults only the relevant documents
before touching UI, instead of re-deriving style decisions from scratch each session (or
worse, from whatever a component library defaults to).

This is a different job from the `cinematic-site-builder` skill: that one builds a single
scroll-driven marketing hero; this one governs the ongoing UI of an app — dashboards,
forms, settings, the everyday screens. A product can use both: a `DESIGN.md` for its app,
a cinematic hero skill for its landing page.

## Ground rules

- **Never copy another brand's `DESIGN.md` wholesale.** Reference material (curated
  collections, another product's design system) is inspiration for structure and
  technique, never a file to paste in and rename. Write an original `DESIGN.md` for this
  product from its own brand brief.
- **Consult narrowly.** Read the specific brief/`DESIGN.md`/notes files named for this
  task, not an entire vault or repository. If research notes live in Obsidian or similar,
  ask which specific notes are relevant rather than reading the whole vault.
- **Check before creating.** Before adding a new component, look for an existing one in
  the project's component directory that already does the job (or almost does).
  Duplicated near-identical components are a sign the audit step was skipped.
- **Propose, then wait.** For any non-trivial design decision, propose a short list of
  options and wait for approval before implementing broadly — don't silently pick one and
  roll it out across the app.

## Workflow

1. **Brand brief** — `references/brand-brief.md`. Positioning, tone, audience, identity.
   Skip this only if one already exists for the product; read it, don't re-derive it.
2. **`DESIGN.md` authoring** — `references/design-md-template.md`. Turn the brief into
   concrete rules: color, typography, spacing, components, composition, responsive
   behavior, explicit do/don't guidance. Reference an aesthetic family (see
   `references/aesthetic-families.md`) rather than inventing an unnamed one from scratch.
3. **Component audit** — `references/component-audit.md`. Before building new UI, check
   what already exists in the project's component library (e.g. `components/ui` if the
   project uses shadcn/ui) and reuse or extend it before adding something new.
4. **Implementation** — build/edit components against the approved `DESIGN.md`, citing
   which rule each non-obvious choice follows. Flag anywhere the brief doesn't cover a
   case you hit, rather than silently improvising a new rule.
5. **Anti-slop pass** — `references/anti-slop-for-uis.md`. Before calling UI work done,
   check it against the catalogue of generic component-library defaults and confirm each
   one was a deliberate choice, not an unexamined default.
6. **Consultation discipline going forward** — `references/consultation-discipline.md`.
   Once a brief and `DESIGN.md` exist, every future UI task should name exactly which
   files to read, not "check the design system" as an open-ended instruction.

## Where things live in a project

A reasonable default layout (adjust to the project's actual conventions):

```
docs/brand/brief.md       -> brand brief (positioning, tone, identity)
docs/design/DESIGN.md     -> approved visual/interaction rules
components/ui/            -> real component implementation (e.g. shadcn/ui)
```

If the project keeps research in an Obsidian vault or similar, that vault is *upstream*
of the brand brief — hypotheses and notes, not something Claude Code reads wholesale on
every task. Name the specific notes that matter for the task at hand.

## Resources inbox

External design-system collections, competitor teardown, or new tools someone shares
while using this skill get logged in `resources.md` with a note on whether/how they feed
back into `references/aesthetic-families.md` or the `DESIGN.md` template — so a
discovery doesn't just disappear into chat history.
