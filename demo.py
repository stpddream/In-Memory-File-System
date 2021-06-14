from file_system_view import FileSystemView
from file_system.file_system import FileSystem
from file_system.utils import parse_path


print('==== Make some directories and files ====')
fsv = FileSystemView()
fsv.make_new_dir('documents')
fsv.make_new_file('temp_file1')
fsv.make_new_file('random_doc')
fsv.make_new_file('system_file')
fsv.make_new_dir('system')
fsv.ls()

fsv.change_dir('documents')
fsv.make_new_dir('dev')
fsv.make_new_file('some_test1')
fsv.change_dir('dev')
fsv.make_new_dir('source_code')
fsv.change_dir('source_code')
fsv.get_current_path()
fsv.change_dir('..')
fsv.get_current_path()
fsv.change_dir('/system')
fsv.get_current_path()
fsv.make_new_dir('ui/bad_code/tests')
fsv.make_new_file('ui/bad_code/tests/some_test1')

fsv.change_dir('ui/bad_code/tests/../.././bad_code/tests')
fsv.make_new_file('ui/bad_code/tests/some_test1')

fsv.change_dir('/')
fsv.ls()

print('==== Remove temp_file1 ====')
fsv.remove('temp_file1')
fsv.ls()

# move files
print('==== Move random_doc to /documents ====')
fsv.move('random_doc', 'documents')
fsv.change_dir('documents')
fsv.ls()

# write and read
print('==== Read and Write Files ====')
fsv.write('/system_file', 'abcde')
fsv.cat('/system_file')

# find
print('==== Searching for some_tests1 ====')
fsv.change_dir('/')
fsv.find('some_test1')

print('==== Copy a single file ====')
fsv.make_new_file('/core_dump_f')
fsv.change_dir('/')
fsv.ls()

fsv.copy('/core_dump_f', 'core_dump_new_f')
fsv.ls()


print('==== Copy a directory ====')
fsv.copy('/documents', 'backup_documents')
fsv.change_dir('/backup_documents')
fsv.ls()

print('==== Copy with duplicate names again ==== ')
fsv.copy('/system_file', '/documents/some_test1')
fsv.change_dir('/documents')
fsv.ls()