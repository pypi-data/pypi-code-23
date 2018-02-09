import MySQLdb
import pickle
from shutil import copyfile
from pathlib import Path
from sys import argv


def execute_query(conn, query):
    """
    Executes a query.
    :param conn: Connection to database
    :param query: SQL query to execute
    :return: Result of query
    """
    cur = conn.cursor()
    cur.execute(query)
    fetched = cur.fetchone()
    cur.close()
    return fetched


def create_media_entry(
        conn,
        model_id=None,
        model_type="document",
        collection_name="default",
        name=None,
        file_name=None,
        mime_type="application/pdf",
        disk="media",
        size=None,
        manipulations="[]",
        custom_properties="[]",
        order_column=None,
        created_at=None,
        updated_at=None
        ):
    """
    Creates an entry in the database table 'media'.
    :param conn: Connection to database
    :param model_id: ID
    :param model_type: "car" or "document"
    :param collection_name: Type of the document
    :param name: ÜP or RP or something like this
    :param file_name: Name of uploaded file
    :param mime_type: "application/pdf"
    :param disk: "media"
    :param size: Filesize in byte
    :param manipulations: empty json
    :param custom_properties: empty json
    :param order_column: wtf?
    :param created_at: NOW!
    :param updated_at: Now or nothing
    :return:
    """
    query = """INSERT INTO media
            (model_id, model_type, collection_name, name, file_name, mime_type, disk, size, manipulations,
             custom_properties, order_column, created_at, updated_at)
    VALUES ({}, '{}', '{}', '{}', '{}', '{}', '{}', {}, '{}', '{}', {}, '{}', '{}')
    """.format(model_id, model_type, collection_name, name, file_name, mime_type, disk, size, manipulations,
               custom_properties, order_column, created_at, updated_at)
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    cur.close()


def create_document_entry(
        conn,
        model_id=None,
        model_type="car",
        user_id=None,
        name=None,
        created_at=None,
        updated_at=None
        ):
    """
    Creates an entry in the database table 'documents'.
    :param conn: Connection to database
    :param model_id: ID
    :param model_type: "car"
    :param user_id: From user, 203 is me
    :param name:  Übernahmeprotokoll or Rücknahmeprotokoll or ...
    :param created_at: NOW!
    :param updated_at: Now or nothing
    :return:
    """
    query = """INSERT INTO documents
            (model_id, model_type, user_id, name, created_at, updated_at)
    VALUES ({}, '{}', '{}', '{}', '{}', '{}')
    """.format(model_id, model_type, user_id, name, created_at, updated_at)
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    cur.close()


def upload_file(local_file_path, target_file_path):
    """
    Copies a file.
    :param local_file_path: Source
    :param target_file_path: Directory
    :return:
    """
    copyfile(local_file_path, target_file_path)


def add_documents(conn, assignment, protocol_type, protocol_dir, storage_dir, order_column):
    """
    Adds documents to database and uploads the files.
    :param conn: Connection to database
    :param assignment: Assignment file with ID's and filenames
    :param protocol_type: "UP" or "RP"
    :param protocol_dir: Source where protocols are saved
    :param storage_dir: Dir to upload protocols in
    :param order_column: a weird integer
    :return:
    """
    media_name = None
    doc_name = None
    if protocol_type == "UP":
        media_name = "ÜP"
        doc_name = "Übernahmeprotokoll"
    if protocol_type == "RP":
        media_name = "RP"
        doc_name = "Rücknahmeprotokoll"
    for key, value in assignment.items():
        car_id = key
        for i in range(0, len(value)):
            file_name = value.pop()
            local_file_path = protocol_dir / file_name
            file_size = local_file_path.stat().st_size

            create_media_entry(conn=conn,
                               model_id=car_id,
                               model_type="document",
                               collection_name="default",
                               name=media_name,
                               file_name=file_name,
                               mime_type="application/pdf",
                               disk="media",
                               size=file_size,
                               manipulations="[]",
                               custom_properties="[]",
                               order_column=(order_column+1),
                               created_at=execute_query(conn, 'SELECT now()')[0],
                               updated_at=execute_query(conn, 'SELECT now()')[0]
                               )
            order_column += 1

            create_document_entry(conn=conn,
                                  model_id=car_id,
                                  model_type="car",
                                  user_id=203,
                                  name=doc_name,
                                  created_at=execute_query(conn, 'SELECT now()')[0],
                                  updated_at=execute_query(conn, 'SELECT now()')[0]
                                  )

            target_dir = Path(storage_dir) / str(car_id)
            target_file_path = target_dir / file_name
            if target_dir.is_dir() is False:
                target_dir.mkdir()
            upload_file(local_file_path=local_file_path, target_file_path=target_file_path)


def upload_protocols(conn, documents_dir, storage_dir):
    """
    Uploads protocols to database.
    :param conn: Connection to db
    :param documents_dir: Source directory of documents
    :param storage_dir: Upload directory on server
    :return:
    """
    up_dir = Path(documents_dir) / Path("uploads/upload_ups")
    rp_dir = Path(documents_dir) / Path("uploads/upload_rps")

    with open(up_dir / "assignment_up.p", "rb") as t:
        assignment_up = pickle.load(t)
    with open(rp_dir / "assignment_rp.p", "rb") as t:
        assignment_rp = pickle.load(t)

    order_column = execute_query(conn, 'SELECT MAX(order_column) FROM media')[0]
    add_documents(conn, assignment_up, "UP", up_dir, storage_dir, order_column)

    order_column = execute_query(conn, 'SELECT MAX(order_column) FROM media')[0]
    add_documents(conn, assignment_rp, "RP", rp_dir, storage_dir, order_column)


def main(host, user, pw, db, documents_dir, storage_dir=Path("storage/app/public/media")):
    conn = MySQLdb.connect(host=host, user=user, passwd=pw, db=db)
    upload_protocols(conn, documents_dir, storage_dir)
    conn.close()


def get_argv():
    """
    Handling of console inputs.
    :return: Inputs for usage in main
    """
    helps = """
    --help: Show usage of commands \n
    -host: Host address of server \n
    -user: Username \n
    -pw: Password \n
    -db: Database to connect with \n
    -docdir: Local path where documents in folder 'uploads' are stored \n
    -stordir: Path to save data on server. Default is \'storage/app/public/media\'
    """
    main_arguments = {}
    for element in argv:
        if element == "--help":
            print(helps)
        if element == "-host":
            main_arguments["host"] = argv[argv.index(element) + 1]
        if element == "-user":
            main_arguments["user"] = argv[argv.index(element) + 1]
        if element == "-pw":
            main_arguments["pw"] = argv[argv.index(element) + 1]
        if element == "-db":
            main_arguments["db"] = argv[argv.index(element) + 1]
        if element == "-docdir":
            main_arguments["documents_dir"] = argv[argv.index(element) + 1]
        if element == "-stordir":
            main_arguments["storage_dir"] = argv[argv.index(element) + 1]
    return main_arguments


if __name__ == "__main__":
    main_arguments = get_argv()
    if "storage_dir" in main_arguments:
        main(host=main_arguments["host"], user=main_arguments["user"], pw=main_arguments["pw"], db=main_arguments["db"],
             documents_dir=main_arguments["documents_dir"], storage_dir=main_arguments["storage_dir"])
    else:
        main(main_arguments["host"], main_arguments["user"], main_arguments["pw"], main_arguments["db"],
             main_arguments["documents_dir"])
