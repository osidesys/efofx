# Story 1.1: Initialize White Label Widget Project

Status: backlog

## Story

As a developer,
I want a modern Vite + React + TypeScript widget project scaffolded with all architectural decisions implemented,
So that I can start building the embeddable chat widget on a solid foundation.

## Acceptance Criteria

**Given** the architecture specifies Vite + React 19 + TypeScript + Tailwind + Shadow DOM
**When** I run the widget initialization commands
**Then** the project structure is created at `apps/efofx-widget/` with:
- Vite configuration for single `embed.js` bundle output
- React 19 and TypeScript 5.x installed
- Tailwind CSS configured with PostCSS
- `vite-plugin-css-injected-by-js` for inline CSS
- Shadow DOM wrapper component stub
- Package.json with build scripts
- Basic folder structure: `src/components/`, `src/api/`, `src/hooks/`, `src/types/`

**And** running `npm run build` produces a single `dist/embed.js` file

**And** the widget can be embedded in a test HTML page with `<script src="dist/embed.js"></script>`

## Tasks / Subtasks

- [ ] Create Vite project at `apps/efofx-widget/` with React + TypeScript template
- [ ] Install and configure Tailwind CSS with PostCSS
- [ ] Install `vite-plugin-css-injected-by-js` plugin
- [ ] Configure Vite to output single `embed.js` bundle
- [ ] Create basic folder structure (components, api, hooks, types)
- [ ] Create Shadow DOM wrapper component stub
- [ ] Verify build produces single bundle file
- [ ] Test widget embedding in test HTML page

## Dev Notes

### Prerequisites

None (first story)

### Technical Notes

- Follow architecture doc: `docs/architecture.md` → Project Initialization → White Label Chat Widget
- Use exact commands from architecture (npm create vite, tailwind init)
- Verify output bundle size is reasonable (<600KB before optimization)
- Document widget initialization pattern in README.md

### References

- [Source: docs/epics.md#Story-1-1]
- [Source: docs/PRD.md] (for requirements context)

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

<!-- To be filled by dev agent -->

### Debug Log References

<!-- To be filled by dev agent during implementation -->

### Completion Notes List

<!-- To be filled by dev agent upon completion -->

### File List

<!-- NEW/MODIFIED/DELETED files will be listed here by dev agent -->
