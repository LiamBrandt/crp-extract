# CRP Extract
This is a simple tool to extract .crp files for [Cities: Skylines](https://store.steampowered.com/app/255710).
As of right now it can extract PNG and DDS files, leaving the other binary files unsorted.

## Requirements:
 * Python 2 or 3 https://www.python.org/downloads/

## Usage:
```
crp_extract.py [-h] [--output-dir OUTPUT_DIR] file

positional arguments:
  file                  The file to unpack

optional arguments:
  -h, --help            show this help message and exit
  --output-dir OUTPUT_DIR
                        The directory to put the unpacked files into (Default:
                        current working directory)
```

A CRP is split up into sections, which when extracted are represented as files in the extract folder.
Each section contains metadata at the beggining.
When the format of the section can be determined, this metadata is moved to a file called metadata.json, and the correct file extension is added to the end of that section file.
For example, if a CRP contained a section with a PNG image, then the metadata for that section would be cut and moved to metadata.json, and the smaller section file would be given a .png extension so that it functions as a PNG file.

## Key for first bytes:
These are the values for the first bytes of each type of file contained in a CRP file. They are probably used as a quick guide for the game to tell which files are which.
 * 0x53 - Assembly-CSharp
 * 0x54 - UnityEngine.Mesh
 * 0x57 - BuildingInfoGen
 * 0x58 - UnityEngine.Material
 * 0x59 - UnityEngine.Texture2D
 * 0x5A - UnityEngine.GameObject
 * 0x5B - CustomAssetMetaData
 * 0x69 - ColossalFramework.Importers.Image
