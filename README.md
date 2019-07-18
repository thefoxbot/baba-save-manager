# Baba Save Manager
Easy save manager for Baba Is You.

This app requires Python 3 with the `PyQt5` package.

**IMPORTANT!** Always back up your saves first before editing it!
The author will not be liable for any loss of data.

## Building
Additionally, to build the app, the `PyInstaller` package is needed as well.

In the directory, run
```
pyinstaller babasaveman.spec 
```

The executable will be located in the `dist/` folder.

The SPEC file was generated with the following command:
```
pyinstaller --add-data "icon.png;icon.png" -i "icon.ico" --noconsole --onefile babasaveman.py
```

The executable provided in releases is built with UPX.

## Understanding the save data
The following table describes data found under the "Properties" section:

Section  | Description
---------|-------------
`<main>` | Stores clear data for all levels within the world, as well as other miscellaneous data, such as level/path unlock status and playtime.
bonus    | Stores the number of bonuses obtained, and from which levels. Signified by orbs.
clears   | Stores the number of areas cleared, and which areas. Signified by blossoms.
complete | Stores which areas are completed. Signified by petals around the level.
converts | Stores info on which maps have transformed levels.
prize    | Stores the number of level clears per area. Signified by dandelion puffs.

Each entry in `converts` has a corresponding entry under the "Level converts" section,
which notes down the level it contains and what it is transformed to.

## Changelog
- v1.0
  - Initial release.
