# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-08-16

### Breaking changes

* Require Python 3.10 or newer ([#74](https://github.com/inertiajs/inertia-django/pull/74), [#86](https://github.com/inertiajs/inertia-django/pull/86)).
* Require Django 5.2 LTS or newer ([#103](https://github.com/inertiajs/inertia-django/pull/103)).
* Move `requests` behind the optional `ssr` extra. Applications using server-side rendering must install `inertia-django[ssr]` ([#73](https://github.com/inertiajs/inertia-django/pull/73)).
* Update the first-load page format and CSRF configuration for Inertia v3. Applications with custom templates or client setup should follow the [Inertia v3 upgrade guide](docs/guide/upgrading-to-v3.md) ([#100](https://github.com/inertiajs/inertia-django/pull/100), [#101](https://github.com/inertiajs/inertia-django/pull/101)).

### Added

* Add full Inertia v3 protocol support, including nested partial reloads, once props, deep merge and scroll props, prepend intent, fragment-preserving redirects, preserved errors, and improved merge metadata ([#100](https://github.com/inertiajs/inertia-django/pull/100), [#101](https://github.com/inertiajs/inertia-django/pull/101)).
* Expose Django messages as top-level Inertia flash data ([#96](https://github.com/inertiajs/inertia-django/pull/96), [#101](https://github.com/inertiajs/inertia-django/pull/101)).
* Add type annotations and ship a PEP 561 `py.typed` marker for downstream type checkers ([#85](https://github.com/inertiajs/inertia-django/pull/85), [#95](https://github.com/inertiajs/inertia-django/pull/95)).
* Log server-side rendering failures while preserving the client-side rendering fallback ([#89](https://github.com/inertiajs/inertia-django/pull/89)).

### Changed

* Make `InertiaRequest` inherit from Django's `HttpRequest` for better compatibility with Django and third-party libraries ([#84](https://github.com/inertiajs/inertia-django/pull/84)).
* Improve the `@inertia` decorator's response handling and stack-trace naming ([#77](https://github.com/inertiajs/inertia-django/pull/77)).

Thanks to @akx, @SarthakJariwala, @mrgalopes, @kennyputman, @willianantunes,
@leeuwr, @benaduo, @Zesuperaker, and @basan17 for their contributions to this release.

## [1.2.0] - 2025-03-25
* Add InertiaMeta class config for easier serialization
* Bugfix for InertiaJsonEncoder customizatin. Thanks @akx!
* Better Errors for missing settings. Thanks @akx!
* Allow serialization of non-model query set results. Thanks @akx
* Special thanks to @svengt for adding ruff formatting!

## [1.1.0] - 2025-01-08
* Refactored rendering logic to create InertiaResponse class
* Bugfix for SSR template data
* Bugfix for relative url. Thanks @Rey092!

## [1.0.0] - 2025-01-05
* Inertia V2 Support
* * Encrypt History. Thanks @svengt!
* * Deferred Props. Thanks @mrfolksy!
* * Optional props and deprecate lazy
* * Merge Props
* Location function. Thanks @keinstn!

## [0.6.0] - 2024-01-26
* Allow Django >=4 Thanks @pmdevita!

## [0.5.3] - 2023-09-20

* Encode SSR page data via the included InertiaJsonEncoder. Thanks @svengt!
* Bugfix for Inertia test helpers. Thanks @nootr!
* Bugfix for 303 redirect HTTP verbs. Thanks @Xzya! 

## [0.5.2] - 2022-12-22

* Make sure CSRF cookies are also set on initial load, not just inertia responses. Thanks @pauldiepold!

## [0.5.1] - 2022-12-21

* Revert switch to using Vary: X-Inertia headers due to bug report.

## [0.5.0] - 2022-12-20

* Automatically Include CSRF Token.
* Switch to using Vary: X-Inertia headers. Thanks @swarakaka!
* Bugfix for Inertia head tag rendering. Thanks @svengt!

## [0.4.1] - 2022-10-10

* Bugfix to allow redirects to be returned from @inertia decorated views.

## [0.4.0] - ???

* Initial release.
