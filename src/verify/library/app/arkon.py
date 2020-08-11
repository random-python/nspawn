import os
import sys
import errno

master_key = "NSPAWN_MASTER_PROCESS"

master_main = os.path.abspath(__file__)


def invoke_main():
    try:
        args = [sys.executable] + [master_main] + sys.argv
        print(args)
        os.execlp(args[0], *args)
    except OSError as e:
        sys.exit('Invoker failure')


def master_ensure():
    
    master_value = os.environ.get(master_key)
    print(f"master_ensure={master_value}")
    
    if master_value:
        print("YES")
    else:
        print("NO")
        os.environ[master_key] = 'MASTER'
        invoke_main()
        

master_ensure()
