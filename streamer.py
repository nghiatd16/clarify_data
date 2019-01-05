import logging
import cv2
import os
import time
from threading import Thread
from queue import Queue

class FileVideoStream:
    def __init__(self, path, preload_size = 1024, start = True):
        assert os.path.isfile(path), "File Not Found !!"
        self.path = path
        self.video_capture = cv2.VideoCapture(path)
        self.total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(self.video_capture.get(3))  
        self.height = int(self.video_capture.get(4))
        self.preload_size = preload_size
        self.frame_queue = Queue(maxsize=preload_size)
        self.running_status = False
        if start:
            self.start()
    

    def start(self):
        t = Thread(target=self.update, args=())
        t.daemon = True
        self.running_status = True
        t.start()
        return self
    

    def update(self):
        while self.video_capture.isOpened() and self.running_status:
            if not self.frame_queue.full():
                ret, frame = self.video_capture.read()
                if ret:
                    self.frame_queue.put(frame)
                else:
                    self.running_status = False
                    break
            else:
               time.sleep(0.0001)

    def has_next(self):
        return (not self.frame_queue.empty()) or (self.running_status)
    
    
    def get_next(self):
        return self.frame_queue.get()
    

    def stop(self):
        self.running_status = False
    

    def restart(self):
        self.running_status = False
        time.sleep(0.1)
        del self.frame_queue
        self.frame_queue = Queue(maxsize=self.preload_size)
        self.video_capture = cv2.VideoCapture(self.path)
        self.start()