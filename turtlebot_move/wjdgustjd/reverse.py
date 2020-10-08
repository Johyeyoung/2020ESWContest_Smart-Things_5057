


def order_reversed(order):
    order = list(reversed(order))  # 경로역순으로 정렬하고 방향을 재조정후 return'
    print(order)
    order_change = {"G":"B", "B":"G", "L":"R", "R":"L"}
    for i in range(len(order)):
        order[i] = order[i].replace(order[i][0], order_change[order[i][0]])
   # order = order + "/G10"  # 원래 앞으로 바라보도록 기본 경로 추가
    print(order)
    return order




