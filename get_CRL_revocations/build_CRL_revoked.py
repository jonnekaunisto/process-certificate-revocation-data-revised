from urlparse import urlparse
import os.path
from multiprocessing import Process, Queue, Value
import json
import sys
import time

WORKERS = 256
INFILE = '../certs_using_crl.json'
CRL = 'megaCRL'
OUTFILE = 'revokedCRLCerts/certs'

def doWork(i, q, megaCRL_org, megaCRL_CN, check_finish):
    print('starting worker ' + str(i))
    num = 0;
    with open(OUTFILE + str(i), 'w') as out:
        while True:
            try:
                if check_finish.value and q.empty():
                    break
                cert = json.loads(q.get(timeout=1))
                num += 1;
                serial = int(cert['serial_number'])
                issuer = cert['issuer']
            except:
                continue # skip to next certificate
            try:
                org = issuer['organization'][0].replace(" ", "_")
            except:
                org = 'unknown'
            try:
                CN = issuer['common_name'][0].replace(" ", "_")
            except:
                CN = 'unknown'
            if(isRevoked(megaCRL_org, megaCRL_CN, org, CN, serial)):
                out.write(json.dumps(cert) + '\n')
            if num % 100000 == 0:
                print("worker %d handles %d certifications" %(i, num))
        print("worker %d exit" %i)

def isRevoked(megaCRL_org, megaCRL_CN, org, CN, serial):
    if org in megaCRL_org:
        if serial in megaCRL_org[org]:
            return True
    if CN in megaCRL_CN:
        if serial in megaCRL_CN[CN]:
            return True
    return False

def buildDict():
    megaCRL_CN = {}
    megaCRL_org = {}
    crlFile = open(CRL, 'r')
    for line in crlFile:
        parsed = json.loads(line)
        issuer = parsed['crl_issuer']
        for entry in issuer:
            if entry[0] == "O":
                org = entry[1].replace(" ", "_")
                if not org in megaCRL_org:
                    megaCRL_org[org] = []
                for serial in parsed['cert_serials']:
                    megaCRL_org[org].append(int(serial, 16))
            if entry[0] == "CN":
                CN = entry[1].replace(" ", "_")
                if not CN in megaCRL_CN:
                    megaCRL_CN[CN] = []
                for serial in parsed['cert_serials']:
                    megaCRL_CN[CN].append(int(serial, 16))
    return megaCRL_CN, megaCRL_org

if __name__ == '__main__':
    print('building megaCRL...')
    check_finish = Value('i', 0)
    megaCRL_CN, megaCRL_org = buildDict()
    q = Queue(WORKERS * 16)
    #q = Queue()
    for i in range(WORKERS):
        p = Process(target=doWork, args=(i, q, megaCRL_org, megaCRL_CN, check_finish))
        p.start()
    try:
        ctr = 0
        for cert in open(INFILE, 'r'):
            q.put(cert)
            ctr += 1
            if(ctr % 10000 == 0):
                print(str(ctr) + " certificates processed")
        check_finish.value = 1
    except KeyboardInterrupt:
        sys.exit(1)
