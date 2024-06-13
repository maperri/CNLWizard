def sum_equal_to(items, item_value, target):
    res = []

    def combination(i, sum, nums):
        sum += item_value(items[i])
        nums.append(items[i])
        if 0 < sum < target:
            while i < len(items) - 1:
                i += 1
                combination(i, sum, nums.copy())
        elif sum == target:
            res.append(nums)

    for i in range(len(items)):
        combination(i, 0, [])
    return res


def sum_less_than(items, item_value, target):
    res = []

    def combination(i, sum, nums):
        sum += item_value(items[i])
        nums.append(items[i])
        if sum < target:
            res.append(nums)
        if sum < target:
            while i < len(items) - 1:
                i += 1
                combination(i, sum, nums.copy())

    for i in range(len(items)):
        combination(i, 0, [])
    return res


def sum_greater_than(items, item_value, target):
    res = []

    def combination(i, sum, nums):
        sum += item_value(items[i])
        nums.append(items[i])
        if sum > target:
            res.append(nums)
        while i < len(items) - 1:
            i += 1
            combination(i, sum, nums.copy())

    for i in range(len(items)):
        combination(i, 0, [])
    return res


def test_sum():
    def item_value(item):
        return item

    # equal to
    assert [[1, 2, 4], [3, 4]] == sum_equal_to([1, 2, 3, 4], item_value, 7)
    assert [[1, 2, 4], [1, 2, 4], [2, 2, 3], [3, 4]] == sum_equal_to([1, 2, 2, 3, 4], item_value, 7)
    # less than
    assert [[1], [1, 2], [1, 2, 3], [1, 3], [1, 4], [2], [2, 3], [2, 4], [3], [4]] == sum_less_than([1, 2, 3, 4],
                                                                                                    item_value, 7), \
        sum_less_than([1, 2, 3, 4], item_value, 7)
    assert [[1], [1, 2], [1, 2, 2], [1, 2, 3], [1, 2], [1, 2, 3], [1, 3], [1, 4], [2], [2, 2], [2, 3], [2, 4], [2],
            [2, 3], [2, 4], [3], [4]] \
           == sum_less_than([1, 2, 2, 3, 4], item_value, 7), sum_less_than([1, 2, 2, 3, 4], item_value, 7)
    # greater than
    assert [[1, 2, 3, 4], [1, 3, 4], [2, 3, 4]] == sum_greater_than([1, 2, 3, 4], item_value, 7), \
        sum_greater_than([1, 2, 3, 4], item_value, 7)
    assert [[1, 2, 2, 3], [1, 2, 2, 3, 4], [1, 2, 2, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 3, 4], [2, 2, 3, 4], [2, 2, 4],
            [2, 3, 4], [2, 3, 4]] \
           == sum_greater_than([1, 2, 2, 3, 4], item_value, 7), sum_greater_than([1, 2, 2, 3, 4], item_value, 7)


if __name__ == '__main__':
    test_sum()
