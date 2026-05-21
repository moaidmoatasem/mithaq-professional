#!/bin/bash
# Reset DVWA database (sets fresh admin/password)
sudo docker exec -i dvwa php /var/www/html/setup.php

# Or restart the container fresh
sudo docker stop dvwa || true
sudo docker rm dvwa || true
sudo docker run -d --name dvwa --restart unless-stopped \
  -p 80:80 \
  -e RECAPTCHA_PRIV_KEY="" \
  -e RECAPTCHA_PUB_KEY="" \
  vulnerables/web-dvwa

# Wait 10s then try: admin / password
sleep 10
