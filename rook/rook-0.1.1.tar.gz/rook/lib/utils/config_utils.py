from backend.management_system.exceptions import Exceptions


def _get_lines(file_name):
    try:
        confLines = open(file_name, "rb").read().rstrip("\n").split("\n")
    except IOError as e:
        raise Exceptions.ManagementException("Failed to read vpn conf file - %s" % str(e))
    # Return data from file
    return confLines


def _find_marker(confLines, line_marker):
    for i, line in enumerate(confLines):
        if line.lower() == line_marker.lower():
            # Found marker
            markerLineIdx = i
            break
    else:
        # Didn't find the marker.
        raise Exceptions.ManagementException("Couldn't find the #Users marker line in the StrongSwan conf file")
    return markerLineIdx


def file_exist(file_name):
    try:
        _get_lines(file_name)
    except IOError as e:
        return False
    return True


def get_marker_index(file_name, line_marker):
    # Get lines
    confLines = _get_lines(file_name)
    # Find the '#Users' line, which marks the start of the users section.
    markerLineIdx = _find_marker(confLines, line_marker)
    # Return marker line index
    return markerLineIdx


def get_before_marker(file_name, line_marker, text=True):
    # Get lines
    confLines = _get_lines(file_name)
    # Find the '#Users' line, which marks the start of the users section.
    markerLineIdx = _find_marker(confLines, line_marker)
    # Return after marker
    data = []
    if len(confLines) > markerLineIdx + 1:
        data = confLines[0:markerLineIdx]
    if text:
        return "\n".join(data)
    return data


def get_after_marker(file_name, line_marker, text=True):
    # Get lines
    confLines = _get_lines(file_name)
    # Find the '#Users' line, which marks the start of the users section.
    markerLineIdx = _find_marker(confLines, line_marker)
    # Return after marker
    data = []
    if len(confLines) > markerLineIdx + 1:
        data = confLines[markerLineIdx + 1:]
    if text:
        return "\n".join(data)
    return data
