rm final_revoked.json
rm final_unrevoked.json

rm final_CRL_revoked.json
rm final_OCSP_revoked.json

rm certs_using_crl.json
rm certs_without_crl.json

cd get_CRL_revocations/
rm CRL_servers
rm CRL_servers_final
rm megaCRL
rm -rf raw_CRLs
rm -rf revokedCRLCerts
cd ..

cd get_OCSP_revocations/c
rm -rf OCSP_revoked
cd ..

cd build_filter/
rm -rf final_revoked
rm -rf final_unrevoked

