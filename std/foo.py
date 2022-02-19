#!/usr/bin/env python3

# rule110.py

NUMBER_OF_COLUMNS = 120


def rule110(number_of_columns):
    number_of_rows = number_of_columns - 2

    line = " "*(number_of_columns - 1) + "*"

    for i in range(number_of_rows):
        next_line = " "
        for j in range(1, number_of_columns-1):
            pattern = line[j-1] + line[j] + line[j+1]
            if pattern == "   ":
                next_line += " "
            elif pattern == "  *":
                next_line += "*"
            elif pattern == " * ":
                next_line += "*"
            elif pattern == " **":
                next_line += "*"
            elif pattern == "*  ":
                next_line += " "
            elif pattern == "* *":
                next_line += "*"
            elif pattern == "** ":
                next_line += "*"
            elif pattern == "***":
                next_line += " "
        next_line += " "
        line = next_line
        print(line)


if __name__ == "__main__":
    rule110(NUMBER_OF_COLUMNS)