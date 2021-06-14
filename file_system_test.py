import unittest

from file_system.file_system import FileSystem
from file_system.file import Directory
from file_system.utils import parse_path, is_directory, is_file
import file_system.error as error

class FileSystemTest(unittest.TestCase):
    
    def test_file_or_dir_creation(self) -> None:
        fs = FileSystem()
        fs.make_new_dir('1')
        fs.make_new_file('2')
        fs.make_new_file('3')
        fs.make_new_file('4')
        fs.make_new_dir('5')
        
        root_dir = fs._root
        self.assertEqual(len(root_dir.get_all_children()), 5)
        
        fs.make_new_dir('1/1.1')
        fs.make_new_dir('1/1.2')
        
        dir_1 = root_dir.get_child('1')
        self.assertEqual(len(dir_1.get_all_children()), 2)
        
        # absolute path
        fs.make_new_dir('/1/1.1/1.1.1')
        self.assertEqual(len(dir_1.get_child('1.1').get_all_children()), 1)
        
        # .
        fs.make_new_dir('./new_dir')
        self.assertEqual(len(root_dir.get_all_children()), 6)

        # ..
        fs.make_new_dir('1/../new_dir_2')
        self.assertEqual(len(root_dir.get_all_children()), 7)
    
    def test_change_dir(self) -> None:
        fs = self._create_test_data()
        
        # invalid, remains root directory
        with self.assertRaises(
            error.InvalidPathComponentException
        ): 
            fs.change_dir('2')
        self.assertEqual(fs._current_dir.get_name(), '')
        
        fs.change_dir('1')
        self.assertEqual(fs._current_dir.get_name(), '1')
        
        # absolute path
        fs.change_dir('/1/1.1')
        self.assertEqual(fs._current_dir.get_name(), '1.1')

        # consecutive ///
        fs.change_dir('/1///1.1//')
        self.assertEqual(fs._current_dir.get_name(), '1.1')

        # .. 
        fs.change_dir('../..')
        self.assertEqual(fs._current_dir.get_name(), '')
    
    def test_remove(self) -> None:
        fs = self._create_test_data()
        
        # remove file
        fs.change_dir('1/1.1')
        self.assertEqual(len(fs._current_dir.get_all_children()), 3)
        fs.remove('file2')
        self.assertEqual(len(fs._current_dir.get_all_children()), 2)
        
        # remove dir
        fs.change_dir('/')
        fs.remove('1')
        self.assertEqual(len(fs._current_dir.get_all_children()), 4)
    
    def test_write_file(self) -> None:
        fs = self._create_test_data()
        
        fs.write('1/1.1/file1', 'abcde')
        file = fs._get_file_object_from_path('1/1.1/file1')
        self.assertEqual(file.read(), 'abcde')

        fs.write('1/1.1/file1', '12345')
        self.assertEqual(file.read(), '12345')

        fs.write('1/1.1/file1', 'abcde', True) # append mode
        self.assertEqual(file.read(), '12345abcde')
    
    """
        parse_path returns a tuple of the pure_path part of a path 
        and the file_name part of the path
    """
    def test_path_parsing(self) -> None:
        self.assertEqual(parse_path('/'), ('/', None))
        self.assertEqual(parse_path('/a'), ('/', 'a'))
        self.assertEqual(parse_path('/a/b'), ('/a', 'b'))
        self.assertEqual(parse_path('/a/b/'), ('/a/b', None))
        self.assertEqual(parse_path('a'), ('.', 'a'))
        self.assertEqual(parse_path('a/b'), ('a', 'b'))
        self.assertEqual(parse_path('a/b/'), ('a/b', None))
        self.assertEqual(parse_path('.'), ('.', None))
        self.assertEqual(parse_path('..'), ('..', None))
        self.assertEqual(parse_path('a/b/..'), ('a/b/..', None))
    
    def test_get_file_object_by_path(self) -> None:
        fs = self._create_test_data()
        
        root_dir = fs._root
        self.assertEqual(fs._get_file_object_from_path('/').get_name(), '')
        dir_1 = fs._get_file_object_from_path('/1')
        self.assertEqual(dir_1.get_name(), '1')
        self.assertEqual(is_directory(dir_1), True)

        self.assertEqual(fs._get_file_object_from_path('/1/1.1').get_name(), '1.1')
        
        fs.change_dir('1')
        self.assertEqual(fs._get_file_object_from_path('1.1').get_name(), '1.1')
        self.assertEqual(fs._get_file_object_from_path('..').get_name(), '')
        self.assertEqual(fs._get_file_object_from_path('1.1/../../1/1.1/../../.').get_name(), '')

        file_1 = fs._get_file_object_from_path('1.1/file1')
        self.assertEqual(file_1.get_name(), 'file1')
        self.assertEqual(is_file(file_1), True)
        
        # invalid path: file1 is not a directory
        with self.assertRaises(
            error.InvalidPathComponentException
        ): 
            fs._get_file_object_from_path('1.1/file1/..')
    
    def test_copy(self) -> None:
        fs = self._create_test_data()
        
        fs.write('2', 'abcde')
        # copy single file
        fs.copy('2', '6')
        file = fs._get_file_object_from_path('6')
        self.assertEqual(file.read(), 'abcde')
        
        # copy with duplicate name
        fs.copy('6', '6')
        file = fs._get_file_object_from_path('6_1')
        self.assertEqual(file.read(), 'abcde')

        # copy entire directory
        dir_1 = fs._get_file_object_from_path('1')
        fs.copy('1', 'new_1')
        fs.change_dir('new_1')
        self.assertTrue(
            self._are_files_equal_in_dir(fs._current_dir, dir_1),
        )

        fs.change_dir('1.1')
        
        self.assertTrue(
            self._are_files_equal_in_dir(fs._current_dir, dir_1.get_child('1.1')),
        )

        fs.change_dir('1.1.1')
        self.assertTrue(
            self._are_files_equal_in_dir(fs._current_dir, dir_1.get_child('1.1').get_child('1.1.1')),
        )
    
    def test_move(self) -> None:
        fs = self._create_test_data()
 
        # move single file
        fs.write('2', 'abcde')
        fs.move('2', '6')
        file = fs._get_file_object_from_path('6')
        self.assertEqual(file.read(), 'abcde')
        
        # move entire directory
        fs.move('1', '5')
        fs.change_dir('5')
        
        children_of_dir_5 = fs._current_dir.get_all_children()
        self.assertEqual(len(children_of_dir_5), 1)
        self.assertEqual(children_of_dir_5[0].get_name(), '1')

        fs.change_dir('1')
        self.assertEqual(len(fs._current_dir.get_all_children()), 2)
    
    def test_find(self) -> None:
        fs = self._create_test_data()
        result = fs.find('file1')
        
        self.assertEqual(len(result), 2)
    
    def _are_files_equal_in_dir(self, dir1: Directory, dir2: Directory) -> bool: 
        dir1_children = dir1.get_all_children()
        dir2_children = dir2.get_all_children()
        
        if len(dir1_children) != len(dir2_children):
            return False
        
        for idx in range(0, len(dir1_children)):
            if dir1_children[idx].get_name() != dir2_children[idx].get_name():
                return False
            if is_file(dir1_children[idx]) and \
                dir1_children[idx].read() != dir2_children[idx].read():
                return False
        return True

    def _create_test_data(self) -> FileSystem:
        fs = FileSystem()
        fs.make_new_dir('1')
        fs.make_new_file('2')
        fs.make_new_file('3')
        fs.make_new_file('4')
        fs.make_new_dir('5')
        
        fs.make_new_dir('1/1.1')
        fs.make_new_dir('1/1.2')
        fs.make_new_file('1/1.2/file1')
        
        fs.make_new_file('1/1.1/file1')
        fs.make_new_file('1/1.1/file2')

        fs.make_new_dir('1/1.1/1.1.1')
        fs.make_new_file('1/1.1/1.1.1/file3')
        return fs
        

if __name__ == '__main__':
    unittest.main()

                