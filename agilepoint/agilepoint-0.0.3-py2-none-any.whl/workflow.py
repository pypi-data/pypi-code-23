"""Workflow Methods for AgilePoint API"""
import json
from ._utils import handle_response, validate_args
# pylint: disable=too-many-public-methods,too-many-lines


class Workflow(object):
    """Workflow Methods for AgilePoint API"""
    def __init__(self, agilepoint):
        self.workflow = agilepoint.agilepoint.Workflow
        self.agilepoint = agilepoint

    def activate_work_item(self, workitemid, activate, **kwargs):
        """Activates a work item.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodActivateWorkItem.html

        Path Args: workItemID, activate
        Required Body Args: clientData
        Optional Body Args: None"""
        req_args = ['clientData']
        validate_args(kwargs, req_args)
        resp = self.workflow.ActivateWorkItem(workitemid)(
            activate).POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def archive_proc_inst(self, procinstid):
        """Archives a process instance based on a specified process instance
        identifier by moving the set of process instance records from the
        current AgilePoint Database into the AgilePoint Archive Database.
        The process instance records and all of the associated data are then
        deleted from the AgilePoint Database. The process instance to be
        archived must be completed or canceled.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodArchiveProcInst.html

        Path Args: procInstID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.ArchiveProcInst(procinstid).POST()
        return handle_response('bool', resp)

    def assign_work_item(self, workitemid, **kwargs):
        """Assigns a work item to a user, which often means claiming a work
        item for oneself. This is often used with task pools where work items
        are created, and then multiple users are notified, but the work item
        is not immediately assigned to a user. A user then claims the work item,
        or his manager assigns it to him. The user must have privileges to
        claim or assign the work item.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodAssignWorkItem.html

        Path Args: workItemID
        Required Body Args: clientData
        Optional Body Args: None"""
        req_args = ['clientData']
        validate_args(kwargs, req_args)
        resp = self.workflow.AssignWorkItem(workitemid).POST(
            data=json.dumps(kwargs))
        return handle_response('json', resp)

    def cancel_activity_inst(self, activityinstanceid):
        """Cancels a manual activity instance along with all manual work items
        associated with the specified manual activity instance ID. Note that an
        activity instance can be associated with one or more manual work items.
        Once the manual activity instance is canceled, the process instance will
        move forward to the next activity.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodCancelActivityInst.html

        Path Args: activityInstanceID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.CancelActivityInst(activityinstanceid).POST()
        return handle_response('json', resp)

    def cancel_mail_deliverable(self, mailid):
        """Cancels the failed mail deliverable record based on a given message
        identifier. Note that canceling the failed mail deliverable record
        prevents it from being recycled or present on a given interval by the
        AgilePoint engine.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodCancelMailDeliverable.html

        Path Args: mailID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.CancelMailDeliverable(mailid).POST()
        return handle_response('bool', resp)

    def cancel_procedure(self, workitemid):
        """Cancels an automatic work item based on supplied specified automatic
        work item identifier.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodCancelProcedure.html

        Path Args: workItemID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.CancelProcedure(workitemid).POST()
        return handle_response('json', resp)

    def cancel_proc_inst(self, processinstanceid):
        """Cancels the process instance based on a specified process instance
        identifier. This method cancels all automatic work items, manual work
        items, and child process instances.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodCancelProcInst.html

        Path Args: processInstanceID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.CancelProcInst(processinstanceid).POST()
        return handle_response('json', resp)

    def cancel_work_item(self, workitemid, **kwargs):
        """Cancels a manual work item based on a specified manual work item
        identifier. Only the following manual work item status can transition
        to a Canceled status: Assigned, New, Pseudo, and Overdue.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodCancelWorkItem.html

        Path Args: workItemID
        Required Body Args: clientData
        Optional Body Args: None"""
        req_args = ['clientData']
        validate_args(kwargs, req_args)
        resp = self.workflow.CancelWorkItem(
            workitemid).POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def checkin_proc_def(self, **kwargs):
        """Checks in the process definition to the AgilePoint Server and returns
        the process definition identifier. This method accepts a string with the
        updated process definition in XML format.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodCheckinProcDef.html

        Path Args: None
        Required Body Args: xml
        Optional Body Args: None"""
        req_args = ['xml']
        validate_args(kwargs, req_args)
        resp = self.workflow.CheckinProcDef.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def checkout_proc_def(self, processtemplateid):
        """This method is used to manage process definition versioning by
        setting the process definition status to CheckedOut based on a given
        process definition ID. Only process definitions with the status of
        Released can transition into the CheckedOut status.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodCheckoutProcDef.html

        Path Args: processTemplateID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.CheckoutProcDef(processtemplateid).POST()
        return handle_response('text', resp)

    def complete_procedure(self, workitemid):
        """Marks an automatic work item as completed by an asynchronous
        activity.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodCompleteProcedure.html

        Path Args: workItemID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.CompleteProcedure(workitemid).POST()
        return handle_response('json', resp)

    def complete_work_item(self, workitemid, **kwargs):
        """Marks a work item as completed.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodCompleteWorkItem.html

        Path Args: None
        Required Body Args: clientData
        Optional Body Args: None"""
        req_args = ['clientData']
        validate_args(kwargs, req_args)
        resp = self.workflow.CompleteWorkItem(workitemid).POST(
            data=json.dumps(kwargs))
        return handle_response('json', resp)

    def create_linked_work_item(self, **kwargs):
        """Creates a manual work item that is linked to another manual work
        item. The work item you create does not depend on the completion of
        the work item to which it is linked. In other words, the original
        (source) work item can be marked as completed before new work item is
        completed.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodCreateLinkedWorkItem.html

        Path Args: None
        Required Body Args: bDependent, BusinessTime, ClientData, Length,
                            SourceWorkItemID, Unit, UserID, WorkToPerform
        Optional Body Args: None"""
        req_args = ['bDependent', 'BusinessTime', 'ClientData', 'Length',
                    'SourceWorkItemID', 'Unit', 'UserID', 'WorkToPerform']
        validate_args(kwargs, req_args)
        resp = self.workflow.CreateLinkedWorkItem.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def create_proc_def(self, **kwargs):
        """Adds a new process definition to the AgilePoint Server.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodCreateProcDef.html

        Path Args: None
        Required Body Args: xml
        Optional Body Args: None"""
        resp = self.workflow.CreateProcDef.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def create_proc_inst(self, **kwargs):
        """Creates a process instance for a specified process definition ID and
        parameters.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodCreateProcInst.html

        Path Args: None
        Required Body Args: Attributes, blnStartImmediately, CustomID,
                            Initiator, ProcessID, ProcessInstID, ProcInstName,
                            SuperProcInstID, WorkObjID, WorkObjInfo
        Optional Body Args: None"""
        req_args = ['Attributes', 'blnStartImmediately', 'CustomID',
                    'Initiator', 'ProcessID', 'ProcessInstID', 'ProcInstName',
                    'SuperProcInstID', 'WorkObjID', 'WorkObjInfo']
        validate_args(kwargs, req_args)
        resp = self.workflow.CreateProcInst.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def create_pseudo_work_item(self, **kwargs):
        """Creates a task by a specific AgileWork or other module that has the
        following characteristics:

            * It does not have to be completed in order for a process to advance
                to the next steps.
            * Unless specifically canceled, it remains active through the
                duration of the entire process, not just the duration of the
                AgileWork or other module that created it.

        This provides a way for tasks to be included in a user's or manager's
        task list purely for monitoring purposes.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodCreatePseudoWorkItem.html

        Path Args: None
        Required Body Args: bReserved, BusinessTime, ClientData, Length,
                            SourceWorkItemID, Unit, UserID, WorkToPerform
        Optional Body Args: None"""
        req_args = ['bReserved', 'BusinessTime', 'ClientData', 'Length',
                    'SourceWorkItemID', 'Unit', 'UserID', 'WorkToPerform']
        validate_args(kwargs, req_args)
        resp = self.workflow.CreatePseudoWorkItem.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def create_work_item(self, **kwargs):
        """Creates a manual work item that is linked to another manual work
        item. The work item you create does not depend on the completion of the
        work item to which it is linked. In other words, the original (source)
        work item can be marked as completed before new work item is completed.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodCreateWorkItem.html

        Path Args: None
        Required Body Args: bDependent, BusinessTime, ClientData, Length,
                            SourceWorkItemID, Unit, UserID, WorkToPerform
        Optional Body Args: None"""
        req_args = ['bReserved', 'BusinessTime', 'ClientData', 'Length',
                    'SourceWorkItemID', 'Unit', 'UserID', 'WorkToPerform']
        validate_args(kwargs, req_args)
        resp = self.workflow.CreateWorkItem.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def delete_custom_attrs(self, customid):
        """Deletes multiple custom attributes using a custom ID.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodDeleteCustomAttrs.html

        Path Args: customID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.DeleteCustomAttrs(customid).POST()
        return handle_response('bool', resp)

    def delete_proc_def(self, processtemplateid):
        """Deletes the process definition and all of the process instances
        associated with the process definition. The process definition cannot be
        deleted if one or more process instances associated with the process
        definition is running or suspended. The function may take a long time to
        execute if there are many process instances associated with the process
        definition.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodDeleteProcDef.html

        Path Args: processTemplateID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.DeleteProcDef(processtemplateid).POST()
        return handle_response('bool', resp)

    def delete_proc_inst(self, processinstanceid):
        """Deletes a process instance. This method removes the specified process
        instance and all the associated data from the database, such as work
        items, email, and activity instances associated with this process
        instance. It may take some time to complete this transaction.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodDeleteProcInst.html

        Path Args: processInstanceID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.DeleteProcInst(processinstanceid).POST()
        return handle_response('bool', resp)

    def get_activity_inst(self, activityinstanceid):
        """Retrieves basic information for a specified activity instance.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetActivityInst.html

        Path Args: activityInstanceID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.GetActivityInst(activityinstanceid).GET()
        return handle_response('json', resp)

    def get_activity_insts_by_p_i_i_d(self, processinstanceid):
        """Retrieves the status of all activity instances for a specified
        process instance.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetActivityInstsByPIID.html

        Path Args: processInstanceID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.GetActivityInstsByPIID(processinstanceid).GET()
        return handle_response('json', resp)

    def get_activity_inst_status(self, procinstid):
        """Retrieves all the status of all activity instances for a specified
        process instance.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetActivityInstStatus.html

        Path Args: procInstID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.GetActivityInstStatus(procinstid).GET()
        return handle_response('json', resp)

    def get_base_proc_def_id(self, procdefname):
        """Retrieves the ID for the first version of the process definition,
        called the base process definition. All subsequent process definition
        versions have the same base process definition ID. This call retrieves
        the base process definition ID with the specified process definition
        name.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetBaseProcDefID.html

        Path Args: procDefName
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.GetBaseProcDefID(procdefname).GET()
        return handle_response('json', resp)

    def get_custom_attr(self, customid, **kwargs):
        """Retrieves a single custom attribute.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetCustomAttr.html

        Path Args: customID
        Required Body Args: attrName
        Optional Body Args: None"""
        req_args = ['attrName']
        validate_args(kwargs, req_args)
        resp = self.workflow.GetCustomAttr(customid).POST(
            data=json.dumps(kwargs))
        return handle_response('json', resp)

    def get_custom_attrsby_id(self, customid):
        """Gets all the custom attributes with the specified array of custom
        IDs.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetCustomAttrsbyID.html

        Path Args: customID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.GetCustomAttrsbyID(customid).GET()
        return handle_response('json', resp)

    def get_custom_attrs_by_names(self, **kwargs):
        """Retrieves a list of custom attributes using their names or xpaths.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetCustomAttrsByNames.html

        Path Args: None
        Required Body Args: AttrNames, CustomIDs
        Optional Body Args: None"""
        req_args = ['AttrNames', 'CustomIDs']
        validate_args(kwargs, req_args)
        resp = self.workflow.GetCustomAttrsByNames.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def get_event(self, eventid):
        """Retrieves an event object. This service call is usually used to
        check if a service call has been completed.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetEvent.html

        Path Args: eventID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.GetEvent(eventid).GET()
        return handle_response('json', resp)

    def get_events_by_proc_inst_i_d(self, processinstanceid):
        """Retrieves all the events that have occurred for a specified process
        instance.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetEventsByProcInstID.html

        Path Args: processInstanceID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.GetEventsByProcInstID(processinstanceid).GET()
        return handle_response('json', resp)

    def get_expecting_send_mail_deliverable(self):  # pylint: disable=invalid-name
        """Retrieves all the failed and scheduled to resend email notifications.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetExpectingSendMailDeliverable.html

        Path Args: None
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.GetExpectingSendMailDeliverable.GET()
        return handle_response('json', resp)

    def get_mail_deliverables(self):
        """Retrieves all the global email templates from the server.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetMailDeliverables.html

        Path Args: None
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.GetMailDeliverables.GET()
        return handle_response('json', resp)

    def get_proc_def_by_base_pid(self, baseprocesstemplateid):
        """Retrieves all process definitions by a specified base process
        definition ID.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetProcDefByBasePID.html

        Path Args: baseprocessTemplateID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.GetProcDefByBasePID(baseprocesstemplateid).GET()
        return handle_response('json', resp)

    def get_proc_def_graphics(self, processid):
        """Retrieves graphical data for the process definition in XML format.
        The graphical representation of the process is XML-serialized by the
        class Graphic Image. The graphical data is used to display the process
        visually.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetProcDefGraphics.html

        Path Args: processID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.GetProcDefGraphics(processid).GET()
        return handle_response('json', resp)

    def get_proc_def_name_version(self, processtemplateid):
        """Retrieves the process definition name and version.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetProcDefNameVersion.html

        Path Args: processTemplateID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.GetProcDefNameVersion(processtemplateid).GET()
        return handle_response('json', resp)

    def get_proc_defs(self):
        """Retrieves all of process definition objects.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetProcDefs.html

        Path Args: None
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.GetProcDefs.GET()
        return handle_response('json', resp)

    def get_proc_def_supplement(self, processdefinitionid, activitydefinitionid):
        """Retrieves all the process definition objects and activity objects.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetProcDefSupplement.html

        Path Args: processDefinitionID, activityDefinitionID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.GetProcDefSupplement(
            processdefinitionid)(activitydefinitionid).GET()
        return handle_response('json', resp)

    def get_proc_def_xml(self, processtemplateid):
        """Retrieves a process definition in XML format.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetProcDefXml.html

        Path Args: processTemplateID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.GetProcDefXml(processtemplateid).GET()
        return handle_response('json', resp)

    def get_procedure(self, workitemid):
        """Retrieves work item data by a specified work item ID.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetProcedure.html

        Path Args: workItemID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.GetProcedure(workitemid).GET()
        return handle_response('json', resp)

    def get_proc_inst_attr(self, processinstanceid, attributename):
        """Retrieves a single attribute for a specified process instance.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetProcInstAttr.html

        Path Args: processInstanceID, attributeName
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.GetProcInstAttr(
            processinstanceid)(attributename).GET()
        return handle_response('json', resp)

    def get_proc_inst_attrs(self, processinstanceid):
        """Retrieves multiple attributes of a process instance.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetProcInstAttrs.html

        Path Args: processInstanceID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.GetProcInstAttrs(processinstanceid).GET()
        return handle_response('json', resp)

    def get_proc_inst(self, processinstanceid):
        """Retrieves basic information about a specified process instance.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetProcInst.html

        Path Args: processInstanceID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.GetProcInst(processinstanceid).GET()
        return handle_response('json', resp)

    def get_released_p_i_d(self, procdefname):
        """Retrieves the released process definition ID by a specified process
        definition name.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetReleasedPID.html

        Path Args: procDefName
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.GetReleasedPID(procdefname).GET()
        return handle_response('json', resp)

    def get_released_proc_defs(self):
        """Retrieves the names and IDs of all released process definitions.

        Path Args: None
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.GetReleasedProcDefs.GET()
        return handle_response('json', resp)

    def get_uuid(self):
        """Retrieves the UUID generated by the AgilePoint Server.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetUUID.html

        Path Args: None
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.GetUUID.GET()
        return handle_response('json', resp)

    def get_work_item(self, workitemid):
        """Retrieves the manual work item object for a specified ID.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetWorkItem.html

        Path Args: workItemID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.GetWorkItem(workitemid).GET()
        return handle_response('json', resp)

    def get_work_list_by_user_i_d(self, **kwargs):
        """Retrieves a work item collection by specifying a user name and work
        item status.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodGetWorkListByUserID.html

        Path Args: None
        Required Body Args: Status, UserName
        Optional Body Args: None"""
        req_args = ['Status', 'UserName']
        validate_args(kwargs, req_args)
        resp = self.workflow.GetWorkListByUserID.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def merge_proc_insts(self, **kwargs):
        """Merges 2 or more process instances into one process instance.

        These process instances should be based on the same process definition.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodMergeProcInsts.html

        Path Args: None
        Required Body Args: MergingProcessInstanceIDs, MergedProcessInstance
        Optional Body Args: None"""
        req_args = ['MergingProcessInstanceIDs', 'MergedProcessInstance']
        validate_args(kwargs, req_args)
        resp = self.workflow.MergeProcInsts.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def migrate_proc_inst(self, processinstanceid, reserved='', **kwargs):
        """Migrates a process definition from one version to another version.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodMigrateProcInst.html

        Path Args: processInstanceID, reserved
        Required Body Args: IncludeXmlData, Action, MatchingActivityDefinition,
                            SourceProcessDefinitionID, TargetProcessDefinitionID
        Optional Body Args: None"""
        req_args = ['IncludeXmlData', 'Action', 'MatchingActivityDefinition',
                    'SourceProcessDefinitionID', 'TargetProcessDefinitionID']
        validate_args(kwargs, req_args)
        resp = self.workflow.MigrateProcInst(processinstanceid)(
            reserved).POST(data=json.dumps(kwargs))
        return handle_response('bool', resp)

    def query_activity_insts(self, **kwargs):
        """Retrieves activity instances that match a query expression.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodQueryActivityInsts.html

        Path Args: None
        Required Body Args: ColumnName, Operator, IsValue
        Optional Body Args: None"""
        req_args = ['ColumnName', 'Operator', 'IsValue']
        validate_args(kwargs, req_args)
        resp = self.workflow.QueryActivityInsts.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def query_audit_trail(self, **kwargs):
        """Retrieves all audit trail items.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodQueryAuditTrail.html

        Path Args: None
        Required Body Args: where
        Optional Body Args: None"""
        req_args = ['where']
        validate_args(kwargs, req_args)
        resp = self.workflow.QueryAuditTrail.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def query_database(self, **kwargs):
        """Queries the database with any valid sql query and returns the dataset
        as a string in XML format.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodQueryDatabase.html

        Path Args: None
        Required Body Args: sql
        Optional Body Args: None"""
        req_args = ['sql']
        validate_args(kwargs, req_args)
        resp = self.workflow.QueryDatabase.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def query_procedure_list(self, **kwargs):
        """Retrieves a list of automatic work items that match a specified query
        expression.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodQueryProcedureList.html

        Path Args: None
        Required Body Args: ColumnName, Operator, WhereClause, IsValue
        Optional Body Args: None"""
        req_args = ['ColumnName', 'Operator', 'WhereClause', 'IsValue']
        validate_args(kwargs, req_args)
        resp = self.workflow.QueryProcedureList.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def query_proc_insts(self, **kwargs):
        """Retrieves a list of process instances that match a specified query
        expression. The WFQueryExpr string is used to generate a query
        expression, and the client application specifies the query terms.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodQueryProcInsts.html

        Path Args: None
        Required Body Args: ColumnName, Operator, IsValue
        Optional Body Args: None"""
        req_args = ['ColumnName', 'Operator', 'IsValue']
        validate_args(kwargs, req_args)
        resp = self.workflow.QueryProcInsts.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def query_proc_insts_using_s_q_l(self, **kwargs):
        """Retrieves a list of process instance based on specified query
        expression.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodQueryProcInstsUsingSQL.html

        Path Args: None
        Required Body Args: sqlWhereClause
        Optional Body Args: None"""
        req_args = ['sqlWhereClause']
        validate_args(kwargs, req_args)
        resp = self.workflow.QueryProcInstsUsingSQL.POST(
            data=json.dumps(kwargs))
        return handle_response('json', resp)

    def query_work_list(self, **kwargs):
        """Retrieves a list of manual work items that match a specified query
        expression.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodQueryWorkList.html

        Path Args: None
        Required Body Args: ColumnName, Operator, WhereClause, IsValue
        Optional Body Args: None"""
        req_args = ['ColumnName', 'Operator', 'WhereClause', 'IsValue']
        validate_args(kwargs, req_args)
        resp = self.workflow.QueryWorkList.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def query_work_list_using_s_q_l(self, **kwargs):
        """Retrieves a list of manual work items based on specified query
        expression.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodQueryWorkListUsingSQL.html

        Path Args: None
        Required Body Args: sqlWhereClause
        Optional Body Args: None"""
        req_args = ['sqlWhereClause']
        validate_args(kwargs, req_args)
        resp = self.workflow.QueryWorkListUsingSQL.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def reassign_work_item(self, **kwargs):
        """Reassigns a work item to another participant, and update the user
        name.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodReassignWorkItem.html

        Path Args: None
        Required Body Args: ClientData, UserName, WorkItemID
        Optional Body Args: None"""
        req_args = ['ClientData', 'UserName', 'WorkItemID']
        validate_args(kwargs, req_args)
        resp = self.workflow.ReassignWorkItem.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def release_proc_def(self, processtemplateid):
        """Releases a process definition from the AgilePoint Server.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodReleaseProcDef.html

        Path Args: processTemplateID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.ReleaseProcDef(processtemplateid).POST()
        return handle_response('bool', resp)

    def remove_custom_attr(self, customid, **kwargs):
        """Removes a custom attribute from a custom ID.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodRemoveCustomAttr.html

        Path Args: customID
        Required Body Args: attributeName
        Optional Body Args: None"""
        req_args = ['attributeName']
        validate_args(kwargs, req_args)
        resp = self.workflow.RemoveCustomAttr(customid).POST(
            data=json.dumps(kwargs))
        return handle_response('bool', resp)

    def remove_custom_attrs(self, customid, **kwargs):
        """Removes multiple custom attributes from a custom ID.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodRemoveCustomAttrs.html

        Path Args: customID
        Required Body Args: namesArray
        Optional Body Args: None"""
        req_args = ['namesArray']
        validate_args(kwargs, req_args)
        resp = self.workflow.RemoveCustomAttrs(customid).POST(data=json.dumps(kwargs))
        return handle_response('bool', resp)

    def resend_mail_deliverable(self, mailid):
        """Resends the mail deliverable with a specified mail ID.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodResendMailDeliverable.html

        Path Args: mailID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.ResendMailDeliverable(mailid).POST()
        return handle_response('bool', resp)

    def restore_proc_inst(self, procinstid):
        """Restores a process instance and associated data from the
        ArchiveDatabase to the AgilePoint Server. The process instance
        records are written to the AgilePoint Database deleted from the
        AgilePoint Archive Database.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodRestoreProcInst.html

        Path Args: procInstID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.RestoreProcInst(procinstid).POST()
        return handle_response('bool', resp)

    def resume_proc_inst(self, processinstanceid):
        """Resumes a process instance with the specified process instance id.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodResumeProcInst.html

        Path Args: processInstanceID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.ResumeProcInst(processinstanceid).POST()
        return handle_response('json', resp)

    def rollback_activity_inst(self, activityinstanceid):
        """Rolls back a manual activity instance to the token position EN -
        that is, the state where the activity is entered. All work items
        associated with the manual activity instance with the status of NEW,
        OVERDUE, or ASSIGNED are canceled.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodRollbackActivityInst.html

        Path Args: activityInstanceID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.RollbackActivityInst(activityinstanceid).POST()
        return handle_response('json', resp)

    def rollback_activity_insts(self, **kwargs):
        """Rolls back a process instance according to a specified instruction.
        The class WFPartialRollbackInstructionis used to specify detailed
        information about the instruction.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodRollbackActivityInsts.html

        Path Args: None
        Required Body Args: PartialRollbackUnits
        Optional Body Args: None"""
        req_args = ['PartialRollbackUnits']
        validate_args(kwargs, req_args)
        resp = self.workflow.RollbackActivityInsts.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def rollback_proc_inst(self, activityinstanceid):
        """Rolls a process instance back to a previous specified activity, or
        skips a specified activity if has not yet been completed. When this
        method is invoked, the current or skipped activity becomes canceled.
        When skipping, the process moves forward regardless of the activity's
        status.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodRollbackProcInst.html

        Path Args: activityInstanceID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.RollbackProcInst(activityinstanceid).POST()
        return handle_response('json', resp)

    def send_mail(self, **kwargs):
        """Sends an email through AgilePoint Server.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodSendMail.html

        Path Args: None
        Required Body Args: Attachments, Body, CC, From, Subject, To
        Optional Body Args: None"""
        req_args = ['Attachments, Body, CC, From, Subject, To']
        validate_args(kwargs, req_args)
        resp = self.workflow.SendMail.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def set_custom_attrs(self, customid, **kwargs):
        """Sets names and values for multiple custom attributes for a specified
        custom ID.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodSetCustomAttrs.html

        Path Args: customID
        Required Body Args: attributes
        Optional Body Args: None"""
        req_args = ['attributes']
        validate_args(kwargs, req_args)
        resp = self.workflow.SetCustomAttrs(customid).POST(data=json.dumps(kwargs))
        return handle_response('bool', resp)

    def set_proc_def_supplement(self, processdefinitionid, activitydefinitionid):
        """Sets supplement information related to process definition.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodSetProcDefSupplement.html

        Path Args: processDefinitionID, activityDefinitionID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.SetProcDefSupplement(
            processdefinitionid)(activitydefinitionid).POST()
        return handle_response('bool', resp)

    def split_proc_inst(self, **kwargs):
        """Splits one process instance into 2 or more process instances. The
        original process is canceled.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodSplitProcInst.html

        Path Args: None
        Required Body Args: SplitProcessInstances, SplittingProcessInstanceID
        Optional Body Args: None"""
        req_args = ['SplitProcessInstances', 'SplittingProcessInstanceID']
        validate_args(kwargs, req_args)
        resp = self.workflow.SplitProcInst.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def suspend_proc_inst(self, processinstanceid):
        """Suspends a process instance. The process instance status is changed
        to Suspended, and the statuses of all the work items (tasks) become
        Pending.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodSuspendProcInst.html

        Path Args: processInstanceID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.SuspendProcInst(processinstanceid).POST()
        return handle_response('json', resp)

    def uncheck_out_proc_def(self, processtemplateid):
        """Undoes a check-out for a process definition. This method returns the
        status of a process definition from CheckedOut to Released without
        making changes to the process definition, or changing the version
        number.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodUnCheckOutProcDef.html

        Path Args: processTemplateID
        Required Body Args: None
        Optional Body Args: None"""
        resp = self.workflow.UnCheckOutProcDef(processtemplateid).POST()
        return handle_response('bool', resp)

    def undo_assign_work_item(self, workitemid, **kwargs):
        """Unassigns a work item that was previously assigned to a user. This
        method applies to work items that can be assigned to members of task
        groups, where a work item can be assigned to or claimed by any of a
        group of users.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodUndoAssignWorkItem.html

        Path Args: workItemID
        Required Body Args: clientData
        Optional Body Args: None"""
        req_args = ['clientData']
        validate_args(kwargs, req_args)
        resp = self.workflow.UndoAssignWorkItem(workitemid).POST(
            data=json.dumps(kwargs))
        return handle_response('json', resp)

    def update_proc_def(self, **kwargs):
        """Updates a process definition without using version control. This
        method is intended for minor changes only, such as typographical errors.
        Warning: Changes made using this method circumvent version control,
        meaning changes are not tracked, and versions cannot be managed. Do not
        use this call for making any major changes to the process definition.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodUpdateProcDef.html

        Path Args: None
        Required Body Args: xml
        Optional Body Args: None"""
        req_args = ['xml']
        validate_args(kwargs, req_args)
        resp = self.workflow.UpdateProcDef.POST(data=json.dumps(kwargs))
        return handle_response('json', resp)

    def update_proc_inst(self, processinstanceid, **kwargs):
        """Updates attributes of a workflow process instance. The attributes
        that can be updated are listed in the attribute table.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodUpdateProcInst.html

        Path Args: processInstanceID
        Required Body Args: attributes
        Optional Body Args: None"""
        req_args = ['attributes']
        validate_args(kwargs, req_args)
        resp = self.workflow.UpdateProcInst(processinstanceid).POST(
            data=json.dumps(kwargs))
        return handle_response('bool', resp)

    def update_work_item(self, workitemid, **kwargs):
        """Updates a manual work item or automatic work item.

        http://documentation.agilepoint.com/SupportPortal/DOCS/ProductDocumentation/CurrentRelease/DocumentationLibrary/maps/restmethodUpdateWorkItem.html

        Path Args: workItemID
        Required Body Args: attributes
        Optional Body Args: None"""
        req_args = ['attributes']
        validate_args(kwargs, req_args)
        resp = self.workflow.UpdateWorkItem(workitemid).POST(
            data=json.dumps(kwargs))
        return handle_response('bool', resp)
