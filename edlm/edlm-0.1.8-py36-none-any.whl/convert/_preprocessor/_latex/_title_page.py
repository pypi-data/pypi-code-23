# coding=utf-8
"""
Title page
"""

# noinspection SpellCheckingInspection
TITLE_PAGE = r"""
\thispagestyle{empty}

\begin{center}
    \vspace*{2em}

    \begin{figure}[h]
      \centering
      \includegraphics[height=6cm]{logo132.png}
    \end{figure}

    \vspace{2em}

    \noindent\rule{\textwidth}{0.4pt}

    {\fontsize{2cm}{2.3cm}\selectfont $title$\par}

    \noindent\rule{\textwidth}{0.4pt}

    $subtitle$

    \vfill

    $if(title_pictures)$
        \begin{figure}[h]
            \begin{minipage}[c]{\linewidth}
                \centering
                $for(title_pictures)$
                      \includegraphics[height=3cm]{$title_pictures$}
                $endfor$
            \end{minipage}
        \end{figure}
    $endif$

    \vfill

    {\href{http://132virtualwing.org}{\wing}}, \the\year \\
    \vspace{0.3cm}
    This work is licensed under a {\href{https://creativecommons.org/licenses/by-sa/3.0/}{Creative Commons Attribution-ShareAlike 3.0 Unported License}}.

\end{center}
"""  # noqa
