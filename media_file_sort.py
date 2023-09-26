import Utils as utils
import argparse, os
import logging
from datetime import datetime
from collections import defaultdict

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('src_path', type=str, help="Source path")
    parser.add_argument('dest_path', type=str, help="Destination path")
    parser.add_argument('-m', '--mode', type=str, default='cp', help="Copy:cp") # support move later on
    args = parser.parse_args()
    src_path = args.src_path
    dest_path = args.dest_path
    
    # create destination direcotry if not exists
    fu = utils.FileUtil()
    if not fu.is_folder_exists(dest_path):
        fu.create_directory_recursive(f'{dest_path}')
    if not fu.is_folder_exists(f'{dest_path}/Logs'):
        fu.create_directory_recursive(f'{dest_path}/Logs')
    db = utils.DBUtil(dest_path)
    md = utils.MetaData()
    # setup logging
    logging.basicConfig(filename=f'{dest_path}/Logs/{str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}-MediaFileSort.log', level=logging.INFO)

    if args.mode == 'cp':
        dest_file2count = defaultdict(int)
        # Search through src and update db
        for file in fu.find_files_recursive(src_path):
            
            filename = file.split('/')[-1]
            file_origin_date = md.get_file_datetime(file)
            if not file_origin_date:
                continue
            print(f'{file}:{file_origin_date}')
            (year,month,*day) = file_origin_date
            file_create_date = f'{year}-{month}-{day}'
            dest = f'{dest_path}/{year}/{month}/{filename}'
            if len(db.select(src_path=file, mode=args.mode, dest_path=dest)) == 0:
                print(f"Processing: {file}")
                # if not exists in db
                potential_duplicate = True if dest_file2count.get(dest,0) > 0 or len(db.select(dest_path=dest)) > 0 else False
                # if duplicated append count before the .
                if potential_duplicate:
                    dest_file2count[dest]+=1
                    file_path, file_extension = os.path.splitext(dest)
                    dest = f'{file_path}{dest_file2count[dest]}{file_extension}' # /src/to/dest1.extension
                    logging.warning(f'Duplicate detected: {dest}')
                db.insert(src_path=src_path, mode=args.mode, dest_path=dest, status="initiated", file_create_datetime=file_create_date, potential_duplicate=potential_duplicate)
            else:
                print(f"Skipping: {file}")
        # at the point all dest files should be created db
        for db_file in db.select(status='initiated'):
            db_src_path = db_file['src_path']
            db_mode = db_file['mode']
            db_dest_path = db_file['dest_path']
            db_status = db_file['status']
            db_file_create_datetime = db_file['file_create_datetime']
            db_potential_duplicate = db_file['potential_duplicate']
            print(f'Updating {db_src_path=} {db_mode=} {db_dest_path=} {db_status=} {db_file_create_datetime=} {db_potential_duplicate=} to Complete')
            db.update(src_path=db_src_path, mode=args.mode, dest_path=db_dest_path, status='Completed', file_create_datetime=db_file_create_datetime, potential_duplicate=db_potential_duplicate)




if __name__=='__main__':
    main()