# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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