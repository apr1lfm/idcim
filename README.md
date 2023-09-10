# iDCIM
Python command-line tool for exporting media and some metadata from the iOS Photos library.

**A better alternative is [osxphotos](https://github.com/RhetTbull/osxphotos) (MacOS/Linux).** This is just a personal project more than anything.

## Requirements
- **Linux**
- Python 3
- An iOS device*
- [ifuse](https://github.com/libimobiledevice/ifuse#ifuse): Mounts the media partition from an iOS device connected via USB (make sure your computer is trusted in iOS). *If you know any similar tools for Windows, please let me know.*

\**iOS 11+ is needed. I have tested this with iOS 16.0 and iPadOS 9.3.5, the latter didn't work because its photo database didn't have a ZASSET table. I can confirm iOS 11+ does have ZASSET because of [this](https://github.com/ScottKjr3347/iOS_Local_PL_Photos.sqlite_Queries/blob/main/iOS11/iOS11_LPL_Phsql_Adjust-Mutat.txt).*

## Setup & Usage
1. Mount the iOS media partition with `ifuse`, for example:
   ```bash
   mkdir -p /home/user/iphone && ifuse /home/user/iphone
   ```
2. Copy `/PhotoData/Photos.sqlite` from the iOS media partition to somewhere on your computer, for example:
   ```bash
   cp /home/user/iphone/PhotoData/Photos.sqlite /home/user/Photos.sqlite
   ```
   
   This step isn't required but is recommended as unexpected behaviour may occur if iOS tries to modify the file while the script is using it.
3. Download `idcim.py` or clone the repository.
4. Set up the correct paths in the constants at the top of `idcim.py`. `DST_ROOT` is where media will be exported to.
5. Run the script (in any directory). *Depending on how many photos and albums you have, this may put a lot of files in the same folder. I might change this behaviour in future.*
6. Briefly check that the date modified on your files matches your Photos library. If not, read the comment near the top of the script.
7. ⚠️If you choose to delete your photos from your device afterwards, be aware that this script does **NOT** export location metadata or faces or most other metadata. If you want to preserve this you should use an alternative like [osxphotos](https://github.com/RhetTbull/osxphotos) or at least keep the Photos.sqlite file.
