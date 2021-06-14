from file_system.error import InvalidPathComponentException, PathComponentNotFoundException
from file_system.file_system import FileSystem


class FileSystemView:
    
    def __init__(self) -> None:
        self._fs = FileSystem()
    
    
    def change_dir(self, path: str) -> None:
        try: 
            self._fs.change_dir(path)
        except InvalidPathComponentException as e:
            print('Error: ', str(e))
    
    def remove(self, path: str) -> None:
        self._fs.remove(path)
    
    def move(self, from_path: str, to_path: str) -> None:
        try:
            self._fs.move(from_path, to_path)
        except InvalidPathComponentException as e:
            print(str(e))
    
    def copy(self, from_path: str, to_path: str) -> None:
        try:
            self._fs.copy(from_path, to_path)
        except InvalidPathComponentException as e:
            print(str(e))
    
    def make_new_dir(self, path: str) -> None:
        try:
            self._fs.make_new_dir(path)
        except PathComponentNotFoundException as e:
            print('Error ', str(e))

    def make_new_file(self, path: str) -> None:
        try:
            self._fs.make_new_file(path)
        except PathComponentNotFoundException as e:
            print('Error ', str(e))

    def ls(self) -> None:
        print('\t'.join(self._fs.ls()))
    
    def get_current_path(self) -> str:
        print(self._fs.get_current_path())
        
    def find(self, name: str) -> None:
        result = self._fs.find(name)

        if result:
            print('\n'.join(result))
        else:
            print('Not found')

    def write(self, path: str, content: str, append=False) -> None:
        try:
            self._fs.write(path, content, append)
        except PathComponentNotFoundException as e:
            print('Error ', str(e))

    def cat(self, path: str) -> None:
        try:
            self._fs.cat(path)
        except PathComponentNotFoundException as e:
            print('Error ', str(e))

        
