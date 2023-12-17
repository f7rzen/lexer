from lexer.LexicalAnalizer import LexicalAnalyzer


def main():
    filename = "test.txt"  # Replace with the name of your input file
    identifiersTable = set()  # Your identifiers table

    lexical_analyzer = LexicalAnalyzer(filename, identifiersTable)

    try:
        lexical_analyzer.analysis()
        print("Tokens:")
        for token in lexical_analyzer.lexeme_table:
            print(token)

        print("\nIdentifiers Table:")
        for identifier in identifiersTable:
            print(identifier)

    except Exception as e:
        print(f"Error: {e} in file {lexical_analyzer.error.filename}, "
              f"line: {lexical_analyzer.current.line_number}, position: {lexical_analyzer.current.pos_number}")

if __name__ == "__main__":
    main()