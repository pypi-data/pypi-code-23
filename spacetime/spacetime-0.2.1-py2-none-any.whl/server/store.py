'''
Created on Apr 19, 2016

@author: Rohan Achar
'''
import json
import dill
import pkgutil
import importlib
import inspect
from time import sleep
from rtypes.pcc.utils.recursive_dictionary import RecursiveDictionary
from spacetime.common.wire_formats import FORMATS
from datamodel.all import DATAMODEL_TYPES
from rtypes.dataframe.dataframe_threading import dataframe_wrapper as dataframe
from rtypes.dataframe.application_queue import ApplicationQueue
from spacetime.common.modes import Modes
from spacetime.common.converter import create_jsondict, create_complex_obj
from spacetime.common.crawler_generator import generate_datamodel
from rtypes.pcc.triggers import TriggerProcedure
from rtypes.connectors.sql import RTypesMySQLConnection

FETCHING_MODES = set([Modes.Getter, 
                      Modes.GetterSetter,
                      Modes.Taker])
TRACKING_MODES = set([Modes.Tracker])
PUSHING_MODES = set([Modes.Deleter,
                     Modes.GetterSetter,
                     Modes.Setter,
                     Modes.TakerSetter,
                     Modes.Producing])
ALL_MODES = set([Modes.Deleter,
                 Modes.GetterSetter,
                 Modes.Setter,
                 Modes.TakerSetter,
                 Modes.Producing,
                 Modes.Tracker,
                 Modes.Getter])

def load_db():
        cred = json.load(open("creds.json"))
        return RTypesMySQLConnection(
            user=cred["username"], password=cred["password"],
            host="127.0.0.1", database="IR_W18_Crawler")

class dataframe_stores(object):
    def load_all_sets(self, app_name):
        app_id = app_name.split("_")[-1]
        uas, filename, typenames = generate_datamodel(app_id)
        classes = list()
        mod = importlib.import_module("datamodel.search." + filename + "_datamodel")
        reload(mod)
        for name, cls in inspect.getmembers(mod):
            if hasattr(cls, "__rtypes_metadata__"):
               self.name2class[cls.__rtypes_metadata__.name] = cls
            if isinstance(cls, TriggerProcedure):
               self.name2class[cls.name] = cls
        return {
            Modes.Producing: set([self.name2class["datamodel.search.{0}_datamodel.{0}Link".format(app_id)]]),
            Modes.GetterSetter: set([self.name2class["datamodel.search.{0}_datamodel.One{0}UnProcessedLink".format(app_id)]]),
            Modes.Triggers: set([self.name2class["datamodel.search.{0}_datamodel.get_downloaded_content".format(app_id)], self.name2class["datamodel.search.{0}_datamodel.add_server_copy".format(app_id)]])
        }

    def parse_type(self, app_name, mode_map):
        if all(tpname in self.name2class
               for mode, mode_types in mode_map.iteritems()
               for tpname in mode_types):
            return {mode: [self.name2class[tpname] for tpname in mode_types]
                    for mode, mode_types in mode_map.iteritems()}
        else:
            return self.load_all_sets(app_name)
        return tp

    def __init__(self, name2class):
        self.sql_con = load_db()
        self.master_dataframe = dataframe(external_db=self.sql_con)
        self.app_to_df = {}
        self.name2class = name2class
        self.pause_servers = False
        self.app_wire_format = {}
        self.master_dataframe.add_types(self.name2class.values())

    def __pause(self):
        while self.pause_servers:
            sleep(0.1)
        
    def add_new_dataframe(self, name, df):
        self.__pause()    
        self.app_to_df[name] = df

    def delete_app(self, app):
        self.__pause()
        del self.app_to_df[app]

    def register_app(self, app, serialized_type_map, wire_format="json"):
        self.__pause()
        type_map = self.parse_type(app, serialized_type_map)
        types_to_get = set()
        for mode in FETCHING_MODES:
            types_to_get.update(set(type_map.setdefault(mode, set())))
        types_to_track = set()
        for mode in TRACKING_MODES:
            types_to_track.update(set(type_map.setdefault(mode, set())))
        types_to_track = types_to_track.difference(types_to_get)
        real_types_to_get = [tpg for tpg in types_to_get]
        real_types_to_track = [tpt for tpt in types_to_track]
        self.master_dataframe.add_types(
            real_types_to_get + real_types_to_track)

        df = ApplicationQueue(
            app, real_types_to_get + real_types_to_track,
            self.master_dataframe)
        self.add_new_dataframe(app, df)
        # Add all types to master.
        types_to_add_to_master = set()
        for mode in ALL_MODES:
            types_to_add_to_master.update(
                set(type_map.setdefault(mode, set())))
        all_types = [tpam for tpam in types_to_add_to_master]
        self.master_dataframe.add_types(all_types)
        for tp in all_types:
            self.name2class.setdefault(tp.__rtypes_metadata__.name, tp)
        self.app_wire_format[app] = wire_format

        if Modes.Triggers in type_map:
            triggers = [
                fn for fn in type_map[Modes.Triggers]]
            if triggers:
                self.master_dataframe.add_triggers(triggers)

    def disconnect(self, app):
        self.__pause()
        if app in self.app_to_df:
            self.delete_app(app)

    def reload_dms(self, datamodel_types):
        self.__pause()
        pass

    def update(self, app, changes):
        # print json.dumps(
        #       changes, sort_keys=True, separators=(',', ': '), indent=4) 
        self.__pause()
        dfc_type, content_type = FORMATS[self.app_wire_format[app]]
        dfc = dfc_type()
        dfc.ParseFromString(changes)
        if app in self.app_to_df:
            self.master_dataframe.apply_changes(dfc, except_app=app)
        if self.sql_con:
            self.master_dataframe.push()

    def getupdates(self, app):
        self.__pause()
        dfc_type, content_type = FORMATS[self.app_wire_format[app]]
        final_updates = dfc_type()
        if app in self.app_to_df:
            final_updates = dfc_type(self.app_to_df[app].get_record())
            self.app_to_df[app].clear_record()
        return final_updates.SerializeToString(), content_type

    def get_app_list(self):
        return self.app_to_df.keys()

    def clear(self, tp = None):
        if not tp:
            self.__init__(self.name2class)
        else:
            if tp in self.master_dataframe.object_map:
                del self.master_dataframe.object_map[tp]
            if tp in self.master_dataframe.current_state:
                del self.master_dataframe.current_state[tp]

    def pause(self):
        self.pause_servers = True

    def unpause(self):
        self.pause_servers = False

    def gc(self, sim):
        # For now not clearing contents
        self.delete_app(sim)
        

    def get(self, tp):
        return [create_jsondict(o) for o in self.master_dataframe.get(tp)]

    def put(self, tp, objs):
        real_objs = [
            create_complex_obj(tp, obj, self.master_dataframe.object_map)
            for obj in objs.values()]
        tpname = tp.__rtypes_metadata__.name
        gkey =  self.master_dataframe.member_to_group[tpname]
        if gkey == tpname:
            self.master_dataframe.extend(tp, real_objs)
        else:
            for obj in real_objs:
                oid = obj.__primarykey__
                if oid in self.master_dataframe.object_map[gkey]:
                    # do this only if the object is already there.
                    # cannot add an object if it is a subset
                    # (or any other pcc type) type if it doesnt exist.
                    for dim in obj.__dimensions__:
                        # setting attribute to the original object,
                        # so that changes cascade
                        setattr(
                            self.master_dataframe.object_map[gkey][oid],
                            dim._name, getattr(obj, dim._name))
        


