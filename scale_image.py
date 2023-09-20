"""
    Scale, sort or crop images
"""

from PIL import Image, ImageOps
import sys
import argparse
import os
import ntpath
import re
import cv2
import numpy as np
from tqdm import tqdm
from reportlab.pdfgen import canvas
from cv2 import imread


plus_num = 3
SUPPORTED_IMAGES = [".png", ".jpg", ".jpeg"]

def list_n_sort_dir(directory:str) -> list:
    """
        Renaming files to n.jpg where n is the number in the original filename
    """
    def remove_from_list(the_list, item):
        return [value for value in the_list if value != item]

    def get_digits(word:str) -> int:
        reg = re.findall(r'\d+', word)
        if reg:
            return int(reg[0])
        return False

    for root, dirs, files in os.walk(directory):
        print(root, dirs)
        new_files = []
        for filename in files:
            #print(filename)
            _, extension = os.path.splitext(filename)  # Seperating the file dir and extension
            if not extension.lower() in SUPPORTED_IMAGES:
                continue
            digits = get_digits(filename)
            # If filename doesn't contain digits
            if not digits:
                continue
            full_name = root + os.sep + filename
            new_name = f"{digits + plus_num}.jpg"
            # If filename alredy exists in dir
            if new_name in files or new_name in new_files:
                continue
            new_files.append(new_name)
            full_new_name = f"{root}/{digits + plus_num}.jpg"
            print(f"Renaming {filename} to {new_name}")
            os.rename(full_name, full_new_name)
                    


def create_dir(dir_name:str):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    return dir_name

def _generate_save_name(file_dir:str, new_name:str, out_dir:str) -> str:
        if new_name:
            return out_dir + os.sep + new_name
        img_path, extension = os.path.splitext(file_dir)  # Seperating the file dir and extension
        save_name = out_dir + os.sep + ntpath.basename(img_path) + "-scaled" + extension  # Assembling it all
        return save_name


def crop_image(img_dir:str, scale:float=0, out_dir:str=".", resolution:tuple=(), override:bool=False):
    """
        Cropping an image by a percentage or by a specific resolution
    """

    image = Image.open(img_dir)
    image = ImageOps.exif_transpose(image)
    width, height = image.size

    if scale:
        new_width = int(width * scale)
        new_height = int(height * scale)
    else:
        new_width, new_height = resolution
    new_image = image.crop((0, 0, new_width, new_height))
    #new_image = image.crop((0, 0, 2450, 3800))
    save_name = _generate_save_name(img_dir, new_name="", out_dir=out_dir)
    new_image.save(save_name)


def crop_dir(dir_name:str, scale:float=0, resolution:tuple=()):
    out_dir = dir_name + os.sep + "Cropped"
    out_dir = create_dir(out_dir)

    for i, img_name in enumerate(os.listdir(dir_name)):
        img_name_and_dir = dir_name + img_name
        _, extension = os.path.splitext(img_name_and_dir)  # Seperating the file dir and extension
        if extension.lower() in SUPPORTED_IMAGES:
            crop_image(img_name_and_dir, scale=scale, out_dir=out_dir, resolution=resolution)
            print(f"Cropped {i}")


def scale_image(img_dir:str, scale:float=0, out_dir:str=".", new_name:str="", resolution:tuple=(), override="") -> None:
    """
        Scaling an image by a percentage or by a specific resolution
    """
    image = Image.open(img_dir)
    # If the image has exif metadata of rotation
    try:
        image = ImageOps.exif_transpose(image)
    except:
        print(f"error at {img_dir}")
    if resolution:
        new_width, new_height = resolution
    else:
        width, height = image.size
        new_width, new_height = int(width * scale), int(height * scale)

    filename, ext = os.path.splitext(img_dir)
    # Converting to jpg if it's a png
    if ext.lower() == ".png":
        image = image.convert('RGB')
    new_image = image.resize((new_width, new_height))
    if new_name:
        save_name = new_name
    else:
        save_name = f"{out_dir}{os.sep}{os.path.basename(filename)}.jpg"

    #save_name = _generate_save_name(img_dir, new_name, out_dir)
    try:
        new_image.save(save_name)
    except Exception as e:
        print(e)
        print(f"Error at {save_name}")


def ls_recursively(dirname:str):
    """
        Scanning in a dir files recursively
        solves the error when trying to OCR a dir
    """
    full_names = []
    for root, dirs, files in os.walk(dirname):
        for f in files:
            full_names.append(os.path.join(root, f))
    return full_names


def scale_dir(dir_name:str, scale:float, override:bool=False, resolution:tuple=()) -> None:
    """
        Scaling a directory of images by the 'scale' margin, 
        Saving to 'out_dir'
    """
    out_dir = dir_name + os.sep + "Scaled"
    out_dir = create_dir(out_dir)

    # iterable = os.listdir(dir_name)
    iterable = ls_recursively(dir_name)
    for i, img_name in tqdm(enumerate(iterable), desc= "Scaled", total=len(iterable), unit="pic"):
        # img_name_and_dir = dir_name + img_name
        img_name_and_dir = img_name
        _, extension = os.path.splitext(img_name_and_dir)  # Seperating the file dir and extension
        if not extension.lower() in SUPPORTED_IMAGES:
            continue
        if override:
            new_name = os.path.splitext(img_name)[0] + '.jpg'
            scale_image(img_name_and_dir, scale, new_name=new_name, resolution=resolution)
        else:
            scale_image(img_name_and_dir, scale, out_dir, resolution=resolution)
            # print(f"Scaled {i}")


def pdfy(images:list[str], save_name:str) -> str:
    """
        Creating a pdf from a list of image paths
    """
    pdf = canvas.Canvas(save_name)
    
    for i, img in enumerate(images):
        print(i)
        im_height, im_width = imread(img, 0).shape
        pdf.setPageSize((im_width, im_height))
        pdf.drawImage(img, 0, 0, width=im_width, height=im_height)
        pdf.showPage()  # Save page
    pdf.save()
    return save_name


def _set_actions(dir:str) -> tuple:
    """
        Determine if we handle a file or dir, and assign the apropriate functions
    """
    # If it's a directory
    if os.path.isdir(dir):  
        actions = {"scale":scale_dir, "crop":crop_dir}
        if not dir.endswith(os.sep):
            dir = dir + os.sep
        return dir, actions

    # If it's a directory or file (file)
    elif os.path.exists(dir):
        actions = {"scale":scale_image, "crop":crop_image}
        return dir, actions
    
def _set_action(dir:str, is_cropping:bool) -> tuple:
    """
        Determine what function to call to handle the inputs
    """
    dir, actions = _set_actions(dir)
    if is_cropping:
        return dir, actions["crop"]
    return dir, actions["scale"]


def main(args):
    dir = args.d
    override = args.override
    #Sorting
    if args.sort:
        list_n_sort_dir(dir)
        return
    elif args.c:  # Crop
        is_cropping = True
        main_arg = args.c
    elif args.s:  # Sort
        is_cropping = False
        main_arg = args.s
    else:
        print("Invalid arguments")
        return
    # Getting the right function to handle the inputs
    dir, action = _set_action(dir, is_cropping)

    # One arg means a percentage for scaling/cropping
    if len(main_arg) == 1:
        scale = main_arg[0] / 100
        action(dir, scale, override=override)
     # Two args mean it's a resolution for scaling/cropping
    elif len(main_arg) == 2:
        action(dir, resolution=main_arg, override=override)
    
    else:
        print("exiting...")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Usage - python3 scale_image -d <directory> [-s <scale> -c <crop> --sort]')
    parser.add_argument('-d', help='Directory of the images', type=str, required=True)
    parser.add_argument('-s', help='scale or resolution for resizing(1-99 or x,x)', nargs="*", type=int)
    parser.add_argument('-c', help='scale or resolution for cropping(1-99 or x,x)', nargs="*", type=int)
    parser.add_argument('--sort', help='whether to sort the images', action="store_true")
    parser.add_argument('--override', help='whether to override the existing images', action="store_true")
    args = parser.parse_args()
    main(args)
    

