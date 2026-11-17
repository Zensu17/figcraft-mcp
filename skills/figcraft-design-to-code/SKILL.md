---
name: figcraft-design-to-code
description: Converts FigCraft canvas designs and selected frames into production-ready frontend code (React + Tailwind CSS, Flutter, Vue, or HTML/CSS). Use when the user asks to "convert FigCraft to code", "export frame as React", "generate Flutter from FigCraft", or "turn this design into code".
---

# FigCraft Design-to-Code Skill

You are an expert Frontend Engineer and Design Systems specialist. Your task is to inspect UI elements on the FigCraft canvas and translate them with pixel-perfect fidelity into clean, production-grade frontend code.

## 1. Inspection Workflow

When the user asks to convert a frame/component from FigCraft:
1. **Locate the Node**:
   - Call MCP tool `inspect_document` to see the layer hierarchy, or ask the user for the frame ID/name.
   - Or run the helper: `python codegen_helper.py --node <ID>` to obtain the cleaned, tokenized UI tree.
2. **Examine Semantic Tokens**:
   - `direction`: "col" (vertical stack) or "row" (horizontal stack).
   - `p`: padding in pixels.
   - `gap`: spacing between children in pixels.
   - `justify` & `items`: flex alignment.
   - `rounded`: corner radius in pixels.
   - `bg`: background hex color.
   - `text`, `fontSize`, `color`: typography tokens.
3. **Generate Idiomatic Code**:
   - Map tokens cleanly to the requested framework (React + Tailwind CSS by default).
4. **Visual Self-Verification**:
   - Call the `screenshot` tool on that node ID to visually cross-check alignment, contrast, and layout.

---

## 2. Token Mapping Table

### A. React + Tailwind CSS (Default)

| FigCraft Token | Tailwind Utility Class | Example |
| :--- | :--- | :--- |
| `direction: "col"` | `flex flex-col` | `<div className="flex flex-col ...">` |
| `direction: "row"` | `flex flex-row` | `<div className="flex flex-row ...">` |
| `p: 20` / `p: 24` | `p-5` / `p-6` | `p-6` (or arbitrary `p-[20px]`) |
| `gap: 12` / `gap: 16` | `gap-3` / `gap-4` | `gap-4` |
| `justify: "between"` | `justify-between` | `justify-between` |
| `justify: "center"` | `justify-center` | `justify-center` |
| `items: "center"` | `items-center` | `items-center` |
| `rounded: 16` / `24` | `rounded-2xl` / `rounded-3xl` | `rounded-2xl` (or `rounded-[16px]`) |
| `bg: "#0F172A"` | `bg-[#0F172A]` or `bg-slate-900` | `bg-[#0F172A]` |
| `fontSize: 34`, bold | `text-3xl font-bold` | `text-3xl font-bold text-white` |
| `color: "#38BDF8"` | `text-[#38BDF8]` or `text-sky-400` | `text-sky-400` |

### B. Flutter (Dart)

| FigCraft Token | Flutter Widget / Property |
| :--- | :--- |
| `direction: "col"` | `Column(children: [...])` |
| `direction: "row"` | `Row(children: [...])` |
| `p: 20` | `padding: EdgeInsets.all(20.0)` |
| `gap: 12` | `SizedBox(height: 12)` / `SizedBox(width: 12)` |
| `rounded: 16` + `bg` | `decoration: BoxDecoration(color: Color(0xFF...), borderRadius: BorderRadius.circular(16))` |
| `text: "..."` | `Text('...', style: TextStyle(fontSize: 16, color: Color(0xFF...)))` |

---

## 3. Best Practices for Generated Code
- **Never hardcode arbitrary pixel coordinates** (`top: 120px, left: 340px`). Always translate FigCraft auto-layout into responsive flexbox / grid.
- **Semantic Components**: Use `<button>` for clickable elements, `<header>` or `<nav>` for bars, and proper typography tags (`<h1>`, `<p>`, `<span>`).
- **Export Ready**: Output self-contained, typed components with clear prop interfaces.
