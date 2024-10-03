\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{cours}

\def\importmath{0}
\def\importinfo{0}

\LoadClassWithOptions{article}
\DeclareOption{math}{\renewcommand{\importmath}{1}}
\DeclareOption{info}{\renewcommand{\importinfo}{1}}

\ProcessOptions\relax

\RequirePackage{cmap}
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage[french]{babel}
\RequirePackage{lmodern}
\RequirePackage{texnames}
\RequirePackage{ragged2e}
\RequirePackage{titlesec}
\RequirePackage{etoc}
\RequirePackage{setspace}
\setstretch{1.2}
\RequirePackage{geometry}
\geometry{
        top=2.5cm,
        bottom=2cm,
        inner=1.7cm,
        outer=1.7cm,
        headsep=10pt,
        headheight=0.5cm,
        footskip=1.4cm,
        columnsep=1cm,
        %showframe,
}

\RequirePackage{array}
\RequirePackage{booktabs}
\RequirePackage{textcomp}
\RequirePackage{multirow}
\RequirePackage{nicematrix}
\RequirePackage{makecell}
\RequirePackage{colortbl}
\RequirePackage{pgfplots}
\RequirePackage{pgfplotstable}
\pgfplotsset{compat=1.18}
\RequirePackage{pdfpages}
\RequirePackage{multicol}

\RequirePackage{tikz}
\RequirePackage[skins]{tcolorbox}
\usetikzlibrary{decorations.pathreplacing,calligraphy}
\usetikzlibrary{automata, arrows, calc, matrix, positioning, math}
\tikzset{>=stealth}

\RequirePackage{wrapfig}
\RequirePackage{graphicx}
\RequirePackage[svgnames, table]{xcolor}
\definecolor{vulm}{HTML}{7d1dd3}
\definecolor{yulm}{HTML}{ffe500}
\RequirePackage{hyperref}

\hypersetup{
    linkbordercolor=vulm,
    citebordercolor=vulm,
    menubordercolor=yulm
}

\RequirePackage[justification=centering]{caption}

\ifnum\importmath=1%
	\RequirePackage{mpb_math}
\fi
\ifnum\importinfo=1\relax%
	\RequirePackage{mpb_info}
\fi


\RequirePackage{fancyhdr}
\pagestyle{fancy}

\renewcommand{\headrulewidth}{0.5pt}

\fancyhf{}
\fancyhead[LE, RO]{\sffamily\thepage}
\fancyhead[LO]{\rightmark}
\fancyhead[RE]{\leftmark}

\fancypagestyle{plain}{
        \fancyhead{}
        \renewcommand{\headrulewidth}{0pt}
}

\RequirePackage{emptypage}

\ifnum\importmath=1
\renewcommand{\titlepage}[4]{
        \thispagestyle{empty}
        \begin{tikzpicture}[overlay,remember picture]
         \end{tikzpicture}
        \begin{tikzpicture}[remember picture, overlay]
                \path[fill tile picture={%
                      \node[inner sep=0pt,outer sep=0pt] {\usebox{\tileone}};
                    }] (current page.south east) rectangle (current page.north west);
                \node [inner sep=0pt] at (current page.center) {#1};
                \node [anchor=center, yshift=5cm, inner sep=1.25cm, rectangle, fill=vulm!50, fill opacity=1, text opacity=1, minimum height=0.2\paperheight, text width=.9\paperwidth, minimum width=\paperwidth] (title) at (current page.center) {#2};
                \node [anchor=north east, rectangle, fill=white, fill opacity=.5, text opacity=1, yshift=-1.4cm, xshift=-.1\paperwidth] at (title.south) {\includegraphics[width=.3\linewidth]{#3}};
                \node [anchor=north west, rectangle, fill=white, fill opacity=.5, text opacity=1, xshift=+.1\paperwidth, yshift=-1.4cm] at (title.south) {\includegraphics[width=.3\linewidth]{~/Documents/ETUDES/ENS/ens_psl}};
                \node [anchor=south, yshift=4cm, inner sep=1.25cm, minimum height=0.2\paperheight, minimum width=\paperwidth, text width=0.9\paperwidth, rectangle, fill=white, fill opacity=.5, text opacity=1] at (current page.south) {#4};
        \end{tikzpicture}
        \cleardoublepage\pagenumbering{arabic}
}


\RequirePackage{adforn}
\definecolor{stictchbrown}{HTML}{E7D192}

\newsavebox{\tileone}
\sbox{\tileone}{%
  \begin{tikzpicture}[x=1cm,y=1cm]
  \clip (0,0) rectangle (2,2);
  \foreach \x in {0,1} {
    \foreach \y in {0,1} {
       \node[font=\Large,text=vulm!20]
         at (2*\x, 2*\y) {$\beth$};
       \node[font=\Large,text=yulm!80!black!40]
         at (2*\x+1, 2*\y+1) {$\aleph$};
     }
  }
  \begin{scope}[dashed, double, stictchbrown!50]
    \draw plot (\x,\x-1);
    \draw plot (\x,\x+1);
    \draw plot (\x,-\x+1);
    \draw plot (\x,-\x+3);
  \end{scope}
  \end{tikzpicture}%
}

\pgfplotsset{colormap/violet}
\pgfplotstableset{
    /color cells/min/.initial=0,
    /color cells/max/.initial=1000,
    /color cells/textcolor/.initial=,
    %
    color cells/.code={%
        \pgfqkeys{/color cells}{#1}%
        \pgfkeysalso{%
            postproc cell content/.code={%
                %
                \begingroup
                %
                \pgfkeysgetvalue{/pgfplots/table/@preprocessed cell content}\value
                \ifx\value\empty
                    \endgroup
                \else
                \pgfmathfloatparsenumber{\value}%
                \pgfmathfloattofixed{\pgfmathresult}%
                \let\value=\pgfmathresult
                %
                \pgfplotscolormapaccess
                    [\pgfkeysvalueof{/color cells/min}:\pgfkeysvalueof{/color cells/max}]
                    {\value}
                    {\pgfkeysvalueof{/pgfplots/colormap name}}%
                %
                \pgfkeysgetvalue{/pgfplots/table/@cell content}\typesetvalue
                \pgfkeysgetvalue{/color cells/textcolor}\textcolorvalue
                %
                \toks0=\expandafter{\typesetvalue}%
                \xdef\temp{%
                    \noexpand\pgfkeysalso{%
                        @cell content={%
                            \noexpand\cellcolor[rgb]{\pgfmathresult}%
                            \noexpand\definecolor{mapped color}{rgb}{\pgfmathresult}%
                            \ifx\textcolorvalue\empty
                            \else
                                \noexpand\color{\textcolorvalue}%
                            \fi
                            \the\toks0 %
                        }%
                    }%
                }%
                \endgroup
                \temp
                \fi
            }%
        }%
    }
}

\fi

\author{Null}
\title{None}

\setcounter{secnumdepth}{4}
\titleformat{\paragraph}
{\normalfont\normalsize\bfseries}{\theparagraph}{1em}{}
\titlespacing*{\paragraph}
{0pt}{3.25ex plus 1ex minus .2ex}{1.5ex plus .2ex}

\AtBeginDocument{\def\labelitemi{$\bullet$}}
\newcommand{\bettertitle}{\maketitle
\begin{center}
    \includegraphics[height=6em]{/home/matthieu/Documents/ETUDES/ENS/ens_psl.pdf}
\end{center}
%\newpage
\tableofcontents}

