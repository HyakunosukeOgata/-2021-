import os
import cv2
import numpy as np
import shutil
import glob
import codecs
import subprocess
import time
def bmp_to_video(folder):
    in_folder_glob = f'{folder}\\*.bmp'
    output_img_name = folder + '.mp4'
    img_list = glob.glob(in_folder_glob)
    if img_list and len(img_list) > 0:
        pass
    else:
        return
    input_frame_rate = 30
    output_frame_rate = 30
    duration = '{:.5f}'.format(1.0 / input_frame_rate)
    lines = []
    input_file_list = 'demux_file_list.txt'
    input_file_list = os.path.abspath(input_file_list)
    if 1:
        with codecs.open(input_file_list, "w", "utf-8") as f:
            for input_img_name in img_list:
                f.write("file '{}'\n".format(input_img_name.replace("\\", "\\\\")))
                f.write("duration {}\n".format(duration))
                last_line = "file '{}'\n".format(input_img_name.replace("\\", "\\\\"))
            f.write(last_line)
            f.close()
    Comment_string = f'ffmpeg -f concat -safe 0 -i "{input_file_list}" -vcodec libx264 -crf 18 -vf "fps={output_frame_rate}" "{output_img_name}"'
    if (os.path.isfile(output_img_name)):
        os.remove(output_img_name)
    subprocess.run(Comment_string, shell=True, check=True)

def remake_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path + '\\')
    time.sleep(1)
    os.mkdir(folder_path)

#ffmpeg -i "data\guys.mpg" -q:v 0 -qmin 1 -vf 'scale=1280:-1' "data\bmp_guys\%05d.bmp"
#ffmpeg -i "data\bird1.mp4" -q:v 0 -qmin 1 -vf 'scale=1280:-1' "data\bmp_bird1\%05d.bmp"
#ffmpeg -i "data\stock2.mp4" -q:v 0 -qmin 1 -vf 'scale=1280:-1' "data\bmp_stock2\%05d.bmp"

#ffmpeg -i "data\stock.mp4" -ss 00:13:04 -to 00:13:14 -c:v copy "data\stock2.mp4"
#ffplay -i "data\stock.mp4" -vf 'crop=1280:720:100:240,fps=30'
#-vcodec libx264 -crf 18
#bird1.mp4

video_name = 'stock'
total_frames = 296
original_bmp_folder = f'data\\exp_{video_name}\\original_bmp'
if 1:
    #video_name = 'bird1'
    #video_name = 'stock'
    Comment_string = f'ffmpeg -i "data\\{video_name}.mp4" -q:v 0 -qmin 1 "data\\exp_{video_name}\\original_bmp\\%05d.bmp"'
    remake_folder(f'data\\exp_{video_name}')
    remake_folder(original_bmp_folder)
    subprocess.run(Comment_string, shell=True, check=True)

    def delete_frames(folder, keep_frames):
        files = f'{folder}\\*.bmp'
        files = glob.glob(files)
        keep_frames = [f'{str(_+1).zfill(5)}.bmp' for _ in range(keep_frames)]
        for f in files:
            if not f.split('\\')[-1] in keep_frames:
                os.remove(f)
    delete_frames(original_bmp_folder, total_frames)

    buffer = np.zeros([100,720,1280,3], dtype = np.uint8)
    transpose_bmp_folder = f'data\exp_{video_name}\\transpose_bmp'
    remake_folder(transpose_bmp_folder)

    for i in range(0, total_frames, 100):
        imgs = []
        for frame_number_offset in range(100):
            read_frame = i + frame_number_offset+1
            if read_frame > total_frames:
                break
            img_bmp = cv2.imread(f'{original_bmp_folder}\\{str(read_frame).zfill(5)}.bmp')
            buffer[frame_number_offset,:,:,:] = img_bmp
            print(f'read_frame:{read_frame}, save to buffer:{frame_number_offset}')
        print('buffer read done')
        #轉置使得新影片的禎數等於原影片的高
        for i_for_old_video_height in range(720):
            new_video_frame_npy = f'{transpose_bmp_folder}\\{str(i_for_old_video_height+1).zfill(5)}.npy'
            if not os.path.exists(new_video_frame_npy):
                new_frame_data = np.zeros([total_frames, 1280, 3], dtype = np.uint8)
            else:
                new_frame_data = np.load(new_video_frame_npy)
            old_video_frame_from = i
            old_video_frame_to = i+100
            if old_video_frame_to > total_frames:
                old_video_frame_to = total_frames
            print(f'new_video_frame:{new_video_frame_npy} frame {old_video_frame_from} to {old_video_frame_to}, read_from_buffer scan line:{i_for_old_video_height}')
            new_frame_data[old_video_frame_from:old_video_frame_to,:,:] = buffer[:old_video_frame_to-old_video_frame_from, i_for_old_video_height, :, :]
            np.save(new_video_frame_npy, new_frame_data)

    for i_for_old_video_height in range(720):
        new_video_frame_npy = f'{transpose_bmp_folder}\\{str(i_for_old_video_height+1).zfill(5)}.npy'
        new_frame_data = np.load(new_video_frame_npy)
        cv2.imwrite(f'{transpose_bmp_folder}\\{str(i_for_old_video_height+1).zfill(5)}.bmp' , new_frame_data)
        os.remove(new_video_frame_npy)

    bmp_to_video(f'data\\exp_{video_name}\\original_bmp')
    bmp_to_video(f'data\\exp_{video_name}\\transpose_bmp')


original_video_height = 720
if 1:
    transpose_mp4 = f'data\\exp_{video_name}\\transpose_bmp.mp4'
    Comment_string = f'ffmpeg -i "{transpose_mp4}" -q:v 0 -qmin 1 -vf "scale=1280:-1" "data\\exp_{video_name}\\transpose_mp4_extract\\%05d.bmp"'
    remake_folder(f'data\\exp_{video_name}\\transpose_mp4_extract\\')
    subprocess.run(Comment_string, shell=True, check=True)


    buffer = np.zeros([100,total_frames,1280,3], dtype = np.uint8)
    remake_folder(f'data\\exp_{video_name}\\transpose_mp4_extract_transpose_back\\')

    for i in range(0, original_video_height, 100):
        imgs = []
        for frame_number_offset in range(100):
            read_frame = i + frame_number_offset+1
            if read_frame > 720:
                break
            img_bmp = cv2.imread(f'data\\exp_{video_name}\\transpose_mp4_extract\\{str(read_frame).zfill(5)}.bmp')
            buffer[frame_number_offset,:,:,:] = img_bmp
            print(f'read_frame:{read_frame}, save to buffer:{frame_number_offset}')
        print('buffer read done')
        #轉置使得新影片的禎數等於原影片的高
        for i_for_old_video_frames in range(total_frames):
            new_video_frame_npy = f'data\\exp_{video_name}\\transpose_mp4_extract_transpose_back\\{str(i_for_old_video_frames+1).zfill(5)}.npy'
            if not os.path.exists(new_video_frame_npy):
                new_frame_data = np.zeros([720,1280,3], dtype = np.uint8)
            else:
                new_frame_data = np.load(new_video_frame_npy)
            old_video_frame_from = i
            old_video_frame_to = i+100
            if old_video_frame_to > 720:
                old_video_frame_to = 720
            fetch_height = old_video_frame_to - old_video_frame_from
            print(f'new_video_frame:{new_video_frame_npy} frame {old_video_frame_from} to {old_video_frame_to}, read_from_buffer scan line:{i_for_old_video_frames}')
            new_frame_data[old_video_frame_from:old_video_frame_to,:,:] = buffer[0:fetch_height,i_for_old_video_frames,:,:]
            np.save(new_video_frame_npy, new_frame_data)

    for i_for_old_video_height in range(total_frames):
        new_video_frame_npy = f'data\\exp_{video_name}\\transpose_mp4_extract_transpose_back\\{str(i_for_old_video_height+1).zfill(5)}.npy'
        new_frame_data = np.load(new_video_frame_npy)
        cv2.imwrite(f'data\\exp_{video_name}\\transpose_mp4_extract_transpose_back\\{str(i_for_old_video_height+1).zfill(5)}.bmp' , new_frame_data)
        os.remove(new_video_frame_npy)

    bmp_to_video(f'data\\exp_{video_name}\\transpose_mp4_extract_transpose_back')


print(f'bmp from {video_name}.mp4 is saved to data\exp_{video_name}\original_bmp')
print(f'transposed bmp is saved to data\exp_{video_name}\\transpose_bmp')

print(f'bmp encode H264 is saved to data\\exp_{video_name}\\original_bmp.mp4')
print(f'transposed bmp encode H264 is saved to data\\exp_{video_name}\\transpose_bmp.mp4')

print(f'transpose_bmp.mp4 is transposed back and saved to data\\exp_{video_name}\\transpose_mp4_extract_transpose_back.mp4')
