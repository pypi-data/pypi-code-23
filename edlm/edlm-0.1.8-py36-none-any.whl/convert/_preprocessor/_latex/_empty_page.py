# coding=utf-8
"""
Simple latex empty page
"""

# noinspection SpellCheckingInspection
EMPTY_PAGE = r"""
\newpage
\thispagestyle{empty}
\clearpage
\vspace*{\fill}
\begin{center}
    \begin{minipage}{ .6\textwidth }
        \centering PAGE INTENTIONALLY LEFT BLANK
    \end{minipage}
\end{center}
\vfill % equivalent to \vspace{\fill}
\clearpage
\thispagestyle{fancy}
"""
