from tkinter import *
import tkinter.ttk as ttk 
from ttkthemes import themed_tk as tk
from PIL import Image, ImageTk
import copy
from random import randint
import time
from decimal import Decimal

# These global values are used by the user for inputs
steps = 0
gens = 10
pop = 100
cross = 1
muta = 1
number = 0

# This class focuses on genetic algorithm which (in this implementation) is inferior to the genetic algorithm.
class Genetic():

    # This function creates a population with random genomes.
    def create_population(self, size, n):
        population = [None for x in range(size)]
        for i in range(size): # For every genome
            genome = [[1 for x in range(n)] for y in range(n)]
            for j in range(n): # For every row
                genome[j][randint(0,n-1)] = -1
            population[i]=(copy.deepcopy(genome), 10000)
        return population
    
    # This function measures how many queens are attacking each other given a genome.
    def fitness(self, genome):
        attacked_queens = 0
        n = len(genome)
        for i in range(n):
            for j in range(n):
                if genome[i][j] == -1:
                    for k in range(n):
                        if genome[i][k] == -1 and k != j: # Rows
                            attacked_queens = attacked_queens + 1

                        if genome[k][j] == -1 and k != i: # Columns
                            attacked_queens = attacked_queens + 1

                        if i+k < n and j+k < n: # Bottom Right
                            if genome[i+k][j+k] == -1 and k != 0:
                                attacked_queens = attacked_queens + 1

                        if i+k < n and j-k >= 0: # Bottom Left
                            if genome[i+k][j-k] == -1 and k != 0:
                                attacked_queens = attacked_queens + 1

                        if i-k >= 0 and j+k < n: # Top Right
                            if genome[i-k][j+k] == -1 and k != 0:
                                attacked_queens = attacked_queens + 1

                        if i-k >= 0 and j-k >= 0: # Top Right
                            if genome[i-k][j-k] == -1 and k != 0:
                                attacked_queens = attacked_queens + 1
        return attacked_queens
    # This function takes a population and returns the two best genomes according to the fitness function above.
    def survival(self, population):
        global steps
        best = 100000000
        second_best = 100000000
        best_genome = []
        for i in range(len(population)):
            fitness_score = self.fitness(population[i][0])
            steps = steps + 1
            if fitness_score < best or (fitness_score == best and randint(0, 100) < 5): #If two genomes have the same fitness value, there is a 5% that the new genome survives.
                second_best_genome = copy.deepcopy(best_genome)
                second_best = best
                best_genome = copy.deepcopy(population[i][0])
                best = fitness_score
            elif fitness_score < second_best or (fitness_score == second_best and randint(0, 100) < 5): #If two genomes have the same fitness value, there is a 5% that the new genome survives.
                second_best_genome = copy.deepcopy(population[i][0])
                second_best = fitness_score
        return [(best_genome, best),(second_best_genome, second_best)]

    # This function mates two genomes either using single crossover or multicrossover depending on the c_type value.
    def crossover(self, genome1, genome2, genome1_score, genome2_score, c_type):
        n = len(genome1)
        genome1_copy = copy.deepcopy(genome1)
        genome2_copy = copy.deepcopy(genome2)
        if c_type == 1: # SINGLE CROSSOVER
            for i in range(randint(1,n-2)):
                genome1[i] = genome2_copy[i]
                genome2[i] = genome1_copy[i]
        elif c_type == 2: # MULTI CROSSOVER
            number_of_crossovers = randint(2,n-2)
            for i in range(number_of_crossovers):
                crossover_index = randint(0, n-1)
                genome1[crossover_index] = genome2_copy[crossover_index]
                genome2[crossover_index] = genome1_copy[crossover_index]      
        return [(genome1, genome1_score), (genome2, genome2_score)]

    # This function has a chance to mutate one queen given a genome and the chance to mutate it.
    def mutation(self, genome): #Mutation range (0.001 ~ 1)
        n = len(genome[0])
        global muta
        mutation_rate = muta
        mutation_rate = mutation_rate * 1000
        if mutation_rate >= randint(1, 1000): #MUTATE
            index = randint(0,n-1)
            for i in range(n):
                genome[0][index][i] = 1
            genome[0][index][randint(0,n-1)] = -1
        return genome

    # This function solves the board using all above functions and returns either a solution or an error that no solution was found. 
    def generations(self, number_of_generations, population_size, n, c_type):
        global steps, number
        steps = 0
        number = 0
        population = self.create_population(population_size, n)
        new_population = []
        pair = []
        for i in range(number_of_generations): # For every generation do the following:
            number = number + 1
            for k in range(int(population_size / 2)):
                pair = copy.deepcopy(self.survival(population))
                for j in pair:
                    print(j[1], number)
                    if j[1] == 0:
                        return j[0]
                pair = copy.deepcopy(self.crossover(pair[0][0], pair[1][0], pair[0][1], pair[1][1], c_type))
                for j in range(2):
                    pair[j] = self.mutation(pair[j])
                new_population.extend(pair)
            population = copy.deepcopy(new_population)
            new_population.clear()
        return [[-1 for x in range(n)] for y in range(n)] # NO SOLUTION FOUND

# This class focuses on A* algorithm which (in this implementation) is superior to the genetic algorithm
class State():

    # Constructor for holding important values for the class
    def __init__(self, parent = 0, children = 0, board = 0, hn = 0, queens = 0):
        self.parent = parent
        self.children = children
        self.board = board
        self.hn = hn
        self.queens = queens

    # This function returns how many squares are not attacked by queens
    def AFindHeuristic(self):
        Hn = 0
        for i in self.board:
            for j in i:
                if j == 1:
                    Hn += 1
        return Hn

    # This function finds the heuristic value of each row
    def AHeuristicRow(self):
        for tmp_row_index in range(len(self.board)):
            if -1 in self.board[tmp_row_index]:
                continue
            if tmp_row_index == len(self.board)-1:
                return self.board[tmp_row_index]
            row = copy.deepcopy(self.board[tmp_row_index])
            for i in range(len(row)):
                if row[i] == 1:
                    tmp_board = copy.deepcopy(self.board)
                    tmp_board[tmp_row_index][i] = -1
                    tmp_state = State(board = tmp_board, queens=self.queens+1)
                    tmp_state.CheckForDanger()
                    row[i] = tmp_state.AFindHeuristic()  
            return row
        return [0 for i in len(self.board[0])]

    # This function takes a board as a 2D array of avaliable squares (1), with queens (-1), and assigns (0) if a queens attacks thats square.
    def CheckForDanger(self):
        n = len(self.board)
        for i in range(n):
            for j in range(n):
                if self.board[i][j] == -1: # Meaning if there is a queen on that square, do the following:
                    for k in range(n):
                        if self.board[i][k] == 1 and k != j: # Rows
                            self.board[i][k] = 0
                        if self.board[k][j] == 1 and k != i: # Columns
                            self.board[k][j] = 0
                        if i+k < n and j+k < n: # Bottom Right
                            if self.board[i+k][j+k] == 1 and k != 0:
                                self.board[i+k][j+k] = 0
                        if i+k < n and j-k >= 0: # Bottom Left
                            if self.board[i+k][j-k] == 1 and k != 0:
                                self.board[i+k][j-k] = 0
                        if i-k >= 0 and j+k < n: # Top Right
                            if self.board[i-k][j+k] == 1 and k != 0:
                                self.board[i-k][j+k] = 0
                        if i-k >= 0 and j-k >= 0: # Top Right
                            if self.board[i-k][j-k] == 1 and k != 0:
                                self.board[i-k][j-k] = 0

    # This function is recursive and takes the board row by row, when it reaches a deadend it goes back and picks the best route according to the function.
    def Solve(self):
        global steps
        steps = steps + 1
        heuristic = self.AHeuristicRow()
        row_of_interest = 0
        for i in range(len(self.board)):
            if -1 not in self.board[i]:
                row_of_interest = i
                break
        x = copy.deepcopy(heuristic)
        sorted_scores = self.SortScores(x)
        for i in sorted_scores:
            if heuristic[i] <= 0:
                return None
            tmp_board = copy.deepcopy(self.board)
            tmp_board[row_of_interest][i] = -1
            tmp_state = State(board = tmp_board, queens=self.queens+1)
            tmp_state.CheckForDanger()
            if tmp_state.queens == len(tmp_board):
                return tmp_state.board          
            solution = tmp_state.Solve()
            if solution is None:
                continue
            return solution
        return None

    # This function returns an array of sorted heuristic scores and acts as a queue. It is used in the function Solve().
    def SortScores(self, row):
        sorted_scores = [0 for i in range(len(row))]
        for i in range(len(row)):
            _max = max(row)
            sorted_scores[i] = row.index(_max)
            row[row.index(_max)] = -1
        return sorted_scores


# Below is the GUI implementation of the program, ranging from themes, buttons, labels, sliders, radiobuttons, windows, and so on.

img = Image.open('queen.png')
cols = num = 0

def SliderChanging(var):
    label_n3_2.configure(text="")
    label_n4_2.configure(text="")
    global cols, rows
    cols = rows = int(float(var))
    label_n2.config(text=cols)
    empty_board = [[1]*rows]*cols
    CreateBoard(empty_board)
    label_n8.place_forget()

def CreateBoard(position):
    global new_img
    board_canvas.delete("all")
    n = len(position)
    ratio = 800/n
    imga=img.resize((int(ratio), int(ratio)), Image.ANTIALIAS)
    new_img = ImageTk.PhotoImage(imga)  # Convert to PhotoImage
    for i in range(n):
        for j in range(n):
            if((j+i) % 2 == 0):
                board_canvas.create_rectangle(
                    j*ratio, i*ratio, (j+1)*ratio, (i+1)*ratio, fill="#b58863")
            if((j+i) % 2 == 1):
                board_canvas.create_rectangle(
                    j*ratio, i*ratio, (j+1)*ratio, (i+1)*ratio, fill="#f0d9b5")
            if (position[i][j] == -1):
                board_canvas.create_image(
                    j*ratio, i*ratio, anchor=NW, image=new_img)

def radio():
    label_n3_2.configure(text="")
    label_n4_2.configure(text="")
    SliderChanging(cols)
    label_n8.place_forget()
    if algorithm.get() == 1:
        label_n5.place_forget()
        label_n5_2.place_forget()
        label_n6.place_forget()
        label_n6_2.place_forget()
        label_n7.place_forget()
        label_n7_2.place_forget()
        label_n8.place_forget()
        slider_generation.place_forget()
        slider_population.place_forget()
        slider_mutation.place_forget()
        radiobutton_single.place_forget()
        radiobutton_multi.place_forget()
        label_n9.place(x=10, y=280)
    elif algorithm.get() == 2:
        label_n5.place(x=10, y=290)
        label_n6.place(x=10, y=340)
        label_n5_2.place(x=350, y=290)
        label_n6_2.place(x=350, y=340)
        label_n7.place(x=10, y=390)
        label_n7_2.place(x=345, y=392)
        slider.place(x=78,y=148)
        slider_generation.place(x=78,y=300)
        slider_population.place(x=78,y=350)
        slider_mutation.place(x=181,y=400)
        radiobutton_single.place(x=25, y=450)
        radiobutton_multi.place(x=25, y=480)
        label_n9.place_forget()

def button():
    label_n8.place_forget()
    global steps
    steps = 0
    start = time.time()
    if algorithm.get() == 1:
        initial_board = [[1 for i in range(cols)] for j in range(rows)] 
        initial_state = State(board = initial_board, queens=0)
        initial_state.CheckForDanger()
        final = initial_state.Solve()
        end = time.time()
        passed = Decimal((end - start))
        label_n3_2.configure(text=str(round(passed, 4)) + " s")
        label_n4_2.configure(text=steps)
        CreateBoard(final)
    elif algorithm.get() == 2:
        solution = Genetic().generations(gens,pop,cols,cross)
        if solution == [[-1 for x in range(cols)] for y in range(cols)]:
            label_n8.place(x=630, y=375)
        else:
            CreateBoard(solution)
        end = time.time()
        passed = Decimal((end - start))
        label_n3_2.configure(text=str(round(passed, 4)) + " s")
        label_n4_2.configure(text=str(number) + " gen")

def SliderGen(var):
    global gens
    label_n5_2.config(text=int(float(var)))
    gens = int(float(var))
    label_n8.place_forget()

def SliderPop(var):
    global pop
    if int(float(var)) % 2 == 0:
        label_n6_2.config(text=int(float(var)))
        pop = int(float(var))
        label_n8.place_forget()

def SliderMuta(var):
    global muta
    var = round(float(var), 3)
    label_n7_2.config(text=var)
    muta = var
    label_n8.place_forget()

# Geometry of the window
window = tk.ThemedTk()
style = ttk.Style(window)
window.set_theme("black")
window.title("N-Queens Solver")
window.geometry("1200x800")
window.resizable(False, False)
window.configure(background="#8b8987")

# Geometry of the board
board_canvas = Canvas(window, width=800, height=800, bg="white", bd=-2)
board_canvas.pack()
board_canvas.place(x=400, y=0)

# Buttons and sliders and labels
label_nqueens = Label(window, text="N-Queens Solver", bg="#8b8987", font=("Courier", 30))
label_nqueens.place(x=15, y=10)

label_n1 = Label(window, text="N =", bg="#8b8987", font=("sans", 18))
label_n1.place(x=25, y=140)

label_n2 = Label(window, text=8, bg="#8b8987", font=("sans", 18))
label_n2.place(x=352, y=140)

label_n3 = Label(window, text="Time: ", bg="#8b8987", font=("sans", 18))
label_n3.place(x=225, y=700)

label_n3_2 = Label(window, text="", bg="#8b8987", font=("sans", 14))
label_n3_2.place(x=290, y=702)

label_n4 = Label(window, text="Steps: ", bg="#8b8987", font=("sans", 18))
label_n4.place(x=225, y=740)

label_n4_2 = Label(window, text="", bg="#8b8987", font=("sans", 14))
label_n4_2.place(x=300, y=743)

label_n5 = Label(window, text="Gen=", bg="#8b8987", font=("sans", 18))
label_n5.place(x=10, y=290)

label_n6 = Label(window, text="Pop= ", bg="#8b8987", font=("sans", 18))
label_n6.place(x=10, y=340)

label_n5_2 = Label(window, text="10", bg="#8b8987", font=("sans", 14))
label_n5_2.place(x=350, y=290)

label_n6_2 = Label(window, text="20", bg="#8b8987", font=("sans", 14))
label_n6_2.place(x=350, y=340)

label_n7 = Label(window, text="Mutation rate = ", bg="#8b8987", font=("sans", 18))
label_n7.place(x=10, y=390)

label_n7_2 = Label(window, text="0.01", bg="#8b8987", font=("sans", 14))
label_n7_2.place(x=345, y=392)

label_n8 = Label(window, text="NO SOLUTION FOUND", bg="red", font=("Courier", 30))
label_n8.place(x=630, y=375)
label_n8.place_forget()

label_n9 = Label(window,justify=LEFT, text="Heuristic: The number of squares that are not attacked given a board\nwith queens. The more the number of unattacked squares, the better.\n\ng(n) is the cost to the goal state.\nh(n) is the heuristic function.\nFinally, f(n) = g(n) + h(n).", bg="#8b8987", font=("sans", 9))
label_n9.place(x=10, y=280)

cross = IntVar()
cross.set(1)

slider = ttk.Scale(window, from_=4, to=100, orient=HORIZONTAL, command=SliderChanging ,length=260)
slider.pack()
slider.set(8)
slider.place(x=78,y=148)

slider_generation = ttk.Scale(window, from_=1, to=1000, orient=HORIZONTAL, command=SliderGen ,length=260)
slider_generation.pack()
slider_generation.set(10)
slider_generation.place(x=78,y=300)

slider_population = ttk.Scale(window, from_=1, to=1000, orient=HORIZONTAL, command=SliderPop ,length=260)
print(slider_generation.keys())
slider_population.pack()
slider_population.set(100)
slider_population.place(x=78,y=350)

slider_mutation = ttk.Scale(window, from_=0.001, to=1, orient=HORIZONTAL , command=SliderMuta ,length=157)
slider_mutation.pack()
slider_mutation.set(100)
slider_mutation.place(x=181,y=400)

radiobutton_single = ttk.Radiobutton(window, text="Single Crossover", variable=cross, value=1, style="Wild.TRadiobutton")
radiobutton_multi =ttk.Radiobutton(window, text="Multi Crossover", variable=cross, value=2, style="Wild.TRadiobutton")
radiobutton_single.pack()
radiobutton_multi.pack()
radiobutton_single.place(x=25, y=450)
radiobutton_multi.place(x=25, y=480)

s = ttk.Style() # Style of the program
s.configure('Wild.TRadiobutton', background='#8b8987', font=("sans", 12), foreground="black")

algorithm = IntVar()
algorithm.set(1)
radiobutton_a = ttk.Radiobutton(window, text=" A* Algorithm", variable=algorithm, value=1, command=radio, style="Wild.TRadiobutton")
radiobutton_genetic =ttk.Radiobutton(window, text=" Genetic Algorithm", variable=algorithm, value=2, command=radio, style="Wild.TRadiobutton")
radiobutton_a.pack()
radiobutton_genetic.pack()
radiobutton_a.place(x=25, y=200)
radiobutton_genetic.place(x=25, y=230)

button_search = Button(window, text="SEARCH",font=("Courier", 30), command=button)
button_search.pack
button_search.place(x=25,y=700)

cols = rows = 8

label_n5.place_forget()
label_n5_2.place_forget()
label_n6.place_forget()
label_n6_2.place_forget()
label_n7.place_forget()
label_n7_2.place_forget()
label_n8.place_forget()
slider_generation.place_forget()
slider_population.place_forget()
slider_mutation.place_forget()
radiobutton_single.place_forget()
radiobutton_multi.place_forget()

window.mainloop() # Display the program