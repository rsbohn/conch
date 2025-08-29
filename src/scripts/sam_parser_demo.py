import conch.sam

sam = conch.sam.Sam()
while True:
    command = input("Enter a Sam command: ")
    if command == "exit":
        break
    try:
        if sam.is_sam_command(command):
            result = sam.parse_command(command, (1, 1))
            if result[1] == "s":
                delimiter = result[2][0]
                result = (result[0], result[1], result[2].split(delimiter))
            print("command:", result)
        else:
            print(f"append: {command}")
    except conch.sam.SamParseError as e:
        print("Error:", e)
