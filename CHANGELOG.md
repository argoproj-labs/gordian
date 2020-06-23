# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com),
and this project adheres to [Semantic Versioning](https://semver.org).

## [1.5.0] - 2020-06-23
### Added
- Added the ability to set labels to sent pull requests using a flag.


## [1.4.1] - 2020-06-18
### Fixed
- set_target_branch was not cleaning the file cache, resulting in gordian not being able to get new files in the new branches.

## [1.4.0] - 2020-06-17
### Added
- Print out PR URLs at the end of a Gordian run
### Fixed
- Fixed bug when not bumping version

## [1.3.0] - 2020-06-13
### Added
- This changelog
- Support to call a function if the PR is created
- Target branch support, now you can create PR against any branch, not only master
### Changed
- Refactored `apply_transformations` function to simplify passing the list of repositories from a different source

