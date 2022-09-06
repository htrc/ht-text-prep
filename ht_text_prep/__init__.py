# Main library file
# by Ashan Liyanage, Ryan Dubnicek, Yuerong Hu
# HathiTrust Research Center (2021), Contact htrc-help@hathitrust.org with issues/feedback

from cgi import print_directory
import cmd
import re
import csv
import glob
import os
import shutil
import sys
from wsgiref.handlers import read_environ
from zipfile import ZipFile
from pathlib import Path
from typing import List
from tqdm import tqdm
from ht_text_prep.htrc.models import HtrcPage
from ht_text_prep.htrc.runningheaders import parse_page_structure

CRED = '\033[91m'
CEND = '\033[0m'
CURL = '\33[4m'
CGREEN = '\33[32m'
CGREY = '\33[100m'
CBLINK = '\33[5m'


def unzip_file(file_name):
    with ZipFile(file_name, 'r') as zipObj:
        zipObj.extractall()


def error_message(msg):
    sys.exit(CRED + msg + CEND)


def get_zips(data_dir: str, output_dir: str, delete_zips=False):
    # A function that will traverse the pairtree directory structure, find the zip files 
    # that contain full text data from HathiTrust, expand them, and move the files to an output directory.
    
    # Returns a new directory with one folder of page text files per volume

    # Parameters
    # ----------
    # data_dir : str, path to folder holding the HathiTrust data to be cleaned/processed.
    
    # output_dir : str, path to new output folder that will hold the cleaned/processed data. Will return error if folder already exists.
    
    # delete_zips : bool, default False, provide value True to delete original zipfiles after expansion, False to keep them.
    
    # Usage
    # -------
    # Find and move zips for HathiTrust dataset, deleting zips after expanded:
    #   data_dir = /Users/rdubnic2/Desktop/data_download
    #   output_dir = /Users/rdubnic2/Desktop/data
        
    #   get_zips(data_dir, output_dir, delete_zips=True)
    
    # Find and move zips for HathiTrust dataset, keeping original zips after expanded:
    #   data_dir = /Users/rdubnic2/Desktop/data_download
    #   output_dir = /Users/rdubnic2/Desktop/data
        
    #   get_zips(data_dir, output_dir, delete_zips=False)
        
    # No variables: find and move zips for HathiTrust dataset, keeping original zips after expanded:
        
    #   get_zips('/Users/rdubnic2/Desktop/data_download', '/Users/rdubnic2/Desktop/data', delete_zips=False)

    data_path = Path(data_dir)
    print(data_dir)
    output_path = Path(output_dir)
    if data_path.exists():  
        if output_path.exists():
            raise Exception(output_dir + ' is already created. please delete it or input a different output directory')
        else:
            try:
                os.mkdir(output_path.parent / output_path.name)

            except OSError:
                raise Exception("Creation of the directory %s failed" % output_dir +
                                "\n* Possible reason there's no \'" + str(output_path.parent) + "\' folder")
            else:
                print("Successfully created the directory \'%s\' " % output_dir)
            cmd = "x"
            for x in glob.glob(data_dir + '/**/*.zip', recursive=True):
                if cmd == 'x':
                    with ZipFile(x, 'r') as zipObj:
                        zipObj.extractall(output_path)
                    # for metadata xml
                    x_data = Path(x)
                    xml_path = x_data.parent / x_data.name.replace('.zip', '.mets.xml')
                    folder_name = x_data.name.replace('.zip', '')
                    if xml_path.exists():
                        shutil.copy(xml_path, output_path / folder_name)
                    else:
                        print("missing xml:" + str(xml_path))
                else:
                    shutil.copy(x, output_dir)

    else:
        raise Exception(data_dir + ' path does not exist. Input a different data directory.')


def rename_file(file_path):
    # clean_tct_file_names invokes this function to rename a file given a str associated with a real file_path 
    fname = file_path.name.split("_")[-1]
    try:
        int(fname.split(".txt")[0])
        file_path_replace = file_path.parent / (
                ''.join([char * (12 - len(str(fname))) for char in '0']) + str(fname))
        os.renames(file_path, file_path_replace)
    except ValueError:
        print("file names must contain underscores between text containing non-numeric characters and numeric characters. i.e., 'scout_001.txt'. Insert underscores to rename the following file:", fname)


def clean_txt_file_names(file: str):
    # Given a path to a single directory holding page text files, this function will normalize 
    # irregular page text file names in HathiTrust data, converting all page text files names 
    # to an 8-digit sequence number in format '00000001.txt' in ascending numerical order based 
    # on original file names. For example:
     
    #     '0000000001.txt' becomes '00000001.txt'
    #     'ark+=13960=t3mw3px6k_00000001.txt' becomes '00000001.txt'
        
    # This function will also normalize jumps in page numbers greater than +1 between files sorted
    # in ascending numerical order. For example, given this file list, names would be normalized to:
    
    #     00000009.txt  becomes  00000009.txt
    #     00000010.txt  becomes  00000010.txt
    #     00000015.txt  becomes  00000011.txt
    #     00000016.txt  becomes  00000012.txt
    
    # Note that file names must contain an underscore between strings containing non-numeric and numeric characters.

    #    For example, 'ark+=13960=t3mw3px6k_00000001.txt' will become '00000001.txt'
    #    But 'ark+=13960=t3mw3px6k00000001.txt' will crash the program. 

    # The function returns nothing explicitly. It simply normalizes file names within the input directory. 

    # Parameters
    # ----------
    # directory_path: str, path to folder holding text files with filenames to be normalized
    
    # prnt: bool, default False, parameter that determines if print messages are returned for each successfully 
    # normalized file.
    
    # Usage
    # -------
    # Normalize file names for one volume's text files in one directory, without print messages:
        
    #   test_directory = '/Users/username/Desktop/data_download/ark+=13960=t3mw3px6k'
    #   normalize_txt_file_names(test_directory)

    # To normalize page file names for multiple volumes held in one top directory, use iteratively:
    
    #   top_dir = ['/Users/rdubnic2/Desktop/data_download/ark+=13960=t3mw3px6k',
    #               '/Users/rdubnic2/Desktop/data_download/ark+=23200=t5mw3px1j',
    #               '/Users/rdubnic2/Desktop/data_download/ark+=53960=t4mp1qr7x']
                    
    #   for folder in top_dir:
    #       normalize_txt_file_names(folder)
    
    
    file_path = Path(file)
    if file_path.exists() and file_path.is_file():
        if '.txt' in str(file_path):
            rename_file(file_path)
        else:
            error_message("Not a txt file\nInvalid txt file: " + str(file_path))
    elif file_path.exists() and file_path.is_dir():
        for x in tqdm(glob.glob(str(file_path) + '/*.txt', recursive=True)):
            x_path = Path(x)
            rename_file(x_path)
    else:
        error_message("Path/File not exists. Path = " + str(file_path))
        


def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

# i suggest we retire this entire function 
def normalize_txt_file_names(dir_path: str, prnt=False):

    # Given a path to a single directory holding page text files, this function will normalize 
    # irregular page text file names in HathiTrust data, converting all page text files names 
    # to an 8-digit sequence number in format '00000001.txt' in ascending numerical order based 
    # on original file names. For example:
     
    #     '0000000001.txt' becomes '00000001.txt'
    #     'ark+=13960=t3mw3px6k_00000001.txt' becomes '00000001.txt'
        
    # This function will also normalize jumps in page numbers greater than +1 between files sorted
    # in ascending numerical order. For example, given this file list, names would be normalized to:
    
    #     00000009.txt  becomes  00000009.txt
    #     00000010.txt  becomes  00000010.txt
    #     00000015.txt  becomes  00000011.txt
    #     00000016.txt  becomes  00000012.txt
    
    # The function returns nothing explicitly, other than normalized file names within the input directory. 

    # Parameters
    # ----------
    # directory_path: str, path to folder holding text files with filenames to be normalized
    
    # prnt: bool, default False, parameter that determines if print messages are returned for each successfully 
    # normalized file.
    
    # Usage
    # -------
    # Normalize file names for one volume's text files in one directory, without print messages:
        
    #   test_directory = '/Users/username/Desktop/data_download/ark+=13960=t3mw3px6k'
    #   normalize_txt_file_names(test_directory)

    # To normalize page file names for multiple volumes held in one top directory, use iteratively:
    
    #   top_dir = ['/Users/rdubnic2/Desktop/data_download/ark+=13960=t3mw3px6k',
    #               '/Users/rdubnic2/Desktop/data_download/ark+=23200=t5mw3px1j',
    #               '/Users/rdubnic2/Desktop/data_download/ark+=53960=t4mp1qr7x']
                    
    #   for folder in top_dir:
    #       normalize_txt_file_names(folder, prnt=True)
    
    
    dir_path = Path(dir_path)
    if dir_path.exists() and dir_path.is_dir():
        orig_file_paths = {}
        clean_txt_file_names(dir_path)
        txt_files = []
        for x in (glob.glob(str(dir_path) + '/*.txt', recursive=True)):
            x_path = Path(x)
            txt_file_name = x_path.name.split(".")[0]
            orig_file_paths[x] = txt_file_name
            # if the file name isnt an int it doesnt work
            if is_integer(txt_file_name):
                txt_files.append(txt_file_name)
            else:
                print("Invalid text file format \nInvalid txt file: " + str(x_path))

        if not txt_files:
            error_message("No txt files found in " + str(dir_or_file_path) +
                          "\nPlease give a directory which have txt files")

        ll = [int(j) for j in txt_files]
        ll = sorted(ll)
        count = ll[0]
        renamed_list = []
        for i in tqdm(ll):
            if count != i:
                # file_path = [path for path, txt in orig_file_paths.items() if int(txt) == int(i)][0]
                file_path = [path for path, txt in orig_file_paths.items()][0]
                print(file_path)
                try:
                    int(file_path)
                    file_path_replace = dir_path / (
                                ''.join([char * (8 - len(str(count))) for char in '0']) + str(count) + ".txt")
                    os.renames(file_path, file_path_replace)
                    renamed_list.append(
                            str(file_path) + CBLINK + " -> " + CEND + CGREEN + str(file_path_replace) + CEND)
                except ValueError: 
                    print(file_path, "file named improperly. please rename.")
            count += 1 
        print("this is the renamed list:", renamed_list)

        if not renamed_list:
            print(f"No normalization is needed")
        elif prnt == True:
            print("Normalized files")
            print("\n".join(renamed_list))

    else:
        error_message(f"Directory {dir_path} does not exist!")


def load_vol(path: str, num_pages: int) -> List[HtrcPage]:
    # A function to load a HathiTrust volume, in the format of a folder of text files, and parse 
    # the page structure in advance of removing running headers and footers. 
    
    # Returns a list of HtrcPage(*) objects (indexed lines of text), ready as input for clean_vol.
    
    # (*) See  https://github.com/htrc/HTRC-Tools-RunningHeaders-Python/blob/develop/htrc/models.py
    
    # Parameters
    # ----------
    # path: str, path to folder of text files for a given HathiTrust volume
    
    # num_pages: int, the number of page text files in the directory for the volume
    
    # Usage
    # -------
    # Load a HathiTrust volume using explicit parameters:
    
    #   load_vol('/Users/rdubnic2/Desktop/data_download/ark+=13960=t3mw3px6k',7)
    
    # Load a HathiTrust volume using variables, generating a list of paths using `glob`:
        
    #   import glob
        
    #   vol_path = '/Users/rdubnic2/Desktop/data_download/ark+=13960=t3mw3px6k'
    #   num_pages = len(glob.glob(str(vol_path)+'/**'))
        
    #   load_vol(vol_path, num_pages)

    pages = []
    py_num_pages = num_pages - 1
    for n in range(py_num_pages):
        if n == 0:
            n = 1
            page_num = str(n).zfill(8)
            with open('{}/{}.txt'.format(path, page_num), encoding='utf-8') as f:
                lines = [line.rstrip() for line in f.readlines()]
                pages.append(HtrcPage(lines))
        else:
            page_num = str(n).zfill(8)
            try:
                with open('{}/{}.txt'.format(path, page_num), encoding='utf-8') as f:
                    lines = [line.rstrip() for line in f.readlines()]
                    pages.append(HtrcPage(lines))
            except FileNotFoundError:
                pass

    return pages


def does_clean(vol_dir_path_list: list, out_dir: str):
    # Function called by clean_vol to parse the page structure of a list of directories containing HathiTrust volumes, 
    # and write out only the page body text,removing running headers and footers.

    vol_num = 0

    assert isinstance(vol_dir_path_list,
                      list), 'clean_vol() 1st parameter vol_dir_path_list="{}" not of <class "list">'.format(
        vol_dir_path_list)
    assert isinstance(out_dir, str), 'clean_vol() 2nd parameter out_dir="{}" not of <class "str">'.format(
        out_dir)

    for vol_dir_path in tqdm(vol_dir_path_list):
        filename = Path(vol_dir_path).name
        filename = str(filename)
        page_paths = sorted(glob.glob(vol_dir_path + '/*.txt'))
        file_count = len(page_paths)
        loaded_vol = load_vol(vol_dir_path, file_count)
        pages = parse_page_structure(loaded_vol)
        outfile = filename + '.txt'
        vol_num += 1

        with open(outfile, 'w') as f:
            clean_file_path = os.getcwd() + "/" + outfile
            for n, page in enumerate(pages):
                f.write(page.body + '\n')
            shutil.move(clean_file_path, out_dir)
    return print(f"Cleaned {vol_num} volume(s)")

def does_clean_one_vol(vol_dir_path: str, out_dir: str):
    # Function called by clean_vol to parse the page structure of one directory containing one volume, 
    # and write out only the page body text,removing running headers and footers.
    # created to satisfy an edge case (sending a list containing one hathitrust vol, ["users/me/htvol"]) 
    # causing the program to crash

    assert isinstance(out_dir, str), 'clean_vol() 2nd parameter out_dir="{}" not of <class "str">'.format(
        out_dir)

    filename = Path(vol_dir_path).name
    filename = str(filename)
    page_paths = sorted(glob.glob(str(vol_dir_path) + '/*.txt'))
    file_count = len(page_paths)
    loaded_vol = load_vol(vol_dir_path, file_count)
    pages = parse_page_structure(loaded_vol)
    outfile = filename + '.txt'
    
    with open(outfile, 'w') as f:
        clean_file_path = os.getcwd() + "/" + outfile
        for n, page in enumerate(pages):
            f.write(page.body + '\n')
        shutil.move(clean_file_path, out_dir)
    return print(f"Cleaned 1 volume(s)")

def clean_vol(vol_dir_path: str or list, clean_dir_path: str):
    # Function to parse the page structure of every HathiTrust volume in a supplied directory and write out only the
    # page body text, removing running headers and footers. 
    
    # Returns nothing explicitly, but yields a single concatenated text file made up of input pages with 
    # running headers and footers removed, located in out_dir.
    
    # Parameters
    # ----------
    # vol_dir_path: either a list containing universal paths to directories containing HathiTrust page text
    # files or the parent directory containing those universal paths to HathiTrust volumes. 
    
    # clean_dir_path: str, path to folder to contain cleaned, concatenated text files.
    
    # Usage
    # -------
    # Use clean_vol to concatenate the pages and remove headers and footers of every hathitrust volume in a directory 
    # or a list of the paths to those volumes. The concatenated, cleaned files are then saved to another directory, clean_dir_path.

    #   vol_dir_path = ['/Users/rdubnic2/Desktop/data_download/ark+=13960=t3mw3px6k',
    #               '/Users/rdubnic2/Desktop/data_download/ark+=23200=t5mw3px1jk',
    #               '/Users/rdubnic2/Desktop/data_download/ark+=53960=t4mp1qr7x']
    #   clean_dir_path = '/Users/rdubnic2/Desktop/final_vols/'
                    
    #   clean_vol(vol_dir_path, clean_dir_path)
        
    #   > Cleaned 3 volume(s)

    # OR

    #   vol_dir_path = '/Users/rdubnic2/Desktop/data_download/'
    #   clean_dir_path = '/Users/rdubnic2/Desktop/final_vols/'
                    
    #   clean_vol(vol_dir_path, clean_dir_path)
        
    #   > Cleaned 3 volume(s)

    subdirs = []
    try:
        vol_dir_path = Path(vol_dir_path)
        if vol_dir_path.exists() and vol_dir_path.is_dir():
            subdirs = []
            for subdir in os.listdir(vol_dir_path): 
                subdirs.append(str(vol_dir_path) + "/" + str(subdir))
            if ".txt" in str(subdirs):
                does_clean_one_vol(vol_dir_path, clean_dir_path)
            else:
                does_clean(subdirs, clean_dir_path)
        else:
             error_message("Path/File not exists. Path = " + str(vol_dir_path))

    except TypeError:
        if type(vol_dir_path) == list: 
             does_clean(vol_dir_path, clean_dir_path)
        else:
            does_clean([vol_dir_path], clean_dir_path)
  

def check_list_of_vols(vol_dir_path_list: list, clean_dir_path: str):
    # called by check_vols to check if a list of subdirectories containing hathitrust volumes have been cleaned by clean_vol.
    
    assert isinstance(vol_dir_path_list,
                      list), 'clean_vol() 1st parameter vol_dir_path_list="{}" not of <class "list">'.format(
        vol_dir_path_list)
    assert isinstance(clean_dir_path, str), 'clean_vol() 2nd parameter out_dir="{}" not of <class "str">'.format(
        clean_dir_path)
    print(f"There are {len(vol_dir_path_list)} total volumes.")
    clean_volume_list = glob.glob(clean_dir_path + '/*.txt')
    list_clean_files = []
    for file in clean_volume_list:
        p = Path(file)
        list_clean_files.append(p.name)
    count = 0
    need_to_clean = []
    for path in vol_dir_path_list:
        p = Path(path)
        ps = (p.name + ".txt")
        if ps not in list_clean_files:
            need_to_clean.append(str(p))
        else:
            count += 1

    print(f"{count} volumes have already been cleaned.")

    if need_to_clean:
        print("Following Directories need to be cleaned")
        print(CRED + "\n".join(need_to_clean) + CEND)

    return need_to_clean




def check_vol(vol_dir_path: list or str, clean_dir_path: str):
    # Function to identify which volumes in a given parent directory or list of subdirectories have already been 
    # processed by clean_vol. Helpful for very large worksets where processing may be interrupted/stopped. 
    # This function will return a list of volume paths that can be used to incrementally resume volume processing.
    
    # Returns a list of volume directory paths that still require processing.
    
    # Parameters
    # ----------
    # vol_dir_path: either a list containing universal paths to directories enclosing HathiTrust page text
    # files OR a str representing a parent directory containig subdirectories of HathiTrust volumes. 
    
    # clean_dir_path: str, path to folder containing cleaned, concatenated text files.
    
    # Usage
    # -------
    # Return a list of paths to volumes that have not yet been processed by clean_vol:
    # Prints reports of how many total volumes exist and how many need to be cleaned
    
    #   data_dir = ['/Users/rdubnic2/Desktop/data_download/ark+=13960=t3mw3px6k',
    #                       '/Users/rdubnic2/Desktop/data_download/ark+=23200=t5mw3px6k',
    #                       '/Users/rdubnic2/Desktop/data_download/ark+=53960=t4mp1qr7x']
        
    #   out_dir = '/Users/rdubnic2/Desktop/clean_volumes/'      
    #   check_vol(data_dir, out_dir)
    #   > ['/Users/rdubnic2/Desktop/data_download/ark+=53960=t4mp1qr7x']

    #   OR

    #   data_dir = "/Users/rdubnic2/Desktop/data_download"
    #   out_dir = '/Users/rdubnic2/Desktop/clean_volumes/'      
    #   check_vol(data_dir, out_dir)
    #   > ['/Users/rdubnic2/Desktop/data_download/ark+=53960=t4mp1qr7x']
        
    # Use check_vol as part of removing running headers/footers process:
        
    #   data_dir = "/Users/rdubnic2/Desktop/data_download"
    #   out_dir = '/Users/rdubnic2/Desktop/clean_volumes/'
    #   to_be_cleaned = check_vol(data_dir, out_dir)
    #   clean_vol(to_be_cleaned, out_dir)

    subdirs = []
    try:
        vol_dir_path = Path(vol_dir_path)
        if vol_dir_path.exists() and vol_dir_path.is_dir():
            subdirs = os.listdir(vol_dir_path)
            if ".txt" in str(subdirs):
                check_list_of_vols([vol_dir_path], clean_dir_path)
            else:
                check_list_of_vols(subdirs, clean_dir_path)
        else:
             error_message("Path/File not exists. Path = " + str(vol_dir_path))

    except TypeError:
        print(vol_dir_path) 
        if type(vol_dir_path) == list: 
             check_list_of_vols(vol_dir_path, clean_dir_path)
        else:
            check_list_of_vols([vol_dir_path], clean_dir_path)
  


