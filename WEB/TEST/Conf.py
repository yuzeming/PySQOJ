WebServer= 'http://127.0.0.1:8000/xmlrpc'

CompileConf={
    "cpp":["g++ $(SRC) -O2 -o $(EXE)","$(EXE)","cpp"],
    "pas":["fpc $(SRC) -O2 -o $(EXE)","$(EXE)","pas"],
}

CompileLimits=[10,128*1024*1024] # Sec Byte

JudgeKey="judge1"
