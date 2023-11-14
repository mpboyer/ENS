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
\RequirePackage{amsmath, amsthm, amssymb, amsfonts}
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
    \newpage
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
\newcommand{\ml}{\mathcal{l}}

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
\newcommand{\mat}[1]{\mathcal{M}_{#1}}

\newcommand{\astuce}{$(\star)$}
