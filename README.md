<p align="center">
<a href="https://www.hathitrust.org/htrc"><img src="https://www.hathitrust.org/files/HTRC_logo.jpg" width="200" title="HathiTrust Reseach Center" alt="HTRC"></a>
</p>

# ht_text_prep
Python library for processing HathiTrust full-text data, which arrives via rsync in [pairtree](https://confluence.ucop.edu/display/Curation/PairTree) format.

## Table of Contents
1. [About ht_text_prep Library](#about)
2. [Installation](#install)
3. [Usage](#usage)


## About `ht_text_prep` Library<a name="about"></a>
Detailed Description goes here.

## Installation <a name="install"></a>

To install,
```bash
pip install ht_text_prep
```
That's it! This library is written for Python 3.6+. For Python beginners, you'll need [pip](https://pip.pypa.io/en/stable/installing/).
  

## Usage <a name="usage"></a>

* Function: `get_zips()` 

    A function that finds the zip files at the end of the pairtree, moves them to a new folder and expands them, removing the zips.
    
    Inputs:
    
    1. Path (string) to directory that holds the pairtree.
    2. Path (string) to directory that will hold the folders from expanded zips.


    ```python
    import ht_text_prep as htp
    htp.get_zips('<path to pairtree parent/s>', 'path to output directory')
    ```
* Function: `normalize_txt_file_names()`

    A function that clean and normalizes page file names.
    
    Example: turns `39002088672754_000001.txt` into `00000001.txt`


    ```python
    import ht_text_prep as htp
    htp.normalize_txt_file_names('txt path or dir to txts') 
    ```

* Function: `check_vol()`
    
    Inputs: 
    
    1. Page directory List
    2. Cleaned vols output dir
    
    Output 
    
    1. Page directory list which is not cleaned yet
        
    ```python
    import ht_text_prep as htp
  page_directory_list = htp.check_vol(page_directory_list, clean_vol_out_dir)
    ``` 

* Function: `clean_vol()`

    Inputs:
    
    1. List of paths (strings) to directories that holds page files, one per volume
    2. Path (string) to output directory where clean single text files will be stored after cleaning and concatenating pages together
    
    Output 
    
    1. text files, one for each volume, with running headers/footers removed and pages concatenated
    
    ```python
    import ht_text_prep as htp
    htp.clean_vol(page_directory_list, clean_vol_out_dir)
    ```
**Questions?** Contact htrc-help@hathitrust.org
