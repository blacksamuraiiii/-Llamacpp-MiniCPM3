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
```bash
cd ../
mkdir models
cd models
```
![image](https://github.com/user-attachments/assets/9f341881-beb4-4493-bc9a-8b188b0df886)

##5、用python创建streamlit网页
自己搞定python环境
```python
import streamlit as st
from PIL import Image
from datetime import datetime
import time
import subprocess

# 设置页面标题和布局
st.set_page_config(page_title="MiniCPM 小钢炮", layout="wide")

# 设置标题并向上移动
st.markdown("<h1 style='text-align: center; margin-top: -50px;'>MiniCPM 小钢炮</h1>", unsafe_allow_html=True)

# 创建标签页
tabs = st.tabs(["文本对话", "图像识别"])

# 全局变量
global_params = {
    "context_length": 1024,
    "max_tokens": 1024,
    "top_p": 0.7,
    "temperature": 0.1,
    "model_path_text": "./models/MiniCPM-3/ggml-model-Q4_K_M.gguf",
    "model_path_image": "./models/MiniCPM-V-2_6/ggml-model-Q4_K_M.gguf",
    "mmproj_path": "./models/MiniCPM-V-2_6/mmproj-model-f16.gguf",
    "top_k": 100,
    "repeat_penalty": 1.05
}

# 对话部分
with tabs[0]:
    
    # 用户输入对话
    user_input = st.text_area("输入你的对话:", "你好,介绍一下你自己")

    # 高级选项
    show_advanced_options = st.checkbox("高级选项", key="advanced_options_text")

    if show_advanced_options:
        # 参数输入
        global_params["context_length"] = st.number_input("Context Length", value=global_params["context_length"], min_value=1, key="context_length_text")
        global_params["model_path_text"] = st.selectbox("Model", [global_params["model_path_text"]], index=0, key="model_path_text")
        global_params["max_tokens"] = st.number_input("Max Tokens", value=global_params["max_tokens"], min_value=1, key="max_tokens_text")
        global_params["top_p"] = st.number_input("Top-p", value=global_params["top_p"], min_value=0.0, max_value=1.0, key="top_p_text")
        global_params["temperature"] = st.number_input("Temperature", value=global_params["temperature"], min_value=0.0, max_value=2.0, key="temperature_text")

    # 点击按钮触发对话
    if st.button("发送对话"):
        # 开始计时
        start_time = time.time()

        # 显示加载状态
        with st.spinner("生成对话中..."):
            # 构建命令
            command = [
                "./llama.cpp/llama-cli",
                "-c", str(global_params["context_length"]),
                "-m", global_params["model_path_text"],
                "-n", str(global_params["max_tokens"]),
                "--top-p", str(global_params["top_p"]),
                "--temp", str(global_params["temperature"]),
                "--prompt", f"<{user_input}>"
            ]

            # 运行命令
            result = subprocess.run(command, capture_output=True, text=True)

            # 结束计时
            end_time = time.time()
            elapsed_time = end_time - start_time

            # 去除用户输入部分
            response = result.stdout.replace(f"<{user_input}>", "").strip()

            # 显示输出
            st.text_area("助手回复:", response)

            # 显示最终耗时
            if elapsed_time >= 60:
                minutes = int(elapsed_time // 60)
                seconds = int(elapsed_time % 60)
                st.write(f"对话生成耗时: {minutes}分{seconds}秒")
            else:
                st.write(f"对话生成耗时: {elapsed_time:.2f} 秒")


# 图像识别部分
with tabs[1]:
    
    # 用户上传图片
    uploaded_file = st.file_uploader("上传图片", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # 检查文件大小
        if uploaded_file.size > 50 * 1024 * 1024:
            st.error("图片大小不能超过50MB，请重新上传。")
        else:
            # 生成时间戳字符串
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            image_path = f"./tmp/{timestamp}.jpg"

            # 保存上传的图片到临时文件
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            #显示图片
            image = Image.open(image_path)
            st.image(image, caption="上传的图片", width=256)
            
            # 压缩图片到256*256
            image = image.resize((256, 256))
            
            # 检查图片模式并处理透明背景
            if image.mode == "RGBA":
                # 创建一个白色背景图像
                background = Image.new("RGB", image.size, (255, 255, 255))  # 白色背景
                # 将透明图像与背景图像合成
                background.paste(image, mask=image.split()[3])  # 使用alpha通道作为mask
                image = background
            
            # 保存压缩后的图片
            image.save(image_path)

            # 用户输入图像识别提示
            image_prompt = st.text_area("输入图像识别提示:", "请描述图片内容")

            # 高级选项
            show_advanced_options = st.checkbox("高级选项", key="advanced_options_image")

            if show_advanced_options:
                # 参数输入
                global_params["model_path_image"] = st.selectbox("Model", [global_params["model_path_image"]], index=0, key="model_path_image")
                global_params["mmproj_path"] = st.selectbox("MMProj", [global_params["mmproj_path"]], index=0, key="mmproj_path_image")
                global_params["context_length"] = st.number_input("Context Length", value=4096, min_value=1, key="context_length_image")
                global_params["temperature"] = st.number_input("Temperature", value=global_params["temperature"], min_value=0.0, max_value=2.0, key="temperature_image")
                global_params["top_p"] = st.number_input("Top-p", value=global_params["top_p"], min_value=0.0, max_value=1.0, key="top_p_image")
                global_params["top_k"] = st.number_input("Top-k", value=global_params["top_k"], min_value=1, key="top_k_image")
                global_params["repeat_penalty"] = st.number_input("Repeat Penalty", value=global_params["repeat_penalty"], min_value=1.0, key="repeat_penalty_image")

            # 点击按钮触发图像识别
            if st.button("发送图像识别"):
                # 开始计时
                start_time = time.time()

                # 显示加载状态
                with st.spinner("图像识别中..."):
                    # 构建命令
                    command = [
                        "./llama.cpp/llama-minicpmv-cli",
                        "-m", global_params["model_path_image"],
                        "--mmproj", global_params["mmproj_path"],
                        "-c", str(global_params["context_length"]),
                        "--temp", str(global_params["temperature"]),
                        "--top-p", str(global_params["top_p"]),
                        "--top-k", str(global_params["top_k"]),
                        "--repeat-penalty", str(global_params["repeat_penalty"]),
                        "--image", image_path,
                        "-p", image_prompt
                    ]

                    # 运行命令
                    result = subprocess.run(command, capture_output=True, text=True)

                    # 结束计时
                    end_time = time.time()
                    elapsed_time = end_time - start_time

                    # 显示输出
                    st.text_area("图像识别结果:", result.stdout)

                    # 显示最终耗时
                    if elapsed_time >= 60:
                        minutes = int(elapsed_time // 60)
                        seconds = int(elapsed_time % 60)
                        st.write(f"图像识别耗时: {minutes}分{seconds}秒")
                    else:
                        st.write(f"图像识别耗时: {elapsed_time:.2f} 秒")
```


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













