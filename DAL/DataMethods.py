import Utilities
from DAL import DbConnector

# returns all objects of a selected class type from database
def GetAll(ttype, TableName):
    result = []
    attrNames = Utilities.GetClassMembersCommaSeperated(ttype)
    query = 'SELECT {0} FROM {1};'.format(attrNames, TableName.value[0])
    rows = DbConnector.ExecuteQuery(query)
    # creating objects from the required class and assigning attribute values from rows
    for row in rows:
        i = 0
        classObject = ttype()
        for attributeName in attrNames.split(','):
            setattr(classObject, attributeName, row[i])
        result.append(classObject)
    return result

# this function will return the objects from DB using search criteria
def Search(ttype, tableName, searchConditions):
    # searchConditions param is a list of tubles. these tubles are constructed as follows:
    # searchCondition[0]: column name, searchConditions[1]: operator (in, =, <, >...), searchConditions[2]: value
    result = []
    attrNames = Utilities.GetClassMembersCommaSeperated(ttype)
    conditions = ''
    for i in range(0, len(searchConditions)):
        searchcondition = searchConditions[i]
        if(i == 0):
            conditions += searchcondition[0] + ' ' + \
                searchcondition[1] + ' ' + searchcondition[2]
        else:
            conditions += ' and ' + \
                searchcondition[0] + ' ' + \
                searchcondition[1] + ' ' + searchcondition[2]
    query = 'select {0} from {1} where {2}'.format(
        attrNames, tableName, conditions)

    rows = []
    
    rows = DbConnector.ExecuteQuery(query)

    # creating objects from the required class and assigning attribute values from rows
    if(rows is not None and len(rows) > 0):
        for i in range(len(rows)):
            classObject = ttype()
            row = rows[i]
            for j in range(len(attrNames.split(','))):
                setattr(classObject, attrNames.split(',')[j], row[j])
            result.append(classObject)
    return result
