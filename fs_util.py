from fat import Fat
import sys

# test fat structure:
# 1.txt > "Hello World!"
# dir1 > 2.txt > "file 2 contents"

if __name__ == "__main__":
    if sys.argv[1] == "-info":
        if len(sys.argv) == 3 and sys.argv[2]:
            try:
                with open(sys.argv[2], "rb") as file:
                    fat = Fat(file)
                    fat.print_fs_info()
            except:
                print("Некорректный путь к файлу")
    elif sys.argv[1] == "-tree":
        if len(sys.argv) == 3 and sys.argv[2]:
            with open(sys.argv[2], "rb") as file:
                fat = Fat(file)
                fat.print_fs_tree()
    elif sys.argv[1] == "-search" and len(sys.argv) == 4:
        if sys.argv[3]:
            try:
                with open(sys.argv[3], "rb") as file:
                    fat = Fat(file)
                    fat.read_file(sys.argv[2])
            except:
                print("Некорректный путь к файлу")
