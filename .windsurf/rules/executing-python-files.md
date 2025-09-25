---
trigger: always_on
---

When executing python files, use python3 instead of python because that adheres to project's venv. Additionally, if you haven't activated venv yet, you have to activate it or else the execution will fail with module not found exception. For this project, it's venv is in another project's, so activate it by running `source ../../doc-venv/bin/activate` - do NOT modify this command if you are willing to activate. Using bash -lc won't work, use the exact command.