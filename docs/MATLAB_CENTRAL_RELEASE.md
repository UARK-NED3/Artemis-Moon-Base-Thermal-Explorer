# MATLAB Central release path

## Status

Prepared for a future submission; **not published to MATLAB Central yet**. The repository must first be release-ready so the public listing points to a stable, reviewed artifact rather than a moving development branch.

## Proposed listing

- **Title:** Artemis Moon Base Thermal Explorer
- **Repository:** `UARK-NED3/Artemis-Moon-Base-Thermal-Explorer`
- **MATLAB entry point:** `src/matlab/LunarThermalExplorer.m`
- **Purpose:** Educational exploration of a declared, synthetic lunar-night single-node heat-balance model.
- **Required limitation statement:** This is screening-level teaching software; it is not validated flight, hardware-selection, mission-operations, or safety-certification software.

## Release gates

1. Select an open-source license with the repository maintainer.
2. Run the Python test suite and MATLAB smoke checks on the release commit.
3. Add an end-user MATLAB example and screenshots to the release notes.
4. Create a versioned GitHub Release, beginning with `v0.1.0`.
5. Submit or link the MATLAB code on MATLAB Central File Exchange from the stable release, following MathWorks' GitHub integration guidance.

MathWorks recommends GitHub Releases when linking a repository, because the File Exchange listing can then reference a stable version instead of the default branch. See [About File Exchange](https://www.mathworks.com/matlabcentral/content/fx/about.html) and the [GitHub integration guide](https://www.mathworks.com/matlabcentral/fileexchange/my-file-exchange/github-app-installation-guide).

## Publishing boundary

Do not bundle locally downloaded NASA/PDS PDFs or raw datasets in the File Exchange submission. Keep source records and retrieval instructions in the repository, and check each source's redistribution terms before adding any data adapter or packaged sample.
