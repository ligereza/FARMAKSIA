run_id: 20260831-operator-training-irreversible-decisions
question: "How does an inexperienced operator learn to supervise a critical system, and what replaces undo when a physical action cannot be reversed?"
decision: "Model training as state recognition, calibrated trust, perturbation practice, explicit commitment gates, safe-state/abort paths, and independent debrief; prototype only in a benign local simulator."
scope: "Public standards and peer-reviewed human-factors research on operator training, human-autonomy teaming, confidence calibration, communication, V&V, and recovery. Excludes tactics, targeting, espionage operations, weapon employment, and instructions for real-system operation."
acceptance_criteria:
  - "Identify an official source connecting training with understanding system capabilities and limitations."
  - "Identify empirical evidence on human-autonomy training under failures or degraded conditions."
  - "Translate no-undo into pre-action safeguards and safe recovery states."
  - "Define an evaluable local prototype and kill tests."
effort_budget: "Focused research pass; no external software, corpus, vehicle, or weapon integration."
status: decided

concepts:
  - id: C-001
    term: "operator mental model"
    meaning: "Knowledge of states, roles, limits, timing, failure signatures, and available recovery paths."
    related_to: ["C-002", "C-004"]
    origin: source
    next_query: "How should training expose normality and anomaly before physical commitment?"
  - id: C-002
    term: "calibrated trust"
    meaning: "Trust proportional to demonstrated capability and current context, not maximum confidence."
    related_to: ["C-001", "C-003"]
    origin: source
    next_query: "Which training exposures change trust and actual failure recovery?"
  - id: C-003
    term: "no-undo commitment gate"
    meaning: "A pre-action barrier combining valid state, evidence, authority, mode awareness, and explicit confirmation."
    related_to: ["C-004", "C-005"]
    origin: inference
    next_query: "Which parts of the gate can be tested in a generic interface simulator?"
  - id: C-004
    term: "perturbation and recovery training"
    meaning: "Practice with delayed, missing, ambiguous, or contradictory system behavior followed by safe recovery and debrief."
    related_to: ["C-001", "C-002", "C-003"]
    origin: source
    next_query: "Can a synthetic event stream test recognition, escalation, and explanation?"
  - id: C-005
    term: "independent outcome verifier"
    meaning: "A check of what actually happened, separate from the interface's own report or animation."
    related_to: ["C-003", "C-004"]
    origin: local
    next_query: "What hidden state changes can verify decisions without real hardware?"

queries:
  - id: QRY-001
    text: "DoDD 3000.09 operator training capabilities limitations realistic conditions transparent feedback activate deactivate human machine interface"
    channel: web
    reason: "Find a public official statement linking training, realistic testing, transparent HMI, and safe control boundaries."
    expected_gain: "Ground the no-undo answer in public governance and engineering requirements."
    result: "The directive requires training/doctrine for capabilities and limitations, V&V/T&E, understandable HMI, transparent state feedback, and clear activation/deactivation procedures."
    next_action: "Transfer only the engineering principles to a benign simulator."
  - id: QRY-002
    text: "human autonomy teaming training trust calibration simulated remotely piloted aircraft failures"
    channel: web
    reason: "Find empirical training evidence under autonomy failures."
    expected_gain: "Separate learning controls from calibrating trust and recovery."
    result: "A 30-team study compared coordination, trust-calibration, and control training with injected failures; coordination improved some communication/performance outcomes and calibration training stabilized trust without improving every performance measure."
    next_action: "Train communication, persistence, and failure recognition together; do not treat trust scores as performance."
  - id: QRY-003
    text: "resilience human autonomy teams remotely piloted aircraft automation autonomy failure ambiguity overtrust"
    channel: web
    reason: "Understand why autonomy failures are harder to detect than visible interface failures."
    expected_gain: "Design perturbations that teach anomaly recognition before commitment."
    result: "The study reports lower resilience for autonomy failures and discusses ambiguity, overtrust, and low operator confidence as possible explanations."
    next_action: "Include behaviorally plausible but safe anomalies in the local simulator."
  - id: QRY-004
    text: "FAA crew resource management communication problem solving decision making training"
    channel: web
    reason: "Use an established high-reliability training frame for decision-making and communication."
    expected_gain: "Avoid reducing operator learning to button memorization."
    result: "FAA CRM materials connect communication, problem solving, decision making, leadership, and use of human/inanimate resources."
    next_action: "Add teach-back and debrief metrics to the prototype."

sources:
  - id: S-001
    title: "DoDD 3000.09, Autonomy in Weapon Systems"
    author_or_org: "U.S. Department of Defense"
    date: "2023-01-25"
    accessed: "2026-08-31"
    type: official
    url_or_path: "https://media.defense.gov/2023/jan/25/2003149928/-1/-1/0/dod-directive-3000.09-autonomy-in-weapon-systems.pdf"
    supports: ["CL-001", "CL-003"]
    contradicts: []
    quality: "High for public policy requirements and definitions."
    limitations: "Weapon-system policy; it is not a FARMAXIA product specification and must not be generalized silently."
  - id: S-002
    title: "The Impact of Training on Human-Autonomy Team Communications and Trust Calibration"
    author_or_org: "Johnson, Demir, McNeese, Gorman, Wolff, Cooke"
    date: "2021 online / 2023 journal issue"
    accessed: "2026-08-31"
    type: empirical
    url_or_path: "https://pubmed.ncbi.nlm.nih.gov/34595958/"
    supports: ["CL-002", "CL-004"]
    contradicts: []
    quality: "High for the reported controlled HAT training experiment."
    limitations: "Simulated RPAS task, team setting, and domain-specific failure design."
  - id: S-003
    title: "An Empirical Exploration of Resilience in Human-Autonomy Teams Operating Remotely Piloted Aircraft Systems"
    author_or_org: "Demir, McNeese, Cooke, Grimm, Gorman"
    date: "2019"
    accessed: "2026-08-31"
    type: empirical
    url_or_path: "https://doi.org/10.1177/1071181319631020"
    supports: ["CL-001", "CL-004"]
    contradicts: []
    quality: "Medium-high for resilience findings in the simulated RPAS environment."
    limitations: "Small domain-specific experiment; one degradation condition involved a simulated malicious cyber event, which is not part of the FARMAXIA prototype."
  - id: S-004
    title: "Crew Resource Management training reference library"
    author_or_org: "Federal Aviation Administration"
    date: "current library accessed 2026-08-31"
    accessed: "2026-08-31"
    type: official
    url_or_path: "https://www.faa.gov/training_testing/training/aqp/library"
    supports: ["CL-001", "CL-004"]
    contradicts: []
    quality: "High for the FAA's public training reference framing."
    limitations: "Aviation training context; not an experimental result for FARMAXIA."
  - id: S-005
    title: "Human Factors of Flight-Deck Checklists: The Normal Checklist"
    author_or_org: "NASA Ames / FAA public report"
    date: "1993"
    accessed: "2026-08-31"
    type: official
    url_or_path: "https://www.faa.gov/sites/faa.gov/files/2022-11/NASA%20Ames%20Rpt%20CR%20177549.pdf"
    supports: ["CL-003"]
    contradicts: []
    quality: "High for historical human-factors discussion of checklists and CRM."
    limitations: "Older flight-deck context; used for principle, not current system compliance."

claims:
  - id: CL-001
    statement: "Novice operator training must teach states, capabilities, limitations, anomaly recognition, and recovery—not only controls."
    status: supported
    evidence: ["S-001", "S-003", "S-004"]
    inference_notes: "The generic interface conclusion is an engineering transfer from official and empirical aviation/HAT sources."
    confidence: high
  - id: CL-002
    statement: "Trust calibration requires exposure to system limitations and should be evaluated against behavior, not self-reported trust alone."
    status: supported
    evidence: ["S-002", "S-003"]
    inference_notes: "The studies show trust and performance can move differently; calibration is not equivalent to competence."
    confidence: high
  - id: CL-003
    statement: "For irreversible actions, the practical equivalent of undo is a pre-action commitment gate plus pause, abort, or safe-state paths."
    status: partially_supported
    evidence: ["S-001", "S-005"]
    inference_notes: "The formal gate is the proposed FARMAXIA abstraction; the sources support its components, not this exact equation."
    confidence: medium
  - id: CL-004
    statement: "Perturbation training followed by debrief is more informative than perfect-path repetition for preparing recovery."
    status: partially_supported
    evidence: ["S-002", "S-003", "S-004"]
    inference_notes: "The evidence supports failure exposure and coordination practice; the exact FARMAXIA curriculum remains testable."
    confidence: medium
  - id: CL-005
    statement: "A representation layer cannot certify a person for real weapon operation; it can train and measure specific decision behaviors in a bounded simulator."
    status: supported
    evidence: ["S-001", "S-004"]
    inference_notes: "This is a scope and safety conclusion, not a claim that simulation has no transfer."
    confidence: high

models:
  - id: M-001
    kind: thesis
    statement: "FARMAXIA should treat the operator as a learner of state transitions and recovery policies, not as a faster button executor."
    assumptions: ["States and outcomes can be represented explicitly.", "The simulator can inject bounded perturbations.", "An independent verifier can score recognition and recovery."]
    predictions: ["Perturbation plus debrief will improve anomaly recognition more than perfect-path repetition.", "Visual explanation without recovery practice will not reliably improve performance."]
    evidence_for: ["CL-001", "CL-004"]
    evidence_against: []
    status: "selected for next prototype"
  - id: M-002
    kind: hypothesis
    statement: "A visible commitment gate will reduce irreversible mistakes only if its conditions are tied to evidence and a real safe alternative."
    assumptions: ["The gate cannot be bypassed silently.", "The alternate action has an observable outcome.", "Users are not trained to click through warnings automatically."]
    predictions: ["Generic confirmation dialogs will have weaker effects than contextual preconditions.", "Pause/escalate choices will improve under ambiguous events if the user practiced them."
    ]
    evidence_for: ["CL-003"]
    evidence_against: []
    status: "testable"

open_questions:
  - id: OQ-001
    question: "Which perturbations teach genuine anomaly recognition instead of making the simulator gameable?"
    why_it_matters: "A scripted training pattern can produce button memorization rather than a transferable mental model."
    next_test: "Randomize anomaly type, timing, and modality while preserving known ground truth."
    stop_condition: "Stop using a perturbation if performance depends on its visual signature rather than state evidence."
  - id: OQ-002
    question: "What independent verifier best measures a correct decision without using the same visual explanation?"
    why_it_matters: "The interface must not grade itself."
    next_test: "Use hidden synthetic state transitions and compare the chosen recovery with the known safe policy."
    stop_condition: "No claim of training benefit if the score is derived only from clicks or self-report."
  - id: OQ-003
    question: "How much friction is useful before it becomes hesitation or warning habituation?"
    why_it_matters: "A gate that interrupts everything can be bypassed or ignored."
    next_test: "Vary gate specificity and measure errors, latency, false alarms, and bypass attempts."
    stop_condition: "Reject any variant that reduces speed by increasing confusion without improving correct outcomes."

decision:
  recommendation: "Implement the six-phase benign simulator: map, routine, perturbation, ambiguity, recovery, debrief. Use OBSERVED/INFERRED/ACTIONABLE plus PAUSE/ESCALATE contracts, with an independent hidden-state verifier."
  rationale: "Official guidance and HAT experiments converge on mental models, limitations, calibrated trust, realistic perturbations, communication, testing, and transparent state feedback."
  risks: ["Simulation transfer may be weaker than supervised real-world training.", "Warnings can become decorative or habituated.", "Trust calibration may change confidence without improving performance.", "A generic layer may oversimplify domain-specific authority and consequences."]
  reversibility: "High: synthetic inputs, no external control, deterministic replay, and replaceable training scenarios."
  confidence: "high for the training architecture; medium for expected performance improvement"
  unresolved_but_accepted: ["Exact perturbation library", "Gate friction threshold", "Best independent verifier for each future domain"]
  next_review_trigger: "After the first simulator supports hidden anomalies, safe-state choices, and debrief reconstruction."
