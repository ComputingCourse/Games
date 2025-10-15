from settings import *
from os import walk
from os.path import join

def import_image(*path, alpha = True, format = 'png'):
    '''loads and image and converts its pixel format for fast blitting'''
    full_path = join(*path) + f'.{format}'#use os.join so the it works of different operating systemes
    # convert alpha allows for alpha pixels(transparency)
    return pygame.image.load(full_path).convert_alpha() if alpha else pygame.image.load(full_path).convert()
    
def import_folder(*path):
    '''loads a folder of images and stores the in a list in the order their names'''
    frames = []
    for folder_path, subfolders, image_names in walk(join(*path)):
        for image_name in sorted(image_names, key = lambda name: int(name.split('.')[0])):
            full_path = join(folder_path, image_name)
            frames.append(pygame.image.load(full_path).convert_alpha())
    return frames 

def import_folder_dict(*path):
    '''loads a folder of images as a dictionary with the key being the image name'''
    frames = {}
    for folder_path, subfolders, image_names in walk(join(*path)):
        for image_name in image_names:
            index = image_name.split(".")[0]
            frames[index] = import_image(folder_path,index).convert_alpha()
    return frames
    
def import_sub_folders(*path):
    '''loads sub folders as lists within a dictionary with the keys bieng the sub folders name'''
    folders = {}
    for folder_path, subfolders, image_names in walk(join(*path)):
        if subfolders:
            for sub_folder in subfolders:
                folders[sub_folder] = import_folder(*path,sub_folder)
    return folders

