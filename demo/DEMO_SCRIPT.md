# Demo Video Script & Walkthrough: The Lenny Growth Assistant
**Role**: Forward Deployed Engineer Take-Home Assessment  
**Author**: Ayush Verma (ayushv3533e@gmail.com)  
**Target Video Duration**: 2–3 minutes (Camera Enabled)  
**YouTube Link**: [https://youtube.com/watch?v=YOUR_DEMO_VIDEO_ID_HERE](https://youtube.com/watch?v=YOUR_DEMO_VIDEO_ID_HERE) *(Replace with recorded video URL)*

---

## 1. Video Outline & Timing Breakdown

| Segment | Timing | Script & Visual Actions |
| :--- | :--- | :--- |
| **1. Hook & Problem Framing** | 0:00 - 0:35 | **Camera On**: Introduce yourself as Ayush Verma. Explain the problem: Product and growth teams want actionable, reliable answers from 200+ hours of Lenny's Podcast wisdom, but face disparate search, hallucination, and a lack of ready-to-use artifacts. |
| **2. Architecture & Local Ollama Demo** | 0:35 - 1:20 | **Screen Share**: Show the app running locally on **Ollama (`llama3`)**. Submit a question: *"What is Shreyas Doshi's advice on high-agency PMs?"*. Show live streaming with clickable citation chips. Click a citation to reveal the slide-out **Transcript Inspector Drawer** showing the exact chunk and episode metadata. |
| **3. Ship 30 for 30 Skill** | 1:20 - 1:55 | Click the **Ship 30 for 30** button. Generate an essay on *"Why B2B Startups Struggle with PLG"*. Point out the hook formula, 1-3-1 cadence, bold emphasis, and transcript grounding (~1,250 words). |
| **4. Claude-Style Artifact Viewer & Sandbox** | 1:55 - 2:30 | Ask the assistant: *"Create an interactive growth loop simulator in HTML/CSS based on Brian Balfour's model"*. Show the split-pane Artifact Viewer auto-opening. Demonstrate the interactive slider controls, switch to the code tab, and highlight the sandboxed iframe security isolation (zero external CDN, CSP meta tag). |
| **5. Technical Trade-off & Conclusion** | 2:30 - 3:00 | **Camera On**: Discuss one key technical trade-off: Choosing **Hybrid RRF (Dense Vector + BM25, k=60)** over pure vector search to achieve high precision on domain-specific PM terminology (e.g. SPADE, 40% PMF rule) while keeping the system 100% locally deployable. Conclude and sign off. |

---

## 2. Key Talking Points Checklist
- [x] Camera enabled throughout the introduction and conclusion.
- [x] Clear explanation of the business problem and pain removed.
- [x] Active demonstration of **Local Ollama** backend.
- [x] Verified transcript citations and source drawer inspection.
- [x] Dedicated Ship 30 for 30 skill execution.
- [x] Interactive Claude-style Artifact Viewer in sandboxed iframe.
- [x] Articulation of the Hybrid RAG trade-off decision.
