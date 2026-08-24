# commons-ssh

SSH/SCP provisioning CLI, published as `@aimarchirico/commons-ssh`.

## Install

```bash
pnpm add @aimarchirico/commons-ssh
```

Every command takes no arguments, reads its inputs from `process.env`, and
fails fast naming every missing variable at once.

## Usage

### `sync-env`

Reconciles a `.env` file on a remote host: reads back whatever already
exists there, generates any missing secrets, and writes the merged result
back with `chmod 600`. Idempotent - a second run with the same inputs makes
no change.

| Variable          | Required | Meaning                                                        |
| :---------------- | :------- | :------------------------------------------------------------- |
| `SSH_HOST`        | Yes      | The remote host.                                               |
| `SSH_USER`        | Yes      | The user to connect as.                                        |
| `SSH_KEY_FILE`    | Yes      | Path to that user's private key.                               |
| `REMOTE_ENV_PATH` | Yes      | Full path to the remote `.env` file.                           |
| `ENV_VALUES`      | No       | `KEY=VALUE` pairs, comma-separated, always written fresh.      |
| `ENV_DEFAULTS`    | No       | `KEY=VALUE` pairs used only when the key doesn't exist yet.    |
| `ENV_SECRET_KEYS` | No       | Keys reused if present, else `process.env[KEY]`, else random.  |
| `OUTPUT_KEYS`     | No       | Subset of resolved keys to also chain onward via outputs.      |

### `copy-files`

Copies local files to a directory on a remote host over `scp`, streaming
`scp`'s own progress output.

| Variable       | Required | Meaning                                   |
| :------------- | :------- | :---------------------------------------- |
| `SSH_HOST`     | Yes      | The remote host.                          |
| `SSH_USER`     | Yes      | The user to connect as.                   |
| `SSH_KEY_FILE` | Yes      | Path to that user's private key.          |
| `REMOTE_DIR`   | Yes      | Destination directory on the remote host. |
| `LOCAL_FILES`  | Yes      | Comma-separated local file paths to copy. |

## Development

### Code Quality

`pnpm check` lints, type-checks, and tests the package; `pnpm fix` applies
what ESLint can fix.

## Contributing

See the root [`CONTRIBUTING.md`](../../../.github/CONTRIBUTING.md).
