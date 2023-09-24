\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{cours}

\LoadClassWithOptions{article}
\RequirePackage[a4paper,margin=3cm]{geometry}
\RequirePackage{cmap}
\RequirePackage{lmodern}
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage[british, french]{babel}
\RequirePackage{texnames}
\RequirePackage{array}
\RequirePackage{tikz}
\RequirePackage{booktabs}
\RequirePackage{textcomp}
\tikzset{>=stealth}
\RequirePackage{ragged2e}
\RequirePackage{amsmath, amsthm, amssymb}
\RequirePackage{multirow}
\RequirePackage{listings}
\RequirePackage{algorithm}
\RequirePackage{titlesec}
\RequirePackage{enumitem}
\RequirePackage{algpseudocode}
\RequirePackage{etoc}
\RequirePackage{stmaryrd}
\setcounter{secnumdepth}{4}
\RequirePackage{wrapfig}
\RequirePackage{graphicx}
\RequirePackage{hyperref}
\graphicspath{ {./} }
\RequirePackage[justification=centering]{caption}

\author{Null}
\title{None}
% \institute{\includegraphics[height=6em]{ens_psl}}


\AfterBeginDocument{\maketitle\tableofcontents}
\newcommand{\AtEverySection}[1]{%
\let\savedsection\section
\renewcommand{\section}[2][]{\savedsection[##1]{##2} #1}
}
\AtEverySection{\localtableofcontents}

\titleformat{\paragraph}
{\normalfont\normalsize\bfseries}{\theparagraph}{1em}{}
\titlespacing*{\paragraph}
{0pt}{3.25ex plus 1ex minus .2ex}{1.5ex plus .2ex}


\newtheorem{theorem}{Théorème}[paragraph]
\newtheorem{corollary}{Corollaire}[theorem]
\newtheorem{lemma}[theorem]{Lemme}
\renewcommand\qedsymbol{$\blacksquare$}

\newcommand{\nocontentsline}[3]{}
\newcommand{\tocless}[2]{\bgroup\let\addcontentsline=\nocontentsline#1{#2}\egroup}

