import json
import time
from threading import Thread

import animation
import requests
from enum import Enum

from utils import Formatter


class Action(Enum):
    read = 1
    check = 2
    stop = 3
    monitor = 4


class ActionHandler():
    @staticmethod
    def action(action, namespace, host, slack_end_point):
        if action is Action.read:
            if namespace.read is not None and len(namespace.read) > 0:
                NPhandler.get_notebook(host, namespace.read)
            else:
                NPhandler.get_notebooks(host)
        if action is Action.check:
            NPhandler.check_running_paragraphs(host)
        if action is Action.stop:
            NPhandler.stop_running_paragraphs(host)
        if action is Action.monitor:
            NPhandler.monitor_paragraphs(host, slack_end_point)
        print '\nExecution completed\n'

class NPhandler():
    @staticmethod
    def get_notebook(end_point, id):
        json_res = ApiCallHandler.get_api_call(end_point + "/" + str(id))
        print json.dumps(json_res['body']['paragraphs'], indent=4, sort_keys=True)
        return json_res

    @staticmethod
    def get_notebooks(end_point):
        json_res = ApiCallHandler.get_api_call(end_point)
        print json.dumps(json_res['body'], indent=4, sort_keys=True)

    @staticmethod
    def check_running_paragraphs(end_point):
        json_res = ApiCallHandler.get_api_call(end_point)
        ids = [n['id'] for n in json_res['body']]
        notebooks = NPhandler._threaded_find_running_notebooks_paragraphs(end_point, 10, ids)
        if len(notebooks) > 0:
            print 'Found running paragraphs: ' + str([' nbId: '+ str(i[0]) + " pId: " + str(i[1]) for i in notebooks])
            return notebooks
        else:
            print '\nNo running paragraphs'
            return []

    @staticmethod
    def stop_running_paragraphs(end_point):
        running_notebooks = NPhandler.check_running_paragraphs(end_point)
        if running_notebooks is None or len(running_notebooks) == 0:
            print 'Nothing to stop'
            return 0
        k = 1
        while len(running_notebooks) > 0 and k < 100:
            for i in running_notebooks:
                ApiCallHandler.delete_api_call(end_point + '/job/' + str(i[0]) + '/' + str(i[1]), k)
                running_notebooks.remove(i)
                time.sleep(3)
                NPhandler._find_running_notebooks_paragraphs(end_point, [i[0]], running_notebooks)
                k += 1
        if len(running_notebooks) == 0:
            print 'Finally stopped all paragraphs with ' + str(k) + ' attempts'
        else:
            print 'Unfortunately ' + str(k) + ' attempts are not enough'

    @staticmethod
    @animation.wait('bar')
    def monitor_paragraphs(end_point, slack_end_point):
        running_notebooks = NPhandler.check_running_paragraphs(end_point)
        if running_notebooks is None or len(running_notebooks) == 0:
            print 'Nothing to Monitor'
            return 0
        time.sleep(5)
        running_notebooks = set(running_notebooks)
        count = len(running_notebooks)
        while count > 0:
            updated_running_notebooks = set(NPhandler.check_running_paragraphs(end_point))
            if updated_running_notebooks > running_notebooks:
                new_paragraphs = updated_running_notebooks - running_notebooks
                print 'New paragraphs are running: ' + str([' nbId: '+ str(i[0]) + " pId: " + str(i[1]) for i in new_paragraphs])
                running_notebooks.update(updated_running_notebooks)
            else:
                terminated_notebook_paragraphs = running_notebooks - updated_running_notebooks
                if len(terminated_notebook_paragraphs) > 0:
                    status_old_running_paragraphs = NPhandler._get_status_notebooks_paragraph(end_point,
                                                                                              terminated_notebook_paragraphs)
                    slack_payload = Formatter.format_slack_message(status_old_running_paragraphs)
                    if ApiCallHandler.post_api_call(slack_end_point, slack_payload):
                        print 'Sent message to slack'
                running_notebooks = updated_running_notebooks
            count = len(running_notebooks)
            time.sleep(5)
            print 'Current running paragraphs ' + str([' nbId: '+ str(i[0]) + " pId: " + str(i[1]) for i in running_notebooks])

    @staticmethod
    def _threaded_find_running_notebooks_paragraphs(end_point, nthreads, id_range):
        notebooks_paragraphs = []
        threads = []
        for i in range(nthreads):
            ids = id_range[i::nthreads]
            t = Thread(target=NPhandler._find_running_notebooks_paragraphs,
                       args=(end_point, ids, notebooks_paragraphs))
            threads.append(t)
        [t.start() for t in threads]
        [t.join() for t in threads]
        return notebooks_paragraphs

    @staticmethod
    def _find_running_notebooks_paragraphs(end_point, ids, notebooks_paragraphs):
        '''
        :param end_point: zeppelin end_point
        :param ids: notebook ids
        :param notebooks_paragraphs: shared dict by multiple threads to store the notebook_id and paragraph_id
        :return: list of tuples notebook_id , paragraph_id
        '''
        for id in ids:
            json_res = ApiCallHandler.get_api_call(end_point + "/job/" + str(id))
            for p in json_res['body']:
                if p['status'] == 'RUNNING':
                    notebooks_paragraphs.append((id, p['id']))
        return notebooks_paragraphs

    @staticmethod
    def _get_status_notebooks_paragraph(end_point, notebook_paragraph_tuples):
        notebook_paragraph_status = []
        for id in notebook_paragraph_tuples:
            json_res = ApiCallHandler.get_api_call(end_point + "/job/" + str(id[0]) + "/")
            for p in json_res['body']:
                if p['id'] == id[1]:
                    notebook_paragraph_status.append((id[0], id[1], p['status']))
                    break
        return notebook_paragraph_status


class ApiCallHandler():
    @staticmethod
    def validate_response(res):
        if (res.status_code == 200) and res.headers['content-type'] == 'application/json':
            return True
        else:
            print 'service error \n' + res.text
            return False

    @staticmethod
    def get_api_call(url):
        res = requests.get(url)
        if ApiCallHandler.validate_response(res):
            json_res = res.json()
            if json_res is not None and 'body' in json_res:
                return json_res
        print 'Error ' + res.text + '\n'
        return None

    @staticmethod
    def post_api_call(url, slack_payload):
        res = requests.post(url, json=slack_payload)
        if res.status_code == 200:
            return True
        return False

    @staticmethod
    def delete_api_call(url, k):
        res = requests.delete(url)
        if ApiCallHandler.validate_response(res):
            json_res = res.json()
            if json_res is not None and 'status' in json_res and json_res['status'] == 'OK':
                print str(k) + ' DELETE ' + url + ' ...'
                return True
        print 'Error from the server ' + url + '\n'
        return False
