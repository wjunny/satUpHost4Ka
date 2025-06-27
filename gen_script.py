print('name_table = {')

for i in range(1, 9):
    for j in range(1, 9):
        print('\'G{}{}_A1H\':G{}{}_A1H, '.format(i, j, i, j), end='')
        print('\'G{}{}_A2H\':G{}{}_A2H, '.format(i, j, i, j), end='')
        print('\'G{}{}_A3H\':G{}{}_A3H, '.format(i, j, i, j), end='')
        print('\'G{}{}_A4H\':G{}{}_A4H, '.format(i, j, i, j), end='')
        print('\'G{}{}_A1V\':G{}{}_A1V, '.format(i, j, i, j), end='')
        print('\'G{}{}_A2V\':G{}{}_A2V, '.format(i, j, i, j), end='')
        print('\'G{}{}_A3V\':G{}{}_A3V, '.format(i, j, i, j), end='')    
        print('\'G{}{}_A4V\':G{}{}_A4V, '.format(i, j, i, j))
print('}')        