class Veruca:
    def __init__(self, key):
        self.key = key
        self.char_to_num = {}
        self.num_to_char = {}
        for x in range(26):
            self.char_to_num[chr(x + 65)] = x
            self.num_to_char[x] = chr(x + 65)

    def nums_to_chars(self, nums):
        chars = []
        for num in nums:
            chars.append(self.num_to_char[num])
        return chars

    def chars_to_nums(self, chars):
        nums = []
        for char in chars:
            nums.append(self.char_to_num[char])
        return nums

    def ksa(self, iv):
        P = []
        K = self.chars_to_nums(self.key)
        c = len(self.key)
        s = 0
        for n in range(26):
            P.append(n)
        for m in range(768):
            n = m % 26
            s = P[(s + P[n] + K[m % c]) % 26]
            P[n], P[s] = P[s], P[n]
        if iv != "":
            V = iv
            z = len(iv)
            for m in range(768):
                n = m % 26
                s = P[(s + P[n] + V[m % z]) % 26]
                P[n], P[s] = P[s], P[n]
        return P, s

    def encrypt(self, data, iv=""):
        ctxt = self.chars_to_nums(data)
        n = 0
        P, s = self.ksa(self.chars_to_nums(iv))
        for i in range(len(ctxt)):
            s = P[(s + P[n]) % 26]
            ctxt[i] = (ctxt[i] + P[(P[P[s]]+1) % 26]) % 26
            P[n], P[s] = P[s], P[n]
            n = (n + 1) % 26
        return "".join(self.nums_to_chars(ctxt))
    
    def decrypt(self, data, iv=""):
        ctxt = self.chars_to_nums(data)
        n = 0
        P, s = self.ksa(self.chars_to_nums(iv))
        for i in range(len(ctxt)):
            s = P[(s + P[n]) % 26]
            ctxt[i] = (ctxt[i] - P[(P[P[s]]+1) % 26]) % 26
            P[n], P[s] = P[s], P[n]
            n = (n + 1) % 26
        return "".join(self.nums_to_chars(ctxt))
