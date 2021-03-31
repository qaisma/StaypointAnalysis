import enum
import inspect


    # Using enum class create enumerations
class Classes(enum.Enum):
    Individual_StayPoint = 1
    Trajectory = 2
    Point = 3

class TableNames(enum.Enum):
    staypoint = 'public.staypoint'
    staypoint_experiment = 'staypoint.staypoint_experiment'

# this function will return the list of attributes only as a list of strings
def GetClassMembers(ttype):
    result = []
    for i in inspect.getmembers(ttype):
    # to remove private and protected
    # functions
        if not i[0].startswith('_'):
        # to remove other methods that
        # does not start with a underscore
            if not inspect.ismethod(i[1]):
                result.append(i[0])
    return result

        
def GetClassMembersCommaSeperated(ttype):
    return ','.join(GetClassMembers(ttype))

def CalculateMean(numbers):
    sum = 0
    for t in numbers:
        sum = sum + t

    avg = sum / len(numbers)
    return avg