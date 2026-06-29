---
description: Create new hierarchical issues
metadata:
    github-path: skills/issues
    github-ref: refs/heads/main
    github-repo: https://github.com/aimarchirico/core
    github-tree-sha: 6b523142fd8c214bf98a9c7f459ee4882f26096e
name: issues
---
## When to Use

Use when the user asks to create new issues.

## Execution Steps

1. Preflight: Verify that `CONTRIBUTING.md` exists in the repository root and the `.github/ISSUE_TEMPLATE/` directory exists. If any are missing, run `npx @aimarchirico/core-docs` to materialize the documentation.
2. Identify the details and context of the issues to create. If these details are not already clear from the user's prompt or context, ask the user for clarification.
3. Map and format the identified work strictly following the hierarchy and conventions defined in `CONTRIBUTING.md#issues` and `.github/ISSUE_TEMPLATE/`. Automatically infer any required logical child issues to completely represent the hierarchy of work. Ensure each issue is assigned its type and priority in their respective fields based on the definitions in `CONTRIBUTING.md`.
4. Show the drafted hierarchy and wait for user approval.
5. Generate a temporary `issues.json` file containing an `items` array where every node in the hierarchy matches this recursive JSON schema:

   ```json
   {
     "items": [
       {
         "title": "string",
         "body": "string",
         "type": "string",
         "priority": "string",
         "children": [
           /* nested child objects following the same schema */
         ]
       }
     ]
   }
   ```

6. Execute `python3 .agents/skills/issues/scripts/create_issues.py issues.json` (the script automatically deletes the temporary file upon completion).
