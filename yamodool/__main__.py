import sys

from .yamodool import YAModool


def main():
    file_path = sys.argv[1]
    yamodool = YAModool(file_path)
    yamodool.parse_yml_data()
    print(yamodool.yml_data)


main()
