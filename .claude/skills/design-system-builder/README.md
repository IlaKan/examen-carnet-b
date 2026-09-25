# design-system-toolkit

A reusable Claude Code skill for establishing and maintaining a product's UI design
system: brand brief → approved `DESIGN.md` → real component implementation, consulted
narrowly so Claude Code stays consistent instead of re-deriving taste every session.

## What's in here

- **`SKILL.md`** — the skill itself: ground rules and the workflow (brand brief →
  `DESIGN.md` → component audit → implementation → anti-slop pass → ongoing narrow
  consultation).
- **`references/`**
  - `brand-brief.md` — what to capture before writing any visual rules.
  - `design-md-template.md` — the structure for an original, enforceable `DESIGN.md`.
  - `aesthetic-families.md` — a naming vocabulary for the system's overall character.
  - `component-audit.md` — checking for existing components before adding new ones,
    including shadcn/ui-specific notes.
  - `anti-slop-for-uis.md` — a catalogue of generic component-library/AI defaults to
    check against before calling UI work done.
  - `consultation-discipline.md` — reading only the files a task actually needs, instead
    of a whole vault or repo, plus a propose-then-approve habit for bigger decisions.
- **`resources.md`** — inbox of external design-system collections/tools evaluated
  against this skill.

## Using it in another project

Copy this repository's contents into that project's
`.claude/skills/design-system-builder/` directory:

```
git clone https://github.com/IlaKan/design-system-toolkit.git /tmp/dst
cp -r /tmp/dst/{SKILL.md,references,resources.md} <your-project>/.claude/skills/design-system-builder/
```

## Scope

This skill governs a product's ongoing UI — components, screens, the design system.
It's a different, complementary job to the sibling `creative-director-toolkit` skill,
which builds a single cinematic scroll-driven marketing hero. A product can use both.
