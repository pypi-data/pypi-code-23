from cherryontop import start_server


if __name__ == "__main__":
    start_server(port=8111, log_to_screen=True, autoreload=True,
    path_to_access_log="./access.log",
    path_to_error_log="./error.log"
    )
