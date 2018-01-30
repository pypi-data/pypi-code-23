import stringcase
import inspect

def get_outer_frame_info():
    outer_frames = inspect.getouterframes(inspect.currentframe())
    for frameinfo in outer_frames:
        if frameinfo.code_context and 'import pepize' in frameinfo.code_context[0]:
            return frameinfo
    return inspect.getframeinfo(inspect.currentframe())


outer_frameinfo = get_outer_frame_info()

fpath = outer_frameinfo[0]

outer_frame = inspect.getouterframes(inspect.currentframe())[-1].frame
variables = outer_frame.f_locals

def pepize(variables):
    code_text = ''
    for key in variables:
        if not inspect.isbuiltin(variables[key]):
            convention_name = key
            if inspect.isclass(variables[key]):
                convention_name = stringcase.pascalcase(key)
            else:
                convention_name = stringcase.snakecase(key)
            if convention_name != key:
                code_text += '{} = {}\n'.format(convention_name, key)
    #print(code_text)
    code_chunk = compile( code_text, '', 'exec' )
    exec(code_chunk, outer_frame.f_globals, outer_frame.f_locals)

pepize(variables)