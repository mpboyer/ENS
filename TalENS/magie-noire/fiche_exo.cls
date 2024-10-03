\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{fiche_exo}
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
\RequirePackage{enumitem}
\RequirePackage[a4paper]{geometry}
\geometry{
        top=2.5cm,
        bottom=2cm,
        inner=1cm,
        outer=1cm,
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
\RequirePackage{hyperref}

\ifnum\importmath=1%
\RequirePackage{mpb_math}
\fi

\ifnum\importinfo=1
\RequirePackage[kholle]{mpb_info}
\fi

\RequirePackage{xsim}
\RequirePackage[most]{tcolorbox}
\RequirePackage{needspace}
\DeclareExerciseCollection[student=A]{A}
\DeclareExerciseCollection[student=B]{B}
\DeclareExerciseCollection[student=C]{C}
\DeclareExerciseTagging{student}

\DeclareExerciseEnvironmentTemplate{custom}
  {%
    \vspace{-.6\baselineskip}
    \begin{tcolorbox}[colframe=vulm, colback=yulm!10, colbacktitle=vulm]
	    \IfInsideSolutionTF%
	    {\hspace{-6pt}\color{black}{\textbf{Solution:} \GetExercisePropertyTF{subtitle}{#1}{Question de Cours}}}
	    {\hspace{-6pt}\color{black}{\textbf{\GetExercisePropertyTF{subtitle}{#1}{Question de Cours}}}}
 
	       \end{tcolorbox}
    \noindent
  }
  {\vspace{\baselineskip}}

\xsimsetup{%
	% headings=runin,
	exercise/pre-hook = \eBox,
	exercise/post-hook = \endeBox,
	solution/pre-hook = \sBox,
	solution/post-hook = \endsBox,
	tags={Nexistepastagpointfr},
	collect,
}

\xsimsetup{exercise/template = custom,
	   solution/template = custom}

\RequirePackage{pdfpages}

\RequirePackage{tikz}
\usetikzlibrary{decorations.pathreplacing,calligraphy}
\usetikzlibrary{automata, arrows, calc, matrix, positioning, math}
\tikzset{>=stealth}

\RequirePackage{wrapfig}
\RequirePackage{graphicx}
\RequirePackage{hyperref}
\RequirePackage[justification=centering]{caption}

% ==================     Booleans     ==================
\def\TRUE{1}
\def\FALSE{0}
\def\SHOW{1}
\def\HIDE{0}

\newcommand{\shortname}{}
\newcommand{\authorname}{}
\newcommand{\coursename}{}
\newcommand{\assignment}{}
\newcommand{\duedate}{}

% ============= Gets Document Info, Generates Heading =============
\RequirePackage{fancyhdr}
\newcommand{\setheading}[5][]{\renewcommand{\shortname}{#1}
  \renewcommand{\authorname}{#2}
  \renewcommand{\coursename}{#3}
  \renewcommand{\assignment}{#4}
  \renewcommand{\duedate}{#5}
}

\newcommand{\heading}[1]{
  \thispagestyle{fancyplain}
  \clearpage
  \pagenumbering{arabic}
  %
  \begin{center}
  \begin{minipage}{0.45\textwidth}
    \begin{flushleft}
 	\hspace{-.6cm}\hypertarget{@assignment}{
        \textbf{\assignment}}\\
        \hspace{-.5cm}\authorname\\
      \hspace{-.5cm}\textbf{Planche #1}
    \end{flushleft}
  \end{minipage}
  \begin{minipage}{.5\textwidth}
  \end{minipage}
  \begin{minipage}{0.45\textwidth}
    \begin{flushright}
	    \coursename\\
	    \duedate\\
    \end{flushright}
  \end{minipage}
  \end{center}
}

\newcommand{\headingcorr}[1]{
  \thispagestyle{fancyplain}
  \clearpage
  \pagenumbering{arabic}
  %
  \begin{center}
  \begin{minipage}{0.45\textwidth}
    \begin{flushleft}
	\hspace{-.6cm}\hypertarget{@assignment}{
        \textbf{\assignment}}\\
        \hspace{-.5cm}\authorname\\
      \hspace{-.5cm}\textbf{Planche #1~:} Corrigés
    \end{flushleft}
  \end{minipage}
  \begin{minipage}{.5\textwidth}
  \end{minipage}
  \begin{minipage}{0.45\textwidth}
    \begin{flushright}
      \coursename\\
      \duedate\\
    \end{flushright}
  \end{minipage}
  \end{center}

}
% ============= Headers and Footers =============
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0.5pt}
\pagestyle{fancyplain}
\fancyhf{}
\lfoot{%
\fancyplain{}{%
  \hyperlink{@assignment}{%
    \small{%
      \color{black}{%
        \assignment%
      }
    }
  }
}
}
\rfoot{%
\fancyplain{}{%
    \small{%
      \coursename%
    }
}
}

\newcommand{\planche}[2][0]{
	\newpage
	\heading{#2}

	\printcollection{#2}
	\ifnum#1=0
	\newpage
	\headingcorr{#2}

	\printcollection[print=solutions]{#2}
	\fi
}
