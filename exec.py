import sys

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
    runflag = 6

class Flag:
    fcall = 0
    bracket = 1
#


class Process:

    def __init__(self, args):
        with open(args[1], 'rb') as f:
            self.STACK = list(f.read())
        self.INSTRUCTION_PTR = 0
        self.FUNCTION_START = 0
        self.NESTING_LEVEL = 0
        self.ARGS_POSITION = len(self.STACK)
        for i in range(2, len(sys.argv)):
            if not args[i].isdigit() or int(args[i]) >= 256 or int(args[i]) < 0:
                print("only integers in range [0, 255] are supported yet")
                exit()
            self.STACK.append(Type.byte)
            self.STACK.append(int(sys.argv[i]))


    def run(self):
        #self.__debugprint()
        while (self._execNextCommand()):
            pass
            #self.__debugprint()

    def _execNextCommand(self):
        t = int(self.STACK[self.INSTRUCTION_PTR])
        v = int(self.STACK[self.INSTRUCTION_PTR + 1])
        self.INSTRUCTION_PTR += 2
        if t == Type.command:
            return self._command(v)
        elif t == Type.byte:
            self.STACK.append(t)
            self.STACK.append(v)
        elif t == Type.arg:
            t, v = self._getarg(v)
            self.STACK.append(t)
            self.STACK.append(v)
        elif t == Type.fcall:
            self.STACK.append(Type.fend)
            self.STACK.append(int(self.INSTRUCTION_PTR / 2))
            self.INSTRUCTION_PTR = 2 * v
        elif t == Type.runflag:
            print("error, cycle found")
            exit()
        return True

    def _command(self, v):
        if v == Command.newfunc:
            self.NESTING_LEVEL += 1
            if self.NESTING_LEVEL == 1:
                self.STACK.append(Type.runflag)
                self.STACK.append(Flag.fcall)
            self.FUNCTION_START = len(self.STACK) - 2
        elif v == Command.newline:
            self.STACK = self.STACK[:(self.FUNCTION_START + 2)]
        elif v == Command.ifjump:
            t, step = self._getargcmd(0)
            assert t == Type.byte
            t, boolean = self._getargcmd(1)
            assert t == Type.byte
            if (boolean != 0):
                while (True):
                    t = int(self.STACK[self.INSTRUCTION_PTR])
                    v = int(self.STACK[self.INSTRUCTION_PTR + 1])
                    if t == Type.command and v == Command.newline:
                        step -= 1
                        if step < 0:
                            break
                    elif t == Type.command and v == Command.error:
                        print("ifjump error: jump out of function")
                        exit()
                    self.INSTRUCTION_PTR += 2
        elif v == Command.plus:
            t, a = self._getargcmd(0)
            assert  t == Type.byte
            t, b = self._getargcmd(1)
            assert t == Type.byte
            assert 0 <= (a + b) < 256
            self.STACK.append(Type.byte)
            self.STACK.append(a + b)
        elif v == Command.minus:
            t, a = self._getargcmd(0)
            assert t == Type.byte
            t, b = self._getargcmd(1)
            assert t == Type.byte
            assert 0 <= (b - a) < 256
            self.STACK.append(Type.byte)
            self.STACK.append(b - a)
        elif v == Command.more:
            t, a = self._getargcmd(0)
            assert t == Type.byte
            t, b = self._getargcmd(1)
            assert t == Type.byte
            self.STACK.append(Type.byte)
            self.STACK.append(int(b > a))
        elif v == Command.endfunc:
            if self.NESTING_LEVEL == 1:
                print(self.STACK[-1])
                return False
            elif self.NESTING_LEVEL > 1:
                self.NESTING_LEVEL -= 1
            else:
                print("unknown error")
                exit()

            assert self.STACK[self.FUNCTION_START] == Type.fend
            self.INSTRUCTION_PTR = self.STACK[self.FUNCTION_START + 1] * 2

            self.STACK[self.FUNCTION_START] = self.STACK[-2]
            self.STACK[self.FUNCTION_START+1] = self.STACK[-1]
            self.STACK = self.STACK[:self.FUNCTION_START+2]

            for i in range(len(self.STACK)-2, -1, -2):
                if self.STACK[i] == Type.runflag and self.STACK[i + 1] == Flag.fcall:
                    self.FUNCTION_START = i
                    return True
                if self.STACK[i] == Type.fend:
                    self.FUNCTION_START = i
                    return True

            print("function start not found")
            exit()

        elif v == Command.open:
            self.STACK.append(Type.runflag)
            self.STACK.append(Flag.bracket)
        elif v == Command.close:
            t, value = self.STACK[-2], self.STACK[-1]
            while(True):
                if self.STACK.pop(-1) == Flag.bracket and self.STACK.pop(-1) == Type.runflag:
                    break
            self.STACK.append(t)
            self.STACK.append(value)
        else:
            print("unknown command", v)
            exit()
        return True

    def _getarg(self, i):
        t = int(self.STACK[self.FUNCTION_START - 2 * (i + 1)])
        v = int(self.STACK[self.FUNCTION_START - 2 * i - 1])
        return t, v

    def _getargcmd(self, i):
        t = self.STACK[-2 - 2*i]
        v = self.STACK[-1 - 2*i]
        return t, v

    def __debugprint(self):
        for i in range(len(self.STACK)):
            if i == self.ARGS_POSITION:
                print('|', end=' ')
            if i == self.INSTRUCTION_PTR:
                print('[', end='')
            if i == self.INSTRUCTION_PTR + 2:
                print(']', end=' ')
            if i == self.INSTRUCTION_PTR + 1:
                print(self.STACK[i], end='')
            else:
                if i >= self.ARGS_POSITION and i%2 == 0:
                    if self.STACK[i] == Type.fend:
                        print('*', end='')
                    elif self.STACK[i] == Type.runflag:
                        print('(', end='')
                else:
                    print(self.STACK[i], end=' ')
        print()



def main():
    assert len(sys.argv) >= 2
    Process(sys.argv).run()

if __name__ == "__main__":
    main()