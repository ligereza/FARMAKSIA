# Continuation proposal

The next bounded increment should replace the SQLite shell's local decision
store with the canonical event-store adapter, keeping the same eligibility
oracle and 090 projection contracts. Add a transport fixture only after that
adapter has restart and concurrent-writer tests. Do not connect IRIS to this
temporal state or activate XIO/LUCIDA live transport until ownership and
failure semantics are specified.
