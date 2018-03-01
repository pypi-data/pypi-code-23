def santize(time_string):#处理时间列表中格式不一致的问题
        if '-' in time_string:
                splitter='-'
        elif ':' in time_string:
                splitter=':'
        else:
                return time_string
        (mins,secs)=time_string.split(splitter)
        return(mins+'.'+secs)
class AthleteList(list):#使用字典管理数据，并将代码和数据封装在类中
        def __init__(self,a_name,a_dob=None,a_times=[]):
                self.name=a_name
                self.dob=a_dob
                self.extend(a_times)
        def top3(self):
                return(sorted(set([santize(t) for t in self]))[0:3])

def get_coach_data(filename):#获得数据并完成分割显示
        try:
                with open(filename) as f:
                        data = f.readline()
                temp = data.strip().split(',')
                return(AthleteList(temp.pop(0),temp.pop(0),temp))
        except IOError as ioerr:
                       print('File Error: '+str(ioerr))
                       return(None)
