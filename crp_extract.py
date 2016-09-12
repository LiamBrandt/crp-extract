import os
import json

from formatter import get_formatted_data
from formatter import get_raw
from formatter import unpack

def main():
    file_name = raw_input("FILE NAME: ")
    bin_file = open(file_name, "rb")

    data = get_formatted_data(bin_file, "crp", "crp")

    name_of_mod = get_raw(data["name_of_mod"], bin_file)
    if name_of_mod == "":
        name_of_mod = file_name[:-4]
    output_path = "./" + name_of_mod + "/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    end_header_offset = get_raw(data["end_header_offset"], bin_file)

    metadata = {}

    #go through each file found
    for file_header in data["file_headers"]:
        file_name = get_raw(file_header["file_name"], bin_file)
        offset_from_header = get_raw(file_header["offset_from_header"], bin_file)
        file_size = get_raw(file_header["file_size"], bin_file)

        #absolute_offset = offset_from_header+end_header_offset+1
        absolute_offset = offset_from_header+end_header_offset

        bin_file.seek(absolute_offset)
        try:
            id_string = unpack(bin_file, "s", 48).lower()
        except:
            id_string = ""

        #manually search for PNG header in data
        png_header = [137, 80, 78, 71, 13, 10, 26, 10]
        bin_file.seek(absolute_offset)
        found_header = True
        for i in range(8):
            if unpack(bin_file, "B") != png_header[i]:
                found_header = False

        #TEXTURE2D
        if "unityengine.texture2d" in id_string:
            print("found texture2d")
            bin_file.seek(absolute_offset)

            dds_string = ""
            #find "DDS " in the file to mark the start of the dds
            while(True):
                value = unpack(bin_file, "B")
                if value == 68:
                    dds_string += "D"
                elif value == 83:
                    dds_string += "S"
                elif value == 32:
                    dds_string += " "
                else:
                    dds_string = ""

                if dds_string == "DDS ":
                    dds_offset = bin_file.tell()-4

                    meta_offset = absolute_offset
                    meta_size = dds_offset - absolute_offset

                    final_path = output_path + file_name + ".dds"
                    final_offset = dds_offset
                    final_size = file_size - meta_size
                    break

        #STEAM PREVIEW PNG (AND RANDOM PNGS)
        elif "icolossalframework.importers.image" in id_string or found_header:
            print("found png")
            bin_file.seek(absolute_offset)

            png_string = ""
            #find "PNG" in the file to mark the start of the png
            while(True):
                value = unpack(bin_file, "B")
                if value == 137:
                    png_string += "89"
                elif value == 80:
                    png_string += "50"
                elif value == 78:
                    png_string += "4E"
                elif value == 71:
                    png_string += "47"
                else:
                    png_string = ""

                if png_string == "89504E47":
                    png_offset = bin_file.tell()-4

                    meta_offset = absolute_offset
                    meta_size = png_offset - absolute_offset

                    final_path = output_path + file_name + ".png"
                    final_offset = png_offset
                    final_size = file_size - meta_size
                    break

        #GENERIC
        else:
            print("found generic")
            meta_offset = absolute_offset
            meta_size = 0

            final_path = output_path + file_name
            final_offset = absolute_offset
            final_size = file_size


        #add metadata to the metadata dictionary
        if meta_size == 0:
            metadata[final_path] = ""
        else:
            bin_file.seek(meta_offset)
            metadata[final_path] = unpack(bin_file, "s", meta_size).decode('utf-8','ignore').encode("utf-8")

        #write file
        write_file = open(final_path, "wb")
        write_file.truncate()

        bin_file.seek(final_offset)
        write_file.write(bin_file.read(final_size))
        write_file.close()

    #save the metadata dictionary using json
    with open(output_path + "metadata.json", "w") as f:
        json.dump(metadata, f, indent=4, sort_keys=True)

main()
