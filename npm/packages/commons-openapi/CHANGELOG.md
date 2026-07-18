# Changelog

## [2.0.0](https://github.com/aimarchirico/commons/compare/commons-openapi-v1.2.0...commons-openapi-v2.0.0) (2026-07-18)


### ⚠ BREAKING CHANGES

* bin invocations now require a subcommand. The old bare bin keys (commons-cloudflare-fix, commons-expo-build-android, commons-firebase-client-decode-google-services) are removed.

### Features

* standardize commons bins on &lt;package&gt; &lt;verb&gt; subcommands ([e61ea8e](https://github.com/aimarchirico/commons/commit/e61ea8e26fb19960a52fe2249d3f231b502cfca7))

## [1.2.0](https://github.com/aimarchirico/commons/compare/commons-openapi-v1.1.3...commons-openapi-v1.2.0) (2026-07-17)


### Features

* **tools:** add root:fix task and fix docs pathing ([8d75182](https://github.com/aimarchirico/commons/commit/8d75182043713d6d389532ed60c783781df2cdad))

## [1.1.3](https://github.com/aimarchirico/commons/compare/commons-openapi-v1.1.2...commons-openapi-v1.1.3) (2026-07-15)


### Bug Fixes

* **cli:** replace URI conversion with path normalization for OpenAPI client generation ([7001dcf](https://github.com/aimarchirico/commons/commit/7001dcf73fd50dc1fd1ee7b0f7c1dc7e4b2ccb52))

## [1.1.2](https://github.com/aimarchirico/commons/compare/commons-openapi-v1.1.1...commons-openapi-v1.1.2) (2026-07-15)


### Bug Fixes

* **cli:** use safe URI for OpenAPI client generation ([7a0f296](https://github.com/aimarchirico/commons/commit/7a0f296d05c48652c4ecabcde276ab2b0be99037))

## [1.1.1](https://github.com/aimarchirico/commons/compare/commons-openapi-v1.1.0...commons-openapi-v1.1.1) (2026-07-06)


### Bug Fixes

* add repository field to all npm packages ([39ca7a2](https://github.com/aimarchirico/commons/commit/39ca7a266824698c75e9669de1aaa38e620b2d6c))
* **commons-firebase-client:** force release ([f6b030c](https://github.com/aimarchirico/commons/commit/f6b030c8645bbb290d955193962d09c7f02f3f94))

## [1.1.0](https://github.com/aimarchirico/commons/compare/commons-openapi-v1.0.0...commons-openapi-v1.1.0) (2026-07-02)


### Features

* rename core to commons ([d06b90c](https://github.com/aimarchirico/commons/commit/d06b90cf5720d3db41d058769ada8bf50983dcfb))

## [0.0.3](https://github.com/aimarchirico/commons/compare/core-openapi-v0.0.2...core-openapi-v0.0.3) (2026-06-29)


### Bug Fixes

* **npm:** correct dependency classification and align package versions ([b636543](https://github.com/aimarchirico/commons/commit/b636543192de6f137874416481794044f023e0e7))
