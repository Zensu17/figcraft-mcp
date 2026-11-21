---
name: figcraft-design-to-code
description: Converts FigCraft canvas designs and selected frames into production-ready frontend code (React + Tailwind CSS, Vue 3, Flutter, or HTML/CSS) with typed props mapping. Use when the user asks to "convert FigCraft to code", "export frame as React", "generate Flutter from FigCraft", or "turn this design into code".
---

# FigCraft Design-to-Code Skill

You are an expert Frontend Engineer and Design Systems specialist. Your task is to inspect UI elements on the FigCraft canvas and translate them with pixel-perfect fidelity into clean, typed, production-grade frontend code.

## 1. Inspection & Generation Workflow

When the user asks to convert a frame or component from FigCraft:

1. **Locate the Node**:
   - Read resource `figcraft://canvas/semantic` (or call `inspect_document` / `figcraft_extract_semantic_ast`) to discover layer IDs and hierarchy.
2. **Generate Baseline Code via MCP Tool or CLI**:
   - **MCP Tool (Recommended)**: Call `figcraft_generate_code` with `node_id`, `framework` (`react-tailwind` | `vue` | `flutter` | `html-css`), optional `component_name`, and `include_props: true`.
   - **CLI Helper**: `python codegen_helper.py --node <ID> --framework react-tailwind`
   - **Semantic AST Only**: Read `figcraft://node/{id}/semantic` or call `figcraft_extract_semantic_ast(node_id=<ID>)`.
3. **Inspect Typed Props & Tokens**:
   - Colors, spacing, corner radii, and font sizes are automatically reverse-mapped against `tokens.json` (`#1E293B` -> `slate-800`, `20px` -> `p-5`, `16px` -> `rounded-2xl`), falling back to arbitrary values when custom tokens are used.
   - Named text layers, explicit `componentPropertyDefinitions` (`TEXT`, `BOOLEAN`, `VARIANT`, `SLOT`), and empty slot frames are automatically exposed as typed component props (`Props` interface in TS/Vue or `final` fields in Flutter).
4. **Refine & Visually Verify**:
   - Call `screenshot` on `node_id` to visually cross-check spacing, alignment, contrast, and typography against the generated component.

---

## 2. Token Mapping Reference

### A. React + Tailwind CSS (Default)

| FigCraft Token | Tailwind Utility Class | Example |
| :--- | :--- | :--- |
| `direction: "col"` | `flex flex-col` | `<div className="flex flex-col ...">` |
| `direction: "row"` | `flex flex-row` | `<div className="flex flex-row ...">` |
| `p: 20` / `px: 24, py: 12` | `p-5` / `px-6 py-3` | Uses `tokens.json` scale or `p-[18px]` |
| `gap: 12` / `gap: 16` | `gap-3` / `gap-4` | `gap-4` |
| `justify: "between"` | `justify-between` | `justify-between` |
| `items: "center"` | `items-center` | `items-center` |
| `rounded: 16` / `9999` | `rounded-2xl` / `rounded-full` | `rounded-2xl` |
| `bg: "#0F172A"` | `bg-slate-900` | Reverse-mapped from `tokens.json` |
| `borderColor` + `borderWidth` | `border border-slate-700` | `border-[2px]` when width > 1 |
| `fontStyle: "Bold"` | `font-bold` | Mapped from FigCraft `fontStyle` |
| `role: "button"` / `"nav"` | `<button type="button">` / `<nav>` | Semantic HTML tag selection |

### B. Vue 3 SFC (`framework: "vue"`)
- Emits `<script setup lang="ts">` with `interface Props` and `withDefaults(defineProps<Props>(), ...)`.
- Emits `<template>` using Tailwind classes and `<slot name="..." />` for slot containers.

### C. Flutter (`framework: "flutter"`)
- Emits `StatelessWidget` with `const` constructor, typed `final` fields, `Container` + `BoxDecoration` (`Color(0xFF...)`, `BorderRadius.circular(...)`, `Border.all(...)`), `Column` / `Row`, and `SizedBox` gaps.

### D. Semantic HTML + CSS (`framework: "html-css"`)
- Emits scoped BEM-style `.component__layer` CSS rules inside `<style>` with semantic HTML5 markup.

---

## 3. Best Practices for Generated Code
- **Never hardcode arbitrary pixel coordinates** (`top: 120px, left: 340px`). Always translate FigCraft auto-layout into responsive flexbox / grid.
- **Props over Hardcoded Copy**: Expose text layers and component variants as typed optional props with canvas values as defaults so generated components are immediately reusable.
- **Accessible Semantics**: Preserve `<button type="button">`, `<nav>`, `<header>`, `<footer>`, and heading hierarchy (`<h1>`, `<h2>`, `<h3>`).
