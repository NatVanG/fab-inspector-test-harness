# Fab Inspector Test Harness

A workspace for authoring, testing, and validating [**Fab Inspector**](https://github.com/NatVanG/fab-inspector) rules against Microsoft Fabric item definitions and Fabric API calls. Use it to develop custom governance rules locally, verify them against pass/fail example items, and iterate with AI-assisted rule generation before enforcing them in CI/CD pipelines.

## Repository structure

| Folder | Purpose |
|---|---|
| `fab-inspector-rules/` | Custom Fab Inspector rules. Each rule lives in its own folder with a `rule.json`, a `README.md`, and `examples/pass` and `examples/fail` Fabric item definitions for local testing. |
| `.ai-assets/` | Rule schemas, example rules, and AI skills that help GitHub Copilot author and validate rules. |
| `.github/instructions/` | Copilot instruction files for CLI usage and rule authoring guidance. |

## Pre-requisites

:note: Currently this solution only runs on win-x64.

1. **Visual Studio Code** — download from <https://code.visualstudio.com>.

2. **.NET 8+ SDK** - check which SDK's you've installed by running `dotnet --list-sdks`, if under version 8 download from <https://dotnet.microsoft.com/en-us/download>

3. **Azure CLI** - download from <https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows?view=azure-cli-latest&tabs=azure-cli&pivots=winget>

4. **Fab Inspector extension** — install from the VS Code Marketplace, see <https://marketplace.visualstudio.com/items?itemName=NatVanG.fab-inspector>  
   This extension provides the `fab-inspector` CLI to evaluate JSONLogic-based rules against Fabric item definitions and also includes the Fab Inspector MCP server.

5. **Fabric MCP Server extension** — this should get installed automatically as a dependency of the Fab Inspector extension; if not, install from the VS Code MarketPlace, see <https://marketplace.visualstudio.com/items?itemName=fabric.vscode-fabric-mcp-server>. This extension exposes Microsoft Fabric metadata (item definitions, workload schemas, etc.) to GitHub Copilot through MCP, enabling AI-assisted rule authoring with real schema evidence.

6. **GitHub Copilot** :copilot: (recommended) — the repo includes instruction files and skills that let Copilot generate, explain, and validate Fab Inspector rules using natural-language prompts.

## Quick start

1. Clone this repository and open it in VS Code.
2. Install the extensions listed above.
3. Go to the Fab Inspector extension's Settings and set the following:
   
   ![Extension settings](./docs/fab-inspector-vscodeext-settings.png  "Extension settings")

4. Start GitHub Copilot chat :copilot:
5. Select the `Fab Inspector Test Harness` agent from the Agent list (Ctrl+.), set the model to `Auto`.
6. Issue a prompt to create a new `Fab Inspector` rule. Your new rule should be created under `fab-inspector-rules/`. Each new rule folder should contain:
   - `rule.json` — the rule definition using Fab Inspector's JSONLogic format.
   - `examples/pass/` — a Fabric item definition(s) that should pass the rule.
   - `examples/fail/` — a Fabric item definition(s) that should fail the rule.
7. The agent should also then automatically run the newly created rule by invoking the Fab Inspector MCP Server's `Inspect` tool. 
8. To debug the rule manually, open the created `rules.json`, select a JSON node to inspect, right-click and select command `Fab Inspector: Log Wrap/Unwrap`. Save the file, then right-click the document and select `Fab Inspector: Run Current Rules`. The debug output will be displayed in the VS Code `Output` window.

![Rules run example](./docs/RunRules.png "Rules run example")

9. (Optionally) run a rule against a Fabric item folder from the VS Code PowerShell terminal. The Fab Inspector CLI Path can be found using the extension command ('>') `Fab Inspector: Show CLI Info`.

   ```powershell
   ./fab-inspector -fabricitem ".\fab-inspector-rules\<RULE_FOLDER>\examples\pass" -rules ".\fab-inspector-rules\<RULE_FOLDER>\rule.json" -verbose true
   ```

## Example prompts

- "Create a rule that checks if a logo/image is present in the top left hand corner of each visible report page, exclude tooltip and drillthrough pages from the test."

## License

Fab Inspector and the Fab Inspector Test Harness are released under the MIT license.