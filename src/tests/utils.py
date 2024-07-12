def py_func_str(name: str, args: list):
    return f'def {name}({", ".join(args)}):\n   raise NotImplementedError\n\n\n'