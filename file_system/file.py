from typing import Optional, List, Dict

class AbstractFile:
    def __init__(self, name: str, parent: Optional['AbstractFile']) -> None:
      self._name: str = name
      self._parent: 'AbstractFile' = parent
      
      # parent of root is itself
      if parent is None:
          self._parent = self
    
    def get_name(self) -> str:
        return self._name
    
    def get_parent(self) -> 'AbstractFile':
        return self._parent
    
    # note that this is not equivalent to renaming a file
    # to rename a file, the node in parent children tree also needs to be renamed
    def set_name_in_file_metadata_only(self, name: str) -> None:
        self._name = name


class File(AbstractFile):
    def __init__(self, name, parent):
        super().__init__(name, parent)

        self.content: str = ''
    
    def write(self, content: str, append=False) -> None:
        if append:
            self.content += content
        
        else:
            self.content = content
    
    def read(self) -> str:
        return self.content


class Directory(AbstractFile):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        
        self.children: Dict[str, AbstractFile] = {}
    
    def add_file(self, file: AbstractFile) -> None:
        self.children[file.get_name()] = file
    
    def remove_file(self, file: AbstractFile) -> None:
        self.children.pop(file.get_name())
    
    def has_child(self, name: str) -> bool:
        return name in self.children.keys()
    
    def get_child(self, name: str) -> AbstractFile:
        return self.children[name]
    
    def get_all_children(self) -> List[AbstractFile]:
        return list(self.children.values())
    
    def is_root(self) -> bool:
        return self._parent == self
    

