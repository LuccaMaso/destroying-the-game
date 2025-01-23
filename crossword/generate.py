import sys
import copy
from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        answers = []
        self.backtrack(dict(), answers)
        print(answers)
        return None

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # For each variable, each word is consistent if:
        #   the variable lenght is equal to the word lenght
        for variable, words in self.domains.items():
            variable_length = variable.length
            for word in words.copy():
                if len(word) != variable_length:
                    self.domains[variable].remove(word)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # For any pair of variables x, y that overlaps at (i, j), variable x is arc consistent with y if:
        #   every word in x domain's has at least one word in y domain's where the character in index 'i' of x is equal to the character in position 'j' in y word
        revised = False
        overlap = self.crossword.overlaps[(x, y)]
        if not overlap:
            return revised
        
        for word in self.domains[x].copy():
            if not self.arc_consistent(word, y, overlap):
                self.domains[x].remove(word)
                revised = True
        return revised


    def arc_consistent(self, x_word, y, overlap):
        return any(x_word[overlap[0]] == y_word[overlap[1]] for y_word in self.domains[y])        


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            arcs = []
            for variable_1 in self.domains:
                for variable_2 in self.domains:
                    if variable_1 != variable_2 and self.crossword.overlaps[(variable_1, variable_2)] != None:
                            arcs.append((variable_1, variable_2))

        while len(arcs) != 0:
            X, Y = arcs.pop(0)
            if self.revise(X, Y):
                if len(self.domains[X]) == 0:
                    return False
                for variable in self.domains:
                    if variable != X and self.crossword.overlaps[(variable, X)] and variable != Y:
                        arcs.append((variable, X))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        all_variables = self.domains
        for variable in all_variables:
            if variable not in assignment.keys():
                return False
        return True 

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # check if there are repeted words
        if len([v for v in assignment.values()]) != len(set([v for v in assignment.values()])):
            return False

        # check if it has the correct lenght
        for variable, value in assignment.items():
            if len(value) != variable.length:
                return False
        
        # check neighbour consistency
        for variable1, word1 in assignment.items():
            for variable2, word2 in assignment.items():
                if variable1 != variable2 and self.crossword.overlaps[(variable1, variable2)]:
                    first, second = self.crossword.overlaps[(variable1, variable2)]
                    if word1[first] != word2[second]:
                        return False
        
        return True 
        
    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        counter_restriction = {word: 0 for word in self.domains[var]}
        variables_without_value = [variable for variable in self.domains.keys() if variable not in assignment and variable != var]
        for unsigned_variable in variables_without_value:
            if self.crossword.overlaps[(var, unsigned_variable)]:
                pos_var, pos_unsigned = self.crossword.overlaps[(var, unsigned_variable)]
                for var_words in self.domains[var]:
                    for domain_word in self.domains[unsigned_variable]:
                        if var_words[pos_var] != domain_word[pos_unsigned]:
                            counter_restriction[var_words] += 1
        counter_restriction = sorted(counter_restriction.items(), key = lambda element: element[1])
        return [word[0] for word in counter_restriction]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # creates a dictionary where the key is a variable and the value a list with first element being the length of the domain and the second the degree 
        all_unsigned_variables = {variable: [0,0] for variable in self.domains if variable not in assignment}
        for variable in all_unsigned_variables:
            all_unsigned_variables[variable][0] = len(self.domains[variable])
        for variable in all_unsigned_variables:
            all_unsigned_variables[variable][1] = len(self.crossword.neighbors(variable))
        return sorted(all_unsigned_variables.items(), key = lambda element: element[1])[0][0]

    def backtrack(self, assignment, answers):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            print(assignment)
            answers.append(copy.deepcopy(assignment))
            return 
        var = self.select_unassigned_variable(assignment)
        possible_words = self.order_domain_values(var, assignment)
        for word in possible_words:
            assignment[var] = word
            if self.consistent(assignment):
                self.backtrack(assignment, answers)
                del assignment[var]
        if var in assignment.keys():
            del assignment[var]
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
