import sqlite3, shutil
from os.path import exists
from os import utime, mkdir
from time import time
from datetime import datetime, timedelta

MEDIA_PARTITION = "/home/user/iphone" # where the device's media partition is mounted
MUTATIONS = MEDIA_PARTITION + "/PhotoData/Mutations" # don't change this
DB_PATH = "/home/user/Photos.sqlite" # your copy of Photos.sqlite
DST_ROOT = "/home/user/Pictures/iphone" # where media is exported to

# Short version:
# If your dates look wrong, set this value to 0 and try running the script again.
TIMESTAMP_FIXING_CONST = 3600*(6 + 24*(31*365.25))

# Long version:
# When using this with iOS 16.0, I found that the photo timestamps in the database were all offset by a certain amount, so this constant is my attempt to fix that.
# This quirk might not exist in other versions. If my patch causes problems then post an Issue with your iOS version.
# If you have any idea why Apple did this, please let me know.

def find_src_file(asset):
    if int(asset[4]):
        # Attempts to find media that was edited in the Photos app.
        # These rules might not always work.
        # If you know a better method, or an attribute in Photos.sqlite that points directly to the edited files, let me know.

        type = asset[1].split(".")[-1].lower()
        if type == "png":
            type = "jpg"
        src = f"{MUTATIONS}/{asset[0]}/{asset[1][:8]}/Adjustments/FullSizeRender.{type}"
        if not exists(src):
            if type == "mp4": type = "mov"
            elif type == "mov": type = "mp4"
            src = f"{MUTATIONS}/{asset[0]}/{asset[1][:8]}/Adjustments/FullSizeRender.{type}"
        if not exists(src):
            print(f"\n{asset[0]}/{asset[1]}: Edited image couldn't be found. Copying original instead.")
            src = f"{MEDIA_PARTITION}/{asset[0]}/{asset[1]}"
    else:
        src = f"{MEDIA_PARTITION}/{asset[0]}/{asset[1]}"
    return src

def correct_date_modified(dst, added_date):
    try:
        utime(dst, (added_date, added_date))
        return 0
    except FileNotFoundError:
        print(dst + " was not properly copied.")
        return 1

if __name__ == "__main__":
    log = ""

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""SELECT ZASSET.ZDIRECTORY,
                ZASSET.ZFILENAME,
                ZADDITIONALASSETATTRIBUTES.ZIMPORTEDBYDISPLAYNAME,
                ZADDITIONALASSETATTRIBUTES.ZORIGINALFILENAME,
                ZASSET.ZHASADJUSTMENTS,
                ZASSET.ZADDEDDATE,
                ZASSET.Z_PK
                FROM ZASSET, ZADDITIONALASSETATTRIBUTES
                WHERE ZASSET.ZADDITIONALATTRIBUTES = ZADDITIONALASSETATTRIBUTES.Z_PK
                AND ZASSET.ZTRASHEDSTATE = 0;""") # ignores assets in Recently Deleted
    assets = cur.fetchall()

    cur.execute("""SELECT ZASSET.Z_PK,
                ZGENERICALBUM.ZTITLE
                FROM ZASSET, ZGENERICALBUM, Z_28ASSETS
                WHERE Z_28ASSETS.Z_3ASSETS = ZASSET.Z_PK
                AND Z_28ASSETS.Z_28ALBUMS = ZGENERICALBUM.Z_PK
                AND ZASSET.ZTRASHEDSTATE = 0;""")
    album_relations_list = cur.fetchall()
    con.close()
    
    album_relations = {}
    for relation in album_relations_list:
        # if the album doesn't have a name
        if not relation[1]:
            continue
        if relation[0] in album_relations:
            print(f"album conflict! asset {relation[0]} is in '{album_relations[relation[0]]}' and '{relation[1]}'")
        else:
            album_relations[relation[0]] = relation[1]

    n = 0
    print(len(assets))

    for asset in assets:
        src = find_src_file(asset)
        
        album = album_relations.get(asset[6], None)
        if album:
            dst_dir = f"{DST_ROOT}/{album}"
        else:
            dst_dir = DST_ROOT
        
        if not exists(dst_dir):
            mkdir(dst_dir)

        software = asset[2]
        filename = asset[3]

        if software:
            dst = f"{dst_dir}/{software}_{filename}"
        else:
            dst = f"{dst_dir}/{filename}"
        
        print(f"\r{n}", end="", flush=True)
        log += "{n} '{src}' -> '{dst}'\n"
        if exists(dst):
            print(f"\n'{dst}':destination file already exists")
            n += 1
            continue
        shutil.copy(src, dst)

        added_date = int(asset[5] + TIMESTAMP_FIXING_CONST)

        correct_date_modified(dst, added_date)
        n += 1

    current_time_formatted = datetime.fromtimestamp(time()).strftime("%Y-%m-%d_%H-%M-%S")
    with open(f"iphone_dcim_{current_time_formatted}.log", "w", encoding="utf8") as file:
        file.write(log)
