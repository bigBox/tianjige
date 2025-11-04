import pymunk
import pygame
import math
import matplotlib.pyplot as plt

# 初始化Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("光滑细绳金属环物块系统模拟")

# 设置物理参数
g = 9.8  # 重力加速度 (m/s²)
H = 1.0  # O到杆的距离 (m)
OA0 = 2 * H  # 初始OA长度 (m)
mass_A = 1.0  # A的质量 (kg)
mass_B = 2.0  # B的质量 (kg)

# 理论预测值
theoretical_vA = 2 * math.sqrt(g * H)
theoretical_T = 10 * mass_A * g

# 缩放因子（将米转换为像素）
scale = 100  # 1米 = 100像素

# 创建物理空间
space = pymunk.Space()
space.gravity = (0, g * scale)  # 重力方向向下（PyGame坐标系y轴向下为正），乘以缩放因子

# 创建静态物体（天花板和杆）
static_body = space.static_body

# O点位置（屏幕上方中央）
O_pos = (400, 100)

# 杆（水平放置，O点正下方H处）
rod_y = O_pos[1] + H * scale
rod_start = (O_pos[0] - 200, rod_y)
rod_end = (O_pos[0] + 200, rod_y)
rod = pymunk.Segment(static_body, rod_start, rod_end, 2)
rod.friction = 0  # 杆光滑
rod.color = (0, 255, 0)
space.add(rod)

# 创建金属环A（初始位置）
# 初始时OA与水平杆夹角30度，OA长度为2H
# 计算A的初始坐标：在O点左侧，距离O点水平距离为H/tan(30°)，垂直距离为H（在杆上）
A_x = O_pos[0] - H / math.tan(math.radians(30)) * scale
A_y = rod_y
A_body = pymunk.Body(mass=mass_A, moment=pymunk.moment_for_circle(mass_A, 0, 5))
A_body.position = (A_x, A_y)
A_shape = pymunk.Circle(A_body, 5)
A_shape.color = (255, 0, 0)
A_shape.friction = 0  # 金属环与杆光滑
# 限制A只能沿杆（水平方向）运动
A_body.velocity_func = lambda body, gravity, damping, dt: (body.velocity[0], 0)
A_body.position_func = lambda body, dt: (body.position[0], rod_y)
space.add(A_body, A_shape)

# 创建物块B（初始位置）
B_x = O_pos[0]
B_y = O_pos[1] + OA0 * scale
B_body = pymunk.Body(mass=mass_B, moment=pymunk.moment_for_circle(mass_B, 0, 10))
B_body.position = (B_x, B_y)
B_shape = pymunk.Circle(B_body, 10)
B_shape.color = (0, 0, 255)
space.add(B_body, B_shape)

# 创建绳子模拟：使用DistanceJoint
# 绳子分为两部分：A到O，O到B
OA_joint = pymunk.constraints.DistanceJoint(A_body, static_body, (0, 0), O_pos)
OB_joint = pymunk.constraints.DistanceJoint(B_body, static_body, (0, 0), O_pos)
OA_joint.collide_bodies = False
OB_joint.collide_bodies = False
space.add(OA_joint, OB_joint)

# 数据采集
vA_data = []
T_data = []
time_data = []
simulation_time = 0.0
time_step = 1/60  # 60 FPS

# 标志位：是否已到达O正下方
has_reached_below_O = False

# 主循环
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 更新物理状态
    space.step(time_step)
    simulation_time += time_step

    # 获取A的位置
    A_x, A_y = A_body.position
    A_x_m = A_x / scale  # 转换为米

    # 记录数据
    vA = A_body.velocity.length / scale  # 速度转换为m/s
    vA_data.append(vA)
    time_data.append(simulation_time)

    # 计算当前OA与水平杆的夹角
    OA_length = math.sqrt((A_x - O_pos[0])**2 + (A_y - O_pos[1])**2) / scale
    if OA_length > 0:
        theta = math.asin(H / OA_length)  # 因为杆到O点的距离是H，所以对边是H，斜边是OA长度
    else:
        theta = 0
    
    # 当A到达O正下方附近（x在O_pos[0] ± 0.01米之间）时，记录张力
    if abs(A_x_m - O_pos[0]/scale) < 0.01 and not has_reached_below_O:
        # 计算A的速度大小
        vA = abs(A_body.velocity[0]) / scale  # 速度转换为m/s
        
        # 计算绳子张力（使用理论公式）
        tension = mass_A * (g + vA**2 / H)
        
        T_data.append(tension)
        has_reached_below_O = True
        print(f"A到达O正下方时：")
        print(f"  时间: {simulation_time:.3f}秒")
        print(f"  模拟速度: {vA:.3f} m/s")
        print(f"  理论速度: {theoretical_vA:.3f} m/s")
        print(f"  速度误差: {abs(vA - theoretical_vA)/theoretical_vA * 100:.2f}%")
        print(f"  模拟张力: {tension:.3f} N")
        print(f"  理论张力: {theoretical_T:.3f} N")
        print(f"  张力误差: {abs(tension - theoretical_T)/theoretical_T * 100:.2f}%")

    # 绘制
    screen.fill((255, 255, 255))

    # 绘制杆
    pygame.draw.line(screen, (0, 255, 0), rod_start, rod_end, 4)

    # 绘制O点
    pygame.draw.circle(screen, (0, 0, 0), O_pos, 5)

    # 绘制金属环A
    pygame.draw.circle(screen, (255, 0, 0), (int(A_x), int(A_y)), 5)

    # 绘制物块B
    pygame.draw.circle(screen, (0, 0, 255), (int(B_body.position[0]), int(B_body.position[1])), 10)

    # 绘制绳子
    pygame.draw.line(screen, (0, 0, 0), O_pos, (int(A_x), int(A_y)), 2)
    pygame.draw.line(screen, (0, 0, 0), O_pos, (int(B_body.position[0]), int(B_body.position[1])), 2)

    # 显示理论值
    font = pygame.font.Font(None, 36)
    text_vA = font.render(f"理论速度: {theoretical_vA:.2f} m/s", True, (0, 0, 0))
    text_T = font.render(f"理论张力: {theoretical_T:.2f} N", True, (0, 0, 0))
    screen.blit(text_vA, (10, 10))
    screen.blit(text_T, (10, 50))

    # 显示模拟值
    if len(vA_data) > 0:
        text_vA_sim = font.render(f"模拟速度: {vA_data[-1]:.2f} m/s", True, (255, 0, 0))
        screen.blit(text_vA_sim, (10, 90))
    if len(T_data) > 0:
        text_T_sim = font.render(f"模拟张力: {T_data[-1]:.2f} N", True, (0, 0, 255))
        screen.blit(text_T_sim, (10, 130))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

# 生成图表
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# 速度随时间变化
ax1.plot(time_data, vA_data, label='模拟速度')
ax1.axhline(y=theoretical_vA, color='r', linestyle='--', label='理论速度')
ax1.set_xlabel('时间 (s)')
ax1.set_ylabel('速度 (m/s)')
ax1.set_title('金属环A的速度随时间变化')
ax1.legend()
ax1.grid(True)

# 张力随时间变化（如果有数据）
if len(T_data) > 0:
    # 在A到达O正下方的时间点绘制张力
    ax2.scatter([time_data[-1]], T_data, color='b', label='模拟张力')
    ax2.axhline(y=theoretical_T, color='r', linestyle='--', label='理论张力')
    ax2.set_xlabel('时间 (s)')
    ax2.set_ylabel('张力 (N)')
    ax2.set_title('绳子张力在A到达O正下方时的值')
    ax2.legend()
    ax2.grid(True)

plt.tight_layout()
plt.savefig('d:\\test\\tianjige\\moni\\simulation_results.png')
plt.show()

# 生成对比报告
with open('d:\\test\\tianjige\\moni\\simulation_report.txt', 'w') as f:
    f.write('光滑细绳金属环物块系统模拟报告\n')
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
    if has_reached_below_O:
        f.write(f'  A到达O正下方的时间: {simulation_time:.3f} s\n')
        f.write(f'  模拟速度: {vA_data[-1]:.3f} m/s\n')
        f.write(f'  速度误差: {abs(vA_data[-1] - theoretical_vA)/theoretical_vA * 100:.2f}%\n')
        f.write(f'  模拟张力: {T_data[-1]:.3f} N\n')
        f.write(f'  张力误差: {abs(T_data[-1] - theoretical_T)/theoretical_T * 100:.2f}%\n')
        f.write('\n')
        f.write('结论:\n')
        if abs(vA_data[-1] - theoretical_vA)/theoretical_vA < 0.05 and abs(T_data[-1] - theoretical_T)/theoretical_T < 0.05:
            f.write('  模拟结果与理论预测一致，误差在5%以内。\n')
            f.write('  理论分析正确。\n')
        else:
            f.write('  模拟结果与理论预测存在较大差异。\n')
            f.write('  需要进一步检查模型或理论分析。\n')
    else:
        f.write('  模拟未完成，A未到达O正下方。\n')

print("模拟完成！")
print(f"结果已保存到 d:\\test\\tianjige\\moni\\simulation_report.txt")
print(f"图表已保存到 d:\\test\\tianjige\\moni\\simulation_results.png")