import NodeDefender.frontend.sockets.admin
import NodeDefender.frontend.sockets.node
import NodeDefender.frontend.sockets.group
import NodeDefender.frontend.sockets.icpe
import NodeDefender.frontend.sockets.sensor
import NodeDefender.frontend.sockets.data
import NodeDefender.frontend.sockets.plotly
import NodeDefender.frontend.sockets.user
import NodeDefender.frontend.sockets.zwave

def load_sockets(socketio):
    NodeDefender.frontend.sockets.admin.load_sockets(socketio)
    NodeDefender.frontend.sockets.node.load_sockets(socketio)
    NodeDefender.frontend.sockets.group.load_sockets(socketio)
    NodeDefender.frontend.sockets.icpe.load_sockets(socketio)
    NodeDefender.frontend.sockets.sensor.load_sockets(socketio)
    NodeDefender.frontend.sockets.data.load_sockets(socketio)
    NodeDefender.frontend.sockets.plotly.load_sockets(socketio)
    NodeDefender.frontend.sockets.user.load_sockets(socketio)
    return True
