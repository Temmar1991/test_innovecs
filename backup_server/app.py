from flask import Flask
import os
import zipfile
from flask_socketio import SocketIO
import logging
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from random import randrange

app = Flask(__name__)
socketio = SocketIO(app)
logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.WARN)

cwd = os.getcwd()
file_name = os.path.join(cwd, os.environ.get("DUMP_FILE"))
zip_name = f"backup_seeder.zip"
zip_file = os.path.join(cwd, zip_name)


def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)


def check_socket(host, port):
    import socket
    from contextlib import closing
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex((host, port)) == 0:
            print("Port is open")
            return True
        else:
            print("Port is not open")
            return False


def make_backup(name) -> None:
    arg_string = f"mysqldump -h {os.environ.get('HOST')} -u {os.environ.get('DATABASE_USER')} -p{os.environ.get('DATABASE_PASS')} {os.environ.get('DATABASE')} > {name} 2>&1 /dev/mull"
    try:
        if randrange(8) == 5:
            socketio.emit('backup_failed')
            raise ValueError('Backup failed')
        os.popen(arg_string)
        backup_zip = zipfile.ZipFile(zip_file, 'w')
        backup_zip.write(name, compress_type=zipfile.ZIP_DEFLATED)
        logging.info("Backup is successful")
        size = file_size(zip_file)
        socketio.emit('backup_successful', {'file_name': zip_file, 'file_size': size, 'date': str(datetime.datetime.now())})
    except Exception as e:
        logging.exception('Command failed')


# def archive(zip_nam, file_to_zip):
#     backup_zip = zipfile.ZipFile(os.path.join(cwd, zip_nam), 'w')
#     for folder, subfolders, files in os.walk(cwd):
#         for file in files:
#             if file_to_zip in file:
#                 backup_zip.write(os.path.join(folder, file), file_to_zip, compress_type=zipfile.ZIP_DEFLATED)
#     backup_zip.close()


def periodic_backup():
    make_backup(file_name)


sched = BackgroundScheduler(daemon=True)
sched.add_job(periodic_backup, trigger='cron', minute="*", second="*/5")
sched.start()


if __name__ == '__main__':
    socketio.run(app, port=9000, host="0.0.0.0", use_evalex=False, debug=False)

