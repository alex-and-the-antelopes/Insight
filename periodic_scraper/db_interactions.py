import sqlalchemy
import secret_manager as secret


def init_tcp_connection_engine(db_config: dict):
    # Todo add docstring and method signature (return type) i know it's None or conn.execute
    """
    Fetches secrets from the secret manager adn creates an sqlalchemy connection pool through
    the connection engine.
    :param db_config: The configuration for the database
    :return: pool of database connections or None if failed to connect.
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
    Function that starts the database connection pool with the configurations specified below.

    :return: a pool of database connection or None if connection failed.
    """
    db_config = {
        "pool_size": 5,  # Max number of permanent connections
        "max_overflow": 2,  # Handle 2 extra connections if pool_size is exceeded (total pool size: 7).
        "pool_timeout": 30,  # Max seconds to wait to retrieve a connection. If time is exceeded an error is thrown
        "pool_recycle": 1800,  # Max seconds a connection can persist
    }
    return init_tcp_connection_engine(db_config)


db = init_connection_engine() #starts the database connection where db is the pool of connections


def interact(statement: str):
    # Todo add docstring and method signature (return type) i know it's None or conn.execute
    """
    Executes the given SQL statement. Used for INSERT, DELETE, UPDATE SQL functions.
    :param statement: The SQL statement to carry out. (including ;)
    :return: The response from the database after the action was carried out as a string
    """
    try:
        with db.connect() as conn:
            return str(conn.execute(statement))
    except Exception as e:
        # Raises the error that the statement could not execute
        raise RuntimeWarning(f"Interaction database failed with message: {str(e)}")


def select(statement: str) -> list or None:
    """
    Executes the given SQL statement. Used for SELECT and similar functions that require something to be returned from
    the database.
    :param statement: The SQL statement to be carried out.
    :return: The resulting query from the database in the form of a string.
    """
    try:
        with db.connect() as conn:
            return str(conn.execute(statement).fetchall())  # Return the result as a list
    except Exception as e:
        # Raises an error that the statement could not finish execution.
        raise RuntimeWarning(f"Selection database failed with message: {str(e)}")
