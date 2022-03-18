import os
import zipfile


def walk_directory(path, endpoint='.py'):
    """

    Args:
        path: Directory path
        endpoint:

    Returns: The list of all files' path in the directory

    """
    file_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith(endpoint):
                file_list.append(file_path)
    return file_list


def get_file_list(source, endpoint='.py'):
    """

    Args:
        endpoint:file_name's endswith
        source:file_name which can be directory, file, zip

    Returns:

    """
    if isinstance(source, str):
        if os.path.isdir(source):
            return walk_directory(source)
        elif source.endswith('.py'):
            return [source]
        elif source.endswith(('.zip', '.rar', '.7z')):
            file_zip = zipfile.ZipFile(source, 'r', zipfile.ZIP_DEFLATED)
            py_files = [py_file for py_file in file_zip.namelist() if py_file.endswith(endpoint)]
            file_zip.extractall(path=os.path.dirname(source), members=py_files)
            return [os.path.dirname(source) + "/" + py_file for py_file in py_files]

    # TODO Add the situation that source is a url or a cache
    else:
        raise ValueError("The parameter source is not supported")


if __name__ == '__main__':
    get_file_list("/Users/liufan/program/PYTHON/SAP/restructure/Test/PrivacyScanTest.7z")
