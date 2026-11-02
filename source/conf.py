project = 'Image Signal Processing (ISP)'
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Image Signal Processing (ISP)'
copyright = '2026, '
author = ''
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []

language = 'en'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

html_title = 'Image Signal Processing (ISP)'

html_logo = '_static/project_logo.svg'

# Logo size adjustment
html_css_files = ['custom_logo_scale.css', 'custom_overrides.css']

# Generated RST files: rstfile1

html_js_files = ['spx_pdf_download.js', 'spx_img_click.js']

latex_engine = 'pdflatex'

latex_toplevel_sectioning = 'section'

latex_documents = [
    (
        'index',
        'Image_Signal_Processing_ISP.tex',
        'Image Signal Processing (ISP)',
        '',
        'howto',
    ),
]

# Ensure LaTeX assets are copied to build directory
try:
    latex_additional_files
except NameError:
    latex_additional_files = []
for _p in ['_static/header.png', '_static/footer.png']:
    if _p not in latex_additional_files:
        latex_additional_files.append(_p)

# SPX_ENSURE_BABEL
latex_elements = globals().get('latex_elements', {})
_spx_lang = globals().get('language', 'en') or 'en'
if not isinstance(_spx_lang, str) or not _spx_lang.strip():
    _spx_lang = 'en'
_spx_lang_norm = _spx_lang.strip().lower().replace('_', '-')
_spx_lang_map = {'en': 'english', 'en-us': 'english', 'en-gb': 'british'}
_spx_lang_final = _spx_lang_map.get(_spx_lang_norm, _spx_lang_norm or 'english')
if not latex_elements.get('babel'):
    latex_elements['babel'] = r'\usepackage[' + _spx_lang_final + ']{babel}'

latex_elements['preamble'] = r'''
\usepackage{fancyhdr}
\usepackage{xcolor}
\usepackage{graphicx}
\usepackage{lastpage}
\usepackage{eso-pic}

\newcommand{\phytecPageNumber}{\raisebox{3mm}{\textcolor{gray}{page~\thepage~of~\pageref{LastPage}}}}

\pagestyle{fancy}
\fancyhf{}
\setlength{\headheight}{22mm}
\setlength{\headsep}{5mm}
\addtolength{\topmargin}{-10mm}
\setlength{\footskip}{20mm}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
\fancyfoot[C]{\phytecPageNumber}

\fancypagestyle{plain}{%
  \fancyhf{}
  \fancyfoot[C]{\phytecPageNumber}
}
\fancypagestyle{titlepage}{%
  \fancyhf{}
  \fancyfoot[C]{\phytecPageNumber}
}
\fancypagestyle{empty}{%
  \fancyhf{}
  \fancyfoot[C]{\phytecPageNumber}
}

\makeatletter
\let\ps@plain\ps@fancy
\let\ps@empty\ps@fancy
\makeatother
\AtBeginDocument{\pagestyle{fancy}\thispagestyle{fancy}}

\providecommand{\sphinxthinrule}{}
\providecommand{\sphinxstrongrule}{}
\providecommand{\sphinxrule}{}
\providecommand{\sphinxbeforetopmargin}{}
\providecommand{\sphinxaftertopmargin}{}

\makeatletter
\let\spxOrigTableofcontents\sphinxtableofcontents
\renewcommand{\sphinxtableofcontents}{\spxOrigTableofcontents\clearpage}
\makeatother

\AddToShipoutPictureBG{%
  \AtPageUpperLeft{\hspace{15mm}\raisebox{-20mm}{\includegraphics[width=180mm,height=18mm,keepaspectratio]{header.png}}}
}
\AddToShipoutPictureBG{%
  \AtPageLowerLeft{\raisebox{12mm}{\hspace{15mm}\includegraphics[width=180mm,height=10mm,keepaspectratio]{footer.png}}}
}

\makeatletter
\renewcommand{\sphinxmaketitle}{%
  \thispagestyle{fancy}%
  \vspace*{\fill}%
  \begin{center}%
    {\LARGE\bfseries \@title}%
  \end{center}%
  \vspace*{\fill}%
  \clearpage%
}
\makeatother
'''

# Prevent even-page blanks and simplify Sphinx maketitle
