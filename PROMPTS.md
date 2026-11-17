# FigCraft Prompt Formula Cheat Sheet

> Ready-to-use prompt formulas for designing UI on the FigCraft canvas and converting designs into frontend code.

**English** | [Baca dalam Bahasa Indonesia](PROMPTS.id.md)

---

## Table of Contents
1. [Anatomy of an Effective Prompt](#1-anatomy-of-an-effective-prompt)
2. [Category 1: Navigation and Menus](#2-category-1-navigation-and-menus)
3. [Category 2: Forms and Authentication](#3-category-2-forms-and-authentication)
4. [Category 3: Content Cards and Media Widgets](#4-category-3-content-cards-and-media-widgets)
5. [Category 4: Dashboards and Metric Displays](#5-category-4-dashboards-and-metric-displays)
6. [Category 5: Modals and Interactive Dialogs](#6-category-5-modals-and-interactive-dialogs)
7. [Category 6: Design-to-Code Conversion Prompts](#7-category-6-design-to-code-conversion-prompts)
8. [Practical Tips for Best Results](#8-practical-tips-for-best-results)

---

## 1. Anatomy of an Effective Prompt

To ensure your AI assistant creates well-structured, proportional UI components that convert cleanly into code, use the following 5-part prompt structure:

```
[Role] + [Container Name & Dimensions] + [Layout Structure] + [Visual Styling & Colors] + [Content Details]
```

### Formula Breakdown:
- **Role**: State that the AI is acting as an interface designer ("Design in FigCraft...").
- **Container Name & Dimensions**: Name the target frame and provide dimension constraints (for example: "Card container 380x480 pixels").
- **Layout Structure**: Specify flex direction (flex-column vertical or flex-row horizontal) alongside `gap` and `padding` values.
- **Visual Styling & Colors**: State your color theme (dark or light), corner radius, borders, and hex color codes.
- **Content Details**: Detail headings, button labels, icons, badges, or input fields.

---

## 2. Category 1: Navigation and Menus

### Formula A: Modern Desktop Top Navbar
```
Design a modern desktop Top Navbar component in FigCraft:
- Main container: Horizontal frame (flex-row), width 1200px, height 72px, dark background #0F172A, horizontal padding 32px, align-items center, justify-between.
- Left side: Logo text 'AcmeFlow' at 20px font-bold in white #FFFFFF.
- Center: Navigation menu with 4 horizontal text links (Products, Solutions, Pricing, Docs) at 14px in muted gray #94A3B8 with a 28px gap.
- Right side: Primary CTA button 'Get Started' with indigo background #6366F1, white text 14px, corner radius 8px, padding 10px 20px.
```

### Formula B: Mobile App Bottom Navigation Bar
```
Create a mobile Bottom Navigation Bar in FigCraft:
- Container: Horizontal frame, width 375px, height 64px, background #1E293B, top border 1px in #334155.
- Items: 4 evenly spaced navigation destinations (Home, Explore, Notifications, Profile).
- Active state: 'Home' item features sky blue text #38BDF8 with a small indicator dot below. The remaining 3 items use muted slate text #64748B.
```

---

## 3. Category 2: Forms and Authentication

### Formula A: Dark Mode Login Card
```
Design a dark-mode Login Card in FigCraft:
- Main container: Vertical frame (flex-col), width 400px, padding 32px, corner radius 16px, background #18181B, subtle 1px border #27272A.
- Header: Title text 'Sign In to Your Account' at 22px bold in white, and subtitle 'Enter your email and password' at 14px in gray #A1A1AA, gap 8px.
- Email Input: Label 'Email Address' at 12px, followed by an input field (frame height 44px, background #27272A, radius 8px, horizontal padding 14px, placeholder text 'name@company.com' in #71717A).
- Password Input: Label 'Password' at 12px, followed by an identical input frame with placeholder text '••••••••'.
- Link: Small 'Forgot password?' link at 12px right-aligned in #818CF8.
- Submit Button: Full-width button frame (width 336px, height 44px), indigo background #4F46E5, radius 8px, bold white text 'Sign In' at 14px centered.
- Gap between form groups: 16px.
```

### Formula B: Registration Form with Password Strength State
```
Create an account registration card in FigCraft with a vertical container of width 420px:
- Form header: 'Create Your Account' in #0F172A on a clean white card #FFFFFF.
- Inputs: Full Name input, Email input, and Password input.
- Visual validation state: Below the password input, add a green indicator text #16A34A reading 'Password strength: Strong'.
- Checkbox for Terms of Service acceptance and an emerald green CTA button #059669 reading 'Register Account'.
```

---

## 4. Category 3: Content Cards and Media Widgets

### Formula A: Modern E-Commerce Product Card
```
Design a sneaker e-commerce product card in FigCraft:
- Card container: Vertical frame, width 320px, radius 16px, background #18181B, padding 16px, gap 14px.
- Image Area: Product placeholder frame height 200px in #27272A, radius 12px, with a red discount badge 'SALE 30%' in #EF4444 in the top-left corner.
- Product Details:
  - Category text: 'MEN RUNNING SHOES' at 11px uppercase in #71717A.
  - Title: 'AeroGlide Pro Runner V2' at 16px bold in white #F4F4F5.
- Size Selector: Horizontal row of size buttons (flex-row, gap 8px) with sizes 40, 41, 42, 43, 44. Size 42 in selected state (white background, dark text).
- Price and CTA Row:
  - Current price '$129.00' at 18px bold in white, and strikethrough price '$189.00' at 12px in gray.
  - Action button 'Buy Now' in indigo #6366F1 with padding 8px 16px and radius 8px.
```

### Formula B: Compact Music Player Widget
```
Design a compact music player widget in FigCraft:
- Container: Vertical frame, width 340px, background #111827, radius 18px, padding 20px, gap 16px.
- Album Art: Square image frame 300x300px in #1F2937 with radius 12px.
- Track Information: Title 'Midnight Echoes' at 18px bold in white, and artist 'Lunar Drift' at 14px in #9CA3AF.
- Progress Bar: Dark track line #374151 height 4px width 300px, with an active progress fill in sky blue #38BDF8 for 180px. Time stamps '2:15' and '3:45' at 11px.
- Playback Controls: Centered horizontal row containing Previous, a large circular Play/Pause button (48px white circle with dark icon), and Next.
```

### Formula C: SaaS Subscription Pricing Card
```
Create a 'Pro Plan' pricing card in FigCraft:
- Container: Width 360px, padding 32px, radius 20px, background #0F172A, 2px border in indigo #6366F1.
- Top badge: 'MOST POPULAR' badge in #6366F1 with bold white text at 10px.
- Pricing figure: '$29' at 36px bold in white, followed by '/month' at 14px gray.
- Features list: 5 checked feature lines (24/7 Priority Support, Unlimited Canvas Exports, Team Collaboration, Full API Access, Cloud Backup).
- Action button: 'Upgrade to Pro' full width in #6366F1 with white text at 14px.
```

---

## 5. Category 4: Dashboards and Metric Displays

### Formula A: Monthly Revenue Analytics Card
```
Design an analytics revenue metric card in FigCraft:
- Container: Vertical frame, width 280px, padding 20px, radius 14px, background #1E293B, border 1px #334155, gap 12px.
- Header Row: Title 'Total Revenue' at 13px in #94A3B8, and a positive growth badge '+18.4%' (background #064E3B, text #34D399, radius 6px, padding 4px 8px, size 11px).
- Main Metric: Large figure '$148,520' at 26px bold in white #F8FAFC.
- Footer: Comparison note 'Compared to previous month ($125,400)' at 12px in #64748B.
```

### Formula B: 3-Column Dashboard Stats Row
```
Create a 3-column stats summary row in FigCraft:
- Parent container: Horizontal frame (flex-row, gap 16px).
- Card 1: 'Active Users' reading '24,810' with trend '+12%'.
- Card 2: 'Conversion Rate' reading '3.42%' with trend '+0.8%'.
- Card 3: 'Avg Response Time' reading '142ms' with trend '-15ms (faster)'.
- Each card has width 220px, dark background #1E293B, and corner radius 12px.
```

---

## 6. Category 5: Modals and Interactive Dialogs

### Formula A: Delete Confirmation Dialog
```
Design a delete confirmation modal dialog in FigCraft:
- Modal container: Vertical frame, width 440px, padding 28px, radius 16px, background #FFFFFF (or dark #18181B), gap 18px.
- Warning Icon: 48px rounded container in soft red #FEE2E2 with a red exclamation symbol #DC2626.
- Text: Heading 'Delete this Project?' at 18px bold, and description 'This action cannot be undone. All canvas history and saved components will be permanently deleted.' at 14px in muted gray.
- Action Buttons Row: Horizontal frame (justify-end, gap 12px) with 'Cancel' button (gray border, dark text) and 'Delete Project' button (red background #DC2626, white text).
```

---

## 7. Category 6: Design-to-Code Conversion Prompts

Once visual components are created on the FigCraft canvas, use these prompt formulas to translate them into clean code.

### Formula A: Convert Canvas Element to React + Tailwind CSS
```
Inspect the active card element on the FigCraft canvas. Extract its layout structure, hex colors, corner radius, padding values, and typography, then generate a standalone TypeScript React functional component styled with responsive Tailwind CSS.
```

### Formula B: Convert Canvas Element to Flutter Widget
```
Read the selected component frame in FigCraft. Translate its container hierarchy, flex columns, flex rows, border radius, and colors into a clean, structured Flutter StatelessWidget.
```

### Formula C: Extract Design Tokens to tailwind.config.js
```
Analyze all color palettes and typography sizes used across this FigCraft canvas page. Generate a theme.extend configuration object for tailwind.config.js capturing the background colors, text colors, and border radius tokens.
```

---

## 8. Practical Tips for Best Results

1. **Use Semantic Frame Names**: Ask the AI to name frames clearly (e.g. `Navbar`, `LoginCard`, `PricingCard`) so the layer tree stays organized.
2. **Explicitly State Flex Directions**: Always mention whether container elements should arrange their children vertically (`flex-col`) or horizontally (`flex-row`).
3. **Provide Hex Color Codes**: For consistent branding, provide exact hex color values (e.g. `#4F46E5` for indigo, `#0F172A` for slate).
4. **Avoid One-Line Prompts**: A prompt like "make a nice button" will generate generic default elements. A prompt like "create a primary CTA button, full-width, height 44px, indigo background #4F46E5, radius 8px, bold white text centered" yields pixel-accurate results.
5. **Use Transparent Layout Wrappers**: When grouping buttons, text links, or metrics (flex rows/cols), ensure wrapper containers use transparent fills (`fill: 'none'`) so FigCraft does not apply its solid white default fill over dark themes.
