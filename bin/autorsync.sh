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
if [ $# -lt 2 ]; then
        help
        exit -1
fi
for dst in $@; do
        echo "Auto rsync uploading $SRCDIR to $dst"
done
while true; do
        for dst in $@; do
                rsync -aq --delete ${SRCDIR}/ ${dst}/ && \
                echo "$(date) uploaded to ${dst}" &
        done
        wait $(jobs -rp)
        inotifywait -r -e modify,create,delete -q ${SRCDIR}
done
