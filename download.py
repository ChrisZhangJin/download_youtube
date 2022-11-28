import sys
import os
import getopt
import string
import unicodedata
from pytube import YouTube
from pytube.cli import on_progress


def usage(myname):
    myname=os.path.basename(myname)
    print(f"{myname} -a -s -i -o -t <output_path> -u <url>\n\ta: audio only\n\ts: silence\n\ti: interactive mode\n\to: output path\n\tt: whether to write track file")


all_letters=string.ascii_letters+"-_,"

def unicodeToAscii(s):
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
        and c in all_letters
    )


audio_only=False
silence=False
interactive=False
debug_log=False
track_file=False
output_path="./download"
url=""

if __name__ == '__main__':
    try:
        opts,args=getopt.getopt(sys.argv[1:], "asidto:u:")
    except getopt.GetoptError:
        usage(sys.argv[0])
        exit(2)

    for opt,arg in opts:
        if opt == "-a":
            audio_only=True
        elif opt == "-s":
            silence=True
        elif opt == "-i":
            interactive=True
        elif opt == "-d":
            debug_log=True
        elif opt == "-t":
            track_file=True
        elif opt == "-o":
            output_path=arg
        elif opt == "-u":
            url=arg
        else:
            pass

    # debug log
    if debug_log:
        print('-----------------------')
        print('[debug]audio_only:', audio_only)
        print('[debug]silence:', silence)
        print('[debug]interactive:', interactive)
        print('[debug]output_path:', output_path)
        print('[debug]url:',url)
        print('-----------------------')

    if url is None or url.strip()=="":
        print("[Err] no specified url!")
        usage(sys.argv[0])
        exit(3)
    
    if not silence:
        print("[info]you're going to download url:",url)
 
    if interactive:
        yt=YouTube(url, on_progress_callback=on_progress)
    else:  
        yt=YouTube(url)   

    title=unicodeToAscii(yt.title)
    download_caption_name=f'{title}.caption'

    # debug log
    if debug_log:
        print('[debug]yt.captions:\n', yt.captions)
    #caption=yt.captions['a.en']
    #if caption is not None:
    #    # caption is unavailable currently
    #    # https://github.com/pytube/pytube/issues/1347
    #    print(caption.xml_captions)
    #    with open(os.path.join(download_path, download_caption_name), 'w') as f:
    #        f.write(caption.generate_srt_captions())
    #        print('wrote down the caption file:', download_caption_name)

    if audio_only:
        streams=yt.streams.filter(only_audio=True, file_extension='mp4')
    else:
        streams=yt.streams.filter(file_extension='mp4')

    stream=streams[0]
    if interactive:
        print("Here are list of streams. Please chooose the one that you'd like to download")
        for i in range(len(streams)):
            print(f"[{i}] {streams[i]}")
        s=input("select one stream that you'd like to download:")
        s=int(s)

        if s<0 or s>=len(streams):
            print("Err: out of range.  your choice: ", s, ", total stream is ", len(streams))
            exit(2)
        
        stream=streams[s]
        
        print('=================\nyou selected stream:\n',stream)

    if audio_only:
        res=f"{stream.abr}_audio" if stream.abr is not None else "audio"
    else:
        res=stream.resolution
    download_filename=f'{title}_{res}.mp4'
    stream.download(output_path=output_path, filename=download_filename)
    
    if not silence:
        print(f'done downloading. download_path: {output_path}, download_filename: {download_filename}')
    else:
        print(download_filename)

    if track_file:
        with open(os.path.join(output_path, f'{title}.urltrack'), 'w') as f:
            f.write(f"{download_filename}\t{url}")


