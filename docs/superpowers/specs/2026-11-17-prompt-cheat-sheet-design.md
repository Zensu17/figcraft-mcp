# Design Document: Pre-built Prompt Cheat Sheet (Suggestion 2)

Date: 2026-11-17
Topic: Prompt Templates and Cheat Sheet (Suggestion 2)
Status: Proposed

## 1. Intent and Why
After installing the FigCraft MCP bridge, new users often wonder how to construct effective prompts to get high-quality visual layouts from AI or how to extract those designs back into code. Providing a comprehensive, categorized cheat sheet of copy-pasteable prompts solves the "blank canvas" problem and teaches users how to communicate with the AI agent effectively.

## 2. Goals, Non-Goals, and Anti-Goals
- Goals:
  - Create dedicated prompt cheat sheet files: `PROMPTS.md` (English) and `PROMPTS.id.md` (Bahasa Indonesia) adhering to Approach B.
  - Formulate a clear "Prompt Structure Anatomy" (Role + Target Layer + Layout/Dimensions + Color/Tokens).
  - Provide copy-pasteable prompt formulas across 6 core categories:
    1. Navigation and Headers
    2. Forms and Authentication
    3. Cards and Media Widgets
    4. Dashboards and Data Displays
    5. Modals and Dialog Overlays
    6. Design-to-Code Extraction (React Tailwind, Flutter, Design Tokens)
  - Reference `PROMPTS.md` and `PROMPTS.id.md` in both README files.
  - Zero emojis or decorative Unicode symbols.
- Non-Goals:
  - Adding code logic to the bridge or CLI.
- Anti-Goals:
  - Using emojis, icons, or vague prompt examples ("make a good button").
  - Having language disparity between the English and Indonesian cheat sheets.

## 3. Constraints
- Strict prohibition of emojis across both markdown files.
- All prompts must use realistic, aesthetic color tokens and layouts that FigCraft supports.
- Clear bilingual symmetry between `PROMPTS.md` and `PROMPTS.id.md`.

## 4. Approaches Considered
- Approach A: Inline section in `README.md`.
  - Rejected: Bloats the primary overview file and makes it difficult to bookmark.
- Approach B: Dedicated standalone files `PROMPTS.md` and `PROMPTS.id.md` (Chosen).
  - Clean, dedicated reference that users can keep open alongside their editor. Consistent with Approach B adopted in Saran 1.

## 5. Specification of Prompt Files

### File: `PROMPTS.md` (English) & `PROMPTS.id.md` (Bahasa Indonesia)
1. Header and cross-language navigation link.
2. Anatomy of an Effective FigCraft Prompt (Formula breakdown).
3. Category 1: Navigation and Menus.
4. Category 2: Authentication and Form Inputs.
5. Category 3: Cards and Content Blocks (E-commerce, Media Player, Pricing Table).
6. Category 4: Analytics and Metric Displays.
7. Category 5: Modals, Popovers, and Dialogs.
8. Category 6: Design-to-Code Conversion Prompts.
9. Pro-tips for Best Results (Layer naming, explicit frame constraints, token reusability).

## 6. Implementation Sequence
1. Create `PROMPTS.id.md` in Bahasa Indonesia with zero emojis.
2. Create `PROMPTS.md` in English with zero emojis.
3. Update `README.md` and `README.id.md` to link to the prompt cheat sheet.
4. Verify zero emojis across all newly created and updated files.
5. Commit locally to git branch `main`.
