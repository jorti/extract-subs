#!/usr/bin/env python3
"""
Copyright 2014 Juan Orti Alcaine <juan.orti@miceliux.com>


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

#mkvmerge -i file.mkv
#mkvextract tracks file.mkv 2:subs.srt

import sys
import os.path
import os
import re
import subprocess

def get_track_id(file):
    """ Returns the track ID of the SRT subtitles track"""
    try:
        raw_info = subprocess.check_output(["mkvmerge", "-i", file])
    except CalledProcessError as e:
        print(e)
        sys.exit(1)
    pattern = re.compile('.*El ID de la pista (\d+): subtitles \(SubRip/SRT\).*', re.DOTALL)
    m = pattern.match(str(raw_info))
    if m:
        return (raw_info, m.group(1))
    else:
        return (raw_info, None)
    
def extract_subs(mkvs):
    for mkv in mkvs:
        if not mkv['srt_track_id']:
            print("No subtitles for: {f}".format(f=mkv['filename']))
            continue
        srt_full_path = os.path.join(mkv['dir'], mkv['basename'] + ".srt")
        if os.path.isfile(srt_full_path):
            print("Subtitles already extracted for: {f}".format(f=mkv['filename']))
            continue
        print("----------")
        print("Processing file {f}".format(f=mkv['filename']))
        try:
            subprocess.call(["mkvextract", "tracks", mkv['full_path'], 
                    mkv['srt_track_id'] + ":" + srt_full_path ])
        except CalledProcessError as ex:
            print("Error al extraer subtitules del archivo {f}: {e}".format(f=mkv['full_path'], e=ex))

def main(argv):
    if not argv:
        print("Error, no directory supplied")
        sys.exit(1)
    if not os.path.isdir(argv[1]):
        sys.exit("Error, {f} is not a directory".format(f=argv[1]))
    mkv_list = []
    for root, dirs, files in os.walk(argv[1]):
        for name in files:
            (basename, ext) = os.path.splitext(name)
            if ext == '.mkv':
                (rawinfo, track_id) = get_track_id(os.path.join(root, name))
                mkv_list.append({ 'filename': name,
                                  'basename': basename,
                                  'extension': ext,
                                  'dir': root,
                                  'full_path': os.path.join(root, name),
                                  'srt_track_id': track_id,
                                  'raw_info': rawinfo
                                })
    extract_subs(mkv_list)

if __name__ == '__main__':
    main(sys.argv)
