import sys
import re
import json
import io
import os
import datetime
import argparse

from cmd2 import Cmd,options,with_argparser
from falkonryclient import client as Falkonry
from falkonryclient.helper.utils import exception_handler
from falkonryclient.helper import schema as Schemas
from pprint import pprint

global _assessmentId
global _datastreamId
global _falkonry
global _self

_self = None
_falkonry = None
_assessmentId = None
_datastreamId = None


class REPL(Cmd):
    prompt = "falkonry>> "

    def __init__(self):
        Cmd.__init__(self)
        global  _self
        _self = self
        print_custom("Welcome to Falkonry Shell !", "green")

    login_argparser = argparse.ArgumentParser()
    login_argparser.add_argument('--host', help="host url")
    login_argparser.add_argument('--token', help="auth token")

    @with_argparser(login_argparser)
    def do_login(self, args=None):
        """login to the falkonry"""
        if (args.host is None or args.host =="") or (args.token is None or args.token ==""):
            print_error("Please pass host url and token")
            return
        if args.host.find("https://") == -1:
            args.host = "https://" + args.host
        if validate_login(args.host, args.token):
            print_success("logged in to falkonry")

    def do_logout(self, line):
        """logout from the falkonry"""
        if check_login():
            global _falkonry
            _falkonry = None
            print_success("logged out from falkonry")

    def do_login_details(self, line):
        """get login details"""
        if check_login():
            print_info('Host : ' + _falkonry.host + "\n" + 'Token : ' +_falkonry.token)

    def do_exit(self, line):
        """exit the falkonry shell"""
        quit()

    def do_datastream_get_list(self, line):
        """list datastreams"""
        if check_login():
            print_info("Listing Datastreams...")
            print_info("==================================================================================================================")
            datastreamList = _falkonry.get_datastreams()
            if len(datastreamList) == 0 :
                print_info("No Datastreams found")
            print_row("Datastream Name", "Id", "Created By", "Live Status")
            print_info("==================================================================================================================")
            for datastream in datastreamList:
                print_row(datastream.get_name(), datastream.get_id(), datastream.get_created_by(), datastream.get_live())
            print_info("==================================================================================================================")

    datastream_get_by_id_parser = argparse.ArgumentParser()
    datastream_get_by_id_parser.add_argument('--id', help="datastream id")

    @with_argparser(datastream_get_by_id_parser)
    def do_datastream_get_by_id(self, args=None):
        """get datastream by id """
        if check_login():
            if args.id is None or args.id == "":
                print_error("Please pass datastream id")
                return
            print_info("Fetching Datastreams")
            try:
                datastreamObject = _falkonry.get_datastream(args.id)
                print_datastream_details(datastreamObject.to_json())
            except Exception as error:
                handle_error(error)

    datastream_default_set_parser = argparse.ArgumentParser()
    datastream_default_set_parser.add_argument('--id', help="datastream id")

    @with_argparser(datastream_default_set_parser)
    def do_datastream_default_set(self, args=None):
        """set default datastream"""
        if check_login():
            try:
                if args.id is None or args.id == "":
                    print_error("Please pass datastream id")
                    return
                global _datastreamId
                datastreamObject = _falkonry.get_datastream(args.id)
                _datastreamId = args.id
                print_success("Default datastream set : "+ args.id)
                return
            except Exception as error:
                handle_error(error)
                return

    def do_datastream_default_get(self, line):
        """get default datastream"""
        global _datastreamId
        if check_login():
            if _datastreamId is None:
                print_error("No default datastream set")
                return
            else:
                try:
                    datastreamObject = _falkonry.get_datastream(_datastreamId)
                    print_info("Default datastream set : " + _datastreamId + " Name : " + datastreamObject.get_name())
                except Exception as error:
                    _datastreamId = None
                    handle_error(error)
                    print_error("Please set the default datastream again")
        return

    def do_datastream_get_entity_meta(self, line):
        """get entitymeta of datastream"""
        global _datastreamId
        if check_login():
            if _datastreamId is None:
                print_error("No default datastream set")
                return
            else:
                try:
                    entityMeta = _falkonry.get_entity_meta(_datastreamId)
                    print_info("Entity Meta of datastream: " + _datastreamId)
                    for entity in entityMeta:
                        print_info("Entity Label : " + entity.get_label() + ". Entity Id : " + entity.get_sourceId())
                except Exception as error:
                    handle_error(error)
        return

    datastream_add_entity_meta_parser = argparse.ArgumentParser()
    datastream_add_entity_meta_parser.add_argument('--path', help="file path of entity meta request")

    @with_argparser(datastream_add_entity_meta_parser)
    def do_datastream_add_entity_meta(self, args=None):
        """add entitymeta of datastream"""
        global _datastreamId
        if check_login():
            if _datastreamId is None:
                print_error("No default datastream set")
                return
            else:
                try:
                    if args.path is None or args.path == "":
                        print_error("Please pass json file path for adding entity meta")
                        return
                    try:
                        file_extension = get_file_extension(args.path)
                        if file_extension != ".json":
                            print_error("Only JSON file is accepted.")
                            return
                        with open(args.path) as data_file:
                            data = json.load(data_file)
                    except Exception as error:
                        print_error("Error in reading file." + str(error))
                        return
                    entityMeta = _falkonry.add_entity_meta(_datastreamId, {}, data)
                    print_info("Entity Meta successfully added to datastream: " + _datastreamId)
                except Exception as error:
                    handle_error(error)
        return

    datastream_create_parser = argparse.ArgumentParser()
    datastream_create_parser.add_argument('--path', help="file path of request")

    @with_argparser(datastream_create_parser)
    def do_datastream_create(self, args=None):
        """create datastream"""
        if check_login():
            try:
                if args.path is None or args.path == "":
                    print_error("Please pass json file path for creating datastream")
                    return
                # read file
                try:
                    file_extension = get_file_extension(args.path)
                    if file_extension != ".json":
                        print_error("Only JSON file is accepted.")
                        return
                    with open(args.path) as data_file:
                        data = json.load(data_file)
                except Exception as error:
                    print_error("Error in reading file." + str(error))
                    return
                created_datastream = _falkonry.create_datastream(data)
                print_success("Datastream successfully created : "+ created_datastream.get_id())
                return
            except Exception as error:
                handle_error(error)
                return
        return

    datastream_delete_argparser = argparse.ArgumentParser()
    datastream_delete_argparser.add_argument('--id', help="datastream id")

    @with_argparser(datastream_delete_argparser)
    def do_datastream_delete(self, args=None):
        """delete datastream"""
        if check_login():
            try:
                if args.id is None:
                    print_error("Please pass datastream id")
                    return
                _falkonry.delete_datastream(args.id)
                print_success("Datastream successfully deleted : "+ args.id)
                return
            except Exception as error:
                handle_error(error)
                return

    def do_datastream_get_live_status(self, line):
        """ Returns the Live monitoring status for the default datastream """
        global _datastreamId
        if check_login():
            try:
                if check_default_datastream():
                    print_info("Fetching Live monitoring status for datastream : " + _datastreamId)
                    res = _falkonry.get_datastream(_datastreamId).get_live()
                    print_info("Live Monitoring : "+ str(res))
                    return res
                return
            except Exception as error:
                handle_error(error)
                return
        return

    def do_datastream_start_live(self, line):
        """ turn on live monitoring of datastream """
        global _datastreamId
        if check_login():
            try:
                if check_default_datastream():
                    print_info("Turning on Live monitoring for datastream : " + _datastreamId)
                    res = _falkonry.on_datastream(_datastreamId)
                    print_success("Datastream is ON for live monitoring")
                return
            except Exception as error:
                handle_error(error)
                return
        return

    def do_datastream_stop_live(self, line):
        """ turn off live monitoring of datastream """
        global _datastreamId
        if check_login():
            try:
                if check_default_datastream():
                    print_info("Turning off Live monitoring for datastream : " + _datastreamId)
                    _falkonry.off_datastream(_datastreamId)
                    print_success("Datastream is OFF for live monitoring")
                return
            except Exception as error:
                handle_error(error)
                return
        return

    datastream_add_historical_data_argparser = argparse.ArgumentParser()
    datastream_add_historical_data_argparser.add_argument('--path', help="file path of request")
    datastream_add_historical_data_argparser.add_argument('--timeIdentifier', help="time identifier in the file")
    datastream_add_historical_data_argparser.add_argument('--entityIdentifier', help="Entity identifier in the file")
    datastream_add_historical_data_argparser.add_argument('--timeFormat', help="Time format")
    datastream_add_historical_data_argparser.add_argument('--timeZone', help="Timezone")
    datastream_add_historical_data_argparser.add_argument('--signalIdentifier', help="signal Identifier in file")
    datastream_add_historical_data_argparser.add_argument('--valueIdentifier', help="Value Identifier in the file")
    datastream_add_historical_data_argparser.add_argument('--batchIdentifier', help="Batch Identifier, if the data being uploaded in batch datastream")

    @with_argparser(datastream_add_historical_data_argparser)
    def do_datastream_add_historical_data(self, args=None):
        """ add historical data to datastream for model learning """
        if check_login():
            try:
                if args.path is None or args.path == "":
                    print_error("Please pass historical data file path")
                    return
                if check_default_datastream():
                    file_extension = get_file_extension(args.path)
                    if file_extension != ".csv" and file_extension != ".json":
                        print_error("Only CSV or JSON file is accepted.")
                        return
                    data = io.open(args.path)
                    options = {}
                    if args.timeIdentifier is not None and args.timeIdentifier != "":
                        options['timeIdentifier'] = args.timeIdentifier
                    if args.timeFormat is not None and args.timeFormat != "":
                        options['timeFormat'] = args.timeFormat
                    if args.timeZone is not None and args.timeZone != "":
                        options['timeZone'] = args.timeZone
                    if args.entityIdentifier is not None and args.entityIdentifier != "":
                        options['entityIdentifier'] = args.entityIdentifier
                    if args.signalIdentifier is not None and args.signalIdentifier != "":
                        options['signalIdentifier'] = args.signalIdentifier
                    if args.valueIdentifier is not None and args.valueIdentifier != "":
                        options['valueIdentifier'] = args.valueIdentifier
                    if args.batchIdentifier is not None and args.batchIdentifier != "":
                        options['batchIdentifier'] = args.batchIdentifier
                    options['streaming'] = False
                    options['hasMoreData'] = False

                    data_options = options
                    response = _falkonry.add_input_stream(_datastreamId, file_extension.split(".")[1], data_options, data)
                    print_info(str(response))
            except Exception as error:
                handle_error(error)
                return

    @with_argparser(datastream_add_historical_data_argparser)
    def do_datastream_add_live_data(self, args=None):
        """add live data to datastream for live monitoring """
        if check_login():
            try:
                if args.path is None or args.path == "":
                    print_error("Please pass historical data file path")
                    return
                if check_default_datastream():
                    file_extension = get_file_extension(args.path)
                    if file_extension != ".csv" and file_extension != ".json":
                        print_error("Only CSV or JSON file is accepted.")
                        return
                    data = io.open(args.path)
                    options = {}
                    if args.timeIdentifier is not None and args.timeIdentifier != "":
                        options['timeIdentifier'] = args.timeIdentifier
                    if args.timeFormat is not None and args.timeFormat != "":
                        options['timeFormat'] = args.timeFormat
                    if args.timeZone is not None and args.timeZone != "":
                        options['timeZone'] = args.timeZone
                    if args.entityIdentifier is not None and args.entityIdentifier != "":
                        options['entityIdentifier'] = args.entityIdentifier
                    if args.signalIdentifier is not None and args.signalIdentifier != "":
                        options['signalIdentifier'] = args.signalIdentifier
                    if args.valueIdentifier is not None and args.valueIdentifier != "":
                        options['valueIdentifier'] = args.valueIdentifier
                    if args.batchIdentifier is not None and args.batchIdentifier != "":
                        options['batchIdentifier'] = args.batchIdentifier
                    options['streaming'] = True
                    options['hasMoreData'] = True

                    data_options = options

                    response = _falkonry.add_input_stream(_datastreamId, file_extension.split(".")[1], data_options, data)
                    print_info(str(response))
            except Exception as error:
                handle_error(error)
                return
        return

    def do_assessment_get_list(self, line):
        """ list assessments for default datastream"""
        if check_login():
            try:
                if check_default_datastream():
                    print_info("Fetching assessment list of datastream : " + _datastreamId + "...")
                    print_info("==================================================================================================================")
                    assessmentList = _falkonry.get_assessments()
                    if len(assessmentList) == 0:
                        print_info("No assessment found")
                    print_row("Assessment Name", "Id", "Created By", "Live Status")
                    print_info("==================================================================================================================")
                    for assessment in assessmentList:
                        if assessment.get_datastream() == _datastreamId :
                            print_row(assessment.get_name(), assessment.get_id(), assessment.get_created_by(), assessment.get_live())
                    print_info("==================================================================================================================")
                return
            except Exception as error:
                handle_error(error)
                return
        return

    assessment_get_by_id_argparser = argparse.ArgumentParser()
    assessment_get_by_id_argparser.add_argument('--id', help="assessment id")

    @with_argparser(assessment_get_by_id_argparser)
    def do_assessment_get_by_id(self, args=None):
        """ fetch assessment by id for default datastream"""
        if check_login():
            try:
                if args.id is None:
                    print_error("Please pass assessment id")
                    return
                assessmentObject = _falkonry.get_assessment(args.id)
                print_assessment_details(assessmentObject.to_json())
                return
            except Exception as error:
                handle_error(error)
                return
        return

    assessment_create_argparser = argparse.ArgumentParser()
    assessment_create_argparser.add_argument('--path', help="file path of request")

    @with_argparser(assessment_create_argparser)
    def do_assessment_create(self, args=None):
        """ create assessment in default datastream"""
        if check_login():
            try:
                if check_default_datastream():
                    if args.path is None or args.path == "":
                        print_error("Please pass json file path for creating assessment")
                        return
                    # read file
                    try:
                        file_extension = get_file_extension(args.path)
                        if file_extension != ".json":
                            print_error("Only JSON file is accepted.")
                            return
                        with open(args.path) as data_file:
                            data = json.load(data_file)
                    except Exception as error:
                        print_error("Error in reading file." + str(error))
                        return
                    data['datastream'] = _datastreamId
                    created_assessment = _falkonry.create_assessment(data)
                    print_success("Assessment successfully created : "+ created_assessment.get_id())
                return
            except Exception as error:
                handle_error(error)
                return
        return

    do_assessment_delete_argparser = argparse.ArgumentParser()
    do_assessment_delete_argparser.add_argument('--id', help="assessment id")

    @with_argparser(do_assessment_delete_argparser)
    def do_assessment_delete(self, args=None):
        """ delete assessment by id default datastream"""
        if check_login():
            try:
                if args.id is None:
                    print_error("Please pass assessment id")
                    return
                _falkonry.delete_assessment(args.id)
                print_info("Assessment deleted successfully: " + args.id)
                return
            except Exception as error:
                handle_error(error)
                return
        return

    assessment_default_set_argparser = argparse.ArgumentParser()
    assessment_default_set_argparser.add_argument('--id', help="assessment id")

    @with_argparser(assessment_default_set_argparser)
    def do_assessment_default_set(self, args=None):
        """ set default assessment"""
        if check_login():
            try:
                if args.id is None:
                    print_error("Please pass assessment id")
                    return
                if check_default_datastream():
                    global _assessmentId
                    assessmentObj = _falkonry.get_assessment(args.id)
                    if assessmentObj.get_datastream() != _datastreamId:
                        print_error("Assessment id : " + args.id + " does not belong to default datastream")
                    _assessmentId = args.id
                    print_success("Default assessment set : "+ args.id)
                return
            except Exception as error:
                handle_error(error)
                return
        return

    def do_assessment_default_get(self, line):
        """ get default assessment"""
        global _assessmentId
        if check_login():
            if _assessmentId is None:
                print_error("No default assessment set")
                return
            else:
                try:
                    assessmentObj = _falkonry.get_assessment(_assessmentId)
                    print_info("Default assessment set : " + _assessmentId + " Name : " + assessmentObj.get_name())
                except Exception as error:
                    _assessmentId = None
                    handle_error(error)
                    print_error("Please set the default assessment again")
        return

    assessment_add_facts_argparser = argparse.ArgumentParser()
    assessment_add_facts_argparser.add_argument('--path', help="file path of request")
    assessment_add_facts_argparser.add_argument('--startTimeIdentifier', help="Start time identifier in the file")
    assessment_add_facts_argparser.add_argument('--endTimeIdentifier', help="End time identifier in the file")
    assessment_add_facts_argparser.add_argument('--timeFormat', help="Time format of start and endtime")
    assessment_add_facts_argparser.add_argument('--timeZone', help="Timezone")
    assessment_add_facts_argparser.add_argument('--entityIdentifier', help="should be kept empty in case of single entity datastream")
    assessment_add_facts_argparser.add_argument('--valueIdentifier', help="Value Identifier in the file")
    assessment_add_facts_argparser.add_argument('--batchIdentifier', help="Batch Identifier, if the data being upload into a batched datastream")
    assessment_add_facts_argparser.add_argument('--keywordIdentifier', help="Keyword Identifier for facts being uploaded")
    assessment_add_facts_argparser.add_argument('--additionalKeyword', help="Keyword for all the facts being uploaded")

    @with_argparser(assessment_add_facts_argparser)
    def do_assessment_add_facts(self, args=None):
        """ add facts to assessment"""
        if check_login():
            try:
                if args.path is None or args.path == "":
                    print_error("Please pass facts data file path")
                    return
                if check_default_assessment():
                    file_extension = get_file_extension(args.path)
                    if file_extension != ".csv" and file_extension != ".json":
                        print_error("Only CSV or JSON file is accepted.")
                        return
                    data = io.open(args.path)
                    options = {}
                    if args.startTimeIdentifier is not None and args.startTimeIdentifier != "":
                        options['startTimeIdentifier'] = args.startTimeIdentifier
                    if args.endTimeIdentifier is not None and args.endTimeIdentifier != "":
                        options['endTimeIdentifier'] = args.endTimeIdentifier
                    if args.timeFormat is not None and args.timeFormat != "":
                        options['timeFormat'] = args.timeFormat
                    if args.timeZone is not None and args.timeZone != "":
                        options['timeZone'] = args.timeZone
                    if args.entityIdentifier is not None and args.entityIdentifier != "":
                        options['entityIdentifier'] = args.entityIdentifier
                    if args.valueIdentifier is not None and args.valueIdentifier != "":
                        options['valueIdentifier'] = args.valueIdentifier
                    if args.batchIdentifier is not None and args.batchIdentifier != "":
                        options['batchIdentifier'] = args.batchIdentifier
                    if args.keywordIdentifier is not None and args.keywordIdentifier != "":
                        options['keywordIdentifier'] = args.keywordIdentifier
                    if args.additionalKeyword is not None and args.additionalKeyword != "":
                        options['additionalKeyword'] = args.additionalKeyword

                    response = _falkonry.add_facts_stream(_assessmentId, file_extension.split(".")[1], options, data)
                    print_info(str(response))
                return
            except Exception as error:
                handle_error(error)
                return
        return

    assessment_get_historical_output_argparser = argparse.ArgumentParser()
    assessment_get_historical_output_argparser.add_argument('--path', help="file path to write output")
    assessment_get_historical_output_argparser.add_argument('--trackerId', help="tracker id of the previous output request")
    assessment_get_historical_output_argparser.add_argument('--modelIndex', help="index of the model of which output needs to be fetched ")
    assessment_get_historical_output_argparser.add_argument('--startTime', help="startTime of the output range should be in ISO8601 format 'YYYY-MM-DDTHH:mm:ss.SSSZ'")
    assessment_get_historical_output_argparser.add_argument('--endTime', help="endTime of the output range should be in ISO8601 format 'YYYY-MM-DDTHH:mm:ss.SSSZ'")
    assessment_get_historical_output_argparser.add_argument('--format', help="format of the output. For csv pass text/csv. For JSON output pass application/json")

    @with_argparser(assessment_get_historical_output_argparser)
    def do_assessment_get_historical_output(self, args=None):
        """ get learn/test output of assessment"""
        if check_login():
            try:
                if check_default_assessment():
                    output_ops = {}
                    if args.trackerId is not None and args.trackerId != "":
                        output_ops['trackerId'] = args.trackerId
                    if args.modelIndex is not None and args.modelIndex != "":
                        output_ops['modelIndex'] = args.modelIndex
                    if args.startTime is not None and args.startTime != "":
                        output_ops['startTime'] = args.startTime
                    if args.endTime is not None and args.endTime != "":
                        output_ops['endTime'] = args.endTime
                    if args.format is not None and args.format != "":
                        if args.format != "application/json" and args.format != "text/csv":
                            print_error("Unsupported response format. Only supported format are : application/json ,text/csv")
                            return
                        output_ops['format'] = args.format
                    if (args.trackerId is None or args.trackerId =="") and (args.startTime is None or args.startTime == ""):
                        print_error("TrackerID or startTime is require for fetching output data")
                        return
                    output_response = _falkonry.get_historical_output(_assessmentId, output_ops)
                    if output_response.status_code == 200:
                        if args.path:
                            #write response to file
                            try:
                                file = open(args.path,"w")
                                file.write(str(output_response.text))
                                file.close()
                                print_success("Output data is written to the file : " + args.path)
                            except Exception as fileError:
                                handle_error(fileError)
                        else:
                            print_info("==================================================================================================================")
                            print_info(str(output_response.text))
                            print_info("==================================================================================================================")
                    if output_response.status_code == 202:
                        print_success(str(output_response.text))
                        json_resp = json.loads(str(output_response.text))
                        print_success("Falkonry is generating your output. Please try following command in some time.")
                        print_success("assessment_get_historical_output --trackerId="+json_resp['__$id'])
                    return
                return
            except Exception as error:
                handle_error(error)
                return
        return

    assessment_output_listen_argparser = argparse.ArgumentParser()
    assessment_output_listen_argparser.add_argument('--format', help="format of the output. For csv pass text/csv. For JSON output pass application/json")

    @with_argparser(assessment_output_listen_argparser)
    def do_assessment_output_listen(self, args=None):
        """ get live output of assessment"""
        if check_login():
            try:
                if not check_default_assessment():
                   return
                output_ops = {}
                if args.format is not None and args.format != "":
                    if args.format != "application/json" and args.format != "text/csv":
                        print_error("Unsupported response format. Only supported format are : application/json ,text/csv")
                        return
                    output_ops['format'] = args.format
                output_response = _falkonry.get_output(_assessmentId, output_ops)
                print_info("Fetching live assessments : ")
                for event in output_response.events():
                    print_info(json.dumps(json.loads(event.data)))
            except Exception as error:
                handle_error(error)
                return
        return

    assessment_get_facts_argparser = argparse.ArgumentParser()
    assessment_get_facts_argparser.add_argument('--path', help="file path to write output")
    assessment_get_facts_argparser.add_argument('--modelIndex', help="index of the model of which facts needs to be fetched ")
    assessment_get_facts_argparser.add_argument('--startTime', help="startTime of the facts range should be in ISO8601 format 'YYYY-MM-DDTHH:mm:ss.SSSZ'")
    assessment_get_facts_argparser.add_argument('--endTime', help="endTime of the facts range should be in ISO8601 format 'YYYY-MM-DDTHH:mm:ss.SSSZ'")
    assessment_get_facts_argparser.add_argument('--format', help="format of the facts data. For csv pass text/csv. For JSON output pass application/json")

    @with_argparser(assessment_get_facts_argparser)
    def do_assessment_get_facts(self, args=None):
        """ get facts of assessment"""
        if check_login():
            try:
                if not check_default_assessment():
                   return
                output_ops = {}
                if args.modelIndex is not None and args.modelIndex != "":
                    output_ops['modelIndex'] = args.modelIndex
                if args.startTime is not None and args.startTime != "":
                    output_ops['startTime'] = args.startTime
                if args.endTime is not None and args.endTime != "":
                    output_ops['endTime'] = args.endTime
                if args.format is not None and args.format != "":
                    if args.format != "application/json" and args.format != "text/csv":
                        print_error("Unsupported response format. Only supported format are : application/json ,text/csv")
                        return
                    output_ops['format'] = args.format
                output_response = _falkonry.get_facts(_assessmentId, output_ops)
                if args.path is not None and args.path != "":
                    #write response to file
                    try:
                        file = open(args.path,"w")
                        file.write(str(output_response.text))
                        file.close()
                        print_success("Facts data is written to the file : " + args.path)
                    except Exception as fileError:
                        handle_error(fileError)
                else:
                    print_info("Facts Data : ")
                    print_info("==================================================================================================================")
                    print_info(str(output_response.text))
                    print_info("==================================================================================================================")
            except Exception as error:
                handle_error(error)
                return
        return


    datastream_get_data_argparser = argparse.ArgumentParser()
    datastream_get_data_argparser.add_argument('--path', help="file path to write output")
    datastream_get_data_argparser.add_argument('--format', help="format of the input data. For csv pass text/csv. For JSON output pass application/json")

    @with_argparser(datastream_get_data_argparser)
    def do_datastream_get_data(self, args=None):
        """ get data of datastream"""
        if check_login():
            try:
                if not check_default_datastream():
                   return
                output_ops = {}
                if args.format is not None and args.format != "":
                    if args.format != "application/json" and args.format != "text/csv":
                        print_error("Unsupported response format. Only supported format are : application/json ,text/csv")
                        return
                    output_ops['format'] = args.format
                output_response = _falkonry.get_datastream_data(_datastreamId, output_ops)
                if args.path is not None and args.path != "":
                    #write response to file
                    try:
                        file = open(args.path,"w")
                        file.write(str(output_response.text))
                        file.close()
                        print_success("Input data is written to the file : " + args.path)
                    except Exception as fileError:
                        handle_error(fileError)
                else:
                    print_info("Input Data : ")
                    print_info("==================================================================================================================")
                    print_info(str(output_response.text))
                    print_info("==================================================================================================================")
            except Exception as error:
                handle_error(error)
                return
        return



def validate_login(host,token):
    """validate Login"""
    try:
        global _falkonry
        if not(not host or not token):
            p = re.compile(
                r'^(?:http|ftp)s?://' # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
                r'localhost|' #localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
                r'(?::\d+)?' # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            m = p.match(host)
            if m:
                _falkonry = Falkonry(host=host, token=token, options={"header":"falkonry-cli"})
                # test auth token validation
                try:
                    datastream = _falkonry.get_datastream('test-id')
                except Exception as error:
                    errorMsg = exception_handler(error)
                    if errorMsg:
                        if errorMsg == "Unauthorized Access":
                            print_error('Unauthorized Access. Please verify your details.')
                            _falkonry = None
                            return False
                        elif errorMsg == "No such Datastream available":
                            return True
                        else:
                            _falkonry = None
                            return False
                    else:
                        _falkonry = None
                        print_error('Unable to connect to falkonry. Please verify your details.')
                        return False
            else:
                print_error("Invalid Host Url")
                return False
    except Exception as error:
        _falkonry = None
        print_error('Unable to connect to falkonry. Please verify your details.')
        return False


def check_default_datastream():
    global _datastreamId
    if _datastreamId is None:
        print_error("Set default datastream first")


def check_login():
    if _falkonry is None:
        print_error("Please login first")
        return False
    else:
        return True


def print_info(msg):
    print(_self.colorize(msg, "blue"))


def print_success(msg):
    print(_self.colorize(msg, "green"))


def print_error(msg):
    print(_self.colorize(msg + "\n Try help <command> for info", "red"))


def print_custom(msg, color):
    print(_self.colorize(msg, color))


def get_file_extension(path):
    file_extension = os.path.splitext(path)
    return file_extension[1]


def check_default_datastream():
    global _datastreamId
    if check_login():
        if _datastreamId is None:
            print_error("No default datastream set")
            return
        else:
            try:
                datastreamObject = _falkonry.get_datastream(_datastreamId)
                print_info("Default datastream set : " + _datastreamId + " Name : " + datastreamObject.get_name())
                return True
            except Exception as error:
                _datastreamId = None
                handle_error(error)
                print_error("Please set the default datastream again")
                return False
    return


def check_default_assessment():
    global _assessmentId
    if check_login():
        if _assessmentId is None:
            print_error("No default assessment set")
            return
        else:
            try:
                assessmentObj = _falkonry.get_assessment(_assessmentId)
                print_info("Default assessment set : " + _assessmentId + " Name : " + assessmentObj.get_name())
                return True
            except Exception as error:
                _assessmentId = None
                handle_error(error)
                print_error("Please set the default assessment again")
                return False
    return


def print_row(name, id, user_id, live_status):
    print_info(" %-45s %-20s %-20s %-20s" % (name, id, user_id, live_status))


def handle_error(error):
    try:
        errorMsg = exception_handler(error)
        print_error(errorMsg)
    except Exception as error_new:
        print(_self.colorize("Unhandled Exception : " + str(error), "red"))

def print_datastream_details(datastream_str):
    datastream = json.loads(datastream_str)
    print_info("==================================================================================================================")
    print_info("Id : " + datastream['id'])
    print_info("Name : " + datastream['name'])
    print_info("Created By : " + datastream['createdBy'])
    print_info("Create Time : " + (str(datetime.datetime.fromtimestamp(datastream['createTime']/1000.0))))
    print_info("Update Time : " + (str(datetime.datetime.fromtimestamp(datastream['updateTime']/1000.0))))
    print_info("Events # : " + str(datastream['stats']['events']))
    # print_info(datastream['timePrecision'])
    if datastream['stats']['events'] > 0:
        if datastream['timePrecision'] != 'micro':
            print_info("Events Start Time : " + (str(datetime.datetime.fromtimestamp(datastream['stats']['earliestDataPoint']/1000.0))))
            print_info("Events End Time : " + (str(datetime.datetime.fromtimestamp(datastream['stats']['latestDataPoint']/1000.0))))
        else:
            print_info("Events Start Time : " + (str(datetime.datetime.fromtimestamp(datastream['stats']['earliestDataPoint']/1000000.0))))
            print_info("Events End Time : " + (str(datetime.datetime.fromtimestamp(datastream['stats']['latestDataPoint']/1000000.0))))

    else:
        print_info("Events Start Time : N/A")
        print_info("Events End Time : N/A")
    print_info("Time Format : " + datastream['field']['time']['format'])
    print_info("Time Zone : " + datastream['field']['time']['zone'])
    #print_info("Assessments: " + datastream.get_create_time())
    print_info("Live Monitoring: " + datastream['live'])
    if len(datastream['inputList']):
        signalList=[]
        for input in datastream['inputList']:
            signalList.append(input['name'])
        print_info("Signals: " +', '.join(signalList))
    else:
        print_info("Signals: N/A")
    #print_info("Entities: " + datastream['dataSource'])
    print_info("==================================================================================================================")


def print_assessment_details(assessment_str):
    assessment = json.loads(assessment_str)
    print_info("==================================================================================================================")
    print_info("Id : " + assessment['id'])
    print_info("Name : " + assessment['name'])
    print_info("Created By : " + assessment['createdBy'])
    print_info("Create Time : " + (str(datetime.datetime.fromtimestamp(assessment['createTime']/1000.0))))
    print_info("Update Time : " + (str(datetime.datetime.fromtimestamp(assessment['updateTime']/1000.0))))
    print_info("Datastream : " + assessment['datastream'])
    print_info("Live : " + assessment['live'])
    print_info("Rate : " + assessment['rate'])
    if len(assessment['aprioriConditionList']) ==0:
        print_info("Condition List : N/A")
    else:
        print_info("Apriori Condition List : " + str(', '.join(assessment['aprioriConditionList'])))
    print_info("==================================================================================================================")


def cli():
    app = REPL()
    app.cmdloop()

if __name__ == '__main__':
    cli()
