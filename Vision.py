import tensorflow as tf
import vision_config
import align.detect_face as df
import cv2
import os
import time
import numpy as np
import logging
                    
class Vision:
    __detect_face_minsize = 50
    __detect_face_threshold = [ 0.6, 0.6, 0.7 ]
    __detect_face_factor = 0.709
    SIZE_OF_INPUT_IMAGE = 160

    def __init__(self, database = None, mode = 'both'):
        self.mode = mode
        if mode != 'both' and mode != 'only_detect':
            raise TypeError("Doesn't support mode " + mode)
        if mode != 'only_detect' and database is None:
            raise TypeError("You have to pass database with mode '{}'".format(mode))
        logging.info("An vision object has been created with mode `{}`".format(mode))
        if mode != 'only_identify':
            self.__pnet, self.__rnet, self.__onet = self.load_detect_face_model(device= vision_config.DETECT_DEVICE)
    
    def get_working_mode(self):
        return self.mode

    @staticmethod
    def load_detect_face_model(device = 'auto'):
        with tf.Graph().as_default():
            if 'cpu' in device:
                config = tf.ConfigProto(device_count = {'GPU': 0})
                config.gpu_options.allow_growth = True
                sess = tf.Session(config=config)
            else:
                #gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.3)
                config = tf.ConfigProto(); 
                config.gpu_options.allow_growth = True
                sess = tf.Session(config= config)
            with sess.as_default():
                pnet, rnet, onet = df.create_mtcnn(sess, None)
        return (pnet, rnet, onet)

    @staticmethod
    def align_faces(bbox_faces, full_coordinate):
        res = []
        for face in bbox_faces:
            x,y,x1,y1 = face
            if not full_coordinate:
                x, y, w, h = face
                x1 = x + w
                y1 = y + h
            size_img = max(x1-x, y1-y)
            center_x = int((x1+x)/2)
            x = int(center_x - size_img/2)
            center_y = int((y1+y)/2)
            y = int(center_y - int(size_img/2))
            if size_img > 0 and x >= 0 and y >= 0:
                res.append((x, y, size_img, size_img))
        return res

    def face_detector(self, frame):
        if self.mode == 'only_identify':
            raise Exception('vision_object is on mode only_identify, cannot detect face')
        bboxes, _ = df.detect_face(frame, self.__detect_face_minsize,\
                                   self.__pnet, self.__rnet, self.__onet, \
                                   self.__detect_face_threshold, self.__detect_face_factor)
        faces = []
        for bbox in bboxes:
            x1 = int(bbox[2])
            y1 = int(bbox[3])
            x = int(bbox[0])
            y = int(bbox[1])
            if (x1-x) > 0 and (y1-y) > 0 and x >= 0 and y >= 0:
                faces.append((x, y, x1, y1))
        faces = Vision.align_faces(faces, full_coordinate= True)
        return faces
    
    def list_face_detector(self, list_frame):
        if self.mode == 'only_identify':
            raise Exception('vision_object is on mode only_identify, cannot detect face')
        list_dt_frame = []
        for frame in list_frame:
            list_dt_frame.append(dt_frame)
        rets = df.bulk_detect_face(list_dt_frame, 1/5,\
                                   self.__pnet, self.__rnet, self.__onet, \
                                   self.__detect_face_threshold, self.__detect_face_factor)
        list_faces = []
        for ret in rets:
            if ret is None:
                list_faces.append([])
                continue
            bboxes, _ = ret
            faces = []
            for bbox in bboxes:
                x1 = int(bbox[2])
                y1 = int(bbox[3])
                x = int(bbox[0])
                y = int(bbox[1])
                if (x1-x) > 0 and (y1-y) > 0:
                    faces.append((x, y, x1, y1))
            faces = Vision.align_faces(faces, full_coordinate= True)
            list_faces.append(faces)
        return list_faces