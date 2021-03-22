import os
import sqlalchemy
import secret_manager as secret

class DBAgent:
    def __init__(
            self,
            name: str,
            host: str = secret.get_version("db_host"),
            user: str = secret.get_version("db_user"),
            password: str = secret.get_version("db_pass")
    ):
        self.password = password
        self.user = user
        self.host = host
        self.name = name
        self.config = {
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

        # Extract host and port from db_host
        host_args = host.split(":")
        hostname, port = host_args[0], int(host_args[1])

        self.pool = sqlalchemy.create_engine(
            # Equivalent URL:
            # mysql+pymysql://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
            sqlalchemy.engine.url.URL(
                drivername="mysql+pymysql",
                username=user,  # e.g. "my-database-user"
                password=password,  # e.g. "my-database-password"
                host=hostname,  # e.g. "127.0.0.1"
                port=port,  # e.g. 3306
                database=name,  # e.g. "my-database-name"
            ),
            **self.config
        )

    def interact(self, statement):
        try:
            # Using a with statement ensures that the connection is always released
            # back into the pool at the end of statement (even if an error occurs)
            with self.pool.connect() as conn:
                return conn.execute(statement)
        except Exception as e:
            # If something goes wrong, handle the error in this section. This might
            # involve retrying or adjusting parameters depending on the situation.
            # [START_EXCLUDE]
            raise RuntimeWarning("Interaction database failed with message:" + str(e))

    def select(self, statement):
        """ Special function for select or similar statements which require something to be returned from the db
        as we want to return a value.
        :param statement: The statement to be carried out.
        :return: The resulting query from the database.
        """

        try:
            # Using a with statement ensures that the connection is always released
            # back into the pool at the end of statement (even if an error occurs)
            with self.pool.connect() as conn:
                return conn.execute(statement).fetchall()
        except Exception as e:
            # If something goes wrong, handle the error in this section. This might
            # involve retrying or adjusting parameters depending on the situation.
            # [START_EXCLUDE]
            raise RuntimeWarning("Selection database failed with message:" + str(e))

