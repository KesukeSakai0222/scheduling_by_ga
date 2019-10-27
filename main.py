import GeneticAlgorithm as ga
import random

SCHEDULE = [5, 3, 4, 2, 3, 2]
GENOM_LENGTH = sum(SCHEDULE)
# {教科: [見込み工数, 期限, 重要度]}
TASKS = {"Japanese": [4, 3, 1], "Math": [5, 4, 2], "English": [6, 5, 3]}
MAX_GENOM_NUM = 1000
PROBABILITY_MUTATION = 0.01
PROBABILITY_GE_MUTATION = 0.1
MAX_GENERATION = 100

def create_genom(length):
    """
    引数で指定された桁のランダムな遺伝子情報を生成し，格納したgenomClassで返す
    :param length 使用可能な工数
    :return schedule_genom
    """
    task_plan = [random.randint(0, len(TASKS)) for _ in range(GENOM_LENGTH)]
    return ga.schedule_genom(task_plan, penalize(task_plan))


def penalize(plan):
    """
    評価関数
    :param plan:genomClassのスケジュールリスト
    :return penalty
    """
    penalty = 0
    last_hour_of_the_day = []
    # 〆切超過penalty rate:1000 * 重要度
    # タスク超過penalty rate:10000
    for i, key in enumerate(TASKS):
        task = TASKS[key]
        i += 1  # 0はFreeに充てるので一つずらす
        remaining_hour = task[0] - plan.count(i)
        if remaining_hour < 0:
            penalty += -10000 * remaining_hour
        deadline_over_hours = task[0] - plan[:sum(SCHEDULE[:task[1]])].count(i)
        if deadline_over_hours > 0:
            penalty += 1000 * task[2] * deadline_over_hours
    # 同じタスクが続くpenalty rate:1
    tmp = -1
    sep_day = []
    for hour_ in SCHEDULE:
        tmp += hour_
        sep_day.append(tmp)
    for i in range(len(plan)-1):
        if plan[i] == plan[i+1] and i not in sep_day and plan[i] != 0:
            penalty += 1
    return penalty


def crossover(ga_fst, ga_snd):
    """
    交叉関数
    :param ga_fst: 一つめの個体
    :param ga_second: 二つ目の個体
    :return progenies: 2つの子孫のリスト
    """
    tmp = random.randint(0, GENOM_LENGTH)
    cross_point = (tmp, random.randint(tmp,GENOM_LENGTH))
    
    fst_plan = ga_fst.GetPlan()
    snd_plan = ga_snd.GetPlan()

    progeny_fst = []
    progeny_snd = []
    for fst_ge, snd_ge in zip(fst_plan, snd_plan):
        if 0.5 >= random.random():
            progeny_fst.append(fst_ge)
            progeny_snd.append(snd_ge)
        else:
            progeny_fst.append(snd_ge)
            progeny_snd.append(fst_ge)

    return [ga.schedule_genom(progeny_fst, penalize(progeny_fst)),
            ga.schedule_genom(progeny_snd, penalize(progeny_snd))]


def next_generation_create(genoms):
    """
    世代交代処理
    : param genoms: 現行遺伝子集団
    : return next_genoms: 次世代遺伝子集団
    """
    next_genoms = []
    random.shuffle(genoms)
    for i in range(int(MAX_GENOM_NUM/2)):
        fa = genoms.pop()
        ma = genoms.pop()
        family = crossover(fa, ma)
        family.extend((fa, ma))
        family = sorted(family, reverse=False, key=lambda u: u.penalty)
        next_genoms.extend(family[:2])
    return next_genoms


def mutation(genoms):
    """
    突然変異関数
    : param genoms：対象GenomClassのリスト
    : return ga: 突然変異処理後のGenomClass
    """
    mutated_genoms = []
    for ga_ in genoms:
        if PROBABILITY_MUTATION > random.random():
            genom = []
            for i_ in ga_.GetPlan():
                if PROBABILITY_GE_MUTATION > random.random():
                    genom.append(random.randint(0, len(TASKS)))
                else:
                    genom.append(i_)
            ga_.SetPlan(genom)
            ga_.SetPenalty(penalize(ga_.GetPlan()))
            mutated_genoms.append(ga_)
        else:
            mutated_genoms.append(ga_)
    return mutated_genoms


if __name__ == '__main__':
    # susus第一世代の生成
    current_generation_genoms = []
    for _ in range(MAX_GENOM_NUM):
        current_generation_genoms.append(create_genom(GENOM_LENGTH))

    for count_ in range(1, MAX_GENERATION + 1):
        # 次世代の作成
        next_generation_genoms = next_generation_create(current_generation_genoms.copy())
        # 突然変異
        next_generation_genoms = mutation(next_generation_genoms)
        # 評価
        fits = [ga_.GetPenalty() for ga_ in current_generation_genoms]

        print("-------第{}世代-------".format(count_))
        print("Min:{}".format(min(fits)))
        print("Max:{}".format(max(fits)))
        print("Avg:{}".format(sum(fits)/MAX_GENOM_NUM))

        current_generation_genoms = next_generation_genoms

    next_generation_genoms = sorted(next_generation_genoms, reverse=False, key=lambda u: u.penalty)
    # print("最も優れた個体")
    for i in range(fits.count(0)):
        keys = ["Free"] + list(TASKS.keys())
        prev = 0
        next = 0
        best_ = [keys[i] for i in next_generation_genoms[i].GetPlan()]
        transformed_plan = []
        for hour_ in SCHEDULE:
            next += hour_
            transformed_plan.append(best_[prev:next])
            prev = next
        print(transformed_plan)
