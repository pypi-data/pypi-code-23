def apply_commands(context,executor,commands,cell):
    for cmd,params in commands:
        cell = executor(context,cell,cmd,params)

    return cell 

def commands_update(commands,k,v):
    for index,entry in enumerate(commands):
        cmd,params =  entry 
        if cmd == k:
            commands[index] = (k,v) 
            return 
    commands.append((k,v)) 


