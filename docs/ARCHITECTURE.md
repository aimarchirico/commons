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
        gradle["gradle/<br/>Kotlin modules"]
        pnpm["pnpm/<br/>config packages + CLI"]
        skills["skills/<br/>agent skills"]
    end

    rp["Release Please<br/>(GitHub Actions)"]
    maven["GitHub Packages<br/>Maven registry"]
    npm["GitHub Packages<br/>npm registry"]

    consumers["Downstream services<br/>(e.g. service template)"]

    gradle -->|release| rp
    pnpm -->|release| rp
    rp -->|publish| maven
    rp -->|publish| npm

    maven -->|Gradle dependency| consumers
    npm -->|npm dependency| consumers
    skills -->|skills add| consumers
```

## Infrastructure Overview

| Layer             | Technology                                   | Hosting                          |
| :---------------- | :------------------------------------------- | :------------------------------- |
| Backend libraries | Kotlin 2.4 · Gradle 9.6 · Spring Boot 4.1    | GitHub Packages (Maven registry) |
| Frontend configs  | pnpm 11.9 · TypeScript 5 · ESLint 9 · Turbo 2 | GitHub Packages (npm registry)   |
| Agent skills      | Markdown `SKILL.md`                          | GitHub repository (`skills add`) |
| CI/CD             | GitHub Actions · Release Please              | GitHub-hosted runners            |

## Project Structure

```text
.
├── gradle/     # Kotlin backend modules and the Gradle convention plugin
├── pnpm/       # frontend configuration packages and the API CLI
├── skills/     # agent skills
├── docs/       # system-level documentation
└── .github/    # CI/release workflows and issue/PR templates
```
