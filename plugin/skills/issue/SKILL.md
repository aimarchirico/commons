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
   `${CLAUDE_PLUGIN_ROOT}/.github/CONTRIBUTING.md`.
3. Show the drafted hierarchy and wait for user approval. Skip this step if
   the `--auto` flag is set, and proceed directly with the drafted
   hierarchy.
4. Generate a temporary `issues.json` file containing an `items` array where
   every node in the hierarchy matches this recursive JSON schema:

   ```json
   {
     "items": [
       {
         "title": "string",
         "body": "string",
         "type": "string",
         "priority": "string",
         "children": [/* nested child objects following the same schema */]
       }
     ]
   }
   ```

5. Execute
   `python3 "${CLAUDE_PLUGIN_ROOT}/skills/issue/scripts/create_issues.py" issues.json`
   (the script automatically deletes the temporary file upon completion).

## Output

The id of the top-level (root) issue created, so a caller that invoked
this skill can act on it.
