需要linux（wsl）或mac环境对llama.cpp进行编译

## 1、安装依赖包
```bash
sudo apt update
sudo apt install ffmpeg pkg-config build-essential make libavformat-dev libavcodec-dev libavutil-dev libswscale-dev-dev
```


## 2、创建项目并拉取llama.cpp分支
```bash
mkdir minicpm_webui
cd minicpm_webui
git clone -b minicpm3 https://github.com/OpenBMB/llama.cpp.git
```

## 3、编译llama.cpp
```bash
cd llama.cpp
sudo make -j8
```
编译完成之后应该多出一堆东西
![image](https://github.com/user-attachments/assets/87014caf-562b-4c53-a9e0-0612b8755a35)


## 4、获取量化后的模型文件gguf
可以去hf或者魔搭上下载现成的，也可以自己量化
```bash
cd ../
mkdir models
cd models
```
![image](https://github.com/user-attachments/assets/9f341881-beb4-4493-bc9a-8b188b0df886)

## 5、用python创建streamlit网页
代码详见 [app.py](https://github.com/blacksamuraiiii/Llamacpp-MiniCPM3/blob/main/app.py)

检查一下模型路径无误后运行即可启动网页demo
```bash
streamlit run app.py
```

## 6、网页效果展示
文本对话模式，模型为MiniCPM3，高级选项内可以调参
![image](https://github.com/user-attachments/assets/ab867096-0eab-44f7-bff6-1d5a9fc74cf5)
![image](https://github.com/user-attachments/assets/acb7ffc0-8c6e-4a61-a5b7-f884dbcb5290)
![image](https://github.com/user-attachments/assets/3153eb82-4226-4912-a6c9-dba68b2328d7)

图像识别模式，模型为MiniCPM-V2.6，同样可以调参
![image](https://github.com/user-attachments/assets/ee371e8b-0bb4-4fb8-abeb-68aa9e635ff8)
![image](https://github.com/user-attachments/assets/bfd96352-3a4a-46e6-a7de-a88da791bae3)













