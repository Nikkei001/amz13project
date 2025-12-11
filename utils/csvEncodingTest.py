import chardet

def detect_file_encoding(file_path):
    # 读取文件前 1000 字节（足够检测编码，避免读取大文件耗时）
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(1000))
    # 返回检测到的编码和置信度（confidence 越接近 1 越准确）
    return result['encoding']


