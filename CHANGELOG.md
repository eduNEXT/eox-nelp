# Change Log

..
All enhancements and patches to eox_nelp will be documented
in this file.  It adheres to the structure of http://keepachangelog.com/ ,
but in reStructuredText instead of Markdown (for ease of incorporation into
Sphinx documentation and the PyPI description).

## v1.1.0-jlc-github-actions.0 - 2023-02-23

### [1.1.0-jlc-github-actions.0](https://github.com/eduNEXT/eox-nelp/compare/v1.0.0...v1.1.0-jlc-github-actions.0) (2023-02-23)

#### ⚠ BREAKING CHANGES

- change unnecessary file for course api
- improve quality for course api
- style quality and complexity

#### Features

- Add arabic translations to fixed strings ([bc685c7](https://github.com/eduNEXT/eox-nelp/commit/bc685c74223786696a4380779003b42befc33615))
- add base github actions ([2cdddd6](https://github.com/eduNEXT/eox-nelp/commit/2cdddd6ddf17a221bb4ab0ad724253bc7ff7d75f))
- add bump version action ([ce51a17](https://github.com/eduNEXT/eox-nelp/commit/ce51a17c2f8641bfbf3f9a2594ce0289c62da542))
- add map_mfe_config_keys implementation ([f54e058](https://github.com/eduNEXT/eox-nelp/commit/f54e058193fcd8bb18f51c7b4b0b85a111c99b15))
- add mfe config endpoint nelp flavour ([8fba961](https://github.com/eduNEXT/eox-nelp/commit/8fba9613d3b9a0b928f2979541c74b0f29dc0cca))
- Add middleware file that includes anew class that allows to extend the registration fields based on tenant settings ([f247bad](https://github.com/eduNEXT/eox-nelp/commit/f247baddfecded56acacc6ab2ae2c0e6ec503fa6))
- Add option to set extended profile field labels in different languages. ([96e9c10](https://github.com/eduNEXT/eox-nelp/commit/96e9c10ae696a188f55e2b6c0ed7bb9831091733))
- add pull request template ([012215d](https://github.com/eduNEXT/eox-nelp/commit/012215d823688d070f0df6f3e25795c7c1038084))
- add python test github action ([ff58089](https://github.com/eduNEXT/eox-nelp/commit/ff58089dc1650cf28b60910d838993842630520e))
- cache program command using eox-tenant ([995bc6e](https://github.com/eduNEXT/eox-nelp/commit/995bc6e4e895008429b824c0b224153e1b4c757d))
- change nesting  of `pgn-color-primary-base` ([e357e92](https://github.com/eduNEXT/eox-nelp/commit/e357e92f4540c7fe2fd8d1e484930963779cc561))
- change to group in pr issue assignment ([21a2e15](https://github.com/eduNEXT/eox-nelp/commit/21a2e15794270969256a8a9e44b312d73467dbb3))
- chnage extension of changelog to md ([e363eef](https://github.com/eduNEXT/eox-nelp/commit/e363eefd42ea29110a0a96cf2bea72983272b5bd)), closes [1#L27](https://github.com/eduNEXT/1/issues/L27)
- forbid change label of REGISTER__EXTRA_FIELD ([535117f](https://github.com/eduNEXT/eox-nelp/commit/535117f1c9b7aa84675dc7633adc1b2dbb0c7da1))
- Import cms signals handler module in order to register receivers ([a6610ce](https://github.com/eduNEXT/eox-nelp/commit/a6610cea938bebeb6aa952b2dc2a0a8ffa891569))
- makefile quality and translations ([e56eea3](https://github.com/eduNEXT/eox-nelp/commit/e56eea36b4f1e0ccc48e727e016d38f1de189f79))

#### Bug Fixes

- bump version in action dont need commit ([aa2bf96](https://github.com/eduNEXT/eox-nelp/commit/aa2bf968b0122da764ad8abc708cd92ae21bd0c3))
- our package has changelog in rst ([a908577](https://github.com/eduNEXT/eox-nelp/commit/a908577b26726079026776e0495838aa9592c026))
- Remove redundant urls ([8d6afbd](https://github.com/eduNEXT/eox-nelp/commit/8d6afbda77b4633ee12ca9c232e2f8085191d748))
- to install tox we dont need tox ([96f2339](https://github.com/eduNEXT/eox-nelp/commit/96f2339bb99785bb613c7f70292f84d0e6ea1805))

#### Code Refactoring

- change unnecessary file for course api ([d7cf3fe](https://github.com/eduNEXT/eox-nelp/commit/d7cf3feb300cb2cde2176f57c65fc000b81efa86))
- configure run python-test ([e8d9d55](https://github.com/eduNEXT/eox-nelp/commit/e8d9d5545856f9644281cf8b70298bff1972132f)), closes [/github.com/eduNEXT/eox-theming/blob/master/eox_theming/settings/test.py#L45](https://github.com/eduNEXT//github.com/eduNEXT/eox-theming/blob/master/eox_theming/settings/test.py/issues/L45) [/github.com/eduNEXT/eox-support/blob/master/eox_support/views.py#L16](https://github.com/eduNEXT//github.com/eduNEXT/eox-support/blob/master/eox_support/views.py/issues/L16)
- improve quality for course api ([5a6edba](https://github.com/eduNEXT/eox-nelp/commit/5a6edba993fcce36e5605846dde43263cf66e490))
- mfe-config-api nelp ([4c51c2b](https://github.com/eduNEXT/eox-nelp/commit/4c51c2b053268c419a5b8e04c0a0f1943d8c80b8))
- style quality and complexity ([58cd8c8](https://github.com/eduNEXT/eox-nelp/commit/58cd8c8453b50f72f1f681c8214bcc7789eceb7d))

## This project adheres to Semantic Versioning (http://semver.org/).
.. There should always be an "Unreleased" section for changes pending release.
Unreleased

## [1.0.0] - 2022-10-18

Added

```
* Maple compatibility.
Removed

```
- Koa compatibility

## [0.2.1] - 2022-09-19

Added

```
* Add image url functionality to courses endpoint.


[0.2.0] - 2022-08-23
---------------------

Added

```
- User search button to add user in course creator model admin.

## [0.1.0] - 2022-08-22

Added

```
* Admin `course_creator` model to studio.


Changed

```
- **BREAKING CHANGE**: Remove unnecessary files from `eox-core` ancestors
- **BREAKING CHANGE**: Changed plugin settings to the requirement of nelp.
- **BREAKING CHANGE**: Copy from edx-platform and Keep only course_api to customize the courses endpoint.

[0.0.0] - 2022-03-30

```
Added
~~~~~
* Hello world for the plugin. Starting in Koa.

```