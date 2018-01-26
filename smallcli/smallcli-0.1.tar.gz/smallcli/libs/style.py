from pygments.token import Token
from prompt_toolkit.styles import style_from_dict


default = style_from_dict({
    Token.Name: 'bold #009AC7',
    Token.Symbol: 'bold #00FF00',
    Token.Mode: 'bold #dadada',
    Token.ModeSymbol: '#ffaf00',
    Token.Menu.Completions.Completion: 'bg:#74B3CC #204a87',
    Token.Menu.Completions.Completion.Current: 'bold bg:#274B7A #ffffff',
    Token.Menu.Completions.Meta: 'bg:#2C568C #eeeeee',
    Token.Menu.Completions.Meta.Current: 'bold bg:#274B7A #ffffff',
    Token.Menu.Completions.MultiColumnMeta: 'bg:#aaaaaa #000000',
    Token.Menu.Completions.ProgressBar: 'bg:#74B3CC',
    Token.Menu.Completions.ProgressButton: 'bg:#274B7A',
    Token.Toolbar: '#ffffff bg:#333333',
})
