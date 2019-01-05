import os
import logging
import time
logging.basicConfig(format='[%(levelname)s|%(asctime)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)

def std_delta_time(delta):
    if delta < 60:
        return time.strftime("%S seconds", time.gmtime(delta))
    if delta < 3600:
        return time.strftime("%M minutes : %S seconds", time.gmtime(delta))
    return time.strftime("%H hours : %M minutes : %S seconds", time.gmtime(delta))

class FileUtils:
    @staticmethod
    def get_file_extension(path):
        return path.split(".")[-1]
    
    @staticmethod
    def get_file_name(path):
        base_name = os.path.basename(path)
        return base_name.split(".")[0]

class Explorer:
    video_extension = ("avi", "flv", "mp4", "mpeg", "mov")
    image_extension = ("jpg", "jpeg", "png")
    sound_extension = ("mp3", "flac", "wav")
    @staticmethod
    def explore_video(directory):
        cwd = os.getcwd()
        try:
            lst_path = []
            os.chdir(directory)
            for f in os.listdir():
                file_ext = f.split(".")[-1]
                if not file_ext.lower() in Explorer.video_extension:
                    continue
                lst_path.append(os.path.abspath(f))
            os.chdir(cwd)
            return lst_path
        except Exception as e:
            logging.exception(e)
    
    @staticmethod
    def explore_image(directory):
        cwd = os.getcwd()
        try:
            lst_path = []
            os.chdir(directory)
            for f in os.listdir():
                file_ext = f.split(".")[-1]
                if not file_ext.lower() in Explorer.image_extension:
                    continue
                lst_path.append(os.path.abspath(f))
            os.chdir(cwd)
            return lst_path
        except Exception as e:
            logging.exception(e)
    
    @staticmethod
    def explore_sound(directory):
        cwd = os.getcwd()
        try:
            lst_path = []
            os.chdir(directory)
            for f in os.listdir():
                file_ext = f.split(".")[-1]
                if not file_ext.lower() in Explorer.sound_extension:
                    continue
                lst_path.append(os.path.abspath(f))
            os.chdir(cwd)
            return lst_path
        except Exception as e:
            logging.exception(e)