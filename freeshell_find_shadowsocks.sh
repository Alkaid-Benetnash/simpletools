for ((i=1;i<=7;++i)); do echo s$i; ssh s$i ps aux | grep -e shadow -e vpnserver; done
