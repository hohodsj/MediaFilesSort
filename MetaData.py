import os, glob
from PIL import Image
from PIL.ExifTags import TAGS
import ffmpeg
import mimetypes
from datetime import datetime

class MetaData:
    def __init__(self) -> None:
        pass

    def get_file_datetime(self, path:str):
         # Check if file is image
        filetype = mimetypes.guess_type(path)[0]
        if not filetype:
            print(f'Unreconized filetype: {path}')
            return
        if filetype.startswith('image'):
            exifdata = self._get_image_meta(path)
            for tagid in exifdata:
                tagname = TAGS.get(tagid, tagid)
                if tagname.lower() == 'datetime':
                    res = exifdata.get(tagid)[:10].split(':')
                    return res
        elif filetype.startswith('video'):
            format_info = self._get_video_meta(path)
            datetime_info = format_info.get('tags').get('creation_time')
            return datetime_info[:10].split('-')
        else:
            print('Consider processing: {path}')

    def get_file_meta_data(self, path:str):

        # Check if file is image
        if path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            return self._get_image_meta(path)
    
    def _get_image_meta(self, path:str):
        try:
            image = Image.open(path)
            exifdata = image.getexif()
            image.verify()
            return exifdata
        except Exception as e:
            print(f'Error when processing: {path} Message: {e}')
    
    def _get_video_meta(self, path:str):
        try:
            vid = ffmpeg.probe(path)
            return vid.get('format')
        except Exception as ex:
            print(ex)
            


if __name__=="__main__":
    path = f'{os.getcwd()}/media'
    for file in os.listdir(path):
        filepath = os.path.join(path,file)
        meta = MetaData()
        print(meta.get_file_datetime(filepath))