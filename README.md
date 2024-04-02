# Map for Vampires Dawn III - The Crimson Realm

This repository contains an interactive map for the game Vampires Dawn III - The Crimson Realm.

The map has been built using the awesome [Leaflet](https://leafletjs.com) library.

**Open map at https://vampiresdawnmaps.github.io/vampires-dawn-3**

## Map Features
* Interactive and navigatable map for each area of the game, starting on the game's world map
* Map markers for transitions to other areas (use the link in the marker's popup)
* Map markers for item locations, traps, hidden passage entry spots
* Search for markers on the current map
* Search for maps by name

## Status of this project
The map is considered work in process.

## License
The Python script that wad used for generating the map resources and the main HTML may be used under the terms of the MIT license. This applies to these files:
* `collect-map-data.py`
* `index.html`

I do not have any rights on the map images hosted in this repository and will therefore remove them if requested by the game's owner.

## Generating the map resources
You may use the python script to generate the map resources yourself by following the steps below.

### Overview
1. Install Python 3.
1. Install the game (I used the German version).
1. Copy the complete `Vampires Dawn 3` directory into this repository's root directory (next to the `collect-map-data.py` script file). We'll call this the `<GAME_COPY>` directory below.
1. Create directory `docs/images` in the repository root.
1. Run `collect-map-data.py` to generate `map-data.js`.
1. In the game copy replace the nwjs runtime with the SDK and enable developer tools.
1. In the game copy inject the mapshot script and adapt it.
1. Run the modified game, load a savegame and start the map screenshot process by pressing the hotkey.

### Enabling developer tools in game
The default nw.js runtime doesn't contain a working developer tools console, therefore you need to download the nw.js SDK from https://nwjs.io/downloads/ and overwrite all files in the copied game directory with the ones from the downloaded SDK ZIP.

To automatically open the developer tools window on game start add this at the top of `<GAME_COPY>/www/js/main.js`:
```javascript
nw.Window.get().showDevTools();
```

Launch the game with `nw.exe`, the developer tools should open automatically (leave the game's fullscreen mode if necessary).

### Creating screenshots of all game maps
Unfortunately there don't seem to be any standalone tools that can directly extract map PNGs from the game data.
Therefore we'll use a modified version of the OrangeMapshot RPGmaker plugin. This is a bit of a quick & dirty hack but gets the job done with some retrying.

Download https://github.com/Hudell/mv-plugins/blob/master/OrangeMapshot.js into `<GAME_COPY>/www/js/plugins`

Enable the mapshot plugin by adding this to `<GAME_COPY>/www/js/plugins.js`:
```json
  {
    "name": "OrangeMapshot",
    "status": true,
    "description": "This plugin will save a picture of the entire map on a Mapshots folder when you press a key. <OrangeMapshot>",
    "parameters": {
      "useMapName": "false"
    }
  }
```

Edit `<GAME_COPY>/www/js/plugins/OrangeMapshot.js` and replace the `$.onKeyUp` key event handler at the bottom of the script with:
```javascript
    $.missing = [151];

    $.loop = function(mapId) {
        $gamePlayer.reserveTransfer(mapId, 1, 1, 0, 2);    
        setTimeout(() => {
            if (SceneManager._scene instanceof Scene_Map) {
                $.saveMapshot();
            }
            if (mapId < 460) {
                $.loop(mapId + 1);
            }
        }, 1000);
    }

    $.loopMissing = function(mapId) {
        $gamePlayer.reserveTransfer($.missing.shift(), 1, 1, 0, 2);
        setTimeout(() => {
            if (SceneManager._scene instanceof Scene_Map) {
                $.saveMapshot();
            }
            if ($.missing.length > 0) {
                $.loopMissing();
            }
        }, 1000);
    }

    $.onKeyUp = function(event) {
        if (event.keyCode == $.Param.keyCode) {
            $.loop(1);
            // $.loopMissing();
        }
    };
```
Open the game and press Print Screen key, wait until all screenshots have been created.
Some maps play a cutscene when entering it, which interfere with the screenshot process. Finish the cutscene and check if the screenshot loop continues. If it does not, save the game, replace the startup index in the initial loop call with the broken map ID and restart the whole procedure. Eventually you should get most images of the 460 maps. To create the remaining ones you can add their IDs to the `$.missing` array and change the key press event listener so it calls `$.loopMissing();` instead.

Once all map images have been generated you probaby want to use a tool such as [oxipng](https://github.com/shssoichiro/oxipng) to decrease their file sizes (it will have a very noticable effect on the file size).