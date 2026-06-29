# Architecture

System-level source of truth for Core. Contains only what spans the whole
repository; implementation detail lives in each subsystem's README.

## Data Flow

Core is built and published from a single monorepo. Release Please cuts versioned
releases, the matching artifacts are published to GitHub Packages, and downstream
repositories consume them.

```mermaid
graph LR
    subgraph Core["Core monorepo"]
        maven_src["maven/<br/>Kotlin modules"]
        npm_src["npm/<br/>config packages + CLI"]
        tools_src["tools/<br/>linting + release config"]
        skills["skills/<br/>agent skills"]
    end

    rp["Release Please<br/>(GitHub Actions)"]
    maven_reg["GitHub Packages<br/>Maven registry"]
    npm_reg["GitHub Packages<br/>npm registry"]

    consumers["Downstream services<br/>(e.g. service template)"]

    maven_src -->|release| rp
    npm_src -->|release| rp
    tools_src -->|release config| rp
    rp -->|publish| maven_reg
    rp -->|publish| npm_reg

    maven_reg -->|Gradle dependency| consumers
    npm_reg -->|npm dependency| consumers
    skills -->|skills add| consumers
```

## Infrastructure Overview

| Layer             | Technology                                    | Hosting                          |
| :---------------- | :-------------------------------------------- | :------------------------------- |
| Backend libraries | Kotlin 2.4 · Gradle 9.6 · Spring Boot 4.1     | GitHub Packages (Maven registry) |
| Frontend configs  | PNPM 11.9 · TypeScript 5 · ESLint 9 · Turbo 2 | GitHub Packages (npm registry)   |
| Tooling configs   | PNPM 11.9 · markdownlint-cli2 · commitlint    | `tools/` (not published)         |
| Agent skills      | Markdown `SKILL.md`                           | GitHub repository (`skills add`) |
| CI/CD             | GitHub Actions · Release Please               | GitHub-hosted runners            |

## Project Structure

```text
.
├── maven/      # Kotlin backend modules and the Gradle convention plugin
├── npm/        # frontend configuration packages and the API CLI
├── tools/      # shared linting configs, commitlint, and release-please config
├── skills/     # agent skills
├── docs/       # system-level documentation
└── .github/    # CI/release workflows and issue/PR templates
```
