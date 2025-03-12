import os

this_dir = os.path.dirname(os.path.abspath(__file__))


def invoke_main():
    try:
        print(f"this_dir={this_dir}")

        dir_1 = f"{this_dir}/dir-1"
        dir_2 = f"{this_dir}/dir-2"
        dir_3 = f"{this_dir}/dir-3"
        work = f"{this_dir}/work"
        root = f"{this_dir}/root"
        result = f"{this_dir}/a-dir"

        options = f"lowerdir={dir_3}:{dir_2}:{dir_1},upperdir={root},workdir={work}"

        mount_cmd = f"mount -v -t overlay -o {options} overlay {result}"
        report_cmd = f"ls -lasR {result}"
        umount_cmd = f"umount -v {result}"

        os.system(f"sudo {mount_cmd}")
        os.system(f"sudo {report_cmd}")
        os.system(f"sudo {umount_cmd}")

    except Exception as error:
        print(f"failure: {error}")


invoke_main()
