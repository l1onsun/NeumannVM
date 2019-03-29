import sys
import re

class Command:
    newfunc = 0
    newline = 1
    ifjump = 2
    plus = 3
    minus = 4
    more = 5
    less = 6
    equal = 7
    open = 8
    close = 9
    endfunc = 10
    endprog = 11
    error = 12

class Type:
    command = 0
    fcall = 1
    fend = 2
    arg = 3
    byte = 4
    char = 5

class Compilator:
    def __init__(self, name, code):
        self.function_table = {}
        self.function_code = {}
        self.current_func = None
        self.lines = list(filter(None, re.split(r'\s*\n\s*', code)))
        self.line_index = 0
        self.main_func = None
        self.prog_name = name

        while self._handler():
            pass
        self._save()

    def _getline(self):
        if self.line_index >= len(self.lines):
            return None

        commands = re.split(r'([\(\)\s;:#])', self.lines[self.line_index])
        commands = [c for c in commands if not re.fullmatch('\s*', c)]
        for i in range(len(commands)):
            if commands[i] == '#':
                commands = commands[:i]
                break

        self.line_index += 1

        if len(commands) == 0:
            return self._getline()
        else:
            return commands

    def _addfunc(self, name):
        if (name == self.prog_name or not self.main_func):
            self.main_func = name
        self.function_table[name] = None
        self.function_code[name] = [(Type.command, Command.newfunc)]
        self.current_func = name

    def _handler(self):
        line = self._getline()
        if not line:
            return False
        if line[0] == ':':
            assert len(line) == 2
            self._addfunc(line[1])
            return True
        if not self.current_func:
            print("programm must start with function")
            exit()
        self._addcommand(Type.command, Command.newline)
        for command in line:
            if command[0] == '.':
                assert command[1:].isdigit()
                self._addcommand(Type.arg, int(command[1:]))
            elif command == '>':
                self._addcommand(Type.command, Command.more)
            elif command == '<':
                self._addcommand(Type.command, Command.less)
            elif command == '+':
                self._addcommand(Type.command, Command.plus)
            elif command == '-':
                self._addcommand(Type.command, Command.minus)
            elif command == '=':
                self._addcommand(Type.command, Command.equal)
            elif command == '^':
                self._addcommand(Type.command, Command.ifjump)
            elif command == '(':
                self._addcommand(Type.command, Command.open)
            elif command == ')':
                self._addcommand(Type.command, Command.close)
            elif command == ';':
                self._addcommand(Type.command, Command.endfunc)
            elif command in self.function_table:
                self._addcommand(Type.fcall, command)
            elif command.isdigit():
                if int(command) < 256:
                    self._addcommand(Type.byte, int(command))
                else:
                    print("integers >= 256 not supported yet")
                    exit()
            else:
                print('the command is not recognized:', command)
                exit()
        return True
    def _addcommand(self, t, v):
        self.function_code[self.current_func].append((t, v))

    def _save(self):
        byte_vector = []

        #add main func
        self.function_table[self.main_func] = 0
        for pair in self.function_code[self.main_func]:
            byte_vector.append(pair[0])
            byte_vector.append(pair[1])
        byte_vector.append(Type.command)
        byte_vector.append(Command.error)

        #add other funcs
        for f in self.function_code:
            if f == self.main_func:
                continue
            self.function_table[f] = int(len(byte_vector) / 2)
            for pair in self.function_code[f]:
                byte_vector.append(pair[0])
                byte_vector.append(pair[1])
            byte_vector.append(Type.command)
            byte_vector.append(Command.error)

        for i in range(0, len(byte_vector), 2):
            if byte_vector[i] == Type.fcall:
                byte_vector[i + 1] = self.function_table[byte_vector[i + 1]]

        with open(self.prog_name + '.bin', 'wb') as f:
            f.write(bytes(byte_vector))



def main():
    assert len(sys.argv) == 2
    name = sys.argv[1]
    with open(name) as f:
        code = f.read()
        Compilator(name, code)

if __name__ == "__main__":
    main()
