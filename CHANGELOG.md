# Changelog

## [0.7.1](https://github.com/EPFL-ENAC/AddLidar/compare/v0.7.0...v0.7.1) (2025-06-20)


### Bug Fixes

* **scanner:** add pipefail option to ensure pipeline failures are caught ([e4f15cf](https://github.com/EPFL-ENAC/AddLidar/commit/e4f15cf231a363f393f448f907899187d8e327f8))

## [0.7.0](https://github.com/EPFL-ENAC/AddLidar/compare/v0.6.0...v0.7.0) (2025-06-20)


### Features

* **database:** add new production snapshot for lidar API ([1aa6586](https://github.com/EPFL-ENAC/AddLidar/commit/1aa65864caff76b435dfa6516894fb0859698705))
* **frontend:** enhance error handling with detailed logs and copy functionality ([a2ec35a](https://github.com/EPFL-ENAC/AddLidar/commit/a2ec35a2479b9e1d4f41c10bac7c27294ce6c93f))
* **makefile:** add database deployment and management commands for Kubernetes environments ([7249f3e](https://github.com/EPFL-ENAC/AddLidar/commit/7249f3e47656cc52738b90419af2a8818d8d5bdf))


### Bug Fixes

* **scanner:** update subPath for Potree volume mount to correct directory ([683ab49](https://github.com/EPFL-ENAC/AddLidar/commit/683ab49dbcd40a0e88656fe8dc2634ea79b5b8a1))

## [0.6.0](https://github.com/EPFL-ENAC/AddLidar/compare/v0.5.1...v0.6.0) (2025-06-16)


### Features

* **api:** add detailed_error_message field to folder and potree metacloud state models ([905e3c5](https://github.com/EPFL-ENAC/AddLidar/commit/905e3c5884f9eb1b1e2837ec3795eb92b13b486f))
* **backend:** add database snapshot management system ([7cfbcf4](https://github.com/EPFL-ENAC/AddLidar/commit/7cfbcf423743f42c2af7d2b6aa38fa9e515e8906))
* **compression:** remove sqlite & add curl ([8f15562](https://github.com/EPFL-ENAC/AddLidar/commit/8f155628285bd36a8dac126a7444a350358f21e1))
* **frontend:** add MissionCard and MissionFootprintMap components for mission visualization ([6dd4038](https://github.com/EPFL-ENAC/AddLidar/commit/6dd4038531ac4cf0c292e591365050ea3f14049f))
* **frontend:** implement zoom to mission functionality in MissionFootprintMap ([15b39da](https://github.com/EPFL-ENAC/AddLidar/commit/15b39da7c464515e482986f5ffb7aff60456f465))
* **potree-converter:** add curl & remove sqlite in docker image ([f2243f4](https://github.com/EPFL-ENAC/AddLidar/commit/f2243f49c195c16eef9bbcb3e22f09ee6aeaf5f4))
* **scanner:** add detailed logging to API for compression and potree convert ([ec75fa5](https://github.com/EPFL-ENAC/AddLidar/commit/ec75fa5bf6121c2bc667d46ab6b36da4b3fcfcf4))
* **scanner:** add function to update last_checked timestamp for folder state ([ab64a4a](https://github.com/EPFL-ENAC/AddLidar/commit/ab64a4acee86928579ddffb620e2b368892c4da1))


### Bug Fixes

* **scanner:** remove folder state condition for potree converter ([ab64a4a](https://github.com/EPFL-ENAC/AddLidar/commit/ab64a4acee86928579ddffb620e2b368892c4da1))
* **sql:** remove trailing comma in detailed_error_message column definition ([da788a9](https://github.com/EPFL-ENAC/AddLidar/commit/da788a98fcd3b82c6e6e6cd95ce1e64e83a7d3a9))

## [0.5.1](https://github.com/EPFL-ENAC/AddLidar/compare/v0.5.0...v0.5.1) (2025-06-15)


### Bug Fixes

* **scanner:** remove persist_state.sql copy instruction ([d409646](https://github.com/EPFL-ENAC/AddLidar/commit/d4096469f4a5c91f1c8b765369ecb51078231c80))

## [0.5.0](https://github.com/EPFL-ENAC/AddLidar/compare/v0.4.0...v0.5.0) (2025-06-15)


### Features

* **api:** add create and update endpoints for folder and potree metacloud states ([b043867](https://github.com/EPFL-ENAC/AddLidar/commit/b0438672a3416ad76b4430e6db2a6997515d7fc5))
* **api:** integrate backend URL for database updates in job templates and scanner ([198f2f1](https://github.com/EPFL-ENAC/AddLidar/commit/198f2f11603ae26e9c36b8258657e7f53fec8157))
* **api:** refactor folder and potree metacloud state creation to use API exclusively ([97073ba](https://github.com/EPFL-ENAC/AddLidar/commit/97073ba9fc3c9b7a8ddffac31ddac1d81ce0e66b))
* **api:** refactor scanner to use API for folder and potree metacloud state management ([1ccedd5](https://github.com/EPFL-ENAC/AddLidar/commit/1ccedd59e7c2b28e5331471fefbe47dceb357605))

## [0.4.0](https://github.com/EPFL-ENAC/AddLidar/compare/v0.3.0...v0.4.0) (2025-06-15)


### Features

* **api:** add health check endpoint for public app ([f403762](https://github.com/EPFL-ENAC/AddLidar/commit/f403762983ffe27e3bd8cf73b5a5f5c132ef962b))
* **api:** refactor main.py to utilize environment variables for server ports and clean up imports ([1e44e20](https://github.com/EPFL-ENAC/AddLidar/commit/1e44e2072b7d096e50d6081fb9e5691f8cd7c9ae))
* **backend:** create two apps - public & internal to protect sensitives routes ([f628383](https://github.com/EPFL-ENAC/AddLidar/commit/f628383c2b949ee7a085d62ba0cc25cd081521f3))
* **backend:** refactor SQLite api file by splitting functionality into separate modules ([1358662](https://github.com/EPFL-ENAC/AddLidar/commit/13586625b6f1e84ffa6365ecf38bba68e2f641a5))
* **docker:** update Dockerfile and Makefile to expose public and internal ports 8000 and 8001 ([06ea382](https://github.com/EPFL-ENAC/AddLidar/commit/06ea3824a306ecaf4582e4f70ba92e1b2367e4b2))
* **sqlite:** add update endpoints for folder and potree metacloud states - internal protected ([99d00d8](https://github.com/EPFL-ENAC/AddLidar/commit/99d00d80e14de122a7ad367f6add399d8ec1a5a8))

## [0.3.0](https://github.com/EPFL-ENAC/AddLidar/compare/v0.2.0...v0.3.0) (2025-06-12)


### Features

* remove time stamp from job name ([d796982](https://github.com/EPFL-ENAC/AddLidar/commit/d796982fafdcb144710983bfcef67dae0a14b4e8))
* remove time stamp from job name ([db6ebbd](https://github.com/EPFL-ENAC/AddLidar/commit/db6ebbd07f220efd8bb078c4d2b358c37d969abb))


### Bug Fixes

* **scanner:** update job names in compression and potree converter templates for consistency ([acf030f](https://github.com/EPFL-ENAC/AddLidar/commit/acf030f6afc5f786b78d282e4d76260a892728e8))
* **scanner:** update job names in compression and potree converter templates for consistency ([f29b465](https://github.com/EPFL-ENAC/AddLidar/commit/f29b4651458df215b8c6857459cc1049afdd9c38))

## [0.2.0](https://github.com/EPFL-ENAC/AddLidar/compare/v0.1.0...v0.2.0) (2025-06-12)


### Features

* add new database snapshot for lidar API ([b935c84](https://github.com/EPFL-ENAC/AddLidar/commit/b935c8465f09682a3f090e65f2ab130bd4c84c3c))


### Bug Fixes

* **scanner:** parameterize image settings in job templates for compression and potree-converter ([e173fd9](https://github.com/EPFL-ENAC/AddLidar/commit/e173fd9c1d41ffcedad863705293f7883a2939d1))

## 0.1.0 (2025-06-12)


### ⚠ BREAKING CHANGES

* clean repo & remove add_lidar prefix for html files

### Features

* add annotations for ArgoCD instance based on environment in job metadata ([5c0b926](https://github.com/EPFL-ENAC/AddLidar/commit/5c0b9263f285a957e991b10bafd0a1cfa140eb52))
* add API prefix handling for production environment in index.html ([ecec51e](https://github.com/EPFL-ENAC/AddLidar/commit/ecec51e84e70f7b9ec7163d85c9464026f746e79))
* add clip box connection between potree & vue js ([e92ccc4](https://github.com/EPFL-ENAC/AddLidar/commit/e92ccc42e275971b31e33fdc95ed12c8c3723286))
* add clip volume component mimicking potree clip volume ([5af502f](https://github.com/EPFL-ENAC/AddLidar/commit/5af502f7f7e9307e91933c3e3501b6e1572487f6))
* add CORS middleware, job status endpoints, and HTML interface for job management ([7d43aac](https://github.com/EPFL-ENAC/AddLidar/commit/7d43aac55c9506f7ee49ad9edcafd11477fa9e47))
* Add debug logging for input directory contents in entrypoint script ([3103930](https://github.com/EPFL-ENAC/AddLidar/commit/3103930a1ab787690904376cc9071abc163cc8c6))
* add debug logging to Dockerfile command and increase job timeout to 120 seconds ([35e6b68](https://github.com/EPFL-ENAC/AddLidar/commit/35e6b6828c7bdef46d449265ba8629216585f323))
* add download data form ([6b4755f](https://github.com/EPFL-ENAC/AddLidar/commit/6b4755f69878d42a430374fd0ec4255392ae35a5))
* add endpoint to retrieve current settings and update FastAPI initialization ([352560c](https://github.com/EPFL-ENAC/AddLidar/commit/352560cb700d18d689eac8c67e528130dd9ffd32))
* add endpoint to retrieve folder state by subpath and update database path in settings ([4e33418](https://github.com/EPFL-ENAC/AddLidar/commit/4e33418a79505da9a6c280a603e5ed96d61f5b87))
* add environment-based annotations for addlidarmanager job ([ab2aa5f](https://github.com/EPFL-ENAC/AddLidar/commit/ab2aa5f410bea745b18724a17c2f304f6c316f47))
* add environment-based annotations for ArgoCD in k8s_addlidarmanager job ([647af56](https://github.com/EPFL-ENAC/AddLidar/commit/647af56cb8d87ca6ab2a7840edbc06d722bb4953))
* add environment-specific labels for addlidarmanager job ([f4fe1d8](https://github.com/EPFL-ENAC/AddLidar/commit/f4fe1d8d5f2cfc13c719827342d046ffecf7ed5c))
* add ErrorMessage component for displaying error messages in PointCloudViewer ([e7d6172](https://github.com/EPFL-ENAC/AddLidar/commit/e7d6172540d4611976cfd64d569e98f7a582d947))
* add example environment configuration and update README instructions ([1d3e9c6](https://github.com/EPFL-ENAC/AddLidar/commit/1d3e9c65c87b7f81e42ca9cc7731ac75cbf3b484))
* add filter range source id ([649e2ba](https://github.com/EPFL-ENAC/AddLidar/commit/649e2baa246df16354f0af799c5499079945a2d6))
* add first view position close to lidar points ([9c2c48b](https://github.com/EPFL-ENAC/AddLidar/commit/9c2c48b9e7a9ef3861f4f6102197f699517beb18))
* add flake8 and black for code quality checks; update quality-checks workflow ([e6bf1a6](https://github.com/EPFL-ENAC/AddLidar/commit/e6bf1a6de8770abaa56d533ba96b91ae49a61336))
* add folder state and potree metacloud state endpoints with new schema ([811decf](https://github.com/EPFL-ENAC/AddLidar/commit/811decfb395d8dc597d73f884978d2f0c04bc7f2))
* add gap to download card layout for improved spacing ([246a714](https://github.com/EPFL-ENAC/AddLidar/commit/246a7149d3ab3b0418027118cf5b46d320c4ae72))
* add Git hooks setup using lefthook for automated formatting and linting ([5d3898b](https://github.com/EPFL-ENAC/AddLidar/commit/5d3898bb13e718ae0eb0d7afa2e8ae74cc587fab))
* add health check functionality and update job status handling ([3b413d3](https://github.com/EPFL-ENAC/AddLidar/commit/3b413d30d8ea5e64a5a6561b8bc40b325bc1115d))
* add input to select attribute variable name to display color ([cc30cf8](https://github.com/EPFL-ENAC/AddLidar/commit/cc30cf8f121853980240d459623e7ae433ddeaba))
* add job api with websocket connection [#4](https://github.com/EPFL-ENAC/AddLidar/issues/4) ([e3ff357](https://github.com/EPFL-ENAC/AddLidar/commit/e3ff35753cfb080806c80ecee93cc2b7322da723))
* add job cleanup route and replace index.html with updated version for AddLidar API ([193387b](https://github.com/EPFL-ENAC/AddLidar/commit/193387bcc209583a8411ea6e95686bc161602761))
* add job log retrieval and enhance job status with creation time and total duration ([7bbe5cd](https://github.com/EPFL-ENAC/AddLidar/commit/7bbe5cde04d866e552ea4f69edd2e896d84fdad7))
* add job persistence and cleanup logic for unretrieved files ([d6391c5](https://github.com/EPFL-ENAC/AddLidar/commit/d6391c50c66606db9901631c1aa812998143218a))
* add lidar monitor first draft script ([eeb8333](https://github.com/EPFL-ENAC/AddLidar/commit/eeb8333bec93af2ddb56a5bf631d55c9f06746a5))
* add mission list view ([7279426](https://github.com/EPFL-ENAC/AddLidar/commit/7279426ae3a583409eac93742c56c25843c8ad04))
* add new variables for radio button color variable ([95ec160](https://github.com/EPFL-ENAC/AddLidar/commit/95ec160b599965ab245b631716bf56ca6f3321a8))
* add OUTPUT_PATH and PVC_OUTPUT_NAME to settings for enhanced Kubernetes volume management ([7ddce52](https://github.com/EPFL-ENAC/AddLidar/commit/7ddce528accae9098fdb5460483c98f660eac0af))
* add PATH_PREFIX configuration to environment settings ([efc9a1d](https://github.com/EPFL-ENAC/AddLidar/commit/efc9a1dadc37c8343ab07f73fa21ae173b31949b))
* add PersistentVolume and PersistentVolumeClaim for local Lidar data storage; update settings to use PVC for ROOT_VOLUME ([873a885](https://github.com/EPFL-ENAC/AddLidar/commit/873a885305413fa3bf700e0818d6726f1e4fced4))
* add Potree conversion job template and scanning functionality for metacloud files ([f1d0dfe](https://github.com/EPFL-ENAC/AddLidar/commit/f1d0dfea93e247201e017c7f005289dc1d2fde23))
* add PVC configuration options for FTS AddLidar and database in scanner.py ([e266b9e](https://github.com/EPFL-ENAC/AddLidar/commit/e266b9ebd756fbdc71ecd1bdd60b7e25201ab77f))
* add pydantic-settings dependency; refactor settings class to use BaseSettings for improved configuration management ([2ccff32](https://github.com/EPFL-ENAC/AddLidar/commit/2ccff32bc147b81f90f84db26b7a79f4fe2f3939))
* add resource requests and limits for Kubernetes jobs in k8s_addlidarmanager ([6013ba0](https://github.com/EPFL-ENAC/AddLidar/commit/6013ba080cf224829ba2ec5797deecb099bb0954))
* add snapshot from prod ([4427a36](https://github.com/EPFL-ENAC/AddLidar/commit/4427a362ae4bbeb74c5e22c52466b14b5bb83cb8))
* add Source ID filtering functionality ([cd6496b](https://github.com/EPFL-ENAC/AddLidar/commit/cd6496b1807c7ae1d58f6a49cf61e89d174a067a))
* add SQLite API routes and configure database settings ([380db4b](https://github.com/EPFL-ENAC/AddLidar/commit/380db4b0b1944b089256ce6efab4558173664200))
* Add SQLite installation to Dockerfile and implement push-image target in Makefile ([7e10d25](https://github.com/EPFL-ENAC/AddLidar/commit/7e10d25b1141be7c0d726cd54375ec833a784598))
* add stop-job endpoint to delete Kubernetes jobs and manage job status ([f704951](https://github.com/EPFL-ENAC/AddLidar/commit/f704951317c4966a96b9ee116c5d8a52f1773f52))
* add stop-job functionality to terminate Kubernetes jobs and update job status handling ([15327f9](https://github.com/EPFL-ENAC/AddLidar/commit/15327f9333e5757de66f6e058555b757eba46a0d))
* add SUB_PATH to settings and use it in volume mount configuration ([0833caa](https://github.com/EPFL-ENAC/AddLidar/commit/0833caa829d0ca87071847f5e4b258b966f1b026))
* add unique filename output and update job creation logic in routes ([52698d0](https://github.com/EPFL-ENAC/AddLidar/commit/52698d02651df446c65fbf583deb33be522c76c5))
* added clip volume parameters inside downloading data form ([09d7abe](https://github.com/EPFL-ENAC/AddLidar/commit/09d7abee7e28170ec8fbf5eb811bc2ae3839111c))
* added quasar ([0a3307f](https://github.com/EPFL-ENAC/AddLidar/commit/0a3307f902e6f4960bc1573b2619755bd7745113))
* added vue app and integrate potree inside ([7f2349f](https://github.com/EPFL-ENAC/AddLidar/commit/7f2349f6765200958bda922cd4600057f95d56b6))
* adjust CPU request and limit values in k8s_addlidarmanager job ([a83b3cf](https://github.com/EPFL-ENAC/AddLidar/commit/a83b3cf572a88b51a35e2cbfc4cdbbc18caf38fc))
* adjust FOV and point budget settings in PointCloudViewer ([08ddd00](https://github.com/EPFL-ENAC/AddLidar/commit/08ddd0086a07b047d8c0b17da45714cf711a1997))
* **archive:** add script for creating compressed archive of a single folder ([6d873cf](https://github.com/EPFL-ENAC/AddLidar/commit/6d873cfad64cde727c7d0a26b362d036025a38d6))
* **archive:** enhance compression by adding blocksize option to pigz command ([7abee03](https://github.com/EPFL-ENAC/AddLidar/commit/7abee035003e4750356370ca3c56c6ff1cf7e248))
* **archive:** optimize script for creating compressed archives with improved logging and error handling ([f5c56df](https://github.com/EPFL-ENAC/AddLidar/commit/f5c56df007b9f0f46764def5b887bdca9b21e27c))
* **archive:** remove compression level from pigz command for improved compression ([f809b33](https://github.com/EPFL-ENAC/AddLidar/commit/f809b33f3044d490e3959668dae54f38606e3efb))
* **batch:** add Kubernetes job configuration and refactor scan_and_enqueue for batch processing BREAKING CHANGE ([d9acf43](https://github.com/EPFL-ENAC/AddLidar/commit/d9acf433d2e8d87bc41d5e17d2a4a40f1704f545))
* **benchmark:** add benchmark results for optimal pigz config ([689d986](https://github.com/EPFL-ENAC/AddLidar/commit/689d9861dc5c5d14c032fcd4e3b929b763df8838))
* clean repo & remove add_lidar prefix for html files ([a54011b](https://github.com/EPFL-ENAC/AddLidar/commit/a54011bd404094aaf4265765ad0c0bbc56d95955))
* cleanup code by removing celery and docker ([c8d2e78](https://github.com/EPFL-ENAC/AddLidar/commit/c8d2e7876173a588a81aea378872098fa9292366))
* comment out job deletion logic in k8s_addlidarmanager and routes ([13f008c](https://github.com/EPFL-ENAC/AddLidar/commit/13f008c7fa984eedaae7cd70e1a67ec43c732e1a))
* **database:** add database rebuild script and state management for archives ([6f6e320](https://github.com/EPFL-ENAC/AddLidar/commit/6f6e320461373cc86961a37b06ca05c2232db0cc))
* **database:** enhance schema initialization and add logging for database operations ([25357f0](https://github.com/EPFL-ENAC/AddLidar/commit/25357f0caa65ca7c8b71793ee1cd363e5dbb2144))
* **database:** implement folder state checker and update logic in archive process ([3a224b5](https://github.com/EPFL-ENAC/AddLidar/commit/3a224b5506a4d25506f72a7b4d1f415d47a2aeb6))
* **docker:** remove ENTRYPOINT for archive_one_folder.sh in Dockerfile ([9409a3c](https://github.com/EPFL-ENAC/AddLidar/commit/9409a3c56615619818b9454019412d32ca5195d9))
* **docker:** update Dockerfile to use archive_one_folder.sh and add Dockerfile-all for comprehensive builds ([edf5277](https://github.com/EPFL-ENAC/AddLidar/commit/edf527719f1f0cbe35b42a92aa18708766442146))
* document handling of job creation failure due to quota limits in TODO.md ([8c4a6b2](https://github.com/EPFL-ENAC/AddLidar/commit/8c4a6b2de800175d1aff43124f10ebf7e6de5177))
* enhance deployment workflow and add Git subtree migration documentation ([bbf3888](https://github.com/EPFL-ENAC/AddLidar/commit/bbf38889f2305df7f7765170c4cabd18decb6af0))
* enhance directory store with pointcloud metadata fetching and update related components ([de2947a](https://github.com/EPFL-ENAC/AddLidar/commit/de2947a9ea1576f7e38d299ca7b78f7d180bb475))
* enhance download functionality with new processing panel and improved UI ([8209f44](https://github.com/EPFL-ENAC/AddLidar/commit/8209f44d8fca7d78a911aa41526669da1fd2cc7e))
* enhance DownloadDataForm with additional input fields and loading state for download process ([f0b0466](https://github.com/EPFL-ENAC/AddLidar/commit/f0b0466a73014d84180b3c7f78b04ab47459dc13))
* enhance file download logic with error handling and content type mapping ([5bca7e9](https://github.com/EPFL-ENAC/AddLidar/commit/5bca7e98e59e489113cb7e9d504d4b9f9c1e5bbb))
* enhance file handling and cleanup logic in point cloud processing ([9c8d677](https://github.com/EPFL-ENAC/AddLidar/commit/9c8d677a5b1f119b8b4fe447c8643e4e5e33c534))
* enhance job start logic with error handling and CLI argument conversion ([a192141](https://github.com/EPFL-ENAC/AddLidar/commit/a192141351efdc849eead8d45827b5ef68e814d0))
* enhance job status tracking with in-memory storage and event loop integration ([eb1fdef](https://github.com/EPFL-ENAC/AddLidar/commit/eb1fdef0cf4b199682c0799e69b89a9e48396193))
* enhance job status tracking with timestamp and output path serialization ([fc898a6](https://github.com/EPFL-ENAC/AddLidar/commit/fc898a699369873883cbdb7e3eb558a0021b19fc))
* enhance job status update and notification handling with type safety and improved error management ([9bd59f3](https://github.com/EPFL-ENAC/AddLidar/commit/9bd59f35f5a8a9391d810b4f3acabaf12587737f))
* enhance logging and update output path configuration for Kubernetes integration ([6474faa](https://github.com/EPFL-ENAC/AddLidar/commit/6474faa75452aed77b2c777e5341f96d78b9c9ce))
* enhance logging in collect_changed_folders to include fingerprint, size, and file count ([6b7b164](https://github.com/EPFL-ENAC/AddLidar/commit/6b7b16436d51711cec58fc0520f46053c2dcc1a3))
* enhance PointCloudRequest model with validation and detailed descriptions; update API routes for improved error handling ([14fcd7c](https://github.com/EPFL-ENAC/AddLidar/commit/14fcd7cb4c88e197fd3bc35f7825aaf424e5fdc1))
* enhance process_point_cloud to return output file path; improve error handling and logging ([8ab4022](https://github.com/EPFL-ENAC/AddLidar/commit/8ab40227de790830a7cb14a710151fc26d7820e8))
* enhance process_point_cloud to support multiple file formats and improve output file handling ([8b6f0c8](https://github.com/EPFL-ENAC/AddLidar/commit/8b6f0c891ebfda033985276b680df7d5f47bee72))
* enhance README with collapsible Plant UML definition ([d83141f](https://github.com/EPFL-ENAC/AddLidar/commit/d83141f9929f01bac69e8c29f78f1b2df1a69ed8))
* enhance UI layout and improve job cleanup logic in lidar-api ([cc0a28e](https://github.com/EPFL-ENAC/AddLidar/commit/cc0a28efc33be182bc12f2053992ba421ec89704))
* harmonize sql table for future potree state management ([b26812b](https://github.com/EPFL-ENAC/AddLidar/commit/b26812b08eaf042980bc7183e7616423313e6bf7))
* implement automated PotreeConverter download in Dockerfile and remove legacy scripts ([81e1480](https://github.com/EPFL-ENAC/AddLidar/commit/81e148016e95e1653cec33826f13894751bc0fc7))
* implement directory store and routing for mission data ([6042aaa](https://github.com/EPFL-ENAC/AddLidar/commit/6042aaad4ab68cc21022404aeec7b5e373cdf0ee))
* implement file download endpoint and enhance output file handling ([4180ab8](https://github.com/EPFL-ENAC/AddLidar/commit/4180ab81619cc9dc30d928c713c2b6da0d603fab))
* implement job log retrieval and enhance job status with additional metadata ([153e3f3](https://github.com/EPFL-ENAC/AddLidar/commit/153e3f327ca70a4524bcdc1fc7c575418c465196))
* improve Git subtree migration Makefile rules ([e2e3002](https://github.com/EPFL-ENAC/AddLidar/commit/e2e300271848c1ba04eb978eab4767100b762726))
* improve readme ([c750057](https://github.com/EPFL-ENAC/AddLidar/commit/c75005739e295bc53e6be0bada233e7f5e36ef7a))
* improve settings and validation for ROOT_VOLUME; enhance file path handling in PointCloudRequest and process_point_cloud ([d239dc3](https://github.com/EPFL-ENAC/AddLidar/commit/d239dc36f6c4327eb518a19e9f2759ac540b5e04))
* **index.html:** make outcrs optional ([90c32d4](https://github.com/EPFL-ENAC/AddLidar/commit/90c32d4412b5436e5caebf04a8ddcfd36b60e660))
* integrate Docker service for point cloud processing; refactor API route to use new service ([b36801a](https://github.com/EPFL-ENAC/AddLidar/commit/b36801ae60c0b691bf59c1ef02460de9be38a8d2))
* **lidar-zip:** add Dockerfile and README for LiDAR ZIP tool; enhance archive script with progress monitoring ([dbd192d](https://github.com/EPFL-ENAC/AddLidar/commit/dbd192d510bcc9799cf31570d5c9c14e071c3a46))
* **lidar-zip:** enhance archive script with thread monitoring and update Dockerfile dependencies ([8b91b7b](https://github.com/EPFL-ENAC/AddLidar/commit/8b91b7b52b4570b6a4c81b9afa1addd0a039f646))
* **lidar:** add Docker build script, Kubernetes job configuration, and update scan_and_enqueue script for job queuing ([0cadcf9](https://github.com/EPFL-ENAC/AddLidar/commit/0cadcf962e571869aa220e108f4f9fa50b0435e0))
* **lidar:** remove archive watcher script ([ea1a031](https://github.com/EPFL-ENAC/AddLidar/commit/ea1a031ba4b25f0a7157a2843b7b1ebeef25038c))
* **lidar:** update job template and scan_and_enqueue script to handle folder fingerprints and improve logging ([034b3ef](https://github.com/EPFL-ENAC/AddLidar/commit/034b3ef68858178568087a901ba6f2b53ef5ca94))
* make color variables selector in expansion item ([c68ccd3](https://github.com/EPFL-ENAC/AddLidar/commit/c68ccd325c5c59b432bf31e818f116617f98b08c))
* migrate lidar API to new structure with updated dependencies and configurations ([2256514](https://github.com/EPFL-ENAC/AddLidar/commit/22565141e000018abe1e3f95ab88ef8eceb1a321))
* migrate point cloud processing from Docker to Kubernetes; add Kubernetes service integration and update dependencies ([bfe7c9b](https://github.com/EPFL-ENAC/AddLidar/commit/bfe7c9baedb8fd51b69027e2ddeb38b352a6f5d4))
* refactor file path validation in PointCloudRequest to enforce absolute paths and remove reliance on ROOT_VOLUME ([85b672c](https://github.com/EPFL-ENAC/AddLidar/commit/85b672c27498f6ee2741a5db67b786a960d2f5fb))
* refactor job status notification handling with improved error management and utility functions ([2506b8a](https://github.com/EPFL-ENAC/AddLidar/commit/2506b8a7132ae85b34c2b1a10604e5771bcf2827))
* reimplemented color variable ([509da28](https://github.com/EPFL-ENAC/AddLidar/commit/509da287cccb800b30e1a7ade5ea762034e3acf4))
* restructure lidar API into addlidar-api package and update dependencies ([bca8845](https://github.com/EPFL-ENAC/AddLidar/commit/bca8845d71e458ce7e2a08c2e3936ae506e3b172))
* **scan_and_enqueue:** add export_only flag for job queuing and enhance command-line interface and dry-run and other options ([c5eb5ba](https://github.com/EPFL-ENAC/AddLidar/commit/c5eb5baae64d758de165605e24fb6fc6b048a716))
* **scan_and_enqueue:** add scan command to Makefile and update logging configuration in script ([0f986e4](https://github.com/EPFL-ENAC/AddLidar/commit/0f986e4521edbc82e3068f08b7382064d0f10fa6))
* **scan_and_enqueue:** refactor argument handling and execution environment configuration ([402a471](https://github.com/EPFL-ENAC/AddLidar/commit/402a471e607e2dec35e2531067e10f3f0a661526))
* set download logic for mvp - only format selection ([14d5ee9](https://github.com/EPFL-ENAC/AddLidar/commit/14d5ee9f92269dfb25acc600f1769dfdc0ba41cb))
* **static:** add tree static files component with download files button ([08e0220](https://github.com/EPFL-ENAC/AddLidar/commit/08e0220ae2d1bb50915c6ba3ec276c1ec3b7dd63))
* update active attribute assignment in loadPointCloud function ([4850778](https://github.com/EPFL-ENAC/AddLidar/commit/4850778b410788d9e0b533f63ef18164e226a0f2))
* update API base URL logic and configure logging based on environment, remove CORS on prod ([a5ad28b](https://github.com/EPFL-ENAC/AddLidar/commit/a5ad28b0d8f3cf360adb71760af95b41fdd48fb1))
* update API calls to include prefix for job status and download links ([eabbe81](https://github.com/EPFL-ENAC/AddLidar/commit/eabbe816d5c82a43375113ba4301eb11365f482e))
* update build script names for clarity and add dense attribute to checkboxes in SourceIDFilter ([f0f72b9](https://github.com/EPFL-ENAC/AddLidar/commit/f0f72b9fb608b744043ee649bfe7dd804e3248c9))
* update default file format to .bin in job file retrieval ([e498d1a](https://github.com/EPFL-ENAC/AddLidar/commit/e498d1a237fe38e5669e6f717c411b6cdcc7c9d1))
* update Docker integration; modify file path handling and enhance error responses in process_point_cloud route ([7a0c2ef](https://github.com/EPFL-ENAC/AddLidar/commit/7a0c2ef7a98d1531f3fdcfb07b047729eae7ad67))
* update dockerfile + GitHub Actions workflow for deployment and add TODO file ([06348a2](https://github.com/EPFL-ENAC/AddLidar/commit/06348a2cfafa622e9e71fc1a5deba755d0c66af7))
* update DownloadDataForm with new input fields and improved download logic ([9268a8d](https://github.com/EPFL-ENAC/AddLidar/commit/9268a8d1aee1002da256ab7a086e01384f84caf2))
* update environment configuration; remove ROOT_VOLUME and DEFAULT_DATA_ROOT, add new settings for Kubernetes and output paths ([3216d24](https://github.com/EPFL-ENAC/AddLidar/commit/3216d245baf82294b6495190d9eaca88ab41c15f))
* update file path handling in PointCloudRequest model; enhance error reporting in process_point_cloud route ([7ded1ae](https://github.com/EPFL-ENAC/AddLidar/commit/7ded1ae40eddd60e288ee38ab727143c82253101))
* update guidelines for testing and file path validation; add pytest configuration and tests for PointCloudRequest model ([1142686](https://github.com/EPFL-ENAC/AddLidar/commit/1142686c331de1a702f6b4b9098c30490091f04a))
* update job annotations and labels for environment-specific configurations in k8s_addlidarmanager ([8717af0](https://github.com/EPFL-ENAC/AddLidar/commit/8717af051ff41fd0c291ac168c22b20012aee4c3))
* update job CLI argument handling and logging for improved clarity ([96430e7](https://github.com/EPFL-ENAC/AddLidar/commit/96430e74cd01a627792cd43134ed67f3f6a53bb2))
* update job configuration to allow retries and control pod deletion behavior ([1aa7dc0](https://github.com/EPFL-ENAC/AddLidar/commit/1aa7dc02069cde223c657ece032e0c4a4055c090))
* update LidarDirectoryTree to nested tree ([26adc07](https://github.com/EPFL-ENAC/AddLidar/commit/26adc07947de1b6ecc614610b763afa4571831af))
* update log level in Dockerfile from debug to info for improved performance ([b08736c](https://github.com/EPFL-ENAC/AddLidar/commit/b08736c2a4b0bba21c58ddd03a44d38769d82180))
* update Makefile logging level, enhance README with local development instructions, and modify local-pv.yaml access modes ([9879c42](https://github.com/EPFL-ENAC/AddLidar/commit/9879c424b4c2be801db6e9194be842dbadcd45a5))
* update Makefile to install and run lidar-api; add health check endpoint ([6db4ca8](https://github.com/EPFL-ENAC/AddLidar/commit/6db4ca84e51c1655dd29087c7ad8791d9328c345))
* update memory requests and limits in k8s_addlidarmanager job and replace annotations with labels ([efd96af](https://github.com/EPFL-ENAC/AddLidar/commit/efd96affe2f774342c08ccb4915a6d4ecf945b9d))
* update NAMESPACE in settings for Kubernetes deployment ([889f13e](https://github.com/EPFL-ENAC/AddLidar/commit/889f13eee0a297febfa360ef763e00001b7d5804))
* update output path configuration to use DEFAULT_ROOT instead of ROOT_VOLUME, working with k8s ([2f30488](https://github.com/EPFL-ENAC/AddLidar/commit/2f304882f25318886f85d243fb901351248cf42d))
* update PointCloudRequest model to allow negative values for returns and number fields; add get_log_job_status function to retrieve job logs ([f2d2c50](https://github.com/EPFL-ENAC/AddLidar/commit/f2d2c50e9efde248d87d89c518b5776757ec298d))
* update readme to the project ([8930dc2](https://github.com/EPFL-ENAC/AddLidar/commit/8930dc2d2479e4cee69e512333c3930b0b67cb68))
* update resource requests and limits for addlidarmanager job ([f18c358](https://github.com/EPFL-ENAC/AddLidar/commit/f18c35854fe4668745527f02796c45a98bb93229))
* update resource requests and limits for k8s_addlidarmanager job ([cc964ab](https://github.com/EPFL-ENAC/AddLidar/commit/cc964ab698931e8c919ca31c222d15d979d589aa))
* update ROI parameter to use an array format in DownloadDataForm and JobParams ([d58ddb6](https://github.com/EPFL-ENAC/AddLidar/commit/d58ddb669af498bb8dfd00330509e04f8a42e2e8))
* update settings for Kubernetes integration; remove default settings and streamline configuration for PVC usage ([1904e7f](https://github.com/EPFL-ENAC/AddLidar/commit/1904e7fd965e0e5aa7beb2494306b804897964c4))
* update settings to dynamically set ROOT_VOLUME for local development; enhance file path validation in PointCloudRequest ([98db054](https://github.com/EPFL-ENAC/AddLidar/commit/98db054a9c867d07ed2105ccb143d5f4a8c5028b))
* update TODO list and enhance valid formats in PointCloudRequest model ([2bb6b9f](https://github.com/EPFL-ENAC/AddLidar/commit/2bb6b9ff529835ffb86f1f074e9e8fefb5193aac))
* update TODO list with completed tasks and add new items for API documentation and form input improvements ([b397418](https://github.com/EPFL-ENAC/AddLidar/commit/b3974184359e07a52e1e5086d36e211ca7c99bd4))
* update TODO with additional options for job cleanup and management ([147c6e5](https://github.com/EPFL-ENAC/AddLidar/commit/147c6e5bd704716e19217a3dae2fe53b3ec7940e))
* update TODO with enhancements for job/pod monitoring and management ([8960aa0](https://github.com/EPFL-ENAC/AddLidar/commit/8960aa02dc2d4b5a858731169c880a1c5e7a7bc2))
* update TODO.md with job creation failure details and remove unused code in routes and k8s_addlidarmanager ([f6b23b2](https://github.com/EPFL-ENAC/AddLidar/commit/f6b23b224f7a54578b7ee198d9c4327e2a903200))
* update with new state from sqlite db ([47c95a6](https://github.com/EPFL-ENAC/AddLidar/commit/47c95a69f52afe9f49bd523335bc6b65b38c0a00))
* **zip:** first commit for lidar zip ([6959de1](https://github.com/EPFL-ENAC/AddLidar/commit/6959de1953274f9df6cde5c89a3f6d231f218a47))


### Bug Fixes

* add CHANGELOG.md to Prettier ignore list ([728be41](https://github.com/EPFL-ENAC/AddLidar/commit/728be41385c090a7ce9c9ad8da785c484d1591a6))
* add logging for invalid folder paths and improve error messaging ([6ea5b8b](https://github.com/EPFL-ENAC/AddLidar/commit/6ea5b8b1f7c0229fb0b950ecb17e13a86f58749e))
* add sqlite3 to Dockerfile and update job template for folder processing ([df2a9ac](https://github.com/EPFL-ENAC/AddLidar/commit/df2a9acf364a1d9777fabc3fd544071d5b12dcc6))
* **addlidar:** add page.html as / ([f97d1e0](https://github.com/EPFL-ENAC/AddLidar/commit/f97d1e06f4c4e5a3a49ace29f01038e61745cedf))
* adjust formatting for completions and parallelism in job template ([f2b6130](https://github.com/EPFL-ENAC/AddLidar/commit/f2b6130b7a2ab73c86dd3c4cd100ced09996caff))
* adjust formatting of activeDeadlineSeconds in job template for consistency ([c629051](https://github.com/EPFL-ENAC/AddLidar/commit/c629051c2fecd602fe5b7ea2868beb5c27b14001))
* bind max prop to range-filter in DownloadDataForm for proper functionality ([ccdc256](https://github.com/EPFL-ENAC/AddLidar/commit/ccdc25615d6c6868ce13f3715f850c49cfedd136))
* comment yet not implemented file format in api ([cc384a4](https://github.com/EPFL-ENAC/AddLidar/commit/cc384a468e69b6be9c22a69186d5363e82cc23ef))
* correct formatting of volume mount configuration in generate_k8s_addlidarmanager_job function ([e23ed55](https://github.com/EPFL-ENAC/AddLidar/commit/e23ed555a8c26656a5eae3e57d5c46a2e275687b))
* Correct input and output directory variable checks and update debug logging ([854a54e](https://github.com/EPFL-ENAC/AddLidar/commit/854a54e3e4c61d76e779d1dab062b3b5ccb33a43))
* Correct parsing logic for POINTS_FILES section in entrypoint script ([db35054](https://github.com/EPFL-ENAC/AddLidar/commit/db35054db8b1dcad470d6e66519cb34abeb931aa))
* correct PVC claimName syntax in job templates for lidar zip and potree converter ([535207d](https://github.com/EPFL-ENAC/AddLidar/commit/535207d2496f683de35edb11b45cd2e08222c18c))
* correct subPath to sub_path in volume mount configuration in generate_k8s_addlidarmanager_job function ([014f456](https://github.com/EPFL-ENAC/AddLidar/commit/014f4564a21bc2fa59a8e17474d669b45c8174fb))
* correct syntax for completions and parallelism in job template ([9b272c3](https://github.com/EPFL-ENAC/AddLidar/commit/9b272c3a6f57e9214039d686827c4a80d120460e))
* Correct typo in OUTPUT_DIR variable check in entrypoint script ([4797466](https://github.com/EPFL-ENAC/AddLidar/commit/479746616eb7a6d0c617eb75faddca886ff048b9))
* Correctly close the conditional block for processing point cloud files in entrypoint script ([eb323a2](https://github.com/EPFL-ENAC/AddLidar/commit/eb323a20d9619dc963f12559c7ca301cff198454))
* enhance folder processing logic to detect new, changed, and incomplete folders ([07d7ca7](https://github.com/EPFL-ENAC/AddLidar/commit/07d7ca7288324d9b82dffbcb7af10211f5466932))
* escape asterisks in README.md to improve Markdown rendering ([40a61d9](https://github.com/EPFL-ENAC/AddLidar/commit/40a61d992f845160653a3d6e3dc5792bfb741a23))
* handle specific error code in run_lidar_cli function to improve response consistency ([3141fbb](https://github.com/EPFL-ENAC/AddLidar/commit/3141fbb10e1d056d7dc38062b4153ba4f15e8ead))
* improve code formatting and consistency in SQLite API ([2f0af7a](https://github.com/EPFL-ENAC/AddLidar/commit/2f0af7a9e33c1689d0061ebb55342a173dba18f1))
* improve error handling and processing logic for metacloud and folder states ([e7c413e](https://github.com/EPFL-ENAC/AddLidar/commit/e7c413e0a75b6217367b82f6e2d68e988caea9c6))
* improve error handling in get_settings endpoint ([b0a1604](https://github.com/EPFL-ENAC/AddLidar/commit/b0a1604dbec658099f53accab306fab32982ce5c))
* Improve file existence check and update file count logic in POINTS_FILES parsing ([cb5f688](https://github.com/EPFL-ENAC/AddLidar/commit/cb5f688e2a5a1df543698532ca58aa682ada2ff8))
* include input directory in conversion log for metacloud files ([7bb0676](https://github.com/EPFL-ENAC/AddLidar/commit/7bb0676460f937193bd1a133d7de5b803ab3394b))
* reduce resource limits for db-dir in job-batch-lidar-zip template ([3fedcc6](https://github.com/EPFL-ENAC/AddLidar/commit/3fedcc64f605211461ed2248679ae8d0fdeb0116))
* reduce resource requests for lidar-zip and potree converter jobs ([fca5f74](https://github.com/EPFL-ENAC/AddLidar/commit/fca5f745982a086d96b915cc00d9b934ab1b55fd))
* remove /LiDAR path for mounted PV ([252e231](https://github.com/EPFL-ENAC/AddLidar/commit/252e231ca1e124ea37875671675d37b3f8fcce58))
* remove /LiDAR path from updating pv ([4a7a9a1](https://github.com/EPFL-ENAC/AddLidar/commit/4a7a9a1ae3c9afd98e1f7d80dc189769b39abe4c))
* remove extraneous quotes from completions and parallelism in job template ([ada5408](https://github.com/EPFL-ENAC/AddLidar/commit/ada5408cd27d2732e7a416823b7fb65063a65a28))
* remove points clouds folder copy from dockerfile ([9bbc4fa](https://github.com/EPFL-ENAC/AddLidar/commit/9bbc4fa8add5abcad045b5abea0d60927f191571))
* remove unused model_config from Settings class ([8411339](https://github.com/EPFL-ENAC/AddLidar/commit/8411339f852327d996d242d785ed7e600e473a77))
* remove version for scripts ([00ac91f](https://github.com/EPFL-ENAC/AddLidar/commit/00ac91f5ed4113f065997e9081b0b1884de7ecad))
* rename PVC keys in job templates for clarity ([7cbf47d](https://github.com/EPFL-ENAC/AddLidar/commit/7cbf47dac23a6f2e5474d7376df4e165bc892d1c))
* run prettier on .md files ([e08c951](https://github.com/EPFL-ENAC/AddLidar/commit/e08c9516654ab3a2f1845276f172413fef251f71))
* set backoff limit and active deadline for potree converter job ([4dbaeb3](https://github.com/EPFL-ENAC/AddLidar/commit/4dbaeb32d019908c421c1d67eff4e742062d4792))
* sync npm shrinkwrap ([ba1ced0](https://github.com/EPFL-ENAC/AddLidar/commit/ba1ced0c789d8fa77014b438cc7a0975022daab2))
* update action reference in release-please workflow ([8b36b36](https://github.com/EPFL-ENAC/AddLidar/commit/8b36b36c8618e4d857b96f79bc00b9048da04bca))
* update build context in GitHub Actions workflow to point to the correct lidar API directory ([38185e4](https://github.com/EPFL-ENAC/AddLidar/commit/38185e410469d80d95e54c9341a135d64f9c3ea6))
* update button label in DownloadDataForm for clarity ([9a9399b](https://github.com/EPFL-ENAC/AddLidar/commit/9a9399bdb9d08bade107e7376245ec255818409d))
* update condition for metacloud changes detection in main function ([3d2e1eb](https://github.com/EPFL-ENAC/AddLidar/commit/3d2e1eb94f850dda1d66f2523ff2adddeed88d3c))
* update database processing status for invalid folders and metacloud files ([b375f1e](https://github.com/EPFL-ENAC/AddLidar/commit/b375f1e18141b5e18f25462f36dfc0138ab701e9))
* Update Docker image tag to latest in Makefile ([c8c8e3d](https://github.com/EPFL-ENAC/AddLidar/commit/c8c8e3df8d79816e102afdb8d3d5380a11c1dfb8))
* update EXTRA_ARGS in potree converter template to remove unnecessary page generation ([bc444c0](https://github.com/EPFL-ENAC/AddLidar/commit/bc444c06257b1ceb09bfe57fa49e0451f4b0fcb1))
* update job template references in Dockerfile and scanner.py for consistency ([f4e4ae0](https://github.com/EPFL-ENAC/AddLidar/commit/f4e4ae0595d14c34da884f0ebe58ab17a9e033a4))
* update lidar database snapshot to latest version ([797e3a2](https://github.com/EPFL-ENAC/AddLidar/commit/797e3a20fa9c2f89f676566b4f76094d53d611bf))
* update logger name to match script context in scanner.py ([568b973](https://github.com/EPFL-ENAC/AddLidar/commit/568b9737d0a12718076ac96a2d49aadfb0ca80d8))
* update Makefile to remove no-cache option and change nginx root page ([2e573ac](https://github.com/EPFL-ENAC/AddLidar/commit/2e573ac78f0ae7c0907668054de4af15aaf7ada3))
* update potree converter image to latest version ([cbca299](https://github.com/EPFL-ENAC/AddLidar/commit/cbca2998a2215edfc35bc2758baf834dcecebd39))
* update volume mount configuration to include orig_dir for fts-addlidar ([9f2c138](https://github.com/EPFL-ENAC/AddLidar/commit/9f2c138f8cd8f84fb264b746d9ef381fee048bc8))
* update volume mounts in job-batch-lidar-zip template to use fts-addlidar and remove obsolete entries ([9d6db82](https://github.com/EPFL-ENAC/AddLidar/commit/9d6db827e59266f0fa6a5ddcf5fb72f8ba177a41))
* use filename from URL parameters for download file path ([658fabd](https://github.com/EPFL-ENAC/AddLidar/commit/658fabdc5df72d95f282996d7adf4b143ada2862))


### Miscellaneous Chores

* release 0.1.0 ([4198e4f](https://github.com/EPFL-ENAC/AddLidar/commit/4198e4f1634d76b40b5f815fc9db648164bfb8f9))
