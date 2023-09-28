# Use the Ubuntu 18.04 base image
FROM ubuntu:18.04

# Copy the custom source.list to the container
COPY source.list /etc/apt/sources.list

# Update the package lists and install necessary dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    openjdk-8-jdk \
    wget \
    curl \
    unzip \
    git \
    pciutils

# Check if an NVIDIA GPU is present
RUN if lspci | grep -i nvidia; then \
        echo "NVIDIA GPU detected"; \
        export TORCH_CUDA_ARCH_LIST="6.0 6.1 7.0 7.5+PTX"; \
        export TORCH_NVCC_FLAGS="-Xfatbin -compress-all"; \
    else \
        echo "No NVIDIA GPU detected"; \
        export TORCH_CUDA_ARCH_LIST=""; \
        export TORCH_NVCC_FLAGS=""; \
    fi

# Install NVIDIA drivers and CUDA toolkit (if GPU is present)
RUN if [ "$TORCH_CUDA_ARCH_LIST" ]; then \
        wget -qO - https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub | apt-key add - \
        && echo "deb http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64 /" >> /etc/apt/sources.list.d/cuda.list \
        && apt-get update && apt-get install -y --no-install-recommends \
            cuda-cudart-11-4 \
            cuda-compat-11-4 \
            cuda-compiler-11-4 \
            cuda-nvcc-11-4 \
            cuda-libraries-11-4 \
            cuda-libraries-dev-11-4 \
            cuda-minimal-build-11-4 \
            cuda-cupti-11-4 \
            libcudnn8=8.2.4.15-1+cuda11.4 \
            libcudnn8-dev=8.2.4.15-1+cuda11.4 \
        && rm -rf /var/lib/apt/lists/*; \
    fi

# Install Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable

# Install PyTorch
RUN pip3 install torch

# Install adb (Android Debug Bridge)
RUN apt-get install -y android-tools-adb

# Set the default Python version
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

# Set the working directory
WORKDIR /app

# Copy your project files to the container
COPY ["./AppUIAutomator2Navigation/","./context_sensitive_privacy_data_location/","./Privacy-compliance-detection-2.1/","run.py","requirements.txt","get_urls.py","config.ini","/app/"]

# Set the entry point for the container
CMD ["/bin/bash"]