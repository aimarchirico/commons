# Changelog

## [4.5.2](https://github.com/aimarchirico/commons/compare/commons-expo-v4.5.1...commons-expo-v4.5.2) (2026-08-03)


### Bug Fixes

* **docs:** align markdown tables and trim trailing blank line ([7e4b237](https://github.com/aimarchirico/commons/commit/7e4b2374212b97ba62630be49b17f5fff89435ae))

## [4.5.1](https://github.com/aimarchirico/commons/compare/commons-expo-v4.5.0...commons-expo-v4.5.1) (2026-08-03)


### Bug Fixes

* **commons-expo:** drop unreliable self-run guard on bin entry point ([4a470f2](https://github.com/aimarchirico/commons/commit/4a470f284e14f55d6df759313632a320ff9c8040))
* drop unreliable self-run guard on CLI bin entry points ([e438c69](https://github.com/aimarchirico/commons/commit/e438c69944693553766a7dd632db7b4b3b41e01b))

## [4.5.0](https://github.com/aimarchirico/commons/compare/commons-expo-v4.4.0...commons-expo-v4.5.0) (2026-08-03)


### Features

* **settings:** add attribution configuration to settings.json ([e271e28](https://github.com/aimarchirico/commons/commit/e271e28cada7dfab52452edcb266c8bf9ec66569))


### Bug Fixes

* **commons-expo:** actually invoke CLI subcommand handlers ([8a6247d](https://github.com/aimarchirico/commons/commit/8a6247d9e8d41194a30bb254f430d572a1a9fb93))

## [4.4.0](https://github.com/aimarchirico/commons/compare/commons-expo-v4.3.0...commons-expo-v4.4.0) (2026-08-02)


### Features

* **eslint:** require JSDoc on default export call expressions and wrap configs in defineConfig ([a94e91e](https://github.com/aimarchirico/commons/commit/a94e91ee5dd122477a99a9eb2034559194ac91ab))


### Bug Fixes

* **commons-expo:** remove dead build include for nonexistent services dir ([f76b5b8](https://github.com/aimarchirico/commons/commit/f76b5b801dae703e10ab7204ed19e599e5312cb3))
* **npm:** fix npm:check failures across ts, cloudflare, expo, firebase-client packages ([4aa99f5](https://github.com/aimarchirico/commons/commit/4aa99f58d134088db92bf53f90a656733ccf0c71))
* **npm:** scope build includes to real entry points, stop excluding bin from coverage ([57de6b2](https://github.com/aimarchirico/commons/commit/57de6b26dd303e7bc196cef74a16b4eb4e4446eb))

## [4.3.0](https://github.com/aimarchirico/commons/compare/commons-expo-v4.2.0...commons-expo-v4.3.0) (2026-08-01)


### Features

* **commons-ts:** add default-export-shape lint rule and update ESLint base config ([4f631e4](https://github.com/aimarchirico/commons/commit/4f631e4750fd715aa172a75f834a0a3381eef265))
* **commons-ts:** add shared 80% vitest coverage config ([3598d0d](https://github.com/aimarchirico/commons/commit/3598d0d3795f3313e44c2b4a0de74c6d40a786d5))

## [4.2.0](https://github.com/aimarchirico/commons/compare/commons-expo-v4.1.0...commons-expo-v4.2.0) (2026-07-30)


### Features

* tighten comment and suppression discipline ([b2f362e](https://github.com/aimarchirico/commons/commit/b2f362ecfce6271bfac3e9309e72c07c6982c74c))


### Bug Fixes

* **commons-expo:** satisfy public-jsdoc-only in bin scripts and lib ([c567611](https://github.com/aimarchirico/commons/commit/c56761123c4b1e75ae6a2217b02808d8ceb8989b))

## [4.1.0](https://github.com/aimarchirico/commons/compare/commons-expo-v4.0.0...commons-expo-v4.1.0) (2026-07-29)


### Features

* clean up package exports and make Cloudflare proxy a root export ([cf45ef8](https://github.com/aimarchirico/commons/commit/cf45ef8612bc7b37b81373a7bca618016cd91d8c))

## [4.0.0](https://github.com/aimarchirico/commons/compare/commons-expo-v3.0.2...commons-expo-v4.0.0) (2026-07-29)


### ⚠ BREAKING CHANGES

* enforce documentation standards via commons-ts and commons-convention
* **commons-expo:** `create-project` needs `eas-cli` declared by the consuming project; it is no longer installed transitively.
* **commons-expo:** a release build without `ANDROID_KEYSTORE_BASE64` fails rather than falling back to debug signing. Set `ANDROID_ALLOW_UNSIGNED` to opt in.
* **commons-expo:** `create-keystore` is replaced by `create-project` and `import-keystore`. `EAS_PROJECT_ID` and `ANDROID_APPLICATION_ID` are no longer inputs, and `eas` 21+ is expected on PATH.
* **commons-project:** subpaths `./env`, `./report`, and `./outputs` are removed in favor of root exports.
* **commons-expo:** `create-keystore` now requires `ANDROID_APPLICATION_ID` and no longer reads `ANDROID_KEYSTORE_FILE`. `EXPO_TOKEN` becomes optional, falling back to the local `eas login` session.

### Features

* add reusable provisioning commands for scaffolded projects ([3c17e79](https://github.com/aimarchirico/commons/commit/3c17e79b7a7067784fe1ca24871b5fcbb4a5bedf))
* **commons-expo:** add create-keystore ([ebee217](https://github.com/aimarchirico/commons/commit/ebee21741874a9b99949c185ed008d5baa92d8f4)), closes [#194](https://github.com/aimarchirico/commons/issues/194) [#195](https://github.com/aimarchirico/commons/issues/195) [#193](https://github.com/aimarchirico/commons/issues/193)
* **commons-expo:** provision through eas-cli instead of the Expo API ([7f1c683](https://github.com/aimarchirico/commons/commit/7f1c68395bc50c4f605d89c6ec5c8c877e5df0ae))
* **commons-expo:** resolve eas-cli from the lockfile instead of PATH ([7249f8c](https://github.com/aimarchirico/commons/commit/7249f8ca5782f8e02ebe80f515f5f56ac91ebc2a))
* **commons-expo:** store the Android keystore in EAS ([75de700](https://github.com/aimarchirico/commons/commit/75de70062c07cbb0aa9af8d7a7faaa9a85d910b3))
* enforce documentation standards via commons-ts and commons-convention ([d6f5028](https://github.com/aimarchirico/commons/commit/d6f5028dbedbd74cdb52d92568fadd44e797e40b))


### Bug Fixes

* **commons-expo:** fail instead of debug-signing an unsigned release ([7e4fd4d](https://github.com/aimarchirico/commons/commit/7e4fd4d2276db3d4cce483b90fda32c90da4a098))
* **commons-github,commons-cloudflare,commons-expo:** drop unused overrides, fail-fast keystore ([04b79a0](https://github.com/aimarchirico/commons/commit/04b79a075adb8062da2b605f31a3694b93354355))


### Code Refactoring

* **commons-expo:** make eas-cli an optional peer dependency ([ec695b4](https://github.com/aimarchirico/commons/commit/ec695b4121e631f2c46aaf9c47da7a1082eeb932))
* **commons-project:** export from root instead of subpaths ([6fda9b7](https://github.com/aimarchirico/commons/commit/6fda9b70ba31d370e53ca2df473c5f63baa2f37d))

## [3.0.2](https://github.com/aimarchirico/commons/compare/commons-expo-v3.0.1...commons-expo-v3.0.2) (2026-07-24)


### Bug Fixes

* update export paths for tsconfig in package.json files ([376d617](https://github.com/aimarchirico/commons/commit/376d617789bd2b1b23aa5642b3db184ab3201f87))
* update tsconfig extends to use tsconfig-base across multiple packages ([1b2bb2a](https://github.com/aimarchirico/commons/commit/1b2bb2a02ab320dd7750965927186aa56c4cb19a))

## [3.0.1](https://github.com/aimarchirico/commons/compare/commons-expo-v3.0.0...commons-expo-v3.0.1) (2026-07-24)


### Bug Fixes

* **expo:** extend eslint-architecture instead of eslint in commons-expo ([2b6eccc](https://github.com/aimarchirico/commons/commit/2b6ecccf636202d8656803ae2b07b85be3c14fa2))
* **folders.ts:** add inport from commons-ts ([aeb836d](https://github.com/aimarchirico/commons/commit/aeb836dafdcc27d1d0452d86c773118cf10c888b))
* **folders.ts:** rename incorrect import ([9bf2811](https://github.com/aimarchirico/commons/commit/9bf28118c120bd79d99a5cbe35fbed28c3efe49a))

## [3.0.0](https://github.com/aimarchirico/commons/compare/commons-expo-v2.2.0...commons-expo-v3.0.0) (2026-07-23)


### ⚠ BREAKING CHANGES

* **eslint:** remove eslint-architecture export and integrate folderRule

### Features

* **eslint:** remove eslint-architecture export and integrate folderRule ([e921ce7](https://github.com/aimarchirico/commons/commit/e921ce786881d065f6ac311a3c1d488c76e00155))

## [2.2.0](https://github.com/aimarchirico/commons/compare/commons-expo-v2.1.0...commons-expo-v2.2.0) (2026-07-22)


### Features

* **commons:** implement base folder logic and update openapi generation path ([2df60a5](https://github.com/aimarchirico/commons/commit/2df60a53ea07144e7c981c839de78066ef052f98))

## [2.1.0](https://github.com/aimarchirico/commons/compare/commons-expo-v2.0.1...commons-expo-v2.1.0) (2026-07-19)


### Features

* **npm:** migrate package CLI scripts from mjs to ts ([f834145](https://github.com/aimarchirico/commons/commit/f834145b5c9eb8330c41b352e378f92cb89b1566))

## [2.0.1](https://github.com/aimarchirico/commons/compare/commons-expo-v2.0.0...commons-expo-v2.0.1) (2026-07-18)


### Bug Fixes

* **eslint:** update eslint configurations to include specific rules for eslint.ts files ([8210eef](https://github.com/aimarchirico/commons/commit/8210eef5e1d7bf0e66b3627e7cb80ab41635a882))

## [2.0.0](https://github.com/aimarchirico/commons/compare/commons-expo-v1.3.2...commons-expo-v2.0.0) (2026-07-18)


### ⚠ BREAKING CHANGES

* bin invocations now require a subcommand. The old bare bin keys (commons-cloudflare-fix, commons-expo-build-android, commons-firebase-client-decode-google-services) are removed.

### Features

* migrate google-signin to nitro + split firebase client by platform ([e7d877d](https://github.com/aimarchirico/commons/commit/e7d877d9707cf670bd2c017722c55f1d95cb9166))
* standardize commons bins on &lt;package&gt; &lt;verb&gt; subcommands ([e61ea8e](https://github.com/aimarchirico/commons/commit/e61ea8e26fb19960a52fe2249d3f231b502cfca7))

## [1.3.2](https://github.com/aimarchirico/commons/compare/commons-expo-v1.3.1...commons-expo-v1.3.2) (2026-07-18)


### Bug Fixes

* correct tsconfig export path in package.json ([1bf4f2b](https://github.com/aimarchirico/commons/commit/1bf4f2bee2a2a3b39483df6afb689ef10ae99f17))
* update TypeScript configuration file references to use consistent naming ([fc0958b](https://github.com/aimarchirico/commons/commit/fc0958b47d5be5317cce61ca91be8ddcc864510d))

## [1.3.1](https://github.com/aimarchirico/commons/compare/commons-expo-v1.3.0...commons-expo-v1.3.1) (2026-07-18)


### Bug Fixes

* disable filename-naming-convention rule for specific file patterns in eslint configs ([ea975fe](https://github.com/aimarchirico/commons/commit/ea975fe640986f7b9abb8c1901e66d94dab30bd0))

## [1.3.0](https://github.com/aimarchirico/commons/compare/commons-expo-v1.2.0...commons-expo-v1.3.0) (2026-07-17)


### Features

* **expo:** restore commons-expo for configuration deduplication ([7d2b293](https://github.com/aimarchirico/commons/commit/7d2b293e83523da73337a8b0f248ff096d407077))

## [1.2.0](https://github.com/aimarchirico/commons/compare/commons-expo-v1.1.1...commons-expo-v1.2.0) (2026-07-07)


### Features

* **commons-expo:** add build-android helper for signed release builds ([2a85773](https://github.com/aimarchirico/commons/commit/2a857736cd66c5e5e724d4fa3231bcfda9134903))
* **commons-expo:** add build-android helper for signed release builds ([be6b785](https://github.com/aimarchirico/commons/commit/be6b785e1efc717518a111c1560b03bb6e80ab36))

## [1.1.1](https://github.com/aimarchirico/commons/compare/commons-expo-v1.1.0...commons-expo-v1.1.1) (2026-07-06)


### Bug Fixes

* add repository field to all npm packages ([39ca7a2](https://github.com/aimarchirico/commons/commit/39ca7a266824698c75e9669de1aaa38e620b2d6c))
* **commons-firebase-client:** force release ([f6b030c](https://github.com/aimarchirico/commons/commit/f6b030c8645bbb290d955193962d09c7f02f3f94))

## [1.1.0](https://github.com/aimarchirico/commons/compare/commons-expo-v1.0.0...commons-expo-v1.1.0) (2026-07-02)


### Features

* rename core to commons ([d06b90c](https://github.com/aimarchirico/commons/commit/d06b90cf5720d3db41d058769ada8bf50983dcfb))

## [0.1.3](https://github.com/aimarchirico/commons/compare/core-expo-v0.1.2...core-expo-v0.1.3) (2026-07-01)


### Bug Fixes

* **tsconfig:** add include to tsconfig ([42b68ad](https://github.com/aimarchirico/commons/commit/42b68ad5393d7c8d9a6a1f8387c2528737829d26))

## [0.1.2](https://github.com/aimarchirico/commons/compare/core-expo-v0.1.1...core-expo-v0.1.2) (2026-07-01)

### Bug Fixes

* **package:** update tsconfig export path in package.json ([edbc710](https://github.com/aimarchirico/commons/commit/edbc7107844027bf1ca246a35ee967ade274f0ca))

## [0.1.1](https://github.com/aimarchirico/commons/compare/core-expo-v0.1.0...core-expo-v0.1.1) (2026-06-29)

### Bug Fixes

* **npm:** correct dependency classification and align package versions ([b636543](https://github.com/aimarchirico/commons/commit/b636543192de6f137874416481794044f023e0e7))

## [0.1.0](https://github.com/aimarchirico/commons/compare/core-expo-v0.0.1...core-expo-v0.1.0) (2026-06-29)

### Features

* **repo:** migrate to pnpm workspace and reorganize repository structure ([06266b2](https://github.com/aimarchirico/commons/commit/06266b2daf9770e94592509c5168680be406f721))
