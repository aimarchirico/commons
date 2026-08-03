# Changelog

## [3.4.0](https://github.com/aimarchirico/commons/compare/commons-firebase-client-v3.3.0...commons-firebase-client-v3.4.0) (2026-08-03)


### Features

* **settings:** add attribution configuration to settings.json ([e271e28](https://github.com/aimarchirico/commons/commit/e271e28cada7dfab52452edcb266c8bf9ec66569))


### Bug Fixes

* **commons-firebase-client:** actually invoke CLI subcommand handlers ([451b7b2](https://github.com/aimarchirico/commons/commit/451b7b2dc17cffcd6f4a744bc2ab0b707de97850))

## [3.3.0](https://github.com/aimarchirico/commons/compare/commons-firebase-client-v3.2.0...commons-firebase-client-v3.3.0) (2026-08-02)


### Features

* **eslint:** require JSDoc on default export call expressions and wrap configs in defineConfig ([a94e91e](https://github.com/aimarchirico/commons/commit/a94e91ee5dd122477a99a9eb2034559194ac91ab))


### Bug Fixes

* **npm:** fix npm:check failures across ts, cloudflare, expo, firebase-client packages ([4aa99f5](https://github.com/aimarchirico/commons/commit/4aa99f58d134088db92bf53f90a656733ccf0c71))
* **npm:** scope build includes to real entry points, stop excluding bin from coverage ([57de6b2](https://github.com/aimarchirico/commons/commit/57de6b26dd303e7bc196cef74a16b4eb4e4446eb))

## [3.2.0](https://github.com/aimarchirico/commons/compare/commons-firebase-client-v3.1.0...commons-firebase-client-v3.2.0) (2026-08-01)


### Features

* **commons-ts:** add shared 80% vitest coverage config ([3598d0d](https://github.com/aimarchirico/commons/commit/3598d0d3795f3313e44c2b4a0de74c6d40a786d5))

## [3.1.0](https://github.com/aimarchirico/commons/compare/commons-firebase-client-v3.0.0...commons-firebase-client-v3.1.0) (2026-07-30)


### Features

* **commons-python:** mirror doc-comment enforcement ([e844994](https://github.com/aimarchirico/commons/commit/e8449949c9c5ce3332e12e566171e69da0d921ef))
* tighten comment and suppression discipline ([b2f362e](https://github.com/aimarchirico/commons/commit/b2f362ecfce6271bfac3e9309e72c07c6982c74c))


### Bug Fixes

* satisfy public-jsdoc-only, commons-ts type check, and docs line length ([232cf7d](https://github.com/aimarchirico/commons/commit/232cf7df1ce5779141f3a7071a4d379188e1c2b9))

## [3.0.0](https://github.com/aimarchirico/commons/compare/commons-firebase-client-v2.1.1...commons-firebase-client-v3.0.0) (2026-07-29)


### ⚠ BREAKING CHANGES

* enforce documentation standards via commons-ts and commons-convention

### Features

* enforce documentation standards via commons-ts and commons-convention ([d6f5028](https://github.com/aimarchirico/commons/commit/d6f5028dbedbd74cdb52d92568fadd44e797e40b))


### Bug Fixes

* **commons-firebase-client,commons-google-signin:** satisfy new jsdoc content rules ([43c1f79](https://github.com/aimarchirico/commons/commit/43c1f79b48754dbaee1491c77bff75a7e6f080e6))

## [2.1.1](https://github.com/aimarchirico/commons/compare/commons-firebase-client-v2.1.0...commons-firebase-client-v2.1.1) (2026-07-24)


### Bug Fixes

* update tsconfig extends to use tsconfig-base in firebase-client and google-signin packages ([b159416](https://github.com/aimarchirico/commons/commit/b1594166d59ac205e70c592d711dfde3ae3e3563))

## [2.1.0](https://github.com/aimarchirico/commons/compare/commons-firebase-client-v2.0.0...commons-firebase-client-v2.1.0) (2026-07-19)


### Features

* **npm:** migrate package CLI scripts from mjs to ts ([f834145](https://github.com/aimarchirico/commons/commit/f834145b5c9eb8330c41b352e378f92cb89b1566))

## [2.0.0](https://github.com/aimarchirico/commons/compare/commons-firebase-client-v1.1.0...commons-firebase-client-v2.0.0) (2026-07-18)


### ⚠ BREAKING CHANGES

* bin invocations now require a subcommand. The old bare bin keys (commons-cloudflare-fix, commons-expo-build-android, commons-firebase-client-decode-google-services) are removed.

### Features

* **firebase-client:** split auth wrapper into platform files ([2ceea86](https://github.com/aimarchirico/commons/commit/2ceea86238d22495875b41a654aad2297c9cd458))
* migrate google-signin to nitro + split firebase client by platform ([e7d877d](https://github.com/aimarchirico/commons/commit/e7d877d9707cf670bd2c017722c55f1d95cb9166))
* standardize commons bins on &lt;package&gt; &lt;verb&gt; subcommands ([e61ea8e](https://github.com/aimarchirico/commons/commit/e61ea8e26fb19960a52fe2249d3f231b502cfca7))

## [1.1.0](https://github.com/aimarchirico/commons/compare/commons-firebase-client-v1.0.2...commons-firebase-client-v1.1.0) (2026-07-17)


### Features

* **tools:** add root:fix task and fix docs pathing ([8d75182](https://github.com/aimarchirico/commons/commit/8d75182043713d6d389532ed60c783781df2cdad))

## [1.0.2](https://github.com/aimarchirico/commons/compare/commons-firebase-client-v1.0.1...commons-firebase-client-v1.0.2) (2026-07-06)


### Bug Fixes

* **commons-firebase-client:** add repository field to package.json ([a8813ac](https://github.com/aimarchirico/commons/commit/a8813ac13ecdf0de948c513c57bd1359f5639d08))
* **commons-firebase-client:** force release ([f6b030c](https://github.com/aimarchirico/commons/commit/f6b030c8645bbb290d955193962d09c7f02f3f94))
* **commons-firebase-client:** trigger release ([7ea7887](https://github.com/aimarchirico/commons/commit/7ea788758925b4ddf31f6b9716ba2694efe0b472))

## [1.0.1](https://github.com/aimarchirico/commons/compare/commons-firebase-client-v1.0.0...commons-firebase-client-v1.0.1) (2026-07-05)


### Bug Fixes

* **commons-firebase-client:** read decode output path from env ([ea93f2f](https://github.com/aimarchirico/commons/commit/ea93f2f2dbb7e9fba5f9a6c4a66ac37438fc467a))

## 1.0.0 (2026-07-05)


### Features

* **commons-firebase-client:** rename from commons-firebase ([c486858](https://github.com/aimarchirico/commons/commit/c48685871538e47a7903f346688c93bb97f43b89))

## Changelog
