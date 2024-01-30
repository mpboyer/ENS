\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{cours}

\LoadClassWithOptions{article}
\RequirePackage[a4paper,margin=3cm]{geometry}
\RequirePackage{cmap}
\RequirePackage{lmodern}
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage[british]{babel}
\RequirePackage{texnames}
\RequirePackage{array}
\RequirePackage{tikz}
\RequirePackage{booktabs}
\RequirePackage{textcomp}
\RequirePackage{pdfpages}
\tikzset{>=stealth}
\RequirePackage{ragged2e}
\RequirePackage{amsfonts, amsmath, amsthm, amssymb}
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
%\institute{\includegraphics[height=6em]{ens_psl}}


\AfterBeginDocument{\maketitle\tableofcontents}


\titleformat{\paragraph}
{\normalfont\normalsize\bfseries}{\theparagraph}{1em}{}
\titlespacing*{\paragraph}
{0pt}{3.25ex plus 1ex minus .2ex}{1.5ex plus .2ex}


\newtheorem{theorem}{Theorem}[subsection]
\newtheorem{corollary}{Corollary}[theorem]
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{remark}{Remark}[theorem]
\newtheorem{proposition}{Proposition}[subsection]
\newtheorem{definition}{Definition}[subsection]
\renewcommand\qedsymbol{$\blacksquare$}
\renewcommand{\phi}{\varphi}
\renewcommand{\epsilon}{\varepsilon}
\renewcommand{\emptyset}{\varnothing}

\newcommand{\nocontentsline}[3]{}
\newcommand{\tocless}[2]{\bgroup\let\addcontentsline=\nocontentsline#1{#2}\egroup}
\newcommand{\abs}[1]{\left|#1\right|}


\makeatletter
\renewcommand{\ALG@name}{Algorithm}
\newcommand{\algorithmautorefname}{Algorithm}
\makeatother 

\algblock{Input}{EndInput}
\algnotext{EndInput}


\renewcommand{\O}{\mathcal{O}}
\newcommand{\Z}{\mathbb{Z}}
\newcommand{\R}{\mathbb{R}}
\newcommand{\Q}{\mathbb{Q}}
\newcommand{\C}{\mathbb{C}}
\newcommand{\N}{\mathbb{N}}
\newcommand{\onen}[1]{\left\llbracket 1, #1\right\rrbracket}
\newcommand{\transpose}[1]{{^{\mathsf{t}}}#1}