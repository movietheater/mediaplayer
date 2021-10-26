# MediaPlayer

A simple non UI fullscreen media player based on VLCs Python bindings.

### Features:
- [x] Hotkey support for controlling the player, see documented hotkeys here: [controlling player](#controlling-player)
- [x] Remembers where it left off, only supports the latest media played
- [x] Automatically adjusts audio to english by default if bundled with the media
- [x] Automatically adjusts subtitle to english by default if bundled with the media

---

### Play media:
There is two methods to play media, either via html or directory passing argument to the executable. Control the player using **hotkeys** and enjoy the content without any UI.

#### From a webpage:
_Disclamer: This only works when the URI protocol has been installed_
```html
<a href="ovlc:////network-share-01/c/Movie.Example.2019.2160p.hdr10plus.bluray.x265.hevc.mkv">Play Movie Example 2019</a>
```
#### From command line:
```cmd
ovlc.exe "ovlc:////network-share-01/c/Movie.Example.2019.2160p.hdr10plus.bluray.x265.hevc.mkv"
```

#### Controlling player:
These are the supported hotkeys the player listen for while playing media or loading up.
| Hotkey         | Description   |
|----------------|---------------|
| ESC | Stops the media and exits |
| LEFT | Backward 1 minute | 
| RIGHT | Forward 1 minute | 
| SPACE | Pause the media | 
| MEDIA STOP | Stops the media and exits | 
| MEDIA NEXT TRACK | Forward 5 minutes | 
| MEDIA PREV TRACK | Backward 5 minutes | 
| MEDIA PLAY PAUSE | Pause the media | 

### Installation:
* Install VLC Media Player from their website (https://www.videolan.org/vlc)
* Build the executable using the `build.py` file
* Copy the `ovlc.exe` executable from **dist** folder to your VLC installation directory
* Install the URI protocol by running `ovlc_protocol_64bit.reg` or `ovlc_protocol_32bit.reg` depending on VLCs architecture
* Done!