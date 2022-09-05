# Changelog for UE_tools repository

## 0.0.3 ##
* Refactor to include ros2 lib build scripts #7

## 0.0.2 ##
CodeGeneratorFromPath.py
* Remove all '_' in outputted UE struct type name
* Add `is_valid_group_name()` before assigning `types_cpp[group_name]` to `info[~Types, ~SetFromROS2, SetROS2]`
* `templates/Action.h, Msg.h, Srv.h` No underscore in UE struct name
* `get_var_names()` -> `get_ue_var_names`() returns a dict {(type, size):var_name}
* `convert_to_cpp_type()` -> `convert_to_ue_type()`: add TArray output
* Add `get_type_default_value_str()` to auto fill-in default value if possible

## 0.0.1 ##
* Add CHANGELOG
* Update maintainers
