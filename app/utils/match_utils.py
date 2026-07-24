
# 匹配返回结果
def match_result(result, new_result):
    for key in ["project", "customer", "sample", "material"]:
        if key in result and isinstance(result.get(key), dict):
            current_value = getattr(new_result, key)
            if hasattr(current_value, "dict"):
                current_dict = current_value.dict()
                current_dict.update(result[key])
                # 重新赋值
                setattr(new_result, key, type(current_value)(**current_dict))
            else:
                # 直接赋值（如果类型匹配）
                setattr(new_result, key, result[key])

    # 覆盖顶层字段
    for key in ["need_clarification", "clarification_question", "extracted_info"]:
        if key in result:
            setattr(new_result, key, result[key])