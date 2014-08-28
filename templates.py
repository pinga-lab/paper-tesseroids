"""
Templates to build Latex files for specific journals.
"""


SEGABS_HEAD = r"""
\documentclass{segabs}
\newcommand{{\mitbf}}[1]{{\mathbf{{#1}}}}
\usepackage{{graphicx}}

\begin{{document}}

\title{{{title}}}
\lefthead{{{heads[0]}}}
\righthead{{{heads[1]}}}

{authors}
"""

GEOPHYISICS_HEAD = r"""
\documentclass[{options}]{{geophysics}}
{endfloat}
\usepackage{{graphicx}}
\newcommand{{\mitbf}}[1]{{\mathbf{{#1}}}}

\begin{{document}}

\title{{{title}}}
\lefthead{{{heads[0]}}}
\righthead{{{heads[1]}}}
% manuscript number
\ms{{}}

{authors}
"""

GJI_HEAD = r"""
\documentclass[{options}]{{gji}}
\usepackage{{timet}}
\usepackage{{graphicx}}

\title[{heads[1]}]{{
{title}
}}

\author[{heads[0]}]{{
{authors}
}}

\begin{{document}}

\label{{firstpage}}
\maketitle
"""

FOOTER = r"""
\bibliographystyle{{{bst}}}
\bibliography{{{bibfile}}}
\end{{document}}
"""


class Manuscript(object):
    """
    Gather metadata for a manuscript and make the main .tex file for a journal.

    Use 'Manuscript.build' in a SCons Command to make the tex file from the
    body of the text.

    Example:

    Putting this in a file named 'SConstruct':

        from templates import Manuscript
        builder = Manuscript(
            title='My title',
            author=['First Author',
                    'Second Author'],
            affil=['First auth affiliation.',
                   'First and second auth affiliation.'],
            # Indexes in 'affil' corresponding to each author
            author_affil=[[0, 1], [1]],
            journal='gji',
            heads=['Author et al.', 'Short title'],
            bibfile='references.bib')
        env = Environment()
        ms = env.Command('manuscript.tex', 'body.tex', builder.build_ms)
        pdf = env.PDF(target='manuscript.pdf', source=ms)

    Then running 'scons' will produce 'manuscript.tex' and compile it to
    'manuscript.pdf' using the Geophysical Journal International template.
    """


    def __init__(self, title, author, affil, author_affil, journal, heads,
                 bibfile):
        self.title = title
        self.author = author
        self.affil = affil
        self.author_affil = author_affil
        self.journal = journal
        self.heads = heads
        self.bibfile = bibfile


    def build_ms(self, target, source, env):
        """
        To be used in a SCons Command as:

            builder = Manuscript(title=...)
            latexfile = env.Command('paper.tex', 'ms_body.tex',
                                    builder.build_ms)

        This will take the body of the text (just the sections and text, no
        documentclass, title, bibiliography, etc) and make the final tex file
        that can be compiled. Uses the right template for the given journal.
        """
        with open(str(source[0])) as f:
            body = f.read()
        text = getattr(self, self.journal)(body)
        with open(str(target[0]), 'w') as f:
            f.write(text)


    def build_paper(self, target, source, env):
        """
        To be used in a SCons Command as:

            builder = Manuscript(title=...)
            latexfile = env.Command('paper.tex', 'ms_body.tex',
                                    builder.build_paper)

        Same as 'build_ms' but will make a latex file for a pretty
        (published-looking) version of the paper (if the document class has
        options for this).
        """
        with open(str(source[0])) as f:
            body = f.read()
        text = getattr(self, self.journal)(body, pretty=True)
        with open(str(target[0]), 'w') as f:
            f.write(text)


    def geophysics(self, body, pretty=False):
        """
        Builds manuscripts for Geophysics articles.
        """
        authors_template = "\\address{{\n{affil}\n}}\n\\author{{\n{author}\n}}"
        affils = [r'\footnotemark[{}]{}'.format(i + 1, name)
                  for i, name in enumerate(self.affil)]
        author_list = []
        for name, num in zip(self.author, self.author_affil):
            tmp = ''.join([r'\footnotemark[{}]'.format(i + 1) for i in num])
            author_list.append(''.join([name, tmp]))
        authors = authors_template.format(
            affil='\\\\\n'.join(affils),
            author=',\n'.join(author_list))
        options = 'manuscript'
        endfloat = '\usepackage[nomarkers]{endfloat}'
        if pretty:
            options = 'paper,twocolumn,twoside'
            endfloat = ''
        header = GEOPHYISICS_HEAD.format(
            title=self.title, heads=self.heads, options=options,
            endfloat=endfloat, authors=authors)
        footer = FOOTER.format(bst='seg', bibfile=self.bibfile)
        text = '\n'.join([header, body, footer])
        return text


    def gji(self, body, pretty=False):
        """
        Builds manuscripts for Geophysical Journal International.
        """
        affils = [r'$^{}${}'.format(i + 1, name)
                  for i, name in enumerate(self.affil)]
        author_list = []
        for name, num in zip(self.author, self.author_affil):
            tmp = '$^{{{0}}}$'.format(','.join([str(i + 1) for i in num]))
            author_list.append(''.join([name, tmp]))
        authors = '\\\\\n'.join([
            ',\n'.join(author_list),
            '\n'.join(affils)
            ])

        options = 'extra,mreferee'
        if pretty:
            options = 'extra'
        header = GJI_HEAD.format(
            title=self.title, heads=self.heads, authors=authors,
            options=options)
        footer = FOOTER.format(bst='gji', bibfile=self.bibfile)
        text = '\n'.join([header, body, footer])
        return text
