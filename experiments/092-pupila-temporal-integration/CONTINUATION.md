# Continuation proposal

The next bounded increment should replace the SQLite shell's local decision
store with the repository's canonical event-store adapter, keeping the same
eligibility oracle and 090 projection contracts. Add a transport fixture only
after that adapter has a restart and concurrent-writer test. Do not connect
IRIS, VIBECODEINE, VJ/LUCIDA or WACHUMA until their ownership and failure
semantics are specified.
