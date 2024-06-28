def isNumberIn(sortedList, target):
    low = 0
    high = len(sortedList) - 1

    while low <= high:
        mid = (low + high) // 2
        midValue = sortedList[mid]

        if midValue == target:
            return True
        elif midValue < target:
            low = mid + 1
        else:
            high = mid - 1
    return False


sortedList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print(isNumberIn(sortedList, 7))