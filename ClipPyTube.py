from pytube import YouTube
from pytube.request import filesize
from rich import print
from rich.progress import FileSizeColumn, Progress, TotalFileSizeColumn

import pyperclip
import schedule
import os
import threading
import time
import configparser
import pyfiglet


clipboard = []

scriptPath = os.path.dirname(__file__)
downloadPath =  scriptPath + "/clipTube_Downloads"

prog = Progress(FileSizeColumn(),('/'),TotalFileSizeColumn())


def show_progress_bar(stream, chunk, bytes_remaining):
    prog.update(task, completed=stream.filesize - bytes_remaining)
    #this show the bytes_remaining, use rich to display a progress bar


def on_complete(stream, file_path):
    prog.remove_task(task)
    prog.stop()
    print('[green] Downloaded ', file_path.split('/')[-1],'\n')


def download(last_copied):
    youtube = YouTube(last_copied)
    print('[yellow]',youtube.title,'\n')
    youtube.register_on_progress_callback(show_progress_bar)
    youtube.register_on_complete_callback(on_complete)
    #bug fix needed app crashes
    #getbyresolution may return none which have to deal with next possible resolution implement it
    stream = youtube.streams

    i = 0
    while i < len(defaultResolution):
        stream = youtube.streams.get_by_resolution(defaultResolution[i])
        if stream == None and i < len(defaultResolution)-1:
            print('[red]',defaultResolution[i],'is not available...trying again with',defaultResolution[i+1],'\n')
            i += 1
        else:
            break

    if i == len(defaultResolution)-1:
        print('[red]Video not available...')
        return

    global task
    #python the download function is working so no progress thread
    task = prog.add_task("downloading...", total=stream.filesize)
    prog.start()
    stream.download(output_path=downloadPath)
    

    # progress bar shows even after the download is completed it should be disappear
    # there is no simultanious downloads
    # the clipboard youtube links must be all present in the list


def job():
    last_copied = pyperclip.paste()
    if last_copied not in clipboard and ("www.youtube.com/watch" in last_copied or "youtu.be" in last_copied):
        clipboard.append(last_copied)
        #print("[green]",clipboard[-1],"\n")
        download(last_copied)


def run_continuously(interval=1):
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


def make_directory():
    try:

        os.mkdir(downloadPath)
        print("[green]Directory Created!")

    except FileExistsError:
        
        print("[red]Directory Already Exists!")


def make_config():
    config = configparser.ConfigParser()
    config["defaults"] = {'resolution':'720p,480p,360p,240p,144p'}
    with open(scriptPath+'/clipTubeConfig.ini', 'w') as configfile:
        config.write(configfile)
    

def read_config():
    config = configparser.ConfigParser()
    config.read(scriptPath+'/clipTubeConfig.ini')
    global defaultResolution
    defaultResolution = config['defaults']['resolution'].split(',')


if __name__ == "__main__":

    banner = pyfiglet.figlet_format('ClipPyTube',font='larry3d')
    print('[red]',banner)
    make_config()
    read_config()
    make_directory()
    schedule.every(1).second.do(job)
    stop_run_continuously = run_continuously()
    print("[green]Enter 'q' to quit\n")
    # this produces exception when ctrl + c is pressed
    
    while input() != 'q':
        continue
    stop_run_continuously.set()
    print("Bye...! :hand: ")
