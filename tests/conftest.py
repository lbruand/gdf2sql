import time
import uuid

import pytest
from pytest_postgres.plugin import create_container, catch_docker_error
import psycopg2


def check_container_isup(postgis_params):
    delay_base = 0.2
    version_query = "select version();"

    for i in range(10):
        try:
            with psycopg2.connect(**postgis_params) as connection:
                with connection.cursor() as cur:
                    cur.execute(version_query)
            break
        except psycopg2.Error:
            time.sleep(delay_base * (1 << i))
    else:
        pytest.fail("Failed to connect to postgresql in container")


@pytest.fixture(scope='session')
def postgis_server(docker, request):
    postgis_host = request.config.getoption('--pg-host')
    postgis_port = request.config.getoption('--pg-port')
    postgis_user = request.config.getoption('--pg-user')
    postgis_password = request.config.getoption('--pg-password')
    postgis_database = request.config.getoption('--pg-database')

    postgis_name = request.config.getoption('--pg-name')
    postgis_image = 'postgis/postgis'
    postgis_resuse = request.config.getoption('--pg-reuse')
    postgis_network = request.config.getoption('--pg-network')

    network = None
    container = None

    if not postgis_host:
        if not postgis_name:
            postgis_name = f'db-{str(uuid.uuid4())}'
    environ_params = {
        'POSTGRES_PASSWORD': postgis_password,
        'POSTGRES_DB': postgis_database,
        'POSTGRES_USER': postgis_user,
    }

    container = create_container(docker=docker,
                                 image=postgis_image,
                                 name=postgis_name,
                                 ports={'5432/tcp': None},
                                 network=postgis_network,
                                 env_params=environ_params)
    container.start()
    container.reload()

    network = container.attrs['NetworkSettings']

    if postgis_network:
        net = network['Networks'][postgis_network]
        postgis_host = net['IPAddress']
    else:
        ports = network['Ports']
        postgis_host = 'localhost'
        first_binding, *_ = ports['5432/tcp']
        postgis_port = first_binding['HostPort']

    postgis_params = {
        'host': postgis_host,
        'port': postgis_port,
        'database': postgis_database,
        'user': postgis_user,
        'password': postgis_password
    }

    try:
        check_container_isup(postgis_params)
        yield {
            'network': network,
            'params': postgis_params
        }
    finally:
        if not postgis_resuse and container:
            with catch_docker_error():
                container.kill()
            with catch_docker_error():
                container.remove()

