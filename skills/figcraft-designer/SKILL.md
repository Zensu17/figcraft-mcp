---
name: figcraft-designer
description: Expert interface designer for FigCraft. Use when the user asks to design, create, update, inspect, or export UI components, screens, or layouts in FigCraft.
---

# FigCraft Designer Skill

FigCraft is an open-source, pure-Rust collaborative interface design tool that speaks MCP natively.

## Coordinate & Layout Rules
- **Coordinates**: Page units (1 unit = 1 px at 100% zoom). X goes right, Y goes DOWN.
- **Parent Relative**: `x` and `y` are relative to the parent frame (or page if no parent).
- **Auto-Layout Alignment Enums**:
  - `mainAlign`: `"min"`, `"center"`, `"max"`, `"spaceBetween"`, `"spaceAround"`, `"spaceEvenly"`. Note: do NOT use `"start"` or `"end"` (use `"min"` / `"max"`).
  - `crossAlign`: `"min"`, `"center"`, `"max"`, `"baseline"`. Note: do NOT use `"start"` or `"end"` (use `"min"` / `"max"`).
  - When auto-layout is enabled on a parent frame, do NOT set manual `x`/`y` on its children.
- **MANDATORY: Transparent Layout Wrappers (`fill: "none"`)**:
  - In FigCraft, any frame created without an explicit `fill` property defaults to solid opaque white (`#FFFFFF`).
  - Therefore, you MUST explicitly specify `fill: "none"` for all structural wrapper frames (flex rows, columns, button groups, metric rows) unless an opaque background card color is specifically intended. Failure to set `fill: "none"` will result in opaque white rectangles covering dark-mode layouts.

## Property Naming Reference
- **Border Stroke**: Use `stroke` (hex color) and `strokeWeight` (number, NOT `strokeWidth`).
- **Typography**: Use `fontSize` (number), `fill` (text color), and `fontStyle` (`"Bold"`, `"SemiBold"`, `"Medium"`, `"Regular"`). Do not use `fontWeight: 700` (use `fontStyle: "Bold"` instead).

## Best Practices
1. **Single Undo Batching**:
   - For multi-layer components, combine steps using the `batch` tool with `onError: "abort"`.
   - Steps can reference previous step results using `{"$ref": "stepName"}`.
2. **Hierarchy**:
   - Create parent container frames first, then pass `parent: container_id` to children.
3. **Visual Self-Verification**:
   - After creating or modifying a layout, call `screenshot` (with layer `ids` or whole page) to visually confirm padding, colors, contrast, and alignment.
4. **Color and Layout Tokens**:
   - Adhere to standard design tokens defined in `tokens.json`:
     - Backgrounds: Dark slate (`#0F172A`, `#1E293B`) or zinc (`#18181B`, `#27272A`).
     - Accents: Indigo (`#4F46E5`, `#6366F1`) or Sky (`#0284C7`, `#38BDF8`).
     - Radius scale: `sm` (2px), `default` (4px), `md` (6px), `lg` (8px), `xl` (12px), `2xl` (16px).
     - Spacing scale: multiples of 4px (8px, 12px, 16px, 20px, 24px, 32px).
   - Use high contrast ratios between text and background fills.
