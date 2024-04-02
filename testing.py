import numpy as np
import pygad

# Define the fitness function


def fitness_func(ga_instance, solution, solution_idx):
    x = solution
    return x**2


# Define the parameters for the GA
num_generations = 100
num_parents_mating = 2
sol_per_pop = 10
num_genes = 1
gene_space = {'low': -5, 'high': 5}
mutation_percent_genes = 10  # Adjusted to mutate at least one gene

# Create the GA instance
ga_instance = pygad.GA(num_generations=num_generations,
                       num_parents_mating=num_parents_mating,
                       fitness_func=fitness_func,
                       sol_per_pop=sol_per_pop,
                       num_genes=num_genes,
                       mutation_type="random")

# Run the GA to optimize the function
ga_instance.run()

# Get the best solution
solution, solution_fitness, solution_idx = ga_instance.best_solution()

print("Parameters of the best solution : {solution}".format(solution=solution))
print("Fitness value of the best solution = {solution_fitness}".format(
    solution_fitness=solution_fitness))
