from data.file_infomations import FILE_INFOMATION as finfos
from utils.file_processing import fileProcessing

# 上传没有经过逆透视的产品编码表
for fileinfo in finfos:
    fileProcessing(fileinfo)

# 上传经过逆透视的迭代编码表
fileProcessing(finfos[0], True, "productid_iteration_unpivoted")

def main():
    print("hola")

if __name__ == "__main__":
    main()