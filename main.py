import re
import sys

# ============================================================================
# Tokenizer
# ============================================================================

def tokenize(code):
    """將輸入字串轉換為 token 串列"""
    tokens = []
    i = 0
    
    while i < len(code):
        # 跳過空白字符
        if code[i] in ' \t\n\r':
            i += 1
            continue
        
        # 跳過註解
        if code[i] == ';':
            while i < len(code) and code[i] != '\n':
                i += 1
            continue
        
        # 括號
        if code[i] in '()':
            tokens.append(code[i])
            i += 1
            continue
        
        # Boolean
        if i + 1 < len(code) and code[i:i+2] in ['#t', '#f']:
            tokens.append(code[i:i+2])
            i += 2
            continue
        
        # 負數或減號
        if code[i] == '-':
            if i + 1 < len(code) and code[i+1].isdigit():
                # 負數
                j = i + 1
                while j < len(code) and code[j].isdigit():
                    j += 1
                tokens.append(code[i:j])
                i = j
            else:
                # 減號運算子
                tokens.append('-')
                i += 1
            continue
        
        # 正數
        if code[i].isdigit():
            j = i
            while j < len(code) and code[j].isdigit():
                j += 1
            tokens.append(code[i:j])
            i = j
            continue
        
        # ID 或運算子
        if code[i].isalpha() or code[i] in '+*/<>=':
            j = i
            # 單字符運算子
            if code[i] in '+*/<>=' and (i + 1 >= len(code) or code[i+1] in ' \t\n\r()'):
                tokens.append(code[i])
                i += 1
                continue
            # ID: letter (letter | digit | '-')*
            while j < len(code) and (code[j].isalnum() or code[j] == '-'):
                j += 1
            tokens.append(code[i:j])
            i = j
            continue
        
        # 其他字符跳過
        i += 1
    
    return tokens

# ============================================================================
# Parser
# ============================================================================

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
    
    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    
    def consume(self):
        token = self.peek()
        self.pos += 1
        return token
    
    def parse_program(self):
        """PROGRAM ::= STMT+"""
        stmts = []
        while self.peek() is not None:
            stmts.append(self.parse_stmt())
        return ('program', stmts)
    
    def parse_stmt(self):
        """STMT ::= EXP"""
        return self.parse_exp()
    
    def parse_exp(self):
        """EXP ::= bool-val | number | VARIABLE | (...)"""
        token = self.peek()
        
        if token is None:
            raise SyntaxError("syntax error")
        
        # Boolean literals
        if token in ['#t', '#f']:
            self.consume()
            return token == '#t'
        
        # Number literals
        if token.lstrip('-').isdigit():
            self.consume()
            return int(token)
        
        # S-expression
        if token == '(':
            self.consume()
            return self.parse_sexp()
        
        # Variable
        if re.match(r'^[a-z][\w-]*$', token):
            self.consume()
            return ('var', token)
        
        raise SyntaxError("syntax error")
    
    def expect(self, expected):
        """消耗並檢查 token"""
        token = self.consume()
        if token != expected:
            raise SyntaxError("syntax error")
    
    def parse_sexp(self):
        """解析 S-expression (已消耗左括號)"""
        op = self.peek()
        
        if op is None or op == ')':
            raise SyntaxError("syntax error")
        
        # Print
        if op in ['print-num', 'print-bool']:
            self.consume()
            exp = self.parse_exp()
            self.expect(')')
            return (op, exp)
        
        # Define
        if op == 'define':
            self.consume()
            var = self.consume()
            if not var or not re.match(r'^[a-z][\w-]*$', var):
                raise SyntaxError("syntax error")
            value = self.parse_exp()
            self.expect(')')
            return ('define', var, value)
        
        # Function
        if op == 'fun':
            self.consume()
            self.expect('(')
            
            params = []
            while self.peek() != ')':
                param = self.consume() 
                if not param or not re.match(r'^[a-z][\w-]*$', param):
                    raise SyntaxError("syntax error")
                params.append(param)
            self.expect(')')
            
            # nested function: fun-body ::= def-stmt* exp
            body_defs = []
            while self.peek() == '(':
                saved = self.pos
                self.consume()
                if self.peek() == 'define':
                    self.pos = saved
                    body_defs.append(self.parse_exp())
                else:
                    self.pos = saved
                    break
            
            body = self.parse_exp()
            self.expect(')')
            
            if body_defs:
                return ('fun', params, ('fun-body', body_defs, body))
            return ('fun', params, body)
        
        # If
        if op == 'if':
            self.consume()
            test = self.parse_exp()
            then_exp = self.parse_exp()
            else_exp = self.parse_exp()
            self.expect(')')
            return ('if', test, then_exp, else_exp)
        
        # Arithmetic operators
        if op in ['+', '*']:
            self.consume()
            exps = []
            while self.peek() != ')':
                exps.append(self.parse_exp())
            self.expect(')')
            if len(exps) < 2:
                raise SyntaxError("syntax error")
            return (op, exps)
        
        if op in ['-', '/', 'mod']:
            self.consume()
            exp1 = self.parse_exp()
            exp2 = self.parse_exp()
            self.expect(')')
            return (op, [exp1, exp2])
        
        # Comparison operators
        if op == '=':
            self.consume()
            exps = []
            while self.peek() != ')':
                exps.append(self.parse_exp())
            self.expect(')')
            if len(exps) < 2:
                raise SyntaxError("syntax error")
            return (op, exps)
        
        if op in ['>', '<']:
            self.consume()
            exp1 = self.parse_exp()
            exp2 = self.parse_exp()
            self.expect(')')
            return (op, [exp1, exp2])
        
        # Logical operators
        if op in ['and', 'or']:
            self.consume()
            exps = []
            while self.peek() != ')':
                exps.append(self.parse_exp())
            self.expect(')')
            if len(exps) < 2:
                raise SyntaxError("syntax error")
            return (op, exps)
        
        if op == 'not':
            self.consume()
            exp = self.parse_exp()
            self.expect(')')
            return ('not', exp)
        
        # Function call: (func args...)
        func = self.parse_exp()
        args = []
        while self.peek() != ')':
            args.append(self.parse_exp())
        self.expect(')')
        return ('call', func, args)

# ============================================================================
# Runtime
# ============================================================================

class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent
    
    def define(self, name, value):
        if name in self.vars:
            raise RuntimeError(f"Redefining variable: {name}")
        self.vars[name] = value
    
    def lookup(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.lookup(name)
        raise RuntimeError(f"Undefined variable: {name}")

class Function:
    def __init__(self, params, body, closure_env):
        self.params = params
        self.body = body
        self.closure_env = closure_env
    
    def call(self, args):
        if len(args) != len(self.params):
            raise RuntimeError(f"Arity mismatch: expected {len(self.params)}, got {len(args)}")
        
        local_env = Environment(parent=self.closure_env)
        for param, arg in zip(self.params, args):
            local_env.define(param, arg)
        
        return evaluate(self.body, local_env)

# ============================================================================
# Evaluator
# ============================================================================

# Type checking 開關 
TYPE_CHECKING = True

def type_error(expected, got):
    """印出 type error 並結束程式"""
    print("Type error!")
    sys.exit(0)  # 正常結束，不是錯誤

def check_number(val, op):
    """檢查是否為 number ( bool 是 int 的子類 )"""
    if TYPE_CHECKING:
        if isinstance(val, bool):  # bool 要先檢查
            type_error('number', val)
        if not isinstance(val, int):
            type_error('number', val)

def check_boolean(val, op):
    """檢查是否為 boolean"""
    if TYPE_CHECKING:
        if not isinstance(val, bool):
            type_error('boolean', val)

def evaluate(expr, env):
    """評估表達式"""
    # Literals
    if isinstance(expr, (bool, int)):
        return expr
    
    if not isinstance(expr, tuple):
        raise RuntimeError(f"Invalid expression: {expr}")
    
    op = expr[0]
    
    # Variable
    if op == 'var':
        return env.lookup(expr[1])
    
    # Print
    if op == 'print-num':
        value = evaluate(expr[1], env)
        check_number(value, 'print-num')
        print(value)
        return value
    
    if op == 'print-bool':
        value = evaluate(expr[1], env)
        check_boolean(value, 'print-bool')
        print('#t' if value else '#f')
        return value
    
    # Define
    if op == 'define':
        value = evaluate(expr[2], env)
        env.define(expr[1], value)
        return value
    
    # Function
    if op == 'fun':
        # params, body, closure_env
        return Function(expr[1], expr[2], env)
    
    # Function body with nested defines
    if op == 'fun-body':
        for def_stmt in expr[1]:
            evaluate(def_stmt, env)
        return evaluate(expr[2], env)
    
    # If
    # if cond then else
    if op == 'if':
        test = evaluate(expr[1], env)
        check_boolean(test, 'if')
        return evaluate(expr[2] if test else expr[3], env)
    
    # Arithmetic
    # +, * 因為可以多參數，所以不一樣
    if op == '+':
        result = 0
        for e in expr[1]:
            val = evaluate(e, env)
            check_number(val, '+')
            result += val
        return result
    
    if op == '-':
        vals = [evaluate(e, env) for e in expr[1]]
        check_number(vals[0], '-')
        check_number(vals[1], '-')
        return vals[0] - vals[1]
    
    if op == '*':
        result = 1
        for e in expr[1]:
            val = evaluate(e, env)
            check_number(val, '*')
            result *= val
        return result
    
    if op == '/':
        vals = [evaluate(e, env) for e in expr[1]]
        check_number(vals[0], '/')
        check_number(vals[1], '/')
        return vals[0] // vals[1]
    
    if op == 'mod':
        vals = [evaluate(e, env) for e in expr[1]]
        check_number(vals[0], 'mod')
        check_number(vals[1], 'mod')
        return vals[0] % vals[1]
    
    # Comparison
    if op == '>':
        vals = [evaluate(e, env) for e in expr[1]]
        check_number(vals[0], '>')
        check_number(vals[1], '>')
        return vals[0] > vals[1]
    
    if op == '<':
        vals = [evaluate(e, env) for e in expr[1]]
        check_number(vals[0], '<')
        check_number(vals[1], '<')
        return vals[0] < vals[1]
    
    if op == '=':
        vals = [evaluate(e, env) for e in expr[1]]
        for v in vals:
            check_number(v, '=')
        return all(v == vals[0] for v in vals)
    
    # Logical
    if op == 'and':
        for e in expr[1]:
            val = evaluate(e, env)
            check_boolean(val, 'and')
            if not val:
                return False
        return True
    
    if op == 'or':
        for e in expr[1]:
            val = evaluate(e, env)
            check_boolean(val, 'or')
            if val:
                return True
        return False
    
    if op == 'not':
        val = evaluate(expr[1], env)
        check_boolean(val, 'not')
        return not val
    
    # Function call
    if op == 'call':
        func = evaluate(expr[1], env)
        if not isinstance(func, Function):
            raise RuntimeError(f"Not a function")
        args = [evaluate(arg, env) for arg in expr[2]]
        return func.call(args)
    
    raise RuntimeError(f"Unknown operation: {op}")

# ============================================================================
# Main
# ============================================================================

def main():
    # 讀取輸入
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()
    
    try:
        tokens = tokenize(code)
        parser = Parser(tokens)
        ast = parser.parse_program()
        
        env = Environment()
        for stmt in ast[1]:
            evaluate(stmt, env)
    except SyntaxError:
        print("syntax error")
    except Exception as e:
        # Debug: 可以 uncomment 下面這行看錯誤訊息
        # print(f"Error: {e}", file=sys.stderr)
        pass

if __name__ == '__main__':
    main()