class ParseError(Exception):
    pass

class Parser:
    """Parser using layering to avoid left recursion"""
    
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current = self.text[0] if text else None
    
    def advance(self):
        self.pos += 1
        if self.pos < len(self.text):
            self.current = self.text[self.pos]
        else:
            self.current = None
    
    def skip_whitespace(self):
        while self.current and self.current.isspace():
            self.advance()
    
    def match(self, expected):
        """Match and consume a character"""
        self.skip_whitespace()
        if self.current == expected:
            self.advance()
            return True
        return False
    
    def number(self):
        """Parse a number"""
        self.skip_whitespace()
        result = ''
        while self.current and self.current.isdigit():
            result += self.current
            self.advance()
        return int(result) if result else None
    
    # === LAYERED GRAMMAR ===
    
    def factor(self):
        """
        factor ::= number | ( expression )
        Lowest layer - handles atoms
        """
        self.skip_whitespace()
        
        # Try parenthesized expression
        if self.current == '(':
            self.advance()
            result = self.expression()
            if not self.match(')'):
               raise ParseError("missing closing parenthesis!")
            return result
        
        # Try number
        return self.number()
    
    def term_prime(self, left):
        """
        term' ::= * factor term' | / factor term' | E

        Continuation for multiplication/division
        """
        self.skip_whitespace()
        
        while self.current in ('*', '/'):
            op = self.current
            self.advance()
            right = self.factor()
            
            if op == '*':
                left = left * right
            else:
                left = left / right

            self.skip_whitespace()
        
        return left

    def term(self):
        """
        term ::= factor term'
        Middle layer - handles multiplication/division
        """
        left = self.factor()
        return self.term_prime(left)
    
    def expression_prime(self, left):
        """
        expression' ::= + term expression' | - term expression' | E

        Continuation for addition/subtraction
        """
        self.skip_whitespace()
        
        while self.current in ('+', '-'):
            op = self.current
            self.advance()
            right = self.term()
            
            if op == '+':
                left = left + right
            else:
                left = left - right
        
        return left
    
    def expression(self):
        """
        expression ::= term expression'
        Top layer - handles addition/subtraction
        """
        left = self.term()
        return self.expression_prime(left)
    
    def parse(self):
        return self.expression()
 
def main():
    while True:
        try:
            # Read
            user_input = input("> ")
            
            # Eval (just echo for now)
            try:
                p = Parser(user_input)
                print(p.parse())
            except ParseError as e:
                print(e)
            
        except KeyboardInterrupt:
            break;
        except EOFError:
            break

if __name__ == "__main__":
    main()
