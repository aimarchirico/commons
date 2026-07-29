# Changelog

## [3.1.0](https://github.com/aimarchirico/commons/compare/commons-cloudflare-v3.0.0...commons-cloudflare-v3.1.0) (2026-07-29)


### Features

* clean up package exports and make Cloudflare proxy a root export ([cf45ef8](https://github.com/aimarchirico/commons/commit/cf45ef8612bc7b37b81373a7bca618016cd91d8c))

## [3.0.0](https://github.com/aimarchirico/commons/compare/commons-cloudflare-v2.1.1...commons-cloudflare-v3.0.0) (2026-07-29)


### ⚠ BREAKING CHANGES

* enforce documentation standards via commons-ts and commons-convention
* **commons-project:** subpaths `./env`, `./report`, and `./outputs` are removed in favor of root exports.

### Features

* add reusable provisioning commands for scaffolded projects ([3c17e79](https://github.com/aimarchirico/commons/commit/3c17e79b7a7067784fe1ca24871b5fcbb4a5bedf))
* **commons-cloudflare:** add provisioning commands ([581b5a8](https://github.com/aimarchirico/commons/commit/581b5a8b71caf8419a567e110f3641536f356a1b)), closes [#189](https://github.com/aimarchirico/commons/issues/189) [#190](https://github.com/aimarchirico/commons/issues/190) [#191](https://github.com/aimarchirico/commons/issues/191) [#192](https://github.com/aimarchirico/commons/issues/192) [#188](https://github.com/aimarchirico/commons/issues/188)
* **commons-cloudflare:** derive the account and production branch ([a0cb8fb](https://github.com/aimarchirico/commons/commit/a0cb8fbc9111e80c979c1fe87b3585895fdfdfa6))
* enforce documentation standards via commons-ts and commons-convention ([d6f5028](https://github.com/aimarchirico/commons/commit/d6f5028dbedbd74cdb52d92568fadd44e797e40b))


### Bug Fixes

* **commons-github,commons-cloudflare,commons-expo:** drop unused overrides, fail-fast keystore ([04b79a0](https://github.com/aimarchirico/commons/commit/04b79a075adb8062da2b605f31a3694b93354355))


### Code Refactoring

* **commons-project:** export from root instead of subpaths ([6fda9b7](https://github.com/aimarchirico/commons/commit/6fda9b70ba31d370e53ca2df473c5f63baa2f37d))

## [2.1.1](https://github.com/aimarchirico/commons/compare/commons-cloudflare-v2.1.0...commons-cloudflare-v2.1.1) (2026-07-24)


### Bug Fixes

* update tsconfig extends to use tsconfig-base across multiple packages ([1b2bb2a](https://github.com/aimarchirico/commons/commit/1b2bb2a02ab320dd7750965927186aa56c4cb19a))

## [2.1.0](https://github.com/aimarchirico/commons/compare/commons-cloudflare-v2.0.0...commons-cloudflare-v2.1.0) (2026-07-19)


### Features

* **npm:** migrate package CLI scripts from mjs to ts ([f834145](https://github.com/aimarchirico/commons/commit/f834145b5c9eb8330c41b352e378f92cb89b1566))

## [2.0.0](https://github.com/aimarchirico/commons/compare/commons-cloudflare-v1.1.2...commons-cloudflare-v2.0.0) (2026-07-18)


### ⚠ BREAKING CHANGES

* bin invocations now require a subcommand. The old bare bin keys (commons-cloudflare-fix, commons-expo-build-android, commons-firebase-client-decode-google-services) are removed.

### Features

* standardize commons bins on &lt;package&gt; &lt;verb&gt; subcommands ([e61ea8e](https://github.com/aimarchirico/commons/commit/e61ea8e26fb19960a52fe2249d3f231b502cfca7))

## [1.1.2](https://github.com/aimarchirico/commons/compare/commons-cloudflare-v1.1.1...commons-cloudflare-v1.1.2) (2026-07-18)


### Bug Fixes

* guard proxy secret header and repair fix-cloudflare script ([5bd5394](https://github.com/aimarchirico/commons/commit/5bd539447bd8290e74eafeb637728b5aff916fe0))

## [1.1.1](https://github.com/aimarchirico/commons/compare/commons-cloudflare-v1.1.0...commons-cloudflare-v1.1.1) (2026-07-06)


### Bug Fixes

* add repository field to all npm packages ([39ca7a2](https://github.com/aimarchirico/commons/commit/39ca7a266824698c75e9669de1aaa38e620b2d6c))
* **commons-firebase-client:** force release ([f6b030c](https://github.com/aimarchirico/commons/commit/f6b030c8645bbb290d955193962d09c7f02f3f94))

## [1.1.0](https://github.com/aimarchirico/commons/compare/commons-cloudflare-v1.0.0...commons-cloudflare-v1.1.0) (2026-07-04)


### Features

* add commons-cloudflare package for web-deploy glue ([1e8cb5f](https://github.com/aimarchirico/commons/commit/1e8cb5ffca48e83e272294fc648a7d42fb69cc2f))
* add commons-cloudflare package for web-deploy glue ([8b46492](https://github.com/aimarchirico/commons/commit/8b46492b6fc2b427a158c2652601edd402e1088b))
