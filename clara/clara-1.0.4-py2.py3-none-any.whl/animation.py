import turtle
wn = turtle.Screen()
smiles = turtle.Turtle()

smiles.penup()
smiles.goto(-75,150)
smiles.pendown()
smiles.circle(10)     #eye one

smiles.penup()
smiles.goto(75,150)
smiles.pendown()
smiles.circle(10)     #eye two

smiles.penup()
smiles.goto(0,0)
smiles.pendown()
smiles.circle(100,90)   #right smile

smiles.penup()            #below is where i feel i'm messing up
smiles.goto(0,0)
smiles.pendown()
smiles.circle(-100,90)
