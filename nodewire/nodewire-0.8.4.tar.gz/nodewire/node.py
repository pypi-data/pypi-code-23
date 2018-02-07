from nodewire.NodeWire import NodeWire

class Port:
    def __init__(self, name, props='Digital OUT', writing=None, reading=None):
        self.store = 0
        self.name = name
        self.props = props
        self.writing = writing
        self.reading = reading

    def read(self):
        if(self.reading): self.reading()
        return  self.store

    def write(self, val):
        if(self.writing): self.writing(val)
        self.store = val

    def properties(self):
        return self.props

class Node:
    def __init__(self, nodename='node01', nw=None):
        self.nw = NodeWire(nodename, process=self.process) if nw==None else nw
        self.nw.debug = True
        self.ports = []

    def process(self, msg):
        if msg.Command == 'get' or msg.Command == 'getportvalue':
            if msg.Params[0] == 'properties':
                p = [pp for pp in self.ports if pp.name == msg.Params[1]]
                if len(p) != 0: self.nw.send(msg.Sender,'properties', p[0].name, p[0].props)
            elif msg.Params[0] == 'ports':
                ps = ''
                for p in self.ports: ps = ps + ' ' + p.name
                self.nw.send(msg.Sender, 'ports', ps)
            else:
                v = self.get(msg.Params[0])
                self.nw.send(msg.Sender, 'portvalue', msg.Params[0], str(v))
        elif msg.Command == 'set' or msg.Command == 'setportvalue':
            self.set(msg.Params[0], msg.Params[1])
            self.nw.send(msg.Sender, 'portvalue', msg.Params[0], self.get(msg.Params[0]))

    def get(self, port):
        p = [pp for pp in self.ports if pp.name==port] # filter(lambda pp: pp.name==port, self.ports)
        if len(p) != 0: return p[0].read()
        else: return 'error'

    def set(self, port, val):
        p = [pp for pp in self.ports if pp.name == port]
        if len(p) != 0: p[0].write(val)

if __name__ == '__main__':
    node = Node()
    node.ports.append(Port('Power'))
    node.ports.append(Port('LED', 'Digital IN'))

    node.nw.run()