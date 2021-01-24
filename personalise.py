import csv
import optparse
import os.path
import shutil
import time
from threading import Thread
import requests
import urllib.request
import pathlib
import subprocess
from PIL import Image



def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-s", "--script", dest="script", help="Script which is communicating with Synthesia API. It is "
                                                            "creating a video with given script and csv information. "
                                                            "As well it adds a custom background to the video")
    parser.add_option("-b", "--background ", dest="background",
                      help="The path to the image of a background that will be used by the API. The image needs to "
                           "have 1920x1080 resolutions.")
    parser.add_option("-d", "--data", dest="data",
                      help="Provide the path to the .csv file from which data will be collected.")
    parser.add_option("-o", "--output", dest="output", help="Set a path to directory in which the video will be saved.")
    return parser.parse_args()


def read_csv_file(path):
    matriceDist = []
    csvReader = csv.reader(open(path), delimiter=',')
    for row in csvReader:
        matriceDist.append(row)
    return (matriceDist)


def create_scripts(csv, scripts):
    keys = []
    # Extract the key words
    for x in csv[0][1:]:
        keys.append("{" + x + "}")
    # for each user construct the script
    for users in csv[1:]:
        users.append(scripts)
        for x in range(0, len(keys)):
            # replace the wanted words
            users[-1] = users[-1].replace(keys[x], str(users[x + 1]))
        # delete all rows except first and last
        for x in range(0, len(keys)):
            del users[1]
    return csv


def generate_videos(scripts):
    # ids = []
    headers = {'Authorization': '73f1516e6ce4b2a656ed75c63c2499f7', 'Content-Type': 'application/json'}
    for script in scripts:
        payload = {"test": True, "input": [
            {"script": str(script[1]), "actor": "anna_costume1_cameraA", "background": "green_screen"}]}
        r = requests.post("https://api.synthesia.io/v1/videos", json=payload, headers=headers)
        # ids.append(r.json()['id'])
        del script[1]
        script.append(r.json()['id'])
    return scripts


def move_file(filename, dirname):
    filepath = os.path.join(pathlib.Path().absolute(), filename)
    path = os.path.join(pathlib.Path().absolute(), dirname)
    if not os.path.exists(path):
        os.mkdir(path)
    shutil.move(filepath, path)
    return "./" + dirname


def add_background(dirpath, video, background):
    video = dirpath + "/" + video
    finalpath = video.replace('temp-','')
    if os.path.exists(finalpath):
        os.remove(finalpath)
    subprocess.call(
        "ffmpeg -i " + background + " -i " + video + " -filter_complex [1:v]colorkey=0xE2E6FF:0.1:0.1[ckout];[0:v][ckout]overlay[out] -map [out] -map 1:a:? " + finalpath,shell=True)
    os.remove(video)
    print("Your video can be found in: " + finalpath)


def get_videos(id, video_id, output, background):
    headers = {'Authorization': 'XXXXXXXXXXXXXXXXXXXX'}
    status = ''
    print("Processing the video with ID:" + video_id)
    while status != "COMPLETE":
        r = requests.get("https://api.synthesia.io/v1/videos/" + video_id, headers=headers)
        status = r.json()['status']
        time.sleep(5)
    print("Video with id:" + video_id + " is finished.")
    url = r.json()['download']
    filename = "temp-" + id + ".mp4"
    #download the video
    urllib.request.urlretrieve(url, filename)
    #construct the directory path
    dirpath = move_file(filename, output)
    #change the backgroud
    add_background(dirpath, filename, background)


if __name__ == '__main__':
    # Collect the arguments
    (options, arguments) = get_arguments()

    if not options.script:  # if filename is not given
        print('Script not given. Type -h for help.')
    elif not options.background:  # if filename is not given
        print('Background path not given. Type -h for help.')
    elif not options.data:  # if filename is not given
        print('Data csv file not given. Type -h for help.')
    elif not options.output:  # if filename is not given
        print('Output path not given. Type -h for help.')
    else:
        if not os.path.exists(options.data):
            print("Data file doesn't exist. Input different path.")
        elif not os.path.exists(options.background):
            print("Background file doesn't exist. Input different path.")
        else:
            with Image.open(options.background) as img:
                width, height = img.size
            if height != 1080 or width != 1920:
                print("Background image needs to have other resolution (1920x1080).")
                exit()
            file = read_csv_file(options.data)
            # Create the script for each row
            scripts = create_scripts(file, options.script)
            del scripts[0]
            #generate video for each element from csv and return their ids
            ids = generate_videos(scripts)
            #for each video download it
            for id in ids:
                Thread(target=get_videos, args=(id[0], id[1], options.output, options.background)).start()
