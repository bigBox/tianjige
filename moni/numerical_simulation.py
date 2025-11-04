import math
import matplotlib.pyplot as plt
from matplotlib import font_manager

# 设置中文字体
font_path = 'C:\\Windows\\Fonts\\simsun.ttc'  # 宋体字体文件路径
font_prop = font_manager.FontProperties(fname=font_path)
plt.rcParams['font.sans-serif'] = [font_prop.get_name()]
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 物理参数
g = 9.8  # 重力加速度 (m/s²)
H = 1.0  # O到杆的距离 (m)
mass_A = 1.0  # A的质量 (kg)
mass_B = 2.0  # B的质量 (kg)

# 理论预测值
theoretical_vA = 2 * math.sqrt(g * H)
theoretical_T = 10 * mass_A * g

# 初始条件
x0 = -H * math.sqrt(3)  # 初始x坐标，OA长度为2H，角度30度，在O点左侧
vA0 = 0.0  # 初始速度

# 数值积分参数
dt = 0.0001  # 时间步长，减小时间步长以提高精度
t_max = 1.0  # 最大模拟时间

# 初始化变量
x = x0
vA = vA0
t = 0.0
last_x = x  # 记录上一时刻的x坐标

# 数据记录
time_data = []
position_data = []
velocity_data = []
tension_data = []

# 数值积分（欧拉法）
while t < t_max:
    # 计算当前OA长度和角度
    l = math.sqrt(x**2 + H**2)
    theta = math.atan(H / x) if x != 0 else math.pi / 2

    # 计算B的速度和加速度（基于绳子不可伸长）
    vB = vA * math.cos(theta)
    
    # 计算A的加速度
    aA = (mass_B * g * math.cos(theta)) / (mass_A + mass_B * math.cos(theta)**2)
    
    # 更新速度和位置
    vA += aA * dt
    last_x = x  # 记录上一时刻的x坐标
    x += vA * dt

    # 计算绳子张力
    T = mass_A * mass_B * g * math.cos(theta) / (mass_A + mass_B * math.cos(theta)**2)
    T = T if math.cos(theta) != 0 else 0

    # 记录数据
    time_data.append(t)
    position_data.append(x)
    velocity_data.append(vA)
    tension_data.append(T)
    
    # 调试输出，每隔一定时间打印一次变量值
    if t > 0 and t % 0.1 < dt:
        print(f"时间: {t:.3f}秒, x: {x:.3f}m, vA: {vA:.3f}m/s, T: {T:.3f}N, theta: {theta:.3f}rad")

    # 检查是否到达O正下方（x从负变为正，或x的绝对值小于阈值）
    if (abs(x) < 0.001 and abs(last_x) > 0.001) or (x > 0 and last_x < 0):
        print(f"A到达O正下方时：")
        print(f"  时间: {t:.3f}秒")
        print(f"  模拟速度: {vA:.3f} m/s")
        print(f"  理论速度: {theoretical_vA:.3f} m/s")
        print(f"  速度误差: {abs(vA - theoretical_vA)/theoretical_vA * 100:.2f}%")
        print(f"  模拟张力: {T:.3f} N")
        print(f"  理论张力: {theoretical_T:.3f} N")
        print(f"  张力误差: {abs(T - theoretical_T)/theoretical_T * 100:.2f}%")
        break

    # 更新时间
    t += dt

# 绘制结果
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# 速度随时间变化
ax1.plot(time_data, velocity_data, label='模拟速度')
ax1.axhline(y=theoretical_vA, color='r', linestyle='--', label='理论速度')
ax1.set_xlabel('时间 (s)')
ax1.set_ylabel('速度 (m/s)')
ax1.set_title('金属环A的速度随时间变化')
ax1.legend()
ax1.grid(True)

# 张力随时间变化
ax2.plot(time_data, tension_data, label='模拟张力')
ax2.axhline(y=theoretical_T, color='r', linestyle='--', label='理论张力')
ax2.set_xlabel('时间 (s)')
ax2.set_ylabel('张力 (N)')
ax2.set_title('绳子张力随时间变化')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.savefig('d:\\test\\tianjige\\moni\\numerical_simulation_results.png')
plt.show()

# 生成模拟报告
with open('d:\\test\\tianjige\\moni\\numerical_simulation_report.txt', 'w', encoding='utf-8') as f:
    f.write('光滑细绳金属环物块系统数值模拟报告\n')
    f.write('=' * 50 + '\n')
    f.write(f'物理参数:\n')
    f.write(f'  H = {H} m\n')
    f.write(f'  金属环A质量 = {mass_A} kg\n')
    f.write(f'  物块B质量 = {mass_B} kg\n')
    f.write(f'  重力加速度g = {g} m/s²\n')
    f.write('\n')
    f.write('理论预测值:\n')
    f.write(f'  A到达O正下方时的速度: {theoretical_vA:.3f} m/s\n')
    f.write(f'  绳子张力: {theoretical_T:.3f} N\n')
    f.write('\n')
    f.write('模拟结果:\n')
    if abs(x) < 0.001:
        f.write(f'  A到达O正下方的时间: {t:.3f} s\n')
        f.write(f'  模拟速度: {vA:.3f} m/s\n')
        f.write(f'  速度误差: {abs(vA - theoretical_vA)/theoretical_vA * 100:.2f}%\n')
        f.write(f'  模拟张力: {T:.3f} N\n')
        f.write(f'  张力误差: {abs(T - theoretical_T)/theoretical_T * 100:.2f}%\n')
        f.write('\n')
        f.write('结论:\n')
        if abs(vA - theoretical_vA)/theoretical_vA < 0.05 and abs(T - theoretical_T)/theoretical_T < 0.05:
            f.write('  模拟结果与理论预测一致，误差在5%以内。\n')
            f.write('  理论分析正确。\n')
        else:
            f.write('  模拟结果与理论预测存在较大差异。\n')
            f.write('  需要进一步检查模型或理论分析。\n')
    else:
        f.write('  模拟未完成，A未到达O正下方。\n')

print("数值模拟完成！")
print(f"结果已保存到 d:\\test\\tianjige\\moni\\numerical_simulation_report.txt")
print(f"图表已保存到 d:\\test\\tianjige\\moni\\numerical_simulation_results.png")