import random
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'FangSong']
plt.rcParams['axes.unicode_minus'] = False


class Character:
    def __init__(self, is_up: bool, level: int, get_type: str = "gacha"):
        self.is_up = is_up
        self.level = level
        self.get_type = get_type


class Record:
    def __init__(self, banner_num: int, gacha_num: int, character: Character):
        self.banner_num = banner_num
        self.gacha_num = gacha_num
        self.character = character


class GachaSimulator:
    def __init__(self):
        self.guaranteed_count = 0
        self.claim_count = 0

        self.guaranteed_num = 160
        self.claim_num = 120
        self.p_five_star = 0.02
        self.p_up = 0.5

        self.history = []

    def banner_init(self):
        self.claim_count = 0

    def pull_one(self) -> Character:
        self.guaranteed_count += 1
        self.claim_count += 1

        if self.guaranteed_count >= self.guaranteed_num:
            self.guaranteed_count = 0
            return Character(is_up=True, level=5, get_type="guaranteed")

        if random.random() < self.p_five_star:
            if random.random() < self.p_up:
                self.guaranteed_count = 0
                return Character(is_up=True, level=5)
            else:
                return Character(is_up=False, level=5)
        else:
            return Character(is_up=False, level=4)

    def similator_banner(self, banner_num: int, max_pull_num=200):
        self.banner_init()
        for i in range(max_pull_num):
            character = self.pull_one()
            self.history.append(Record(banner_num, i + 1, character))

            if character.is_up:
                break
            if self.claim_count >= self.claim_num:
                self.history.append(Record(banner_num, 0, Character(is_up=True, level=5, get_type="claim")))
                break

    def similator_multiple_banner(self, max_banner_num=10):
        for i in range(max_banner_num):
            self.similator_banner(i + 1)


def analyze_history(sim: GachaSimulator):
    total_pulls = 0  # 总抽卡次数(不含claim)
    up_count = 0  # 正常抽+保底获得的UP数量
    claim_count = 0  # 免费领取的UP数量
    guaranteed_count = 0  # 保底获得的UP数量
    gacha_count = 0  # 正常抽中的UP数量
    up_pulls_list = []  # 每个UP的抽出次数(用于分布)
    banner_up_dict = {}  # 每期卡池对应的UP获取方式和抽卡数

    for record in sim.history:
        char = record.character
        if not char.is_up:
            continue  # 只关注UP角色

        if char.get_type == "claim":
            claim_count += 1
            continue  # 免费领取不计入抽卡行为

        # 以下是抽卡获得的UP(gacha 或 guaranteed)
        up_count += 1
        banner = record.banner_num
        pull_num = record.gacha_num
        total_pulls += pull_num

        banner_up_dict[banner] = (pull_num, char.get_type)
        up_pulls_list.append(pull_num)

        if char.get_type == "guaranteed":
            guaranteed_count += 1
        elif char.get_type == "gacha":
            gacha_count += 1

    banner_num = up_count + claim_count
    # 平均每UP花费抽卡数
    avg_pulls_per_up = total_pulls / banner_num

    # 输出统计
    print("\n" + "=" * 60)
    print("📊 抽卡模拟统计结果")
    print("=" * 60)
    print(
        f"模拟卡池数量: {banner_num}")
    print(f"通过抽卡获得的UP角色总数: {up_count}")
    print(f"通过120抽免费领取的UP角色数: {claim_count}")
    print(f"通过160抽保底强制获得的UP数: {guaranteed_count}")
    print(f"通过正常抽取获得的UP数: {gacha_count}")
    print(f"\n总抽卡次数(不含免费领取): {total_pulls}")
    print(f"平均每个UP花费抽卡数: {avg_pulls_per_up:.2f}")

    # UP抽出分布
    print(f"\n🎯 UP抽出分布(按抽卡数区间):")
    if up_pulls_list:
        bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
        hist, _ = np.histogram(up_pulls_list, bins=bins)
        for i, count in enumerate(hist):
            if count > 0:
                print(f"  {bins[i]}~{bins[i + 1]}抽: {count}个")

        # 绘制直方图(可选)
        plt.figure(figsize=(10, 6))
        plt.hist(up_pulls_list, bins=bins, edgecolor='black', alpha=0.7)
        plt.title("UP角色抽出分布_不含保底和免费领取")
        plt.xlabel("抽卡次数")
        plt.ylabel("获得次数")
        plt.xticks(bins)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.show()
    else:
        print("  暂无数据")

    # 额外：是否有人在120抽前没出UP却领了免费UP？
    banners_with_claim = set()
    banners_with_up = set()
    for record in sim.history:
        if record.character.is_up:
            if record.character.get_type == "claim":
                banners_with_claim.add(record.banner_num)
            else:
                banners_with_up.add(record.banner_num)

    claimed_without_up = banners_with_claim - banners_with_up
    if claimed_without_up:
        print(f"\n💡 注意：有 {len(claimed_without_up)} 期卡池是通过120抽免费领取UP，且未在抽取中获得UP(即靠保底或未出)")
        print(f"涉及卡池编号: {sorted(claimed_without_up)}")

    print("\n✅ 统计完成")


if __name__ == '__main__':
    sim = GachaSimulator()
    sim.similator_multiple_banner(1000)
    analyze_history(sim)
