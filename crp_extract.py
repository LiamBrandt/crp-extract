import argparse
import os
import json

from formatter import get_formatted_data
from formatter import get_raw
from formatter import unpack

# Safely make directories necessary to save something at the given path
def make_directories_for(path):
    path = os.path.dirname(path)
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == os.errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def argparse_valid_directory_type(value):
    abs_path = os.path.abspath(value)
    if not os.path.isdir(abs_path):
        raise argparse.ArgumentTypeError("{0} is not a valid directory".format(abs_path))
    return abs_path

# Return a string from the file
def string_at(file, offset, size):
    file.seek(offset)
    return unpack(file, "s", size).decode("utf-8", "ignore")

# Slice part of the given file and write it to file at the given path
def slice_and_write_file(file, offset, size, path):
    make_directories_for(path)
    write_file = open(path, "wb")
    write_file.truncate()

    file.seek(offset)
    write_file.write(file.read(size))
    write_file.close()

# Return the relative offset from the offset in the file of the first sequence
# of bytes that match. Return None if there is no matching sequence.
def first_sequence(file, offset, sequence, exactly_first=False):
    file.seek(offset)
    index = 0
    while(True):
        value = unpack(file, "B")
        # Next byte matches
        if value == sequence[index]:
            index += 1
            # We read the whole sequence so return the offset from the offset
            if index == len(sequence):
                return file.tell() - offset - len(sequence)
        # Next byte does not match
        else:
            # Try this byte one more time from the start of the sequence if
            # we were in the middle before.
            if index != 0:
                index = 0
                file.seek(-1, os.SEEK_CUR)
        # If we are searching for the sequence exactly at the start and it
        # is not at the exact start then return None.
        if exactly_first and file.tell() - offset > len(sequence):
            return None
        # TODO: handle hitting the end of the file and returning None

def main():
    parser = argparse.ArgumentParser(description="Unpack Colossal Raw Package (.crp) files")
    parser.add_argument("file", type=argparse.FileType("rb"),
                        help="The file to unpack")
    parser.add_argument("--output-dir", type=argparse_valid_directory_type, default=".",
                        help="The directory to put the unpacked files into (Default: current working directory)")
    args = parser.parse_args()

    file_name = args.file.name
    file = args.file

    data = get_formatted_data(file, "crp", "crp")

    name_of_mod = get_raw(data.get("name_of_mod", ""), file)
    # If there is no mod name default to the file name
    if name_of_mod == "":
        name_of_mod = file_name[:-4]
    output_path = os.path.join(args.output_dir, name_of_mod.decode('utf-8'))

    end_header_offset = get_raw(data["end_header_offset"], file)

    metadata = {}

    # Go through each file from the header
    for file_header in data["file_headers"]:
        file_name = get_raw(file_header["file_name"], file).decode('utf-8')
        offset_from_header = get_raw(file_header["offset_from_header"], file)
        file_size = get_raw(file_header["file_size"], file)

        file_offset = offset_from_header + end_header_offset

        # Try to read a special descriptive string at the start of the file
        file.seek(file_offset)
        try:
            id_string = str(unpack(file, "s", 48)).lower()
        except:
            id_string = ""

        # Check for PNG header at start of file
        is_png = first_sequence(
            file,
            file_offset,
            [137, 80, 78, 71, 13, 10, 26, 10],
            exactly_first=True
        )

        # DDS
        if "unityengine.texture2d" in id_string:
            file_path = os.path.join(output_path, file_name + '.dds')
            relative_offset = first_sequence(file, file_offset, [68, 68, 83, 32])
            # Slice starting at "DDS "
            slice_and_write_file(
                file,
                file_offset + relative_offset,
                file_size - relative_offset,
                file_path
            )
            metadata[file_path] = string_at(file, file_offset, relative_offset)
        # PNG
        elif "icolossalframework.importers.image" in id_string or is_png:
            file_path = os.path.join(output_path, file_name + '.png')
            relative_offset = first_sequence(file, file_offset, [137, 80, 78, 71])
            # Slice starting at PNG header
            slice_and_write_file(
                file,
                file_offset + relative_offset,
                file_size - relative_offset,
                file_path
            )
            metadata[file_path] = string_at(file, file_offset, relative_offset)
        # Other
        else:
            slice_and_write_file(
                file,
                file_offset,
                file_size,
                os.path.join(output_path, file_name)
            )

    # Save the metadata dictionary as json
    meta_path = os.path.join(output_path, "metadata.json")
    make_directories_for(meta_path)
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=4, sort_keys=True)

if __name__ == '__main__':
    main()
