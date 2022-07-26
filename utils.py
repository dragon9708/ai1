# -*- encoding: utf-8 -*-

# 最大值
def max_util(array_list):
    max_value = array_list[0]
    for i in range(1, len(array_list)):
        if max_value < array_list[i]:
            max_value = array_list[i]

    return max_value
