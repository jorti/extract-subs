#!/usr/bin/env python3
"""
Copyright 2015 Juan Orti Alcaine <j.orti.alcaine@gmail.com>


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
import subliminal


def get_mkv_track_id(file):
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


def download_subs(file):
    print("Downloading subs for {f}".format(f=file['filename']))
    print("    full path: {f}".format(f=file['full_path']))
    video = subliminal.scan_videos([file['full_path'], ], subtitles=False, embedded_subtitles=False)
    subliminal.download_best_subtitles(video, {Language('eng')})


def extract_mkv_subs(file):
    print("Extracting subs for {f}".format(f=file['filename']))
    try:
        subprocess.call(["mkvextract", "tracks", file['full_path'], 
                        file['srt_track_id'] + ":" + srt_full_path ])
    except CalledProcessError as ex:
        print("Error al extraer subtitules del archivo {f}: {e}".format(f=file['full_path'], e=ex))


def extract_subs(files):
    for file in files:
        if file['srt_exists']:
            continue
        if not file['srt_track_id']:
            print("No subtitles for: {f}".format(f=file['filename']))
            download_subs(file)
        else:
            extract_mkv_subs(file)


def main(argv):
    supported_extensions = ['.mkv', '.mp4']
    if not argv:
        print("Error, no directory supplied")
        sys.exit(1)
    if not os.path.isdir(argv[1]):
        sys.exit("Error, {f} is not a directory".format(f=argv[1]))
    file_list = []
    for root, dirs, files in os.walk(argv[1]):
        for name in files:
            (basename, ext) = os.path.splitext(name)
            if ext in supported_extensions:
                print("Analyzing {f}".format(f=name))
                if ext == 'mkv':
                    (raw_track_info, track_id) = get_mkv_track_id(os.path.join(root, name))
                else:
                    raw_track_info = None
                    track_id = None
                srt_full_path = os.path.join(root, basename + ".srt")
                if os.path.isfile(srt_full_path):
                    srt_exists = True
                else:
                    srt_exists = False
                file_list.append({ 'filename': name,
                                   'basename': basename,
                                   'extension': ext,
                                   'dir': root,
                                   'full_path': os.path.join(root, name),
                                   'srt_track_id': track_id,
                                   'srt_full_path': srt_full_path,
                                   'srt_exists': srt_exists,
                                   'raw_info': raw_track_info
                                 })
    extract_subs(file_list)


if __name__ == '__main__':
    main(sys.argv)
