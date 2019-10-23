import GeneticAlgorithm as ga
import random

SCHEDULE = [5, 3, 4, 2, 3, 2]
GENOM_LENGTH = sum(SCHEDULE)
# {教科: [見込み工数, 期限, 重要度]}
tasks = {"Japanese": [4, 3, 1], "Math": [5, 4, 2], "English": [6, 5, 3]}
MAX_GENOM_NUM = 100
SELECT_GENOM = 20
PROBABILITY_MUTATION = 0.03
PROBABILITY_GE_MUTATION = 0.1
MAX_GENERATION = 200

def create_genom(length, tasks):
    """
    引数で指定された桁のランダムな遺伝子情報を生成し，格納したgenomClassで返す
    :param length 使用可能な工数
    :param tasks tasksの辞書
    :return schedule_genom
    """
    task_plan = [random.randint(0, len(tasks)) for _ in range(GENOM_LENGTH)]
    return ga.schedule_genom(task_plan, 0)


def penalize(ga, schedule, tasks):
    """
    評価関数
    :param ga:genomClass
    :param schedule: スケジュールのlist
    :return penalty
    """
    penalty = 0
    plan = ga.GetPlan()
    last_hour_of_the_day = []
    # 〆切超過penalty rate:100 * 重要度
    # 残りタスクpenalty rate:80
    # タスク超過penalty rate:10
    for i, key in enumerate(tasks):
        task = tasks[key]
        i += 1  # 0はFreeに充てるので一つずらす
        remaining_hour = plan.count(i) - task[0]
        if remaining_hour >= 0:
            penalty += 80 * remaining_hour
        else:
            penalty += -10 * remaining_hour
        dead_line_over_hours = plan[:sum(schedule[:task[1]])].count(i) - task[0]
        if dead_line_over_hours > 0:
            penalty += 100 * task[2] * dead_line_over_hours
    # 同じタスクが続くpenalty rate:1
    for i in range(len(plan)-1):
        if plan[i] == plan[i+1]:
            penalty += 1
    return penalty


def select(genoms, elite_length):
    """
    選択関数
    :param genoms: genomClassのリスト
    :param elite_length: 選択するエリートの数
    :return 選択した数のgenomClassのリスト
    """
    sort_result = sorted(genoms, reverse=False, key=lambda u: u.penalty)
    return sort_result[:elite_length]
 

def crossover(ga_fst, ga_snd):
    """
    交叉関数
    :param ga_fst: 一つめの個体
    :param ga_second: 二つ目の個体
    :return progenies: 2つの子孫のリスト
    """
    tmp = random.randint(0, GENOM_LENGTH)
    cross_point = (tmp, random.randint(tmp,GENOM_LENGTH))
    
    fst_genom = ga_fst.GetPlan()
    snd_genom = ga_snd.GetPlan()

    progeny_fst = fst_genom[:cross_point[0]] + snd_genom[cross_point[0]:cross_point[1]] + fst_genom[cross_point[1]:]
    progeny_snd = snd_genom[:cross_point[0]] + snd_genom[cross_point[0]:cross_point[1]] + snd_genom[cross_point[1]:]

    return [ga.schedule_genom(progeny_fst, 0), ga.schedule_genom(progeny_snd, 0)]


def next_generation_create(genoms, ga_elite, ga_progeny):
    """
    世代交代処理
    : param genoms: 現行遺伝子集団
    : param ga_elite: 現行エリート集団
    : param ga_progeny: 現行子孫集団
    : return next_genoms: 次世代遺伝子集団
    """
    next_genoms = sorted(genoms, reverse=False, key=lambda u: u.penalty)
    next_genoms = next_genoms[0: MAX_GENOM_NUM-len(ga_elite)-len(ga_progeny)]

    next_genoms.extend(ga_elite)
    next_genoms.extend(ga_progeny)
    return next_genoms


def mutation(genoms, tasks, probability_mutation, probability_ge_mutation):
    """
    突然変異関数
    : param genoms：対象GenomClassのリスト
    : param tasks : taskのリスト
    : param probability_mutation: 個体に対する突然変異確率 range(0,1)
    : param probability_ge_mutation: 遺伝子情報の変異確率 range(0,1)
    : return ga: 突然変異処理後のGenomClass
    """
    mutated_genoms = []
    for ga_ in genoms[1:]:  # 一番いい個体は残す
        if probability_mutation > random.random():
            genom = []
            for i_ in ga_.GetPlan():
                if probability_ge_mutation > random.random():
                    genom.append(random.randint(0, len(tasks)))
                else:
                    genom.append(i_)
            ga_.SetPlan(genom)
            mutated_genoms.append(ga_)
        else:
            mutated_genoms.append(ga_)
    return mutated_genoms

if __name__ == '__main__':
    # 第一世代の生成
    current_generation_genoms = []
    for _ in range(MAX_GENOM_NUM):
        current_generation_genoms.append(create_genom(GENOM_LENGTH, tasks))

    for count_ in range(1, MAX_GENERATION + 1):
        # 評価
        for ga_ in current_generation_genoms:
            ga_.SetPenalty(penalize(ga_, SCHEDULE, tasks))
        # エリート集団の生成
        elite_genoms = select(current_generation_genoms, SELECT_GENOM)
        # 子孫の生成
        progeny_genoms = []
        for i in range(SELECT_GENOM):
            progeny_genoms.extend(crossover(elite_genoms[i-1], elite_genoms[i]))
        next_generation_genoms = next_generation_create(current_generation_genoms,
                                                        elite_genoms, progeny_genoms)
        # 突然変異
        next_generation_genoms = mutation(next_generation_genoms, tasks,
                                          PROBABILITY_MUTATION, PROBABILITY_GE_MUTATION)
        # 評価
        fits = [ga_.GetPenalty() for ga_ in current_generation_genoms]

        print("-------第{}世代-------".format(count_))
        print("Min:{}".format(min(fits)))
        print("Max:{}".format(max(fits)))
        print("Avg:{}".format(sum(fits)/MAX_GENOM_NUM))

        current_generation_genoms = next_generation_genoms

    print("最も優れた個体")
    keys = ["Free"] + list(tasks.keys())
    print([keys[i] for i in elite_genoms[0].GetPlan()])