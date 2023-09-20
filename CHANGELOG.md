# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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