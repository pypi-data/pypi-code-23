#
#   Copyright 2018 University of Lancaster
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import asyncio
import contextlib
import json
import logging
import time

import jquery_querybuilder_psycopg2
import psycopg2
import websockets

from .errors import ClientLeakableError
from .query_rules_rule_set_parser import QueryRulesRuleSetParser


class Session:
    def __init__(self, endpoint, websocket):
        self.endpoint = endpoint
        self.websocket = websocket

        self.logger = SessionLoggerAdapter(
            logging.getLogger(), {'session': self})

        self.jwt_issuer_claims_set = {}
        self.refresh_jwt_issuer_claims_set_json()

        self.logger.info("Created new session")

    async def websocket_handler(self):
        self.send_database_readiness(self.endpoint.database_listener.ready)

        while True:
            try:
                wspg_msg_json = await self.websocket.recv()

            except websockets.ConnectionClosed as e:
                msg = "Websocket closed with code {}, reason {!r}"
                self.logger.info(msg.format(e.code, e.reason))
                return

            try:
                wspg_msg = json.loads(wspg_msg_json)

                if not isinstance(wspg_msg, dict):
                    raise TypeError("wspg_msg must be a dict")

                _type = wspg_msg.pop('type')
                if not isinstance(_type, str):
                    raise TypeError("type must be a str")

                _id = wspg_msg.pop('id')
                if not isinstance(_id, str):
                    raise TypeError("id must be a str")

                asyncio.ensure_future(self.wspg_handler(_type, _id, wspg_msg))

            except Exception as e:
                msg = "Exception whilst parsing WSPG message"

                self.logger.warning("{}: {!r}".format(msg, e))

                await self.websocket.close(4002, "Unparsable message")

    async def wspg_handler(self, _type, _id, wspg_msg):
        try:
            handler_result = await self._wspg_handler(_type, wspg_msg)

            if not isinstance(handler_result, JsonLiteral):
                handler_result = json.dumps(handler_result)

            # Hand craft the JSON because the result is already json-encoded
            succeeded_json = '{{"type": "succeeded", "id": {_id}, "result": {result}}}'.format(
                _id=json.dumps(_id),
                result=handler_result)

            await self.websocket.send(succeeded_json)

        except ClientLeakableError as e:
            msg = "Error whilst handling WSPG message"

            if self.endpoint.application.args.verbose:
                self.logger.exception(msg)
            else:
                self.logger.warning("{}: {!r}".format(msg, e))

            failed_json = json.dumps({
                'type': "failed",
                'id': _id,
                'reason': str(e)})

            await self.websocket.send(failed_json)

        except Exception as e:
            msg = "Exception whilst handling WSPG message"

            if self.endpoint.application.args.verbose:
                self.logger.exception(msg)
            else:
                self.logger.warning("{}: {!r}".format(msg, e))

            failed_json = json.dumps({
                'type': "failed",
                'id': _id,
                'reason': "Internal server error"})

            await self.websocket.send(failed_json)

    def send_database_readiness(self, ready):
        msg_json = json.dumps({
            'type': "database-readiness",
            'ready': ready})

        asyncio.ensure_future(self.websocket.send(msg_json))

    def send_notification(self, notification):
        msg_json = json.dumps({
            'type': "notification",
            'channel': notification.channel,
            'payload': notification.payload})

        asyncio.ensure_future(self.websocket.send(msg_json))

    async def _wspg_handler(self, _type, wspg_msg):
        method_name = "handle_{}".format(_type.replace('-', '_'))

        try:
            handler = getattr(self, method_name)
        except AttributeError:
            raise ClientLeakableError("Message type {!r} is not defined".format(_type)) from None

        with call_timing_logger(self.logger, "WSPG handler"):
            return await handler(wspg_msg)

    async def handle_select(self, wspg_msg):
        relation_sql = extract_wspg_msg_relation_sql(wspg_msg)
        query_rules = extract_wspg_msg_query_rules(wspg_msg)
        returning_columns = extract_wspg_msg_returning_columns(wspg_msg)
        order = extract_wspg_msg_order(wspg_msg)
        limit = extract_wspg_msg_limit(wspg_msg)

        return await self._select(
            relation_sql, query_rules, returning_columns, order, limit)

    async def _select(self, relation_sql, query_rules, returning_columns, order, limit):
        fetch_result = True

        if returning_columns is None:
            columns_sql = psycopg2.sql.SQL("*")
        elif returning_columns == []:
            columns_sql = psycopg2.sql.SQL("1")
            fetch_result = False
        else:
            columns_sql = psycopg2.sql.SQL(", ").join(
                [psycopg2.sql.Identifier(column) for column in returning_columns])

        if query_rules:
            where_sql = psycopg2.sql.SQL("WHERE {}").format(query_rules)
        else:
            where_sql = psycopg2.sql.SQL("")

        if order:
            order_sqls = []
            for item in order:
                item_column = psycopg2.sql.Identifier(item['column'])

                if item['direction'] == 'ascending':
                    item_direction = psycopg2.sql.SQL("ASC")
                else:
                    item_direction = psycopg2.sql.SQL("DESC")

                if item['nulls'] == 'first':
                    item_nulls = psycopg2.sql.SQL("FIRST")
                else:
                    item_nulls = psycopg2.sql.SQL("LAST")

                order_sqls.append(
                    psycopg2.sql.SQL("{column} {direction} NULLS {nulls}").format(
                        column=item_column,
                        direction=item_direction,
                        nulls=item_nulls))

            order_sql = psycopg2.sql.SQL("ORDER BY {}").format(
                psycopg2.sql.SQL(", ").join(order_sqls))
        else:
            order_sql = psycopg2.sql.SQL("")

        if limit:
            limit_sql = psycopg2.sql.SQL("LIMIT {}").format(
                psycopg2.sql.Literal(limit))
        else:
            limit_sql = psycopg2.sql.SQL("")

        select_sql = psycopg2.sql.SQL("SELECT {columns} FROM {relation} {where} {order} {limit}").format(
            columns=columns_sql, relation=relation_sql, where=where_sql,
            order=order_sql, limit=limit_sql)

        return await self._execute_sql(select_sql, fetch_result)

    async def handle_insert(self, wspg_msg):
        relation_sql = extract_wspg_msg_relation_sql(wspg_msg)
        rows = extract_wspg_msg_rows(wspg_msg)
        returning_columns = extract_wspg_msg_returning_columns(wspg_msg)

        return await self._insert(relation_sql, rows, returning_columns)

    async def _insert(self, relation_sql, rows, returning_columns):
        columns = set()
        for row in rows:
            columns.update(row)

        columns = list(columns)
        columns_sql = psycopg2.sql.SQL(", ").join(
            [psycopg2.sql.Identifier(column) for column in columns])

        values_sqls = []

        for row in rows:
            row_values = []

            for column in columns:
                if column in row:
                    value = psycopg2.sql.Literal(row[column])
                else:
                    value = psycopg2.sql.SQL("DEFAULT")

                row_values.append(value)

            values_sqls.append(psycopg2.sql.SQL("({})").format(
                psycopg2.sql.SQL(", ").join(row_values)))

        values_sql = psycopg2.sql.SQL(", ").join(values_sqls)

        fetch_result = True

        if returning_columns is None:
            returning_sql = psycopg2.sql.SQL("RETURNING *")
        elif returning_columns == []:
            returning_sql = psycopg2.sql.SQL("")
            fetch_result = False
        else:
            returning_sql = psycopg2.sql.SQL("RETURNING {}").format(
                psycopg2.sql.SQL(", ").join(
                    [psycopg2.sql.Identifier(column) for column in returning_columns]))

        insert_sql = psycopg2.sql.SQL("INSERT INTO {relation} ({columns}) VALUES {values} {returning}").format(
            relation=relation_sql, columns=columns_sql,
            values=values_sql, returning=returning_sql)

        return await self._execute_sql(insert_sql, fetch_result)

    async def handle_update(self, wspg_msg):
        relation_sql = extract_wspg_msg_relation_sql(wspg_msg)
        updates = extract_wspg_msg_updates(wspg_msg)
        query_rules = extract_wspg_msg_query_rules(wspg_msg)
        returning_columns = extract_wspg_msg_returning_columns(wspg_msg)

        return await self._update(relation_sql, updates, query_rules, returning_columns)

    async def _update(self, relation_sql, updates, query_rules, returning_columns):
        updates_sqls = []
        for column, value in updates.items():
            updates_sql = psycopg2.sql.SQL("{}={}").format(
                psycopg2.sql.Identifier(column), psycopg2.sql.Literal(value))
            updates_sqls.append(updates_sql)

        updates_sql = psycopg2.sql.SQL(", ").join(updates_sqls)

        if query_rules:
            where_sql = psycopg2.sql.SQL("WHERE {}").format(query_rules)
        else:
            where_sql = psycopg2.sql.SQL("")

        fetch_result = True

        if returning_columns is None:
            returning_sql = psycopg2.sql.SQL("RETURNING *")
        elif returning_columns == []:
            returning_sql = psycopg2.sql.SQL("")
            fetch_result = False
        else:
            returning_sql = psycopg2.sql.SQL("RETURNING {}").format(
                psycopg2.sql.SQL(", ").join(
                    [psycopg2.sql.Identifier(column) for column in returning_columns]))

        update_sql = psycopg2.sql.SQL("UPDATE {relation} SET {updates} {where} {returning}").format(
            relation=relation_sql, updates=updates_sql, where=where_sql,
            returning=returning_sql)

        return await self._execute_sql(update_sql, fetch_result)

    async def handle_delete(self, wspg_msg):
        relation_sql = extract_wspg_msg_relation_sql(wspg_msg)
        query_rules = extract_wspg_msg_query_rules(wspg_msg)

        return await self._delete(relation_sql, query_rules)

    async def _delete(self, relation_sql, query_rules):
        if query_rules:
            where_sql = psycopg2.sql.SQL("WHERE {}").format(query_rules)
        else:
            where_sql = psycopg2.sql.SQL("")

        delete_sql = psycopg2.sql.SQL("DELETE FROM {relation} {where}").format(
            relation=relation_sql, where=where_sql)

        return await self._execute_sql(delete_sql, False)

    async def handle_listen(self, wspg_msg):
        channel = extract_wspg_msg_channel(wspg_msg)

        await self.endpoint.database_listener.listen(self, channel)

    async def handle_unlisten(self, wspg_msg):
        channel = extract_wspg_msg_channel(wspg_msg)

        await self.endpoint.database_listener.unlisten(self, channel)

    async def handle_apply_jwt(self, wspg_msg):
        issuer = extract_wspg_msg_issuer(wspg_msg)
        token = extract_wspg_msg_token(wspg_msg)

        await self._apply_jwt(issuer, token)

    async def _apply_jwt(self, issuer, token):
        jwt_issuer = self.endpoint.application.jwt_issuers.get(issuer)
        if not jwt_issuer:
            raise ClientLeakableError("JWT issuer {!r} is not defined".format(issuer))

        if token is None:
            if issuer in self.jwt_issuer_claims_set:
                del self.jwt_issuer_claims_set[issuer]
                self.refresh_jwt_issuer_claims_set_json()

            return

        claims_set = jwt_issuer.decode(token)

        self.jwt_issuer_claims_set[issuer] = claims_set
        self.refresh_jwt_issuer_claims_set_json()

    def refresh_jwt_issuer_claims_set_json(self):
        self.jwt_issuer_claims_set_json = json.dumps(self.jwt_issuer_claims_set)

    async def _execute_sql(self, sql, fetch_result=True):
        try:
            async with self.endpoint.db_pool.acquire() as connection:
                async with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    return await self._execute_sql_on_cursor(
                        cursor, sql, fetch_result)

        except psycopg2.Error as e:
            if e.diag.message_primary:
                db_msg = e.diag.message_primary
                if e.diag.message_detail:
                    db_msg += ": " + e.diag.message_detail
            else:
                db_msg = str(e).splitlines()[0]

            raise ClientLeakableError("Database error: {}".format(db_msg)) from e

    async def _execute_sql_on_cursor(self, cursor, sql, fetch_result):
        jwt_claims_sql = psycopg2.sql.SQL("SET wspg.jwt_issuer_claims_set = {}").format(
            psycopg2.sql.Literal(self.jwt_issuer_claims_set_json))

        await cursor.execute(jwt_claims_sql)

        if fetch_result:
            sql = psycopg2.sql.SQL("WITH results AS ({}) SELECT COALESCE(jsonb_agg(to_jsonb(results)), '[]'::jsonb)::text AS result FROM results").format(sql)

        await cursor.execute(sql)

        if fetch_result:
            return JsonLiteral((await cursor.fetchall())[0]['result'])


class SessionLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        template = "[{path}:{remote_address}] {msg}"
        msg = template.format(
            path=self.extra['session'].endpoint.path,
            remote_address=self.extra['session'].websocket.remote_address,
            msg=msg)
        return msg, kwargs


def extract_wspg_msg_relation_sql(wspg_msg):
    relation = wspg_msg.get('relation')

    if not isinstance(relation, str) or not relation:
        raise ClientLeakableError("relation must be a string")

    relation_sql = psycopg2.sql.Identifier(relation)

    schema = wspg_msg.get('schema')
    if schema is not None:
        if not isinstance(schema, str):
            raise ClientLeakableError("schema must be a string or null")

        schema_sql = psycopg2.sql.Identifier(schema)
        relation_sql = psycopg2.sql.SQL("{}.{}").format(
            schema_sql, relation_sql)

    return relation_sql


def extract_wspg_msg_query_rules(wspg_msg):
    query_rules = wspg_msg.get('query-rules')

    if query_rules is None:
        return

    try:
        query_rules = QueryRulesRuleSetParser(query_rules)
    except jquery_querybuilder_psycopg2.ParseError as e:
        raise ClientLeakableError("Failed to parse query-rules: {}".format(e))

    return query_rules


def extract_wspg_msg_returning_columns(wspg_msg):
    returning_columns = wspg_msg.get('returning-columns')

    if returning_columns is None:
        return

    if not isinstance(returning_columns, list):
        raise ClientLeakableError("returning-columns must be a list or null")

    for item in returning_columns:
        if not isinstance(item, str):
            raise ClientLeakableError("returning-columns list items must be strings")

    return returning_columns


def extract_wspg_msg_order(wspg_msg):
    order = wspg_msg.get('order')

    if order is None:
        return

    if not isinstance(order, list):
        raise ClientLeakableError("order must be a list or null")

    if len(order) < 1:
        raise ClientLeakableError("order list must not be empty")

    for item in order:
        if not isinstance(item, dict):
            raise ClientLeakableError("order list items must be dictionaries")

        item_column = item.get('column')
        if not isinstance(item_column, str) or not item_column:
            raise ClientLeakableError("column must be a string")

        item_direction = item.get('direction')
        if item_direction is None:
            item['direction'] = 'ascending'
        else:
            if not isinstance(item_direction, str) or not item_direction:
                raise ClientLeakableError("direction must be a string or null")

            if item_direction not in ('ascending', 'descending'):
                raise ClientLeakableError("direction must be one of \"ascending\", \"descending\"")

        item_nulls = item.get('nulls')
        if item_nulls is None:
            item['nulls'] = "last" if item_direction == "ascending" else "first"
        else:
            if not isinstance(item_nulls, str) or not item_nulls:
                raise ClientLeakableError("nulls must be a string or null")

            if item_nulls not in ('first', 'last'):
                raise ClientLeakableError("nulls must be one of \"first\", \"last\"")

    return order


def extract_wspg_msg_limit(wspg_msg):
    limit = wspg_msg.get('limit')

    if limit is None:
        return

    if not isinstance(limit, int):
        raise ClientLeakableError("limit must be an integer or null")

    if limit < 1:
        raise ClientLeakableError("limit must be a non-zero positive integer")

    return limit


def extract_wspg_msg_rows(wspg_msg):
    rows = wspg_msg.get('rows')

    if not isinstance(rows, list):
        raise ClientLeakableError("rows must be a list")

    if len(rows) < 1:
        raise ClientLeakableError("rows list must not be empty")

    for item in rows:
        if not isinstance(item, dict):
            raise ClientLeakableError("rows list items must be dictionaries")

        if len(item) < 1:
            raise ClientLeakableError("row dictionary must not be empty")

    return rows


def extract_wspg_msg_updates(wspg_msg):
    updates = wspg_msg.get('updates')

    if not isinstance(updates, dict):
        raise ClientLeakableError("updates must be a dictionary")

    if len(updates) < 1:
        raise ClientLeakableError("updates must not be empty")

    return updates


def extract_wspg_msg_channel(wspg_msg):
    channel = wspg_msg.get('channel')

    if not isinstance(channel, str) or not channel:
        raise ClientLeakableError("channel must be a string")

    return channel


def extract_wspg_msg_issuer(wspg_msg):
    issuer = wspg_msg.get('issuer')

    if not isinstance(issuer, str) or not issuer:
        raise ClientLeakableError("issuer must be a string")

    return issuer


def extract_wspg_msg_token(wspg_msg):
    token = wspg_msg.get('token')

    if token is None:
        return

    if not isinstance(token, str) or not token:
        raise ClientLeakableError("token must be a string or null")

    return token


@contextlib.contextmanager
def call_timing_logger(logger, prefix):
    start_time = time.time()
    try:
        yield
    finally:
        call_time = time.time() - start_time
        msg = "{} took {:.6f}s"
        logger.debug(msg.format(prefix, call_time))


class JsonLiteral(str):
    pass
