run_id: 20260831-critical-interfaces-drones-intelligence
question: "What can public critical-system interfaces teach FARMAXIA about adaptive representation without building weapon control, covert surveillance, or autonomous action?"
decision: "Adopt an evidence-and-state representation layer as the shared technical core; use drone/intelligence systems only as public design references and benign simulation patterns."
scope: "Public official documentation, open-source repositories, and empirical human-factors research about UAS supervision, intelligence analysis, provenance, uncertainty, multimodal feedback, and task-oriented UI. Excludes targeting, intrusion, covert collection, evasion, and real-vehicle control."
acceptance_criteria:
  - "Find at least two primary or official sources describing human/system function allocation, state visibility, or task views."
  - "Find at least two established open-source projects with reusable data/interface patterns and a clear adoption boundary."
  - "Find empirical evidence about workload, correctness, uncertainty, or multimodal representation."
  - "Translate findings into a reversible FARMAXIA prototype and explicit kill tests."
effort_budget: "One focused web research pass plus local synthesis; no external corpus or model download."
status: decided

concepts:
  - id: C-001
    term: "state-evidence-action separation"
    meaning: "Keep observed state, interpretation, human action, and verified outcome as different objects and views."
    related_to: ["C-002", "C-004"]
    origin: source
    next_query: "How do established operator consoles separate monitoring, planning, and analysis?"
  - id: C-002
    term: "uncertainty as interface data"
    meaning: "Confidence, assumptions, source quality, gaps, and conflicts are displayed as part of the evidence contract."
    related_to: ["C-001", "C-003"]
    origin: source
    next_query: "Which public models preserve source lineage and distinguish raw observations from interpretations?"
  - id: C-003
    term: "correlated evidence"
    meaning: "Derived or duplicated observations sharing a root do not count as independent corroboration."
    related_to: ["C-002"]
    origin: inference
    next_query: "How should FARMAXIA represent shared roots and conflicting branches in its ledger?"
  - id: C-004
    term: "adaptive multimodal representation"
    meaning: "Visual, temporal, spatial, and optional nonvisual cues can divide attention and semantic explanation, but each needs stable meaning and a static fallback."
    related_to: ["C-001", "C-005"]
    origin: source
    next_query: "Which cue combinations improve correct belief updates without increasing workload?"
  - id: C-005
    term: "input as verification boundary"
    meaning: "Interaction is an observable event and a possible action boundary, not proof that the user understood the representation."
    related_to: ["C-001", "C-004"]
    origin: local
    next_query: "What independent outcome can verify that a representation helped?"

queries:
  - id: QRY-001
    text: "FAA UAS human factors function allocation normal/non-normal system state control station requirements"
    channel: web
    reason: "Find an official human-factors baseline for UAS interfaces."
    expected_gain: "Ground the interface problem in state awareness and human/system allocation."
    result: "FAA identifies function allocation, state awareness, distraction, observer limitations, and minimum control-station design guidelines as research issues."
    next_action: "Use as a safety/interface constraint, not as operational drone guidance."
  - id: QRY-002
    text: "QGroundControl official UI views telemetry actions logs"
    channel: web
    reason: "Inspect a high-reputation open-source operator console without adopting vehicle control."
    expected_gain: "Extract view separation, status indicators, contextual actions, and replay patterns."
    result: "QGC separates Fly, Plan, Analyze, Vehicle Configuration, and Settings; Fly combines map, telemetry, status, video, and contextual actions."
    next_action: "Reuse the separation pattern in a benign local simulator."
  - id: QRY-003
    text: "ODNI ICD 203 analytic standards uncertainty confidence source summary"
    channel: web
    reason: "Find an authoritative public model for communicating uncertainty in analysis."
    expected_gain: "Prevent visual confidence from being mistaken for truth."
    result: "ICD 203 requires expressing and explaining uncertainty, its basis, source quality, gaps, assumptions, and effects on judgments."
    next_action: "Add uncertainty and assumptions to every claim/representation contract."
  - id: QRY-004
    text: "OpenCTI observables indicators immutable objects provenance relationships official"
    channel: web
    reason: "Find a mature open-source information model separating raw observables from interpretation."
    expected_gain: "Map provenance and immutable roots to FARMAXIA evidence."
    result: "OpenCTI distinguishes immutable observables from contextual indicators and exposes knowledge, content, analyses, sightings, and history."
    next_action: "Adopt the data-model distinction, not the threat-intelligence corpus."
  - id: QRY-005
    text: "MISP official repository events attributes correlations opinions audit API"
    channel: web
    reason: "Find an open-source model for structured events, relationships, analyst perspectives, and auditability."
    expected_gain: "Identify portable structures for evidence and collaboration."
    result: "MISP provides events, attributes, objects, correlations, opinions, counter-analyses, workflow, REST API, sharing controls, and audit logging."
    next_action: "Use event/attribute/relationship patterns in synthetic fixtures only."
  - id: QRY-006
    text: "multimodal feedback human belief updating cognitive load autonomous drone 2026"
    channel: web
    reason: "Find empirical evidence linking representation modality to correctness and workload."
    expected_gain: "Keep VIZZ multimodal design grounded in measurable outcomes."
    result: "A 30-participant VR study reported faster and more reliable change reports for combined visual+haptic feedback, while haptic-only feedback showed higher cognitive load; results are controlled and correlational in interpretation."
    next_action: "Test semantic complementarity and static fallback, not vibration by default."
  - id: QRY-007
    text: "distributed unmanned assets interface positional uncertainty power communications spatiotemporal representation search rescue"
    channel: web
    reason: "Find a non-weapon multi-agent interface example emphasizing uncertainty and temporal context."
    expected_gain: "Transfer spatial/temporal status visualization without operational weapon content."
    result: "A 2021 design study represents search areas, asset positions, communication signals, power, notifications, and operator influence."
    next_action: "Prototype a timeline/map-like evidence view with no physical vehicle connection."

sources:
  - id: S-001
    title: "Unmanned Aircraft Systems Human Factors Considerations"
    author_or_org: "Federal Aviation Administration"
    date: "2015-2017 research brief"
    accessed: "2026-08-31"
    type: official
    url_or_path: "https://www.faa.gov/sites/faa.gov/files/uas/research_development/information_papers/UAS-Human-Factors-Considerations.pdf"
    supports: ["CL-001"]
    contradicts: []
    quality: "High for the official problem framing; concise research brief rather than a complete design standard."
    limitations: "UAS aviation context; does not validate FARMAXIA or generalize to all critical systems."
  - id: S-002
    title: "QGroundControl UI Overview and Fly View"
    author_or_org: "MAVLink / QGroundControl"
    date: "current documentation accessed 2026-08-31"
    accessed: "2026-08-31"
    type: repository
    url_or_path: "https://docs.qgroundcontrol.com/master/en/qgc-user-guide/getting_started/ui_overview.html"
    supports: ["CL-002"]
    contradicts: []
    quality: "High for documenting the project's own interface and architecture."
    limitations: "Project documentation is not an independent human-factors experiment."
  - id: S-003
    title: "ICD 203 Analytic Standards"
    author_or_org: "Office of the Director of National Intelligence"
    date: "2024 public copy"
    accessed: "2026-08-31"
    type: official
    url_or_path: "https://www.dni.gov/files/documents/ICD/ICD-203.pdf"
    supports: ["CL-003"]
    contradicts: []
    quality: "High for an official analytic-tradecraft standard."
    limitations: "A standard for analytic products; not a UI evaluation protocol."
  - id: S-004
    title: "Observations"
    author_or_org: "OpenCTI / Filigran"
    date: "current documentation accessed 2026-08-31"
    accessed: "2026-08-31"
    type: repository
    url_or_path: "https://docs.opencti.io/latest/usage/exploring-observations/"
    supports: ["CL-003", "CL-004"]
    contradicts: []
    quality: "High for the project's documented data model and UI behavior."
    limitations: "Threat-intelligence domain; adoption here is a pattern study only."
  - id: S-005
    title: "MISP - Threat Intelligence Sharing Platform"
    author_or_org: "MISP Project"
    date: "current repository accessed 2026-08-31"
    accessed: "2026-08-31"
    type: repository
    url_or_path: "https://github.com/MISP/MISP"
    supports: ["CL-003", "CL-004"]
    contradicts: []
    quality: "High for the project's documented event, relationship, sharing, and audit features."
    limitations: "Security-intelligence platform; no claim that its visual patterns improve human decisions in FARMAXIA."
  - id: S-006
    title: "Multimodal feedback enhances human belief updating performance and reduces cognitive load in urban drone operation"
    author_or_org: "Sun, Wu, You, Du et al.; Frontiers in Robotics and AI"
    date: "2026-06-10"
    accessed: "2026-08-31"
    type: empirical
    url_or_path: "https://doi.org/10.3389/frobt.2026.1707022"
    supports: ["CL-005"]
    contradicts: []
    quality: "Medium-high for the controlled study; explicit sample, repeated conditions, reaction time, correctness, workload, and eye-tracking measures."
    limitations: "30 participants, VR simulation, urban-drone task, and correlational interpretation of cognitive-load relationships."
  - id: S-007
    title: "User Experience Design for Human-Machine Teaming in Commanding a Distributed Constellation of Unmanned Assets in Search and Rescue"
    author_or_org: "Anderson et al.; Human Factors and Ergonomics Society"
    date: "2021"
    accessed: "2026-08-31"
    type: empirical
    url_or_path: "https://doi.org/10.1177/1071181321651130"
    supports: ["CL-006"]
    contradicts: []
    quality: "Medium for design guidance; directly discusses positional uncertainty, power, communications, notifications, and operator influence."
    limitations: "Search-and-rescue design study; not a military system and not a proof of general performance benefit."
  - id: S-008
    title: "Research 023 — open-source reference audit"
    author_or_org: "FARMAXIA local research"
    date: "2026-08-27"
    accessed: "2026-08-31"
    type: local
    url_or_path: "research/literature/023-open-source-reference-audit.md"
    supports: ["CL-002", "CL-003", "CL-007"]
    contradicts: []
    quality: "Local synthesis with explicit adoption gates and licensing cautions."
    limitations: "Not an external validation; claims must be traced back to its cited primary sources."

claims:
  - id: CL-001
    statement: "Critical operator interfaces must expose function allocation and normal/non-normal system state, not only controls."
    status: supported
    evidence: ["S-001", "S-002"]
    inference_notes: "Transfer from UAS and avionics-style supervision to a generic representation layer is an engineering inference."
    confidence: high
  - id: CL-002
    statement: "Separating monitoring, planning, configuration, analysis, and action is a mature reusable interface pattern."
    status: supported
    evidence: ["S-002"]
    inference_notes: "QGroundControl documents the pattern; performance benefit for FARMAXIA still requires testing."
    confidence: high
  - id: CL-003
    statement: "Raw observations, interpretations, confidence, assumptions, and decisions should remain distinct data objects."
    status: supported
    evidence: ["S-003", "S-004", "S-005"]
    inference_notes: "ODNI provides analytic discipline; OpenCTI/MISP provide software patterns."
    confidence: high
  - id: CL-004
    statement: "Correlated or derived evidence must not be counted as independent corroboration."
    status: partially_supported
    evidence: ["S-004", "S-005", "S-008"]
    inference_notes: "The no-double-counting rule is a provenance/inference consequence; the reviewed product docs do not constitute a FARMAXIA benchmark."
    confidence: medium
  - id: CL-005
    statement: "Complementary multimodal cues can improve correct belief updates, but abstract single-channel cues can raise workload or reduce reliability."
    status: partially_supported
    evidence: ["S-006"]
    inference_notes: "The study is controlled and domain-specific; it supports a hypothesis, not a universal prescription."
    confidence: medium
  - id: CL-006
    statement: "Spatiotemporal state, communications, resource status, notifications, and positional uncertainty are useful interface objects for multi-agent supervision."
    status: partially_supported
    evidence: ["S-007"]
    inference_notes: "The source is a design study in search and rescue; transfer to other domains remains an engineering hypothesis."
    confidence: medium
  - id: CL-007
    statement: "The best FARMAXIA shortcut is to adopt mature patterns and build a small synthetic simulator before installing large platforms or models."
    status: supported
    evidence: ["S-002", "S-004", "S-005", "S-008"]
    inference_notes: "This is a project-efficiency decision based on scope, licensing, and reversibility, not an empirical claim about all teams."
    confidence: high

models:
  - id: M-001
    kind: thesis
    statement: "FARMAXIA's common product is an evidence-and-state representation layer, not a single domain UI."
    assumptions: ["The layer can receive structured events without owning the source application.", "A verifier can measure task outcomes independently of the visual representation."]
    predictions: ["The same contracts can support VIZZ, X-ANA-X, and CODE-INE in different views.", "A prototype can be evaluated without real drones or sensitive corpora."]
    evidence_for: ["CL-001", "CL-002", "CL-003", "CL-007"]
    evidence_against: []
    status: "selected for next prototype"
  - id: M-002
    kind: hypothesis
    statement: "Adaptive multimodal cues will improve correct state updates only when each cue has stable semantics and the display preserves a static fallback."
    assumptions: ["Tasks produce measurable state-change reports.", "Cue timing and semantics can be logged.", "Workload and false alarms are measured with correctness."]
    predictions: ["Semantic visual emphasis will outperform decorative motion.", "Haptic or audio cues without an explanatory visual channel will show higher decoding cost."]
    evidence_for: ["CL-005"]
    evidence_against: []
    status: "testable"
  - id: M-003
    kind: hypothesis
    statement: "Visible provenance and conflict branches will reduce false certainty even if they increase initial interaction time."
    assumptions: ["Users can access evidence explanations on demand.", "Root identity and derivation are accurately recorded."]
    predictions: ["Users will better distinguish observation, inference, and unresolved conflict.", "A visual confidence style alone will not produce the same benefit."]
    evidence_for: ["CL-003", "CL-004"]
    evidence_against: []
    status: "testable"

open_questions:
  - id: OQ-001
    question: "Which minimal event schema can support VIZZ, X-ANA-X, and CODE-INE without becoming a universal database?"
    why_it_matters: "The schema is the actual reusable product boundary."
    next_test: "Design a synthetic fixture with state, evidence, exposure, input, and outcome events."
    stop_condition: "If one schema requires domain-specific fields for every consumer, split the contract."
  - id: OQ-002
    question: "Can adaptive salience improve correct updates without creating visual persuasion or oscillation?"
    why_it_matters: "A layer that feels clear but biases judgment is not a safe improvement."
    next_test: "Compare stable, adaptive, and decorative variants with identical underlying evidence."
    stop_condition: "Stop if false-positive rate or provenance recall worsens beyond the preregistered threshold."
  - id: OQ-003
    question: "What is the smallest independent outcome verifier for a cross-application representation?"
    why_it_matters: "Clicks and explanations are not proof that the underlying task succeeded."
    next_test: "Use hidden state changes and perturbation tasks in the local simulator."
    stop_condition: "No production claim if the outcome cannot be verified without the representation itself."
  - id: OQ-004
    question: "Which open-source component should be installed, if any, after the synthetic prototype?"
    why_it_matters: "Adoption should remove work rather than add infrastructure."
    next_test: "Compare local contracts against QGC/OpenCTI/MISP export and event patterns."
    stop_condition: "Do not install a component unless it removes a measured bottleneck and passes license/security review."

decision:
  recommendation: "Build a benign local Evidence Operations Layer using FARMAXIA contracts and a synthetic multi-sensor/event simulator. Reuse QGroundControl's view separation, OpenCTI/MISP provenance patterns, ODNI-style uncertainty fields, and the multimodal study's evaluation logic as references."
  rationale: "The sources converge on state visibility, evidence lineage, uncertainty, task-specific views, and measured human outcomes. They do not justify a weapon-control or covert-surveillance implementation."
  risks: ["Transfer from public UAS/intelligence examples to generic desktop interfaces may fail.", "Adaptive visual emphasis may persuade rather than clarify.", "A synthetic simulator may underrepresent real workload and domain complexity.", "External platforms have domain-specific schemas, licenses, and operational assumptions."]
  reversibility: "High: no external corpus, no model download, no real vehicle connection, and all proposed actions are local/synthetic."
  confidence: "high for the architectural direction; medium for performance benefits until measured locally"
  unresolved_but_accepted: ["Exact event schema", "Best cue timing and modality", "Which mature open-source dependency, if any, is worth installing"]
  next_review_trigger: "After the first simulator contract and a comparison of stable versus adaptive representation on held-out tasks."
