import psutil


def main():
    '''Process kill function'''
    for proc in psutil.process_iter():
        if any(procstr in proc.name() for procstr in\
            ['Adobe', 'CCXProcess', 'notepad.exe', 'Creative Cloud']):
            print(f'Killing {proc.name()}')
            proc.kill()


if __name__ == "__main__":
    main()