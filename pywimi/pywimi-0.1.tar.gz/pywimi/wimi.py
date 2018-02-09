#!/usr/bin/python
# coding: utf-8

"""
Wrapper pour l'utilisation des APi WIMI
https://www.wimi-teamwork.com/fr/

:author kevin.daviet@accenture.com
:date 14/09/2017
:version 1.0.0
"""

import requests
import logging
import json
import urllib
import os
import sys

class Wimi(object):
    
    """
    Constructeur
    """

    def __init__(self):
        """
        Declaration d'une nouvelle instance Wimi

        :param account_name: le nom du wimi
        :param login: compte de connexion
        :param password: mot de passe de connexion
        :return ne retourne rien
        """
        # logging.getLogger().setLevel(logging.INFO)  # A commenter en PRD
        logging.info("> START Constructeur")
        self.account_name = ""
        self.login = ""
        self.password = ""
        self.project_slug = ""
        self.token = ""
        self.project_id = ""
        self.app_token = ""
        logging.info("< END Constructeur")

    def callApi(self, target, identification, data):
        """
        Appel generique a l'API

        :param target: webservice a contacter
        :param identification: parametre lie a l'identification
        :param data: parametre concernant les donnees
        :return: le retour du webservice au format string
        """
        msg = '{"header": {"target": "'+target+'","identification": '+identification+',"auth": {"login": "'+self.login+'","password": "'+self.password+'"},"api_version": "1.0", "token":"'+self.token+'","msg_key": ""},"body": {"data": '+data+'}}'
        headers = '{"Content-type": "application/json; charset=UTF-8; multipart/form-data", "Accept": "text/plain"}'
        response = requests.post("https://api.wimi.pro", msg, headers)
        logging.info(response.json())
        # Affichage des details de l'erreur
        if 'error' in response.json()['body']:
            logging.error("Erreur lors de l'appel a la target : "+target)
            logging.error(response.json()['body']['error']['debug_msg'])
        return response.text

    def log_in(self, account_name, login, password, project_slug, app_token):
        """
        Connexion a l'instance Wimi

        :param: pas de paramètre
        :return ne retourne rien
        """
        logging.info("> START login")

        self.account_name = account_name
        self.login = login
        self.password = password
        self.project_slug = project_slug
        self.app_token = app_token

        response = json.loads(self.callApi("auth.user.login", '{"account_name":"'+self.account_name+'"}', '{ "list_projects" : true }'))
        logging.info(response['body']['data']['account_id'])
        self.account_id = response['body']['data']['account_id']
        self.user_id = response['body']['data']['user']['user_id']
        self.token = response['header']['token']
        projects = response['body']['data']['projects']
        # Recuperation du project_id
        for project in projects:
            if project['slug'] == self.project_slug:
                self.project_id = project['id']
                break
        logging.info("project_id : "+str(self.project_id))
        logging.info("< END login")
        return True

    def log_out(self):
        """
        Deconnexion du Wimi

        :param: pas de paramètre
        :return ne retourne rien
        """
        logging.info("> START logout")
        identification = '{"user_id":"'+str(self.user_id)+'", "account_id":"'+str(self.account_id)+'"}'
        data = '{}'
        self.callApi("auth.user.logout", identification, data)
        logging.info("< END logout")

    def getTaskListId(self, task_list_name):
        """
        Recupère l'id d'une liste de tache

        :param: task_list_name : le nom de la liste a chercher
        :return task_list_id : l'id de la liste recherchee
        """
        logging.info("> START getTaskListId")
        task_list_id = '';
        identification = '{"user_id":"' + str(self.user_id) + '", "account_id":"' + str(self.account_id) + '", "project_id":"'+str(self.project_id)+'"}'
        data = '{}'
        response = json.loads(self.callApi("task.tlist.getall", identification, data))
        logging.info(response)
        lists = response['body']['data']['lists']
        for list in lists:
            if list['label'] == task_list_name:
                task_list_id = list['task_list_id']
                break
        logging.info("< END getTaskListId")
        return task_list_id

    def getTaskId(self, task_name, task_list_id):
        """
        Recupère l'id d'une tache

        :param: task_name : le nom de la tache a chercher
        :param: task_list_id : l'id de la liste dans laquelle chercher
        :return task_id : l'id de la tache recherchee
        """
        logging.info("> START getTaskId")
        task_id = '';
        identification = '{"user_id":"' + str(self.user_id) + '", "account_id":"' + str(
            self.account_id) + '", "project_id":"' + str(self.project_id) + '", "task_list_id":"'+str(task_list_id)+'"}'
        data = '{}'
        response = json.loads(self.callApi("task.task.getall", identification, data))
        # @TODO : Ajouter un controle sur la presence de la tache
        try:
            tasks = response['body']['data']['tasks']
            for task in tasks:
                if task['label'] == task_name:
                    task_id = task['task_id']
                    break
                else:
                    task_id = "false"
        except ValueError:
            logging.warn("Tache non trouve. task_id set to false")
            task_id = "false"
        logging.info("< END getTaskId")
        return task_id

    def listTask(self, task_list_id):
        """
        Recupère une liste de tache par liste

        :param: task_list_id : l'id de la liste dans laquelle chercher
        :return list_task : tableau contenant l'ensemble des id des taches
        """
        logging.info("> START listTask")
        list_task = [];
        identification = '{"user_id":"' + str(self.user_id) + '", "account_id":"' + str(
            self.account_id) + '", "project_id":"' + str(self.project_id) + '", "task_list_id":"'+str(task_list_id)+'"}'
        data = '{}'
        response = json.loads(self.callApi("task.task.getall", identification, data))
        tasks = response['body']['data']['tasks']
        for task in tasks:
            list_task.append(task['task_id'])
        logging.info("< END listTask")
        return list_task

    def getTaskDetail(self, task_id):
        """
        Recupère les details d'une tache

        :param: task_id : l'id de la tache a chercher
        :return task_detail : les details de la tache
        """
        logging.info("> START getTaskDetail")
        identification = '{"user_id":"' + str(self.user_id) + '", "account_id":"' + str(
            self.account_id) + '", "project_id":"' + str(self.project_id) + '", "task_id":"'+str(task_id)+'"}'
        data = '{}'
        response = json.loads(self.callApi("task.task.get", identification, data))
        task_detail = response['body']['data']['task']
        logging.info("< END getTaskDetail")
        return task_detail

    def setTaskDescription(self, task_id, description):
        """
        Ecrit dans la description d'une tache

        :param: task_id : l'id de la tache a chercher
        :return ne retourne rien
        """
        logging.info("> START setTaskDescription")
        identification = '{"user_id":"' + str(self.user_id) + '", "account_id":"' + str(
            self.account_id) + '", "project_id":"' + str(self.project_id) + '", "task_id":"'+str(task_id)+'"}'
        data = '{"description":"'+description+'"}'
        response = json.loads(self.callApi("task.task.update", identification, data))
        logging.info("< END setTaskDescription")

    def createTask(self, task_list_id, data):
        """
        Creer une nouvelle tache

        :param: task_list_id : l'id de la liste dans laquelle ajouter la tache
        :return ne retourne rien
        """
        logging.info("> START createTask")
        identification = '{"user_id":"' + str(self.user_id) + '", "account_id":"' + str(
            self.account_id) + '", "project_id":"' + str(self.project_id) + '", "task_list_id":"'+str(task_list_id)+'"}'
        self.callApi("task.task.create", identification, data)
        logging.info("< END createTask")

    def deleteTask(self, task_id):
        """
        Supprimer une tache

        :param: task_id : l'id de la tache a supprimer
        :return ne retourne rien
        """
        logging.info("> START deleteTask")
        identification = '{"user_id":"' + str(self.user_id) + '", "account_id":"' + str(
            self.account_id) + '", "project_id":"' + str(self.project_id) + '", "task_id":"'+str(task_id)+'"}'
        data = '{}'
        self.callApi("task.task.delete", identification, data)
        logging.info("< END deleteTask")

    def upload(self, file_path, file_name):
        """
        Upload un fichier dans la zone de travaille selectionnee

        :param: file_path : chemin du fichier a uploader
        :param: file_name : nom du fichier a uploader
        :return le status code de l'appel http
        """
        logging.info("> START upload")

        identification = '{"user_id":"' + str(self.user_id) + '", "account_id":"' + str(
            self.account_id) + '", "project_id":"' + str(self.project_id) + '","account_name":"'+str(self.account_name)+'"}'

        # recuperation de la taille du fichier en octet
        file_size = os.path.getsize(file_path+file_name)

        # creation du header specifique a l'upload des fichiers
        header = '{"header": {"target": "document.file.upload", "app_token":"' + self.app_token + '","api_version": "1.2", "msg_key":"mon message", "token":"'+self.token+'", "identification": ' + identification + ', "debug":{"indent_output":true}}, "body": {"data": {"notify":false, "replace_master":true, "name":"' + file_name + '", "size":' + str(
            file_size) + '}}}'
        headers = {
            'X-Wimi-WApi': urllib.quote(header)
        }
        data = open(file_path + file_name, 'rb').read()
        logging.info(header)
        try:
            response = requests.post('https://api.files.wimi.pro/', headers=headers, data=data)
            logging.info(response.json())
        except requests.exceptions.RequestException as e:
            logging.error("[upload] "+str(e.message))
            self.logout()
            sys.exit(1)

        logging.info("< END upload")

        return response.status_code

    def download(self, file_id, file_name):
        """
        Download un fichier depuis la zone de travaille selectionnee

        :param: file_id : l'id du fichier a telecharger
        :param: file_name : nom du fichier source
        :return le status code de l'appel http
        """
        logging.info("> START download")

        identification = '{"user_id":"' + str(self.user_id) + '", "account_id":"' + str(
            self.account_id) + '", "project_id":"' + str(self.project_id) + '","account_name":"'+str(self.account_name)+'","file_id":'+str(file_id)+'}'

        # creation du header specifique a l'upload des fichiers
        msg = '{"header":{"target":"document.file.Download", "app_token":"' + self.app_token + '", "token":"'+self.token+'" ,"identification": ' + identification + ',"api_version":"1.2","msg_key":"document.file.download"}, "body":{"data":null}}'
        response = requests.post("https://api.files.wimi.pro/", msg)

        with open('./download/'+file_name, 'wb') as f:
            f.write(response.content)
        logging.info("< END download")

        return response.status_code

    def getFileData(self, file_name):
        """
        Recupère la liste des fichiers dans l'espace de travail par defaut

        :param: n/a
        :return la liste des fichiers avec leurs attributs
        """
        logging.info("> START getFileData")

        file_data = ""
        identification = '{"user_id":"' + str(self.user_id) + '", "account_id":"' + str(
            self.account_id) + '", "project_id":"' + str(self.project_id) + '"}'
        data = '{}'
        response = json.loads(self.callApi("document.entry.List", identification, data))
        try:
            files = response['body']['data']['files']
            for file in files:
                if file['name'] == file_name:
                    file_data = file
                    break
                else:
                    file_data = "false"
        except ValueError:
            logging.warn("Tache non trouve. task_id set to false")
            file_data = "false"

        logging.info("< END getFileData")

        return file_data

    def deleteFile(self, file_id):
        """
        Supprime un fichier

        :param: file_id : l'id du fichier a supprimer
        :return: n/a
        """
        logging.info("> START deleteFile")

        identification = '{"user_id":"' + str(self.user_id) + '", "account_id":"' + str(
            self.account_id) + '", "project_id":"' + str(self.project_id) + '", "file_id_list":['+str(file_id)+']}'
        data = '{}'
        response = self.callApi("document.file.MoveToTrash", identification, data)
        response = self.callApi("document.file.moveToGarbageCollector", identification, data)
        logging.info(response)
        logging.info("< END deleteFile")


