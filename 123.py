from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import hashlib
import re
from typing import List, Dict

# 连接 Elasticsearch
es = Elasticsearch("http://localhost:9200")
if es.ping():
    print("✅ 成功连接到 Elasticsearch")
else:
    print("❌ 无法连接到 Elasticsearch，请检查服务状态或地址")
    exit(1)

print("""开始处理数据""")
print("""—————————————————————————————————————————————""")
index_name = "questions"  # 替换为你的索引名


def clean_text(text: str) -> str:
    """
    清洗文本，去除格式差异，保留核心内容
    """
    if not text:
        return ""

    # 转换为小写（可选，根据需要决定是否大小写敏感）
    # text = text.lower()

    # 去除选项前缀（如"A、" "B." "C "等格式）
    text = re.sub(r'^[A-Za-z]\s*[、.]?\s*', '', text.strip())

    # 去除题干末尾的标点符号
    text = re.sub(r'[。；？！,.!?;]$', '', text)

    # 统一空格（多个空格合并为一个，去除首尾空格）
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def get_option_text(option: Dict) -> str:
    """提取选项的文本内容"""
    if not isinstance(option, dict):
        return ""

    # 优先获取text字段，没有则获取image字段
    text = option.get("text", "")
    if not text:
        text = option.get("image", "")

    return clean_text(text)


def generate_signature(question: Dict) -> str:
    """
    生成题目的签名，用于判断相似性
    针对题干相似、选项格式有差异但内容相同的情况进行优化
    """
    # 处理题干
    title = clean_text(question.get("title", ""))

    # 处理选项
    options = question.get("options", [])
    if not isinstance(options, list):
        options = []

    # 提取并清洗所有选项文本
    option_texts = []
    for opt in options:
        opt_text = get_option_text(opt)
        if opt_text:
            option_texts.append(opt_text)

    # 对选项进行排序，避免因选项顺序不同导致签名不同
    option_texts_sorted = sorted(option_texts)

    # 组合题干和选项生成签名字符串
    signature_str = title + "||".join(option_texts_sorted)

    # 生成哈希值作为最终签名
    return hashlib.md5(signature_str.encode('utf-8')).hexdigest()


def find_duplicate_questions() -> Dict[str, List[Dict]]:
    """查找所有相似的题目"""
    print("正在扫描所有题目...")
    results = scan(es, index=index_name, query={"query": {"match_all": {}}})

    signature_map = {}
    count = 0
    error_count = 0

    for doc in results:
        count += 1
        if count % 100 == 0:
            print(f"已处理 {count} 道题目，发现 {error_count} 个格式异常")

        try:
            doc_id = doc["_id"]
            source = doc["_source"]

            # 生成签名
            signature = generate_signature(source)

            # 将题目添加到对应的签名组
            if signature not in signature_map:
                signature_map[signature] = []
            signature_map[signature].append({
                "id": doc_id,
                "source": source,
                "title_preview": clean_text(source.get("title", ""))[:50]  # 用于预览
            })
        except Exception as e:
            error_count += 1
            print(f"处理题目时出错: {str(e)}")

    print(f"共处理 {count} 道题目，发现 {error_count} 个格式异常")

    # 过滤出有重复的组
    duplicate_groups = {
        sig: group for sig, group in signature_map.items()
        if len(group) > 1
    }

    print(f"发现 {len(duplicate_groups)} 组相似题目")
    return duplicate_groups


def handle_duplicates_with_option_diff(duplicate_groups: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
    """
    处理选项数量略有差异但核心内容相同的情况
    例如：前3个选项相同，第4个选项不同但不影响题目的情况
    """
    new_duplicate_groups = {}

    for sig, group in duplicate_groups.items():
        new_duplicate_groups[sig] = group

    # 查找选项数量差异但核心相似的题目
    all_questions = []
    for group in duplicate_groups.values():
        all_questions.extend(group)

    # 检查所有题目组合，寻找选项数量不同但核心相似的题目
    checked_pairs = set()
    for i in range(len(all_questions)):
        for j in range(i + 1, len(all_questions)):
            if (i, j) in checked_pairs:
                continue

            q1 = all_questions[i]
            q2 = all_questions[j]

            # 检查题干是否相同
            if q1["title_preview"] != q2["title_preview"]:
                continue

            # 提取选项
            opts1 = [get_option_text(opt) for opt in q1["source"].get("options", []) if get_option_text(opt)]
            opts2 = [get_option_text(opt) for opt in q2["source"].get("options", []) if get_option_text(opt)]

            # 找到共同的选项
            common_opts = set(opts1) & set(opts2)

            # 如果大部分选项相同，视为相似
            if len(common_opts) >= min(len(opts1), len(opts2)) * 0.8:
                # 将它们合并到同一组
                merged_group = [q1, q2]

                # 生成新的签名
                new_sig = f"merged_{q1['title_preview']}_{len(common_opts)}"
                new_sig = hashlib.md5(new_sig.encode()).hexdigest()

                # 添加到新的重复组
                if new_sig not in new_duplicate_groups:
                    new_duplicate_groups[new_sig] = []

                # 确保不添加重复项
                for item in merged_group:
                    if not any(existing["id"] == item["id"] for existing in new_duplicate_groups[new_sig]):
                        new_duplicate_groups[new_sig].append(item)

                checked_pairs.add((i, j))

    # 过滤出只有一个题目的组
    new_duplicate_groups = {
        sig: group for sig, group in new_duplicate_groups.items()
        if len(group) > 1
    }

    return new_duplicate_groups


def delete_duplicates(duplicate_groups: Dict[str, List[Dict]], keep_first: bool = True) -> None:
    """删除重复题目，保留每组中的第一个题目"""
    total_duplicates = sum(len(group) - 1 for group in duplicate_groups.values())
    print(f"总共发现 {total_duplicates} 道重复题目")

    # 显示重复组详情
    for i, (sig, group) in enumerate(duplicate_groups.items(), 1):
        print(f"\n组 {i}:")
        print(f"  题干预览: {group[0]['title_preview']}...")
        print(f"  包含 {len(group)} 道题目，ID: {[q['id'] for q in group]}")

    # 确认删除
    confirm = input("\n是否确认删除所有重复题目？(y/N): ")
    if confirm.lower() != 'y':
        print("已取消删除操作")
        return

    total_deleted = 0

    for group in duplicate_groups.values():
        # 保留第一个，删除其余
        to_keep = group[0]
        to_delete = group[1:]

        print(f"\n保留题目 ID: {to_keep['id']}")

        for doc in to_delete:
            try:
                es.delete(index=index_name, id=doc["id"])
                total_deleted += 1
                print(f"已删除 ID: {doc['id']}")
            except Exception as e:
                print(f"删除 ID: {doc['id']} 失败: {str(e)}")

    print(f"\n处理完成，共删除 {total_deleted} 道重复题目")


if __name__ == "__main__":
    # 查找重复题目
    duplicate_groups = find_duplicate_questions()

    # 处理选项数量略有差异的相似题目
    duplicate_groups = handle_duplicates_with_option_diff(duplicate_groups)

    if not duplicate_groups:
        print("没有发现相似题目，无需删除")
        exit(0)

    # 删除重复题目
    delete_duplicates(duplicate_groups)
