| name | fab-inspector-rules |
|------|---------------------|
| description | Author Fab Inspector rules using JSONLogic to test Microsoft Fabric item definitions. Activate when users need to write, edit, debug, or understand inspection rules, operators, or the rule file format. |

# Fab Inspector Rule Authoring

This skill provides comprehensive guidance for writing Fab Inspector rules — deterministic, JSONLogic-based tests that validate Microsoft Fabric item definitions.

## 0 — Fabric MCP grounding

Use the local Fabric MCP server tools to verify rule accuracy:

- `docs_item_definitions` — validate `itemType`, `part`, `var`, JSON Pointer paths, and payload shapes.
- `docs_platform_api_spec` — verify core Fabric platform API endpoints for `apiget` rules only.
- `docs_workload_api_spec` — verify workload-specific API endpoints and payloads for `apiget` rules only.

If Fabric MCP tools are unavailable, install via [the official instructions](https://github.com/microsoft/mcp/blob/main/servers/Fabric.Mcp.Server/README.md#installation) before authoring rules.

## 1 — Rules file structure

A rules file is a JSON document containing a `rules` array:

```json
{
  "rules": [
    { /* rule 1 */ },
    { /* rule 2 */ }
  ]
}
```

*Important*: Adhere to this JSON schema when authoring rules: [fab-inspector-rules.schema.json](..\..\RuleSchemas\fab-inspector-rules.schema.json) and add a local $schema reference at the top of the file for validation in supported editors:

```json
{
  "$schema": "../.ai-assets/RuleSchemas/fab-inspector-rules.schema.json",
  "rules": [
    {
      "id": "SIMPLEST_RULE",
      "name": "Simplest Rule",
      "test": [true, true]
    }
  ]
}
```

### Minimal rule example

```json
{
  "id": "SIMPLEST_RULE",
  "name": "Simplest Rule",
  "test": [
    true,
    true
  ]
}
```

### Rule properties

| Property | Required | Default | Description |
|----------|----------|---------|-------------|
| `id` | Yes | — | Unique identifier (e.g. `"CHECK_THEME_NAME"`). Used in output and CI/CD. |
| `name` | Yes | — | Human-readable name displayed in results. |
| `description` | No | — | Explanation of what the rule validates and the returned value or ojects. *Important*: Ensure that the description is actionable so that an agent has clear but concise instructions on how to fix the issue. |
| `test` | Yes | — | Test definition array (see Section 3). |
| `itemType` | No | — | Fabric item type(s) to target. Use `\|` to combine (see Section 6). |
| `part` | No | — | Part iterator selector (see Section 2). |
| `disabled` | No | `false` | When `true`, the rule is skipped. |
| `logType` | No | `"warning"` | Severity: `"error"`, `"warning"`. |
| `applyPatch` | No | `false` | When `true` and a `patch` is defined, auto-fix is applied. |
| `patch` | No | — | Deprecated - Auto-fix definition (see Section 7). |
| `pathErrorWhenNoMatch` | No | `false` | When `true`, raises an error if the part iterator matches no files. |

## 2 — The `part` iterator

The `part` property controls **which files or parts** the rule runs against. If a part matches multiple items, the rule runs iteratively against each one. Only use the `part` property when you want to display separate test results for each iteration, otherwise use a part operator within the test logic to access multiple parts in the same test.

### Reserved Report part names (case-sensitive)

When `itemType` is `Report`, these reserved names are available:

| Part name | Returns |
|-----------|---------|
| `Report` | The `report.json` file content |
| `ReportExtensions` | The `reportExtensions.json` file content |
| `Pages` | List of all `*.page.json` files (iterates each page) |
| `PagesHeader` | The `pages.json` collection header |
| `AllPages` | All pages as a single array |
| `Visuals` | Visual files (`*.visual.json`) in the context of the current part iterator |
| `AllVisuals` | All visuals across the entire report |
| `MobileVisuals` | Mobile visual files (`*.mobile.json`) in the current part context |
| `AllMobileVisuals` | All mobile visuals across the report |
| `Bookmarks` | Bookmark files (`*.bookmark.json`) in the current part context |
| `BookmarksHeader` | The `bookmarks.json` collection header |
| `AllBookmarks` | All bookmarks across the report |
| `Files` | List of all files within the parent part context |

### Regex-based file matching

For non-Report item types (or to match specific files within any item), use a **regular expression**. Folder separators are normalised to the colon character (`:`) for cross-platform compatibility.

```json
"part": "copyjob-content.json"
```

Matches any path ending in `copyjob-content.json`.

```json
"part": "folder1:.*:copyjob-content\\.json$"
```

Matches `copyjob-content.json` files under any subfolder of `folder1`.

This colon-based normalisation means:
- Windows path `C:\fabricproject\folder1\copyjob1.CopyJob\copyjob-content.json`
- Linux path `/home/fabricproject/folder1/copyjob1.CopyJob/copyjob-content.json`

Both match `folder1:.*:copyjob-content.json`.

### File extension matching

```json
"part": ".pq$"
```

Matches all PowerQuery files. Useful for Dataflow inspections.

```json
"part": ".sql"
```

Matches all SQL files. Useful for SQLDatabase inspections.

## 3 — Test definition

A test is an array with **2 or 3 elements**:

```json
"test": [
  { /* logic (JSONLogic expression) */ },
  { /* data mapping (optional) */ },
  /* expected result */
]
```

| Element | Required | Description |
|---------|----------|-------------|
| Logic | Yes | A JSONLogic expression that produces a result. |
| Data mapping | No | Named variables bound via JSON Pointer paths starting with the '/' character; these variables are then available via the `var` operator in the logic expression. JSONLogic expressions cannot be evaluated in here. Data mapping can be omitted (2-element test). |
| Expected result | Yes | The value the logic must produce for the test to pass. |

The test **passes** when the logic output matches the expected result exactly.

### The `var` operator

The `var` operator accesses values from the current JSON context:

```json
{ "var": "displayName" }
```

Access nested properties with dot notation:

```json
{ "var": "properties.jobMode" }
```

An empty `var` returns the root item:

```json
{ "var": "" }
```

### Data mapping (optional second element)

A good use case for data mapping is to bind variables to hardcoded Json objects, arrays or values such a list of allowed visual types, expected property values, or other constants that are referenced multiple times in the logic.

```json
{
  "axisRoles": [
            "X",
            "Y",
            "Category",
            "Series",
            "SecondaryX",
            "SecondaryY"
          ]
}
```

Once defined in the data mapping, these variables can be accessed in the logic with `var`:

```json
{ "var": "axisRoles" }
```

*Important*: You cannot use JSONLogic operators in the data mapping.

### Expected result patterns

| Pattern | Meaning |
|---------|---------|
| `true` | Boolean assertion |
| `"someString"` | Exact string match |
| `4` | Exact numeric match |
| `[]` | Empty array — "no failures found" (most common for filter-based rules) |
| `["a", "b"]` | Exact array match |
| `{ "key": "val" }` | Exact object match |

**Best practice**: Design rules to return an **array of failing items** (e.g., visual names or item IDs) with an expected result of `[]`. This makes results actionable — you see exactly what failed. If the rule only returns `true`/`false`, you know something is wrong but not what.

## 4 — Built-in JSONLogic operators

All [standard JSONLogic operators](https://jsonlogic.com/operations.html) are available (comparison, logic, arithmetic, array, string, data access). The [JsonLogicExamples.json](JsonLogicExamples.json) file contains worked examples as an array of arrays each in the form of [expression, data, result]. Operator signatures and argument types are defined in the [JSONLogic schema](../../RuleSchemas/fab-inspector-jsonlogic.schema.json).

## 5 — Custom operators reference

Fab Inspector adds these custom operators beyond standard JSONLogic. Grouped by category. These are also defined in the [JSONLogic schema](../../RuleSchemas/fab-inspector-jsonlogic.schema.json) with signatures and argument types.

### Navigation operators

#### `part`
Returns file content of a Fabric item definition within the `test` logic part, use it to access specific parts. A part set to an empty string (`""`) refers to the current part from the rule-level iterator.

```json
{ "part": "Visuals" }
{ "part": "Pages" }
{ "part": "Report" }
{ "part": "copyjob-content.json" }
{ "part": "" }           // Current part (from rule-level iterator)
```

#### `partinfo`
Similar to the `part` operator but returns metadata about a part instead of its content. Metadata includes:

```json
{
  "filesystemname": "Date.sql",
  "filesystempath": "C:\\...\\dbo\\Tables\\Date.sql",
  "partfilesystemtype": "File",
  "filesize": 1030,
  "filecount": 1
}
```

Usage: `{ "partinfo": "" }` returns metadata for the current part.

#### `query`
Applies an operator to the output of another operator. This is useful when a single Json object is returned instead of an array. Takes two parameters: the output of the first operator and the operator to apply.

```json
{
  "query": [
    { "part": "Version" },
    { "var": "version" }
  ]
}
```

#### `path`
JSONPath expression to query the current context. Uses [JsonPath.Net](https://docs.json-everything.net/path/basics/) / [RFC 9535](https://www.rfc-editor.org/rfc/rfc9535.html) syntax.

```json
{ "path": "$..projections[*]" }
{ "path": "$.*.properties.jobMode" }
```

*Impportant* To apply a JSONPath to a specific data node use in conjunction with the `query` operator:

```json
{ "query": [ {  "var": "response" }, { "path": "$.value[*].displayName" } ] }
```

#### `drillvar`
Parses stringified JSON on the right of a `>` character in a JSON pointer path. Useful for querying escaped JSON (e.g., Deneb custom visual definitions).

### Set operators

#### `diff`
Set difference: returns items in the first array that are not in the second.

```json
{ "diff": [["a","b","c","d"], ["d","c"]] }
// Result: ["a","b"]
```

#### `equalsets`
Tests if two arrays are equal as unordered sets.

```json
{ "equalsets": [["a","b","c"], ["c","a","b"]] }
// Result: true
```

#### `intersection`
Set intersection: returns items present in both arrays.

```json
{ "intersection": [["a","b","c","d"], ["d","c","f","e"]] }
// Result: ["c","d"]
```

#### `symdiff`
Symmetric difference: returns items in either array but not in both.

```json
{ "symdiff": [["a","b","c","d"], ["d","c","f","e"]] }
// Result: ["a","b","f","e"]
```

#### `union`
Set union: returns all unique items from both arrays.

```json
{ "union": [["a","b","c","d"], ["d","c","f","e"]] }
// Result: ["a","b","c","d","f","e"]
```

### String operators

#### `strcontains`
Counts regex matches in a string. Returns the match count.

```json
{ "strcontains": ["The quick brown brown fox", "brown"] }
// Result: 2
```

#### `strsplit`
Splits a string by a delimiter. Returns an array.

```json
{ "strsplit": [{ "var": "name" }, ","] }
```

#### `strjoin`
Joins an array of strings with a separator.

```json
{ "strjoin": [["a", "b", "c"], ","] }
// Result: "a,b,c"
```

#### `regexextract`
Extracts matches from a string using a regex pattern. Optionally returns a specific capture group instead of the full match.

```json
{ "regexextract": [{ "var": "sourceText" }, "\\b[A-Z]{2,}\\b"] }
```

```json
{ "regexextract": [{ "var": "sourceText" }, "(\\w+)@(\\w+)", 2] }
// Returns group 2 matches only
```

#### `tostring`
Converts a JSON node to its stringified JSON representation.

```json
{ "tostring": [["a","b","c","d"]] }
// Result: "[\"a\",\"b\",\"c\",\"d\"]"
```

### Data operators

#### `count`
Counts items in an array.

```json
{ "count": [["a","b","c","d"]] }
// Result: 4
```

#### `torecord`
Constructs a JSON record from key/value pairs.

```json
{
  "torecord": [
    "isPersistentUserStateDisabled", { "var": "/settings/isPersistentUserStateDisabled" },
    "hideVisualContainerHeader", { "var": "/settings/hideVisualContainerHeader" }
  ]
}
```

#### `distinct`
Returns unique values from an array.

```json
{ "distinct": [["a", "b", "a", "c", "b"]] }
// Result: ["a", "b", "c"]
```

```json
{ "distinct": [["page1", "page2", "page1", "page3"]] }
// Result: ["page1", "page2", "page3"]
```

#### `keys`
Returns the keys of a JSON object.

```json
{ "keys": [{ "name": "Sales", "type": "barChart" }] }
// Result: ["name", "type"]
```

```json
{ "keys": [{ "x": 10, "y": 20, "width": 300 }] }
// Result: ["x", "y", "width"]
```

#### `values`
Returns the values of a JSON object.

```json
{ "values": [{ "name": "Sales", "type": "barChart" }] }
// Result: ["Sales", "barChart"]
```

```json
{ "values": [{ "x": 10, "y": 20, "width": 300 }] }
// Result: [10, 20, 300]
```

#### `typeof`
Returns the type of a JSON node as a string.

```json
{ "typeof": [{ "part": "Pages" }] }
// Result: "array"
```

```json
{ "typeof": [{ "var": "displayName" }] }
// Result: "string"
```

#### `hasprop`
Checks if a JSON object has a specific property.

```json
{ "hasprop": [{ "var": "visual" }, "objects"] }
// Result: true
```

```json
{ "hasprop": [{ "name": "AxisBar", "visualType": "barChart" }, "subtitle"] }
// Result: false
```

#### `isnullorempty`
Tests whether a value is null or empty.

```json
{ "isnullorempty": [""] }
// Result: true
```

```json
{ "isnullorempty": [["AxisBar"]] }
// Result: false
```

#### `coalesce`
Returns the first non-null value from a array of expressions. There is no concept of fallback value for this operator.

```json
{ "coalesce": [null, "", "fallback"] }
// Result: ""
```

```json
{ "coalesce": [null, { "var": "subtitle" }, "Untitled visual"] }
// Result: "Untitled visual"
```

#### `slice`
Extracts a slice of an array (start/end indices). Supports negative indices (counting from the end).

```json
{ "slice": [["a", "b", "c", "d"], 1, 3] }
// Result: ["b", "c"]
```

```json
{ "slice": [["Page 1", "Page 2", "Page 3", "Page 4"], -2] }
// Result: ["Page 3", "Page 4"]
```

### Variable binding

#### `let`
Binds computed values to named variables for reuse within the same expression. Avoids duplicate computation (e.g., multiple API calls). The binding behaviour is as follows:
1. Earlier bindings are available to later bindings in the same let.
2. Existing input fields are still visible.
3. Bound names still shadow existing fields with the same name.

**Basic binding:**

```json
{
  "let": [
    { "items": { "path": "$.visuals[*].name" } },
    { "count": [{ "var": "items" }] }
  ]
}
```

**Multiple bindings:**

```json
{
  "let": [
    {
      "themeName": { "var": "themeCollection.baseTheme.name" },
      "version": { "var": "version" }
    },
    {
      "strjoin": [
        [{ "var": "themeName" }, " @ v", { "var": "version" }],
        ""
      ]
    }
  ]
}
```

**Avoid duplicate API calls:**

```json
{
  "let": [
    {
      "response": { "apiget": ["https://api.fabric.microsoft.com/v1/admin/tenantsettings", "{context-token}"] }
    },
    {
      "and": [
        { "!": [{ "isnullorempty": [{ "var": "response" }] }] },
        { "==": [{ "path": ["$.tenantsettings[?(@.settingName=='AllowSPNs')].enabled", { "var": "response" }] }, true] }
      ]
    }
  ]
}
```

### File system operators

#### `filesize`
Returns file size in bytes. Accepts a file path string or the output of `partinfo`.

```json
{ "filesize": [{ "partinfo": "" }] }
```

#### `filetextsearchcount`
Counts regex matches in a file's text content. Takes a file path (or `partinfo` output) and a regex pattern.

```json
{ "filetextsearchcount": [{ "partinfo": "" }, "ErrorLogID"] }
```

#### `fromyamlfile`
Reads and parses a YAML file, returning its content as JSON.

```json
{ "fromyamlfile": ["config.yaml"] }
// Result: { "environment": "production", "debug": false, "timeout": 30 }
```

```json
{ "fromyamlfile": ["settings.yaml"] }
// Result: { "regions": ["us-east", "us-west"], "replicas": 3, "version": "2.1" }
```

### Date/time operators

#### `now`
Returns the current UTC date/time.

```json
{ "now": [] }
// Result: "2026-04-29T14:32:18.123Z"
```

```json
{ "now": [-7, "days"] }
// Result: "2026-04-22T14:32:18.123Z"
```

#### `datediff`
Calculates the difference between two dates.

```json
{ "datediff": ["2026-04-01T10:00:00Z", "2026-04-29T10:00:00Z", "days"] }
// Result: 28
```

```json
{ "datediff": [{ "var": "createdDate" }, { "now": [] }, "hours"] }
// Result: 168
```

### Layout operators

#### `rectoverlap`
Detects overlapping visuals on a report page. Takes an array of rectangle records (with `name`, `x`, `y`, `width`, `height` properties) and an optional margin width.

```json
{
  "rectoverlap": [
    {
      "map": [
        { "filter": [{ "part": "Visuals" }, { /* visibility checks */ }] },
        {
          "torecord": [
            "name", { "var": "name" },
            "x", { "var": "position.x" },
            "y", { "var": "position.y" },
            "width", { "var": "position.width" },
            "height", { "var": "position.height" }
          ]
        }
      ]
    },
    5
  ]
}
```

### REST API operators (require non-local auth)

#### `daxquery`
Executes a DAX query against a Semantic Model via the Power BI ExecuteQueries API. Returns the query result. Supports a simple string form (uses `{context-fabricworkspace}` and `{context-fabricitem}`) or an array form with explicit parameters.

```json
{ "daxquery": "EVALUATE VALUES('Employee Country')" }
```

Array form: `[query, workspaceId, semanticModelId, includeNulls, impersonatedUserName]`

```json
{
  "daxquery": [
    "EVALUATE VALUES('Product'[Category])",
    "f45498e6-9f62-4bbb-bdb6-6d8a7e3a2703",
    "6a496a15-d00c-4cd6-a731-a3fd79e8fb10",
    true,
    "analyst@contoso.com"
  ]
}
```

#### `apiget`
Performs an authenticated HTTP GET against any supported Power BI or Fabric REST API endpoint and returns the parsed JSON response.

Supported API surfaces:
- Any GET endpoint under `https://api.powerbi.com/v1.0/myorg/...`
- Any GET endpoint under `https://api.fabric.microsoft.com/v1/...`

There is no path-level whitelist in the operator. If the URL starts with one of those two base URLs, Fab Inspector will issue the GET request with the correct access token scope for that host.

Supported forms:

```json
{ "apiget": "https://api.powerbi.com/v1.0/myorg/groups/{context-fabricworkspace}/reports" }
```

```json
{
  "apiget": [
    "https://api.fabric.microsoft.com/v1/workspaces/{context-fabricworkspace}/items?type={type}&recursive={recursive}",
    "Lakehouse",
    "true"
  ]
}
```

How URL resolution works:
- `{context-fabricworkspace}` is replaced with the workspace GUID from the current CLI/runtime context.
- `{context-fabricitem}` is replaced with the current item GUID from the CLI/runtime context.
- Any remaining placeholders such as `{type}`, `{recursive}`, `{itemId}`, `{reportId}` are filled sequentially from the array arguments in the order the placeholders appear in the URL.
- Placeholder names are descriptive only; substitution is positional, not name-based.
- Query-string placeholders are supported the same way as path placeholders.

Authentication and runtime behavior:
- Requires non-local authentication and a configured `HttpClient`/token provider.
- Fab Inspector adds the bearer token in the request header; do not use `{context-token}` inside the URL template.
- Only HTTP GET is supported by this operator.
- The response body must be JSON; the operator parses and returns it as a JSON node.
- Continuation tokens and pagination are not handled automatically. Use `apiget` for single-page endpoints, or endpoints where the first page is sufficient for the rule.
- Unsupported hosts throw an error before the request is sent.

Common GET patterns the skill should understand when authoring rules:
- Power BI workspace inventory, such as `/groups/{context-fabricworkspace}/reports`, `/datasets`, `/dashboards`, `/dataflows`
- Power BI admin/read APIs that are available through GET
- Fabric workspace/item inventory, such as `/workspaces/{context-fabricworkspace}/items`
- Fabric item metadata/settings endpoints, such as `/workspaces/{context-fabricworkspace}/onelake/settings`
- Fabric resource collections filtered by query-string parameters, such as `?type=Lakehouse&recursive=true`

```json
{ "apiget": "https://api.powerbi.com/v1.0/myorg/groups/{context-fabricworkspace}/reports" }
```

With explicit parameters:

```json
{
  "apiget": [
    "https://api.fabric.microsoft.com/v1/workspaces/{context-fabricworkspace}/items?type={type}&recursive={recursive}",
    "Lakehouse",
    "true"
  ]
}
```

Best practice: if a rule only needs a subset of the API response, combine `apiget` with `let`, `path`, `filter`, `map`, or `var` so the test compares a small deterministic projection instead of the full response payload.

#### `dfsget`
Retrieves a file from OneLake DFS endpoint. The URL must use HTTPS and target a host ending in `.dfs.fabric.microsoft.com`. Returns parsed JSON, or a raw string if the response is not valid JSON. Supports template variables and path parameters.

```json
{
  "dfsget": [
    "https://onelake.dfs.fabric.microsoft.com/{context-fabricworkspace}/{context-fabricitem}/Files/{folder}/{fileName}",
    "Config",
    "settings.json"
  ]
}
```

#### `scannerapi`
Invokes the Power BI Scanner API to scan a workspace. Multi-step: initiates scan, polls for completion (up to 60 attempts at 5-second intervals), retrieves results. Polling can take up to 5 minutes; using `scannerapi` with `-parallel true` is not recommended as long-running polls will block worker threads.

```json
{ "scannerapi": "{context-fabricworkspace}" }
```

With all metadata options:

```json
{ "scannerapi": ["<workspace-guid>", true, true, true, true, true] }
```

Parameters: workspace ID, lineage, datasource details, dataset schema, expressions, users.

## 6 — Item types

| `itemType` value | Description |
|------------------|-------------|
| `Report` | Power BI Report (PBIR format). Benefits from reserved part names. |
| `CopyJob` | Fabric CopyJob |
| `Lakehouse` | Fabric Lakehouse |
| `SemanticModel` | Power BI Semantic Model / Dataset |
| `DataPipeline` | Fabric Data Pipeline |
| `VariableLibrary` | Pipeline Variable Library |
| `Dataflow` | Dataflow Gen2 |
| `SQLDatabase` | Fabric SQL Database |
| `Warehouse` | Fabric Warehouse |
| `Notebook` | Fabric Notebook |
| `Environment` | Fabric Environment |
| `*` | Cross-item rule — applies across all item types |
| `json` | Matches any JSON metadata file |
| `none` | API-only rules that don't inspect item files |

For cross-item rules that only apply to a subset of item types, separate the types with `|` so the rule only runs against those types. For example, to run a rule against both Data Pipelines and Variable Libraries:

```json
"itemtype": "DataPipeline|VariableLibrary"
```

## 7 — Patches (deprecated)

Rules can optionally define a patch to auto-fix failing items. Currently **only Power BI Report parts** are supported.

### Patch structure

```json
"patch": [
  "<target-part>",
  [ /* RFC 6902 JSON Patch operations (add, remove, replace, move, copy, test) */ ]
]
```

Target part must be one of the reserved Report part names from Section 2.

### Example: fix missing axis titles

```json
{
  "id": "SHOW_AXES_TITLES",
  "name": "Show visual axes titles",
  "part": "Pages",
  "disabled": false,
  "applyPatch": true,
  "test": [
    {
      "map": [
        {
          "filter": [
            { "part": "Visuals" },
            {
              "and": [
                { "in": [{ "var": "visual.visualType" }, ["lineChart", "barChart", "columnChart"]] },
                {
                  "or": [
                    { "==": [{ "var": "visual.objects.categoryAxis.0.properties.showAxisTitle.expr.Literal.Value" }, "false"] },
                    { "==": [{ "var": "visual.objects.valueAxis.0.properties.showAxisTitle.expr.Literal.Value" }, "false"] }
                  ]
                }
              ]
            }
          ]
        },
        { "var": "name" }
      ]
    },
    {},
    []
  ],
  "patch": [
    "Visuals",
    [
      { "op": "replace", "path": "/visual/objects/categoryAxis/0/properties/showAxisTitle/expr/Literal/Value", "value": "true" },
      { "op": "replace", "path": "/visual/objects/valueAxis/0/properties/showAxisTitle/expr/Literal/Value", "value": "true" }
    ]
  ]
}
```

**Important**: Set `"applyPatch": true` on the rule to enable patch execution.

## 8 — Rule creation walkthrough

### Step 1: Start with the simplest possible rule

```json
{
  "rules": [
    {
      "id": "TRUE_IS_TRUE",
      "name": "True is true",
      "test": [true, true]
    }
  ]
}
```

### Step 2: Use a JSONLogic operator

```json
{
  "id": "SIMPLE_COMPARISON",
  "name": "Simple comparison",
  "test": [
    { "==": ["a", "a"] },
    true
  ]
}
```

### Step 3: Nest operators

```json
{
  "id": "NESTED_OPERATIONS",
  "name": "Nested operations",
  "test": [
    { "if": [{ "<": [1, 2] }, "smaller", "equalorgreater"] },
    "smaller"
  ]
}
```

### Step 4: Query a Fabric item

Reference the root item with an empty `var`:

```json
{
  "id": "ROOT_FABRIC_ITEM",
  "name": "Root Fabric Item",
  "test": [
    { "var": "" },
    {}
  ]
}
```

### Step 5: Iterate with the part iterator

This rule runs once per report page, checking each page's display name:

```json
{
  "id": "CHECK_PAGE_NAME",
  "name": "Check page display name",
  "part": "Pages",
  "test": [
    { "var": "displayName" },
    "My page display name"
  ]
}
```

### Step 6: Use the part operator in logic

Combine all pages' display names into a single array:

```json
{
  "id": "RETURN_PAGE_NAMES",
  "name": "Return all page names",
  "test": [
    {
      "map": [
        { "part": "Pages" },
        { "var": "displayName" }
      ]
    },
    ["Page 1", "Page 2", "Page 3"]
  ]
}
```

### Step 7: Filter and report failures

Return names of pages with default names (the common pattern):

```json
{
  "id": "GIVE_PAGES_MEANINGFUL_NAMES",
  "name": "Give visible pages meaningful names",
  "test": [
    {
      "map": [
        {
          "filter": [
            { "part": "Pages" },
            {
              "and": [
                { "strcontains": [{ "var": "displayName" }, "^Page [1-9]+$"] },
                { "!=": [{ "var": "visibility" }, "HiddenInViewMode"] }
              ]
            }
          ]
        },
        { "var": "displayName" }
      ]
    },
    {}
    []
  ]
}
```

### Step 8: Fabric (non-Report) item rules

Use a regex-based part iterator for any Fabric item:

```json
{
  "id": "CHECK_COPYJOB_JOBMODE",
  "name": "Check that CopyJob JobMode is Batch",
  "itemType": "CopyJob",
  "part": "copyjob-content.json",
  "test": [
    { "var": "properties.jobMode" },
    "Batch"
  ]
}
```

Restrict to a specific subfolder:

```json
"part": "folder1:.*:copyjob-content\\.json$"
```

### Step 9: Cross-item rules

Compare data across multiple Fabric item types:

```json
{
  "id": "VARLIBRARY_MISSINGREFERENCES",
  "name": "Check pipeline variable library references",
  "itemtype": "DataPipeline|VariableLibrary",
  "test": [
    {
      "diff": [
        { "query": [{ "part": "pipeline-content.json" }, { "path": "$.*.properties.libraryVariables.*.variableName" }] },
        { "query": [{ "part": "variables.json" }, { "path": "$.*.variables[*].name" }] }
      ]
    },
    []
  ]
}
```

### Step 10: API-driven rules

Execute a DAX query:

```json
{
  "id": "EXECUTE_DAX_QUERY",
  "name": "Execute DAX query",
  "itemType": "SemanticModel",
  "test": [
    { "daxquery": "EVALUATE VALUES('Employee Country')" },
    ["Canada"]
  ]
}
```

Call a Fabric REST API:

```json
{
  "id": "CHECK_ONELAKE_SETTINGS",
  "name": "Check OneLake settings",
  "itemType": "none",
  "test": [
    { "apiget": ["https://api.fabric.microsoft.com/v1/workspaces/{context-fabricworkspace}/onelake/settings"] },
    []
  ]
}
```

## 9 — Common patterns and idioms

| Pattern | Technique |
|---------|-----------|
| Return failing item names | `filter` + `map` with `{ "var": "name" }`, expected `[]` |
| Check a property value | `{ "var": "property.path" }`, expected `"value"` |
| Count items | `{ "count": [...] }`, expected number |
| Compare sets | `diff`, `intersection`, `equalsets`, `symdiff`, `union` |
| Query nested JSON | `query` + `part` + `var` or `path` |
| Regex file matching | `"part": "pattern"` with colon folder separators |
| Avoid redundant API calls | `let` to bind API response, then reference via `var` |
| Build structured output | `torecord` with key/value pairs |
| Check file sizes | `filesize` + `partinfo` |
| Search file contents | `filetextsearchcount` + `partinfo` + regex |

## 10 — Rule examples

The [RuleExamples](../../RuleExamples/) folder contains working rule files covering a range of item types, operators, and patterns. When creating or editing rules, consult these for real-world usage:

| File | Covers |
|------|--------|
| `Example-pbir-rules.json` | Report rules — pages, visuals, bookmarks, themes |
| `Example-CopyJob-Rules.json` | CopyJob item rules |
| `Example-lakehouse-workspace-naming-rules.json` | Lakehouse + workspace naming conventions |
| `Example-FabricCrossItem-Rules.json` | Cross-item (`*`) rules |
| `Sample-VariableLibrary-rules.json` | VariableLibrary + DataPipeline cross-item |
| `Example-fabric-apiget-rule.json` | `apiget` with Fabric REST API |
| `Example-pbi-apiget-rule.json` | `apiget` with Power BI REST API |
| `Example-daxquery-rule.json` | `daxquery` operator |
| `Example-scannerapi-rules.json` | `scannerapi` operator |
| `Example-dfsget-rule.json` | `dfsget` operator |
| `Example-let-rule.json` | `let` variable binding |
| `Example-Let-Nested-Sample.json` | Nested `let` bindings |
| `Example-patches.json` | Patch (auto-fix) definitions |
| `Example-NewOperators-rules.json` | Misc custom operators |

## 11 — Reference links

- **Wiki — Anatomy of a rule**: https://github.com/NatVanG/PBI-InspectorV2/wiki/Anatomy-of-a-PBI-Inspector-V2-rule
- **Wiki — Operators**: https://github.com/NatVanG/PBI-InspectorV2/wiki/Operators
- **Wiki — Rule creation tutorial**: https://github.com/NatVanG/PBI-InspectorV2/wiki/Rule-creation-tutorial
- **JSONLogic specification**: https://jsonlogic.com/operations.html
- **JSON Pointer specification**: https://datatracker.ietf.org/doc/html/rfc6901
- **JSONPath.Net**: https://docs.json-everything.net/path/basics/
- **JSON Patch (RFC 6902)**: https://tools.ietf.org/html/rfc6902
- **CLI invocation**: see the `fab-inspector-cli` skill
