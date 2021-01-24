# Synthesia

## Prerequisites
1. Python 3.x (https://www.python.org/downloads/)
2. ffmpeg (https://ffmpeg.org/download.html)
3. Access Synthesia API (https://www.synthesia.io/create-account)
4. In line 88 input your API KEY

The script that is comunicating with the https://docs.synthesia.io/docs API. It sends it hte request the script that is consting of command line arguments and csv file. As a response it uses the Video file form synthesisa. Finalay it substitutes the background from "green screen" to a file requested as a command line parameter using ffmpeg.

## Example Use
```bash
python personalise.py -d data.csv -s "Hey {name} your age is {age}." -b background.jpg -o output
```
