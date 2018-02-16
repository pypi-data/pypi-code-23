import visa
rm = visa.ResourceManager()
class gpib(object):
    def addr(gpib_no,gpib_port):
        add_var = 'GPIB%d::%d::INSTR' % (gpib_no,gpib_port)
        inst = rm.open_resource(add_var)
        return inst
        # return inst.query('*IDN?')

class serial(object):
    def addr(port):
        add_var = 'ASRL%d::INSTR' %port
        inst = rm.open_resource(add_var)
        return inst
        # return inst.query('*IDN?')