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
\RequirePackage{booktabs}
\RequirePackage{textcomp}
\tikzset{>=stealth}
\RequirePackage{ragged2e}
\RequirePackage{amsmath, amsthm, amssymb}
\RequirePackage{multirow}
\RequirePackage{stmaryrd}
\RequirePackage{listings}

\newenvironment{attention}{\begin{tabular}{m{.1\linewidth}m{.8\linewidth}}\includegraphics[width=\linewidth]{attention}&}{\end{tabular}}

\usefonttheme[onlymath]{serif}
\RequirePackage{setspace}
\setstretch{1.2}

\mode<presentation>
\usetheme{Dresden}


% \AtBeginSection[]{\begin{frame}{Plan}\tableofcontents[subsectionstyle=show/shaded/hide,sectionstyle=show/shaded]\end{frame}}

\AtBeginSubsection[]{\begin{frame}{Plan}\tableofcontents[subsectionstyle=show/shaded/hide,sectionstyle=show/shaded]\end{frame}}

\author{Matthieu Boyer}
% \institute{\includegraphics[height=3em]{ens_psl}}

\setbeamertemplate{navigation symbols}{}


\lstset{showstringspaces=false}

\newcommand{\latex}[1][]{\lstinline[language={[LaTeX]TeX},emph={#1}]}
\lstnewenvironment{latexblock}[1][]{\lstset{columns=flexible,language=[LaTeX]TeX,emph={#1}}}{}
\newcommand{\deriv}[2]{\frac{\mathrm{d}}{\mathrm{d}#1}\!\left(#2\right)}
\newtheorem{definitionfr}{Définition}


\ifdefined\beamerboxesrounded
\definecolor{mygray}{gray}{0.90}
\definecolor{mygreen}{rgb}{0,0.5,0}
\definecolor{maroon}{rgb}{0.5,0,0}
\lstset{emphstyle=\color{alert},basicstyle=\small\ttfamily,stringstyle=\color{mygreen},keywordstyle=\color{structure.fg},commentstyle=\color{maroon}\itshape,backgroundcolor=\color{mygray}}
\let\oldlatex\latex
\renewcommand{\latex}[1]{\colorbox{mygray}{\oldlatex{#1}}}
\fi

\newtheorem{remark}{Remarque}[theorem]
\newtheorem{proposition}{Proposition}[subsection]
\renewcommand\qedsymbol{$\blacksquare$}
\renewcommand{\phi}{\varphi}
\renewcommand{\epsilon}{\varepsilon}
\renewcommand{\emptyset}{\varnothing}
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
\newcommand{\comp}[1]{\textsc{#1}}
\newcommand{\onen}[1]{\left\llbracket 1, #1\right\rrbracket}


\definecolor{vulm}{HTML}{7d1dd3}
\definecolor{yulm}{HTML}{ffe500}
\setbeamercolor{structure}{fg = vulm}
\setbeamercolor{section in head/foot}{fg = yulm}
\setbeamercolor{subsection in head/foot}{fg = yulm}

\usetikzlibrary{automata, arrows, calc, matrix, positioning}
\definecolor{vulm}{HTML}{7d1dd3}
\definecolor{yulm}{HTML}{ffe500}
\usepackage{caption}

\usepackage{tcolorbox}
\tcbuselibrary{theorems}
\NewTcbTheorem[auto counter, number within=section]{définition}{Définition}%
 {colback=yulm!10, colframe=vulm!45!black, fonttitle=\bfseries}{def}
\resetcounteronoverlays{tcb@cnt@définition}

\NewTcbTheorem[auto counter, number within=section]{théorème}{Théorème}%
 {colback=yulm!10!white, colframe=vulm!65!black, fonttitle=\bfseries}{thm}
 \resetcounteronoverlays{tcb@cnt@théorème}

\NewTcbTheorem[auto counter, number within=section]{propositionfr}{Proposition}%
 {colback=yulm!10!white, colframe=vulm!25!black, fonttitle=\bfseries}{propo}
 \resetcounteronoverlays{tcb@cnt@propositionfr}

\NewTcbTheorem[auto counter, number within=section]{corollaire}{Corollaire}%
 {colback=yulm!10, colframe=vulm!35!black, fonttitle=\bfseries}{cor}
 \resetcounteronoverlays{tcb@cnt@corollaire}

\NewTcbTheorem[auto counter, number within=section]{lemme}{Lemme}%
 {colback=yulm!10, colframe=vulm!15!black, fonttitle=\bfseries}{lemme}
 \resetcounteronoverlays{tcb@cnt@lemme}

\NewTcbTheorem[auto counter, number within=section]{remarque}{Remarque}%
 {colback=yulm!10, colframe=vulm!65!black, fonttitle=\bfseries}{rem}
 \resetcounteronoverlays{tcb@cnt@remarque}


