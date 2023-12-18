# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com),
and this project adheres to [Semantic Versioning](https://semver.org).

## [3.7.1] - 2023-12-15
### Fix
- Removed dockerhub publish

## [3.7.0] - 2023-10-18
### Added
- Added support to pass in a path when calling get_files(), resolves issue #34

## [3.6.0] - 2023-10-06
### Fix
- Fetch repo content from target branch
- Publishing to dockerhub and ghcr together in workflows
### Added
- New maintainer added! Welcome @kaosx5s

## [3.5.0] - 2023-05-16
### Added
- Added support to pass in a github token, username and password as named parameters

## [3.4.0] - 2023-02-24
### Added
- Added method to return the github client

## [3.3.0] - 2022-05-12
### Added
- Added support for serialization options when dumping a file

## [3.2.0] - 2021-03-26
### Added
- Added plain text file support

## [3.1.1] - 2020-12-11
### Fix
- Remove '.git' from repo_name

## [3.1.0] - 2020-08-26
### Added
- Allow `repo#create_pr` to be called without setting labels

## [3.0.1] - 2020-07-29
### Fixed
- Fixed error handling logic when forking to retry when Github returns 404 (because that implies the repo hasn't yet finished forking)

## [3.0.0] - 2020-07-17
### Changed
- Made forking optional via `--fork` argument, which is mutually exclusive with `--branch`

## [2.1.2] - 2020-06-25
### Added
 - Added entrypoint script to meet requirements of official docker image consistency

## [2.1.1] - 2020-06-23
### Fixed
- Fixed setting the labels twice when releasing 2.1.0

## [2.1.0] - 2020-06-23
### Added
- New optional flag to pass a description to the PR created by gordian.

## [2.0.0] - 2020-06-23
### Added
- Gordian now forks the repo instead of creating a branch in the specified repo so that users can run Gordian against repos that they do not have write permissions on.

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

