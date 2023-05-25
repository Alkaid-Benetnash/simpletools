#!/bin/bash
SRCDIR=$1
shift 1
help() {
    echo "Use case: ${0} src/dir ssh_host:/dest/dir [...]"
    echo "Example ssh_config:"
    cat << EOF
    Host h1
      ...
    Host h2
      ...
    Host h1 h2
        ControlMaster auto
        ControlPath /tmp/ssh.persist.%u-%n
        ControlPersist 2h
EOF
}
RSYNCFLAGS="--delete-after --exclude=local --exclude=terminfo --copy-unsafe-links"
sigint_handler() {
	echo "sigint triggered force rsync"
	echo "sigquit to quit"
	#rsync_all $@
}
trap sigint_handler SIGINT
trap exit SIGQUIT
if [ $# -lt 1 ]; then
	help
	exit -1
fi
for dst in $@; do
	echo "Auto rsync uploading $SRCDIR to $dst"
done
while true; do
	# script logic:
	# Use inotifywait to guard a loop-body. If any tracked file changed
	# with in that loop-body. The loop will not be blocked and it will
	# continue the next iteration
	# Currently, the loop-body is parallel-rsync
	symlinks=$(find ${SRCDIR} -type l)
	inotifywait -r -e modify,create,delete,move --exclude="(${SRCDIR}/local|.*\.swp|.*\.swx|${SRCDIR}/terminfo)" ${SRCDIR} ${symlinks} &
	for dst in $@; do
		rsync -aq ${RSYNCFLAGS} ${SRCDIR}/ ${dst}/ && \
		echo "$(date) uploaded to ${dst}" &
	done
	wait $(jobs -rp)
	# sleep to workaround blaze build
	sleep 1
done
