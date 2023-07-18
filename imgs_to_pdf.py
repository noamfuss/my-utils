import argparse
import os
from reportlab.pdfgen import canvas
from cv2 import imread
import re
from tqdm import tqdm

def get_digits(word:str) -> int:
    reg = re.findall(r'\d+', word)
    print(''.join(reg))
    if reg:
        return int(''.join(reg))  # An int to sort files by
    return False


def remove_from_list(the_list, item):
    return [value for value in the_list if value != item]

def write_pdf(images:list[str], save_name:str):
    """
        Creating a pdf from a list of omage paths
    """
    pdf = canvas.Canvas(save_name)
    
    for i, img in tqdm(enumerate(images), desc="Processed", total=len(images), unit="pic"):
        im_height, im_width = imread(img, 0).shape
        pdf.setPageSize((im_width, im_height))
        pdf.drawImage(img, 0, 0, width=im_width, height=im_height)
        pdf.showPage()  # Save page
    pdf.save()


def sort_files(directory:str) -> list:
    """
        Scanning a dir, and returning a list of the files 
        in the dir, sorted by the digits in the filename
    """
    file_extensions = [".jpg", ".jpeg", ".png"]
    for root, dirs, files in os.walk(args.d):
        print(root, dirs)
        for filename in files:
            #print(filename)
            f_extension = os.path.splitext(filename)[-1]
            if not f_extension in file_extensions:
                continue
            digits = get_digits(filename)
            if digits:
                full_name = root + os.sep + filename
                images.append((digits, full_name))
    images.sort(key=lambda a: a[0])
    sorted_filenames = list(map(lambda a: a[1], images))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Usage - python3 pytess.py -d <directory>')
    parser.add_argument('-d', help='directory', type=str, required=True)
    args = parser.parse_args()
    #parser.add_argument('--dir', help='the file is a dir of pictures', action="store_true")
    list_dir = os.listdir(args.d)
    # images = [None] * len(list_dir)  # Creating an empty list with n cells
    # print(len(images))
    images = []
    file_extensions = [".jpg", ".jpeg", ".png"]
    for root, dirs, files in os.walk(args.d):
        print(root, dirs)
        for filename in files:
            #print(filename)
            f_extension = os.path.splitext(filename)[-1]
            if not f_extension in file_extensions:
                continue
            digits = get_digits(filename)
            if digits:
                full_name = root + os.sep + filename
                images.append((digits, full_name))
                # images[digits] = full_name

    #images = filter(None, images)
    # images = remove_from_list(images, None)
    images.sort(key=lambda a: a[0])
    sorted_filenames = list(map(lambda a: a[1], images))
    print(sorted_filenames[:20])
    dir_save_name = os.path.basename(args.d) + ".pdf"
    write_pdf(sorted_filenames, dir_save_name)
    print(f"Output file at {dir_save_name}")