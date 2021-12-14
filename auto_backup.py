import argparse
import gzip
import os
import shutil
import sys
import threading


def parse_input():
    """
    Argument Parsing function, for parsing CLI.
    Returns: pars_args()

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-t','--target',nargs=1,required=True,help='Target Backup folder')
    parser.add_argument('-s','--source',nargs='+',required=True, help='Source Files to be added')
    parser.add_argument('-c','--compress',nargs=1,type=int,help='Gzip threshold in bytes, Default 1024KB',default=[1024000])

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    return parser.parse_args()


def size_if_newer(source, target):
    """
    If there is a difference in size, this function reports the difference.
    Args:
        source: Source Path
        target: Target for ZIP file

    Returns: The Size difference
    """
    src_stat = os.stat(source)
    try:
        target_ts = os.stat(target).st_mtime
    except FileNotFoundError:
        try:
            target_ts = os.stat(target + '.gz').st_mtime
        except FileNotFoundError:
            target_ts = 0
    return src_stat.st_size if (src_stat.st_mtime - target_ts > 1) else False


def threaded_sync_file(source, target, compress):
    """
    Multithreading for synced files.
    Args:
        source: Source Path
        target: Target for ZIP file
        compress: The compression threshold

    Returns: The threads
    """
    size = size_if_newer(source, target)
    if size:
        thread = threading.Thread(target=transfer_file,args=(source, target, size > compress))
        thread.start()
        return thread


def sync_file(source, target, compress):
    """
    Synchronizing files
    Args:
        source: Source Path
        target: Target for ZIP file
        compress: The compression Threshold
    """
    size = size_if_newer(source, target)

    if size:
        transfer_file(source, target, size > compress)

def transfer_file(source, target, compress):
    """
    Transferring files
    Args:
        source: Source Path
        target: Target for ZIP file
        compress: The compression Threshold
    """
    try:
        if compress:
            with gzip.open(target + '.gz', 'wb') as target_fid:
                with open(source, 'rb') as source_fid:
                    target_fid.writelines(source_fid)
            print('Compress {}'.format(source))
        else:
            shutil.copy2(source, target)
            print('Copy {}'.format(source))
    except FileNotFoundError:
        os.makedirs(os.path.dirname(target))
        transfer_file(source, target, compress)


def sync_root(root, arg):
    """
    Synchronize Root with Target
    
    """
    target = arg.target[0]
    compress = arg.compress[0]
    threads = []

    for path,_,files in os.walk(root):
        for source in files:
            source = path + '/' + source
            threads.append(threaded_sync_file(source, target+source, compress))
    for thread in threads:
        thread.join()


if __name__ == '__main__':
    arg = parse_input()
    print('-------------------------Start Copy-------------------------')
    print('____________________________________________________________')    
    for root in arg.source:
        sync_root(root, arg)
    print('____________________________________________________________')
    print('-------------------------Done Done!-------------------------')
    