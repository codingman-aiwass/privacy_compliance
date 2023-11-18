# Use the Ubuntu 20.04 base image
#FROM ubuntu:20.04
FROM nullptr001/ubuntu_miniconda_dependencies
# Copy the custom source.list to the container
#COPY sourcelist.txt /etc/apt/sources.list
# 修改时区
#ENV TZ=Asia/Shanghai \
#    DEBIAN_FRONTEND=noninteractive

#RUN apt update \
#    && apt install -y tzdata \
#    && ln -fs /usr/share/zoneinfo/${TZ} /etc/localtime \
#    && echo ${TZ} > /etc/timezone \
#    && dpkg-reconfigure --frontend noninteractive tzdata \
#    && rm -rf /var/lib/apt/lists/*

# Update the package lists and install necessary dependencies
# RUN apt-get update && apt-get install software-properties-common -y && add-apt-repository ppa:deadsnakes/ppa # 添加python源，暂时弃用
#RUN apt-get update && apt-get install -y \
#    openjdk-8-jdk \
#    wget \
#    curl \
#    unzip \
#    git \
#    android-tools-adb \
#    tesseract-ocr \
#    usbutils \
#    apt-get purge -y --auto-remove $buildDeps

# Install Google Chrome
# 安装117.0.5938.132版本的Google chrome
#RUN wget -q  https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_117.0.5938.132-1_amd64.deb && apt-get install ./google-chrome-stable_117.0.5938.132-1_amd64.deb -y &&  apt-mark hold google-chrome-stable
#RUN wget -O /tmp/chromedriver.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/117.0.5938.132/linux64/chromedriver-linux64.zip
#RUN cd /tmp && unzip chromedriver.zip && mv chromedriver-linux64/chromedriver /usr/bin && chmod +x /usr/bin/chromedriver
# 安装110.0.5481.77版本的Google chrome,弃用
# RUN wget -q  https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_110.0.5481.96-1_amd64.deb && apt-get install ./google-chrome-stable_110.0.5481.77-1_amd64.deb -y &&  apt-mark hold google-chrome-stable # 禁止更新
#RUN wget -q  https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_110.0.5481.77-1_amd64.deb && apt-get install ./google-chrome-stable_110.0.5481.77-1_amd64.deb -y &&  apt-mark hold google-chrome-stable # 禁止更新
#RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/110.0.5481.77/chromedriver_linux64.zip
#RUN cd /tmp && unzip chromedriver.zip && mv chromedriver /usr/bin && chmod +x /usr/bin/chromedriver
# 下载最新的pip3，弃用
# RUN apt-get install python3.10-distutils
# RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
# RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py
# 关联python3 到python3.10，弃用
#RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
#&& update-alternatives --install /usr/local/lib/python3.10/dist-packages/pip pip3 /usr/local/lib/python3.10/dist-packages/pip 1

# Set the working directory
WORKDIR /app

# Copy your project files to the container
#COPY ["requirements.txt","./AppUIAutomator2Navigation","./context_sensitive_privacy_data_location","./Privacy-compliance-detection-2.1","run.py","get_urls.py","config.ini","/app/"]
COPY ["requirements_docker.txt","model","/app/"]
SHELL ["/bin/bash", "-c"]
RUN /root/miniconda3/envs/py380/bin/pip3 install -r /app/requirements_docker.txt -i https://pypi.tuna.tsinghua.edu.cn/simple && /root/miniconda3/envs/py380/bin/pip3 install --upgrade requests urllib3 chardet -i https://pypi.tuna.tsinghua.edu.cn/simple && /root/miniconda3/envs/py380/bin/pip3 install hanlp[full] -U -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY ["requirements_yolov5.txt","/app/"]
RUN /root/miniconda3/envs/py380/bin/pip3 install -r /app/requirements_yolov5.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY chi_sim.traineddata  /usr/share/tesseract-ocr/4.00/tessdata/chi_sim.traineddata
# 使docker容器被手机信任
COPY adbkey /root/.android/adbkey
COPY adbkey.pub /root/.android/adbkey.pub
COPY . /app
# 在这一步首先执行adb connect 连接设备。需要在执行dockerfile之前，获取到手机的IP地址，并且断开主机上的adb-server
# 在主机执行adb shell ip -f inet addr show wlan0 | findstr inet，返回值是 inet 192.168.137.88/24 brd 192.168.137.255 scope global wlan0。需要通过正则表达式只获取192.168.137.88/24部分。
# 并在主机上执行 adb tcpip 12005,确定端口号，再在主机上执行adb connect IP:12005,再adb kill-server。
# 进入容器，并执行adb connect IP:12005
# 参考链接：https://wangqianhong.com/2021/01/docker%E5%AE%B9%E5%99%A8%E8%BF%9E%E6%8E%A5%E4%B8%BB%E6%9C%BA%E4%B8%8A%E7%9A%84android%E6%89%8B%E6%9C%BA/
CMD ["/bin/bash"]