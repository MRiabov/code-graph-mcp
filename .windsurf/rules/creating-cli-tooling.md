---
trigger: model_decision
description: When creating CLI tooling
---

1. I prefer configuring scripts through YAML. When creating CLI tooling, "[module_name]_config.yaml", and put all config there. Secrets should be put in a `.env` file, and loaded with `dotenv.load_dotenv()`.

2. When getting values from CLI tooling, I want to avoid silent failures, so instead of using dict.get() with default values use dict __getitem__ syntax. This will make it clearer when debugging configuration.