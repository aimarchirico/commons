# Changelog

## [1.4.1](https://github.com/aimarchirico/commons/compare/commons-github-v1.4.0...commons-github-v1.4.1) (2026-08-03)


### Bug Fixes

* **commons-github:** drop unreliable self-run guard on bin entry point ([21ad7ed](https://github.com/aimarchirico/commons/commit/21ad7edcf682aebce443f0724d1bca5605aefb00))
* drop unreliable self-run guard on CLI bin entry points ([e438c69](https://github.com/aimarchirico/commons/commit/e438c69944693553766a7dd632db7b4b3b41e01b))

## [1.4.0](https://github.com/aimarchirico/commons/compare/commons-github-v1.3.0...commons-github-v1.4.0) (2026-08-03)


### Features

* **settings:** add attribution configuration to settings.json ([e271e28](https://github.com/aimarchirico/commons/commit/e271e28cada7dfab52452edcb266c8bf9ec66569))


### Bug Fixes

* **commons-github:** actually invoke CLI subcommand handlers ([f97ddbf](https://github.com/aimarchirico/commons/commit/f97ddbfad41bd6da6d24f1f7466f56eec659b11b))

## [1.3.0](https://github.com/aimarchirico/commons/compare/commons-github-v1.2.1...commons-github-v1.3.0) (2026-08-02)


### Features

* **eslint:** require JSDoc on default export call expressions and wrap configs in defineConfig ([a94e91e](https://github.com/aimarchirico/commons/commit/a94e91ee5dd122477a99a9eb2034559194ac91ab))


### Bug Fixes

* **commons-github:** add unit tests for CLI bin scripts and resolve coverage check threshold failure ([6a13f16](https://github.com/aimarchirico/commons/commit/6a13f164bd23157096948e38354686aca935ab13))
* **commons-github:** stop emitting test files into dist ([92b5d1b](https://github.com/aimarchirico/commons/commit/92b5d1b2b216a6a28cc1fb2b51b19e5e30de17ac))
* **npm:** scope build includes to real entry points, stop excluding bin from coverage ([57de6b2](https://github.com/aimarchirico/commons/commit/57de6b26dd303e7bc196cef74a16b4eb4e4446eb))
* **npm:** stop exporting bin-script internals solely for testing ([5fd9ef1](https://github.com/aimarchirico/commons/commit/5fd9ef153d60856b5836cb55950ec67c9460a571))

## [1.2.1](https://github.com/aimarchirico/commons/compare/commons-github-v1.2.0...commons-github-v1.2.1) (2026-08-02)


### Bug Fixes

* add explicit .js extensions to relative imports ([62321ab](https://github.com/aimarchirico/commons/commit/62321abe70fc0246cb000eb4cca2156ee18dadd2))
* **commons-github:** add explicit .js extensions to relative imports ([3c6ea83](https://github.com/aimarchirico/commons/commit/3c6ea839003cf866c5aad6b327ed7370f2e8799f))

## [1.2.0](https://github.com/aimarchirico/commons/compare/commons-github-v1.1.2...commons-github-v1.2.0) (2026-08-01)


### Features

* **commons-ts:** add shared 80% vitest coverage config ([3598d0d](https://github.com/aimarchirico/commons/commit/3598d0d3795f3313e44c2b4a0de74c6d40a786d5))

## [1.1.2](https://github.com/aimarchirico/commons/compare/commons-github-v1.1.1...commons-github-v1.1.2) (2026-08-01)


### Bug Fixes

* add principles section to contributing guidelines ([88a6646](https://github.com/aimarchirico/commons/commit/88a66465875f80162f88721cf82dd2fa4a1cdda4))
* cite source and spell out names in principles section ([70e766b](https://github.com/aimarchirico/commons/commit/70e766b9561527c3f3b58da9271d77001c9235a0))
* expand and group principles section ([88a7834](https://github.com/aimarchirico/commons/commit/88a7834d4c3aa0071a9eaf95d48574c6ecc2a244))
* scope code quality section to language-specific tooling ([ed3fee3](https://github.com/aimarchirico/commons/commit/ed3fee3dfd56ae27f699ae9870461aa211ac50bd))

## [1.1.1](https://github.com/aimarchirico/commons/compare/commons-github-v1.1.0...commons-github-v1.1.1) (2026-07-31)


### Bug Fixes

* **commons-github:** shorten Bug issue type description to "A problem." ([747ccbd](https://github.com/aimarchirico/commons/commit/747ccbd32dbec49cb4df5bbffe1d75cf2ef4388c))
* **commons-github:** shorten Bug issue type description to "A problem." ([2a73689](https://github.com/aimarchirico/commons/commit/2a73689bf86a57294e3050b9b0f6ed6f8d87eabb)), closes [#261](https://github.com/aimarchirico/commons/issues/261)

## [1.1.0](https://github.com/aimarchirico/commons/compare/commons-github-v1.0.0...commons-github-v1.1.0) (2026-07-30)


### Features

* tighten comment and suppression discipline ([b2f362e](https://github.com/aimarchirico/commons/commit/b2f362ecfce6271bfac3e9309e72c07c6982c74c))


### Bug Fixes

* **commons-github:** satisfy public-jsdoc-only in bin scripts and gh service ([c89c5d9](https://github.com/aimarchirico/commons/commit/c89c5d97062df01343d462fe3c4f922b921c1802))

## 1.0.0 (2026-07-29)


### ⚠ BREAKING CHANGES

* enforce documentation standards via commons-ts and commons-convention
* **commons-project:** subpaths `./env`, `./report`, and `./outputs` are removed in favor of root exports.

### Features

* add reusable provisioning commands for scaffolded projects ([3c17e79](https://github.com/aimarchirico/commons/commit/3c17e79b7a7067784fe1ca24871b5fcbb4a5bedf))
* **commons-github:** add repository provisioning commands ([5024ad6](https://github.com/aimarchirico/commons/commit/5024ad6a46373803459d12682c37e80e132262dd)), closes [#183](https://github.com/aimarchirico/commons/issues/183) [#184](https://github.com/aimarchirico/commons/issues/184) [#185](https://github.com/aimarchirico/commons/issues/185) [#186](https://github.com/aimarchirico/commons/issues/186) [#187](https://github.com/aimarchirico/commons/issues/187) [#182](https://github.com/aimarchirico/commons/issues/182)
* enforce documentation standards via commons-ts and commons-convention ([d6f5028](https://github.com/aimarchirico/commons/commit/d6f5028dbedbd74cdb52d92568fadd44e797e40b))


### Bug Fixes

* **commons-firebase-client:** force release ([f6b030c](https://github.com/aimarchirico/commons/commit/f6b030c8645bbb290d955193962d09c7f02f3f94))
* **commons-github,commons-cloudflare,commons-expo:** drop unused overrides, fail-fast keystore ([04b79a0](https://github.com/aimarchirico/commons/commit/04b79a075adb8062da2b605f31a3694b93354355))
* **commons-github:** copy from a public Commons Template project ([6c7a676](https://github.com/aimarchirico/commons/commit/6c7a676af0e34a6d76026498f7a45db32fc1de6c))
* **commons-github:** derive project title and source from repo, not env vars ([1ed24cf](https://github.com/aimarchirico/commons/commit/1ed24cff61d8f404735b800e72cdb99d227bf8d4))


### Code Refactoring

* **commons-project:** export from root instead of subpaths ([6fda9b7](https://github.com/aimarchirico/commons/commit/6fda9b70ba31d370e53ca2df473c5f63baa2f37d))
