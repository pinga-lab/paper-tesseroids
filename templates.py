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
        ms = env.Command('manuscript.tex', 'body.tex', builder.build)
        pdf = env.PDF(target='manuscript.pdf', source=ms)

    Then running 'scons' will produce 'manuscript.tex' and compile it to
    'manuscript.pdf' using the Geophysical Journal International template.

    Pass 'pretty=True' to 'Manuscript' to produce a 'final paper'-looking
    output.
    """


    def __init__(self, title, author, affil, author_affil, journal, heads,
                 bibfile, pretty=False):
        self.title = title
        self.author = author
        self.affil = affil
        self.author_affil = author_affil
        self.journal = journal
        self.heads = heads
        self.bibfile = bibfile
        self.pretty = pretty


    def build(self, target, source, env):
        """
        To be used in a SCons Command as:

            builder = Manuscript(title=...)
            ms = env.Command('manuscrit.tex', 'ms_body.tex', builder.build)

        This will take the body of the text (just the sections and text, no
        documentclass, title, bibiliography, etc) and make the final tex file
        that can be compiled. Uses the right template for the given journal.
        """
        with open(str(source[0])) as f:
            body = f.read()
        text = getattr(self, self.journal)(body)
        with open(str(target[0]), 'w') as f:
            f.write(text)


    def geophysics(self, body):
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
        if self.pretty:
            options = 'paper,twocolumn,twoside'
            endfloat = ''
        header = GEOPHYISICS_HEAD.format(
            title=self.title, heads=self.heads, options=options,
            endfloat=endfloat, authors=authors)
        footer = FOOTER.format(bst='seg', bibfile=self.bibfile)
        text = '\n'.join([header, body, footer])
        return text


    def gji(self, body):
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
        if self.pretty:
            options = 'extra'
        header = GJI_HEAD.format(
            title=self.title, heads=self.heads, authors=authors,
            options=options)
        footer = FOOTER.format(bst='gji', bibfile=self.bibfile)
        text = '\n'.join([header, body, footer])
        return text
