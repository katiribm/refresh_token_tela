from sqlalchemy import Connection, create_engine
import json, os


class SybaseConnection:
    """
    Classe para interação com Sybase ASA 9
    """

    @classmethod
    def connect(cls, dsn: str) -> Connection:
        """
        Retorna um objeto de conexão do sqlalchemy.

        >> Driver ODBC testado: Adaptive Server Anywhere 9.0

        Args:
        dsn (str): nome da fonte de dados ODBC para conexão
        """
        with open(f"{os.path.dirname(__file__)}\\credentials.json", "r") as file:
            data = json.loads(file.read())
            data = data["sybase"]

        user, password = data["user"], data["password"]

        engine = create_engine(f"sybase+pyodbc://{user}:{password}@{dsn}")

        try:
            endpoint = engine.connect()
            return endpoint

        except Exception as error:
            print(
                f"Falha na conexão. Favor verificar se o nome da fonte de dados e as credenciais estão corretas.\n {error}"
            )


class FirebirdConnection:
    """
    Classe para interação com Firebird 3.0
    """

    @classmethod
    def connect(cls, db_name: str, server: str = "localhost") -> Connection:
        """
        Retorna um objeto de conexão do sqlalchemy

        Args:
        db_name (str): nome do arquivo de backup do firebird que será utilizado
        """
        with open(f"{os.path.dirname(__file__)}\\credentials.json", "r") as file:
            data = json.loads(file.read())
            data = data["firebird"]

        user, password = data["user"], data["password"]

        engine = create_engine(
            f"firebird://{user}:{password}@{server}/{os.path.dirname(__file__)}\\data\\{db_name}"
        )

        try:
            endpoint = engine.connect()
            return endpoint

        except Exception as error:
            print(
                f"Falha na conexão. Favor verificar se o nome da fonte de dados e as credenciais estão corretas.\n {error}"
            )


class SqlServerConnection:
    """
    Classe para interação com SQL Server 17
    """

    @classmethod
    def connect(cls, dsn: str) -> Connection:
        """
        Retorna um objeto de conexão do sqlalchemy

        >> Driver ODBC testado: ODBC Driver 17 for SQL Server

        Args:
        dsn (str): nome da fonte de dados ODBC para conexão
        """
        with open(f"{os.path.dirname(__file__)}\\credentials.json", "r") as file:
            data = json.loads(file.read())
            data = data["sqlserver"]

        user, password = data["user"], data["password"]

        # print(f"mssql+pyodbc://{user}:{password}@{dsn}")
        engine = create_engine(f"mssql+pyodbc://{dsn}?trusted_connection=yes")

        try:
            endpoint = engine.connect()
            return endpoint

        except Exception as error:
            print(
                f"Falha na conexão. Favor verificar se o nome da fonte de dados e as credenciais estão corretas.\n {error}"
            )


class PostgresConnection:
    """
    Classe para interação com Postgres 15
    """

    @classmethod
    def connect(cls, db_name: str, port: int, server: str = "localhost") -> Connection:
        """
        Retorna um objeto de conexão do sqlalchemy

        Args:
        port (int): porta de conexão do servidor
        db_name (str): nome do banco de dados que será utilizado
        """
        with open(f"{os.path.dirname(__file__)}\\credentials.json", "r") as file:
            data = json.loads(file.read())
            data = data["postgres"]

        user, password = data["user"], data["password"]

        engine = create_engine(
             f"postgresql+psycopg2://{user}:{password}@{server}:{port}/{db_name}"
        )

        try:
            endpoint = engine.connect()
            return endpoint

        except Exception as error:
            print(
                f"Falha na conexão. Favor verificar se o nome da fonte de dados e as credenciais estão corretas.\n {error}"
            )




class SqLiteConnection:
    """
    Classe para interação com SQLite 3
    """

    @classmethod
    def connect(cls, db_name: str) -> Connection:
        """
        Retorna um objeto de conexão do sqlalchemy

        Args:
        port (int): porta de conexão do servidor
        db_name (str): nome do banco de dados que será utilizado
        """
        engine = create_engine(f"sqlite:///{db_name}")

        try:
            endpoint = engine.connect()
            return endpoint

        except Exception as error:
            print(
                f"Falha na conexão. Favor verificar se o nome da fonte de dados e as credenciais estão corretas.\n {error}"
            )


class MySQLConnection:
    """
    Classe para interação com MySQL
    """

    @classmethod
    def connect(cls, db_name: str, port: int, server: str = "localhost") -> Connection:
        """
        Retorna um objeto de conexão do sqlalchemy

        Args:
        port (int): porta de conexão do servidor
        db_name (str): nome do banco de dados que será utilizado
        """
        try:
            with open(
                os.path.join(os.path.dirname(__file__), "credentials.json"), "r"
            ) as file:
                data = json.load(file)
                data = data["mysql"]

            user, password = data["user"], data["password"]

            engine = create_engine(
                f"mysql+mysqlconnector://{user}:{password}@{server}:{port}/{db_name}"
            )

            # create_engine("mysql+mysqlconnector://user:password@host/database")

            endpoint = engine.connect()
            return endpoint

        except Exception as error:
            print(
                f"Falha na conexão. Favor verificar se o nome da fonte de dados e as credenciais estão corretas.\n {error}"
            )


# Exemplo de uso:
# with PostgresConnection.connect(params["dsn_postgres"], params["port"]) as conn:
#     df = pd.read_sql(query, conn)
