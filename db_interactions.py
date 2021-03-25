import sqlalchemy
import secret_manager as secret


def init_tcp_connection_engine(db_config: dict):
    # Todo add docstring and method signature (return type) i know it's None or conn.execute
    """

    :param db_config:
    :return:
    """
    db_user = secret.get_version("db_user")
    db_pass = secret.get_version("db_pass")
    db_name = secret.get_version("db_name")
    db_host = secret.get_version("db_host")

    # Extract the host and port from db_host
    host_args = db_host.split(":")
    db_hostname, db_port = host_args[0], int(host_args[1])

    pool = sqlalchemy.create_engine(
        # Equivalent URL: mysql+pymysql://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
        sqlalchemy.engine.url.URL(
            drivername="mysql+pymysql",
            username=db_user,
            password=db_pass,
            host=db_hostname,
            port=db_port,
            database=db_name,
        ),
        **db_config
    )
    return pool


def init_connection_engine():
    # Todo add docstring and method signature (return type) i know it's None or conn.execute
    """

    :return:
    """
    db_config = {
        "pool_size": 5,  # Max number of permanent connections
        "max_overflow": 2,  # Handle 2 extra connections if pool_size is exceeded (effective pool size: 7).
        "pool_timeout": 30,  # Max seconds to wait to retrieve a connection. If time is exceeded an error is thrown
        "pool_recycle": 1800,  # Max seconds a connection can persist
    }
    return init_tcp_connection_engine(db_config)


db = init_connection_engine()


def interact(statement: str):
    # Todo add docstring and method signature (return type) i know it's None or conn.execute
    """
    Executes the given SQL statement. Used for INSERT, DELETE, UPDATE SQL functions.
    :param statement: The SQL statement to carry out.
    :return:
    """
    try:
        # Using a with statement ensures that the connection is always released
        # back into the pool at the end of statement (even if an error occurs)
        with db.connect() as conn:
            return conn.execute(statement)
    except Exception as e:
        # If something goes wrong, handle the error in this section. This might
        # involve retrying or adjusting parameters depending on the situation.
        # [START_EXCLUDE]
        raise RuntimeWarning(f"Interaction database failed with message: {str(e)}")


def select(statement: str) -> list or None:
    """
    Executes the given SQL statement. Used for SELECT and similar functions that require something to be returned from
    the database.
    :param statement: The SQL statement to be carried out.
    :return: The resulting query from the database in the form of a list.
    """
    try:
        # Using a with statement ensures that the connection is always released
        # back into the pool at the end of statement (even if an error occurs)
        with db.connect() as conn:
            return list(conn.execute(statement).fetchall())  # Return the result as a list
    except Exception as e:
        # If something goes wrong, handle the error in this section. This might
        # involve retrying or adjusting parameters depending on the situation.
        # [START_EXCLUDE]
        raise RuntimeWarning(f"Selection database failed with message: {str(e)}")
