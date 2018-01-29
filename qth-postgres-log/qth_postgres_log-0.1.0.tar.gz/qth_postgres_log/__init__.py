import asyncio
import asyncpg
import qth
import argparse
import json

from .version import __version__

async def init_tables(loop, pg_client):
    """Create all required database tables/functions."""
    async with pg_client.transaction():
        await pg_client.execute("""
            CREATE TABLE IF NOT EXISTS qth_paths(
                path_id SERIAL PRIMARY KEY,
                path TEXT NOT NULL UNIQUE
            )
        """)
        await pg_client.execute("""
            CREATE TABLE IF NOT EXISTS qth_log(
                log_id SERIAL PRIMARY KEY,
                path_id SERIAL REFERENCES qth_paths,
                value JSONB,
                time TIMESTAMP NOT NULL
            )
        """)
        await pg_client.execute("""
            CREATE OR REPLACE FUNCTION qth_path_to_id(desired_path TEXT) RETURNS INTEGER AS $$
            DECLARE
                id INTEGER;
            BEGIN
                id := (SELECT path_id FROM qth_paths
                       WHERE path = desired_path
                       LIMIT 1);
                IF id IS NULL THEN
                    INSERT INTO qth_paths(path)
                    VALUES (desired_path)
                    RETURNING path_id INTO id;
                END IF;
                RETURN id;
            END;
            $$ LANGUAGE plpgsql
        """)


async def async_main(loop, qth_host, qth_port,
                     **pg_kwargs):
    qth_client = qth.Client("qth_postgres_log", loop=loop,
                            host=qth_host, port=qth_port)
    pg_client = await asyncpg.connect(
        user="jonathan", password="", database="jonathan")
    
    await init_tables(loop, pg_client)
    
    pglock = asyncio.Lock(loop=loop)
    
    async def on_message(topic, data):
        async with pglock:
            if data is not qth.Empty:
                data = json.dumps(data)
            else:
                data = None
            await pg_client.execute("""
                INSERT INTO qth_log(path_id, value, time)
                VALUES (qth_path_to_id($1), $2, CURRENT_TIMESTAMP)
            """, topic, data)
    
    await qth_client.subscribe("#", on_message)
    
    return qth_client, pg_client


async def async_shutdown(loop, qth_client, pg_client):
    await qth_client.close()
    await pg_client.close()


def main():
    parser = argparse.ArgumentParser(
        description="A simple PostgreSQL-based logger for Qth.")
    parser.add_argument("--version", "-V", action="version",
                        version="%(prog)s {}".format(__version__))
    parser.add_argument("--qth-host",
                        default=None,
                        help="The hostname of the MQTT broker.")
    parser.add_argument("--qth-port",
                        default=None, type=int,
                        help="The port number for the MQTT broker.")
    parser.add_argument("--postgres-host", default=None,
                        help="The PostgreSQL server hostname.")
    parser.add_argument("--postgres-user", default=None,
                        help="The PostgreSQL username.")
    parser.add_argument("--postgres-password", default=None,
                        help="The PostgreSQL password.")
    parser.add_argument("--postgres-database", default=None,
                        help="The PostgreSQL database.")
    args = parser.parse_args()
    
    loop = asyncio.get_event_loop()
    try:
        qth_client, pg_client = loop.run_until_complete(async_main(
            loop,
            qth_host=args.qth_host,
            qth_port=args.qth_port,
            user=args.postgres_user,
            password=args.postgres_password,
            database=args.postgres_database,
            ))
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(async_shutdown(loop, qth_client, pg_client))


if __name__ == "__main__":
    main()
