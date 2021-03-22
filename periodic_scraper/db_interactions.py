import os
import sqlalchemy
import secret_manager as secret


def init_tcp_connection_engine(db_config):

    db_user = secret.get_version("db_user", version_name="latest")
    db_pass = secret.get_version("db_pass", version_name="latest")
    # todo: check how to get this automatically
    # db_name = secret.get_version("db_name", version_name="latest")
    db_name = "bill_data"
    db_host = secret.get_version("db_host", version_name="latest")
    print(f"db_user:{db_user}")
    print(f"db_pass:{db_pass}")
    print(f"db_name:{db_name}")
    print(f"db_host:{db_host}")


    # Extract host and port from db_host
    host_args = db_host.split(":")
    db_hostname, db_port = host_args[0], int(host_args[1])

    pool = sqlalchemy.create_engine(
        # Equivalent URL:
        # mysql+pymysql://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
        sqlalchemy.engine.url.URL(
            drivername="mysql+pymysql",
            username=db_user,  # e.g. "my-database-user"
            password=db_pass,  # e.g. "my-database-password"
            host=db_hostname,  # e.g. "127.0.0.1"
            port=db_port,  # e.g. 3306
            database="bill_data",  # e.g. "my-database-name"
        ),
        **db_config
    )
    return pool


def init_connection_engine():
    db_config = {
        # Pool size is the maximum number of permanent connections to keep.
        "pool_size": 5,
        # Temporarily exceeds the set pool_size if no connections are available.
        "max_overflow": 2,
        # The total number of concurrent connections for your application will be
        # a total of pool_size and max_overflow.
        # 'pool_timeout' is the maximum number of seconds to wait when retrieving a
        # new connection from the pool. After the specified amount of time, an
        # exception will be thrown.
        "pool_timeout": 30,  # 30 seconds
        # 'pool_recycle' is the maximum number of seconds a connection can persist.
        # Connections that live longer than the specified amount of time will be
        # reestablished
        "pool_recycle": 1800,  # 30 minutes
    }
    return init_tcp_connection_engine(db_config)


db = init_connection_engine()


def interact(statement):
    try:
        # Using a with statement ensures that the connection is always released
        # back into the pool at the end of statement (even if an error occurs)
        with db.connect() as conn:
            return conn.execute(statement)
    except Exception as e:
        # If something goes wrong, handle the error in this section. This might
        # involve retrying or adjusting parameters depending on the situation.
        # [START_EXCLUDE]
        return None




def select(statement):
    """ Special function for select or similar statements which require something to be returned from the db
    as we want to return a value.
    :param statement: The statement to be carried out.
    :return: The resulting query from the database.
    """

    try:
        # Using a with statement ensures that the connection is always released
        # back into the pool at the end of statement (even if an error occurs)
        with db.connect() as conn:
            return list(conn.execute(statement).fetchall())
    except Exception as e:
        # If something goes wrong, handle the error in this section. This might
        # involve retrying or adjusting parameters depending on the situation.
        # [START_EXCLUDE]
        return None

