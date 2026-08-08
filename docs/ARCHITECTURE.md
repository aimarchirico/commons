# Architecture

System-level source of truth for Commons. Contains only what spans the whole
repository; implementation detail lives in each subsystem's README.

## Data Flow

### Package Publishing & Monorepo Distribution

Commons is built and published from a single monorepo. Release Please cuts
versioned releases, the matching artifacts are published to GitHub Packages, and
downstream repositories consume them.

```mermaid
graph LR
    subgraph Commons["Commons monorepo"]
        tools_src["tools/<br/>linting + release config"]
        maven_src["maven/<br/>Kotlin modules"]
        npm_src["npm/<br/>config packages + CLI"]
        python_src["python/<br/>Python packages"]
        plugin["plugin/<br/>agent skills"]
    end

    rp["Release Please<br/>(GitHub Actions)"]
    maven_reg["GitHub Packages<br/>Maven registry"]
    npm_reg["GitHub Packages<br/>npm registry"]

    consumers["Downstream services<br/>(e.g. service template)"]

    tools_src -->|release config| rp
    maven_src -->|release| rp
    npm_src -->|release| rp
    rp -->|publish| maven_reg
    rp -->|publish| npm_reg

    maven_reg -->|Gradle dependency| consumers
    npm_reg -->|npm dependency| consumers
    python_src -->|git dependency @ main| consumers
    plugin -->|plugin install| consumers
```

### Provisioning Commands & External Services

Alongside the libraries and configs it publishes, Commons publishes CLI
commands that provision the external resources a newly scaffolded project
needs. The division of responsibility is deliberate: Commons owns the
mechanics and stays generic, while the downstream repository owns every
project-specific value and the order the commands run in. Failures, no-ops,
and steps only a human can take (reported as action required, distinct from a
failure) are all reported explicitly.

```mermaid
graph LR
    subgraph Downstream["Downstream repository"]
        config["project config<br/>+ rename manifest"]
        orchestrator["setup task<br/>(orchestration + values)"]
    end

    subgraph Commands["Commons provisioning commands"]
        project["commons-project<br/>rename-project"]
        github["commons-github<br/>project, environments,<br/>variables, secrets"]
        cloudflare["commons-cloudflare<br/>pages, tunnel route,<br/>service token"]
        expo["commons-expo<br/>project, keystore import"]
    end

    resources["External resources<br/>(GitHub · Cloudflare · EAS)"]

    config --> orchestrator
    orchestrator -->|env| project
    orchestrator -->|env| github
    orchestrator -->|env| cloudflare
    orchestrator -->|env| expo
    project --> resources
    github --> resources
    cloudflare --> resources
    expo --> resources
    cloudflare -.->|emitted values| orchestrator
    expo -.->|emitted values| orchestrator
```

Command and variable reference: [npm/README.md](../npm/README.md).

### Agent Skill & Subagent Execution

The agent plugin packages reusable workflows (`skills/`) and subagent prompts
(`agents/`). Agent skills delegate task execution to specialized subagents
or deterministic Python scripts, which execute GitHub GraphQL/REST operations
and manage git worktrees.

```mermaid
graph TD
    user["User / Developer"]
    skill["Agent Skill<br/>(plugin/skills/*)"]
    agents["Subagents<br/>(plugin/agents/*)"]
    scripts["Python Scripts<br/>(skills/*/scripts/*)"]
    github_git["GitHub API & Git Repositories"]

    user -->|invokes| skill
    skill -->|delegates task| agents
    skill -->|runs script| scripts
    agents -->|executes via| scripts
    scripts -->|API calls & worktrees| github_git
```

#### Skill Selection & Development Lifecycle Flow

```mermaid
graph TD
    start_proj["Brand-New Project"] --> plan["/commons:plan<br/>Draft Planning & Design Artifacts"]
    plan --> issue["/commons:issue<br/>Create Issue Hierarchy"]

    survey["Survey Work"] --> triage["/commons:triage<br/>Survey PRs & Backlog"]
    triage -->|New Task/Story| issue
    triage -->|Existing Issue| solve["/commons:solve<br/>Implement Issue Fix"]
    issue --> solve

    solve --> pr["/commons:pr<br/>Create Pull Request"]
    pr --> review["/commons:review<br/>Parallel Code Review"]

    review -->|Changes Requested| resolve["/commons:resolve<br/>Address Feedback & Re-review"]
    resolve --> review

    review -->|Approved| merge["Merge PR"]

    subgraph FastTrack["Fast-Track Flow"]
        ship["/commons:ship<br/>Chains issue → solve → review → resolve"]
    end
```

## Infrastructure Overview

| Layer             | Technology                                               | Hosting                                       |
| :---------------- | :------------------------------------------------------- | :-------------------------------------------- |
| Backend libraries | Java 25 · Kotlin 2.4 · Gradle 9.6 · Spring Boot 4.1      | GitHub Packages (Maven registry)              |
| Frontend configs  | Node 20+ · PNPM 11.9 · TypeScript 6 · ESLint 9 · Turbo 2 | GitHub Packages (npm registry)                |
| Tooling configs   | PNPM 11.9 · markdownlint-cli2 · commitlint               | `tools/` (not published)                      |
| Python tooling    | Python 3.13 · uv · ruff · coverage · hatchling           | git dependency pinned to `main` (no registry) |
| Agent skills      | Markdown `SKILL.md`                                      | GitHub repository (Claude Code plugin)        |
| CI/CD             | GitHub Actions · Release Please                          | GitHub-hosted runners                         |

## Project Structure

```text
.
├── tools/      # shared linting configs, commitlint, and release-please config
├── .github/    # CI/release workflows and issue/PR templates
├── docs/       # system-level documentation
├── maven/      # Kotlin backend modules and the Gradle convention plugin
├── npm/        # frontend configuration packages and the API CLI
├── python/     # Python package(s): shared ruff/coverage config + CLI, git dependency @ main
└── plugin/     # Claude Code plugin (skills/, agents/, shared/), the only tree consumers install
```
