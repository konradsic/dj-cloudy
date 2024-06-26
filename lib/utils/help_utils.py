import typing as t

commands = {}

# def register_command(
#     name: str,
#     description: str,
#     category: str,
#     arguments: t.Optional[t.List[t.Tuple[str, str, bool]]] = None
# ): 
#     """
#     Help Utils: Register Command
#     ---------------------------------------
#     Registers command with given parameters

#     Parameters
#     ---------
#     `name`: str - name of the command
#     `description`: str - description of the command
#     `category`: str - category of the command

#     `arguments`: list[tuple[str,str,bool]] - (optional) arguments of the command represented in following order: (name, description, required)
#     """
#     commands[name] = {
#         "description": description,
#         "category": category,
#     }
#     if arguments is not None:
#         commands[name]["arguments"] = {}
#         for arg in arguments:
#             commands[name]["arguments"][arg[0]] = {
#                 "description": arg[1],
#                 "required": arg[2]
#             }
#     else:
#         commands[name]["arguments"] = {}

# def get_commands():
#     """
#     Help Utils: Get Commands
#     ---------------------------------------
#     Get all registered commands
    
#     Returns
#     --------
#     `list` - a list of all commands
#     """
#     if not commands:
#         return []
#     return_commands = []
#     for command in commands:
#         dicted_command = {
#             "name": command,
#             "description": commands[command]["description"],
#             "category": commands[command]["category"]
#         }
#         if commands[command]["arguments"]:
#             dicted_command["arguments"] = commands[command]["arguments"]
#         return_commands.append(dicted_command)
#     return return_commands

def add(name, description, category, arguments={}):
    def wrapper(command):
        commands[name] = {
            "category": category,
            "description": description,
            "arguments": arguments
        }
        return command
    return wrapper

def get_by_category():
    categories = {}
    for command, data in commands.items():
        category_name = data["category"]
        # if len(command.split(" ")) == 1: category_name = "Miscellaneous"
        try: categories[category_name].append([command,data])
        except: categories[category_name] = [[command,data]]
        
    return categories
    
def get_command_cound():
    return len(commands.items())



