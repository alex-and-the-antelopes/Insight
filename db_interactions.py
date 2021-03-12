import os
import sqlalchemy


class DatabaseInteraction:
    """Creates a pool of cursors (3) for the cloudsql database connected to through the env variables"""

    def __init__(self):
        self.db_user = os.environ.get('CLOUD_SQL_USERNAME')
        self.db_password = os.environ.get('CLOUD_SQL_PASSWORD')
        self.db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
        self.db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')
        # When deployed to App Engine, the `GAE_ENV` environment variable will be
        # set to `standard`
        if os.environ.get('GAE_ENV') == 'standard':
            # If deployed, use the local socket interface for accessing Cloud SQL
            unix_socket = '/cloudsql/{}'.format(self.db_connection_name)
            engine_url = 'mysql+pymysql://{}:{}@/{}?unix_socket={}'.format(
                self.db_user, self.db_password, self.db_name, unix_socket)
        # The Engine object returned by create_engine() has a QueuePool integrated
        # See https://docs.sqlalchemy.org/en/latest/core/pooling.html for more
        # information
        self.engine = sqlalchemy.create_engine(engine_url, pool_size=3)

    def execute(self, statement):
        """Executes an SQL statement and returns the result of that transaction as a string """
        cnx = self.engine.connect()
        cursor = cnx.execute(statement)
        result = cursor.fetchall()
        cnx.close()
        return str(result)
