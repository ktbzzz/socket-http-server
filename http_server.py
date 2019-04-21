import socket
import sys
import traceback
import mimetypes
import os
import subprocess

def response_ok(body=b"This is a minimal response", mimetype=b"text/plain"):
    response = b"\r\n".join([
        b"HTTP/1.1 200 OK",
        b"Content-Type: " + mimetype,
        b"",
        body])

    return response


def response_method_not_allowed():
    response = b"\r\n".join([
        b"HTTP/1.1 405 METHOD NOT ALLOWED",
        b"",
        b"Stop it"])

    return response


def response_not_found():
    response = b"\r\n".join([
        b"HTTP/1.1 404 NOT FOUND",
        b"",
        b"File not found."])

    return response


def parse_request(req):
    request_type, request_path, request_protocol = req.split("\r\n")[0].split(" ")

    if request_type == "GET":
        return request_path
    else:
        raise NotImplementedError


def response_path(path):
    file_conents = b''

    relative_path = os.path.join("webroot", path.strip('/'))
    is_file = os.path.isfile(relative_path)
    is_dir = os.path.isdir(relative_path)

    if is_file is True:
        if relative_path.endswith(".py"):
            if relative_path.endswith(".py"):
                proc = subprocess.Popen(['python', relative_path], stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)
                file_conents = proc.communicate()[0]
                mime_type = b"text/html"

                return file_conents, mime_type
        else:
            try:
                mime_type = mimetypes.guess_type(relative_path)[0].encode()

                with open(relative_path, 'rb') as f:
                    byte = f.read(1)
                    while byte:
                        file_conents += byte
                        byte = f.read(1)
            except FileNotFoundError:
                raise NameError
    elif is_dir is True:
        file_conents = '\n'.join(os.listdir(relative_path)).encode()
        mime_type = b"text/plain"
    else:
        raise NameError

    return file_conents, mime_type


def server(log_buffer=sys.stderr):
    address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("making a server on {0}:{1}".format(*address), file=log_buffer)
    sock.bind(address)
    sock.listen(1)

    try:
        while True:
            print('waiting for a connection', file=log_buffer)
            conn, addr = sock.accept()
            try:
                print('connection - {0}:{1}'.format(*addr), file=log_buffer)

                request = ''
                while True:
                    data = conn.recv(1024)
                    request += data.decode('utf8')

                    if '\r\n\r\n' in request:
                        break

                try:
                    desired_path = parse_request(request)
                    request_content, request_mime_type = response_path(desired_path)

                    response = response_ok(
                        body=request_content,
                        mimetype=request_mime_type
                    )

                    conn.sendall(response)
                except NameError:
                    conn.sendall(response_not_found())
                except NotImplementedError:
                    conn.sendall(response_method_not_allowed())


            except:
                traceback.print_exc()
            finally:
                conn.close() 

    except KeyboardInterrupt:
        sock.close()
        return
    except:
        traceback.print_exc()


if __name__ == '__main__':
    server()
    sys.exit(0)


