%% This program is  free software; you can redistribute  it and/or modify
%% it under the  terms of the GNU General Public  License as published by
%% the Free Software Foundation; either  version 2 of the License, or (at
%% your option) any later version.

%% This program  is distributed in the  hope that it will  be useful, but
%% WITHOUT   ANY  WARRANTY;   without  even   the  implied   warranty  of
%% MERCHANTABILITY  or FITNESS  FOR A  PARTICULAR PURPOSE.   See  the GNU
%% General Public License for more details.

%% This is file `ajceam-class.cls', the class file for publications
%% in the "Academic Journal on Computing, Engineering and Applied Mathematics
%% from Universidade Federal do Tocantins, Brazil,
%% https://
%% This file was originally written by Tiago Almeida
%% First revision: 2019-10-29
%% Second revision: 2020-03-17
%%
%% History:
%%           2019-10-29  First version by Tiago Almeida
%%

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ajceam-class}[2019/10/29 AJCEAM paper class]

% Initial Statements
\DeclareOption{11pt}{\OptionNotUsed}
\DeclareOption{12pt}{\OptionNotUsed}
\DeclareOption{onecolumn}{\OptionNotUsed}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\newif\if@isblind\@isblindfalse
\DeclareOption{blind}{\@isblindtrue}
% Language Statements
\newif\iflang@eng
\newif\iflang@por
\def\lang@mutopterr{%
    \PackageError{lang}{Options 'eng' and 'por' are mutually exclusive.}{}%
}%
\DeclareOption{eng}{%
    \iflang@por\lang@mutopterr\fi
    \lang@engtrue\lang@porfalse
}
\DeclareOption{por}{%
    \iflang@eng\lang@mutopterr\fi
    \lang@engfalse\lang@portrue
}

\ProcessOptions\relax
\LoadClass[twoside,a4paper,10pt,twocolumn,english]{article}

% Default language: English
  \iflang@eng
  \else
    \iflang@por
    \else
      \lang@engtrue\lang@porfalse
    \fi
  \fi


% Required Packages
\usepackage[utf8]{inputenc}
    \iflang@eng
      \usepackage[english]{babel}
    \fi
    \iflang@por
      \usepackage[portuguese,english]{babel}
    \fi
\usepackage[T1]{fontenc}
\usepackage{ae,aecompl}
\usepackage{pslatex}
\usepackage[samesize]{cancel}
\usepackage{graphicx}
\usepackage{setspace}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{float}
\usepackage{mathptmx} % Use the Adobe Times Roman as the default text font together with math symbols from the Sym­bol, Chancery and Com­puter Modern fonts
\usepackage{url}
\Urlmuskip=0mu plus 1mu % break url lines
\usepackage{calc}
\usepackage{tabto}
\usepackage{lettrine}

%%% PDF file setup
\usepackage[bookmarks,
                 bookmarksopen = true,
                 bookmarksnumbered = true,
                 breaklinks = true,
                 colorlinks = true,
                 linkcolor = black,
                 urlcolor  = black,
                 citecolor = black,
                 anchorcolor = green,
                 hyperindex = true,
                 hyperfigures
                 ]{hyperref}


% Page setup
\setlength{\hoffset}{-1in}
\setlength{\voffset}{-1in}
\setlength{\oddsidemargin}{2cm}
\setlength{\evensidemargin}{2cm}
\setlength{\topmargin}{.7cm}
\setlength{\headheight}{1.2cm}
\setlength{\headsep}{0.4cm}
\setlength{\textheight}{25.7cm}
\setlength{\textwidth}{17.5cm}
\setlength{\footskip}{1.0cm}
\setlength{\columnsep}{0.5cm}

% Author and Affiliate Setup
\usepackage[noblocks]{authblk}
\renewcommand\AB@affilsepx{\protect\par\protect\Affilfont}
\iflang@eng
  \renewcommand\Authands{ and }
  \renewcommand\Authand{ and }
\fi
\iflang@por
  \renewcommand\Authands{ e }
  \renewcommand\Authand{ e }
\fi
\renewcommand{\Affilfont}{\fontsize{9}{12} \selectfont \itshape}
\renewcommand{\Authfont}{\fontsize{12}{14} \selectfont}

% Macro Declaration
\def\thisvolume#1{\gdef\@thevolume{#1}}        % Volume
\def\thisnumber#1{\gdef\@thenumber{#1}}         % Number
\def\thismonth#1{\gdef\@themonth{#1}}             % Month
\def\thisyear#1{\gdef\@theyear{#1}}             % Year
\def\publicationdate#1{\gdef\@publicationdate{#1}}   % Publication Date
\def\abstract#1{\gdef\@englishabstract{#1}}        % Abstract in English
\def\keywords#1{\gdef\@englishkeywords{#1}}        % Keywords in English
\def\resumo#1{\gdef\@portugueseabstract{#1}}        % Resumen en inglés
\def\palavraschave#1{\gdef\@portuguesekeywords{#1}}        % Palabras clave en inglés

% Definition for contact data
\def\contactauthor#1{\gdef\@thecontactauthor{#1}}
\def\email#1{\gdef\@theemail{#1}}
\newcommand*{\contacto}{%
  \if@isblind
    \iflang@eng
      Version for reviewers.
    \fi
    \iflang@por
      Versão para revisores.
    \fi
  \else
    \iflang@eng
      \@thecontactauthor,
      \@theemail
    \fi
    \iflang@por
      \@thecontactauthor,
      \@theemail
    \fi
  \fi
}
\renewcommand*\footnoterule{}
\newcommand\blfootnote[1]{%
  \begingroup
  \renewcommand\thefootnote{}\footnote{#1}%
  \addtocounter{footnote}{-1}%
  \endgroup
}
\newcommand*{\printcontactdata}{%
  \blfootnote{\\ {\fontsize{8}{11} \selectfont
  \iflang@eng
    Contact data:
    \fi
  \iflang@por
    Dados de contato:
  \fi
  \contacto}}
}

% Header Definitions
\def\title#1{\gdef\@title{#1}\gdef\thetitle{#1}}
\def\titulo#1{\gdef\@titulo{#1}} 
\def\shorttitle#1{\gdef\@theshorttitle{#1}}
\def\firstauthor#1{\gdef\@thefirstauthor{#1}}
\newcommand*{\authorheader}{%
  \begingroup
  \ifnum\value{authors}<4 % One author
      \if@isblind
        \iflang@eng
          AUTHOR
        \fi
        \iflang@por
          AUTOR
        \fi
      \else
        \MakeUppercase{\@thefirstauthor}
      \fi
    \else % 4 or more authors
      \if@isblind
        \iflang@eng
          1st. AUTHOR~{\itshape et al.}
        \fi
        \iflang@por
          1ro. AUTOR~{\itshape et al.}
        \fi
      \else
        {\MakeUppercase{\@thefirstauthor}~{\itshape et al.}}
      \fi
    \fi
  \endgroup
  }
\newcommand{\vcenteredinclude}[1]{\begingroup
\setbox0=\hbox{\includegraphics[height=\headheight]{#1}}%
\parbox{\wd0}{\box0}\endgroup}


% Configuration of figure headings
\usepackage{caption}
\captionsetup[figure]{font=small,labelfont=bf,justification=centering}
\captionsetup[figure]{name=Fig.}
\DeclareCaptionFormat{myformat}{#1#2#3}%\rule{\linewidth}{.3pt}}
\captionsetup[figure]{format=myformat}

\captionsetup[table]{font={small,sc},labelfont={bf,sc},justification=centering}
\iflang@eng
  \captionsetup[table]{name=Table}
\fi
\iflang@por
  \captionsetup[table]{name=Tabela}
  \captionsetup[figure]{name=Figura}
\fi
\usepackage{makecell} % break lines in cell tables
\renewcommand\theadalign{cc}
\renewcommand\theadgape{\Gape[4pt]}
\renewcommand\cellgape{\Gape[4pt]}
\addtolength{\belowcaptionskip}{-8pt}
\addtolength{\abovecaptionskip}{0pt}


% Work job cover
\newcommand*\varhrulefill[1][0.4pt]{\leavevmode\leaders\hrule height#1\hfill\kern0pt}
\renewcommand{\@maketitle}{%
  \newpage
  \null
  \onecolumn
  \begingroup
    \vspace{0cm}%
    {\begin{center}%
    \noindent\varhrulefill[0.25mm] \par    
     \iflang@eng
      {\fontsize{20}{24} \selectfont \@title \par}
     \fi
     \iflang@por
      {\fontsize{20}{24} \selectfont \@titulo \par}
      \vspace{0.3cm}
      {\fontsize{14}{16}\itshape \selectfont \@title \par}
     \fi
     \noindent\varhrulefill[0.25mm] \par    
     {\setlength{\tabcolsep}{0in}
     \if@isblind
       \iflang@eng
         {\fontsize{12}{14} \selectfont Version for reviewers.} \\
       \fi
       \iflang@por
         {\fontsize{12}{14} \selectfont Versão para revisores.} \\
       \fi
     \else        
        \begin{tabular}[c]{c}%
                {\@author}
        \end{tabular}
      \fi
      %\vspace{0.1cm}
      {%\setstretch{0.85}
       \iflang@eng
         {\fontsize{8}{10} \selectfont Publication date: \@publicationdate}      
       \fi
       \iflang@por
         {\fontsize{8}{10} \selectfont Data de recebimento do manuscrito: \@receptiondate} \\
         {\fontsize{8}{10} \selectfont Data de aceitação do manuscrito: \@acceptancedate} \\
         {\fontsize{8}{10} \selectfont Data de publicação: \@publicationdate}
       \fi
     }}%
    \end{center}}% end of \parbox
    %\vspace{0.3cm}
    \noindent\varhrulefill[0.25mm] \par    
    \vspace{0.4cm}
      \iflang@eng
        \noindent {\fontsize{9}{12} \selectfont {\bfseries{Abstract}}---\@englishabstract} \par
        \vspace{0.3cm}
        \noindent {\fontsize{9}{12} \selectfont {\bfseries{Keywords}}---\@englishkeywords} \par
      \fi
      \iflang@por
        \noindent {\fontsize{9}{12} \selectfont {\bfseries{Resumo}}---\@portugueseabstract} \par
        \vspace{0.3cm}
        \noindent {\fontsize{9}{12} \selectfont {\bfseries{Palavras-chave}}---\@portuguesekeywords} \par
        \vspace{0.3cm}
        \noindent {\fontsize{9}{12}\itshape \selectfont {\bfseries{Abstract}}---\@englishabstract} \par
        \vspace{0.3cm}
        \noindent {\fontsize{9}{12}\itshape \selectfont {\bfseries{Keywords}}---\@englishkeywords} \par
      \fi
    \vspace{0.2cm}
    \noindent\varhrulefill[0.25mm]
  \twocolumn
  \endgroup
  %\vspace{0.5cm}
} % end of \@maketitle

%%% Header and footer settings
\usepackage{fancyhdr}
\pagestyle{fancy}
\renewcommand{\headrulewidth}{0pt}
\fancyhead[LO]{\includegraphics[width=1.5cm]{Logo_del_ITESM.png}}
% \fancyhead[LE]{\includegraphics[width=1.5cm]{Logo_del_ITESM.png}}
\fancyhead[RO]{{\fontsize{7}{10} \selectfont Departamento de Ingeniería y Ciencias.~\@thevolume, NO.~\@thenumber, \@themonth~\@theyear}}
% \fancyhead[RE]{{\fontsize{7}{10} \selectfont Departamento de Ingeniería y Ciencias.~\@thevolume, NO.~\@thenumber, \@themonth~\@theyear}}
\fancyhead[CE]{{\fontsize{7}{10} \selectfont \MakeUppercase{\@theshorttitle}}}
% \fancyhead[CO]{{\fontsize{7}{10} \selectfont \MakeUppercase{\@theshorttitle}}}



\renewcommand{\sectionmark}[1]{}
\renewcommand{\subsectionmark}[1]{}

%numero de pagina
% \fancyfoot[LO,LE]{ }
% \fancyfoot[CO,CE]{ }
% \fancyfoot[RO,RE]{ }
% \fancyfoot[R]{\thepage}
   
% Section Format Settings
\renewcommand{\@seccntformat}[1]{\csname the#1\endcsname.~}

\renewcommand*{\thesection}{\Roman{section}}
\renewcommand{\section}{\@startsection{section}{1}{0mm}%
                                     {-12pt}%
                                     {6pt}%
                                     {\setlength\parindent{0em} \fontsize{12}{14} \selectfont \bfseries\textsc}}%
\renewcommand \thesubsection{\alph{subsection}}
\renewcommand{\subsection}{\@startsection{subsection}{2}{0mm}%
                                     {-12pt}%
                                     {6pt}%
                                     {\setlength\parindent{0em} \fontsize{11}{13} \selectfont \bfseries\textit}}%
\renewcommand \thesubsubsection{\arabic{subsubsection}}
\renewcommand{\subsubsection}{\@startsection{subsubsection}{3}{0mm}%
                                     {-12pt}%
                                     {6pt}%
                                     {\setlength\parindent{0em} \fontsize{11}{13} \selectfont \textit}}



% Set bibliography style
\newcounter{iteminbib}
\addtocounter{iteminbib}{0}
\newlength{\bibmargin}
\setlength{\bibmargin}{20pt}
\TabPositions{\bibmargin}
\newcommand{\quotes}[1]{``#1''}
\newcommand{\insertbibliography}[1]{%
\setlength{\parindent}{0pt}
%\setlength{\bibsep}{4pt}
%\setlength\itemindent{0pt}
%\setlength{\bibhang}{\bibmargin}
{\setstretch{0.85}
\fontsize{8}{10} \selectfont
\iflang@eng
  \bibliographystyle{IEEETran}
  \renewcommand\refname{References}  
\fi
\iflang@por
  \bibliographystyle{IEEETran}
  \renewcommand\refname{Referências}  
\fi
\bibliography{#1}}
}

% Definitions for capital letter
\newcommand{\firstword}[2]{\lettrine[findent=2pt]{\textbf{#1}}{}#2 }

\if@isblind
\makeatletter
\AtBeginDocument{
   \hypersetup{
      pdfinfo={
         Title={\@title},
         Author={AUTHOR},
         Keywords={\@englishkeywords},
         Producer={AJCEAM/UFT},
         Subject={\@englishabstract}
      }
   }
}
\makeatother
\else
\makeatletter
\AtBeginDocument{
   \hypersetup{
      pdfinfo={
         Title={\@title},
         Author={\@thefirstauthor},
         Keywords={\@englishkeywords},
         Producer={AJCEAM/UFT},
         Subject={\@englishabstract}
      }
   }
}
\makeatother
\fi