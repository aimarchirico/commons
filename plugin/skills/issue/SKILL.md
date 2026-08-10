---
name: issue
description:
  Create new hierarchical issues. Use when the user asks to create new
  issues.
argument-hint: "[--auto]"
---

## Arguments

| Flag     | Required | Description                                                       |
| :------- | :------- | :---------------------------------------------------------------- |
| `--auto` | No       | Skip the approval step and create the drafted hierarchy directly. |

## Workflow

1. Identify the details and context of the issues to create. If these details
   are not already clear from the user's prompt or context, ask the user for
   clarification.
2. Map and format the identified work strictly following the hierarchy and
   conventions defined in `${CLAUDE_PLUGIN_ROOT}/.github/CONTRIBUTING.md#issues`
   and `${CLAUDE_PLUGIN_ROOT}/.github/ISSUE_TEMPLATE/`. Automatically infer any
   required logical child issues to completely represent the hierarchy of
   work. Ensure each issue is assigned its type and priority in their
   respective fields based on the definitions in
   `${CLAUDE_PLUGIN_ROOT}/.github/CONTRIBUTING.md`. Also identify any issues
   that must be done in a specific order (e.g. one issue's implementation
   depends on another's), and record those as blocked-by relationships using
   the `id`/`blocked_by` fields below. `blocked_by` can reference any other
   item being created in the batch, regardless of its type or position in
   the hierarchy. Do not use blocked-by for parent/child pairs; that
   relationship is already expressed by nesting.
3. Show the drafted hierarchy and wait for user approval. Skip this step if
   the `--auto` flag is set, and proceed directly with the drafted
   hierarchy.
4. Generate a temporary `issues.json` file containing an `items` array where
   every node in the hierarchy matches this recursive JSON schema:

   ```json
   {
     "items": [
       {
         "id": "string, optional, a local-only label to reference from another item's blocked_by",
         "title": "string",
         "body": "string",
         "type": "string",
         "priority": "string",
         "blocked_by": ["array of other items' \"id\" values, optional"],
         "children": [/* nested child objects following the same schema */]
       }
     ]
   }
   ```

   `id` and `blocked_by` are local to this file and never sent to GitHub
   directly; the script resolves `blocked_by` references to the real issue
   numbers after every issue in the batch has been created, then wires them
   up as native GitHub "blocked by" relationships.

5. Create all issues in the hierarchy:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/issue/scripts/create_issues.py" issues.json
   ```

   This creates each item, wires native GitHub blocked-by relationships, and
   automatically deletes the temporary file upon completion.

## Output

The id of the top-level (root) issue created, so a caller that invoked
this skill can act on it.
