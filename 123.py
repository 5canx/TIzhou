import os


def print_directory_structure(path, indent=0):
    # 遍历指定路径下的所有文件和子目录
    for item in os.listdir(path):
        item_path = os.path.join(path, item)

        # 判断是否是目录
        if os.path.isdir(item_path):
            print("  " * indent + f"- {item}/")  # 输出目录，末尾加斜杠表示目录
            # 递归调用，进入子目录
            print_directory_structure(item_path, indent + 1)
        else:
            # 输出文件
            print("  " * indent + f"- {item}")


# 获取当前工作目录
current_directory = os.getcwd()

# 打印当前目录及其子目录结构
print_directory_structure(current_directory)
