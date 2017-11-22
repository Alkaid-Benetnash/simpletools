import sys
if len(sys.argv) < 3:
    print("fname, count")
    sys.exit(-1)
fname = sys.argv[1]
count = int(sys.argv[2])
d = open(fname+'.pts','wb')
for i in range(count):
    f = open(fname+'.d/'+str(i)+'.pts','rb')
    d.write(f.read())
    f.close()
d.close()
