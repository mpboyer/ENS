\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{mpbmail}

\PassOptionsToClass{options, foldmarks=true,foldmarks=blmtP,fromalign=left,fromrule=afteraddress,fromlogo,fromphone,fromemail,version=last}{scrlttr2}
\newif\if@french
\DeclareOption{french}{\@frenchtrue}

\newif\if@british
\DeclareOption{british}{\@britishtrue}

\ProcessOptions

\LoadClass{scrlttr2}


\if@french
\usepackage[french]{babel}
\setkomavar{fromname}[Expéditeur : ]{Matthieu Boyer}
\fi

\if@british
\usepackage[british]{babel}
\setkomavar{fromname}[Sender : ]{Matthieu Boyer}
\fi
\usepackage{graphicx}
\setkomavar{fromaddress}{45 Rue d'Ulm \\
75005 Paris}
\setkomavar{fromemail}{matthieu.boyer@ens.psl.eu}
\setkomavar{fromphone}{+33\,6\,13\,68\,72\,59}
% \setkomavar{fromlogo}{\includegraphics[scale = .16]{concentric-rinds}}

