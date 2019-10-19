from socketIO_client import SocketIO, LoggingNamespace

sock = SocketIO('http://localhost', 9000, LoggingNamespace)


def backup_event(message):
    print(f"Backup file {message['file_name']}, size {message['file_size']} is done at time {message['date']}")


sock.on('backup', backup_event)


if __name__ == '__main__':
    sock.wait()
