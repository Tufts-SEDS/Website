"""
A simple static file minifier for Django projects

Using jsmin (python package) and toptal (an api), the file size for
static css and javascript files can be reduced, which optimizes 
the overall site performance in production. This module should be ran whenever 
there is a change made to any of the css or js files which are ready to be pushed
to production.

For more information on the tools used for this, read the following:
https://www.toptal.com/developers/cssminifier/documentation 
https://github.com/tikitu/jsmin/
"""

import glob
import requests
import os
from pathlib import Path
from jsmin import jsmin


BASE_DIR = Path(__file__).resolve().parent
CSS_DIR = os.path.join(BASE_DIR, 'tuftsseds\\static\\css')
JS_DIRS = [os.path.join(BASE_DIR, 'tuftsseds\\static\\js'), os.path.join(BASE_DIR, 'tuftsseds\\static\\vendors')]

# Files that should not be minified
css_files_to_exclude = [] 
js_files_to_exclude = ["apolo.core.js", "apolo.init.js",]
          
def list_files(directory, ignored_subdirectories, ignored_files):
    # Recursively find all files in the directory and its subdirectories
    filepaths = glob.glob(os.path.join(directory, '**'), recursive=True)
    
    for filepath in filepaths:
        
        # Skip directories
        if os.path.isdir(filepath):
            continue
        
        # Get the filename
        filename = os.path.basename(filepath)
        
        if "min" in filename:
            ignored_files.append(filename)
        
        # Check if the file is in any ignored subdirectories
        if ignored_subdirectories is not None:
                if any(sub_dir in filepath for sub_dir in ignored_subdirectories):
                    ignored_files.append(filename)
                    
def write_minified_js_files(directory, ignored_subdirectories, ignored_files):
    filepaths = glob.glob(os.path.join(directory, '**'), recursive=True)
    
    for filepath in filepaths:
        if os.path.isdir(filepath):
            continue
        
        filename = os.path.basename(filepath)
        
        if ignored_subdirectories is not None:
                if any(sub_dir in filepath for sub_dir in ignored_subdirectories):
                    continue
        
        if filename not in ignored_files:
            with open(filepath) as js_file:
                minified = jsmin(js_file.read())
                
            base_name, extension = os.path.splitext(filename)
            new_filename = base_name + ".min" + extension
            new_file_path = os.path.join(os.path.dirname(filepath), new_filename)
            
            with open(new_file_path, 'w') as minified_file:
                minified_file.write(minified)
                
                
def write_minified_css_files(directory, ignored_subdirectories, ignored_files):
    filepaths = glob.glob(os.path.join(directory, '**'), recursive=True)
    
    for filepath in filepaths:
        if os.path.isdir(filepath):
            continue
        
        filename = os.path.basename(filepath)
        
        if ignored_subdirectories is not None:
                if any(sub_dir in filepath for sub_dir in ignored_subdirectories):
                    continue
        
        if filename not in ignored_files:
            with open(filepath) as css_file:
                minified = requests.post('https://www.toptal.com/developers/cssminifier/api/raw', data=dict(input=css_file.read())).text
                
            base_name, extension = os.path.splitext(filename)
            new_filename = base_name + ".min" + extension
            new_file_path = os.path.join(os.path.dirname(filepath), new_filename)
            
            with open(new_file_path, 'w') as minified_file:
                minified_file.write(minified)


# Handling CSS files
list_files(CSS_DIR, None, css_files_to_exclude)
# Handling JS files (non-vendor/wordpress type shit, custom apolo stuff)
list_files(JS_DIRS[0], None, js_files_to_exclude)
# Handling more JS files (vendor/wordpress shit)
list_files(JS_DIRS[1], ["arcticmodal", "owl-carousel", "revolution", "swiper"], js_files_to_exclude)

write_minified_css_files(CSS_DIR, None, css_files_to_exclude)
write_minified_js_files(JS_DIRS[0], None, js_files_to_exclude)
write_minified_js_files(JS_DIRS[1], ["arcticmodal", "owl-carousel", "revolution", "swiper"], js_files_to_exclude)
