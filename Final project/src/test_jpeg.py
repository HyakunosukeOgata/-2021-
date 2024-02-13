from flat.image import image
import glob
import os
import shutil
_luminance_quantization = bytes([ # Luminance quantization table in zig-zag order
    16, 11, 12, 14, 12, 10, 16, 14, 13, 14, 18, 17, 16, 19, 24, 40,
    26, 24, 22, 22, 24, 49, 35, 37, 29, 40, 58, 51, 61, 60, 57, 51,
    56, 55, 64, 72, 92, 78, 64, 68, 87, 69, 55, 56, 80,109, 81, 87,
    95, 98,103,104,103, 62, 77,113,121,112,100,120, 92,101,103, 99])
_chrominance_quantization = bytes([ # Chrominance quantization table in zig-zag order
    17, 18, 18, 24, 21, 24, 47, 26, 26, 47, 99, 66, 56, 66, 99, 99,
    99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99,
    99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99,
    99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99])

# Luminance DC code lengths
_ld_lengths = bytes(
    [0, 1, 5, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0])
# Luminance DC values
_ld_values = bytes([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])

# Luminance AC code lengths
_la_lengths = bytes([0, 2, 1, 3, 3, 2, 4, 3, 5, 5, 4, 4, 0, 0, 1, 125])
# Luminance AC values
_la_values = bytes([
      1,  2,  3,  0,  4, 17,  5, 18, 33, 49, 65,  6, 19, 81, 97,  7, 34,113,
     20, 50,129,145,161,  8, 35, 66,177,193, 21, 82,209,240, 36, 51, 98,114,
    130,  9, 10, 22, 23, 24, 25, 26, 37, 38, 39, 40, 41, 42, 52, 53, 54, 55,
     56, 57, 58, 67, 68, 69, 70, 71, 72, 73, 74, 83, 84, 85, 86, 87, 88, 89,
     90, 99,100,101,102,103,104,105,106,115,116,117,118,119,120,121,122,131,
    132,133,134,135,136,137,138,146,147,148,149,150,151,152,153,154,162,163,
    164,165,166,167,168,169,170,178,179,180,181,182,183,184,185,186,194,195,
    196,197,198,199,200,201,202,210,211,212,213,214,215,216,217,218,225,226,
    227,228,229,230,231,232,233,234,241,242,243,244,245,246,247,248,249,250])

# Chrominance DC code lengths
_cd_lengths = bytes([0, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0])
# Chrominance DC values
_cd_values = bytes([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])

# Chrominance AC code lengths
_ca_lengths = bytes([
    0, 2, 1, 2, 4, 4, 3, 4, 7, 5, 4, 4, 0, 1, 2, 119])
# Chrominance AC values
_ca_values = bytes([
      0,  1,  2,  3, 17,  4,  5, 33, 49,  6, 18, 65, 81,  7, 97,113, 19, 34,
     50,129,  8, 20, 66,145,161,177,193,  9, 35, 51, 82,240, 21, 98,114,209,
     10, 22, 36, 52,225, 37,241, 23, 24, 25, 26, 38, 39, 40, 41, 42, 53, 54,
     55, 56, 57, 58, 67, 68, 69, 70, 71, 72, 73, 74, 83, 84, 85, 86, 87, 88,
     89, 90, 99,100,101,102,103,104,105,106,115,116,117,118,119,120,121,122,
    130,131,132,133,134,135,136,137,138,146,147,148,149,150,151,152,153,154,
    162,163,164,165,166,167,168,169,170,178,179,180,181,182,183,184,185,186,
    194,195,196,197,198,199,200,201,202,210,211,212,213,214,215,216,217,218,
    226,227,228,229,230,231,232,233,234,242,243,244,245,246,247,248,249,250])

#iPhone 6 used huffman table, same as standard jpeg huffman table
DHT = {
    '_ld_lengths':_ld_lengths,
    '_ld_values':_ld_values,
    '_la_lengths':_la_lengths,
    '_la_values':_la_values,

    '_cd_lengths':_cd_lengths,
    '_cd_values':_cd_values,
    '_ca_lengths':_ca_lengths,
    '_ca_values':_ca_values,
}

def jpeg_quantization_table(table, quality):
    quality = max(0, min(quality, 100))
    if quality < 50:
        q = 5000//quality
    else:
        q = 200 - quality*2
    return bytes([max(1, min((i*q + 50)//100, 255)) for i in table])

DQT = {
    'luma':jpeg_quantization_table(_luminance_quantization, 50),
    'chroma':jpeg_quantization_table(_chrominance_quantization, 50)
}


def bmp_to_jpeg(folder):
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

    jpeg_folder = f'{folder}_jpeg'
    if os.path.exists(jpeg_folder):
        shutil.rmtree(jpeg_folder)
    os.mkdir(jpeg_folder)

    n = 1
    for input_img_name in img_list:
        input_jpg_image = image.open(input_img_name)
        save_path = f'{folder}_jpeg\\{n}.jpg'
        n += 1
        input_jpg_image.jpeg(save_path, DHT=DHT, DQT=DQT, Huffman_Optimized=True)
        print('jpg saved ', save_path)

video_name = 'stock'
if 1:
    bmp_to_jpeg(f'data\\exp_{video_name}\\transpose_bmp')
    bmp_to_jpeg(f'data\\exp_{video_name}\\original_bmp')


