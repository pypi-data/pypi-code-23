def get_commands(dicom,action,item=None,fields=None):
    '''get a dcm4che command to remove or replace.'''

    commands = []
    field = action.get('field')   # e.g: PatientID, endswith:ID
    value = action.get('value')   # "suid" or "var:field"
    action = action.get('action') # "REPLACE"
    
    if fields is None:
        fields = dicom.dir()

    # If there is an expander applied to field, we iterate over
    fields = expand_field_expression(field=field,
                                     dicom=dicom,
                                     contenders=fields)

    for field in fields:
        command = _get_command(dicom=dicom,
                               field=field,
                               item=item,
                               action=action,
                               value=value)
        if command is not None:
            commands += command
    return commands

    

def _get_command(dicom,field,action,value=None,item=None):
    '''return dcm4che commands '''
    if action not in valid_actions:
        bot.warning('%s in not a valid choice [%s]. Defaulting to blanked.' %(action,
                                                                              ".".join(valid_actions)))
        action = "BLANK"

    if field in dicom and action != "ADD":
        # Blank the value
        if action == "BLANK":
            return 'dcmodify -i "(0010,0020)=0000000-0” %s' %(dicom_file)
            bot.debug("BLANKING %s" %field)
            dicom = blank_tag(dicom,field)
        # Code the value with something in the response
        elif action == "REPLACE":
            value = parse_value(item,value)
            if value is not None:
                # If we make it here, do the replacement
                dicom = update_tag(dicom,
                                   field=field,
                                   value=value)
            else:
                bot.warning("REPLACE %s unsuccessful" %field)
        # Code the value with something in the response
        elif action == "JITTER":
            value = parse_value(item,value)
            if value is not None:
                # Jitter the field by the supplied value
                dicom = jitter_timestamp(item=dicom,
                                         field=field,
                                         value=value)
            else:
                bot.warning("JITTER %s unsuccessful" %field)
        # elif "KEEP" --> Do nothing. Keep the original
        # Remove the field entirely
        elif action == "REMOVE":
            dicom = remove_tag(dicom,field)
    elif action == "ADD":
        value = parse_value(item,value)
        if value is not None:
            dicom = add_tag(dicom,field,value) 
    else:
        bot.warning('Field %s is not present in %s' %(field,dicom_file))
    return dicom




    return updated_files
dcmodify -i "(0010,0010)=Fake Name” file.dcm

to overwrite segment 0010,0010, which is patient name. You can do the same for MRN, date of birth and address:

dcmodify -i "(0010,0020)=0000000-0” file.dcm
dcmodify -i "(0010,0030)=19000101” file.dcm
dcmodify -i "(0010,0040)=123 Fake Address Lane, Anytown, CA, 00000” file.dcm

Alternately you can remove these headers entirely with the -ea flag:

dcmodify -e "(0010,0010)" *.dcm
dcmodify -e "(0010,0020)" *.dcm
dcmodify -e "(0010,0030)" *.dcm
dcmodify -e "(0010,0040)" *.dcm



def replace_identifiers_recipe(dicom_files,
                               ids,
                               deid=None,
                               save=True,
                               overwrite=False,
                               config=None,
                               strip_sequences=True,
                               remove_private=True):

    '''replace_identifiers_recipe will write dcmtk set of commands to replace identifiers 
    for a set of dicoms. If save is True, the commands will be issued to the files. If not,
    they are returned
    ''' 
    dicom_files, deid, config = _prepare_replace_config(dicom_files, 
                                                        deid=deid,
                                                        config=config)

    # First issue commands across files, to remove and blank
    if deid is not None:
        for item_id in ids:
            for action in deid['header']:
                new_commands = get_commands(dicom=dicom,
                                            item=ids[item_id],
                                            action=action) 


    dcmodify -e "(0010,0010)" *.dcm


    commands = []
    for d in range(len(dicom_files)):
        dicom_file = dicom_files[d]
        dicom = read_file(dicom_file,force=force)
        idx = os.path.basename(dicom_file)
        print("[%s of %s]: %s" %(d,len(dicom_files),idx))
        fields = dicom.dir()

        # Remove sequences first, maintained in DataStore
        if strip_sequences is True:
            dicom = remove_sequences(dicom)
        if remove_private is True:
            dicom.remove_private_tags()
        else:
            bot.warning("Private tags were not removed!")


        if deid is not None:
            for item_id in ids:
                for action in deid['header']:
                    new_commands = get_commands(dicom=dicom,
                                                item=ids[item_id],
                                                action=action) 

        # Next perform actions in default config, only if not done
        for action in config['put']['actions']:
            if action['field'] in fields:
                 dicom = perform_action(dicom=dicom,
                                        action=action)
        ds = Dataset()
        for field in dicom.dir():
            ds.add(dicom.data_element(field))

        # Copy original data types
        attributes = ['is_little_endian','is_implicit_VR']
        for attribute in attributes:
            ds.__setattr__(attribute,
                           dicom.__getattribute__(attribute))
        # Save to file?
        if save is True:
            ds = save_dicom(dicom=ds,
                            dicom_file=dicom_file,
                            output_folder=output_folder,
                            overwrite=overwrite)

        updated_files.append(ds)

    return updated_files
dcmodify -i "(0010,0010)=Fake Name” file.dcm

to overwrite segment 0010,0010, which is patient name. You can do the same for MRN, date of birth and address:

dcmodify -i "(0010,0020)=0000000-0” file.dcm
dcmodify -i "(0010,0030)=19000101” file.dcm
dcmodify -i "(0010,0040)=123 Fake Address Lane, Anytown, CA, 00000” file.dcm

Alternately you can remove these headers entirely with the -ea flag:

dcmodify -e "(0010,0010)" *.dcm
dcmodify -e "(0010,0020)" *.dcm
dcmodify -e "(0010,0030)" *.dcm
dcmodify -e "(0010,0040)" *.dcm

