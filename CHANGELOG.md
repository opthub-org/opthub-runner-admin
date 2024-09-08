# Changelog

## [0.3.4](https://github.com/opthub-org/opthub-runner-admin/compare/v0.3.3...v0.3.4) (2024-09-08)


### Bug Fixes

* SyntaxError: f-string: unmatched '[' ([bf0f7eb](https://github.com/opthub-org/opthub-runner-admin/commit/bf0f7eb27ddf0d0ef3df4f4c4d8d43e3586c23db))

## [0.3.3](https://github.com/opthub-org/opthub-runner-admin/compare/v0.3.2...v0.3.3) (2024-09-08)


### Bug Fixes

* SyntaxError: f-string: unmatched '[' ([e46a2ec](https://github.com/opthub-org/opthub-runner-admin/commit/e46a2ec1d8003bd3a2bed34410b54db42bd3dfbe))

## [0.3.2](https://github.com/opthub-org/opthub-runner-admin/compare/v0.3.1...v0.3.2) (2024-09-05)


### Bug Fixes

* Unify timezone ([9f32d74](https://github.com/opthub-org/opthub-runner-admin/commit/9f32d7484c6c00596c463745b2963dd6b4650bd1))

## [0.3.1](https://github.com/opthub-org/opthub-runner-admin/compare/v0.3.0...v0.3.1) (2024-08-26)


### Bug Fixes

* Error handling when authentication fails and the Docker image ca… ([#64](https://github.com/opthub-org/opthub-runner-admin/issues/64)) ([15814ea](https://github.com/opthub-org/opthub-runner-admin/commit/15814ea47f19867c93cf39ad033917958af57804))

## [0.3.0](https://github.com/opthub-org/opthub-runner-admin/compare/v0.2.0...v0.3.0) (2024-08-17)


### Features

* accessibility validation for SQS and DynamoDB ([417d1cd](https://github.com/opthub-org/opthub-runner-admin/commit/417d1cdf14745ef61921d4f1c04f6240127d147f))
* Change to more secure credentials ([#52](https://github.com/opthub-org/opthub-runner-admin/issues/52)) ([8e203a8](https://github.com/opthub-org/opthub-runner-admin/commit/8e203a830e9b5d45c781f500d2c4dd8a0fc8a1fb))
* Check if docker is running and accessible ([#57](https://github.com/opthub-org/opthub-runner-admin/issues/57)) ([6f37581](https://github.com/opthub-org/opthub-runner-admin/commit/6f37581018f8b82b37551cbce657eec731095f14))


### Bug Fixes

* Fix exit status ([#53](https://github.com/opthub-org/opthub-runner-admin/issues/53)) ([b5514cd](https://github.com/opthub-org/opthub-runner-admin/commit/b5514cdc614623dcb4c80e6417b9104d1bcf1710))
* Use local images ([725426b](https://github.com/opthub-org/opthub-runner-admin/commit/725426b125657c5fbcf867953ead2027a6a99773))

## [0.2.0](https://github.com/opthub-org/opthub-runner-admin/compare/v0.1.1...v0.2.0) (2024-07-17)


### Features

* Change error handling method ([#48](https://github.com/opthub-org/opthub-runner-admin/issues/48)) ([b29b20d](https://github.com/opthub-org/opthub-runner-admin/commit/b29b20de6359f72c5a29b8e3e3386610b24c4a8d))

## [0.1.1](https://github.com/opthub-org/opthub-runner-admin/compare/v0.1.0...v0.1.1) (2024-06-29)


### Bug Fixes

* Change Python version (3.12.1 -&gt; >=3.10, &lt; 4.0) ([18e4a27](https://github.com/opthub-org/opthub-runner-admin/commit/18e4a27a6b3df21be965f833816fb7616629b1cf))

## 0.1.0 (2024-06-28)


### Features

Evaluator: Feature to evaluate user-submitted solutions on Opthub using Docker Image.
Scorer: Feature to calculate scores from a series of evaluations using Docker Image.
