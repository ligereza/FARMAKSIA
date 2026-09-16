run_id: 20260831-un-autonomous-weapons-policy
question: "What is the UN request on autonomous weapons as of 2026-08-31, and what does it imply for FARMAXIA's human-interface layer?"
decision: "Treat the UN/ICRC call as a policy boundary: prohibit unpredictable and anti-personnel autonomous weapons, regulate other systems with meaningful human control, and translate the unresolved verification problem into a safe FARMAXIA contract for transparency, dialogue, provenance, interruption and audit."
scope: "Official UN resolutions, Secretary-General statements, UN/CCW GGE process, and high-level implications for civilian simulation and interface research. Excludes weapon tactics, targeting, real-system control, covert surveillance, and autonomous force."
acceptance_criteria:
  - "Distinguish political calls, General Assembly resolutions, and a binding treaty."
  - "Verify the latest 2025 resolution and August 2026 UN/ICRC appeal."
  - "Record what remains unresolved in the CCW/GGE process."
  - "Define a safe, non-weapon experiment that tests meaningful human control as an interface property."
effort_budget: "Focused official-source research and repository record; no software installation or external integration."
status: decided

concepts:
  - id: C-001
    term: "meaningful human control"
    meaning: "Human involvement must be informed, predictable, temporally sufficient, and capable of changing the outcome; a decorative confirmation is insufficient."
    related_to: ["C-002", "C-003", "C-004"]
    origin: source_and_inference
    next_query: "Which observable interface metrics distinguish meaningful control from rubber-stamping?"
  - id: C-002
    term: "two-tier approach"
    meaning: "Prohibit systems that are inherently unacceptable or cannot comply with international humanitarian law; impose positive restrictions and safeguards on other autonomous systems."
    related_to: ["C-001", "C-005"]
    origin: source
    next_query: "How can a software contract encode prohibitions and positive obligations without claiming legal certification?"
  - id: C-003
    term: "unpredictability"
    meaning: "The operator cannot anticipate or limit the outcome of force, making meaningful control and legal compliance impossible."
    related_to: ["C-001", "C-002"]
    origin: source
    next_query: "How should an interface expose predictive uncertainty and abstain before an irreversible commitment?"
  - id: C-004
    term: "attention versus authority"
    meaning: "Gaze, pointer, keyboard and adaptive rendering may guide attention, but must not silently authorize an irreversible action."
    related_to: ["C-001", "C-006"]
    origin: inference
    next_query: "Can the same input be used for navigation while requiring a distinct commitment gesture?"
  - id: C-005
    term: "human accountability"
    meaning: "The system must preserve who or what had authority, what was known, what was proposed, and what was confirmed."
    related_to: ["C-001", "C-006"]
    origin: source_and_inference
    next_query: "What minimum provenance fields make an interface decision replayable?"
  - id: C-006
    term: "safe-domain transfer"
    meaning: "Validate the interface contract in civilian, industrial or rescue simulation before considering any higher-risk domain."
    related_to: ["C-004", "C-005"]
    origin: decision
    next_query: "Which non-lethal simulator best tests ambiguity, escalation and interruption?"

queries:
  - id: QRY-001
    text: "UN Secretary-General ICRC renewed call autonomous weapons 27 August 2026 unpredictable anti-personnel"
    channel: web
    reason: "Verify the latest public request and its two prohibition categories."
    expected_gain: "Ground the current policy summary in a primary UN source."
    result: "UN Egypt press release reports the renewed call for a legally binding instrument, prohibitions for unpredictable systems and systems targeting humans, and restrictions for other systems."
    next_action: "Use as the current political position, not as a treaty."
  - id: QRY-002
    text: "A/RES/79/62 lethal autonomous weapons systems human role responsibility accountability two-tier"
    channel: web
    reason: "Verify the latest fully accessible General Assembly resolution before the 2025 record."
    expected_gain: "Separate adopted resolution language from Secretary-General advocacy."
    result: "Resolution affirms applicability of international law, says weapons incompatible with IHL must not be used, stresses human responsibility and notes a two-tier approach."
    next_action: "Translate into a FARMAXIA interface contract, without claiming legal compliance."
  - id: QRY-003
    text: "A/RES/80/57 lethal autonomous weapons systems 2025 vote"
    channel: web
    reason: "Check whether the General Assembly continued the item in the 80th session."
    expected_gain: "Avoid presenting 2024 as the latest resolution."
    result: "A/RES/80/57 was adopted 2025-12-01 with vote summary 164-6-7."
    next_action: "Record the continued political process and lack of treaty."
  - id: QRY-004
    text: "UN CCW GGE LAWS 2026 session elements instrument without prejudging nature"
    channel: web
    reason: "Check current negotiation status and whether a final legal instrument exists."
    expected_gain: "State accurately what remains unresolved."
    result: "The 2026 GGE session runs 31 August–4 September and continues formulating elements of an instrument without prejudging its nature."
    next_action: "Treat definition, legal form and verification threshold as open questions."

sources:
  - id: S-001
    title: "UN chief, Red Cross renew call for rules on lethal autonomous weapons"
    author_or_org: "United Nations in Egypt"
    date: "2026-08-27"
    accessed: "2026-08-31"
    type: official
    url_or_path: "https://egypt.un.org/en/321747-un-chief-red-cross-renew-call-rules-lethal-autonomous-weapons"
    supports: ["CL-001", "CL-002", "CL-003"]
    contradicts: []
    quality: "High for the latest public UN/ICRC call; a press release, not a treaty text."
    limitations: "Reports the political appeal and quoted principles; it does not establish universal legal obligations."
  - id: S-002
    title: "A/RES/79/62 Lethal autonomous weapons systems"
    author_or_org: "United Nations General Assembly"
    date: "2024-12-02"
    accessed: "2026-08-31"
    type: official
    url_or_path: "https://documents.un.org/doc/undoc/gen/n24/391/35/pdf/n2439135.pdf"
    supports: ["CL-001", "CL-002", "CL-005"]
    contradicts: []
    quality: "High for the adopted resolution and its operative paragraphs."
    limitations: "A General Assembly resolution is not the requested binding treaty."
  - id: S-003
    title: "A/RES/80/57 Lethal autonomous weapons systems"
    author_or_org: "United Nations General Assembly, 80th session"
    date: "2025-12-01"
    accessed: "2026-08-31"
    type: official_record
    url_or_path: "https://digitallibrary.un.org/record/4095989?ln=en&v=%5B%27pdf%27%5D"
    supports: ["CL-006"]
    contradicts: []
    quality: "High for existence, date and vote summary of the latest located resolution."
    limitations: "The accessible record metadata alone does not provide the full operative text in this pass."
  - id: S-004
    title: "2026 Group of Governmental Experts on LAWS, second session"
    author_or_org: "United Nations Office for Disarmament Affairs"
    date: "2026-08-31 to 2026-09-04"
    accessed: "2026-08-31"
    type: official_process
    url_or_path: "https://indico.un.org/event/1019358/"
    supports: ["CL-006"]
    contradicts: []
    quality: "High for the public meeting schedule and process description."
    limitations: "An ongoing meeting cannot establish its final outcome before the report is adopted."
  - id: S-005
    title: "A/79/88 Report of the Secretary-General on lethal autonomous weapons systems"
    author_or_org: "United Nations"
    date: "2024"
    accessed: "2026-08-31"
    type: official_compilation
    url_or_path: "https://documents.un.org/doc/undoc/gen/n24/154/32/pdf/n2415432.pdf"
    supports: ["CL-002", "CL-004"]
    contradicts: ["CL-002"]
    quality: "High for the record of submitted state and stakeholder positions; useful for mapping convergence and disagreement."
    limitations: "It compiles views and is not itself a consensus legal standard."

claims:
  - id: CL-001
    statement: "As of 2026-08-31, the UN/ICRC position is an urgent political call to negotiate a legally binding instrument, not an already adopted universal treaty."
    status: supported
    evidence: ["S-001", "S-002", "S-003", "S-004"]
    inference_notes: "The distinction follows from the appeal's request to begin negotiations and the continuing GGE process."
    confidence: high
  - id: CL-002
    statement: "The emerging two-tier direction is to prohibit systems that are unpredictable or target humans autonomously and regulate other systems with meaningful human control, restrictions and accountability."
    status: supported_with_open_details
    evidence: ["S-001", "S-002", "S-005"]
    inference_notes: "The exact legal definitions, scope and positive obligations remain under negotiation."
    confidence: high
  - id: CL-003
    statement: "A visible human confirmation is not sufficient if the person cannot understand the state, anticipate the result or intervene in time."
    status: partially_supported_inference
    evidence: ["S-001", "S-005"]
    inference_notes: "This is an engineering interpretation of the control, predictability and accountability principles, not a judicial test."
    confidence: medium
  - id: CL-004
    statement: "FARMAXIA can contribute to the unresolved verification problem through provenance, uncertainty display, bounded dialogue, distinct attention/authority inputs and replayable interruption records."
    status: design_hypothesis
    evidence: ["S-001", "S-002", "S-005"]
    inference_notes: "This does not certify a weapon or institution as lawful; it is a safe interface research direction."
    confidence: medium
  - id: CL-005
    statement: "In FARMAXIA, gaze, pointer and adaptive rendering should guide attention but not silently authorize irreversible action."
    status: design_decision
    evidence: ["S-001", "S-002"]
    inference_notes: "This is a project safety and usability boundary derived from the human-control problem."
    confidence: high
  - id: CL-006
    statement: "The definition, legal form and final verification threshold for a future instrument remain unresolved in the public process reviewed here."
    status: supported
    evidence: ["S-003", "S-004", "S-005"]
    inference_notes: "The ongoing GGE mandate explicitly does not prejudge the nature of the instrument."
    confidence: high

models:
  - id: M-001
    kind: thesis
    statement: "The strongest safe FARMAXIA contribution is a human-control and decision-transparency layer validated in non-lethal simulation, not a weapon-control adapter."
    assumptions: ["The host exposes state/evidence or can be instrumented in a simulator.", "The layer can preserve an explicit distinction between attention and authority.", "Evaluation includes ambiguity and interruption, not only speed."]
    predictions: ["Users will detect ambiguous states more often when evidence and uncertainty are visible.", "Progress-preserving dialogue will reduce unsafe guessing without requiring camera input."]
    evidence_for: ["CL-003", "CL-004", "CL-005"]
    evidence_against: []
    status: selected
  - id: M-002
    kind: falsifiable_experiment
    statement: "A transparency-plus-confirmation renderer will outperform recommendation-only display on state recognition and calibrated hold/escalate decisions, at acceptable interaction cost."
    assumptions: ["The simulator provides a known ground truth.", "Ambiguity is represented explicitly.", "The confirmation gate is distinct from attention navigation."]
    predictions: ["Fewer false certainties.", "More correct escalations under contradictory evidence.", "Higher audit completeness."]
    evidence_for: []
    evidence_against: []
    status: testable

open_questions:
  - id: OQ-001
    question: "What observable metrics distinguish meaningful human control from a rubber-stamp confirmation?"
    why_it_matters: "The term is central to policy but cannot remain a visual label."
    next_test: "Measure state recall, prediction of consequences, intervention before commitment and correction after perturbation in a safe simulator."
    stop_condition: "Do not claim meaningful control if users confirm without being able to predict or alter the result."
  - id: OQ-002
    question: "How should the layer behave when the model is fast but its state is not predictable?"
    why_it_matters: "Speed can increase risk when it hides uncertainty."
    next_test: "Compare continue, hold and escalate policies under controlled ambiguity."
    stop_condition: "Reject any policy that reduces visible uncertainty or penalizes correct abstention."
  - id: OQ-003
    question: "Which non-lethal domain best exposes the same interface failure without crossing into weapon enablement?"
    why_it_matters: "The experiment needs consequential decisions without real-world harm."
    next_test: "Compare rescue coordination, industrial inspection and hospital kiosk simulation."
    stop_condition: "Choose the domain with clear ground truth, reversible actions and no operational access."

decision:
  recommendation: "Adopt a cross-project contract for meaningful human control: provenance, evidence/uncertainty, bounded dialogue, distinct attention and authority inputs, explicit commit, interruption, handoff and replay. Validate it first in a non-lethal simulator."
  rationale: "The current UN process treats human judgment, accountability, predictability and legal compliance as central while leaving definitions and the final instrument unresolved. That gap is a valid research problem for FARMAXIA."
  risks: ["A policy label could be mistaken for legal certification.", "Adaptive visual emphasis could hide important warnings.", "A fast confirmation flow could turn the human into a rubber stamp.", "A military framing could drift into operational enablement."]
  reversibility: "High: simulated domain, typed event log, no external actuation, and replaceable rendering policy."
  confidence: "high for the policy distinction; medium for the proposed interface metrics"
  unresolved_but_accepted: ["Final treaty text", "Universal definition of autonomy", "Formal threshold for meaningful human control", "Best non-lethal simulator domain"]
  next_review_trigger: "After the first safe simulator compares recommendation-only, transparent confirmation, and transparent confirmation plus dialogue/handoff."
