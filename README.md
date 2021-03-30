<p align="center">
<a href="https://www.hathitrust.org/htrc"><img src="https://wiki.htrc.illinois.edu/download/attachments/1769480/logo_googleForm.png?version=1&modificationDate=1584514252000&api=v2" width="600" title="HathiTrust Reseach Center" alt="HTRC"></a>
</p>

# ht_text_prep

## Table of Contents
1. [About ht_text_prep Library](#about)
2. [Installation](#install)
3. [Usage](#usage)


## About `ht_text_prep` Library<a name="about"></a>
Python library to assist in processing HathiTrust full-text data outside of HathiTrust Research Center environments. This library helps manage the data that is stored and arrives in [pairtree](https://confluence.ucop.edu/display/Curation/PairTree) format.

This library also has tools for finding and removing running headers and footers in a given volume, removing them, and concatenating page-level text files into a single text file per HathiTrust volume.

## Installation <a name="install"></a>

To install,
```bash
pip install ht_text_prep
```
That's it! This library is written for Python 3.6+. For Python beginners, you'll need [pip](https://pip.pypa.io/en/stable/installing/).
  

## Usage <a name="usage"></a>

### Import the library for use:
    	
```python
import ht_text_prep as htp
```

### Function: `get_zips(data_dir: str, output_dir: str, delete_zips=False)` 

A function that will traverse the pairtree directory structure, find the zip files that contain full text data from HathiTrust, expand them, and move the files to an output directory.

Returns a new directory with one folder of page text files per volume

#### Inputs:

`data_dir`: path to folder holding the HathiTrust data to be cleaned/processed.

`output_dir`: path to new output folder that will hold the cleaned/processed data. Will return error if folder already exists.

`delete_zips`: default False, provide value True to delete original zipfiles after expansion, False to keep them.

#### Examples:
   		
* Find and move zips for HathiTrust dataset, deleting zips after expanded:
	
```python
import ht_text_prep as htp

data_dir = '/Users/rdubnic2/Desktop/data_download'
output_dir = '/Users/rdubnic2/Desktop/data'

htp.get_zips(data_dir, output_dir, delete_zips=True)
```
	
* Find and move zips for HathiTrust dataset, keeping original zips after expanded:
	
```python
data_dir = '/Users/rdubnic2/Desktop/data_download'
output_dir = '/Users/rdubnic2/Desktop/data'

htp.get_zips(data_dir, output_dir, delete_zips=False)
```

* Using paths rather than variables, find and move zips for HathiTrust dataset, keeping original zips after expanded:
	
```python 
htp.get_zips('/Users/rdubnic2/Desktop/data_download', '/Users/rdubnic2/Desktop/data', delete_zips=False)
```

### Function: `normalize_txt_file_names(directory_path: str, prnt=False)`

Given an input path to a single directory holding page text files, this function will normalize irregular page text file names in HathiTrust data, converting all page text files names to an 8-digit sequence number in format '00000001.txt' in ascending numerical order based on original file names. For example:

	`0000000001.txt` becomes `00000001.txt`

	`ark+=13960=t3mw3px6k_00000001.txt` becomes `00000001.txt`
        
This function will also normalize jumps in page numbers greater than +1 between files sorted in ascending numerical order. For example, given this file list, names would be normalized to:
    
	`00000009.txt`  becomes  `00000009.txt`

	`00000010.txt`  becomes  `00000010.txt`
	
	`00000015.txt`  becomes  `00000011.txt`

	`00000016.txt`  becomes  `00000012.txt`

	
The function returns nothing explicitly, but yields normalized file names within the input directory.
    
#### Inputs:
   	
`directory_path`: path to folder holding text files with filenames to be normalized
    
`prnt`: parameter that determines if print messages are returned for each successfully normalized file. By default, this value is `False`.

#### Examples:
	
* Normalize file names for one volume's text files in one directory, without print messages:
    	
```python 
import ht_text_prep as htp
test_directory = '/Users/username/Desktop/data_download/ark+=13960=t3mw3px6k'
htp.normalize_txt_file_names(test_directory)
```

* To normalize page file names for multiple volumes held in one top directory, use iteratively:
    	
```python
top_dir = ['/Users/rdubnic2/Desktop/data_download/ark+=13960=t3mw3px6k',
	'/Users/rdubnic2/Desktop/data_download/ark+=23200=t5mw3px1j',
	'/Users/rdubnic2/Desktop/data_download/ark+=53960=t4mp1qr7x']
				
for folder in top_dir:
	htp.normalize_txt_file_names(folder, prnt=True)
```
    
### Function: `load_vol(path: str, num_pages: int)`

A function to load a HathiTrust volume, in the format of a folder of text files, and parse the page structure in advance of removing running headers and footers. 

Returns a list of HtrcPage(*) objects (indexed lines of text), ready as input for clean_vol.

(*) See https://github.com/htrc/HTRC-Tools-RunningHeaders-Python/blob/develop/htrc/models.py
	
#### Inputs:

`path`: path to folder of text files for a given HathiTrust volume

`num_pages`: the number of page text files in the directory for the volume

#### Examples:

* Load a HathiTrust volume using explicit parameters:
	
```python
import ht_text_prep as htp

htp.load_vol('/Users/rdubnic2/Desktop/data_download/ark+=13960=t3mw3px6k', 7)
```

* Load a HathiTrust volume using variables, generating a list of paths using `glob`:

```python
import glob

vol_path = '/Users/rdubnic2/Desktop/data_download/ark+=13960=t3mw3px6k'
num_pages = len(glob.glob(str(vol_path)+'/**'))

htp.load_vol(vol_path, num_pages)
```  	

### Function: `check_vol(vol_dir_path_list: list, clean_dir_path: str)`
	
Function to check an input directory to identify which volumes have already been processed by clean_vol. 
Intended as a helpful for very large worksets, where processing may be interrupted/stopped. This function
will return a list of volume paths that can be used to incrementally resume volume processing.

Returns a list of volume directory paths that still require processing.

#### Inputs:

`vol_dir_path_list`: a list containing universal paths to directories containing HathiTrust page text
files.

`out_dir`: path to folder containing cleaned, concatenated text files.

#### Examples:

* Return a list of paths to volumes that have not yet been processed by `clean_vol()`:
	
```python
import ht_text_prep as htp

data_dir = ['/Users/rdubnic2/Desktop/data_download/ark+=13960=t3mw3px6k',
	'/Users/rdubnic2/Desktop/data_download/ark+=23200=t5mw3px6k',
	'/Users/rdubnic2/Desktop/data_download/ark+=53960=t4mp1qr7x']

out_dir = '/Users/rdubnic2/Desktop/clean_volumes/'
			
htp.check_vol(data_dir, out_dir)

> ['/Users/rdubnic2/Desktop/data_download/ark+=53960=t4mp1qr7x']
```
	
* Use `check_vol()` as part of removing running headers/footers workflow, with `clean_vol()`:
	
```python
data_dir = ['/Users/rdubnic2/Desktop/data_download/ark+=13960=t3mw3px6k',
	'/Users/rdubnic2/Desktop/data_download/ark+=23200=t5mw3px6k',
	'/Users/rdubnic2/Desktop/data_download/ark+=53960=t4mp1qr7x']

out_dir = '/Users/rdubnic2/Desktop/clean_volumes/'
			
to_be_cleaned = htp.check_vol(data_dir, out_dir)

htp.clean_vol(to_be_cleaned, out_dir)
```

### Function: `clean_vol(vol_dir_path_list: list, out_dir: str)`:

Function to parse the page structure of a HathiTrust volume, and write out only the page body text, removing running headers and footers.

Returns nothing explicitly, but yields a single concatenated text file made up of input pages with running headers and footers removed, located in out_dir.

#### Inputs:

`vol_dir_path_list`: a list containing universal paths to directories containing HathiTrust page text
files.

`out_dir`: path to folder to contain cleaned, concatenated text files.

#### Examples:

* Remove running headers/footers for a directory containing sub-directories holding page text:
	
```python
import ht_text_prep as htp

vol_dir = ['/Users/rdubnic2/Desktop/data_download/ark+=13960=t3mw3px6k',
	'/Users/rdubnic2/Desktop/data_download/ark+=23200=t5mw3px1jk',
	'/Users/rdubnic2/Desktop/data_download/ark+=53960=t4mp1qr7x']

out_dir = '/Users/rdubnic2/Desktop/final_vols/'
			
htp.clean_vol(vol_dir, out_dir)

> 'Cleaned 3 volume(s)'
```

**Questions?** Contact htrc-help@hathitrust.org
