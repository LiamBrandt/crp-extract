# CRP Extract
This is a simple tool to extract .crp files for Cities: Skylines. As of right now it can extract PNG and DDS files, leaving the other binary files unsorted.

##Requirements:
 * Python 2.7 https://www.python.org/downloads/

##Usage:
 * You will be prompted to input type in the file name in the console when you launch the program. Don't forget the .crp extension.

##Key for first bytes:
 * 0x53 - Assembly-CSharp
 * 0x54 - UnityEngine.Mesh
 * 0x57 - BuildingInfoGen
 * 0x58 - UnityEngine.Material
 * 0x59 - UnityEngine.Texture2D
 * 0x5A - UnityEngine.GameObject
 * 0x5B - CustomAssetMetaData
 * 0x69 - ColossalFramework.Importers.Image
