from sqlalchemy import create_engine


class DBEngine:

    dataset_engine = create_engine('mysql://scott:tiger@localhost:5432/mydatabase')

