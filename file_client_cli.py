import socket
import json
import base64
import logging
import os

# Ganti IP dan port sesuai dengan alamat server
server_address = ('0.0.0.0', 7777)


def send_command(command_str=""):
    """Mengirim perintah ke server dan menerima respon JSON."""
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(server_address)
        logging.warning(f"Terhubung ke {server_address}")
        command_str += "\r\n\r\n"
        sock.sendall(command_str.encode())

        data_received = ""
        while True:
            data = sock.recv(1024)
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                break

        hasil = json.loads(data_received)
        return hasil
    except Exception as e:
        logging.warning(f"Gagal menerima data: {e}")
        return {"status": "ERROR", "data": str(e)}
    finally:
        sock.close()


def remote_list():
    hasil = send_command("LIST")
    if hasil.get('status') == 'OK':
        print("📄 Daftar file yang tersedia:")
        for file in hasil['data']:
            print(f"- {file}")
        return True
    else:
        print("Gagal mengambil daftar file.")
        return False


def remote_get(filename=""):
    hasil = send_command(f"GET {filename}")
    if hasil.get('status') == 'OK':
        try:
            with open(hasil['data_namafile'], 'wb') as fp:
                fp.write(base64.b64decode(hasil['data_file']))
            print(f"✅ File '{filename}' berhasil diunduh.")
            return True
        except Exception as e:
            print(f"❌ Kesalahan saat menyimpan file: {e}")
    else:
        print("❌ Gagal mengunduh file.")
    return False


def remote_upload(filepath="", upload_as=""):
    if not os.path.exists(filepath):
        print(f"❌ File '{filepath}' tidak ditemukan.")
        return False

    try:
        with open(filepath, 'rb') as f:
            encoded_data = base64.b64encode(f.read()).decode()

        filename = upload_as or os.path.basename(filepath)
        command = f"UPLOAD {filename}||{encoded_data}"
        hasil = send_command(command)
        if hasil.get('status') == 'OK':
            print(f"✅ File '{filename}' berhasil di-upload.")
            return True
        else:
            print(f"❌ Gagal upload: {hasil.get('data')}")
    except Exception as e:
        print(f"❌ Kesalahan saat upload: {e}")
    return False


def remote_delete(filename=""):
    hasil = send_command(f"DELETE {filename}")
    if hasil.get('status') == 'OK':
        print(f"🗑️ File '{filename}' berhasil dihapus dari server.")
        return True
    else:
        print(f"❌ Gagal menghapus file: {hasil.get('data')}")
        return False


if __name__ == '__main__':
    server_address = ('172.16.16.102', 6667)
    # Langkah-langkah otomatis:
    remote_list()  # 1. List file

    remote_get("donalbebek.jpg")  # 2. Download file donalbebek.jpg dari server

    remote_upload("donalbebek.jpg", "upload_tes.jpg")  # 3. Upload file tsb sebagai upload_tes.jpg

    remote_delete("upload_tes.jpg")  # 4. Hapus file hasil upload
