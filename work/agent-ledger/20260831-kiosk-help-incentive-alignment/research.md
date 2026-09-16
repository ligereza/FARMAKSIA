run_id: 20260831-kiosk-help-incentive-alignment
question: "How can an interface help a user who starts quickly and then stalls, and how can a critical system avoid rewarding fast wrong actions over calibrated doubt?"
decision: "Build an interaction-only continuity assistant: infer sustained task difficulty from stage-relative event sequences, provide contextual help and progress-preserving handoff, and score verified outcomes plus correct pause/escalation rather than raw speed or points."
scope: "Public accessibility guidance, kiosk/self-service research, adaptive interaction research, and public analysis of incentive alignment in drone programs. Excludes weapon tactics, real-system operation, covert monitoring, and emotion or medical inference."
acceptance_criteria:
  - "Find public guidance for error feedback and irreversible-action confirmation."
  - "Find empirical or pilot evidence about kiosk hesitation, queue pressure, help-seeking, and recovery."
  - "Find a concrete adaptive interaction approach that avoids fixed thresholds."
  - "Translate the evidence into a measurable FARMAXIA prototype and kill tests."
effort_budget: "Focused web research pass plus local record; no external installation or corpus download."
status: decided

concepts:
  - id: C-001
    term: "task-stall state"
    meaning: "A latent operational state inferred from lack of stage progress, errors, retries, and backtracking; not a diagnosis of emotion."
    related_to: ["C-002", "C-003"]
    origin: source
    next_query: "Which event sequences distinguish slow progress from a true stall?"
  - id: C-002
    term: "progress-preserving assistance"
    meaning: "Contextual help, review, or human handoff that preserves the user's current work and dignity."
    related_to: ["C-001", "C-004"]
    origin: source
    next_query: "Which assistance level reduces abandonment without interrupting normal progress?"
  - id: C-003
    term: "change of interaction regime"
    meaning: "A transition from rapid progress to a prolonged non-progressing state, detected relative to the current task stage."
    related_to: ["C-001"]
    origin: inference
    next_query: "Can a sequential score detect rapid-start-then-freeze without punishing slow users?"
  - id: C-004
    term: "calibrated hesitation"
    meaning: "Pausing or escalating when evidence is weak and error cost is high, while continuing when evidence supports action."
    related_to: ["C-005"]
    origin: source
    next_query: "How should outcome scoring value correct pause and escalation?"
  - id: C-005
    term: "metric gaming risk"
    meaning: "A proxy such as points, speed, or action count becomes the target and displaces the real outcome."
    related_to: ["C-004"]
    origin: inference
    next_query: "What outcome and safety constraints prevent a leaderboard from rewarding wrong action?"

queries:
  - id: QRY-001
    text: "self-service kiosk hesitation queue pressure assistance recovery older adults 2026"
    channel: web
    reason: "Study simple public interactions where a user stalls under social pressure."
    expected_gain: "Identify nonintrusive recovery cues and human handoff patterns."
    result: "Recent qualitative work links queue pressure, weak confirmation, legibility, and payment ambiguity to hesitation/abandonment, and recommends visible help and predictable recovery."
    next_action: "Use progress-preserving assistance as the first prototype behavior."
  - id: QRY-002
    text: "just-in-time assistance kiosk confusion help-seeking intention multimodal modeling 2026"
    channel: web
    reason: "Find research that treats confusion as a developing latent state rather than simple inactivity."
    expected_gain: "Avoid a presence timeout or intrusive prompt."
    result: "A nine-participant pilot models sustained difficulty before explicit help-seeking; facial-expression variability was promising and EEG response heterogeneous."
    next_action: "Use event traces first; treat camera/physiology as optional later signals."
  - id: QRY-003
    text: "W3C error feedback confirmation irreversible action review correct form"
    channel: web
    reason: "Ground the interface behavior in established accessibility guidance."
    expected_gain: "Define useful feedback and commit gates without generic modal interruptions."
    result: "W3C recommends concise correction guidance, success/error notification, review/correction, and confirmation for actions that cannot be undone."
    next_action: "Implement local contextual help and explicit confirmation for commitment events."
  - id: QRY-004
    text: "adaptive dwell time per user per control IBM OptiDwell"
    channel: web
    reason: "Find a mature adaptive interaction pattern beyond fixed thresholds."
    expected_gain: "Support stage/user-relative baselines and conservative adaptation."
    result: "OptiDwell adapts dwell thresholds using per-user and per-button experience in a 9000-task study."
    next_action: "Borrow the principle, not necessarily gaze input or dwell-click."
  - id: QRY-005
    text: "Army of Drones bonus points incentives target metric unintended consequences analysis"
    channel: web
    reason: "Examine the user's example of rewards distorting critical outcomes."
    expected_gain: "Define a safer outcome-aligned score for FARMAXIA simulations."
    result: "A recent analysis describes verified e-points for drone units and discusses the tension between countable rewards, procurement, sensitive data, and broader mission objectives."
    next_action: "Do not use raw points/leaderboards; score verified outcomes and calibrated pause/escalation."

sources:
  - id: S-001
    title: "Multimodal Modeling of Help-Seeking Intentions in Self-Service Kiosk Interactions toward Just-in-Time Assistance"
    author_or_org: "Li, Zhen, Hara, Wang, Ota; Procedia CIRP"
    date: "2026"
    accessed: "2026-08-31"
    type: empirical
    url_or_path: "https://doi.org/10.1016/j.procir.2026.05.195"
    supports: ["CL-001"]
    contradicts: []
    quality: "Medium: pilot study with explicit design and small sample."
    limitations: "Nine participants; physiological and facial signals do not establish a general confusion detector."
  - id: S-002
    title: "Empathy Mapping for Inclusive Design: A Qualitative Exploration of Older Adults’ Experiences With Self-Order Kiosks in Restaurant Settings"
    author_or_org: "Cheng, Koo, Teo"
    date: "2026"
    accessed: "2026-08-31"
    type: empirical
    url_or_path: "https://doi.org/10.1177/21582440261445622"
    supports: ["CL-001", "CL-002"]
    contradicts: []
    quality: "Medium: detailed qualitative analysis with explicit contextual mechanisms."
    limitations: "Specific restaurant setting and purposive qualitative sample; not a universal population estimate."
  - id: S-003
    title: "User Notification"
    author_or_org: "W3C Web Accessibility Initiative"
    date: "current guidance accessed 2026-08-31"
    accessed: "2026-08-31"
    type: official
    url_or_path: "https://www.w3.org/WAI/tutorials/forms/notifications/"
    supports: ["CL-002", "CL-003"]
    contradicts: []
    quality: "High for public accessibility guidance on feedback, correction, and unobtrusive notifications."
    limitations: "Guidance and techniques, not evidence that every pattern improves every kiosk task."
  - id: S-004
    title: "G168: Requesting confirmation to continue with selected action"
    author_or_org: "W3C Web Accessibility Initiative"
    date: "updated 2025-07-15"
    accessed: "2026-08-31"
    type: official
    url_or_path: "https://www.w3.org/WAI/WCAG22/Techniques/general/G168"
    supports: ["CL-002", "CL-003"]
    contradicts: []
    quality: "High for the documented reversible/irreversible action pattern."
    limitations: "A technique example, not a complete interaction policy."
  - id: S-005
    title: "OptiDwell: Intelligent adjustment of dwell click time"
    author_or_org: "IBM Research"
    date: "2017"
    accessed: "2026-08-31"
    type: empirical
    url_or_path: "https://research.ibm.com/publications/optidwell-intelligent-adjustment-of-dwell-click-time"
    supports: ["CL-003"]
    contradicts: []
    quality: "Medium-high for the reported adaptive dwell interaction experiment."
    limitations: "Gaze-click task, 10 computer-savvy users, and not a confusion detector."
  - id: S-006
    title: "Gamifying Ukraine’s army of drones: strategic or moral(e) destruction?"
    author_or_org: "Giametta; International Politics"
    date: "2026"
    accessed: "2026-08-31"
    type: secondary
    url_or_path: "https://link.springer.com/article/10.1057/s41311-026-00753-w"
    supports: ["CL-004"]
    contradicts: []
    quality: "Medium for public analysis of an incentive program and its ethical/strategic tensions."
    limitations: "Secondary analysis of a live conflict; not evidence that every points program causes the same behavior."

claims:
  - id: CL-001
    statement: "A stall should be inferred from sustained stage-relative non-progress and interaction errors, not from a single timeout or camera-based presence signal."
    status: partially_supported
    evidence: ["S-001", "S-002", "S-005"]
    inference_notes: "The stage-relative sequential score is a proposed FARMAXIA model; the sources motivate sustained-struggle detection and adaptive thresholds."
    confidence: medium
  - id: CL-002
    statement: "The first intervention should be contextual feedback and progress-preserving recovery; human help should remain visible and available."
    status: supported
    evidence: ["S-002", "S-003", "S-004"]
    inference_notes: "Transfer to FARMAXIA is an engineering decision, but the recovery principles are explicit in the sources."
    confidence: high
  - id: CL-003
    statement: "Adaptive thresholds can be safer and more comfortable than one universal threshold when they are conservative and do not change control meaning."
    status: partially_supported
    evidence: ["S-005"]
    inference_notes: "OptiDwell supports per-user/per-control adaptation for dwell time, not generic task-stall detection."
    confidence: medium
  - id: CL-004
    statement: "Raw speed, clicks, or points can become a bad proxy for critical outcomes; correct pause and escalation should be represented in the utility function."
    status: partially_supported
    evidence: ["S-006", "S-004"]
    inference_notes: "Metric displacement is a general incentive-design inference; the cited conflict program is context-specific."
    confidence: medium
  - id: CL-005
    statement: "A critical interface should value calibrated doubt: act when evidence suffices, pause when error cost dominates, and verify the result independently."
    status: supported
    evidence: ["S-003", "S-004", "S-006"]
    inference_notes: "The exact scoring equation is a FARMAXIA design proposal."
    confidence: high

models:
  - id: M-001
    kind: thesis
    statement: "FARMAXIA's useful function in a public kiosk is continuity assistance, not presence detection."
    assumptions: ["The host application exposes enough task-stage and interaction events.", "Assistance can preserve current state.", "A human handoff channel exists when self-service should stop."
    ]
    predictions: ["Contextual help will reduce abandonment more safely than a generic timeout prompt.", "Progress-preserving handoff will reduce social pressure without forcing completion."]
    evidence_for: ["CL-001", "CL-002"]
    evidence_against: []
    status: "selected for next prototype"
  - id: M-002
    kind: hypothesis
    statement: "Outcome-aligned scoring will produce fewer wrong commitments than a raw speed/points leaderboard."
    assumptions: ["The simulator has hidden ground truth and outcome verification.", "The scoring function includes false positives, omissions, and correct escalation.", "Users cannot optimize the score through a known shortcut."
    ]
    predictions: ["Speed-only users will commit more errors under ambiguity.", "Outcome-aligned users will pause more selectively and recover better."]
    evidence_for: ["CL-004", "CL-005"]
    evidence_against: []
    status: "testable"

open_questions:
  - id: OQ-001
    question: "Which sequence of events most reliably separates slow progress from true stall across different tasks?"
    why_it_matters: "A false intervention humiliates or slows a user who was succeeding."
    next_test: "Generate normal, slow-progress, rapid-freeze, error-loop, and abandonment traces in the simulator."
    stop_condition: "Reject the detector if it triggers more on slow success than on sustained non-progress."
  - id: OQ-002
    question: "How much help is enough before assistance itself becomes pressure?"
    why_it_matters: "Repeated guidance can feel like surveillance or public exposure."
    next_test: "Compare passive cue, contextual guide, and preserved-progress handoff."
    stop_condition: "Reject any policy that increases abandonment or repeated errors despite more prompts."
  - id: OQ-003
    question: "What is the right value of a correct pause relative to delay and false alarm?"
    why_it_matters: "The score determines whether the operator learns prudence or reckless speed."
    next_test: "Use scenarios with varied error cost and hidden ground truth."
    stop_condition: "Reject scoring if a faster but wrong policy dominates the correct policy."

decision:
  recommendation: "Implement the event contract and three-level continuity assistant in a synthetic kiosk. Use OBSERVED_PROGRESS, DIFFICULTY_PROBABLE, HELP_EXPOSED, HANDOFF, PAUSE, ESCALATE, COMMIT, and OUTCOME_VERIFIED."
  rationale: "Kiosk research and accessibility guidance converge on visible recovery, clear confirmation, stage-specific support, and preserved user progress. Incentive research warns that countable proxies can displace the real outcome."
  risks: ["A stage-relative model can inherit bias from the baseline population.", "Assistance can become intrusive or stigmatizing.", "Outcome scoring can hide unmeasured harms.", "Public conflict-program reporting is context-specific and secondary."
  ]
  reversibility: "High: synthetic traces, local UI, no camera, no real controls, and replayable scoring."
  confidence: "high for the continuity-assistance direction; medium for the exact detection and incentive model"
  unresolved_but_accepted: ["Event schema across apps", "Stage baseline construction", "Utility weights and thresholds"]
  next_review_trigger: "After the simulator compares timeout-only, contextual assistance, and progress-preserving handoff on held-out traces."
