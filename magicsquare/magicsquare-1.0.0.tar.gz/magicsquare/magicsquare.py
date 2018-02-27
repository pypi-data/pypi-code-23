'''
A program to play with magic square

(automatically generate a magic square of certain size)

'''


'''
Create blank matrix
'''
def create_field(input):
    # create the matrix with 0
    matrix = [[0 for x in range(input)] for y in range(input)]

    return matrix


'''
Create odd magic square using Mezirac method
'''
def create_odd_square(matrix):
    # initialize the variables we need
    current = 1
    current_x = 0
    current_y = len(matrix) / 2
    max_num = len(matrix)**2
    n = len(matrix)


    while(current <= max_num):
        # fill in the first number
        matrix[current_x][current_y] = current

        # every time the next move will be in the upper right direction
        next_x = current_x - 1
        next_y = current_y + 1

        # if the next move is out of top boundary
        if (next_x < 0):
            next_x += n

        # if the next move is out of right boundary
        if (next_y == n):
            next_y = n - next_y

        # if there is vacant position for the next number, fill in
        if (matrix[next_x][next_y]==0):
            current_x = next_x
            current_y = next_y
        # otherwise fill in the position below it
        else:
            current_x += 1
            if (current_x == n):
                current_x = current_x - n

        # increment the number after each fill
        current += 1

    return matrix



'''
Create double even magic square using Spring method
'''
def create_double_even_square(matrix):
    # initialize the variables
    num = 1
    n = len(matrix)

    # fill in the square in order
    for i in range(n):
        for j in range(n):
            matrix[i][j] = num
            num += 1

    # change the dimensional values to its complementary value
    for i in range(n):
        for j in range(n):
            if ( i % 4 == 0 and abs(i-j) % 4 == 0):
                for k in range(4):
                    matrix[i+k][j+k] = abs(n**2 + 1 - matrix[i+k][j+k])
            elif ( i % 4 == 3 and (i+j) % 4 == 3):
                for k in range(4):
                    matrix[i-k][j+k] = abs(n**2 + 1 - matrix[i-k][j+k])

    return matrix



'''
Create single even magic square using Strachey method
'''
def create_single_even_square(n):
    # initiaize the variables
    k = n/2
    matrix = create_field(n)
    # create four odd magic squares
    create_odd_square(matrix[:k][:k])


    for i in range(k):
        for j in range(k):
            matrix[i+k][j+k] = matrix[i][j] + k*k
            matrix[i][j+k] = matrix[i][j] + 2*k*k
            matrix[i+k][j] = matrix[i][j] + 3*k*k

    m = (n-2)/4

    for i in range(m-1):
        switch = matrix[k/2][i]
        matrix[k/2][i] = matrix[k/2+k][i]
        matrix[k/2+k][i] = switch

    switch = matrix[k/2][k/2]
    matrix[k/2][k/2] = matrix[k/2+k][k/2]
    matrix[k/2+k][k/2] = switch

    for i in range(k):
        for j in range(k/2):
            if (i != k/2):
                switch = matrix[i][j]
                matrix[i][j] = matrix[i+k][j]
                matrix[i+k][j] = switch

    for i in range(k):
        for j in range(n-1,n-1-(m-1), -1):
            switch = matrix[i][j]
            matrix[i][j] = matrix[i+k][j]
            matrix[i+k][j] = switch


    return matrix


'''
Check if the output is correct
'''
def check(n,matrix):
    # comes from the Math equations
    sum_theory = (n* ( n**2 + 1 ) ) / 2
    sum_a, sum_b = 0,0

    # check the sum of dimensional
    for i in range(n):
        for j in range(n):
            sum_a += matrix[i][j]
        if(sum_a != sum_theory):
            return False
        sum_a = 0

    for i in range(n):
        for j in range(n):
            sum_a += matrix[j][i]
        if sum_a != sum_theory:
            return False
        sum_a = 0

    for i in range(n):
        sum_a += matrix[i][i]
        sum_b += matrix[i][n-1-i]

    if (sum_a != sum_theory or sum_b != sum_theory):
        return False

    return True


def main():

    n = input("Magic Square starts! Please enter the length of square you want : ")
    if (n % 2 != 0):
        matrix = create_field(n)
        output = create_odd_square(matrix)
    elif (n % 4 == 0):
        matrix = create_field(n)
        output = create_double_even_square(matrix)
    elif (n % 2 == 0):
        output = create_single_even_square(n)
    else:
        print ("Please input a positive valid number")
        
    print ("The magic square is as follows : ")
    print (output)

    if check(n,output) is False:
        print (" The solution is wrong, magic square fails ...")
    else:
        print (" The solution is correct, you have the magic square of size %s" % (int(round(n**2))))


if __name__ == '__main__':
    main()