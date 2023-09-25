import os, glob
from PIL import Image
from PIL.ExifTags import TAGS
import ffmpeg
import mimetypes
from datetime import datetime
import logging


class MetaData:
    def __init__(self) -> None:
        pass

    def get_file_datetime(self, path:str):
         # Check if file is image
        filetype = mimetypes.guess_type(path)[0]
        if not filetype:
            print(f'Unreconized filetype: {path}')
            logging.warning(f'Unreconized filetype: {path}')
            return
        if filetype.startswith('image'):
            exifdata = self._get_image_meta(path)
            if exifdata is None:
                print(f'meta data is not available for {path} moving to 9999 folder')
                logging.error(f'Image meta data missing: {path}')
                return ('9999','99','99') #unable to find photo meta data
            for tagid in exifdata:
                tagname = TAGS.get(tagid, tagid)
                if str(tagname).lower() == 'datetime':
                    try:
                        year_month_day = exifdata.get(tagid)[:10] #yyyymmdd
                        if ":" in year_month_day:
                            datetime_info = year_month_day.split(':') # yyyy:mm:dd <- 10
                        else:
                            datetime_info = year_month_day.split('/') # yyyy/mm/dd <- 10
                        return datetime_info
                    except Exception as e:
                        logging.error(f'Image datetime information is missing {path}')
        elif filetype.startswith('video'):
            format_info = self._get_video_meta(path)
            if format_info is None:
                logging.error(f'Video meta data missing: {path}')
                return ('9999', '99', '98') #unable to find video meta data
            try:
                datetime_info = format_info.get('tags').get('creation_time')
                return datetime_info[:10].split('-')
            except Exception as e:
                logging.error(f'Video datetime information is missing {path}')
        else:
            logging.warn(f'Consider processing: {path}')
            print(f'Consider processing: {path}')
            return

    def get_file_meta_data(self, path:str):

        # Check if file is image
        if path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            return self._get_image_meta(path)
    
    def _get_image_meta(self, path:str):
        try:
            image = Image.open(path)
            exifdata = image.getexif()
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