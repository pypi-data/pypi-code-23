import faker as fk
import pandas as pd

class DummyData:
    """ Generate dummy data from dict(schema) """
    def __init__(self, schema):
        self.schema = schema 
        #print('From DummyData', type(self.schema))
    
    def generate_data(self):
        # For more complex types check https://github.com/joke2k/faker
        fake = fk.Faker()
                
        if self.schema['format'] == 'pandas.dataframe':
            data  = {}
            
            # scan each field and generate dummy 
            for field in self.schema['fields']:
                dummy_content = []
                types = field['type'].keys()
                #print('Processing field=', field['name'])
                for t in types:
                    nelems = field['type'][t]  # elements of this type
                    #print('type=', t, 'num_elements=', nelems)
                    
                    ###############################
                    # Fake primitive types
                    ###############################                    
                    if t == 'int':
                        for i in range(nelems):
                            dummy_int = fake.pyint() # np.random.randint(0, 100000)
                            dummy_content.append(dummy_int)
                    if t == 'str':
                        for i in range(nelems):
                            #strlen = np.random.randint(42)
                            #dummy_str = (''.join(random.choice(s.ascii_letters+' ') for i in range(strlen)))
                            dummy_str = fake.pystr()
                            dummy_content.append(dummy_str)
                    if t == 'float':
                        for i in range(nelems):
                            dummy_float = fake.pyfloat() # dummy_content.append(dummy_float) 
                            dummy_content.append(dummy_float)
                    if t == 'bool':
                        for i in range(nelems):
                            dummy_bool = fake.pybool()
                            dummy_content.append(dummy_bool)
                            
                    ###############################
                    # Fake complex types
                    ###############################
                    if t == 'email':
                        for i in range(nelems):
                            dummy_content.append(fake.email())
                    if t == 'address':
                        for i in range(nelems):
                            dummy_address = fake.address()
                            dummy_content.append(dummy_address)
                    if t == 'time':
                        for i in range(nelems):
                            dummy_time = fake.time()
                            dummy_content.append(dummy_time)

                # Fill dataframe by column
                data[field['name']] = dummy_content
                
            # Convert to dataframe and return      
            df = pd.DataFrame(data=data)
            return df


