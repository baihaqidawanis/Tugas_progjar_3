from socket import *
import socket
import threading
import logging
import sys

from file_protocol import FileProtocol
fp = FileProtocol()

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)

    def run(self):
        buffer = ''
        try:
            while True:
                data = self.connection.recv(1024)
                if not data:
                    break
                buffer += data.decode()

                # Jika sudah dapat akhir protokol
                if '\r\n\r\n' in buffer:
                    break

            # Proses hanya jika buffer tidak kosong
            if buffer.strip():
                command = buffer.strip('\r\n')
                logging.warning(f"data diterima dari {self.address}: {command}")

                hasil = fp.proses_string(command)
                hasil += '\r\n\r\n'
                self.connection.sendall(hasil.encode())
        except Exception as e:
            logging.error(f"Terjadi kesalahan pada {self.address}: {str(e)}")
        finally:
            self.connection.close()


class Server(threading.Thread):
    def __init__(self, ipaddress='0.0.0.0', port=6666):
        self.ipinfo = (ipaddress, port)
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        threading.Thread.__init__(self)

    def run(self):
        logging.warning(f"Server aktif di {self.ipinfo}")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(5)

        while True:
            try:
                connection, client_address = self.my_socket.accept()
                logging.warning(f"Koneksi dari {client_address}")
                clt = ProcessTheClient(connection, client_address)
                clt.start()
                self.the_clients.append(clt)
            except KeyboardInterrupt:
                logging.warning("Server dihentikan oleh pengguna")
                break
            except Exception as e:
                logging.error(f"Kesalahan server: {str(e)}")


def main():
    svr = Server(ipaddress='0.0.0.0', port=6667)
    svr.start()


if __name__ == "__main__":
    main()
