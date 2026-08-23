# Changelog

## [3.2.0](https://github.com/aimarchirico/commons/compare/commons-convention-v3.1.0...commons-convention-v3.2.0) (2026-08-23)


### Features

* adopt design document standard and chain it through the skill lifecycle ([f150d66](https://github.com/aimarchirico/commons/commit/f150d668342dea626ce22b02dd251c91aadbf1b4))
* **commons-convention:** permit inline comments and remove PublicKDocOnly ([1cca91b](https://github.com/aimarchirico/commons/commit/1cca91b4162045c39d50bb80ee084bb66cd6c6fb))
* permit inline comments and disambiguate service api from public code contracts ([2233015](https://github.com/aimarchirico/commons/commit/22330152bf191a1f91d37d6ca6759f36d6954a3c))


### Bug Fixes

* **commons-convention:** align detekt rule kdoc with contract standard and expand test coverage ([b7e9538](https://github.com/aimarchirico/commons/commit/b7e9538ea6517f3690681b775e12f1b35c6f8697))

## [3.1.0](https://github.com/aimarchirico/commons/compare/commons-convention-v3.0.0...commons-convention-v3.1.0) (2026-08-16)


### Features

* **commons-convention:** fail check when main sources lack tests ([aec6efc](https://github.com/aimarchirico/commons/commit/aec6efc6ceeb3a2c8ef449cad0b5d38273758565))
* **commons-convention:** fail check when main sources lack tests ([5b64592](https://github.com/aimarchirico/commons/commit/5b64592793fea5e8206720d9df4588a207b96ac8))


### Bug Fixes

* **commons-convention:** resolve SourceSetContainer at project scope ([0acc17d](https://github.com/aimarchirico/commons/commit/0acc17d9dedfd508165c7a4f1b00bcaf516a24b4))

## [3.0.0](https://github.com/aimarchirico/commons/compare/commons-convention-v2.3.0...commons-convention-v3.0.0) (2026-08-03)


### ⚠ BREAKING CHANGES

* **convention:** modules relying on `no.chirico.commons.convention.spring` for JPA entity all-open support or Spring Boot Postgres/web dependencies must additionally apply `no.chirico.commons.convention.postgresql` and/or `no.chirico.commons.convention.web`.

### Features

* **convention:** split postgresql and web deps out of spring plugin ([ea5a37a](https://github.com/aimarchirico/commons/commit/ea5a37a767a620c0383baf8eb94617fcbe77664c))

## [2.3.0](https://github.com/aimarchirico/commons/compare/commons-convention-v2.2.0...commons-convention-v2.3.0) (2026-08-02)


### Features

* **convention:** centralize test dependencies into kotlin and spring plugins ([70cc7b5](https://github.com/aimarchirico/commons/commit/70cc7b5b66462260a7e714b6868351af406e68ff))


### Bug Fixes

* **convention:** raise commons-convention branch coverage to 80% ([ec912b1](https://github.com/aimarchirico/commons/commit/ec912b134e1cdd4b659ff9edd15544e6213c9c56))
* **coverage:** enforce 80% line and branch coverage in Jacoco verification ([71a790a](https://github.com/aimarchirico/commons/commit/71a790a9d6ec81ba648e321f5c7f7491c8729451))
* **npm:** scope build includes to real entry points, stop excluding bin from coverage ([57de6b2](https://github.com/aimarchirico/commons/commit/57de6b26dd303e7bc196cef74a16b4eb4e4446eb))
* **tests:** fix KDoc comment formatting ([f60b66d](https://github.com/aimarchirico/commons/commit/f60b66d681e9142be210c89262d3835008710ec8))

## [2.2.0](https://github.com/aimarchirico/commons/compare/commons-convention-v2.1.0...commons-convention-v2.2.0) (2026-08-01)


### Features

* **commons-convention:** dogfood jacoco coverage on the plugin's own module ([14d7c64](https://github.com/aimarchirico/commons/commit/14d7c643f70e43ebc35c21f2931eb3356f64e487))
* **commons-convention:** enforce 80% jacoco line coverage in kotlin plugin ([0fb90f8](https://github.com/aimarchirico/commons/commit/0fb90f8438019105e742c02de8192f034c85eaa3))
* **commons-convention:** enforce 80% jacoco line coverage in kotlin plugin ([0f28374](https://github.com/aimarchirico/commons/commit/0f283744f08fbd4bc1f1f01ac00532ddd85e016d))
* **commons-convention:** enforce comment discipline on its own module ([8d41607](https://github.com/aimarchirico/commons/commit/8d41607fc3d1644e523b01ac1e58bb4456970455))
* **maven:** require KDoc on every public test declaration repo-wide ([6e1a576](https://github.com/aimarchirico/commons/commit/6e1a5766a04bdc0b17bdeb4e629a10e03bdd8ff3))


### Bug Fixes

* **commons-convention:** exclude test sources from PublicKDocOnly ([82d8c20](https://github.com/aimarchirico/commons/commit/82d8c20998f440354424d62e8c7a4eaa77f4fea3))
* **commons-convention:** resolve detekt-api metadata gap and cover the plugin's own module ([9056272](https://github.com/aimarchirico/commons/commit/9056272eff05de0955278056e809e58f50f983ee))
* **maven:** fix Kotlin test compile errors and JUnit platform launcher resolution ([44ec338](https://github.com/aimarchirico/commons/commit/44ec3380b1ea84c3ed1e0ba65e92a2782c827139))

## [2.1.0](https://github.com/aimarchirico/commons/compare/commons-convention-v2.0.0...commons-convention-v2.1.0) (2026-07-30)


### Features

* **commons-convention:** tighten Kotlin comment and suppression discipline ([c414cae](https://github.com/aimarchirico/commons/commit/c414caee96962a11d36effaf454dc9438770e371))
* **convention:** add FileLength and FileNaming detekt rules ([3dd98ce](https://github.com/aimarchirico/commons/commit/3dd98cee1486a67f2106e531e66a1a2564e99810))
* **convention:** move BaseConventionTest file checks into detekt ([024cde3](https://github.com/aimarchirico/commons/commit/024cde3573f0bd6137dd1ad2fc08af5e79e333a5))
* tighten comment and suppression discipline ([b2f362e](https://github.com/aimarchirico/commons/commit/b2f362ecfce6271bfac3e9309e72c07c6982c74c))


### Bug Fixes

* **convention:** remove unneeded excludes from FileLength rule ([29bdb05](https://github.com/aimarchirico/commons/commit/29bdb054356a19bda3975f1f55ce3929f1ecd2a8))

## [2.0.0](https://github.com/aimarchirico/commons/compare/commons-convention-v1.6.1...commons-convention-v2.0.0) (2026-07-29)


### ⚠ BREAKING CHANGES

* enforce documentation standards via commons-ts and commons-convention
* **commons-convention:** consumers of the convention plugin now fail `check` on any comment that is not a KDoc block.
* **commons-convention:** consumers of the convention plugin now fail `check` on undocumented public classes, functions, and properties.

### Features

* **commons-convention:** allow only kdoc comments ([2407ca2](https://github.com/aimarchirico/commons/commit/2407ca251cda697661a7b81ce5ef60ad73dd2a6b))
* **commons-convention:** require kdoc on public declarations ([b7f3b47](https://github.com/aimarchirico/commons/commit/b7f3b471c1ce80c781b9389353af7c473d7d76a6))
* **commons-convention:** validate kdoc content against the actual signature ([cba1cab](https://github.com/aimarchirico/commons/commit/cba1cab01efdb1fcc3a0a073f61d3253ee6a70b8))
* enforce documentation standards via commons-ts and commons-convention ([d6f5028](https://github.com/aimarchirico/commons/commit/d6f5028dbedbd74cdb52d92568fadd44e797e40b))


### Bug Fixes

* **commons-convention:** import File in the kotlin convention plugin ([84a7c6a](https://github.com/aimarchirico/commons/commit/84a7c6ab4fb7609359103f4929ce98a3595d65b0))

## [1.6.1](https://github.com/aimarchirico/commons/compare/commons-convention-v1.6.0...commons-convention-v1.6.1) (2026-07-21)


### Bug Fixes

* **kotlin:** add -java-parameters to freeCompilerArgs ([d4fbde1](https://github.com/aimarchirico/commons/commit/d4fbde14ff25abc502208ac14368d51110a00cdb))
* **kotlin:** add -java-parameters to freeCompilerArgs ([1390834](https://github.com/aimarchirico/commons/commit/1390834b71e6af1b8b0ed73f5458834b7adb2b22))

## [1.6.0](https://github.com/aimarchirico/commons/compare/commons-convention-v1.5.2...commons-convention-v1.6.0) (2026-07-19)


### Features

* **maven:** add mapstruct convention plugin ([4f4ceba](https://github.com/aimarchirico/commons/commit/4f4cebab38fb5164a650c9603069cf86350a6fdd))

## [1.5.2](https://github.com/aimarchirico/commons/compare/commons-convention-v1.5.1...commons-convention-v1.5.2) (2026-07-18)


### Bug Fixes

* add detekt dependency to check task ([47b2da3](https://github.com/aimarchirico/commons/commit/47b2da37f77a400b97d9348245a1e0815b27158a))
* remove detekt dependency from check task ([5ebe6b0](https://github.com/aimarchirico/commons/commit/5ebe6b08e4aa63d5a22e9c98217e72fcf23db7ee))

## [1.5.1](https://github.com/aimarchirico/commons/compare/commons-convention-v1.5.0...commons-convention-v1.5.1) (2026-07-18)


### Bug Fixes

* **commons-convention:** force release ([c55cb89](https://github.com/aimarchirico/commons/commit/c55cb89e371b3884ff855ad460aaadd8990595d0))
* **commons-convention:** remove release trigger comment ([58b82ba](https://github.com/aimarchirico/commons/commit/58b82baaf0138a60d5329e9a8dd2bfa97eea7ef4))

## [1.5.0](https://github.com/aimarchirico/commons/compare/commons-convention-v1.4.0...commons-convention-v1.5.0) (2026-07-07)


### Features

* **architecture:** derive jar archive names from module path ([89d1903](https://github.com/aimarchirico/commons/commit/89d1903a9a193a067eb8b275a1efe8c16394ef47))

## [1.4.0](https://github.com/aimarchirico/commons/compare/commons-convention-v1.3.0...commons-convention-v1.4.0) (2026-07-07)


### Features

* **architecture:** match nested :api and :impl module suffixes ([0b0a818](https://github.com/aimarchirico/commons/commit/0b0a818acfc67b44fe5420dfabafaee5a8c5b19b))
* **architecture:** match nested :api and :impl module suffixes ([9852b1a](https://github.com/aimarchirico/commons/commit/9852b1a6ce6118e6d4c4d3d9edba60e582f9be9c))

## [1.3.0](https://github.com/aimarchirico/commons/compare/commons-convention-v1.2.0...commons-convention-v1.3.0) (2026-07-06)


### Features

* **architecture:** strictly enforce -api and -impl suffixes ([f29efd0](https://github.com/aimarchirico/commons/commit/f29efd0b1e6e7b866087af0bdc52e8a2b250daf2))
* **architecture:** support -api and -impl suffixes ([33bd7ab](https://github.com/aimarchirico/commons/commit/33bd7abcac4b83540bd8abfc5c944d61fcc9d037))

## [1.2.0](https://github.com/aimarchirico/commons/compare/commons-convention-v1.1.1...commons-convention-v1.2.0) (2026-07-06)


### Features

* **convention:** add architecture enforcer plugin, remove BaseArchitectureTest ([a0cca50](https://github.com/aimarchirico/commons/commit/a0cca50b73acd7a266e8c1fe1dc3243540d5922b))
* **convention:** add architecture module-dependency enforcer plugin ([66d0c2b](https://github.com/aimarchirico/commons/commit/66d0c2b2c01ed5bdb05152a5ab682327dee59f94))

## [1.1.1](https://github.com/aimarchirico/commons/compare/commons-convention-v1.1.0...commons-convention-v1.1.1) (2026-07-06)


### Bug Fixes

* **commons-firebase-client:** force release ([f6b030c](https://github.com/aimarchirico/commons/commit/f6b030c8645bbb290d955193962d09c7f02f3f94))

## [1.1.0](https://github.com/aimarchirico/commons/compare/commons-convention-v1.0.0...commons-convention-v1.1.0) (2026-07-02)


### Features

* rename core to commons ([d06b90c](https://github.com/aimarchirico/commons/commit/d06b90cf5720d3db41d058769ada8bf50983dcfb))


### Bug Fixes

* bundle spring boot plugin into spring convention plugin and fix package names ([b30457e](https://github.com/aimarchirico/commons/commit/b30457e09082daa84eef6a9a254dde44a7dd79ba))

## [0.2.0](https://github.com/aimarchirico/commons/compare/core-build-logic-v0.1.0...core-build-logic-v0.2.0) (2026-06-29)


### Features

* **repo:** migrate to pnpm workspace and reorganize repository structure ([06266b2](https://github.com/aimarchirico/commons/commit/06266b2daf9770e94592509c5168680be406f721))

## [0.1.0](https://github.com/aimarchirico/commons/compare/v0.0.3...v0.1.0) (2026-06-29)


### Features

* **repo:** migrate to pnpm workspace and reorganize repository structure ([06266b2](https://github.com/aimarchirico/commons/commit/06266b2daf9770e94592509c5168680be406f721))
