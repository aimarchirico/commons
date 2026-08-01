# Changelog

## [4.2.0](https://github.com/aimarchirico/commons/compare/commons-google-signin-v4.1.0...commons-google-signin-v4.2.0) (2026-08-01)


### Features

* **commons-ts:** add default-export-shape lint rule and update ESLint base config ([4f631e4](https://github.com/aimarchirico/commons/commit/4f631e4750fd715aa172a75f834a0a3381eef265))
* **commons-ts:** add shared 80% vitest coverage config ([3598d0d](https://github.com/aimarchirico/commons/commit/3598d0d3795f3313e44c2b4a0de74c6d40a786d5))

## [4.1.0](https://github.com/aimarchirico/commons/compare/commons-google-signin-v4.0.0...commons-google-signin-v4.1.0) (2026-07-30)


### Features

* **commons-python:** mirror doc-comment enforcement ([e844994](https://github.com/aimarchirico/commons/commit/e8449949c9c5ce3332e12e566171e69da0d921ef))
* tighten comment and suppression discipline ([b2f362e](https://github.com/aimarchirico/commons/commit/b2f362ecfce6271bfac3e9309e72c07c6982c74c))


### Bug Fixes

* satisfy public-jsdoc-only, commons-ts type check, and docs line length ([232cf7d](https://github.com/aimarchirico/commons/commit/232cf7df1ce5779141f3a7071a4d379188e1c2b9))

## [4.0.0](https://github.com/aimarchirico/commons/compare/commons-google-signin-v3.0.1...commons-google-signin-v4.0.0) (2026-07-29)


### ⚠ BREAKING CHANGES

* enforce documentation standards via commons-ts and commons-convention

### Features

* enforce documentation standards via commons-ts and commons-convention ([d6f5028](https://github.com/aimarchirico/commons/commit/d6f5028dbedbd74cdb52d92568fadd44e797e40b))


### Bug Fixes

* **commons-firebase-client,commons-google-signin:** satisfy new jsdoc content rules ([43c1f79](https://github.com/aimarchirico/commons/commit/43c1f79b48754dbaee1491c77bff75a7e6f080e6))

## [3.0.1](https://github.com/aimarchirico/commons/compare/commons-google-signin-v3.0.0...commons-google-signin-v3.0.1) (2026-07-24)


### Bug Fixes

* update tsconfig extends to use tsconfig-base in firebase-client and google-signin packages ([b159416](https://github.com/aimarchirico/commons/commit/b1594166d59ac205e70c592d711dfde3ae3e3563))

## [3.0.0](https://github.com/aimarchirico/commons/compare/commons-google-signin-v2.0.0...commons-google-signin-v3.0.0) (2026-07-23)


### ⚠ BREAKING CHANGES

* **eslint:** remove eslint-architecture export and integrate folderRule

### Features

* **eslint:** remove eslint-architecture export and integrate folderRule ([e921ce7](https://github.com/aimarchirico/commons/commit/e921ce786881d065f6ac311a3c1d488c76e00155))

## [2.0.0](https://github.com/aimarchirico/commons/compare/commons-google-signin-v1.2.1...commons-google-signin-v2.0.0) (2026-07-18)


### ⚠ BREAKING CHANGES

* **google-signin:** consumers must replace the @react-native-google-signin/google-signin peer dependency with react-native-nitro-google-signin + react-native-nitro-modules, and swap the Expo config plugin accordingly.

### Features

* **google-signin:** migrate to react-native-nitro-google-signin ([85178ec](https://github.com/aimarchirico/commons/commit/85178ec8a1cb9c087b64d8523aad261701cf2332))
* migrate google-signin to nitro + split firebase client by platform ([e7d877d](https://github.com/aimarchirico/commons/commit/e7d877d9707cf670bd2c017722c55f1d95cb9166))

## [1.2.1](https://github.com/aimarchirico/commons/compare/commons-google-signin-v1.2.0...commons-google-signin-v1.2.1) (2026-07-18)


### Bug Fixes

* return a value for every google sign-in outcome ([1ccc09a](https://github.com/aimarchirico/commons/commit/1ccc09a130e97d08ac8276e27aa226bd5b7909fa))

## [1.2.0](https://github.com/aimarchirico/commons/compare/commons-google-signin-v1.1.2...commons-google-signin-v1.2.0) (2026-07-17)


### Features

* **tools:** add root:fix task and fix docs pathing ([8d75182](https://github.com/aimarchirico/commons/commit/8d75182043713d6d389532ed60c783781df2cdad))

## [1.1.2](https://github.com/aimarchirico/commons/compare/commons-google-signin-v1.1.1...commons-google-signin-v1.1.2) (2026-07-06)


### Bug Fixes

* **commons-firebase-client:** force release ([f6b030c](https://github.com/aimarchirico/commons/commit/f6b030c8645bbb290d955193962d09c7f02f3f94))
* **commons-google-signin:** add repository field to package.json ([0f42e0e](https://github.com/aimarchirico/commons/commit/0f42e0ebe6a6a920d8e1b689b54a59e36d301d2f))

## [1.1.1](https://github.com/aimarchirico/commons/compare/commons-google-signin-v1.1.0...commons-google-signin-v1.1.1) (2026-07-05)


### Bug Fixes

* **commons-google-signin:** consume renamed commons-firebase-client ([5cf0b70](https://github.com/aimarchirico/commons/commit/5cf0b70a80857e2fe3f6cdce5a5d476e08446748))

## [1.1.0](https://github.com/aimarchirico/commons/compare/commons-google-signin-v1.0.0...commons-google-signin-v1.1.0) (2026-07-05)


### Features

* add commons-firebase and commons-google-signin packages ([97bdfff](https://github.com/aimarchirico/commons/commit/97bdffff71d31d5388f5c4a4de4ef1cc0a369903))
* add commons-firebase and commons-google-signin packages ([46f17a8](https://github.com/aimarchirico/commons/commit/46f17a8ed94b507b2b2ef84060202fbf5dc867a0))


### Bug Fixes

* update check script to include TypeScript compilation ([4bbfaec](https://github.com/aimarchirico/commons/commit/4bbfaecd0f9a4a2e86052512bd98b5fd97700fba))
* update react and typescript dependencies in pnpm-lock.yaml ([1d4c41c](https://github.com/aimarchirico/commons/commit/1d4c41c3d545abd2f13d4d0d1dcf48764aae9452))
