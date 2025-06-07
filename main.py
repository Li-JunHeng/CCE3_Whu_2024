# main.py

import random
import sys
from questions_data import QUESTIONS
from answer_key import ANSWER_KEY

def pick_random_passage():
    """从 QUESTIONS 中随机抽取一个 passage_key"""
    return random.choice(list(QUESTIONS.keys()))

def shuffle_options(options):
    """
    将 options（长度 4 的列表）随机打乱，
    并返回 (shuffled_options, mapping)：
      - shuffled_options: 打乱后的列表
      - mapping: 长度 4 的列表，mapping[i] = 原始 options 的索引
    """
    idxs = list(range(len(options)))
    random.shuffle(idxs)
    shuffled = [options[i] for i in idxs]
    return shuffled, idxs

def display_passage(passage_key):
    """
    打印出标题和该大题的所有小题（仅选项，听力题常见）。
    返回一个 list of mappings，便于后续判分：
      mappings[i] 对应第 i 题打乱前→后的索引映射列表
    """
    data = QUESTIONS[passage_key]
    title = data["title"]
    print("\n" + "=" * 60)
    print(f"【{title}】")
    print("-" * 60)

    mappings = []
    for q_idx, opts in enumerate(data["questions"], start=1):
        shuffled_opts, mapping = shuffle_options(opts)
        mappings.append(mapping)

        print(f"{q_idx}.")
        for letter, text in zip("ABCD", shuffled_opts):
            print(f"   {letter}. {text}")
        print()
    return mappings

def prompt_user(n):
    """
    提示用户输入 n 道题的答案，例如 'ABC' 或带空格 'A B C'。
    返回一个纯大写字母字符串，长度 = n。
    """
    while True:
        ans = input(f"请输入这 {n} 道题的答案（例如：{'A'*n}）：").upper().replace(" ", "")
        if ans == "Q":
            return None
        if len(ans) != n or any(c not in "ABCD" for c in ans):
            print(f"输入无效，请输入 {n} 个 A/B/C/D，或输入 Q 退出本题。")
        else:
            return ans

def grade(passage_key, user_ans, mappings):
    """
    根据 user_ans（长度 n 的字符串），mappings（n × 4 的映射），
    以及 ANSWER_KEY 中的原始正确答案列表，返回每题对错情况和总分。
    """
    correct_list = ANSWER_KEY.get(passage_key)
    if correct_list is None:
        print(f"⚠️ 警告：找不到 {passage_key} 的参考答案，请先在 answer_key.py 填入。")
        sys.exit(1)
    if len(correct_list) != len(user_ans):
        print(f"⚠️ 答案长度不匹配：key={passage_key}，参考答案 {len(correct_list)} 题，您输入 {len(user_ans)} 题。")
        sys.exit(1)

    results = []
    score = 0
    for i, ua in enumerate(user_ans):
        # 用户选择的新顺序下的索引
        picked_new_idx = ord(ua) - ord('A')
        # 对应原始 options 的索引
        picked_orig_idx = mappings[i][picked_new_idx]

        # 参考答案，原始顺序下的正确字母
        correct_letter = correct_list[i]
        correct_orig_idx = ord(correct_letter) - ord('A')

        is_correct = (picked_orig_idx == correct_orig_idx)
        if is_correct:
            score += 1

        # 在新顺序下找出正确项对应的新字母
        correct_new_idx = mappings[i].index(correct_orig_idx)
        correct_new_letter = chr(correct_new_idx + ord('A'))

        results.append({
            "q_no": i+1,
            "user": ua,
            "correct_orig": correct_letter,
            "correct_new": correct_new_letter,
            "is_correct": is_correct
        })
    return results, score

def display_results(results, score):
    """打印每题对错并显示本题总分。"""
    print("\n—— 判分结果 ——")
    for r in results:
        mark = "✅" if r["is_correct"] else "❌"
        if r["is_correct"]:
            print(f"{r['q_no']}. 您的答案 {r['user']} {mark}")
        else:
            print(f"{r['q_no']}. 您的答案 {r['user']} {mark} ；正确答案应为 {r['correct_new']}（原序号 {r['correct_orig']}）")
    print(f"本大题得分：{score}/{len(results)}")
    print("=" * 60)

def main():
    print("欢迎使用听力随机练习（输入 Q 随时退出本大题）\n")
    try:
        while True:
            key = pick_random_passage()
            mappings = display_passage(key)
            n = len(mappings)
            user_ans = prompt_user(n)
            if user_ans is None:
                print("跳过本大题，准备下一题…")
                continue

            results, score = grade(key, user_ans, mappings)
            display_results(results, score)

            cont = input("继续下一大题？（回车继续，输入 N 或 Q 退出）: ").strip().upper()
            if cont.startswith('N') or cont.startswith('Q'):
                break
    except KeyboardInterrupt:
        print("\n检测到中断，程序结束。")
    print("\n感谢练习，期待下次再见！")

if __name__ == "__main__":
    main()
