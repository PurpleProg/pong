#!/bin/bash
BRANCH=`git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/\1/'`
if [ ! "${BRANCH}" == "" ]
then
	echo "[${BRANCH}${STAT}]"
else
	echo ""
fi
