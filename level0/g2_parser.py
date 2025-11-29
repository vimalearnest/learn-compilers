class ParseError(Exception):
    pass

class Parser:
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
    
    def number(self):
        """Parse integer or float"""
        self.skip_whitespace()
        result = ''
        has_dot = False
        
        while self.current and (self.current.isdigit() or self.current == '.'):
            if self.current == '.':
                if has_dot:
                    break
                has_dot = True
            result += self.current
            self.advance()
        
        if not result or result == '.':
            return None
        
        return float(result) if has_dot else int(result)
    
    def primary(self):
        """
        primary ::= number | ( expression )
        HIGHEST precedence - atoms
        """
        self.skip_whitespace()
        
        if self.current == '(':
            self.advance()
            result = self.expression()
            self.skip_whitespace()
            if self.current == ')':
                self.advance()
            return result
        
        return self.number()
    
    def unary(self):
        """
        unary ::= - unary | primary
        Level 4 - unary minus
        """
        self.skip_whitespace()
        
        if self.current == '-':
            self.advance()
            return -self.unary()
        
        return self.primary()
    
    def exponent(self):
        """
        exponent ::= unary (^ exponent)?
        Level 3 - exponentiation (RIGHT-associative)
        """
        left = self.unary()
        
        self.skip_whitespace()
        if self.current == '^':
            self.advance()
            # Right-associative: parse full right side
            right = self.exponent()
            return left ** right
        
        return left
    
    def term(self):
        """
        term ::= exponent ((* | /) exponent)*
        Level 2 - multiplication and division (LEFT-associative)
        """
        left = self.exponent()
        
        while True:
            self.skip_whitespace()
            
            if self.current == '*':
                self.advance()
                right = self.exponent()
                left = left * right
            elif self.current == '/':
                self.advance()
                right = self.exponent()
                left = left / right
            else:
                break
        
        return left
    
    def expression(self):
        """
        expression ::= term ((+ | -) term)*
        Level 1 - addition and subtraction (LEFT-associative)
        LOWEST precedence
        """
        left = self.term()
        
        while True:
            self.skip_whitespace()
            
            if self.current == '+':
                self.advance()
                right = self.term()
                left = left + right
            elif self.current == '-':
                self.advance()
                right = self.term()
                left = left - right
            else:
                break
        
        return left
    
    def parse(self):
        result = self.expression()
        self.skip_whitespace()
        if self.current is not None:
            raise Exception(f"Unexpected character: {self.current}")
        return result


def test():
    tests = [
        ("2 + 3", 5),
        ("2 * 3 + 4", 10),                    # (2 * 3) + 4
        ("2 + 3 * 4", 14),                    # 2 + (3 * 4)
        ("(2 + 3) * 4", 20),                  # Parentheses override
        ("2 ^ 3", 8),                         # Exponentiation
        ("2 ^ 3 ^ 2", 512),                   # Right-associative: 2 ^ (3 ^ 2)
        ("2 * 3 ^ 2", 18),                    # 2 * (3 ^ 2)
        ("-5", -5),                           # Unary minus
        ("-2 * 3", -6),                       # (-2) * 3
        ("2 * -3", -6),                       # 2 * (-3)
        ("-(2 + 3)", -5),                     # Unary on expression
        ("10 / 2 / 5", 1.0),                  # Left-associative: (10 / 2) / 5
        ("2 + 3 * 4 - 5 / 2", 11.5),          # Mixed operators
        ("((2 + 3) * 4 - 1) / 3", 6.333),     # Nested parentheses
    ]
 
    print("Expression                           Result    Expected")
    print("-" * 60)
    for expr, expected in tests:
        parser = Parser(expr)
        result = parser.parse()
        status = "pass" if abs(result - expected) < 0.01 else "FAIL"
        print(f"{expr:30} = {result:8.3f}  ({expected:8.3f}) {status}")

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
