import json
import argparse
import glob
import os

from jsonschema import validate, exceptions
import yaml

## python schema_validator.py --schemafile preacher.schema.json '../test-case/**/*.yml'


# 本家 Preacher のシナリオのパーサに解釈させると一部の項目がオブジェクトになるため独自に丸めている
# タグを文字列扱いする。intelliJ での挙動に合わせる
for tag in ['argument', 'include', 'context']:
    yaml.SafeLoader.add_constructor(f'!{tag}', lambda loader, node: f'!{tag} {loader.construct_scalar(node)}')
# !relative_datetime は子要素に関わらず無理やり文字列にして intelliJ での挙動に合わせる
yaml.SafeLoader.add_constructor('!relative_datetime', lambda loader, node: '!relative_datetime')

# 日付形式の文字列を文字列に解釈する
yaml.SafeLoader.add_constructor('tag:yaml.org,2002:timestamp', lambda loader, node: loader.construct_scalar(node))
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--schemafile', required=True, help='JSON Schema のスキーマファイル')
    parser.add_argument('filepath', help='検証したい yaml ファイルパス。ワイルドカード利用の場合はシングルクォートで囲む')
    args = parser.parse_args()

    exit_status = 0

    with open(args.schemafile) as f:
        schema = json.load(f)

    for path in glob.glob(os.path.expanduser(args.filepath), recursive=True):
        try:
            with open(path) as f:
                docs = yaml.safe_load_all(f)
                for doc in docs:
                    try:
                        validate(instance=doc, schema=schema)
                        # print(f'OK: {path}')
                    except exceptions.ValidationError as e:
                        print(f'NG: {path}')
                        print(e.json_path)
                        print(e.message)
                        exit_status = 1
        except Exception as e:
            print(f'NG: {path}')
            print(e)
            exit_status = 1
    
    return exit_status

if __name__ == '__main__':
    exit_status = main()
    exit(exit_status)

