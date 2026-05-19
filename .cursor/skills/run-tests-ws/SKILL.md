---
name: run-tests-ws
description: run-tests-ws
disable-model-invocation: true
---

# run-tests-ws

This command will run the tests for the ws schema. It will use the port 5544 for the database.
It should be used to run the tests for the ws schema instead of running `pytest` directly.

```bash
DB_PORT=5544 ./scripts/test_local.sh ws
```
