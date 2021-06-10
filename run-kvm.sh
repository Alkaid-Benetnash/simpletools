#!/bin/sh
qemu-system-x86_64 -enable-kvm -smp 8 -m 12G -cpu host\
    -drive file=illixr.qcow2,if=virtio,aio=native,cache.direct=on \
    -net nic,model=virtio \
    -net user,hostfwd=tcp::2222-:22 \
    -vga virtio \
    -cdrom ubuntu-18.04.5-desktop-amd64.iso \
    -display sdl,gl=on
