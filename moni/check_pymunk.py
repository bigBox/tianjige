import pymunk

print("pymunk版本:", getattr(pymunk, '_version', '未知'))
print("可用的约束类:", [attr for attr in dir(pymunk) if 'Joint' in attr])
print("pymunk.constraints模块是否存在:", hasattr(pymunk, 'constraints'))
if hasattr(pymunk, 'constraints'):
    print("constraints模块中的可用类:", [attr for attr in dir(pymunk.constraints) if 'Joint' in attr])