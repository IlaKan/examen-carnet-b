# Consultation Discipline

Once a brand brief and `DESIGN.md` exist, the point is to consult them cheaply and
precisely — not to re-read everything on every task.

## Name the files, not the vault

Instead of an open-ended instruction like "check the design system," name exactly what
should be read for this task:

> Read only `docs/brand/brief.md` and `docs/design/DESIGN.md`. Consult the Obsidian notes
> I name, not the whole vault. Before creating components, check what already exists in
> `components/ui`. Propose three design decisions and wait for my approval.

This does three things: bounds the token cost, keeps the decision auditable (it's clear
which document justified which choice), and forces a review step before broad changes
land.

## Defaults for how much to read

| Task | Read |
|---|---|
| Small UI tweak inside an existing pattern | `DESIGN.md` section relevant to that component |
| New component | `DESIGN.md` in full, plus a scan of `components/ui` for near-duplicates |
| Anything touching brand tone/positioning | `docs/brand/brief.md` |
| Research-backed decision | The specific named notes, never the entire vault/repo |

## Propose, don't roll out silently

For anything beyond a small, contained fix: state the options, pick a recommendation, and
wait for approval before applying it across multiple screens. A design decision made once
and quietly propagated everywhere is much more expensive to unwind than one caught before
it spreads.
