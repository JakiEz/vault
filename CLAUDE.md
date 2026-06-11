# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

This is an **Obsidian knowledge vault**, not a software codebase. There is no build, lint, or test step — "working in this repo" means reading, writing, and linking Markdown notes. Content is primarily personal engineering project documentation (FSAE electric-vehicle hardware/firmware and related software project plans). The owner is Jackie (Jedsarid Sangsuwan), CPE @ KMUTT.

## Navigation — read the index first

- **`INDEX.md`** is the Map of Content (MOC) hub. It summarizes every note in 1–2 lines. **Read it first** to locate the right note instead of globbing and reading every file — this is the intended token-saving workflow.
- For BMS/hardware questions, the answer is almost always in **`bms-project-context.md`** — check its `## TL;DR` section before reading the whole file.
- **Keep `INDEX.md` current:** when you create or substantially change a note, add/update its one-line entry there.

## Note conventions

- **Wikilinks** `[[note-name]]` connect notes (link by filename without extension). They are navigational only — they do *not* auto-include the linked note's content; you must `Read` a file to see it.
- Newer structured notes use **YAML frontmatter** (`type:`, `description:`, `updated:`/`created:`). The `description` field is meant to be a one-line summary readable without opening the full note — prefer adding/maintaining these so questions can be answered from summaries.
- Project notes follow a pattern worth matching: a `## TL;DR` near the top, then detail sections, then a "lessons learned" / backlog section. Mirror this structure and the existing terse, table-heavy style when adding notes.
- Use absolute Windows paths (e.g. `D:\ObsidianVault\note.md`); this is a `win32` environment with PowerShell as the default shell.

## Structure notes / gotchas

- Real content lives in the **vault root**. Everything under `.obsidian/` is Obsidian app config and plugin code (BRAT, claude-code-mcp) — do not edit it as part of content work.
- There is a **nested empty Obsidian starter vault at `vault/`** (its own `.obsidian/` + default Welcome content). It is *not* part of the knowledge base; ignore it and do not add notes there.
- `Untitled.canvas`, `Untitled.base`, and the dated daily notes are mostly empty stubs/scratch. Don't treat them as authoritative content.

## Vault rules (owner-specified)

- This is the owner's **personal** knowledge vault — be careful with edits.
- **New notes go in `Inbox/`** unless the user specifies a folder. (This folder does not exist yet; create it when first needed.)
- When updating `context.md` files, **append to a `## Log` section** — do not rewrite history.
- Date entries as **YYYY-MM-DD**.

## Editing etiquette

- The user authors these notes. When asked to clean up, **do not delete files the user created** without explicit confirmation — surface them for the user to remove instead.
- Before sending vault content to any external service, treat it as personal/unpublished and confirm first.
