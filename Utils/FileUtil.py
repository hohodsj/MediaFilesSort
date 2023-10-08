import os
import os.path
import shutil

class FileUtil:
    def __init__(self):
        pass

    def find_pwd_files(self, path:str):
        if self.is_folder_exists(path):
            for file in os.listdir(path):
                filepath = os.path.join(path,file)
                yield filepath
    
    def find_files_recursive(self, path:str):
        for dirpath, _, filenames in os.walk(path):
            for filename in filenames:
                if not filename.startswith('.'): # ignores hidden files
                    filepath = os.path.join(dirpath, filename)
                    yield filepath
    
    def is_folder_exists(self, path:str):
        return os.path.isdir(path)
    
    def is_file_exists(self, path:str):
        return os.path.isfile(path)

    def create_directory_recursive(self, path:str):
        os.makedirs(path, exist_ok=True)
    
    def copy_file(self, src:str, dest:str):
        if not self.is_file_exists(src):
            print(f"{src} does not exists")
            return
        if self.is_file_exists(dest):
            print(f"{dest} already exists no need to copy")
            return
        # determine if path is file or directory
        # if contains . means theres file type
        src_parts = src.split('/')
        dest_parts = dest.split('/')
        # src must contains file name, if last part of src == last part of dest
        # dest must contains file
        if src_parts[-1] == dest_parts[-1]:
            dest = "/".join(dest_parts[:-1])
        if not self.is_folder_exists(dest):
            self.create_directory_recursive(dest)
        shutil.copy2(src, dest)
        
if __name__ == '__main__':
    fu = FileUtil()
    path = '/path/to/src'
    print('pwd')
    for f in fu.find_pwd_files(path):
        print(f)
    print('recursive')
    for f in fu.find_files_recursive(path):
        print(f)
    print('check folder exists')
    print(fu.is_folder_exists(path))

    print('check file exists')
    print(fu.is_file_exists(path))

    print("create directory")
    fu.create_directory_recursive(f"{path}/test/test1/test2")

    src = "/path/to/src"
    dest = "/path/to/dest"
    fu.copy_file(src,dest)