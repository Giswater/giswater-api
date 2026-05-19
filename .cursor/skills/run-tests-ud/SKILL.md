---
name: run-tests-ud
description: run-tests-ud
disable-model-invocation: true
---

# run-tests-ud

This command will run the tests for the ud schema. It will use the port 5544 for the database.
It should be used to run the tests for the ud schema instead of running `pytest` directly.

```bash
DB_PORT=5544 ./scripts/test_local.sh ud
```
