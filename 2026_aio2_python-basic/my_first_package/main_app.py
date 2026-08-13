# 방법1
# import magic_calc.basic_ops as mc
# print(mc.add(10,5))

# from magic_calc.basic_ops import add
# print(add(10,5))


# 방법2
# import magic_calc.basic_ops as mc
# print(mc.subtract(100,30))

# from magic_calc import basic_ops, advanced_ops
# result_sub = basic_ops.subtract(100, 30)
# print(result_sub)


# 방법 3: 패키지 내 모듈에서 특정 함수 직접 임포트
# from magic_calc.basic_ops import multiply, divide
# # from magic_calc.advanced_ops import power
# print("\n--- 방법 3: multiply, divide, power 직접 사용 ---")
# result_mul = multiply(7, 8)
# print(f"7 * 8 = {result_mul}")


import magic_calc.advanced_ops as ao

print(f"power() : {ao.power(2, 5)}")
print(f"sqrt() : {ao.sqrt(4)}")
print(f"magic_multy() : {ao.magic_multiply(10)}\n")


print(
    f"power(2,5) : {ao.power(2, 5)}, sqrt(10) : {round(ao.sqrt(10))}, magic_multy(3) : {ao.magic_multiply(3)}\n"
)
