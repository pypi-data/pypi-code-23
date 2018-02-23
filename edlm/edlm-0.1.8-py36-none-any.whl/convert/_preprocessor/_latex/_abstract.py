# coding=utf-8
"""
Latex abstract
"""

_PARBOX = r'\parbox[t]{10cm}'
_COLOR = r'\color{gray}'
_CHANGES = r'$for(summary_of_changes)$ $summary_of_changes$ \vspace{2mm} \\ $endfor$'
_APPLIES = r'$for(applies)$ \textbf{$applies$} \\ $endfor$'
_SPACING = r'\null'

# noinspection SpellCheckingInspection
ABSTRACT = rf"""
$if(applies)$
    \thispagestyle{{empty}}
    \null
    \vfill
    \begin{{minipage}}{{\textwidth}}
        \begin{{center}}
            \begin{{tabular}}{{ r l }}

                {{{_COLOR}APPLIES TO:}} & {_PARBOX}{{{_APPLIES}}} \\ {_SPACING} \\

                $if(type)$ {{{_COLOR}TYPE:}} & {_PARBOX}{{\textbf{{$type$}}}} \\ {_SPACING} \\ $endif$

                $if(version)$ {{{_COLOR}VERSION:}} & {_PARBOX}{{$version$}} \\ {_SPACING} \\ $endif$

                $if(audience)$ {{{_COLOR}INTENDED AUDIENCE:}} & {_PARBOX}{{$audience$}} \\ {_SPACING} \\ $endif$

                $if(status)$ {{{_COLOR}STATUS:}} & {_PARBOX}{{$status$}} \\ {_SPACING} \\ $endif$

                $if(published_date)$ {{{_COLOR}PUBLISHED DATE:}} & {_PARBOX}{{$published_date$}} \\ {_SPACING} \\
                $endif$

                $if(responsible)$ {{{_COLOR}DOCUMENT RESPONSIBLE:}} & {_PARBOX}{{$responsible$}} \\ {_SPACING} \\
                $endif$

                $if(summary_of_changes)$ {{{_COLOR}SUMMARY OF CHANGES:}} & {_PARBOX}{{{_CHANGES}}} \\ {_SPACING} \\
                $endif$

            \end{{tabular}}
        \end{{center}}
    \end{{minipage}}
    \vfill
$endif$
"""
