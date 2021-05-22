#!/bin/bash
COMMAND=/usr/bin/analyzer
FREELINGSHARE=/usr/share/freeling $COMMAND --server -p 9999 --outlv tagged -f analyzer.cfg &
FREELINGSHARE=/usr/share/freeling $COMMAND --server -p 9995 --outlv tagged -f analyzer_en.cfg &
FREELINGSHARE=/usr/share/freeling $COMMAND --server -p 9994 --outlv tagged -f analyzer_fr.cfg &

FREELINGSHARE=/usr/share/freeling $COMMAND --server -p 9998 --outlv parsed -f analyzer.cfg &
FREELINGSHARE=/usr/share/freeling $COMMAND --server -p 9993 --outlv parsed -f analyzer_en.cfg &
FREELINGSHARE=/usr/share/freeling $COMMAND --server -p 9992 --outlv parsed -f analyzer_fr.cfg &

FREELINGSHARE=/usr/share/freeling $COMMAND --server -p 9997 --outlv dep -f analyzer.cfg &
FREELINGSHARE=/usr/share/freeling $COMMAND --server -p 9996 --outlv dep -f analyzer_en.cfg &
FREELINGSHARE=/usr/share/freeling $COMMAND --server -p 9991 --outlv dep -f analyzer_fr.cfg &
 