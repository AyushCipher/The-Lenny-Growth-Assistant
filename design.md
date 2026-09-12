# Design Specification: The Lenny Growth Assistant
**Role**: Forward Deployed Engineer Take-Home Assessment  
**Author**: Ayush Verma (ayushv3533e@gmail.com)  
**Status**: Approved & Active  
**Version**: 1.0.0  

---

## 1. UI/UX Principles & Philosophy

1. **High Craft & Density**: Designed specifically for product leaders who value information density, clear typography, and zero fluff.
2. **Immediate Grounding & Verifiability**: Citations are not hidden in footnotes; they appear as interactive, clickable badges directly within the flow of conversation.
3. **Claude-Style Split Pane**: Generating an artifact transforms the chat experience into an interactive IDE split-screen without disruptive page navigation or popups.
4. **Resilient Transparency**: System states (active LLM provider, Ollama connectivity, index health, token usage) are always visible and actionable.
5. **Defense-in-Depth Sandbox Security**: The Artifact Viewer provides complete isolation for generated HTML/CSS using iframe sandboxing and strict Content Security Policies.

---

## 2. Information Architecture & Layout Hierarchy

```
+---------------------------------------------------------------------------------------------------+
|  Header: [Brand Logo / Title]  |  [Model Selector Badge: Ollama / Claude / OpenAI]  | [Health]     |
+-------------------+----------------------------------------------------+--------------------------+
|  SIDEBAR          |  CENTER CHAT PANE                                  |  ARTIFACT VIEWER (RIGHT) |
|  - New Chat       |  - Conversation Stream                             |  - Header: Title & Type  |
|  - Ship 30 Skill  |  - Grounded Markdown & LaTeX                       |  - Tabs: Preview / Code  |
|  - Session List   |  - Clickable Citation Chips: [[Guest - Ep]](id)    |  - Sandboxed <iframe>    |
|  - Knowledge Base |  - Follow-up Suggestion Pills                      |  - Version History Drop  |
|  - Diagnostics    |  - Input Area + Skill Shortcuts                    |  - Copy / Download .html |
+-------------------+----------------------------------------------------+--------------------------+
|  Slide-Out Drawer: [Transcript Inspector: Source metadata, full quotes, episode timestamp link]  |
+---------------------------------------------------------------------------------------------------+
```

### 2.1 Layout Modes
- **Single Pane (Chat Mode)**: When no artifact is active, the chat pane occupies the full main workspace width (max-w-4xl centered) for comfortable reading.
- **Split Pane (Artifact Mode)**: When an artifact is generated or opened, the workspace divides into a 50/50 split (customizable via drag resizer), with chat on the left and the interactive sandbox on the right.
- **Mobile Responsive Mode (< 768px)**: Automatically transitions into stacked tab views (Chat tab vs. Artifact tab) with a persistent bottom navigation bar.

---

## 3. Design System & Tokens

### 3.1 Color Palette
- **Backgrounds**:
  - Main App Background: `#0B0F17` (Deep Obsidian Dark)
  - Surface Card / Sidebar: `#111827` (Rich Slate)
  - Surface Elevated / Modals: `#1F2937` (Cool Charcoal)
  - Border Accents: `#374151` / `#4B5563`
- **Typography & Brand Accents**:
  - Primary Brand Accent: `#6366F1` (Indigo Glow)
  - Accent Secondary: `#8B5CF6` (Violet)
  - Citation Accent: `#10B981` (Emerald Green badge)
  - Warning / Diagnostic: `#F59E0B` (Amber)
  - Text Primary: `#F9FAFB` (95% White)
  - Text Secondary: `#9CA3AF` (Muted Gray)
  - Text Code / Mono: `#E5E7EB` with JetBrains Mono font family

### 3.2 Typography Hierarchy
- Headings: Inter Display (`font-sans`, weights 600-700)
- Body Prose: Inter (`font-sans`, weights 400-500, `leading-relaxed`)
- Code & Data Tables: JetBrains Mono / Fira Code (`font-mono`, weight 400)

---

## 4. Key Interaction States & Micro-interactions

### 4.1 Chat Feed & Grounded Citations
- **Assistant Streaming**: Renders text progressively with smooth Markdown formatting.
- **Citation Chips**: Rendered as styled pill badges: `[[Shreyas Doshi - Product Strategy | 14:30]](src_shreyas_doshi_01)`.
  - *Hover*: Displays tooltip with snippet preview.
  - *Click*: Opens the **Transcript Inspector Drawer** on the right, highlighting the exact retrieved chunk.
- **Follow-up Suggestions**: Rendered as clickable pill buttons at the bottom of the assistant message.

### 4.2 Ship 30 for 30 Skill Trigger
- **Modal Trigger**: Clicking "Ship 30 for 30" in the sidebar opens a dedicated parameter modal allowing users to enter a core topic (e.g. *"Why Most Startups Fail at PLG"*), target persona, and selected podcast guest influences.
- **Structured Rendering**: Outputs the complete ~1,250-word essay with H2 section breaks, 1-3-1 pacing cadence, selective bold emphasis, and a 3-step action takeaway box.

### 4.3 Claude-Style Artifact Viewer
- **Automatic Opening**: When the agent outputs `:::artifact{title="..." type="html"} ... :::`, the split pane transitions smoothly into view.
- **Tab 1 - Rendered Preview**:
  - Runs in a clean, isolated `<iframe>` environment with `sandbox="allow-scripts"`.
  - Injected CSP `<meta>` tag blocks external network requests (`connect-src 'none'`) and external scripts (`script-src 'unsafe-inline'`).
  - Supports local JavaScript interactivity (e.g., interactive sliders for growth loops, dynamic ROI calculations, canvas charts).
- **Tab 2 - Source Code**:
  - Full syntax-highlighted code editor (PrismJS) with line numbers.
  - Actions: **Copy to Clipboard**, **Download File** (`.html` or `.md`), **Open in Fullscreen**.
- **Version History**: Dropdown selector allowing users to switch between iterations of an artifact created in the same session.

---

## 5. Security & Isolation Strategy

### 5.1 Defense-in-Depth Matrix
| Layer | Mechanism | Protection Provided |
| :--- | :--- | :--- |
| **Layer 1: Backend Sanitizer** | Python `bleach` & AST clean | Strips dangerous `<script>` src tags, `onerror`, `onload`, `eval()`, `javascript:` URIs. |
| **Layer 2: Content Isolation** | Self-contained styles | All CSS is injected inline or bundled; no external CDN links inside untrusted markup. |
| **Layer 3: Strict CSP** | Injected `<meta>` CSP header | `default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src 'self' data:; connect-src 'none'; frame-src 'none'; font-src 'none';` blocks data exfiltration. |
| **Layer 4: Browser Sandbox** | `iframe sandbox="allow-scripts"` | Strictly omits `allow-same-origin`, `allow-top-navigation`, and `allow-forms`. |

---

## 6. Accessibility & Responsiveness (WCAG 2.1 AA)

1. **Color Contrast**: All text elements maintain $\ge 4.5:1$ contrast ratio against dark backgrounds.
2. **Keyboard Navigation**:
   - `Enter` sends message; `Shift + Enter` inserts new line.
   - `Esc` closes modals and slide-out drawers.
   - Tab indexes follow natural reading order.
3. **Screen Reader Compatibility**: ARIA labels on all icon buttons (`aria-label="Copy code"`, `aria-label="Toggle model selector"`, `aria-label="Inspect source citation"`).
