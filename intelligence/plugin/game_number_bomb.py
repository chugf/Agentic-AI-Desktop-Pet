import json
import random

remain_times = 4
number_bomb = None


def game_number_bomb(user_input_number: int | None = None):
    """
    当你需要玩数字炸弹游戏时非常有用

    :Author: Made by 0xff
    """
    global remain_times, number_bomb
    if user_input_number is None:
        number_bomb = random.randint(0, 100)
        return json.dumps(
            {'error': None,
             'number_bomb': number_bomb,
             'message': '（初始化，无信息）',
             'remain_times': remain_times,
             'operate': '你需要问用户输入一个即不大于100的数字也不小于0的数字'
             })
    else:
        if user_input_number > 100 or user_input_number < 0:
            return json.dumps(
                {'error': '数字无效',
                 'message': '数字过大或过小',
                 'number_bomb': number_bomb,
                 'remain_times': remain_times,
                 'operate': '给出信息，并要求用户再输入一个数字'
                 })
        if remain_times - 1 <= 0:
            remain_times = 4
            number_bomb = None
            return json.dumps(
                {'error': None,
                 'message': '很遗憾，你输了',
                 'number_bomb': number_bomb,
                 'operate': '给出信息，并给出玩家炸弹数字的多少'
                 })

        if user_input_number > number_bomb:
            remain_times -= 1
            return json.dumps(
                {'error': None,
                 'message': '大了',
                 'remain_times': remain_times,
                 'number_bomb': number_bomb,
                 'operate': '给出信息，并要求用户再输入一个数字'
                 })
        elif user_input_number < number_bomb:
            remain_times -= 1
            return json.dumps(
                {'error': None,
                 'message': '小了',
                 'remain_times': remain_times,
                 'number_bomb': number_bomb,
                 'operate': '给出信息，并要求用户再输入一个数字'
                 })
        else:
            return json.dumps(
                {'error': None,
                 'message': '恭喜你，猜对了',
                 'operate': '给出信息，并结束游戏'
                 })