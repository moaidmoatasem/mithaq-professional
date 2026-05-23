# DVWA Setup Report

## Which Option Worked
Option 1 worked:
```bash
sudo docker pull vulnerables/web-dvwa
sudo docker run -d --name dvwa --restart unless-stopped -p 80:80 vulnerables/web-dvwa
```
*(Note: To get docker to extract the layers without "operation not permitted" error on overlayfs, `/etc/docker/daemon.json` had to be modified to use the "vfs" storage-driver).*

## What URL Scanners Should Target
Scanners should target:
`http://localhost:80`
