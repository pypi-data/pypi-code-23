import numpy as np
from sklearn.cross_validation import train_test_split 
import random
from collections import defaultdict
from itertools import count
from functools import partial
from sklearn import svm
from sklearn.metrics import accuracy_score
from sklearn.neighbors import KNeighborsClassifier
from statistics import mean

class Genetic:
    def __init__(self, X, y, choosen, total, population, select):
        self.values = []
        self.total = total
        self.X = X
        self.y = y
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y)

        self.population = []
        for i in range(0, population):
            self.population.append(random.sample(range(0, total), choosen))

        self.fitness = []
        for member in self.population:
            self.fitness.append(self.accuracy(member))

        self.select = select

    def accuracy(self, features):
        X_train = self.X_train[:,features]
        X_test = self.X_test[:,features]
        clf = KNeighborsClassifier(n_neighbors=3)
        #clf = svm.SVC()
        clf.fit(X_train, self.y_train)
        predicted = clf.predict(X_test)
        return accuracy_score(self.y_test, predicted)

    def fitness_value(self):
        
        self.fitness = []
        for member in self.population:
            self.fitness.append(self.accuracy(member))


    def selection(self):

    	self.selected = []

    	if self.select == 'Elitist':
    		e = self.winner()
    		self.selected.append(e)
    	elif self.select == 'Roulette_wheel':
         s = float(sum(self.fitness))
         values = []
         for i in range(len(self.fitness)):
             values.append(self.fitness[i]/s)
         for i in range(1, len(values)):
             values[i] += values[i-1]
         p = random.random()
         for i in range(0, len(values)):
             if p <= values[i]:
                 self.selected.append(self.population[i])
                 break
             

    def crossover(self):
        pop = len(self.population)
        sel = len(self.selected)
        while sel < pop:
            #print(len(self.selected), len(self.population))
            temp1 = random.randrange(0, len(self.population))
            temp2 = random.randrange(0, len(self.population))
            if random.random()  <=  0.9:
                one = list(self.population[temp1])
                two = list(self.population[temp2])
                l = len(one)
                p = random.randrange(0,l)
                one[0:p], two[0:p] = two[0:p], one[0:p]
                self.selected.append(list(one))
                self.selected.append(list(two))
                sel += 2

        self.population = list(self.selected)
        
    def mutation(self):
        for i in range(10):
            start = 0
            if self.select == 'Elitist':
                start = 1
            temp = random.randrange(start, len(self.population))
            cur = list(self.population[temp])
            if random.random() < 0.1:
                p = random.randrange(0, len(cur))
                cur[p] = self.total - cur[p] - 1
                self.population[temp] = list(cur)
    		
    def winner(self):
    	index = self.fitness.index(max(self.fitness))
    	return self.population[index]

    def genetic(self, generations):
        ans = []
        ans.append([max(self.fitness),min(self.fitness), mean(self.fitness)])
        
        for i in range(0, generations):
            
            self.selection()
            self.crossover()
            self.mutation()
            self.fitness_value()
            #print(self.population[0])
            ans.append([max(self.fitness),min(self.fitness), mean(self.fitness)])
        return ans
    
