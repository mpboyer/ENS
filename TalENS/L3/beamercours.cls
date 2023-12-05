\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{beamercours}

\LoadClassWithOptions{beamer}
\RequirePackage{cmap}
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage[french]{babel}
\RequirePackage{texnames}
\RequirePackage{array}
\RequirePackage{tikz}
\RequirePackage{bookmark}
\RequirePackage{booktabs}
\RequirePackage{textcomp}
\tikzset{>=stealth}
\RequirePackage{ragged2e}
\RequirePackage{amsmath, amsthm, amssymb, amsfonts}
\RequirePackage{dsfont}
\RequirePackage{multirow}
\RequirePackage{stmaryrd}
\RequirePackage{listings}
\RequirePackage{enumitem}
\RequirePackage{listings}
\RequirePackage{stmaryrd}
\RequirePackage{algorithm}
\RequirePackage{algpseudocode}
\RequirePackage{etoc}
\RequirePackage{wrapfig}
\RequirePackage{hyperref}

\usefonttheme[onlymath]{serif}
\RequirePackage{setspace}
\setstretch{1.2}

\mode<presentation>
\usetheme{Dresden}
%\AtBeginSubsection[]{\begin{frame}{Plan}\tableofcontents[subsectionstyle=show/shaded/hide,sectionstyle=show/shaded]\end{frame}}
\setbeamertemplate{navigation symbols}{}
\lstset{showstringspaces=false}

\author{Matthieu Boyer}
\institute{\includegraphics[height=3em]{ens_psl}}

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
\renewcommand{\d}{{\, \rm d}}
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
\newcommand{\deriv}[2]{\frac{\mathrm{d}}{\mathrm{d}#1}\!\left(#2\right)}
\newcommand{\onen}[1]{\left\llbracket 1, #1\right\rrbracket}



\newcommand{\latex}[1][]{\lstinline[language={[LaTeX]TeX},emph={#1}]}
\lstnewenvironment{latexblock}[1][]{\lstset{columns=flexible,language=[LaTeX]TeX,emph={#1}}}{}

\ifdefined\beamerboxesrounded
\definecolor{mygray}{gray}{0.90}
\definecolor{mygreen}{rgb}{0,0.5,0}
\definecolor{maroon}{rgb}{0.5,0,0}
\lstset{emphstyle=\color{alert},basicstyle=\small\ttfamily,stringstyle=\color{mygreen},keywordstyle=\color{structure.fg},commentstyle=\color{maroon}\itshape,backgroundcolor=\color{mygray}}
\let\oldlatex\latex
\renewcommand{\latex}[1]{\colorbox{mygray}{\oldlatex{#1}}}
\fi