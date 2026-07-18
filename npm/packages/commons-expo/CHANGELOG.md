# Changelog

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
