"""gRPC ExecutionEnvironment Server code - StorageLocation/EE methods."""

from io import BytesIO
import logging

from dataclay.commonruntime.Runtime import getRuntime
from dataclay.communication.grpc import Utils
from dataclay.communication.grpc.generated.dataservice import dataservice_pb2_grpc as ds
from dataclay.communication.grpc.messages.common import common_messages_pb2
from dataclay.communication.grpc.messages.dataservice import dataservice_messages_pb2
from dataclay.exceptions.exceptions import DataclayException
from dataclay.executionenv import ExecutionEnvironment
from dataclay.util.YamlParser import dataclay_yaml_load

__author__ = 'Enrico La Sala <enrico.lasala@bsc.es>'
__copyright__ = '2017 Barcelona Supercomputing Center (BSC-CNS)'

logger = logging.getLogger(__name__)

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class DataServiceEE(ds.DataServiceServicer):

    """ Execution environment being managed """
    execution_environment = None

    def __init__(self, theexec_env):
        self.execution_environment = theexec_env

    def ass_client(self):
        self.client = getRuntime().ready_clients["@STORAGE"]

    def deployMetaClasses(self, request, context):
        
        logger.debug("[deployMetaClasses] Deploying classes")

        try:
            namespace = request.namespace
            classes_map_yamls = request.deploymentPack 
            self.execution_environment.ds_deploy_metaclasses(namespace, classes_map_yamls)
            return common_messages_pb2.ExceptionInfo()

        except DataclayException as e:
            logger.warning("[deployMetaClasses] Received DataclayException with message:\n%s", e.message)
            return common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=Utils.prepare_exception("Check parameters: 'namespace name' and 'deployment pack'",
                                                             Utils.return_stack())
            )

        except NotImplementedError as e:
            logger.warning("[deployMetaClasses] Received NotImplementedError with message:\n%s", e.message)

            return common_messages_pb2.ExceptionInfo(
                isException=True,
                exceptionMessage=Utils.prepare_exception("Check parameters: 'namespace name' and 'deployment pack'",
                                                         Utils.return_stack())
            )

    def newPersistentInstance(self, request, context):

        try:
            iface_bit_maps = {}

            for k, v in request.ifaceBitMaps.iteritems():
                iface_bit_maps[Utils.get_id_from_uuid(k)] = bytes(v)

            params = []

            if request.params:
                params = Utils.get_param_or_return(request.params)

            oid = self.client.ds_new_persistent_instance(Utils.get_id(request.sessionID),
                                                         Utils.get_id(request.classID),
                                                         Utils.get_id(request.implementationID),
                                                         iface_bit_maps,
                                                         params)

            return dataservice_messages_pb2.NewPersistentInstanceResponse(objectID=Utils.get_msg_options['object'](oid))

        except DataclayException as e:
            logger.warning("[newPersistentInstance] Received DataclayException with message:\n%s", e.message)
            return dataservice_messages_pb2.NewPersistentInstanceResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=Utils.prepare_exception("Check parameters: 'session_id', 'class_id',"
                                                             " 'implementation_id', 'i_face_bitmaps' and 'params'",
                                                             Utils.return_stack()))
            )

        except NotImplementedError as e:
            logger.warning("[newPersistentInstance] Received NotImplementedError with message:\n%s", e.message)
            return dataservice_messages_pb2.NewPersistentInstanceResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=Utils.prepare_exception("Check parameters: 'session_id', 'class_id',"
                                                             " 'implementation_id', 'i_face_bitmaps' and 'params'",
                                                             Utils.return_stack()))
            )

    def storeObjects(self, request, context):
                
        try:
            objects_list = []
            for vol_param in request.objects:
                param = Utils.get_obj_with_data_param_or_return(vol_param)
                serialized_obj = BytesIO(param[3])
                dcobj = param[0], param[1], param[2], serialized_obj
                objects_list.append(dcobj)

            ids_with_alias_set = set()
            if request.idsWithAlias is not None and len(request.idsWithAlias) > 0:
                for ids_with_alias in request.idsWithAlias:
                    ids_with_alias_set.add(Utils.get_id(ids_with_alias))

            self.execution_environment.store_objects(request.sessionID, objects_list, request.moving, ids_with_alias_set)
            return common_messages_pb2.ExceptionInfo()

        except DataclayException as e:
            logger.error("[storeObjects] Received DataclayException with message:\n%s", e.message, exc_info=True)
            return common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=Utils.prepare_exception("Check parameters: 'session_id', 'objects', 'moving'"
                                                             " and 'ids_with_alias'",
                                                             Utils.return_stack())
            )

        except NotImplementedError as e:
            logger.error("[storeObjects] Received NotImplementedError with message:\n%s", e.message, exc_info=True)
            return common_messages_pb2.ExceptionInfo(
                isException=True,
                exceptionMessage=Utils.prepare_exception("Check parameters: 'session_id', 'objects', 'moving'"
                                                         " and 'ids_with_alias'",
                                                         Utils.return_stack())
            )
        
    def executeImplementation(self, request, context):
        
        try:
            object_id = Utils.get_id(request.objectID)
            implementation_id = Utils.get_id(request.implementationID)
            serialized_params = Utils.get_param_or_return(request.params)
            session_id = Utils.get_id(request.sessionID)
            try:
                result = self.execution_environment.ds_exec_impl(object_id, implementation_id, serialized_params, session_id)
            except DataclayException as de:
                logger.info("ExecuteImplementation finished with exception %s", de)
                return dataservice_messages_pb2.ExecuteImplementationResponse(
                    excInfo=common_messages_pb2.ExceptionInfo(
                        isException=True,
                        # ToDo fix the ugly /%s -> de/ to something more readable
                        exceptionMessage=Utils.prepare_exception("Exception during the Execution %s" % de, Utils.return_stack()))
                )
            logger.info("ExecuteImplementation finished, sending response")

            return dataservice_messages_pb2.ExecuteImplementationResponse(ret=Utils.get_param_or_return(result))

        # ToDo: Understand how to serialize and send exception

        except DataclayException as e:
            logger.warning("[executeImplementation] Received DataclayException with message:\n%s", e.message)
            return dataservice_messages_pb2.ExecuteImplementationResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    serializedException=bytes(e),
                    exceptionMessage=Utils.prepare_exception("Check parameters: 'object_id', 'implementation_id',"
                                                             " 'session_id' and 'params'",
                                                             Utils.return_stack()))
            )

        except NotImplementedError as e:
            logger.warning("[executeImplementation] Received NotImplementedError with message:\n%s", e.message)
            return dataservice_messages_pb2.ExecuteImplementationResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=Utils.prepare_exception("Check parameters: 'object_id', 'implementation_id',"
                                                             " 'session_id' and 'params'",
                                                             Utils.return_stack()))
            )

    def getObjects(self, request, context):
        try:
            object_ids = set()
            for oid in request.objectIDS:
                object_ids.add(Utils.get_id(oid))

            result = self.execution_environment.get_objects(Utils.get_id(request.sessionID),
                                            object_ids,
                                            request.recursive,
                                            request.moving)

            obj_list = []

            for entry in result:
                obj_list.append(Utils.get_obj_with_data_param_or_return(entry))

            return dataservice_messages_pb2.GetObjectsResponse(objects=obj_list)

        except DataclayException as e:
            logger.warning("[getObjects] Received DataclayException with message:\n%s", e.message)
            return dataservice_messages_pb2.GetObjectsResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=Utils.prepare_exception("Check parameters: 'session_id', 'object_ids',"
                                                             " 'recursive' and 'moving'",
                                                             Utils.return_stack()))
            )

        except NotImplementedError as e:
            logger.warning("[getObjects] Received NotImplementedError with message:\n%s", e.message)
            return dataservice_messages_pb2.GetObjectsResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=Utils.prepare_exception("Check parameters: 'session_id', 'object_ids',"
                                                             " 'recursive' and 'moving'",
                                                             Utils.return_stack()))
            )

    def newMetaData(self, request, context):

        try:
            md_infos = {}

            for k, v in request.mdInfos.iteritems():

                md_infos[Utils.get_id_from_uuid(k)] = dataclay_yaml_load(v)

            self.client.ds_new_metadata(md_infos)

            return common_messages_pb2.ExceptionInfo()

        except DataclayException as e:
            logger.warning("[newMetaData] Received DataclayException with message:\n%s", e.message)
            return common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=Utils.prepare_exception("Check parameter: 'md_infos'",
                                                             Utils.return_stack())
            )

        except NotImplementedError as e:
            logger.warning("[newMetaData] Received NotImplementedError with message:\n%s", e.message)
            return common_messages_pb2.ExceptionInfo(
                isException=True,
                exceptionMessage=Utils.prepare_exception("Check parameter: 'md_infos'",
                                                         Utils.return_stack())
            )

    def newVersion(self, request, context):

        try:
            result = self.execution_environment.new_version(
                Utils.get_id(request.sessionID),
                Utils.get_id(request.objectID),
                dataclay_yaml_load(request.metadataInfo)
            )

            vers_ids = dict()

            for k, v in result[1].iteritems():
                vers_ids[bytes(k)] = bytes(v)

            return dataservice_messages_pb2.NewVersionResponse(
                objectID=Utils.get_msg_options['object'](result[0]),
                versionedIDs=vers_ids
            )

        except DataclayException as e:
            logger.warning("[newVersion] Received DataclayException with message:\n%s", e.message)
            return dataservice_messages_pb2.NewVersionResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=Utils.prepare_exception("Check parameters: 'session_id', 'object_id'"
                                                             " and 'metadata_info'",
                                                             Utils.return_stack()))
            )

        except NotImplementedError as e:
            logger.warning("[newVersion] Received NotImplementedError with message:\n%s", e.message)
            return dataservice_messages_pb2.NewVersionResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=Utils.prepare_exception("Check parameters: 'session_id', 'object_id'"
                                                             " and 'metadata_info'",
                                                             Utils.return_stack()))
            )

    def consolidateVersion(self, request, context):

        try:
            self.execution_environment.consolidate_version(Utils.get_id(request.sessionID),
                                           dataclay_yaml_load(request.versionInfo))

            return common_messages_pb2.ExceptionInfo()

        except DataclayException as e:
            logger.warning("[consolidateVersion] Received DataclayException with message:\n%s", e.message)
            return common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=Utils.prepare_exception("Check parameters: 'session_id' and 'version_info'",
                                                             Utils.return_stack())
            )

        except NotImplementedError as e:
            logger.warning("[consolidateVersion] Received NotImplementedError with message:\n%s", e.message)
            return common_messages_pb2.ExceptionInfo(
                isException=True,
                exceptionMessage=Utils.prepare_exception("Check parameters: 'session_id' and 'version_info'",
                                                         Utils.return_stack())
            )

    def upsertObjects(self, request, context):

        try:
            session_id = Utils.get_id(request.sessionID)

            objects = []
            for entry in request.bytesUpdate:
                objects.append(Utils.get_obj_with_data_param_or_return(entry))

            self.execution_environment.upsert_objects(session_id, objects)

            return common_messages_pb2.ExceptionInfo()

        except DataclayException as e:
            logger.warning("[upsertObjects] Received DataclayException with message:\n%s", e.message)
            return common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=Utils.prepare_exception("Check parameters: 'session_id' and 'object_bytes'",
                                                             Utils.return_stack())
            )

        except NotImplementedError as e:
            logger.warning("[upsertObjects] Received NotImplementedError with message:\n%s", e.message)
            return common_messages_pb2.ExceptionInfo(
                isException=True,
                exceptionMessage=Utils.prepare_exception("Check parameters: 'session_id' and 'object_bytes'",
                                                         Utils.return_stack())
            )

    def newReplica(self, request, context):

        ##### NOT WELL IMPL. NEW ALGORITHM MISSING FOR MOVING OBJECTS CHECKING FIRST THE MEMORY ######

        try:
            result = self.execution_environment.new_replica(Utils.get_id(request.sessionID),
                                            Utils.get_id(request.objectID),
                                            request.recursive)

            repl_ids_list = []

            for oid in result:
                repl_ids_list.append(Utils.get_msg_options['object'](oid))

            return dataservice_messages_pb2.NewReplicaResponse(
                replicatedIDs=repl_ids_list
            )

        except DataclayException as e:
            logger.warning("[newReplica] Received DataclayException with message:\n%s", e.message)
            return dataservice_messages_pb2.NewReplicaResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=Utils.prepare_exception("Check parameters: 'session_id' and 'object_id'",
                                                             Utils.return_stack()))
            )

        except NotImplementedError as e:
            logger.warning("[newReplica] Received NotImplementedError with message:\n%s", e.message)
            return dataservice_messages_pb2.NewReplicaResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=Utils.prepare_exception("Check parameters: 'session_id' and 'object_id'",
                                                             Utils.return_stack()))
            )

    def moveObjects(self, request, context):

        ##### NOT WELL IMPL. NEW ALGORITHM MISSING FOR MOVING OBJECTS CHECKING FIRST THE MEMORY ######

        try:
            result = self.client.ds_move_objects(Utils.get_id(request.sessionID),
                                                 Utils.get_id(request.objectID),
                                                 Utils.get_id(request.destLocID),
                                                 request.recursive)

            mov_obj_list = []

            for oid in result:
                mov_obj_list.append(Utils.get_msg_options['object'](oid))

            return dataservice_messages_pb2.MoveObjectsResponse(
                movedObjects=mov_obj_list
            )

        except DataclayException as e:
            logger.warning("[moveObjects] Received DataclayException with message:\n%s", e.message)
            return dataservice_messages_pb2.MoveObjectsResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=Utils.prepare_exception("Check parameters: 'session_id', 'object_id',"
                                                             " 'dest_st_location' and 'recursive'",
                                                             Utils.return_stack()))
            )

        except NotImplementedError as e:
            logger.warning("[moveObjects] Received NotImplementedError with message:\n%s", e.message)
            return dataservice_messages_pb2.MoveObjectsResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=Utils.prepare_exception("Check parameters: 'session_id', 'object_id',"
                                                             " 'dest_st_location' and 'recursive'",
                                                             Utils.return_stack()))
            )

    def removeObjects(self, request, context):

        try:
            object_ids = set()

            for oid in request.getObjectsIDSList():
                object_ids.add(Utils.get_id(oid))

            result = self.client.ds_remove_objects(Utils.get_id(request.sessionID),
                                                   object_ids,
                                                   request.recursive,
                                                   request.moving,
                                                   Utils.get_id(request.newHint))

            rem_obj = dict()

            for k, v in result.iteritems():
                rem_obj[str(k)] = str(v)

            return dataservice_messages_pb2.RemoveObjectsResponse(
                removedObjects=rem_obj
            )

        except DataclayException as e:
            logger.warning("[removeObjects] Received DataclayException with message:\n%s", e.message)
            return dataservice_messages_pb2.RemoveObjectsResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=Utils.prepare_exception("Check parameters: 'session_id', 'object_ids',"
                                                             " 'recursive', 'moving' and 'new_hint'",
                                                             Utils.return_stack()))
            )

        except NotImplementedError as e:
            logger.warning("[removeObjects] Received NotImplementedError with message:\n%s", e.message)
            return dataservice_messages_pb2.RemoveObjectsResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=Utils.prepare_exception("Check parameters: 'session_id', 'object_ids',"
                                                             " 'recursive', 'moving' and 'new_hint'",
                                                             Utils.return_stack()))
            )

    def migrateObjectsToBackends(self, request, context):

        try:
            backends = dict()

            for k, v in request.destStorageLocs.iteritems():
                backends[Utils.get_id_from_uuid(k)] = dataclay_yaml_load(v)

            result = self.client.ds_migrate_objects_to_backends(backends)

            migr_obj_res = dict()

            for k, v in result[0].iteritems():
                migrated_obj_builder = dataservice_messages_pb2.MigratedObjects()

                for oid in v:
                    migrated_obj_builder(objs=Utils.get_msg_options['object'](oid))
                migr_obj_res[str(k)] = migrated_obj_builder

            non_migrated_objs_builder = dataservice_messages_pb2.MigratedObjects()

            non_migr_obj_res = []

            for oid in result[1]:
                non_migrated_objs_builder(objs=Utils.get_msg_options['object'](oid))

            non_migr_obj_res.append(non_migrated_objs_builder)

            return dataservice_messages_pb2.MigrateObjectsResponse(
                migratedObjs=migr_obj_res,
                nonMigratedObjs=non_migr_obj_res
            )

        except DataclayException as e:
            logger.warning("[migrateObjectsToBackends] Received DataclayException with message:\n%s", e.message)
            return dataservice_messages_pb2.MigrateObjectsResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=Utils.prepare_exception("Check parameter: 'back_ends'",
                                                             Utils.return_stack()))
            )

        except NotImplementedError as e:
            logger.warning("[migrateObjectsToBackends] Received NotImplementedError with message:\n%s", e.message)
            return dataservice_messages_pb2.MigrateObjectsResponse(
                excInfo=common_messages_pb2.ExceptionInfo(
                    isException=True,
                    exceptionMessage=Utils.prepare_exception("Check parameter: 'back_ends'",
                                                             Utils.return_stack()))
            )
