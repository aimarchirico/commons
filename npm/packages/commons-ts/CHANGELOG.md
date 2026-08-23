# Changelog

## [3.6.0](https://github.com/aimarchirico/commons/compare/commons-ts-v3.5.0...commons-ts-v3.6.0) (2026-08-23)


### Features

* **commons-ts:** require jsdoc only on the supported node types ([52d8ae3](https://github.com/aimarchirico/commons/commit/52d8ae3ae688ab67f320b0f17b31b9a22758ed08))
* stop requiring documentation the guide prohibits writing ([85db739](https://github.com/aimarchirico/commons/commit/85db739678f52def46c421b8ea4fa53e50970b4e))

## [3.5.0](https://github.com/aimarchirico/commons/compare/commons-ts-v3.4.5...commons-ts-v3.5.0) (2026-08-23)


### Features

* adopt design document standard and chain it through the skill lifecycle ([f150d66](https://github.com/aimarchirico/commons/commit/f150d668342dea626ce22b02dd251c91aadbf1b4))
* **commons-ts:** permit inline comments and remove public-jsdoc-only ([d5aecf0](https://github.com/aimarchirico/commons/commit/d5aecf0c853edfdcbb78415e284682e7e78a749f))
* permit inline comments and disambiguate service api from public code contracts ([2233015](https://github.com/aimarchirico/commons/commit/22330152bf191a1f91d37d6ca6759f36d6954a3c))

## [3.4.5](https://github.com/aimarchirico/commons/compare/commons-ts-v3.4.4...commons-ts-v3.4.5) (2026-08-07)


### Bug Fixes

* **comments.ts:** add ObjectExpression to eligible JSDoc visitors ([0959bd0](https://github.com/aimarchirico/commons/commit/0959bd0800ef35c6d69aa95d0e0f0637822b30fa))
* **comments.ts:** add ObjectExpression to eligible JSDoc visitors ([1a8a1d2](https://github.com/aimarchirico/commons/commit/1a8a1d2ca76c65525d2bd9fa27057bf08c9758e8))
* **default-export-shape.ts:** reorder allowed export shapes for clarity ([c1c4963](https://github.com/aimarchirico/commons/commit/c1c4963a2af85cabe0625f1670c294949e00a981))

## [3.4.4](https://github.com/aimarchirico/commons/compare/commons-ts-v3.4.3...commons-ts-v3.4.4) (2026-08-07)


### Bug Fixes

* **eslint-base.ts:** allow additional config file extensions for ESLint ([0f2f544](https://github.com/aimarchirico/commons/commit/0f2f5445c7a3582df40d617836e02d9bf502d702))
* **eslint-base.ts:** allow additional config file extensions for ESLint ([d72207c](https://github.com/aimarchirico/commons/commit/d72207ca6f762b2dd6dc9fe82aa9e118c739d0fb))

## [3.4.3](https://github.com/aimarchirico/commons/compare/commons-ts-v3.4.2...commons-ts-v3.4.3) (2026-08-02)


### Bug Fixes

* **commons-ts:** recognize CJS module.exports as exported in public-jsdoc-only ([c986280](https://github.com/aimarchirico/commons/commit/c986280ac5fc0d656e434db5e896384a991b71ed))
* **commons-ts:** recognize CJS module.exports as exported in public-jsdoc-only ([818a92d](https://github.com/aimarchirico/commons/commit/818a92d914095eaa8e0ab1c45e8556f8053e44bf))

## [3.4.2](https://github.com/aimarchirico/commons/compare/commons-ts-v3.4.1...commons-ts-v3.4.2) (2026-08-02)


### Bug Fixes

* **commons-ts:** allow object literal default exports in config files ([fedf427](https://github.com/aimarchirico/commons/commit/fedf4270e6259451581706d9e6f00859908a53a4))
* **commons-ts:** allow object literal default exports in config files ([f2b54e3](https://github.com/aimarchirico/commons/commit/f2b54e3356980eb73ceaf7c3dbeba0d3e5455f84))

## [3.4.1](https://github.com/aimarchirico/commons/compare/commons-ts-v3.4.0...commons-ts-v3.4.1) (2026-08-02)


### Bug Fixes

* **package:** remove unused vitest-coverage exports from package.json ([2d9db11](https://github.com/aimarchirico/commons/commit/2d9db11da903e6e37c60eefdec86576eaedd684f))
* **package:** remove unused vitest-coverage exports from package.json ([fb98b8f](https://github.com/aimarchirico/commons/commit/fb98b8f10251832da4b3a7e273b276a9991e9bbf))

## [3.4.0](https://github.com/aimarchirico/commons/compare/commons-ts-v3.3.0...commons-ts-v3.4.0) (2026-08-02)


### Features

* **eslint:** require JSDoc on default export call expressions and wrap configs in defineConfig ([a94e91e](https://github.com/aimarchirico/commons/commit/a94e91ee5dd122477a99a9eb2034559194ac91ab))


### Bug Fixes

* **commons-ts:** add types field to vitest-coverage subpath export ([a4ef899](https://github.com/aimarchirico/commons/commit/a4ef89976c666701b3953c8cf942e36c9ef95282)), closes [#308](https://github.com/aimarchirico/commons/issues/308)
* **commons-ts:** exclude test files from build and stop excluding bin from coverage ([49e5c32](https://github.com/aimarchirico/commons/commit/49e5c324acec03b96000f86e5398527b8fd50b00))
* **commons-ts:** require call expression or named declaration in default exports ([6b59a58](https://github.com/aimarchirico/commons/commit/6b59a58ca6db8c37ac10d59f1bb98315a2549776))
* **npm:** fix npm:check failures across ts, cloudflare, expo, firebase-client packages ([4aa99f5](https://github.com/aimarchirico/commons/commit/4aa99f58d134088db92bf53f90a656733ccf0c71))
* **npm:** scope build includes to real entry points, stop excluding bin from coverage ([57de6b2](https://github.com/aimarchirico/commons/commit/57de6b26dd303e7bc196cef74a16b4eb4e4446eb))
* **npm:** update README for lint and fix vitest configuration export ([2a414f7](https://github.com/aimarchirico/commons/commit/2a414f74ffd20b7d3dffa07c9b459156d0caeced))

## [3.3.0](https://github.com/aimarchirico/commons/compare/commons-ts-v3.2.0...commons-ts-v3.3.0) (2026-08-01)


### Features

* **commons-ts:** add default-export-shape lint rule and update ESLint base config ([4f631e4](https://github.com/aimarchirico/commons/commit/4f631e4750fd715aa172a75f834a0a3381eef265))
* **commons-ts:** add shared 80% vitest coverage config ([3598d0d](https://github.com/aimarchirico/commons/commit/3598d0d3795f3313e44c2b4a0de74c6d40a786d5))
* **commons-ts:** add shared 80% vitest coverage config ([ea92178](https://github.com/aimarchirico/commons/commit/ea921784cdfab0e388593aca033808e2adb37ee0))

## [3.2.0](https://github.com/aimarchirico/commons/compare/commons-ts-v3.1.1...commons-ts-v3.2.0) (2026-07-30)


### Features

* **commons-python:** mirror doc-comment enforcement ([e844994](https://github.com/aimarchirico/commons/commit/e8449949c9c5ce3332e12e566171e69da0d921ef))
* **commons-ts:** tighten comment and suppression discipline ([9893615](https://github.com/aimarchirico/commons/commit/989361590121db84ec1934ffa06b62ab34d80bed))
* tighten comment and suppression discipline ([b2f362e](https://github.com/aimarchirico/commons/commit/b2f362ecfce6271bfac3e9309e72c07c6982c74c))


### Bug Fixes

* **comments:** handle undefined declaration in resolveVariableDeclarationOwner ([194d47f](https://github.com/aimarchirico/commons/commit/194d47fd24ed4e46eb55ea805dc97321c0ae6c48))
* **commons-ts:** resolve variable-declarator JSDoc association bug ([f9716de](https://github.com/aimarchirico/commons/commit/f9716de7fcfa1ca8498663fbb8e1a0a2c3f1ecd9))
* **commons-ts:** satisfy public-jsdoc-only in folders and gitignore ([dcde90c](https://github.com/aimarchirico/commons/commit/dcde90c884c53431a3a9e2e1ae1f7058c57cb9ad))
* satisfy public-jsdoc-only, commons-ts type check, and docs line length ([232cf7d](https://github.com/aimarchirico/commons/commit/232cf7df1ce5779141f3a7071a4d379188e1c2b9))

## [3.1.1](https://github.com/aimarchirico/commons/compare/commons-ts-v3.1.0...commons-ts-v3.1.1) (2026-07-29)


### Bug Fixes

* **commons-ts:** allow x-release-please-version marker comments ([13cea02](https://github.com/aimarchirico/commons/commit/13cea02807578826207c9749cd017d30d3b2dcc2))

## [3.1.0](https://github.com/aimarchirico/commons/compare/commons-ts-v3.0.0...commons-ts-v3.1.0) (2026-07-29)


### Features

* clean up package exports and make Cloudflare proxy a root export ([cf45ef8](https://github.com/aimarchirico/commons/commit/cf45ef8612bc7b37b81373a7bca618016cd91d8c))

## [3.0.0](https://github.com/aimarchirico/commons/compare/commons-ts-v2.0.3...commons-ts-v3.0.0) (2026-07-29)


### ⚠ BREAKING CHANGES

* enforce documentation standards via commons-ts and commons-convention
* **commons-ts:** consumers of the shared ESLint configuration now fail `check` on undocumented exports and on any non-documentation comment.

### Features

* add reusable provisioning commands for scaffolded projects ([3c17e79](https://github.com/aimarchirico/commons/commit/3c17e79b7a7067784fe1ca24871b5fcbb4a5bedf))
* **commons-github:** add repository provisioning commands ([5024ad6](https://github.com/aimarchirico/commons/commit/5024ad6a46373803459d12682c37e80e132262dd)), closes [#183](https://github.com/aimarchirico/commons/issues/183) [#184](https://github.com/aimarchirico/commons/issues/184) [#185](https://github.com/aimarchirico/commons/issues/185) [#186](https://github.com/aimarchirico/commons/issues/186) [#187](https://github.com/aimarchirico/commons/issues/187) [#182](https://github.com/aimarchirico/commons/issues/182)
* **commons-ts:** add provisioning env and reporting helpers ([989754d](https://github.com/aimarchirico/commons/commit/989754dadebe457a70a40cb6d62f40054315a934)), closes [#175](https://github.com/aimarchirico/commons/issues/175) [#176](https://github.com/aimarchirico/commons/issues/176) [#174](https://github.com/aimarchirico/commons/issues/174)
* **commons-ts:** require jsdoc and allow only doc comments ([e8e1c32](https://github.com/aimarchirico/commons/commit/e8e1c32394dbf7aebd4643f0b5126a7bb5764c26))
* **commons-ts:** validate jsdoc content and scope prettier rules independently of code rules ([fe1fa9c](https://github.com/aimarchirico/commons/commit/fe1fa9c7b67a162aa9fc0d39a616863272759243))
* enforce documentation standards via commons-ts and commons-convention ([d6f5028](https://github.com/aimarchirico/commons/commit/d6f5028dbedbd74cdb52d92568fadd44e797e40b))


### Bug Fixes

* **commons-ts:** scope documentation rules to typescript files ([569d130](https://github.com/aimarchirico/commons/commit/569d1309575f3f01e754888fca009592ea95dfc6))

## [2.0.3](https://github.com/aimarchirico/commons/compare/commons-ts-v2.0.2...commons-ts-v2.0.3) (2026-07-25)


### Bug Fixes

* **tsconfig-base.json:** remove @ alias ([116ee1b](https://github.com/aimarchirico/commons/commit/116ee1bfba6cb820e69b8dcbfc59e86b43a8590b))

## [2.0.2](https://github.com/aimarchirico/commons/compare/commons-ts-v2.0.1...commons-ts-v2.0.2) (2026-07-24)


### Bug Fixes

* **commons-ts:** add jiti dependency for typescript eslint config loading ([97b33dd](https://github.com/aimarchirico/commons/commit/97b33dd7e5817a20cf8e61992389bc95bf60d65c))

## [2.0.1](https://github.com/aimarchirico/commons/compare/commons-ts-v2.0.0...commons-ts-v2.0.1) (2026-07-24)


### Bug Fixes

* add comment to trigger release ([85a5af2](https://github.com/aimarchirico/commons/commit/85a5af28400c8967fbd1b9e450448571277052bb))
* update export paths for tsconfig in package.json files ([376d617](https://github.com/aimarchirico/commons/commit/376d617789bd2b1b23aa5642b3db184ab3201f87))

## [2.0.0](https://github.com/aimarchirico/commons/compare/commons-ts-v1.6.0...commons-ts-v2.0.0) (2026-07-23)


### ⚠ BREAKING CHANGES

* **eslint:** remove eslint-architecture export and integrate folderRule

### Features

* **eslint:** remove eslint-architecture export and integrate folderRule ([e921ce7](https://github.com/aimarchirico/commons/commit/e921ce786881d065f6ac311a3c1d488c76e00155))

## [1.6.0](https://github.com/aimarchirico/commons/compare/commons-ts-v1.5.0...commons-ts-v1.6.0) (2026-07-22)


### Features

* **commons:** implement base folder logic and update openapi generation path ([2df60a5](https://github.com/aimarchirico/commons/commit/2df60a53ea07144e7c981c839de78066ef052f98))

## [1.5.0](https://github.com/aimarchirico/commons/compare/commons-ts-v1.4.1...commons-ts-v1.5.0) (2026-07-19)


### Features

* **npm:** migrate package CLI scripts from mjs to ts ([f834145](https://github.com/aimarchirico/commons/commit/f834145b5c9eb8330c41b352e378f92cb89b1566))

## [1.4.1](https://github.com/aimarchirico/commons/compare/commons-ts-v1.4.0...commons-ts-v1.4.1) (2026-07-18)


### Bug Fixes

* **eslint:** update eslint configurations to include specific rules for eslint.ts files ([8210eef](https://github.com/aimarchirico/commons/commit/8210eef5e1d7bf0e66b3627e7cb80ab41635a882))
* **eslint:** update file patterns and rules for config files ([c061d00](https://github.com/aimarchirico/commons/commit/c061d002a832dde5bae45257b13d5c5e60a94dad))

## [1.4.0](https://github.com/aimarchirico/commons/compare/commons-ts-v1.3.1...commons-ts-v1.4.0) (2026-07-18)


### Features

* migrate google-signin to nitro + split firebase client by platform ([e7d877d](https://github.com/aimarchirico/commons/commit/e7d877d9707cf670bd2c017722c55f1d95cb9166))

## [1.3.1](https://github.com/aimarchirico/commons/compare/commons-ts-v1.3.0...commons-ts-v1.3.1) (2026-07-18)


### Bug Fixes

* include .cjs files in TypeScript configuration and ESLint rules ([1bb20da](https://github.com/aimarchirico/commons/commit/1bb20dae86d41491fdf0cc83ad309c77478329a4))
* update TypeScript configuration file references to use consistent naming ([fc0958b](https://github.com/aimarchirico/commons/commit/fc0958b47d5be5317cce61ca91be8ddcc864510d))

## [1.3.0](https://github.com/aimarchirico/commons/compare/commons-ts-v1.2.1...commons-ts-v1.3.0) (2026-07-18)


### Features

* add stricter options and configDir paths to shared tsconfig ([134743f](https://github.com/aimarchirico/commons/commit/134743f892f0452e1ae5f8d0dd9cf6d3924fb88c))

## [1.2.1](https://github.com/aimarchirico/commons/compare/commons-ts-v1.2.0...commons-ts-v1.2.1) (2026-07-18)


### Bug Fixes

* disable filename-naming-convention rule for specific file patterns in eslint configs ([ea975fe](https://github.com/aimarchirico/commons/commit/ea975fe640986f7b9abb8c1901e66d94dab30bd0))
* update filename-naming-convention rule to include cjs files ([7a703df](https://github.com/aimarchirico/commons/commit/7a703df9768234575e6a5473ca97800fd1a5c339))

## [1.2.0](https://github.com/aimarchirico/commons/compare/commons-ts-v1.1.1...commons-ts-v1.2.0) (2026-07-17)


### Features

* **eslint:** convert js configs to ts and mjs ([9b577f1](https://github.com/aimarchirico/commons/commit/9b577f107f25c6782acd53ba68ec9e6d85a16e64))
* **eslint:** ignore all git-ignored paths, including nested .gitignores ([b272ae1](https://github.com/aimarchirico/commons/commit/b272ae19baf5551ac89579ba1c4434db1b22ee86))
* **eslint:** move json linting back to commons-ts base config ([ec35e5c](https://github.com/aimarchirico/commons/commit/ec35e5c6487106c625226ba63fa922afa63f6be2))
* **tools:** add global eslint config and yaml/json linting ([5180e43](https://github.com/aimarchirico/commons/commit/5180e4333aabf8ad54dd35c90454cea98e64bacb))
