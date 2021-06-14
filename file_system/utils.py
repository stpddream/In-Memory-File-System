from typing import Tuple

from file_system.file import AbstractFile, Directory, File

import file_system.constant as constant

def is_directory(file: AbstractFile) -> bool:
    return type(file) == Directory

def is_file(file: AbstractFile) -> bool:
    return type(file) == File

def join_path(path1: str, path2: str) -> str:
    return path1 + '/' + path2
    

RESERVED_FILE_NAMES = ['.', '..']

"""
  parse a complete path into /path/to/file/ and file_name
  (path, None) will be returned if path leads to a directory
"""
def parse_path(path: str) -> Tuple[str, str]:
    if path == '.' or path == '..':
        return (path, None)

    path_without_file_name = []
    # absolute path
    if path.startswith('/'):
        path_without_file_name.append('/')

    path_components = path.split('/')
    
    if path_components[-1] == '' or path_components[-1] in RESERVED_FILE_NAMES:
        # treated as part of the pure path
        file_name = None
    else: 
        file_name = path_components[-1]
        path_components = path_components[:-1]
    
    path_without_file_name.append('/'.join(filter(None, path_components)))
    path_str = ''.join(path_without_file_name)
    path_str = '.' if path_str == '' else path_str
    
    return (path_str, file_name)


"""
  auto handle naming collision by adding a auto incremented count at the end
  'file_name_1', 'file_name_2' etc
"""
def get_valid_name_before_adding_to_dir(name: str, target_dir: Directory) -> str:
    if not target_dir.has_child(name):
        return name
    
    count = 1
    format_str = name + '_{}'
    while count < constant.FILE_NAME_AUTO_INC_MAX:
        new_name = format_str.format(count)
        if not target_dir.has_child(new_name):
            return new_name
        
        count += 1
    
    raise Exception('Naming collision handling exceeded our limit, rejecting')
    

    
