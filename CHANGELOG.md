# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.7.0] - 2026-02-10

### Added

- DMA connecs endpoints
- Waterbalance endpoint
- Tests
- Database logging + endpoint to see them

### Changed

- DMA endpoints prefix

### Removed

- Hydraulic engine endpoints

## [0.6.0] - 2026-01-29

### Added

- Toggle valve status endpoint
- Get mincut valves endpoint
- Get mincut dialog endpoint
- Get features from polygon endpoint
- Profile endpoint
- Flow endpoint
- Get arc audit values endpoint

### Changed

- Valve unaccess endpoint
- Message level allowed values
- Linter (ruff)
- Configuration to .env file

## [0.5.0] - 2025-12-11

### Added

- This CHANGELOG file.
- Keycloak authorization support.
- `X-Device` and `X-Lang` headers.
- Functionality on mincut endpoints (start, end, cancel, delete)
- New endpoint: getlist.
- Exception handler class & function.

### Changed

- CI files and workflows.
- Hydrometer models.
- Mincut endpoints to be RESTful.
- Mincut models to be Pydantic objects.
- Mincut parameters & return models following gw_fct_setmincut refactor.
- Group common dependencies.

### Removed

- Deprecated code.
- Unused imports.

## [0.4.0] - 2025-11-05

### Added

- Option to fetch all feature types in getfeaturechanges.
- CRM endpoints and models (6 new endpoints).

### Changed

- Models for getfeaturechanges.
- Type of connecId to int.

## [0.3.4] - 2025-07-10

### Added

- DMA models.
- Fetch DMAs from database.
- Hydrometer models.

### Fixed

- Send parameters properly in getsearch endpoint.

## [0.3.3] - 2025-07-09

### Added

- Support for circular routes.

### Changed

- Start following [SemVer](https://semver.org) properly.
- Geometry field type in GetSelectorsData model.

### Fixed

- getsearch endpoint.
- Procedure call to gw_fct_getfeatures.

## [0.3.2] - 2025-06-27

### Added

- Call to gw_fct_getsearch.

### Changed

- GetFeatureChanges models to include node and connec features.

## [0.3.1] - 2025-06-26

### Added

- Maneuvers support for routing endpoints.

### Changed

- GetFeatureChanges response.

## [0.3.0] - 2025-06-19

### Added

- Routing endpoints.
- Search endpoint.

### Changed

- Group routers by Giswater toolbars.

## [0.2.0] - 2025-06-16

### Added

- Basic endpoint code structure for Features, Hydraulic engine, Mincut
  & Water balance.
- Docker configuration file.
- Plugin support.
- Basic test with pytest.
- Basic CI workflow.

[unreleased]: https://github.com/giswater/giswater-api/compare/v0.7.0...main
[0.7.0]: https://github.com/giswater/giswater-api/compare/v0.6.0...0.7.0
[0.6.0]: https://github.com/giswater/giswater-api/compare/v0.5.0...0.6.0
[0.5.0]: https://github.com/giswater/giswater-api/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/giswater/giswater-api/compare/v0.3.4...v0.4.0
[0.3.4]: https://github.com/giswater/giswater-api/compare/v0.3.3...v0.3.4
[0.3.3]: https://github.com/giswater/giswater-api/compare/mv0.3.2...v0.3.3
[0.3.2]: https://github.com/giswater/giswater-api/compare/mv0.3.1...mv0.3.2
[0.3.1]: https://github.com/giswater/giswater-api/compare/mv0.3.0...mv0.3.1
[0.3.0]: https://github.com/giswater/giswater-api/compare/mv0.2.0...mv0.3.0
[0.2.0]: https://github.com/giswater/giswater-api/releases/tag/mv0.2.0
