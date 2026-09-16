# Delegation decision - 20260902-tool-adoption-stack

role: primary_agent
delegation_scope: prepare XIO and MOSAIK inputs for a future LUCIDA Python engine without implementing the engine in their repositories
delegation_authority: user has previously authorized autonomous work by the XIO and MOSAIK agents; this record does not dispatch them yet
nested_delegation: false

## Objective

Reduce integration rework by allowing each domain repository to prepare its
own stable input contract while the primary agent owns the shared LUCIDA
engine and final integration.

## Decision

Use two narrow preparatory tasks, not broad autonomous feature work:

- XIO prepares a host-neutral event catalog, redaction boundary and replay fixture.
- MOSAIK prepares a host-neutral show projection and preview-candidate fixture.

Neither task may add an overlay, import LUCIDA, add VIZZ/PUPILA semantics,
open a network transport or install a new dependency merely for exploration.

## Acceptance boundary

Each delegated result must include:

- exact branch and commit;
- English ASCII contract identifiers;
- one replayable fixture;
- tests for ordering, redaction and invalid input;
- declared consumer and producer;
- no assets, credentials, raw media or private user data;
- full suite result and a documented stop condition.

The primary agent will review the published commit once, then decide whether
the contract is suitable for `lucida_engine`. No code is merged automatically.

## Cost comparison

| option | expected benefit | main risk | decision |
|---|---|---|---|
| primary agent builds the complete engine first | fast central implementation | engine shape may not fit real XIO/MOSAIK events | reject as first move |
| agents continue broad autonomous work | more activity | scope drift, duplicate semantics and expensive review | reject |
| agents prepare narrow inputs while primary builds the reducer | parallel information and bounded integration | requires a frozen contract and one review | select |

## Review cost

The review is limited to contract shape, fixture replay, tests, dependency
changes and boundary violations. If a result requires reconstructing the
whole domain project, it is not accepted as a delegation success.
