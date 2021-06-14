from typing import Tuple, List

from file_system.file import Directory, File, AbstractFile
from file_system.utils import is_directory, is_file, join_path, parse_path, get_valid_name_before_adding_to_dir
from file_system.error import PathComponentNotFoundException, InvalidOperationException, InvalidPathComponentException

class FileSystem:

    def __init__(self) -> None:
        self._root: Directory = Directory('', None) # root dir has empty string as name
        self._current_dir: Directory = self._root
    
    def change_dir(self, path: str) -> None:
        maybe_dir = self._get_file_object_from_path(path)
        
        if not is_directory(maybe_dir):
            raise InvalidPathComponentException('Path does not point to a directory')

        self._current_dir = maybe_dir
    
    def remove(self, path: str) -> None:
        file = self._get_file_object_from_path(path)
        self._remove_file(file)

    def move(self, from_path: str, to_path: str) -> None:
        from_file = self._get_file_object_from_path(from_path)
        to_pure_path, to_file_name = self._get_target_path_and_file_name_for_move(from_file, to_path)
        
        to_parent_dir = self._get_file_object_from_path_and_auto_create_dir(to_pure_path)
        
        if not is_directory(to_parent_dir):
            raise InvalidPathComponentException('Move target is not directory')
        
        self.remove(from_path)
        from_file.set_name_in_file_metadata_only(to_file_name)
        to_parent_dir.add_file(from_file)
    
    """
        Support both single file and directory.
        Will auto rename if duplicate name is encountered
    """
    def copy(self, from_path: str, to_path: str) -> None:
        source_file = self._get_file_object_from_path(from_path)
        to_pure_path, to_file_name = self._get_target_path_and_file_name_for_move(source_file, to_path)
           
        to_parent_dir = self._get_file_object_from_path_and_auto_create_dir(to_pure_path)
        
        queue = [(source_file, to_parent_dir)]
        is_top_level = True
        while queue:
            to_be_copied, target_parent_dir = queue.pop(0)

            file_copy = self._copy_single_file(
                to_be_copied, 
                target_parent_dir, 
                
                # always use the source_file name unless this is the root file of the copy
                to_file_name if is_top_level else to_be_copied.get_name(),
            )
            is_top_level = False
                
            if is_directory(to_be_copied):
                children = to_be_copied.get_all_children()
                for child in children:
                    queue.append((child, file_copy))
       
    def make_new_dir(self, path: str) -> None:
        self._get_file_object_from_path_and_auto_create_dir(path)
    
    def make_new_file(self, path: str) -> None:
        pure_path, file_name = parse_path(path)
        
        parent_dir = self._get_file_object_from_path_and_auto_create_dir(
            pure_path,
        )

        new_dir = File(file_name, parent_dir)
        parent_dir.add_file(new_dir)
    
    def ls(self) -> List[str]:
        return [file.get_name() + ('/' if is_directory(file) else '') for file in self._current_dir.get_all_children()]
    
    def get_current_path(self) -> str:
        path_list = []
        cur_file = self._current_dir
        while cur_file._parent != cur_file:
            path_list.append(cur_file.get_name())
            cur_file = cur_file._parent
        
        path_list.reverse()
        
        return '/' + '/'.join(path_list)

    def find(self, name: str) -> List[str]:
        stack = [(None, self._current_dir)]
        result = []
        
        while stack:
            this_path, this_dir = stack.pop()
            
            if this_dir.get_name() == name:
                result.append(join_path(this_path, this_dir.get_name()))
            
            if is_directory(this_dir):
                children = this_dir.get_all_children()
                next_path = '.' if this_path is None else join_path(this_path, this_dir.get_name())
                
                for child in children:
                    stack.append((next_path, child))
        
        return result
        
    def write(self, path: str, content: str, append=False) -> None:
        file = self._get_file_object_from_path(path)
        
        if not is_file(file):
            raise InvalidPathComponentException('Invalid File')
        
        file.write(content, append)


    def cat(self, path: str) -> str:
        file = self._get_file_object_from_path(path)
        
        if not is_file(file):
            raise InvalidPathComponentException('Invalid File')
        
        return file.read()
 
    def _get_file_object_from_path_and_auto_create_dir(self, path: str) -> AbstractFile:
        return self._get_file_object_from_path(
            path, 
            True, # automatically create directory is not exist
        )

    """
        Given a path, returns the file that path represents. Works for both directories and actual files
        auto_create_dir: automatically create directories if not exist
    """
    def _get_file_object_from_path(self, path: str, auto_create_dir=False) -> AbstractFile:
        if not path:
            raise InvalidPathComponentException('Invalid path')

        path_components = path.split('/')
        current_dir = self._current_dir

        # absolute path
        if path[0] == '/':
            current_dir = self._root
            
            # cd /
            if len(path) == 1:
                return current_dir
        
            path = path[1:]
            
        path_components = path.split('/')
        
        for idx, comp in enumerate(path_components):
            if comp == '.':
                continue
            elif comp == '..':
                current_dir = current_dir.get_parent()
                continue
            elif not comp: # skip empty entries. we allow /a////b/
                continue
            
            if not current_dir.has_child(comp):
                if auto_create_dir:
                    current_dir.add_file(Directory(comp, current_dir))
                else:
                    raise PathComponentNotFoundException(comp + 'not found in ' + current_dir.get_name())

            child = current_dir.get_child(comp)

            # only last component in the chain is allowed to be a file
            if idx != len(path_components) - 1 and is_file(child):
                raise InvalidPathComponentException(comp, 'is not a directory')
            
            current_dir = child
        return current_dir
     
    def _copy_single_file(self, source_file: File, target_dir: Directory, to_file_name: str) -> Directory:
        maybe_new_file_name = get_valid_name_before_adding_to_dir(to_file_name, target_dir)
        
        if is_file(source_file):
            copied_file = File(maybe_new_file_name, target_dir)
            copied_file.write(source_file.read())
        else:
            copied_file = Directory(maybe_new_file_name, target_dir)

        target_dir.add_file(copied_file)
        
        return copied_file
    
    def _remove_file(self, file: File) -> None:
        if is_directory(file) and file.is_root():
            raise InvalidOperationException('You can not remove root directory')

        file.get_parent().remove_file(file)
    
    """
      decide path/file_name for move or copy
      /a/b if b exists as a directory, then path is /a/b/, file_name is same as source
      /a/b if b does not exist, then path is /a/, file_name is b
    """
    def _get_target_path_and_file_name_for_move(self, source_file: AbstractFile, to_path: str) -> str:
        to_pure_path, to_file_name = parse_path(to_path)
            
        to_file_name = source_file.get_name() if to_file_name is None else to_file_name

        # if to_path is 'path/dir' and dir exists and is a directory then we keep the original name  
        # but if to_path is 'path/file' and file does not exist and is not a directory, then we treat 'file' as the new file name
        try: 
            maybe_target_dir_file = self._get_file_object_from_path(to_path)
            if is_directory(maybe_target_dir_file):
                to_file_name = source_file.get_name()
                
                return (to_path, to_file_name)

        except PathComponentNotFoundException: 
            pass
         
        return (to_pure_path, to_file_name)
        