import os
from volcenginesdkarkruntime import Ark
import base64
import pyperclip

def execute(image_path):
    def local_image_to_base64(image_path):
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
            # 获取图片格式（处理jpg/jpeg兼容）
            image_format = image_path.split(".")[-1].lower()
            if image_format == "jpg":
                image_format = "jpeg"
            # 生成Base64 Data URL（关键！）
            base64_url = f"data:image/{image_format};base64,{base64.b64encode(image_data).decode('utf-8')}"
            return base64_url
        except Exception as e:
            print(f"图片读取失败：{str(e)}")
            return None

    base64_image = local_image_to_base64(image_path)

    # 请确保您已将 API Key 存储在环境变量 ARK_API_KEY 中
    # 初始化Ark客户端，从环境变量中读取您的API Key
    client = Ark(
        # 此为默认路径，您可根据业务所在地域进行配置
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
        api_key=os.environ.get("ARK_API_KEY"),
    )

    
    completion = client.chat.completions.create(
    # 指定您创建的方舟推理接入点 ID，此处已帮您修改为您的推理接入点 ID
        model="ep-20251122205538-wsgd7",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": base64_image
                        },
                    },
                    {"type": "text", "text": "请识别图片中的纯数字或算式,如果是数字只需返回你识别到的四位数字即可,如果是算式请返回你的计算结果即可,不返回任何其他内容"},
                ],
            }
        ],
        reasoning_effort="medium",
        
        extra_headers={'x-is-encrypted': 'true'},
    )

    result = completion.choices[0].message.content
    pyperclip.copy(result)
    print("剪贴板内容：", result)
    

def main():
    print("This is a test of the OCR system.")

if __name__ == "__main__":
    main()