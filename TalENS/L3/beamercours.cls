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

% \AtBeginSection[]{\begin{frame}{Plan}\tableofcontents[subsectionstyle=shaded/hide,sectionstyle=show/shaded]\end{frame}}

\AtBeginSubsection[]{\begin{frame}{Plan}\tableofcontents[subsectionstyle=show/shaded/hide,sectionstyle=show/shaded]\end{frame}}

\author{Matthieu Boyer}
\institute{\includegraphics[height=3em]{ens_psl}}

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

\renewcommand{\O}{\mathcal{O}}
\newcommand{\Z}{\mathbb{Z}}
\newcommand{\R}{\mathbb{R}}
\newcommand{\Q}{\mathbb{Q}}
\newcommand{\C}{\mathbb{C}}
\newcommand{\N}{\mathbb{N}}
\newcommand{\abs}[1]{\left|#1\right|}

