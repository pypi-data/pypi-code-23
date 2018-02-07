from trackerfw.webserver import Webserver

def main():
    server = Webserver()
    server.listen(
        'localhost',
        9999
    )