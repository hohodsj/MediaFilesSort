import Utils as utils
import argparse, os
import logging
from datetime import datetime
from collections import defaultdict

def main():
    print('Start')
    parser = argparse.ArgumentParser()

    parser.add_argument('src_path', default='./src', type=str, help="Source path")
    parser.add_argument('dest_path', default='./dest', type=str, help="Destination path")
    parser.add_argument('-m', '--mode', type=str, default='cp', help="Copy:cp") # support move later on
    args = parser.parse_args()
    src_path = args.src_path
    dest_path = args.dest_path
    print(f'{args.mode=}')
    
    # create destination direcotry if not exists
    fu = utils.FileUtil()
    if not fu.is_folder_exists(dest_path):
        fu.create_directory_recursive(dest_path)
    if not fu.is_folder_exists(f'{dest_path}/Logs'):
        fu.create_directory_recursive(f'{dest_path}/Logs')
    db = utils.DBUtil(dest_path)
    md = utils.MetaData()
    # setup logging
    logging.basicConfig(filename=f'{dest_path}/Logs/{str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}-MediaFileSort.log', level=logging.INFO)

    if args.mode == 'cp':
        dest_file2count = defaultdict(int)
        # Search through src and update db
        for origin_file_path in fu.find_files_recursive(src_path):
            
            filename = origin_file_path.split('/')[-1]
            file_origin_date = md.get_file_datetime(origin_file_path)
            if not file_origin_date:
                continue
            print(f'{origin_file_path}:{file_origin_date}')
            try:
                (year,month,day) = file_origin_date
                file_create_date = datetime.strptime(f'{year}-{month}-{day}', '%Y-%m-%d').date()
            except Exception as e:
                logging.error(f'Date not recognize {file_origin_date} origin file: {origin_file_path}')
                year = '9999'
                month = '12'
                day = '31'
                file_create_date = datetime(year=9999, month=12, day=31)
            dest_file_path = f'{dest_path}/{year}/{month}/{filename}'
            find_res = db.select(src_path=origin_file_path, mode=args.mode, dest_path=dest_file_path)
            if len(find_res) == 0:
                print(f"Processing: {origin_file_path}")
                # if not exists in db
                potential_duplicate = True if dest_file2count.get(dest_file_path,0) > 0 or len(db.select(dest_path=dest_file_path)) > 0 else False
                # if duplicated append count before the .
                if potential_duplicate:
                    dest_file2count[dest_file_path]+=1
                    file_path, file_extension = os.path.splitext(dest_file_path)
                    dest_file_path= f'{file_path}{dest_file2count[dest_file_path]}{file_extension}' # /src/to/dest1.extension
                    logging.warning(f'Duplicate detected: {dest_file_path}')
                db.insert(src_path=origin_file_path, mode=args.mode, dest_path=dest_file_path, status="initiated", file_create_datetime=file_create_date, potential_duplicate=potential_duplicate)
            else:
                print(f"Skipping: {origin_file_path}")
        # at the point all dest files should be created db
        for db_file in db.select(status='initiated'):
            db_src_path = db_file['src_path']
            db_mode = db_file['mode']
            db_dest_path = db_file['dest_path']
            db_status = db_file['status']
            db_file_create_datetime = db_file['file_create_datetime']
            db_potential_duplicate = db_file['potential_duplicate']
            fu.copy_file(db_src_path, db_dest_path)
            print(f"Completed copying file from {db_src_path} to {db_dest_path}")
            db.update(src_path=db_src_path, mode=args.mode, dest_path=db_dest_path, status='Completed', file_create_datetime=db_file_create_datetime, potential_duplicate=db_potential_duplicate)
            print(f'Completed updating {db_src_path=} {db_mode=} {db_dest_path=} {db_status=} {db_file_create_datetime=} {db_potential_duplicate=} to Complete')
    elif args.mode == 'db':
        for db_file in db.select(status='initiated'):
            db_src_path = db_file['src_path']
            db_mode = db_file['mode']
            db_dest_path = db_file['dest_path']
            db_status = db_file['status']
            db_file_create_datetime = db_file['file_create_datetime']
            db_potential_duplicate = db_file['potential_duplicate']
            fu.copy_file(db_src_path, db_dest_path)
            print(f"Completed copying file from {db_src_path} to {db_dest_path}")
            db.update(src_path=db_src_path, mode=args.mode, dest_path=db_dest_path, status='Completed', file_create_datetime=db_file_create_datetime, potential_duplicate=db_potential_duplicate)
            print(f'Completed updating {db_src_path=} {db_mode=} {db_dest_path=} {db_status=} {db_file_create_datetime=} {db_potential_duplicate=} to Complete')

if __name__=='__main__':
    main()