#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     Luis Cañas-Díaz <lcanas@bitergia.com>
#

import collections
import colorama
import dateutil.parser
import elasticsearch as es
import elasticsearch_dsl as dsl
import json
import prettytable
import re
import sys

DESC_MSG = \
"""Life among ES indexes is tough so am I"""


class IndexWarrior:
    def __init__(self, client, term=None, date=None):
        self.client = client
        self.aliases = self.__cat_aliases()
        self.indices = self.__cat_indices()
        self.term = term

    def add_alias(self, indexes, alias):
        """ Point indexes to alias
        """
        try:
            self.client.indices.put_alias(indexes, alias)
            self.show_aliases()
        except es.exceptions.NotFoundError:
            print(' 404 buddy! Indexes not found.' )
            sys.exit(0)

    def delete_alias(self, indexes, alias):
        """ Delete indexes from alias
        """
        try:
            self.client.indices.delete_alias(indexes, alias)
            self.show_aliases()
        except es.exceptions.NotFoundError:
            print(' 404 buddy! Indexes not found.' )
            sys.exit(0)

    def delete(self, index, date_field, origin=None, older_than=None):
        """ Delete index name
        """
        s = dsl.Search(using=self.client, index=index)

        # don't get any fields in response, only get ids
        s = s.source([])

        if (not origin and not older_than):

            print(' Confirm you want to delele the entired index %s' % (index))
            self.__confirm_or_exit(' Are you sure?')

            try:
                code = self.client.indices.delete(index=index)
                if(code['acknowledged']):
                    print('Done.')

            except es.exceptions.NotFoundError:
                print(' 404 buddy! Indexes not found.' )
                sys.exit(0)

        else:

            if origin:
                s = s.query('match', origin={'query': origin, 'operator': 'and'}, _expand__to_dot=False)
            elif older_than:
                s = s.query('range', ** {date_field: {'gt': older_than}}, _expand__to_dot=False)
            elif (origin and older_than):
                s = s.query('match', origin={'query': origin, 'operator': 'and'}) \
                    .query('range', ** {date_field: {'gt': older_than}}, _expand__to_dot=False)
            try:
                print(' %s documens found with the condition:' % s.count())
                print(' - origin == %s\n - %s > %s ' % (origin, date_field, older_than), flush=True)
                self.__confirm_or_exit('\n Do you really want to remove them?\n')

                i = 0

                ### Variables for bulk requests
                bulk_size = 1000 # max. number of items allowed into the same bulk request
                bulk_items_list = []
                bulk_counter = 0
                total_items_to_remove = s.count()

                for hit in s.scan():
                    i += 1
                    bulk_counter += 1

                    delete_request_body = {
                        "delete" : {
                            "_index" : index,
                            "_type" : "items",
                            "_id" : hit.meta.id
                        }
                    }

                    bulk_items_list.append(json.dumps(delete_request_body))

                    # bulk requests
                    if (bulk_counter == bulk_size):
                        self.client.bulk("\n".join(bulk_items_list))
                        print(" %s/%s" % (i,total_items_to_remove))
                        bulk_counter = 0
                        bulk_items_list = []

                # last bulk
                if (bulk_counter != 0):
                    self.client.bulk("\n".join(bulk_items_list))
                    print(" %s/%s\n" % (i,total_items_to_remove))

                print('%s documents were removed' % i)

            except es.exceptions.NotFoundError:
                print(' 404 buddy! Indexes not found.' )
                sys.exit(0)

    def __read_indices(self):
        """ Return indexes dict after filtering using self.term if it exists"""
        res = []
        for entry in self.indices:
            if self.__matches_term(entry['index']):
                res.append(entry)
        return res

    def __enrich_index_data(self, avoid_dates=False):
        """ Add extra information about dates and aliases to the indexes.
        Sometimes we want a quicker view so dates can de skippped. """
        if not avoid_dates:
            self.__add_dates()
        self.__add_alias()

    def __matches_term(self, name):
        if (self.term == None or name.rfind(self.term) >= 0):
            return True
        else:
            return False

    def set_term(self, term):
        self.term = term

    def __cat_indices(self):
        """ Return /_cat/indices with collapsed fields for a better printing

        E.g:

        {'health': 'yellow', 'status': 'yellow/open', 'index': 'slack_cncf_170509_enriched_170821',
        'pri': '5', 'rep': '1', 'docs.count': '2251', 'docs.deleted': '16', 'store.size': '3.7mb',
        'pri.store.size': '3.7mb', 'rep/pri size/pri.size': '1/5 3.7mb/3.7mb'}
        """

        def __collapse_fields(indices_data):
            for i in indices_data:
                i['rep/pri size/pri.size'] = '%s/%s %s/%s' % (i['rep'], i['pri'], i['store.size'], i['pri.store.size'])
                i['status'] = '%s/%s' % (i['health'], i['status'])

        indices_data = self.client.cat.indices(format='json')
        __collapse_fields(indices_data)
        return indices_data

    def __cat_aliases(self):
        """ Return a list of dictionaries with the fields:
            alias, index, filter, routing.index, routing.search  """
        return self.client.cat.aliases(format='json')

    def __index_is_aliased(self, index):
        """ Returns True if any alias points to the index
        """
        for a in self.aliases:
            if a['index'] == index:
                return True
        return False

    def __get_max_date(self, index, field):
        try:
            s = dsl.Search(using=self.client, index=index)
            s.aggs.metric('max_date', 'max', field=field, _expand__to_dot=False)
            response = s.execute()
            #return (response.aggregations.max_date.value,
            #        response.aggregations.max_date.value_as_string)
            return response.aggregations.max_date.value_as_string
        except AttributeError:
            return None

    def __add_dates(self):
        """ Add inforation about the dates defined at 'date_fields' to object self.indices"""
        date_fields=['metadata__timestamp', 'metadata__updated_on', 'metadata__enriched_on']

        for i in self.__read_indices():
            for df in date_fields:
                i[df] = self.__get_max_date(i['index'], df)

    def __add_alias(self):
        for i in self.__read_indices():
            if not self.__matches_term(i['index']): continue
            if self.__index_is_aliased(i['index']):
                i['alias'] = True

    def __get_alias_filter(self):
        """ Return a list of aliases with extended info about their filters """
        alias_data = []
        indices = self.__read_indices()

        for index in indices:
            aliases_list_by_index = self.client.indices.get_alias(index['index'])
            for alias in aliases_list_by_index[index['index']]['aliases']:
                alias_filter = json.dumps(aliases_list_by_index[index['index']]['aliases'][alias], indent=4)
                alias_data.append({'index': index['index'], 'alias': alias, 'filter': alias_filter})
        return alias_data

    def show_aliases(self, show_filters=None):
        """ Print via stdout information about aliases (with/without extended info about filters) """
        headers = ['alias', 'index', 'filter']
        if not show_filters:
            aliases = self.aliases
        else:
            filters_data = self.__get_alias_filter()
            aliases = filters_data
        self.__print_table(headers, 'alias', aliases)

    def show_indices(self, show_less=False):
        """ Print via stdout information about indexes. By default this information is printed also with
            modification dates"""

        if not show_less:
            print(' Getting data from %s indexes, it may take a while \r' % len(self.indices), end='\r', flush=True)
        self.__enrich_index_data(show_less)

        if show_less:
            headers = ['status', 'index', 'alias', 'docs.count', 'docs.deleted', 'rep/pri size/pri.size']
        else:
            headers = ['status', 'index', 'alias', 'docs.count', 'docs.deleted', 'metadata__updated_on', 'metadata__timestamp', 'metadata__enriched_on', 'rep/pri size/pri.size']
        self.__print_indices_table(headers)

    def __expired_indices(self):
        """ Return list of expired indexes based on the information available in the self.indices
        object
        """
        res = []
        for i in self.__read_indices():
            if ('expired' in i.keys() and i['expired']):
                res.append(i['index'])
        res.sort()
        return res

    def drop(self, date):
        """ Prints via stdout the list of indexes to be removed and ask for confirmation before
        deleting them
        """
        if not date: sys.exit(1)

        print(' Getting data from %s indexes, it may take a while \r' % len(self.indices),
                end='\r', flush=True)
        self.__enrich_index_data()

        expiration_date = dateutil.parser.parse(date)
        self.__mark_expired_indexes(expiration_date)

        fields = ['status', 'index', 'alias', 'expired', 'docs.count',
                    'metadata__timestamp', 'metadata__updated_on']
        self.__print_indices_table(fields)

        if len(self.__expired_indices()) == 0:
            print('\n No indexes to be removed')
            sys.exit(0)

        print('The indexes marked to be remove are:')

        for i in self.__expired_indices():
            if self.__index_is_aliased(i):
                print(colorama.Fore.RED + colorama.Style.BRIGHT+ ' - %s -> WARNING! it is linked from an alias' % (i)
                        + colorama.Style.RESET_ALL)
            else:
                if i.rfind('enrich') > 0:
                    print(' - %s' % (i))
                else:
                    print(colorama.Fore.RED + colorama.Style.BRIGHT+ ' - %s -> WARNING! could be a raw index' % (i)
                        + colorama.Style.RESET_ALL)

        self.__confirm_or_exit('\nAre you sure?')
        self.__confirm_or_exit('Please, confirm you want to remove the index(es) above. Are you sure?')

        for item in self.__expired_indices():
            print('Deleting index %s' % (item))
            self.client.indices.delete(index=item)

    def __mark_expired_indexes(self, expiration_date):
        """ Iterate the indexes data and mark the expired indexes based on the
            expiration_date, which is a string parameter
        """
        for i in self.__read_indices():
            if i['metadata__timestamp']:
                if expiration_date >= dateutil.parser.parse(i['metadata__timestamp']):
                    i['expired'] = True

    def __print_indices_table(self, headers):
        """ Print via stdout the content of self.indices returned by self.__read_indices()
            for the headers passed by parameter. It also rename some columns for a better
            understanding
        """
        pretty_headers = [h.replace('docs.count', 'count') for h in headers]
        pretty_headers = [h.replace('docs.deleted', 'deleted') for h in pretty_headers]
        pretty_headers = [h.replace('alias', 'A') for h in pretty_headers]

        self.__print_table(headers, 'index', self.__read_indices())

    def __print_table(self, headers, sort_by, data):
        """ Print table using prettytable library. The information printed is based on the headers
            and data provided. Finally the table is sorted by sorty_by before printed.
            The output of some boolean and 1-character-length fields is replaced for a better
            understanding
        """
        t = prettytable.PrettyTable(headers)

        t.align = 'l'
        t.align['count']='r'
        t.align['deleted']='r'

        for batch in data:
            row = []
            for item in headers:
                try:
                    if isinstance(batch[item], bool):
                        if (item == 'alias' and batch[item] == True):
                            row.append('*')
                        elif (item == 'expired' and batch[item] == True):
                            row.append('YES')
                    else:
                        # before printing, we print '' instead of '-' to improve readability
                        if (batch[item] == '-'):
                            row.append('')
                        else:
                            row.append(batch[item])
                except KeyError:
                    row.append('')

            t.add_row(row)

        print(t.get_string(sortby=(sort_by), reversesort=False))

    def __check_indices_exist(self, index1, index2):
        """ """
        if not self.client.indices.exists(index1):
            print("[!] Index %s does not exist \n" % index1)
            sys.exit(0)
        if not self.client.indices.exists(index2):
            print("[!] Index %s does not exist \n" % index2)
            sys.exit(0)

    def compare_data(self, index_a, index_b, buckets=10, print_enabled=True):
        """Compare basic data from two indexes and print them via stdout. It returns
            True when the 'b' index looks candidate than the 'a' index and False in the
            opposite scenario
        """
        def __count_docs_per_field(myindex, field):
            s = dsl.Search(using=self.client, index=myindex)
            s.aggs.bucket(field, 'terms', field=field, size=buckets) \
                  .metric('n_docs', 'value_count', field=field)
            response = s.execute()
            return response.aggregations[field]

        def __count_docs(myindex):
            s = dsl.Search(using=self.client, index=myindex)
            response = s.execute()
            return response['hits']['total']

        self.__check_indices_exist(index_a, index_b)

        #FIXME we can't compare empty indexes
        docs_index_a = __count_docs(index_a)
        docs_index_b = __count_docs(index_b)

        if docs_index_a == 0 and docs_index_b == 0:
            return True
        elif docs_index_a == 0:
            return True
        elif docs_index_b == 0:
            return False
        # we know both are not empty at this point

        index_data = collections.OrderedDict()
        index_data['name'] = {}
        index_data['docs'] = {}
        index_data['metadata__timestamp'] = {}
        index_data['metadata__updated_on'] = {}
        index_data['affiliation'] = {}
        index_data['origin'] = {}

        index_data['name']['a'] = index_a
        index_data['name']['b'] = index_b

        index_data['docs']['a'] = docs_index_a
        index_data['docs']['b'] = docs_index_b

        au_values = self.__get_max_date(index_a, 'metadata__updated_on')
        index_data['metadata__updated_on']['a'] = au_values

        at_values = self.__get_max_date(index_a, 'metadata__timestamp')
        index_data['metadata__timestamp']['a'] = at_values

        bu_values = self.__get_max_date(index_b, 'metadata__updated_on')
        index_data['metadata__updated_on']['b'] = bu_values

        bt_values = self.__get_max_date(index_b, 'metadata__timestamp')
        index_data['metadata__timestamp']['b'] = bt_values

        a_aff = __count_docs_per_field(index_a, 'author_org_name')
        index_data['affiliation']['a'] = collections.OrderedDict()
        for item in a_aff:
            index_data['affiliation']['a'][item.key] = item.n_docs.value

        b_aff = __count_docs_per_field(index_b, 'author_org_name')
        index_data['affiliation']['b'] = collections.OrderedDict()
        for item in b_aff:
            index_data['affiliation']['b'][item.key] = item.n_docs.value

        a_docs = __count_docs_per_field(index_a, 'origin')
        index_data['origin']['a'] = collections.OrderedDict()
        for item in a_docs:
            index_data['origin']['a'][item.key] = item.n_docs.value

        b_docs = __count_docs_per_field(index_b, 'origin')
        index_data['origin']['b'] = collections.OrderedDict()
        for item in b_docs:
            index_data['origin']['b'][item.key] = item.n_docs.value

        if print_enabled:
            self.__print_comparison(index_data)

        #when replacing alias, the b index is supposed to be the fresh one.
        #we return True if b is fresher than a. False in the opposite scenario.
        if at_values[0] > bt_values[0]:
            return False

        return True

    def __print_comparison(self, data):
        """Print the result of comparing the old and new index via stdout"""

        def __dict_to_str(d):
            res = ''
            for item in d.keys():
                aux = '%s: %s\n' % (item, d[item])
                aux = __truncate_string(aux,45)
                res += aux
            return res

        def __truncate_string(name, lmax=45):
            minus_two = lmax - 2
            if len(name) > lmax:
                return ".."+name[-minus_two:]
            else:
                return name

        t = prettytable.PrettyTable(['data/index',data['name']['a'],data['name']['b']])
        t.align = 'l'

        for batch in data:
            if batch == 'name': continue
            row = []
            row.append(batch)
            for item in ['a','b']:
                cell_content = data[batch][item]
                if isinstance(cell_content, dict):
                    cell_content = __dict_to_str(cell_content)
                row.append(cell_content)
            t.add_row(row)
            t.add_row(['','',''])

        print(t.get_string(reversesort=False))

    def switch(self, old_index, new_index):
        """Get all the aliases linked to the old_index and switch them for the
            new_index"""
        looksgood = self.compare_data(old_index, new_index)

        if looksgood is False:
            wrn_msg = '[WARNING] The index to be unlinked from the alias has more recent metadata__timestamp time'
            print(colorama.Fore.RED + '\n'+ wrn_msg + colorama.Style.RESET_ALL)
            answer = self.__yes_or_no('Are you sure you want to switch the aliases?')
            if answer is False:
                print('Exiting ..\n')
                sys.exit(0)
        self.__switch_aliases(old_index, new_index)
        self.show_aliases()

    def __switch_aliases(self, old_index, new_index):
        """Get all the aliases linked to the old_index and switch them for the
            new_index"""
        target_aliases, switched_aliases = ([] for i in range(2))
        for a in self.__get_alias_filter():
            if a['index'] == old_index:
                target_aliases.append({a['alias']: a['filter']})

        for alias in target_aliases:
            for t in alias:
                switched_aliases.append(t)
                self.client.indices.delete_alias(index=old_index, name=t)
                self.client.indices.put_alias(index=new_index, name=t, body=alias[t])

        print("\nAliases %s point now to %s" % (','.join(switched_aliases), new_index))

        self.client.indices.refresh(index=new_index)
        print("Index %s refreshed\n" % (new_index))

    def __confirm_or_exit(self, question):
        reply = str(input(question+' (y/n): ')).lower().strip()
        if reply[0] == 'y':
            return True
        else:
            sys.exit(0)

    def autoupdate(self, aliases):
        """ Get all the indexes linked to a list of given aliases and update those
        alias if fresher and bigger index is found.

        The name of the index is used in order to find candidate versions. This is prone
        to human errors so besides that the modification dates of the indexes are
        compared. The final check is the number of docs. This method won't switch
        the index aliased if the number of documents of the new version is smaller.

        There is a current restriction related to the way indexes are being used
        in production. This approach expects the relationship index-alias to be 1:n
        """
        raw_pattern = re.compile('[a-z]+\_[a-z]+\_[0-9]+[a-z]*$')
        enriched_pattern = re.compile('[a-z]+\_[a-z]+\_[0-9]+[a-z]*\_[a-z]+\_[0-9]+[a-z]*$')

        def __index_aliased(alias):
            """Returns the index name pointed by a given alias.

            Restriction: only works for 1 alias
            """
            for ele in self.aliases:
                if ele['alias'] == alias:
                    return ele['index']

        def __get_latest_index_name(index_name):
            """ Returns the name of the index with a major version number based on
            the prefix of the index name given as unique argument
            """
            pos = index_name.index('_', index_name.index('_') + 1 )
            index_prefix = index_name[:pos]

            if enriched_pattern.match(index_name):
                index_type = 'enriched'
            elif raw_pattern.match(index_name):
                index_type = 'raw'

            indices = []
            for item in self.indices:
                iname = item['index']
                if iname.rfind(index_prefix) >= 0:
                    if index_type =='raw':
                        if raw_pattern.match(iname):
                            indices.append(iname)
                    elif index_type == 'enriched':
                        if enriched_pattern.match(iname):
                            indices.append(iname)

            indices.sort()
            return indices[-1]

        def __number_of_documents(index_name):
            """ Return number of documents for a given index name"""
            docs = 0
            for item in self.indices:
                if item['index'] == index_name:
                    docs = int(item['docs.count'])

            return docs

        def __show_autoupdate_applied(aliases, indice, index_docs, candidate, candidate_docs):
            __show_autoupdate_status(aliases, indice, index_docs, candidate, candidate_docs, 'done')

        def __show_autoupdate_not_applied(aliases, indice, index_docs, candidate, candidate_docs):
            __show_autoupdate_status(aliases, indice, index_docs, candidate, candidate_docs, 'blocked')

        def __show_autoupdate_up_to_date(aliases, indice, index_docs):
            __show_autoupdate_status(aliases, indice, index_docs, None, None, 'uptodate')

        def __show_autoupdate_empty(aliases, indice, index_docs, candidate, candidate_docs):
            __show_autoupdate_status(aliases, indice, index_docs, candidate, candidate_docs, 'empty')

        def __show_autoupdate_status(aliases, indice, index_docs, candidate, candidate_docs, status):
            """ Print the status of the index found for the given aliases. Remember we can have more than an alias
            pointing to an index. E.g git and git_author
            """
            print('alias: %s' % str(aliases))
            print('   current:\t%s (%s docs) ' % (indice, index_docs))
            if status == 'done':
                print('   found:\t%s (%s docs)' % (candidate, candidate_docs))
                print('   status:\t', end='')
                print(colorama.Fore.GREEN + 'change applied' + colorama.Style.RESET_ALL)
            elif status == 'blocked':
                print('   found:\t%s (%s docs)' % (candidate, candidate_docs))
                print('   status:\t', end='')
                print(colorama.Fore.RED + 'warning: more recent data but fewer documents, it won\'t be changed' + colorama.Style.RESET_ALL)
            elif status == 'uptodate':
                print('   status:\talias is up to date')
            elif status == 'empty':
                print('   found:\t%s (%s docs)' % (candidate, candidate_docs))
                print('   status:\t', end='')
                print(colorama.Fore.RED + 'warning: new version of index found with no data' + colorama.Style.RESET_ALL)

        def __search_indexes(aliases):
            """ Return dictionary with index:[alias] based on a given list of aliases
            """
            index_aliases = {}
            for a in aliases:
                index = __index_aliased(a)
                if not index:
                    continue

                if index in index_aliases.keys():
                    index_aliases[index].append(a)
                else:
                    index_aliases[index] = [a]
            return index_aliases

        index_aliases = __search_indexes(aliases)

        for indice in index_aliases:
            candidate = __get_latest_index_name(indice)

            index_docs = 0
            candidate_docs = 0

            index_docs = __number_of_documents(indice)
            candidate_docs = __number_of_documents(candidate)

            if (indice == candidate):
                # current alised index is the one with a bigger version name
                __show_autoupdate_up_to_date(index_aliases[indice], indice, index_docs)
            else:
                if self.compare_data(indice, candidate, print_enabled=False):
                    #candidate has fresher data
                    if candidate_docs >= index_docs:
                        self.__switch_aliases(indice, candidate)
                        __show_autoupdate_applied(index_aliases[indice], indice, index_docs, candidate, candidate_docs)
                    else:
                        # candidate has fresher data but less documents
                        __show_autoupdate_not_applied(index_aliases[indice], indice, index_docs, candidate, candidate_docs)
                elif candidate_docs == 0:
                    #candidate is empty
                    __show_autoupdate_empty(index_aliases[indice], indice, index_docs, candidate, candidate_docs)
