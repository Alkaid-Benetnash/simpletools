#!/bin/bash
# This script should be executed via root (sudo)
# It creates a new netns that goes under an NAT of a predefined network
# interface, gateway, etc. via a veth link.
# This is useful if you want two isolated network namespace each of which has a
# default gateway (e.g. one private network, one public network)
#
set -e 
# configurations:
# Users should check and change the following lines to accommodate their needs
USER=user
NETNS_ROUTE_TABLE=5421
NETNS_HOST_IF=veth0
NETNS_NS_IF=veth1
NETNS_NS_NAME=publicn
NETNS_NS_DNS=1.1.1.1
NETNS_HOST_IP=10.0.0.1
NETNS_NS_IP=10.0.0.2
NETNS_NS_SUBNET=24
NETNS_FWD_IF=wlan0
NETNS_FWD_GATEWAY=192.168.1.1
#end of configurations

# This is the most error prone part, execute this first
setup_route() {
    ip route add default via ${NETNS_FWD_GATEWAY} dev ${NETNS_FWD_IF} table ${NETNS_ROUTE_TABLE}
    ip route | grep -v default | while read line; do
	ip route add ${line} table ${NETNS_ROUTE_TABLE}
    done
}
setup_if() {
    ip link add ${NETNS_HOST_IF} type veth peer name ${NETNS_NS_IF}
    ip link set ${NETNS_HOST_IF} up
    ip addr add ${NETNS_HOST_IP}/${NETNS_NS_SUBNET} dev ${NETNS_HOST_IF}
    ip rule add from all iif ${NETNS_HOST_IF} table ${NETNS_ROUTE_TABLE}

    # setup NAT
    iptables -t nat -A POSTROUTING -o ${NETNS_FWD_IF} -j MASQUERADE
    sysctl net.ipv4.conf.${NETNS_FWD_IF}.forwarding=1
    sysctl net.ipv4.conf.${NETNS_HOST_IF}.forwarding=1
}
create_ns() {
    ip netns add ${NETNS_NS_NAME}
    ip link set ${NETNS_NS_IF} netns ${NETNS_NS_NAME}
    mkdir -p /etc/netns/${NETNS_NS_NAME}
    RESOLVCONF=/etc/netns/${NETNS_NS_NAME}/resolv.conf
    if [ ! -f ${RESOLVCONF} ]; then
	echo "Creating new resolv.conf using DNS ${NETNS_NS_DNS}"
	echo "nameserver ${NETNS_NS_DNS}" > ${RESOLVCONF}
    fi
    ip netns exec ${NETNS_NS_NAME} ip link set ${NETNS_NS_IF} up
    ip netns exec ${NETNS_NS_NAME} ip addr add ${NETNS_NS_IP}/${NETNS_NS_SUBNET} dev ${NETNS_NS_IF}
    ip netns exec ${NETNS_NS_NAME} ip route add default via ${NETNS_HOST_IP} dev ${NETNS_NS_IF}
    echo "Inside NS ${NETNS_NS_NAME} resolv.conf is :"
    ip netns exec ${NETNS_NS_NAME} cat /etc/resolv.conf
}

ns_shell() {
    echo "#####################################################################"
    echo "## A new NS ${NETNS_NS_NAME} will be created, you are getting a shell from inside that NS. You can access to the public network in that shell."
    echo "## NOTICE: Once you exit this shell, all NS environment will be destroyed"
    echo "#####################################################################"
    ip netns exec ${NETNS_NS_NAME} sudo -u ${USER} -s
}

shutdown_ns() {
    set -o errexit off
    ip route flush table ${NETNS_ROUTE_TABLE}
    ip rule del from all iif ${NETNS_HOST_IF} table ${NETNS_ROUTE_TABLE}
    iptables -t nat -D POSTROUTING -o ${NETNS_FWD_IF} -j MASQUERADE
    ip link del ${NETNS_HOST_IF}
    ip netns del ${NETNS_NS_NAME}
}
trap shutdown_ns EXIT

if [ "$EUID" != "0" ]; then
    echo "Please execute this with root permission"
    exit 1
fi
setup_route
setup_if
create_ns
ns_shell
while true; do
    echo -n "Do you really want to exit and destroy this NS environment (y/n)? "
    read choice
    case $choice in
	y|yes|Y|Yes) break;;
	n|no|N|No) ns_shell;;
	*) echo "Invalid Choice";;
    esac
done
echo "You have exit the NS shell."
echo "Destroying this NS environment."
