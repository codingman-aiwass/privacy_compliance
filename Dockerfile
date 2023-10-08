# Use the Ubuntu 20.04 base image
FROM ubuntu:20.04

# Copy the custom source.list to the container
COPY sourcelist.txt /etc/apt/sources.list
ENV DEBIAN_FRONTEND=noninteractive
# Update the package lists and install necessary dependencies
RUN apt-get update && apt-get install software-properties-common -y && add-apt-repository ppa:deadsnakes/ppa
RUN apt-get install -y \
    python3.10-full \
    openjdk-8-jdk \
    wget \
    curl \
    unzip \
    git


# Install Google Chrome
# RUN wget -q  https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_110.0.5481.96-1_amd64.deb && apt-get install ./google-chrome-stable_110.0.5481.77-1_amd64.deb -y &&  apt-mark hold google-chrome-stable # 禁止更新
RUN wget -q  https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_110.0.5481.77-1_amd64.deb && apt-get install ./google-chrome-stable_110.0.5481.77-1_amd64.deb -y &&  apt-mark hold google-chrome-stable # 禁止更新
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/110.0.5481.77/chromedriver_linux64.zip
RUN cd /tmp && unzip chromedriver.zip && mv chromedriver /usr/bin && chmod +x /usr/bin/chromedriver
# 下载最新的pip3
RUN apt-get install python3.10-distutils
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py
# 关联python3 到python3.10
#RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
#&& update-alternatives --install /usr/local/lib/python3.10/dist-packages/pip pip3 /usr/local/lib/python3.10/dist-packages/pip 1

# Install adb (Android Debug Bridge)
RUN apt-get install -y android-tools-adb tesseract-ocr usbutils
COPY chi_sim.traineddata  /usr/share/tesseract-ocr/4.00/tessdata/chi_sim.traineddata
# 使docker容器被手机信任
COPY adbkey /root/.android/adbkey
# Set the working directory
WORKDIR /app

# Copy your project files to the container
#COPY ["requirements.txt","./AppUIAutomator2Navigation","./context_sensitive_privacy_data_location","./Privacy-compliance-detection-2.1","run.py","get_urls.py","config.ini","/app/"]
COPY ["requirements_docker.txt","model","/app/"]
RUN pip install -r /app/requirements_docker.txt -i https://pypi.tuna.tsinghua.edu.cn/simple && pip install --upgrade requests urllib3 chardet -i https://pypi.tuna.tsinghua.edu.cn/simple && pip install hanlp[full] -U -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY . /app
# 在这一步首先执行adb connect 连接设备。需要在执行dockerfile之前，获取到手机的IP地址，并且断开主机上的adb-server
# 在主机执行adb shell ip -f inet addr show wlan0 | findstr inet，返回值是 inet 192.168.137.88/24 brd 192.168.137.255 scope global wlan0。需要通过正则表达式只获取192.168.137.88/24部分。
# 并在主机上执行 adb tcpip 12005,确定端口号，再在主机上执行adb connect IP:12005,再adb kill-server。
# 进入容器，并执行adb connect IP:12005
# 参考链接：https://wangqianhong.com/2021/01/docker%E5%AE%B9%E5%99%A8%E8%BF%9E%E6%8E%A5%E4%B8%BB%E6%9C%BA%E4%B8%8A%E7%9A%84android%E6%89%8B%E6%9C%BA/
# Set the entry point for the container
# 需要解决如何将手机的IP传给dockerfile或者在用户接触到bash之前执行
# 可以考虑把这个IP写入到容器的一个文件夹内，然后放在CMD['/bin/bash adb connect IP:12005','/bin/bash]
#RUN adb connect IP:12005
#COPY IP.txt /app/IP.txt
#CMD bash -c "IP=$(cat /app/IP.txt); adb connect $IP; \
#            if adb shell 'pidof frida-server' >/dev/null 2>&1; \
#            then \
#              adb shell 'su -c \"killall frida-server\"'; \
#            fi; \
#            adb shell 'su -c \"cd /data/local/tmp && ./frida-server &\"'; \
#            exit; /bin/bash"
CMD ["/bin/bash"]