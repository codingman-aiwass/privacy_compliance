Copy-Item -Path $env:USERPROFILE\.android\adbkey -Destination .\adbkey
docker build -t privacy_compliance_image:v1.0 .