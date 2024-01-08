from constants.objectives.conditions import ConditionType

class ObjectiveConditionMetadata:
    def __init__(self, id, condition: ConditionType):
        self.id = id
        self.condition = condition

    def to_json(self):
        fn = self.condition.string_function
        value_descriptions = []
        # Call the string_function for each value specified to get the corresponding name of the check
        # For example, Characters will loop through 1..14 and generate value_descriptions like the following:
        # "value_descriptions": [
        #     "Recruit 1 Characters",
        #     "Recruit 2 Characters",
        #     "Recruit 3 Characters",
        #     "Recruit 4 Characters",
        #     "Recruit 5 Characters",
        #     "Recruit 6 Characters",
        #     "Recruit 7 Characters",
        #     "Recruit 8 Characters",
        #     "Recruit 9 Characters",
        #     "Recruit 10 Characters",
        #     "Recruit 11 Characters",
        #     "Recruit 12 Characters",
        #     "Recruit 13 Characters",
        #     "Recruit 14 Characters"
        # ],
        for value in (self.condition.value_range or []):
            if value == "r":
                value_descriptions.append('Random')
            elif hasattr(fn, '__call__'):
                value_descriptions.append(fn(value))
            else:
                value_descriptions.append(value)
        # Call the result_exception method for each value specified to get the corresponding list of exceptions for the check
        result_exceptions = []
        result_exception_fn = self.condition.result_exceptions
        for value in (self.condition.value_range or []):
            if value == "r":
                result_exceptions.append([]) # TODO: figure out how to handle exceptions for Random
            elif hasattr(result_exception_fn, '__call__'): # the result_exception is a function (like the lambdas for check_bit and quest_bit). Call it
                result_exceptions.append(result_exception_fn(value))
            else: # The "result_exceptions" for this condition are expected to be a list itself. Just use it as-is
                result_exceptions.append(result_exception_fn)
        return {
            'id': self.id,
            'condition_type_name': self.condition.name,
            'value_range': getattr(self.condition, 'value_range', None),
            'value_descriptions': value_descriptions,
            'range': self.condition.min_max,
            'result_exceptions': result_exceptions,
        }
