# Manual UI/UX Test Plan: The Lenny Growth Assistant
**Role**: Forward Deployed Engineer Take-Home Assessment  
**Author**: Ayush Verma (ayushv3533e@gmail.com)  
**Version**: 1.0.0  

---

## 1. Scope & Objective
This manual QA test plan guides an evaluator through verifying all user-facing features, split-pane interactions, model switching, grounded citations, Ship 30 for 30 essay generation, and sandboxed artifact execution.

---

## 2. Test Execution Checklist

### Test Scenario 1: Initial Launch & Health Check
- [ ] Open `http://localhost:5173` in a web browser.
- [ ] Verify that the header displays the brand title **"Lenny Assistant"** and the active model selector badge.
- [ ] Click the **Telemetry & Diagnostics** button in the sidebar footer.
- [ ] Verify that Database status is green ("Connected") and RAG stats show at least 6 episodes and 12+ chunks.

### Test Scenario 2: Grounded Q&A with Citation Inspection
- [ ] Click one of the starter prompt cards (e.g., *"High-Agency vs. Low-Agency PMs"*).
- [ ] Observe that the assistant streams an authoritative answer.
- [ ] Verify that inline citation chips (e.g. `[[Shreyas Doshi - Product Strategy | 04:15]]`) appear in the response and citation shelf.
- [ ] Click the citation chip.
- [ ] Verify that the slide-out **Transcript Inspector Drawer** opens smoothly on the right, displaying the guest profile, episode ID, and full verbatim dialogue passage.
- [ ] Close the drawer by clicking the X or "Close Drawer" button.

### Test Scenario 3: Ship 30 for 30 Essay Skill
- [ ] Click the **Ship 30 for 30 Skill** button in the sidebar or input bar.
- [ ] Select a preset topic: *"Why Most Startups Fail at Product-Led Growth (PLG)"*.
- [ ] Click **"Generate Ship 30 Essay"**.
- [ ] Verify the output follows the Ship 30 structure:
  - Curiosity/contrarian headline hook.
  - 2-Year Test opening.
  - 1-3-1 sentence pacing cadence.
  - Selective bold emphasis.
  - Verified Lenny podcast guest citations.
  - 3-step immediate action plan checklist.
  - Word count approximates ~1,250 words.

### Test Scenario 4: Claude-Style Artifact Generation & Interactive Preview
- [ ] Type a prompt requesting an interactive artifact:
  *"Generate an interactive SaaS CAC and LTV growth calculator in HTML/CSS based on Brian Balfour's unit economics framework."*
- [ ] Observe that the assistant returns an artifact tag and the **Artifact Viewer Split Pane** auto-opens on the right.
- [ ] In the **Preview Tab**:
  - Verify that the interactive widget renders in a clean sandboxed iframe.
  - Interact with input fields/buttons to verify local calculations work.
- [ ] In the **Code Tab**:
  - Verify that syntax-highlighted HTML/CSS is viewable.
- [ ] Click the **Copy** button and verify clipboard notification.
- [ ] Click the **Download** button and verify that `.html` downloads correctly.
- [ ] Toggle **Fullscreen** and verify responsive expansion.

### Test Scenario 5: Model Provider Switching
- [ ] Click the **Model Selector** dropdown in the top header.
- [ ] Switch provider between **Local Ollama**, **Anthropic Claude**, and **OpenAI**.
- [ ] Verify that the active badge updates instantly and displays the live connectivity status.

### Test Scenario 6: Session Independence & Persistence
- [ ] Click **"New Strategy Chat"** in the sidebar.
- [ ] Ask a new question on a different topic (e.g. *"What is Gokul Rajaram's SPADE framework?"*).
- [ ] Switch back and forth between previous sessions in the sidebar.
- [ ] Verify that each session preserves its distinct conversation history, citations, and artifacts.
- [ ] Refresh the browser page (`F5`) and confirm that the active session and message history persist.
