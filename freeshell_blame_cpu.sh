for ((i=1;i<=7;++i)); do echo s$i; ssh s$i ps aux --sort=+pcpu | tail -n 10; done
