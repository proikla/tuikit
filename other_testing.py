MODES = {'regular': 0, 'bold': 1, 'dim': 2, 'italic': 3}

for i in range(0, 37):
    print(f"{i=:2}: \033[{i};5m test \033[0;0m")
# for i in range(0, 30):
#     print(f"{i=}: \033[1;0m test \033[0;0m")
# for i in range(29, 48):
#     print(f"\033[0;{i}m test \033[0;0m")
