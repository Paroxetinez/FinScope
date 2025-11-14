import os
import fnmatch

def load_gitignore(root_dir):
    """加载 .gitignore 文件并返回忽略的模式列表"""
    gitignore_path = os.path.join(root_dir, '.gitignore')
    if not os.path.exists(gitignore_path):
        return []
    
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        patterns = f.read().splitlines()
    
    # 添加额外的忽略模式
    additional_patterns = ['node_modules/', '__pycache__/', '.vite/']
    patterns.extend(additional_patterns)
    
    return patterns

def is_ignored(path, patterns, root_dir):
    """检查路径是否匹配 .gitignore 中的模式"""
    relative_path = os.path.normpath(os.path.relpath(path, start=root_dir))
    for pattern in patterns:
        # 规范化模式
        normalized_pattern = os.path.normpath(pattern)
        if fnmatch.fnmatch(relative_path, normalized_pattern):
            print(f"Ignoring {relative_path} due to pattern {normalized_pattern}")  # 调试信息
            return True
    return False

def generate_directory_tree(root_dir, prefix='', depth=0, max_depth=3, file=None, patterns=None):
    """生成目录树并写入文件"""
    if depth > max_depth:
        return
    
    try:
        entries = sorted(os.listdir(root_dir))
    except PermissionError:
        if file:
            file.write(prefix + os.path.basename(root_dir) + " [Permission Denied]\n")
        else:
            print(prefix + os.path.basename(root_dir) + " [Permission Denied]")
        return
    
    for index, entry in enumerate(entries):
        path = os.path.join(root_dir, entry)
        
        # 忽略 .git 目录
        if os.path.basename(path) == '.git':
            continue
        
        # 忽略 .gitignore 中的文件和目录
        if patterns and is_ignored(path, patterns, root_dir):
            continue
        
        if os.path.isdir(path):
            if file:
                file.write(prefix + entry + '/\n')
            else:
                print(prefix + entry + '/')
            if index == len(entries) - 1:
                generate_directory_tree(path, prefix + '    ', depth + 1, max_depth, file, patterns)
            else:
                generate_directory_tree(path, prefix + '│   ', depth + 1, max_depth, file, patterns)
        else:
            if file:
                file.write(prefix + entry + '\n')
            else:
                if index == len(entries) - 1:
                    print(prefix + entry)
                else:
                    print(prefix + entry)

if __name__ == '__main__':
    project_root = '.'  # 你可以在这里指定项目根目录，例如 '/path/to/your/project'
    output_file = 'directory_tree.txt'  # 输出文件名
    max_depth = 3  # 设置最大深度
    print(f"Generating directory tree (max depth {max_depth}) and saving to {output_file}")
    
    patterns = load_gitignore(project_root)
    
    with open(output_file, 'w', encoding='utf-8') as file:
        generate_directory_tree(project_root, max_depth=max_depth, file=file, patterns=patterns)