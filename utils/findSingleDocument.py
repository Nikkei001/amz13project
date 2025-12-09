from pathlib import Path 

def findSingleDocument(folderPath, keyword, caseSensitive=False):

    pattern = f'*{keyword}*'
    targetFile = [f for f in Path(folderPath).glob(pattern, case_sensitive = caseSensitive) if f.is_file()]

    if len(targetFile) == 0:
        raise FileNotFoundError(f"未找到含'{keyword}'的文件")
    elif len(targetFile) > 1:
        raise ValueError(f"找到多个文件：{[f.name for f in targetFile]}")

    return targetFile[0]

test = findSingleDocument(r'C:\Users\Administrator\OneDrive\文档\产品库存数量表\产品库存数量表原表\产品库存数量表_原表\原表', 'copy')
print(test)

if __name__ == '__main__':
    print("ha hahaha hahahaha hahahahahahaha")
