# main.py

import random
import sys
import time

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
    打印出标题和该大题的所有小题（仅选项）。
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
    返回一个纯大写字母字符串，长度 = n，或 None（用户输入 Q 跳过本大题）。
    """
    while True:
        ans = input(f"请输入这 {n} 道题的答案（例如：{'A'*n}，输入 Q 跳过）: ").strip().upper().replace(" ", "")
        if ans == "Q":
            return None
        if len(ans) != n or any(c not in "ABCD" for c in ans):
            print(f"输入无效，请输入 {n} 个 A/B/C/D，或输入 Q 跳过本大题。")
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
        print(f"⚠️ 答案长度不匹配：key={passage_key}，参考 {len(correct_list)} 题，您输入 {len(user_ans)} 题。")
        sys.exit(1)

    results = []
    score = 0
    for i, ua in enumerate(user_ans):
        picked_new_idx = ord(ua) - ord('A')
        picked_orig_idx = mappings[i][picked_new_idx]

        correct_letter = correct_list[i]
        correct_orig_idx = ord(correct_letter) - ord('A')

        is_correct = (picked_orig_idx == correct_orig_idx)
        if is_correct:
            score += 1

        # 在新顺序下找到正确项的新字母
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
            print(f"{r['q_no']}. 您的答案 {r['user']} {mark}；正确应为 {r['correct_new']}（原序 {r['correct_orig']}）")
    print(f"本大题得分：{score}/{len(results)}")
    print("=" * 60)

def main():
    print("欢迎使用听力随机练习！\n")
    all_scores, all_results = [], 0

    # —— 模式选择 —— #
    mode = None
    while mode not in ('1','2'):
        print("请选择出题模式：")
        print("  1 - 随机可重复（默认随机抽题，可能重复）")
        print("  2 - 随机不重复（直到用完全部题后才重置）")
        mode = input("输入 1 或 2：").strip()
    no_repeat = (mode == '2')

    # 如果不重复模式，预先打乱一轮题库
    if no_repeat:
        pool = list(QUESTIONS.keys())
        random.shuffle(pool)
    else:
        pool = None

    try:
        while True:
            # 根据模式获取下一个 passage_key
            if no_repeat:
                if not pool:
                    print("🎉 全部 24 道大题已练完，当前轮次结束，重新随机一轮。")
                    print("-------------总信息-------------")
                    print(f"\n\n\n\n🎉🎉🎉总成绩：{sum(all_scores)} / {all_results}")
                    print(f"\🎉🎉🎉正确率：{sum(all_scores) / all_results * 100:.2f}%\n\n\n\n")
                    print("-------------总信息-------------")
                    pool = list(QUESTIONS.keys())
                    random.shuffle(pool)
                passage_key = pool.pop()
            else:
                passage_key = pick_random_passage()

            mappings = display_passage(passage_key)
            user_ans = prompt_user(len(mappings))
            if user_ans is None:
                print("已跳过本大题，进入下一题…")
                continue

            results, score = grade(passage_key, user_ans, mappings)
            all_scores.append(score)
            all_results += len(results)
            display_results(results, score)

            cont = input("继续下一大题？（回车继续，N 或 Q 退出）: ").strip().upper()
            if cont.startswith('N') or cont.startswith('Q'):
                break

    except KeyboardInterrupt:
        print("\n检测到中断，程序结束。")
    print("\n感谢练习，期待下次再见！")

if __name__ == "__main__":
    random.seed(time.time())
    main()