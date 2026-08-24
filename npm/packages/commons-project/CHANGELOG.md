# Changelog

## [1.4.2](https://github.com/aimarchirico/commons/compare/commons-project-v1.4.1...commons-project-v1.4.2) (2026-08-24)


### Bug Fixes

* **commons-project:** count a written outcome as a change in printSummary ([c1678b3](https://github.com/aimarchirico/commons/commit/c1678b3435be4e1622b9941045d7bd1d36128b08))
* **commons-project:** count a written outcome as a change in printSummary ([d4fef51](https://github.com/aimarchirico/commons/commit/d4fef51e4dce87f1d6dae3a04dbf336bef626dfc))

## [1.4.1](https://github.com/aimarchirico/commons/compare/commons-project-v1.4.0...commons-project-v1.4.1) (2026-08-24)


### Bug Fixes

* **cli:** prefix printSummary tallies with the package name ([1a71b90](https://github.com/aimarchirico/commons/commit/1a71b90291c3422a109f79837c8a701b71856e7b))
* **cli:** prefix printSummary tallies with the package name ([77c5daa](https://github.com/aimarchirico/commons/commit/77c5daac47540940627766708706ff51f44c9a37))

## [1.4.0](https://github.com/aimarchirico/commons/compare/commons-project-v1.3.1...commons-project-v1.4.0) (2026-08-09)


### Features

* **commons-github:** standardize documentation format guidance in CONTRIBUTING.md ([88c4462](https://github.com/aimarchirico/commons/commit/88c44624ab924b10708958faeba74f80f697b777))

## [1.3.1](https://github.com/aimarchirico/commons/compare/commons-project-v1.3.0...commons-project-v1.3.1) (2026-08-03)


### Bug Fixes

* **docs:** align markdown tables and trim trailing blank line ([7e4b237](https://github.com/aimarchirico/commons/commit/7e4b2374212b97ba62630be49b17f5fff89435ae))

## [1.3.0](https://github.com/aimarchirico/commons/compare/commons-project-v1.2.0...commons-project-v1.3.0) (2026-08-02)


### Features

* **eslint:** require JSDoc on default export call expressions and wrap configs in defineConfig ([a94e91e](https://github.com/aimarchirico/commons/commit/a94e91ee5dd122477a99a9eb2034559194ac91ab))


### Bug Fixes

* **commons-project:** narrow build include to actual entry points ([7681e46](https://github.com/aimarchirico/commons/commit/7681e46a968e138e2bef76fe11d4fb28dbac05c1))
* **npm:** scope build includes to real entry points, stop excluding bin from coverage ([57de6b2](https://github.com/aimarchirico/commons/commit/57de6b26dd303e7bc196cef74a16b4eb4e4446eb))

## [1.2.0](https://github.com/aimarchirico/commons/compare/commons-project-v1.1.0...commons-project-v1.2.0) (2026-08-01)


### Features

* **commons-ts:** add default-export-shape lint rule and update ESLint base config ([4f631e4](https://github.com/aimarchirico/commons/commit/4f631e4750fd715aa172a75f834a0a3381eef265))
* **commons-ts:** add shared 80% vitest coverage config ([3598d0d](https://github.com/aimarchirico/commons/commit/3598d0d3795f3313e44c2b4a0de74c6d40a786d5))

## [1.1.0](https://github.com/aimarchirico/commons/compare/commons-project-v1.0.0...commons-project-v1.1.0) (2026-07-30)


### Features

* tighten comment and suppression discipline ([b2f362e](https://github.com/aimarchirico/commons/commit/b2f362ecfce6271bfac3e9309e72c07c6982c74c))


### Bug Fixes

* **commons-project:** satisfy public-jsdoc-only across services and types ([a03f748](https://github.com/aimarchirico/commons/commit/a03f7486ffcdff208ae12f5f60d89314bf903962))

## 1.0.0 (2026-07-29)


### ⚠ BREAKING CHANGES

* enforce documentation standards via commons-ts and commons-convention
* **commons-project:** subpaths `./env`, `./report`, and `./outputs` are removed in favor of root exports.

### Features

* add reusable provisioning commands for scaffolded projects ([3c17e79](https://github.com/aimarchirico/commons/commit/3c17e79b7a7067784fe1ca24871b5fcbb4a5bedf))
* **commons-expo:** resolve eas-cli from the lockfile instead of PATH ([7249f8c](https://github.com/aimarchirico/commons/commit/7249f8ca5782f8e02ebe80f515f5f56ac91ebc2a))
* **commons-project:** add cli, git and instruction helpers ([e019cdf](https://github.com/aimarchirico/commons/commit/e019cdf9fb8bf4f19f03ebf6fd496707e0b97c98))
* enforce documentation standards via commons-ts and commons-convention ([d6f5028](https://github.com/aimarchirico/commons/commit/d6f5028dbedbd74cdb52d92568fadd44e797e40b))


### Bug Fixes

* **commons-firebase-client:** force release ([f6b030c](https://github.com/aimarchirico/commons/commit/f6b030c8645bbb290d955193962d09c7f02f3f94))


### Code Refactoring

* **commons-project:** export from root instead of subpaths ([6fda9b7](https://github.com/aimarchirico/commons/commit/6fda9b70ba31d370e53ca2df473c5f63baa2f37d))
