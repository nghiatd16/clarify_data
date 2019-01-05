import argparse
import time
from multiprocessing.pool import Pool
from streamer import FileVideoStream
from Vision import Vision
import logging
import os
import cv2
from AIF_Utils import FileUtils, Explorer, std_delta_time
import vision_config
def _multi_run_wrapper(args):
    try:
        process_video(*args)
    except ChildProcessError as e:
        logging.error(e)

def process_video(video_path, outdir):
    vision_object = Vision(mode="only_detect")
    video_name = FileUtils.get_file_name(video_path)
    logging.info("Starting process video: {}".format(video_name))
    st_time = time.time()
    saved_faces = 0
    processed_frames = 0
    fvs = FileVideoStream(video_path, preload_size=256, start=True)
    check_frame = 0
    delay_frame = 7
    while fvs.has_next():
        frame = fvs.get_next()
        processed_frames += 1
        if processed_frames - check_frame < delay_frame:
            continue
        check_frame = processed_frames
        faces = vision_object.face_detector(frame)
        for face in faces:
            x, y, w, h = face
            img_face = frame[y:y+h, x:x+w]
            out_path = os.path.join(outdir, "{}.jpg".format(time.time()))
            cv2.imwrite(out_path, img_face)
            saved_faces += 1
    elapsed_time = time.time() - st_time
    std_et = std_delta_time(int(elapsed_time))
    logging.info("Process {} in {} - processed_frames/total_frames {}/{} - Saved Faces {} - Avg FPS: {}".format(video_name, 
                                                                                                            std_et,
                                                                                                            processed_frames,
                                                                                                            fvs.total_frames,
                                                                                                            saved_faces,
                                                                                                            int(processed_frames/elapsed_time)))
        
def main(args):
    if not os.path.isdir(args.outdir):
        os.makedirs(args.outdir)
    else:
        logging.error("Out directory `{}` is alreadry existed".format(args.outdir))
        # exit(0)
    worker = int(args.worker)
    list_path = Explorer.explore_video(args.dir)
    if len(list_path) == 0:
        logging.info("No video is found in directory `{}`".format(args.dir))
        exit(0)
    lst_args = []
    sum_str = "\nSummary\n"
    sum_str = sum_str + "Directory: {}".format(os.path.abspath(args.dir)) + "\n"
    sum_str = sum_str + "Out directory: {}".format(os.path.abspath(args.outdir)) + "\n"
    sum_str = sum_str + "Found {} videos".format(len(list_path)) + "\n"
    sum_str = sum_str + "Worker: {}".format(worker) + "\n"
    sum_str = sum_str + "Input Scale: {}".format(vision_config.INPUT_SCALE) + "\n"
    sum_str = sum_str + "Detect Scale: {}".format(vision_config.DETECT_SCALE) + "\n"
    logging.info(sum_str)
    lst_args = []
    for vf in list_path:
        video_name = FileUtils.get_file_name(vf)
        outdir = os.path.join(args.outdir, video_name)
        os.makedirs(outdir)
        lst_args.append((vf, outdir))
    p = Pool(worker)
    p.map(_multi_run_wrapper, lst_args)

parser = argparse.ArgumentParser(description="")
parser.add_argument("-dir", help="-dir: Directory containning your data", dest="dir", action="store")
parser.add_argument("-outdir", help="-outdir: Directory containning your output data", dest="outdir", action="store")
parser.set_defaults(outdir="output")
parser.add_argument("-worker", help="-worker: Number of processing thread", dest="worker", action="store")
parser.set_defaults(worker="2")

if __name__ == "__main__":
    main(parser.parse_args())