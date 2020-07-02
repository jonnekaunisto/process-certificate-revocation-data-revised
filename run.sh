cd get_CRL_revocations
python extract_crls.py
sort -u CRL_servers > CRL_servers_final
mkdir raw_CRLs
cd raw_CRLs
aria2c -i ../CRL_servers_final -j 16
cd ..
mkdir revokedCRLCerts
python build_CRL_revoked.py
cat revokedCRLCerts/certs* > ../final_CRL_revoked.json
cd ..
echo Done_with_CRL_revocations
wc -l final_CRL_revoked.json
cd get_OCSP_revocations
mkdir OCSP_revoked
python build_OCSP_revoked.py
cat OCSP_revoked/certs* > ../final_OCSP_revoked.json
echo Done_With_OCSP
cd ../build_filter
mkdir final_unrevoked 
mkdir final_revoked
python build_final_sets.py
cat final_unrevoked/*.json > ../final_unrevoked.json
