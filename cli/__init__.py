import argparse

parser = argparse.ArgumentParser(description='GMS: an interpretor')
parser.add_argument('-i', help='交互模式', required=False, nargs='?')
parser.add_argument('filepath', default=None, help='文件路径', nargs='?')
parser.add_argument('-p', '--prettyprint', action='store_true', default=False, help='仅打印代码')
parser.add_argument('-c', '--check', action='store_true', default=False, help='仅静态检查')
parser.add_argument('-g', '--graph', action='store_true', default=False, help='打印ast(mermaid)')
parser.add_argument('--scope', default=False, action='store_true', help='打印出名字作用域')
args = parser.parse_args()
