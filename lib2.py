def get_proportional_function(a, b):
    """
    给定两个数 a, b，返回一个函数 f(new_a)
    f(new_a) 会根据 a -> new_a 的比例计算 b 的新值
    """
    ratio = b / a  # 第二个数相对于第一个数的比例

    def f(new_a):
        return new_a * ratio

    return f

# ----------------------------
# 使用示例
# ----------------------------
a, b = 5, 2
f = get_proportional_function(a, b)

new_a = 3
new_b = f(new_a)
print(f"原来: {a}, {b}")
print(f"第一个数变成 {new_a} 时，第二个数等比例变为 {new_b}")
