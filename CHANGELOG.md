# Changelog

All notable changes to EOSCF-ContentBasedRS will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

*For each release, use the following sub-sections:*

- *Added (for new features)*
- *Changed (for changes in existing functionality)*
- *Deprecated (for soon-to-be removed features)*
- *Removed (for now removed features)*
- *Fixed (for any bug fixes)*
- *Security (in case of vulnerabilities)*

## [2.0.0] - RELEASED

### What’s Changed

- Re-filling ground truth when creating the files for manual evaluation… (#182) @AnnaMitsopoulou
- Initial project assistant implementation (#178) @AnnaMitsopoulou
- Mark annotation conflicts (#179) @MikeXydas
- move get object inside reranking (#174) @kathdevx
- Autocompletion api testing (#171) @MikeXydas
- Test RS API with mongo (similar services, project completion, health, update) (#169) @MikeXydas
- Make id type agnostic (#167) @AnnaMitsopoulou
- Fixed recommendations format and auto update status and ar reports (#155) @kathdevx
- Better health messages (#152) @MikeXydas
- Manual evaluation file (#147) @MikeXydas
- Reranking recommendations (#146) @kathdevx
- filter services by status (#145) @kathdevx
- Manual versioning (#143) @MikeXydas
- Tf idf baseline (#141) @MikeXydas
- Select services for evaluation (#136) @AnnaMitsopoulou
- Calculating pairwise distance of different RS variations. (#132) @MikeXydas
- Created docker files (#121) @MikeXydas
- Remove service id conversion to str (#119) @AnnaMitsopoulou
- Auto completion evaluation fixes (#114) @AnnaMitsopoulou
- Calculate statistics of manual evaluation (#113) @AnnaMitsopoulou
- Added maximum_suggestions as evaluation parameter (#111) @MikeXydas
- Api versioning (#109) @MikeXydas
- Create separate update for each mode (#105) @AnnaMitsopoulou
- Use catalogue api (#104) @AnnaMitsopoulou
- Monitoring services (#93) @kathdevx
- Refactoring rs (#91) @AnnaMitsopoulou
- Standarized RS responses (#90) @MikeXydas
- Most popular baseline (#72) @AnnaMitsopoulou
- Calculate metrics: precision, recall, f1-score (#71) @AnnaMitsopoulou
- Add examples to recommendation routes (#70) @AnnaMitsopoulou
- Fix bug with maximum suggestions (#58) @MikeXydas
- Added mode parameter in config (#54) @MikeXydas
- Add optimal parameters for auto-complete suggestions in config (#34) @MikeXydas
- Set user to guest when not found (#32) @MikeXydas
- Auto completion (#31) @MikeXydas
- Created more detailed diagnostic messages (#30) @MikeXydas
- Created health check functionality for recommender (#25) @MikeXydas
- Guest users in similar services (#24) @MikeXydas
- Added URI building for mongo (#22) @MikeXydas
- Add filtering in project_completion (#21) @AnnaMitsopoulou
- Update for one service (#20) @AnnaMitsopoulou
- Only use mongo in user profile, not postgres (#19) @MikeXydas
- Added redis in deployment compose (#18) @MikeXydas
- Storing rs structures (#17) @AnnaMitsopoulou
- Change db used in project_completion, enable user history usage (#16) @AnnaMitsopoulou
- Integrating redis for storage instead of file system (#15) @MikeXydas
- Scheduling updates every N hours and monitoring with cronitor (#14) @MikeXydas
- Initialization of RS objects is performed on startup event (#13) @MikeXydas
- Add versioning (#12) @AnnaMitsopoulou
- Redesigned how exceptions are caught (#11) @MikeXydas
- Separated db connection and db operations (#10) @MikeXydas
- Cleaning up the root of the project (#7) @MikeXydas
