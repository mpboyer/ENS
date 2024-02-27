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
\RequirePackage{pdfpages}
\tikzset{>=stealth}
\RequirePackage{ragged2e}
\RequirePackage{amsmath}
\RequirePackage{dsfont}

\RequirePackage{amsfonts}
\RequirePackage{mathrsfs}
\RequirePackage{amsthm}
\RequirePackage{amssymb}
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
\RequirePackage[justification=centering]{caption}

\author{Null}
\title{None}


\AtBeginDocument{\def\labelitemi{$\bullet$}}
\AfterBeginDocument{
    \maketitle
    \begin{center}
        \includegraphics[height=6em]{/home/matthieu/Documents/ETUDES/ENS/ens_psl.pdf}
    \end{center}
    %\newpage
    \tableofcontents}


\titleformat{\paragraph}
{\normalfont\normalsize\bfseries}{\theparagraph}{1em}{}
\titlespacing*{\paragraph}
{0pt}{3.25ex plus 1ex minus .2ex}{1.5ex plus .2ex}

\newtheorem{theorem}{Théorème}[subsection]
\newtheorem{corollary}{Corollaire}[theorem]
\newtheorem{lemma}[theorem]{Lemme}
\newtheorem{remark}{Remarque}[theorem]
\newtheorem{proposition}{Proposition}[subsection]
\newtheorem{definition}{Définition}[subsection]
\newtheorem{example}{Exemple}[subsection]


\renewcommand{\d}{{\, \rm d}}

%Symboles
\newcommand{\Id}{\mathrm{Id}}
\newcommand{\N}{\mathbb{N}}
\newcommand{\Z}{\mathbb{Z}}
\newcommand{\Q}{\mathbb{Q}}
\newcommand{\R}{\mathbb{R}}
\newcommand{\C}{\mathbb{C}}
\newcommand{\K}{\mathbb{K}}
\newcommand{\U}{\mathbb{U}}
\renewcommand{\O}{\mathcal{O}}
\newcommand{\A}{\mathcal{A}}
\newcommand{\mL}{\mathcal{L}}
\newcommand{\B}{\mathcal{B}}
\newcommand{\ml}{\mathcal{l}}
\newcommand{\mU}{\mathcal{U}}

\renewcommand{\P}{\mathbb{P}}
\renewcommand{\d}{{\rm \, d}}

\newcommand{\asympt}{\mathop{\sim}}
\newcommand{\lin}{\mathcal{L}}
\newcommand{\M}{\mathcal{M}}
\newcommand{\cont}{\mathcal{C}}
\renewcommand{\phi}{\varphi}
\renewcommand{\epsilon}{\varepsilon}
\renewcommand{\emptyset}{\varnothing}
\renewcommand\qedsymbol{$\blacksquare$}

%Operators
\DeclareMathOperator{\Card}{Card}
\DeclareMathOperator{\Gl}{Gl}
\DeclareMathOperator{\pgcd}{pgcd}
\DeclareMathOperator{\Tr}{Tr}
\DeclareMathOperator{\rg}{rg}
\DeclareMathOperator{\ch}{ch}
\DeclareMathOperator{\sh}{sh}
\DeclareMathOperator{\sgn}{sgn}
\renewcommand{\th}{\mathop{\rm th}}
\makeatletter
\renewcommand{\ALG@name}{Algorithme}
\newcommand{\algorithmautorefname}{Algorithme}
\makeatother 

\algblock{Input}{EndInput}
\algnotext{EndInput}


%Macros
\newcommand{\applic}[4]{\begin{array}[t]{rcl}
#1 & \to & #2 \\
#3 & \mapsto & #4
\end{array}}

\newcommand{\norm}[1]{\left\lVert #1 \right\rVert}
\newcommand{\ninf}[1]{\left\lVert #1 \right\rVert_\infty}
\newcommand{\normop}[1]{\left| \left| \left| #1 \right| \right| \right|}
\newcommand{\tocless}[2]{\bgroup\let\addcontentsline=\nocontentsline#1{#2}\egroup}
\newcommand{\abs}[1]{\left|#1\right|}
\newcommand{\scalar}[1]{\left\langle #1 \right\rangle}
\newcommand{\znz}[1]{\Z/#1\Z}
\newcommand{\mat}[2]{\mathscr{M}_{#1}\left(#2\right)}
\newcommand{\poly}[1]{\mathscr{P}_{#1}}
\newcommand{\astuce}{$(\star)$}
\newcommand{\vect}[2][]{\text{Vect}_{#2}\left(#1\right)}
\renewcommand{\H}{\mathbb{H}}
\newcommand{\transpose}[1]{{^{\mathsf{t}}}#1}
\newcommand{\onen}[1]{\left\llbracket 1, #1\right\rrbracket}

\usetikzlibrary{automata, arrows, calc, matrix, positioning}
\usetikzlibrary{math}
\definecolor{vulm}{HTML}{7d1dd3}
\definecolor{yulm}{HTML}{ffe500}
\usepackage{caption}

\usepackage{tcolorbox}
\tcbuselibrary{theorems}
\NewTcbTheorem[auto counter, number within=section]{définition}{Définition}%
 {colback=yulm!10, colframe=vulm!45!black, fonttitle=\bfseries}{def}

\NewTcbTheorem[auto counter, number within=section]{théorème}{Théorème}%
 {colback=yulm!10!white, colframe=vulm!65!black, fonttitle=\bfseries}{thm}

\NewTcbTheorem[auto counter, number within=section]{propositionfr}{Proposition}%
 {colback=yulm!10!white, colframe=vulm!25!black, fonttitle=\bfseries}{propo}

\NewTcbTheorem[auto counter, number within=section]{corollaire}{Corollaire}%
 {colback=yulm!10, colframe=vulm!35!black, fonttitle=\bfseries}{cor}

\NewTcbTheorem[auto counter, number within=section]{lemme}{Lemme}%
 {colback=yulm!10, colframe=vulm!15!black, fonttitle=\bfseries}{lemme}

\NewTcbTheorem[auto counter, number within=section]{remarque}{Remarque}%
 {colback=yulm!10, colframe=vulm!65!black, fonttitle=\bfseries}{rem}
