run_id: 20260831-task-dialogue-repair-handoff
question: "How should an interface enter a task dialogue with a confused user, repair misunderstandings, and hand off to a human without losing progress?"
decision: "Treat dialogue as a typed task-state repair protocol with mixed initiative, minimal clarification, explicit confirmation, and context-preserving human handoff; compare it against no-dialogue and free-chat controls in a synthetic kiosk."
scope: "Task-oriented dialogue research, open-source dialogue-management patterns, accessibility guidance, dialogue evaluation, and high-level transfer to critical-system interfaces. Excludes weapon tactics, real-system commands, covert monitoring, and autonomous commitment."
acceptance_criteria:
  - "Find evidence for mixed-initiative clarification or implicit-request handling."
  - "Find an open-source dialogue manager with repair and human-handoff patterns."
  - "Find a task-oriented dialogue evaluation framework that separates task success from dialogue cost."
  - "Define a concrete, safe experiment for a kiosk-like flow."
effort_budget: "Focused research pass; no external installation or live integration."
status: decided

concepts:
  - id: C-001
    term: "task-oriented dialogue"
    meaning: "Conversation turns are anchored to a task state and either clarify, modify, confirm, or transfer that state."
    related_to: ["C-002", "C-003"]
    origin: source
    next_query: "How do dialogue systems repair ambiguity without restarting the task?"
  - id: C-002
    term: "mixed initiative"
    meaning: "Both user and system may introduce relevant information or ask for clarification while the task remains bounded."
    related_to: ["C-001", "C-004"]
    origin: source
    next_query: "When should the system propose help instead of waiting for an explicit request?"
  - id: C-003
    term: "grounding and repair"
    meaning: "The system exposes its interpretation, identifies what is missing, and asks a minimal question to resolve the branch."
    related_to: ["C-001", "C-005"]
    origin: source
    next_query: "Which repair message reduces ambiguity without adding conversational cost?"
  - id: C-004
    term: "progress-preserving handoff"
    meaning: "A human receives current stage, confirmed values, errors, and unresolved question so the user does not restart."
    related_to: ["C-002", "C-005"]
    origin: source
    next_query: "What minimum context must be transferred for a human to resume?"
  - id: C-005
    term: "dialogue cost"
    meaning: "Time, turns, repetition, errors, abandonment, and cognitive burden incurred by the conversation."
    related_to: ["C-003", "C-004"]
    origin: source
    next_query: "How should task success and dialogue cost be combined without rewarding unsafe speed?"

queries:
  - id: QRY-001
    text: "TITAN task-oriented dialogues mixed-initiative clarification implicit requests IJCAI 2023"
    channel: web
    reason: "Find research on systems initiating useful clarification rather than waiting for explicit help."
    expected_gain: "Ground the proposed kiosk dialogue in mixed-initiative interaction."
    result: "TITAN provides 1,800 human-human conversations with mixed-initiative strategies; models still struggle with implicit requests and alternatives."
    next_action: "Keep the first FARMAXIA dialogue bounded and state-driven."
  - id: QRY-002
    text: "Rasa official conversation patterns clarification correction human handoff fallback"
    channel: web
    reason: "Find a high-reputation open-source implementation with repair and escalation states."
    expected_gain: "Adopt patterns without building a free-form chatbot."
    result: "Rasa documents patterns for correction, clarification, interruption, cancellation, error, and human handoff, plus staged fallback."
    next_action: "Use as architecture reference; do not install until the local contract is stable."
  - id: QRY-003
    text: "PARADISE framework task success dialogue cost evaluation spoken dialogue agents"
    channel: web
    reason: "Find a mature evaluation method separating task success from conversational cost."
    expected_gain: "Avoid optimizing naturalness or speed while missing the actual task."
    result: "PARADISE models performance using task success and dialogue costs and supports comparison across tasks."
    next_action: "Use task success, errors, turns, time, handoff, and recovery as prototype metrics."
  - id: QRY-004
    text: "W3C confirmation irreversible action concise feedback error correction forms"
    channel: web
    reason: "Ground confirmation and correction behavior in accessibility guidance."
    expected_gain: "Make dialogue useful at commitment boundaries."
    result: "W3C recommends clear feedback, correction guidance, review, and confirmation for irreversible actions."
    next_action: "Add explicit commit confirmation to the dialogue state machine."

sources:
  - id: S-001
    title: "TITAN: Task-oriented Dialogues with Mixed-Initiative Interactions"
    author_or_org: "Yan, Song, Li, Meng, Hu; IJCAI"
    date: "2023"
    accessed: "2026-08-31"
    type: empirical
    url_or_path: "https://www.ijcai.org/proceedings/2023/583"
    supports: ["CL-001", "CL-002"]
    contradicts: []
    quality: "High for the dataset and task-oriented mixed-initiative framing."
    limitations: "Dataset and benchmark; it does not prove the same dialogue policy works in kiosks or critical systems."
  - id: S-002
    title: "Conversation Patterns"
    author_or_org: "Rasa"
    date: "current documentation accessed 2026-08-31"
    accessed: "2026-08-31"
    type: repository
    url_or_path: "https://rasa.com/docs/reference/primitives/patterns/"
    supports: ["CL-003", "CL-004"]
    contradicts: []
    quality: "High for documenting the project's own dialogue repair and handoff architecture."
    limitations: "Product documentation is not an independent evaluation of every pattern."
  - id: S-003
    title: "Fallback and Human Handoff"
    author_or_org: "Rasa Open Source documentation"
    date: "current legacy documentation accessed 2026-08-31"
    accessed: "2026-08-31"
    type: repository
    url_or_path: "https://legacy-docs-oss.rasa.com/docs/rasa/fallback-handoff/"
    supports: ["CL-003", "CL-004"]
    contradicts: []
    quality: "High for the described fallback and context-transfer pattern."
    limitations: "Implementation pattern, not a guarantee of successful human service."
  - id: S-004
    title: "PARADISE: A Framework for Evaluating Spoken Dialogue Agents"
    author_or_org: "Walker, Litman, Kamm, Abella"
    date: "1997"
    accessed: "2026-08-31"
    type: empirical
    url_or_path: "https://arxiv.org/abs/cmp-lg/9704004"
    supports: ["CL-005"]
    contradicts: []
    quality: "High as a foundational task/dialogue evaluation framework."
    limitations: "Older spoken-dialogue context; metrics require adaptation to visual kiosk interactions."
  - id: S-005
    title: "User Notification"
    author_or_org: "W3C Web Accessibility Initiative"
    date: "current guidance accessed 2026-08-31"
    accessed: "2026-08-31"
    type: official
    url_or_path: "https://www.w3.org/WAI/tutorials/forms/notifications/"
    supports: ["CL-003"]
    contradicts: []
    quality: "High for concise feedback and correction guidance."
    limitations: "Guidance, not a task-dialogue experiment."
  - id: S-006
    title: "Gamifying Ukraine’s army of drones: strategic or moral(e) destruction?"
    author_or_org: "Giametta; International Politics"
    date: "2026"
    accessed: "2026-08-31"
    type: secondary
    url_or_path: "https://link.springer.com/article/10.1057/s41311-026-00753-w"
    supports: ["CL-005"]
    contradicts: []
    quality: "Medium for public analysis of a live-conflict incentive program."
    limitations: "Secondary and context-specific; not evidence that any points system always causes metric displacement."

claims:
  - id: CL-001
    statement: "A useful dialogue must be anchored to the current task stage rather than operate as open-ended chat."
    status: supported
    evidence: ["S-001", "S-002"]
    inference_notes: "The FARMAXIA state contract is an engineering implementation of the task-oriented principle."
    confidence: high
  - id: CL-002
    statement: "The system can initiate a minimal clarification when sustained difficulty or an implicit request is detected."
    status: partially_supported
    evidence: ["S-001", "S-002"]
    inference_notes: "Mixed initiative is established, but the best trigger for a real kiosk remains an experiment."
    confidence: medium
  - id: CL-003
    statement: "Repair, staged fallback, and explicit human handoff are more useful than generic timeout prompts."
    status: supported
    evidence: ["S-002", "S-003", "S-005"]
    inference_notes: "Effectiveness in FARMAXIA still requires a controlled comparison."
    confidence: high
  - id: CL-004
    statement: "A handoff must preserve confirmed context and the unresolved question."
    status: supported
    evidence: ["S-003"]
    inference_notes: "Context transfer is a software design pattern; its effect on public dignity and completion should be tested."
    confidence: high
  - id: CL-005
    statement: "Dialogue quality must be evaluated by verified task success and dialogue cost, not naturalness or speed alone."
    status: supported
    evidence: ["S-004", "S-006"]
    inference_notes: "The incentive-displacement conclusion is a general design inference from the cited conflict analysis."
    confidence: high

models:
  - id: M-001
    kind: thesis
    statement: "X-ANA-X should be a bounded task-dialogue repair layer: clarify, explain, compare, preserve context, and hand off."
    assumptions: ["The host application exposes current stage and valid next states.", "A human or guided path exists for unresolved cases.", "The agent cannot silently commit an ambiguous action."]
    predictions: ["It will reduce abandonment more than a generic chatbot if it preserves task context.", "It will use fewer turns than open chat while improving repair success."]
    evidence_for: ["CL-001", "CL-003", "CL-004"]
    evidence_against: []
    status: "selected for next prototype"
  - id: M-002
    kind: hypothesis
    statement: "Progress-preserving handoff will improve completion and reduce repetition cost under queue pressure."
    assumptions: ["The handoff summary is accurate.", "The human helper can access the transferred context.", "The user chooses or accepts handoff."
    ]
    predictions: ["Handoff users will restart fewer steps.", "Visible help will reduce abandonment without requiring camera-based detection."]
    evidence_for: ["CL-003", "CL-004"]
    evidence_against: []
    status: "testable"

open_questions:
  - id: OQ-001
    question: "What is the smallest clarification question that reliably separates the current task branches?"
    why_it_matters: "A question that does not reduce ambiguity only adds pressure and delay."
    next_test: "For each synthetic stage, enumerate valid next states and generate one discriminating question."
    stop_condition: "Reject the question if most answers still lead to the same unresolved branch."
  - id: OQ-002
    question: "When should a stalled user receive a system-initiated dialogue instead of waiting for help?"
    why_it_matters: "Early intervention can embarrass; late intervention can cause abandonment."
    next_test: "Compare fixed timeout, stage-relative stall score, and explicit help-only interaction."
    stop_condition: "Reject the proactive policy if it increases false interventions for slow successful users."
  - id: OQ-003
    question: "What context must cross a human handoff to prevent repetition and preserve privacy?"
    why_it_matters: "The handoff is only useful if the human can resume the task safely."
    next_test: "Test summaries containing current stage, confirmed values, errors, and unresolved question."
    stop_condition: "No handoff claim if the user must repeat critical information or if the summary invents it."

decision:
  recommendation: "Implement a typed task dialogue with mixed initiative, one-question repair, explicit confirmation, progress-preserving handoff, and replayable events. Compare it against no-dialogue and free-chat controls in the synthetic kiosk."
  rationale: "Research and mature open-source patterns converge on bounded task state, clarification/repair, staged fallback, context transfer, and success-versus-dialogue-cost evaluation."
  risks: ["Proactive help can feel intrusive or stigmatizing.", "A generative answer can sound confident while failing to change the task state.", "Handoff context can expose more data than necessary.", "Dialogue turn minimization can reward unsafe guessing."
  ]
  reversibility: "High: local synthetic flow, no external action, replayable dialogue events, and replaceable policy."
  confidence: "high for task-dialogue architecture; medium for intervention timing and handoff benefit"
  unresolved_but_accepted: ["Trigger threshold", "Question generation constraints", "Minimum handoff payload"]
  next_review_trigger: "After the first simulator compares no-dialogue, bounded dialogue, and free-chat controls on held-out task traces."
