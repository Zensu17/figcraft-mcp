---
name: figcraft-designer
description: Expert interface designer for FigCraft. Use when the user asks to design, create, update, inspect, or export UI components, screens, or layouts in FigCraft.
---

# FigCraft Designer Skill

FigCraft is an open-source, pure-Rust collaborative interface design tool that speaks MCP natively.

## Coordinate & Layout Rules
- **Coordinates**: Page units (1 unit = 1 px at 100% zoom). X goes right, Y goes DOWN.
- **Parent Relative**: `x` and `y` are relative to the parent frame (or page if no parent).
- **Auto-Layout**:
  - Always prefer auto-layout for production UI: `layout: "vertical"` or `"horizontal"`.
  - Configure `gap`, `padding`, `mainAlign` (`"start"`, `"center"`, `"end"`, `"space-between"`), and `crossAlign`.
  - When auto-layout is enabled on a parent frame, do NOT set manual `x`/`y` on its children.

## Best Practices
1. **Single Undo Batching**:
   - For multi-layer components, combine steps using the `batch` tool with `onError: "abort"`.
   - Steps can reference previous step results using `{"$ref": "stepName"}`.
2. **Hierarchy**:
   - Create parent container frames first, then pass `parent: container_id` to children.
3. **Visual Self-Verification**:
   - After creating or modifying a layout, call `screenshot` (with layer `ids` or whole page) to visually confirm padding, colors, contrast, and alignment.
4. **Color Tokens**:
   - Use standard hex colors `#RRGGBB` or `#RRGGBBAA` with high contrast ratios.
