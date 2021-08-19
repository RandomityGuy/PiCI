from io import BytesIO
import subprocess, os, sys, threading, select;


p = subprocess.Popen(['ping', 'google.com'], stdout=subprocess.PIPE)
p2 = subprocess.Popen(['ping', 'bing.com'], stdout=subprocess.PIPE)
p3 = subprocess.Popen(['ping', 'example.com'], stdout=subprocess.PIPE)
p4 = subprocess.Popen(['ping', 'microsoft.com'], stdout=subprocess.PIPE)
p5 = subprocess.Popen(['ping', 'marbleblast.com'], stdout=subprocess.PIPE)
p6 = subprocess.Popen(['ping', 'reddit.com'], stdout=subprocess.PIPE)

proclist = [p,p2,p3,p4,p5,p6]

def readproc():
    streams = [proc.stdout for proc in proclist]
    while True:
        rstreams, _, _ = select.select(streams, [], [])
        for stream in rstreams:
            line = stream.readline()
            print(line.decode(), end='')
        if all(proc.poll() is not None for proc in proclist):
            break
t = threading.Thread(target=lambda: readproc())
t.daemon = True
t.start()

p.wait()

input()