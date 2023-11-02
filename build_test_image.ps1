Copy-Item -Path $env:USERPROFILE\.android\adbkey -Destination .\adbkey
Copy-Item -Path $env:USERPROFILE\.android\adbkey.pub -Destination .\adbkey.pub
docker build -f Dockerfile.test -t privacy_compliance_image:v1.0 .
