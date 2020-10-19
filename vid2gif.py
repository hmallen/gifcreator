#!/usr/bin/python3

import argparse
import logging
import os
import shutil

import subprocess

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

VALID_INPUT_TYPES = ['mp4', 'm4v', 'mkv']

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', required=True,
                    help='Input file or directory of files for gif conversion.')
args = parser.parse_args()

if __name__ == '__main__':
    input_files = []
    if os.path.isdir(args.input):
        base_path = args.input

        with os.scandir(args.input) as dir_scan:
            for item in dir_scan:
                logger.debug(f'item: {item}')
                if not item.name.startswith('.') and item.is_file():
                    if item.split('.')[-1] in VALID_INPUT_TYPES:
                        item_path = f'{base_path}/{item}'
                        logger.info(f'Adding {item_path} to conversion list.')
                        input_files.append(item_path)
                    else:
                        logger.debug(f'Skipping incompatible file, {item}.')
                        continue

    else:
        base_path = os.path.dirname(args.input)
        input_files.append(args.input)

    ffmpeg_path = subprocess.run(
        ['which', 'ffmpeg'], capture_output=True, text=True).stdout.rstrip('\n')
    logger.debug(f'ffmpeg_path: {ffmpeg_path}')

    palette_file = 'palette.png'

    for in_file in input_files:
        out_file = f'{os.path.dirname(in_file)}/{os.path.basename(in_file).split(".")[0]}.gif'
        if out_file.startswith('/'):
            out_file = out_file.lstrip('/')
        logger.debug(f'out_file: {out_file}')

        palettegen_param = "[0:v] palettegen"
        file_palette_cmd = f'{ffmpeg_path} -i {in_file} -filter_complex PG_PLACEHOLDER {palette_file}'
        logger.debug(f'file_palette_cmd: {file_palette_cmd}')

        paletteuse_param = "[0:v][1:v] paletteuse"
        file_convert_cmd = f'{ffmpeg_path} -i {in_file} -i {palette_file} -filter_complex PU_PLACEHOLDER -r 10 {out_file}'
        logger.debug(f'file_convert_cmd: {file_convert_cmd}')

        palette_cmd_list = file_palette_cmd.split(' ')
        palette_cmd_list[palette_cmd_list.index(
            'PG_PLACEHOLDER')] = palettegen_param
        logger.debug(f'palette_cmd_list: {palette_cmd_list}')

        convert_cmd_list = file_convert_cmd.split(' ')
        convert_cmd_list[convert_cmd_list.index(
            'PU_PLACEHOLDER')] = paletteuse_param
        logger.debug(f'convert_cmd_list: {convert_cmd_list}')

        palette_proc = subprocess.run(
            palette_cmd_list, capture_output=True, text=True)
        logger.info(f'palette_proc: {palette_proc}')

        convert_proc = subprocess.run(
            convert_cmd_list, capture_output=True, text=True)
        logger.info(f'convert_proc: {convert_proc}')

        os.remove(palette_file)
