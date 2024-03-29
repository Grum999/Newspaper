# Newspaper

A [Krita](https://krita.org/en) plugin to apply halftone effect on image.
![Example](https://github.com/Grum999/Newspaper/raw/master/newspaper/newspaper/newspaper.jpg)

## What is Newspaper?
*Newspaper* is a Python plugin made for [Krita](https://krita.org) (free professional and open-source painting program).

It allows to apply halftone effect on image, like a newspaper printing effect.
Plugin provides differents tuning options to define final result:
- Color modes: Monochrome / CMYK
- Rendering chapes: Circle, Diamond, Square, Line
- Antialiasing method
- ...


## Download, Install & Execute

### Download
+ **[ZIP ARCHIVE - v1.2.1](https://github.com/Grum999/Newspaper/releases/download/V1.2.1/newspaper.zip)**
+ **[SOURCE](https://github.com/Grum999/Newspaper)**


### Installation

Open [Krita](https://krita.org) and go to **Tools** -> **Scripts** -> **Import Python Plugins...** and select the **newspaper.zip** archive and let the software handle it.

To enable *Newspaper* go to **Settings** -> **Configure Krita...** -> **Python Plugin Manager** and click the checkbox to the left of the field that says **Newspaper**.

### Execute
When you want to execute *Newspaper*, simply go to **Tools** -> **Scripts** and select **Newspaper**.


### What's new?
_[2023-05-09] Version 1.2.1_
- Fix bug *Krita 5.2.0 Compatibility*

_[2021-11-30] Version 1.2.0_
- Improvement: add possibility to open/save newspapers settings
- Fix bug: now a layer located in a group layer is processed, don't need anymore to work on layer from document root
- Fix bug: compatibility with Krita 5.1.x

_[2020-06-23] Version 1.1.1_
- Compatibility with Krita 4.3.0

_[2020-05-01] Version 1.1.0_
- Add **Three color (CMY - Pictures)** mode
*No black layer, Black key is obtained by the combination of Cyan, Magenta, Yellow*
- Add a **Four color (CMY+K - Pictures)** mode
*Use of [registration black](https://en.wikipedia.org/wiki/Rich_black): black key is obtained by the combination of Cyan, Magenta, Yellow, and an additional black layer is added*
- Improve the **Four color (CMY+K - Comics #2)**


### Bugs
Plugin has been tested with Krita 5.2.0 (appimage)


### What’s next?
- Some improvements can be made to user interface
- Maybe adding a preset management allowing user to save preferred configuration(s) rather than having to redefine everything each time :grimacing:
- Speedup processing using multi-thread


## License

### Newspaper is released under the GNU General Public License (version 3 or any later version).

*Newspaper* is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.

*Newspaper* is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should receive a copy of the GNU General Public License along with KanvasBuddy. If not, see <https://www.gnu.org/licenses/>.


Long story short: you're free to download, modify as well as redistribute *leNewLayerColorName* as long as this ability is preserved and you give contributors proper credit. This is the same license under which Krita is released, ensuring compatibility between the two.
