from datetime import datetime

time_type = r'%Y-%m-%d %H:%M:%S'

a = datetime.strptime('2024-08-02 23:46:25', time_type)
print(a)
b = datetime(2024, 1, 1, 1, 1, 1)
print(b.strftime(time_type))

print(a > b)