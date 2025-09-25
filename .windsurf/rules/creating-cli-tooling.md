---
trigger: model_decision
description: When creating CLI tooling
---

I prefer configuring scripts through YAML. When creating CLI tooling, "[module_name]_config.yaml", and put all config there. Secrets should be put in a `.env` file, and loaded with `dotenv.load_dotenv()`.