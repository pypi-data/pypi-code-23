import numpy as np

n = 5
world = np.zeros((n, n))
num = np.zeros((n, n))


def transition(s, a):
    i_s = s[0]
    j_s = s[1]

    i_a = a[0]
    j_a = a[1]
    if (i_s == 0 and i_a == -1) or (j_s == 0 and j_a == -1) or (j_s == n - 1 and j_a == 1) \
            or (i_s == n - 1 and i_a == 1):
        s_p = s
        proba = 0
        # r = -1
    else:
        i_sp = i_s + i_a
        j_sp = j_s + j_a
        s_p = [i_sp, j_sp]
        proba = 1 / 4
        # r = 0
    r = -1
    # if s == [0, 1]:
    #     s_p = [4, 1]
    #     r = 10
    #
    # if s == [0, 3]:
    #     s_p = [2, 3]
    #     r = 5

    return s_p, r, proba


V = np.zeros((n, n))
gamma = 1
while True:
    Delta = 0
    for i_s in range(5):
        for j_s in range(5):
            state = [i_s, j_s]
            if (i_s == 0 and j_s == 0) or (i_s == n - 1 and j_s == n - 1):
                continue

            v = V[i_s, j_s]
            s_u, r_u, pr_u = transition(state, [-1, 0])
            s_d, r_d, pr_d = transition(state, [1, 0])
            s_l, r_l, pr_l = transition(state, [0, -1])
            s_r, r_r, pr_r = transition(state, [0, 1])
            V[i_s, j_s] = pr_u * (r_u + gamma * V[s_u[0], s_u[1]]) + \
                          pr_d * (r_d + gamma * V[s_d[0], s_d[1]]) + \
                          pr_l * (r_l + gamma * V[s_l[0], s_l[1]]) + \
                          pr_r * (r_r + gamma * V[s_r[0], s_r[1]])

            # print(Delta)
            Delta = np.max(np.array([Delta, np.abs(v - V[i_s, j_s])]))
    if Delta < 0.001:
        break

print(np.round(V))
