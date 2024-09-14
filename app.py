"""
Author: black_samurai
Project: https://github.com/blacksamuraiiii/Llamacpp-MiniCPM3
Description: 基于Llamacpp+MiniCPM3创建网页demo

测试代码
#minicpm3 对话
./llama.cpp_chat/llama-cli -c 1024 -m ./models/MiniCPM-3/ggml-model-Q4_K_M.gguf -n 1024 --top-p 0.7 --temp 0.1 --prompt "你好"

#minicpmv2.6 图像识别
./llama.cpp_video/llama-minicpmv-cli -m ./models/MiniCPM-V-2_6/ggml-model-Q4_K_M.gguf --mmproj ./models/MiniCPM-V-2_6/mmproj-model-f16.gguf -c 4096 --temp 0.1 --top-p 0.8 --top-k 100 --repeat-penalty 1.05 --image ./models/MiniCPM-V-2_6/demo.jpg -p "请描述图片内容"

#minicpmv2.6 视频识别 特别慢,乱码
./llama.cpp_video/llama-minicpmv-cli -m ./models/MiniCPM-V-2_6/ggml-model-Q4_K_M.gguf --mmproj ./models/MiniCPM-V-2_6/mmproj-model-f16.gguf -c 8192 --temp 0.1 --top-p 0.8 --top-k 100 --repeat-penalty 1.05 --video ./models/MiniCPM-V-2_6/cat_compressed.mp4 -p "请告诉我视频内容"
"""


import os
import streamlit as st
import subprocess
import time
from datetime import datetime
from PIL import Image

# 设置页面标题和布局
st.set_page_config(page_title="MiniCPM 小钢炮", layout="wide")

# 设置标题并向上移动
st.markdown("<h1 style='text-align: center; margin-top: -50px;'>MiniCPM 小钢炮</h1>", unsafe_allow_html=True)

# 创建标签页
tabs = st.tabs(["文本对话", "图像识别", "视频识别"])

# 全局变量
global_params = {
    "model_path_text": "./models/MiniCPM-3/ggml-model-Q4_K_M.gguf", #默认对话模型
    "model_path_text2": "./models/Qwen2/qwen2-1_5b-instruct-q4_k_m.gguf",
    "model_path_image": "./models/MiniCPM-V-2_6/ggml-model-Q4_K_M.gguf",
    "mmproj_path": "./models/MiniCPM-V-2_6/mmproj-model-f16.gguf",
    "max_tokens": 1024,
    "context_length": 1024,
    "temperature": 0.1,
    "top_p": 0.7,
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
        global_params["model_path_text"] = st.selectbox("Model", [global_params["model_path_text"], global_params["model_path_text2"]], index=0, key="model_path_text")
        global_params["context_length"] = st.number_input("Context Length", value=global_params["context_length"], min_value=1, key="context_length_text")
        global_params["max_tokens"] = st.number_input("Max Tokens", value=global_params["max_tokens"], min_value=1, key="max_tokens_text")
        global_params["top_p"] = st.number_input("Top-p", value=global_params["top_p"], min_value=0.0, max_value=1.0, step=0.1, key="top_p_text")
        global_params["temperature"] = st.number_input("Temperature", value=global_params["temperature"], min_value=0.0, max_value=2.0, step=0.1, key="temperature_text")

    # 点击按钮触发对话
    if st.button("发送对话"):
        print('用户输入: ',user_input)
        # 开始计时
        start_time = time.time()

        # 显示加载状态
        with st.spinner("生成对话中..."):
            print('生成对话中')
            # 构建命令
            command = [
                "./llama.cpp_chat/llama-cli",
                "-c", str(global_params["context_length"]),
                "-m", global_params["model_path_text"],
                "-n", str(global_params["max_tokens"]),
                "--top-p", str(global_params["top_p"]),
                "--temp", str(global_params["temperature"]),
                "--prompt", f"<{user_input}>"
            ]

            # 运行命令
            result = subprocess.run(command, capture_output=True, text=True)      
            if result.returncode != 0:
                st.text_area("错误信息:", result.stderr)
                print("错误信息:", result.stderr)
            else:
                # 结束计时
                end_time = time.time()
                elapsed_time = end_time - start_time

                # 去除用户输入部分
                response = result.stdout.replace(f"<{user_input}>", "").strip()

                # 显示输出
                st.text_area("助手回复:", response)
                print('助手回复: ',response)

                # 显示最终耗时
                if elapsed_time >= 60:
                    minutes = int(elapsed_time // 60)
                    seconds = int(elapsed_time % 60)
                    st.write(f"对话生成耗时: {minutes}分{seconds}秒")
                    print(f"对话生成耗时: {minutes}分{seconds}秒")
                else:
                    st.write(f"对话生成耗时: {elapsed_time:.2f} 秒")
                    print(f"对话生成耗时: {elapsed_time:.2f} 秒")


# 图像识别部分
with tabs[1]:   
    # 用户上传图片
    uploaded_file = st.file_uploader("上传图片", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        print('用户上传图片')
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
            
            # 显示图片
            image = Image.open(image_path)
            st.image(image, caption="上传的图片", width=256)

            # 用户输入图像识别提示
            image_prompt = st.text_area("输入图像识别提示:", "请描述图片内容")
            print('用户输入: ',image_prompt)
                           

            # 高级选项
            show_advanced_options = st.checkbox("高级选项", key="advanced_options_image")

            if show_advanced_options:
                # 参数输入
                global_params["model_path_image"] = st.selectbox("Model", [global_params["model_path_image"]], index=0, key="model_path_image")
                global_params["mmproj_path"] = st.selectbox("MMProj", [global_params["mmproj_path"]], index=0, key="mmproj_path_image")
                global_params["context_length"] = st.number_input("Context Length", value=4096, min_value=1, key="context_length_image")
                global_params["temperature"] = st.number_input("Temperature", value=global_params["temperature"], min_value=0.0, max_value=2.0, step=0.1, key="temperature_image")
                global_params["top_p"] = st.number_input("Top-p", value=global_params["top_p"], min_value=0.0, max_value=1.0, step=0.1, key="top_p_image")
                global_params["top_k"] = st.number_input("Top-k", value=global_params["top_k"], min_value=1, step=1, key="top_k_image")
                global_params["repeat_penalty"] = st.number_input("Repeat Penalty", value=global_params["repeat_penalty"], min_value=1.0, max_value=10.0, step=0.1, key="repeat_penalty_image")

            # 点击按钮触发图像识别
            if st.button("发送图像识别"):
                print('开始图像识别')
                # 开始计时
                start_time = time.time()

                # 显示加载状态
                with st.spinner("图像识别中..."):
                    
                    # 压缩图片到256*256
                    image = image.resize((256, 256))
                    
                    # 检查图片模式并处理透明背景
                    if image.mode == "RGBA":
                        # 创建一个白色背景图像
                        background = Image.new("RGB", image.size, (255, 255, 255))  # 白色背景
                        # 将透明图像与背景图像合成
                        background.paste(image, mask=image.split()[3])  # 使用alpha通道作为mask
                        image = background
                       
                    #保存压缩后的照片  
                    compressed_image_path = f"./tmp/{timestamp}_compressed.jpg"
                    image.save(compressed_image_path)
                    
                    # 构建命令
                    command = [
                        "./llama.cpp_video/llama-minicpmv-cli",
                        "-m", global_params["model_path_image"],
                        "--mmproj", global_params["mmproj_path"],
                        "-c", str(global_params["context_length"]),
                        "--temp", str(global_params["temperature"]),
                        "--top-p", str(global_params["top_p"]),
                        "--top-k", str(global_params["top_k"]),
                        "--repeat-penalty", str(global_params["repeat_penalty"]),
                        "--image", compressed_image_path, 
                        "-p", image_prompt
                    ]

                    # 运行命令
                    result = subprocess.run(command, capture_output=True, text=True)
                    if result.returncode != 0:
                        st.text_area("错误信息:", result.stderr)
                        print("错误信息:", result.stderr) 
                    else:
                        # 结束计时
                        end_time = time.time()
                        elapsed_time = end_time - start_time

                        # 显示输出
                        st.text_area("图像识别结果:", result.stdout)
                        print('图像识别结果: ',result.stdout)

                        # 显示最终耗时
                        if elapsed_time >= 60:
                            minutes = int(elapsed_time // 60)
                            seconds = int(elapsed_time % 60)
                            st.write(f"图像识别耗时: {minutes}分{seconds}秒")
                            print(f"图像识别耗时: {minutes}分{seconds}秒")
                        else:
                            st.write(f"图像识别耗时: {elapsed_time:.2f} 秒")
                            print(f"图像识别耗时: {elapsed_time:.2f} 秒")
                            
                        #删除压缩后的图片
                        os.remove(compressed_image_path)
                            
        # 删除图片
        os.remove(image_path)
        
# 视频识别部分
with tabs[2]:   
    # 用户上传视频
    uploaded_file = st.file_uploader("上传视频", type=["mp4"])

    if uploaded_file is not None:
        print('用户上传视频')
        # 检查文件大小
        if uploaded_file.size > 50 * 1024 * 1024:
            st.error("视频大小不能超过50MB，请重新上传。")
        else:
            # 生成时间戳字符串
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            video_path = f"./tmp/{timestamp}.mp4"
           
            # 保存上传的视频到临时文件
            with open(video_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # 显示视频宽度20% 
            container, _, _ = st.columns([20, 40, 40])
            with container:
                st.video(video_path)
            
            # 用户输入视频识别提示
            video_prompt = st.text_area("输入视频识别提示:", "请描述视频内容")
            print('用户输入: ',video_prompt)
            

            # 高级选项
            show_advanced_options = st.checkbox("高级选项", key="advanced_options_video")

            if show_advanced_options:
                # 参数输入
                global_params["model_path_image"] = st.selectbox("Model", [global_params["model_path_image"]], index=0, key="model_path_video")
                global_params["mmproj_path"] = st.selectbox("MMProj", [global_params["mmproj_path"]], index=0, key="mmproj_path_video")
                global_params["context_length"] = st.number_input("Context Length", value=4096, min_value=1, key="context_length_video")
                global_params["temperature"] = st.number_input("Temperature", value=global_params["temperature"], min_value=0.0, max_value=2.0, step=0.1, key="temperature_video")
                global_params["top_p"] = st.number_input("Top-p", value=global_params["top_p"], min_value=0.0, max_value=1.0, step=0.1, key="top_p_video")
                global_params["top_k"] = st.number_input("Top-k", value=global_params["top_k"], min_value=1, step=1, key="top_k_video")
                global_params["repeat_penalty"] = st.number_input("Repeat Penalty", value=global_params["repeat_penalty"], min_value=1.0, max_value=10.0, step=0.1, key="repeat_penalty_video")

            # 点击按钮触发视频识别
            if st.button("发送视频识别"):
                # 开始计时
                start_time = time.time()

                # 显示加载状态
                with st.spinner("视频识别中..."): 
                    
                    # 压缩视频到分辨率448*448,24帧
                    compressed_video_path = f"./tmp/{timestamp}_compressed.mp4"
                    ffmpeg_command = [
                        "ffmpeg",
                        "-i", video_path,
                        "-vf", "scale=448:448,fps=24",   
                        "-c:a", "copy",
                        compressed_video_path
                    ]
                    print('开始压缩视频')
                    result = subprocess.run(ffmpeg_command, capture_output=True)
                    if result.returncode != 0:
                        st.text_area("错误信息:", result.stderr)
                        print("错误信息:", result.stderr) 
                    else:
                        # 发送给llama.cpp
                        command = [
                            "./llama.cpp_video/llama-minicpmv-cli",
                            "-m", global_params["model_path_image"],
                            "--mmproj", global_params["mmproj_path"],
                            "-c", str(global_params["context_length"]),
                            "--temp", str(global_params["temperature"]),
                            "--top-p", str(global_params["top_p"]),
                            "--top-k", str(global_params["top_k"]),
                            "--repeat-penalty", str(global_params["repeat_penalty"]),
                            "--video", video_path, 
                            "-p", video_prompt
                        ]

                        # 运行命令
                        print('开始视频识别')
                        result = subprocess.run(command, capture_output=True, text=True)
                        if result.returncode != 0:
                            st.text_area("错误信息:", result.stderr)
                            print("错误信息:", result.stderr) 
                        else:
                            # 结束计时
                            end_time = time.time()
                            elapsed_time = end_time - start_time

                            # 显示输出
                            st.text_area("视频识别结果:", result.stdout)
                            print('视频识别结果: ',result.stdout)

                            # 显示最终耗时
                            if elapsed_time >= 60:
                                minutes = int(elapsed_time // 60)
                                seconds = int(elapsed_time % 60)
                                st.write(f"视频识别耗时: {minutes}分{seconds}秒")
                                print(f"视频识别耗时: {minutes}分{seconds}秒")
                            else:
                                st.write(f"视频识别耗时: {elapsed_time:.2f} 秒")
                                print(f"视频识别耗时: {elapsed_time:.2f} 秒")
                            
                            #删除压缩后的视频
                            os.remove(compressed_video_path)
                            
        # 删除视频
        os.remove(video_path)
