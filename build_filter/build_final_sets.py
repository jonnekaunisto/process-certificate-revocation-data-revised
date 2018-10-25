#! /usr/bin/env python
from multiprocessing import Process, Queue,Value
import json

workers = 64
infile_certs1 = '../certs_using_crl.json' 
infile_certs2 = '../certs_without_crl.json'
infile_revoked1 = '../final_OCSP_revoked.json'
infile_revoked2 = '../final_CRL_revoked.json'
unrevoked_outfile = 'final_unrevoked/'
revoked_outfile = 'final_revoked/'

def doWork(i, q, revokedDict, check_finish):
    print('starting worker ' + str(i))
    rev_out = open(revoked_outfile + str(i) + '.json', 'w')
    unrev_out = open(unrevoked_outfile + str(i) + '.json', 'w')
    while True:
        if check_finish.value and q.empty():
            break
        try:
            cert = json.loads(q.get(timeout=1))
            fingerprint = cert['parsed']['fingerprint_sha256']
        except:
            continue
        if(fingerprint in revokedDict):
            rev_out.write(fingerprint + '\n')
        else:
            unrev_out.write(fingerprint + '\n')
        
def buildRevokedDict():
    revokedDict = {}
    revoked1 = open(infile_revoked1, 'r')
    revoked2 = open(infile_revoked2, 'r')
    ctr = 0
    for line in revoked1:
        ctr += 1
        if(ctr % 10000 == 0):
                print(str(ctr) + " certs added to dict")
        try:
            cert = json.loads(line)
            fingerprint = cert['parsed']['fingerprint_sha256']
            revokedDict[fingerprint] = True
        except ValueError:
            pass
    for line in revoked2:
        ctr += 1
        if(ctr % 10000 == 0):
                print(str(ctr) + " certs added to dict")
        try:
            cert = json.loads(line)
            fingerprint = cert['parsed']['fingerprint_sha256']
            revokedDict[fingerprint] = True
        except ValueError:
            pass
    return revokedDict;

if __name__ == '__main__':
    print('building revoked dictionary...')
    revokedDict = buildRevokedDict()
    q = Queue(workers * 16)
    check_finish = Value('i', 0)
    for i in range(workers):
        p = Process(target=doWork, args=(i, q, revokedDict, check_finish))
        p.start()
    try:
        ctr = 0
        for cert in open(infile_certs1, 'r'):
            q.put(cert)
            ctr += 1
            if(ctr % 10000 == 0):
                print(str(ctr) + " certificates processed")
        for cert in open(infile_certs2, 'r'):
            q.put(cert)
            ctr += 1
            if(ctr % 10000 == 0):
                print(str(ctr) + " certificates processed")
        print("End of put certificates into queue")
        check_finish.value = 1
    except KeyboardInterrupt:
        sys.exit(1)
