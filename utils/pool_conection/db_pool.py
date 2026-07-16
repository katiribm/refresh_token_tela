from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool


class ConnectionPool:
    _instance = None
    _engine = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConnectionPool, cls).__new__(cls)
        return cls._instance

    def initialize(self, db_params):
        if not self._engine:
            # Monta a string de conexão do PostgreSQL
            db_url = (
                f"postgresql+psycopg2://{db_params['user']}:{db_params['password']}"
                f"@{db_params['host']}:{db_params['port']}/{db_params['db_name']}"
            )

            # Cria o 'engine' que gerencia o pool
            # pool_size = 4 -> O número máximo de conexões no pool (igual ao número de workers)
            # max_overflow = 2 -> Permite criar 2 conexões extras temporariamente se o pool estiver cheio
            self._engine = create_engine(
                db_url, poolclass=QueuePool, pool_size=8, max_overflow=2
            )
            print("Pool de conexões inicializado.")

    def get_connection(self):
        # Pede uma conexão do pool
        return self._engine.connect()


# Exemplo de como usaria essa classe no script principal
# Supondo que 'params' contém user, password, host, etc.
# db_pool = ConnectionPool()
# db_pool.initialize(params)
