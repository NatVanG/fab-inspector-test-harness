# Fab Inspector Test Harness

A workspace for authoring, testing, and validating **Fab Inspector** rules against Microsoft Fabric item definitions and Fabric API calls. Use it to develop custom governance rules locally, verify them against pass/fail example items, and iterate with AI-assisted rule generation before enforcing them in CI/CD pipelines.

## Repository structure

| Folder | Purpose |
|---|---|
| `MyRules/` | Custom Fab Inspector rules. Each rule lives in its own folder with a `rule.json`, a `README.md`, and `examples/pass` and `examples/fail` Fabric item definitions for local testing. |
| `MyFabricItems/` | Place Fabric item definitions (e.g. PBIR reports, semantic models) here to scan them with your rules. |
| `.ai-assets/` | Rule schemas, example rules, and AI skills that help GitHub Copilot author and validate rules. |
| `.github/instructions/` | Copilot instruction files for CLI usage and rule authoring guidance. |

## Pre-requisites

1. **Visual Studio Code** — download from <https://code.visualstudio.com>.

2. **Fab Inspector extension** — install from the VS Code Marketplace.  
   This extension provides the `fab-inspector` CLI and the rule engine that evaluates JSONLogic-based rules against Fabric item definitions.

3. **Fabric MCP Server extension** — install from the VS Code Marketplace.  
   This extension exposes Microsoft Fabric metadata (item definitions, workload schemas, etc.) to GitHub Copilot through MCP, enabling AI-assisted rule authoring with real schema evidence.

4. **GitHub Copilot** (recommended) — the repo includes instruction files and skills that let Copilot generate, explain, and validate Fab Inspector rules using natural-language prompts.

## Quick start

1. Clone this repository and open it in VS Code.
2. Install the extensions listed above.
3. Add or edit rules under `MyRules/`. Each rule folder should contain:
   - `rule.json` — the rule definition using Fab Inspector's JSONLogic format.
   - `examples/pass/` — a Fabric item definition that should pass the rule.
   - `examples/fail/` — a Fabric item definition that should fail the rule.
4. Run a rule against an example item from the integrated terminal:

   ```powershell
   fab-inspector -fabricitem ".\MyRules\<RULE_FOLDER>\examples\pass" -rules ".\MyRules\<RULE_FOLDER>\rule.json" -verbose true
   ```

5. Place real Fabric item definitions in `MyFabricItems/` and scan them:

   ```powershell
   fab-inspector -fabricitem ".\MyFabricItems\<ITEM_FOLDER>" -rules ".\MyRules\<RULE_FOLDER>\rule.json" -verbose true
   ```

## License

See the individual extension licenses on the VS Code Marketplace for Fab Inspector and Fabric MCP Server.
