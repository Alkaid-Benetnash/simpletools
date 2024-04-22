#!/bin/sh
target=backup
netconsole_path=/sys/kernel/config/netconsole/${target}
dmesg -E
dmesg -n 8 #set console log level to 8
modprobe configfs
modprobe netconsole
mount none -t configfs /sys/kernel/config
mkdir /sys/kernel/config/netconsole/${target}
cd /sys/kernel/config/netconsole/${target}
echo '192.168.100.1' > $netconsole_path/remote_ip
echo '6555' > $netconsole_path/remote_port
