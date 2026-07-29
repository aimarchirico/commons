# Changelog

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
