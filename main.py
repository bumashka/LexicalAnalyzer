from Analyzer import Analyzer

if __name__ == '__main__':
    path = "text.txt"
    lex = Analyzer()
    lex.analyze(path)
    lex.print_table()
