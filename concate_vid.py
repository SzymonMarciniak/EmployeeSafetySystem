# import os 

# viedos = os.listdir("/media/szymon/TOSHIBA EXT/Monitoring/01-03-2023")

# for vid in viedos:


from moviepy.editor import *
import os
from natsort import natsorted

L = []

for root, dirs, files in os.walk("/media/szymon/TOSHIBA EXT/Monitoring/01-03-2023"):

    #files.sort()
    files = natsorted(files)
    for file in files:
        if os.path.splitext(file)[1] == '.mp4':
            filePath = os.path.join(root, file)
            video = VideoFileClip(filePath)
            L.append(video)

final_clip = concatenate_videoclips(L)
final_clip.to_videofile("output.mp4", fps=60, remove_temp=False)

