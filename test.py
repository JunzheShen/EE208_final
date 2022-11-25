def parseCommand(command):
    '''
    input: C title:T site:S
    output: {'contents':C, 'sport':S, 'site':U}
    '''
    allowed_opt = ['sport', 'site']
    command_dict = {}
    opt = 'contents'
    for i in command.split(' '):
        if ':' in i:
            opt, value = i.split(':')[:2]
            opt = opt.lower()
            if opt in allowed_opt and value != '':
                command_dict[opt] = value
        else:
            command_dict[opt] = command_dict.get(opt, '') + i
    return command_dict
print(parseCommand('足球 sport:足球'))
print('test modification')