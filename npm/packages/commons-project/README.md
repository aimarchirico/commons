# commons-project

Project-rename CLI, published as `@aimarchirico/commons-project`, plus the
shared provisioning helpers (`env`, `report`, `outputs`, `cli`, `git`) other
provisioning packages depend on. The one command it exposes takes no
arguments, reads its inputs from `process.env`, fails fast naming every
missing variable at once, and is idempotent: a second run makes no
destructive change and reports a no-op.

## `rename-project`

Rewrites a generated repository from its template placeholder values to the
project's real values.

| Key             | Required | Purpose                                             |
| :-------------- | :------- | :--------------------------------------------------- |
| `MANIFEST_PATH` | No       | Manifest to execute. Defaults to `./manifest.json`. |

The manifest holds all layout knowledge and is validated in full before
anything is written:

```json
{
  "values": {
    "backendPackage": {"from": "no.chirico.template", "to": "no.chirico.myapp"},
    "backendName": {"from": "Template", "to": "My App"}
  },
  "replacements": [
    {"value": "backendPackage", "files": ["backend/**/*.kt"]},
    {
      "value": "backendName",
      "transforms": ["pascal", "lower"],
      "files": ["backend/**/*.kt", "backend/compose.prod.yaml"]
    }
  ],
  "moves": [
    {
      "from": "backend/app/src/main/kotlin/{{backendPackage|path}}",
      "to": "backend/app/src/main/kotlin/{{backendPackage|path}}"
    }
  ],
  "deletes": ["README.md"]
}
```

- `replacements` replace each value's literal variants across the matched
  globs. `transforms` selects which variants: `identity` (the default),
  `lower`, `kebab`, `snake`, `camel`, `pascal`, `title`, and `path` (a dotted
  identifier to path segments). An unknown transform fails with it named.
- `moves` interpolate `{{value}}`, `{{value|transform}}`, and
  `{{value.from|transform}}`. An unqualified placeholder takes the side of the
  field it appears in, so a move's `from` reads source values and its `to`
  reads target values.
- Re-running a completed rename finds nothing to change and reports a no-op,
  since the source values are gone.

`rename-project` runs after `pnpm install` on a freshly generated repository:
the replacement scan ignores `node_modules`, so installing first is safe, and
it means the template's own lockfile pins the version of the tool that
rewrites it. Re-run `pnpm install` afterwards when the manifest moved
workspace directories or renamed packages, since both invalidate the links
and `importers` entries recorded at install time.

## Development

```bash
pnpm install
pnpm --filter @aimarchirico/commons-project check   # lint + typecheck + test
pnpm --filter @aimarchirico/commons-project fix      # auto-fix lint
```

Vitest enforces an 80% line/function/branch/statement coverage floor via
`commons-ts`'s shared `./vitest-base` config; `bin/` entrypoints are excluded.
Released by Release Please and published to the GitHub Packages npm registry
when a release touches this package's path.
