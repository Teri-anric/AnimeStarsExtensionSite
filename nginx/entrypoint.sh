service nginx start

while :; do
    certbot renew --nginx --non-interactive --quiet
    sleep 12h
done
