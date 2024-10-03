%%%%%%%%%%%%%%%%%%
% Class Preamble
%%%%%%%%%%%%%%%%%%
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{beamercours}
\DeclareOption{math}{\RequirePackage{mpb_math}}
\DeclareOption{info}{\RequirePackage{mpb_info}}
\LoadClassWithOptions{beamer}

%%%%%%%%%%%%%%%%%%
% Required Imports
%%%%%%%%%%%%%%%%%%
\RequirePackage{cmap}
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage[french, british]{babel}
\RequirePackage{lmodern}
\RequirePackage{texnames}
\RequirePackage{ragged2e}
\RequirePackage{setspace}
\setstretch{1.2}

\RequirePackage{array}
\RequirePackage{booktabs}
\RequirePackage{textcomp}
\RequirePackage{multirow}
\RequirePackage{multicol}
\RequirePackage{nicematrix}
\RequirePackage{makecell}
\RequirePackage{colortbl}

\RequirePackage{pdfpages}

\RequirePackage{tikz}
\RequirePackage{tikz-3dplot}
\RequirePackage{pgfplots}
\RequirePackage{pgfplotstable}
\pgfplotsset{compat=1.18}
\usetikzlibrary{decorations.pathreplacing,calligraphy}
\usetikzlibrary{automata, arrows, calc, matrix, positioning, math}
\tikzset{>=stealth}

\RequirePackage{wrapfig}
\RequirePackage{graphicx}
\RequirePackage{hyperref}
\hypersetup{
    linkbordercolor=vulm,
    citebordercolor=vulm,
    menubordercolor=yulm
}
\RequirePackage[justification=centering]{caption}

\ProcessOptions\relax

%%%%%%%%%%%%%%%%%%
% Beamer Setup
%%%%%%%%%%%%%%%%%%
\usefonttheme[onlymath]{serif}

\mode<presentation>
\usetheme{Dresden}

\AtBeginSection[]{\begin{frame}{Plan}\tableofcontents[subsectionstyle=shaded/hide,sectionstyle=show/shaded]\end{frame}}
\AtBeginSubsection[]{\begin{frame}{Plan}\tableofcontents[subsectionstyle=show/shaded/hide,sectionstyle=show/shaded]\end{frame}}

\setbeamercolor{structure}{fg = vulm}
\setbeamercolor{section in head/foot}{fg = yulm}
\setbeamercolor{subsection in head/foot}{fg = yulm}
\setbeamercolor{background canvas}{bg = yulm!10}
\setbeamertemplate{navigation symbols}{}

\author{Matthieu Boyer}
% \institute{\includegraphics[height=3em]{ens_psl}}

\RequirePackage[skins]{tcolorbox}
\resetcounteronoverlays{tcb@cnt@définition}
\resetcounteronoverlays{tcb@cnt@théorème}
\resetcounteronoverlays{tcb@cnt@propositionfr}
\resetcounteronoverlays{tcb@cnt@corollaire}
\resetcounteronoverlays{tcb@cnt@lemme}
\resetcounteronoverlays{tcb@cnt@remarque}

%%%%%%%%%%%%%%%%%%
% Document Macros
%%%%%%%%%%%%%%%%%%
\newcommand{\tocless}[2]{\bgroup\let\addcontentsline=\nocontentsline#1{#2}\egroup}

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

\newcommand{\reporttitleframe}[4]{
	\begin{tikzpicture}[overlay,remember picture]
  \end{tikzpicture}
  \begin{tikzpicture}[remember picture, overlay]
	  \node[yshift=-\headheight - 4pt] (upperleft) at (current page.north west) {};
		 \path[fill opacity=.5, fill tile picture={%
		     \node[inner sep=0pt,outer sep=0pt] {\usebox{\tileone}};
     }] (upperleft) rectangle (current page.south east);
    	\node [inner sep=0pt, anchor=north, yshift=.1\paperheight] at (current page.north) {#1};
	\node [anchor=north, rectangle, fill=vulm!50, fill opacity=1, text opacity=1, text width=.9\paperwidth, minimum width=\paperwidth, yshift=-\headheight - 8pt, minimum height=.35\paperheight, inner sep=3pt] (title) at (current page.north) {#2};
	\node [anchor=north east, rectangle, fill=yulm!10, fill opacity=.5, text opacity=1, yshift=-.017\paperheight, xshift=-.1\paperwidth] at (title.south) {\includegraphics[width=.3\linewidth]{#3}};
	\node [anchor=north west, rectangle, fill=yulm!10, fill opacity=.5, text opacity=1, xshift=+.1\paperwidth, yshift= -.017\paperheight] at (title.south) {\includegraphics[width=.3\linewidth]{~/Documents/ETUDES/ENS/ens_psl}};
	\node [anchor=south, yshift=\footheight + 4pt, minimum width=\paperwidth, text width=0.9\paperwidth, rectangle, fill=yulm!10, fill opacity=.5, text opacity=1] at (current page.south) {#4};
  \end{tikzpicture}
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

\newcommand{\beamercite}[1]{

}
