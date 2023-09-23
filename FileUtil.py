import os
import os.path
from glob import glob

class FileUtil:
    def __init__(self):
        pass

    def find_pwd_files(self, path:str):
        for file in os.listdir(path):
            filepath = os.path.join(path,file)
            yield filepath
    
    def find_files_recursive(self, path:str):
        for dirpath, _, filenames in os.walk(path):
            for filename in filenames:
                if not filename.startswith('.'): # ignores hidden files
                    filepath = os.path.join(dirpath, filename)
                    yield filepath


if __name__ == '__main__':
    fu = FileUtil()
    path = '/path/to/directory'
    print('pwd')
    for f in fu.find_pwd_files(path):
        print(f)
    print('recursive')
    for f in fu.find_files_recursive(path):
        print(f)