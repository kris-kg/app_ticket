from psycopg2 import pool


class Databese:
    __connection_pool = None

    @classmethod
    def initialise(cls,  ** kwargs):
        cls.__connection_pool = pool.SimpleConnectionPool(1, 10, **kwargs)  
    
    @classmethod
    def get_connection(cls):
        return cls.__connection_pool.getconn()

    @classmethod
    def return_connection(cls, connection):
        Databese.__connection_pool.putconn(connection)

    @classmethod
    def close_all_connection(cls):
        Databese.__connection_pool.closeall()



class CursorFromConnectionFromPool:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def __enter__(self):   
        self.connection = Databese.get_connection()
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exception_type, exception_value, exception_tracenack):  #exc - exception 
        if exception_value:
            self.connection.rollback()
        else:
            self.cursor.close()
            self.connection.commit()
            Databese.return_connection(self.connection)
