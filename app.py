from flask import Flask, jsonify, request
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

app = Flask(__name__)

uri = os.getenv("URI")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
driver = GraphDatabase.driver(uri, auth=(username, password), database="neo4j")

# Task 3 finished
def get_emp(tx):
    query = "MATCH (m:Employee) RETURN m"
    results = tx.run(query).data()
    return [{"employee": result['m']} for result in results]

@app.route('/employees', methods=['GET'])
def get_employees():
    with driver.session() as session:
        results = session.execute_read(get_emp)
        response = {'result': results}
        return jsonify(response)

# Task 3 extended finished
def get_emp_prop(tx, prop):
    prop_tab = prop.split("=")
    if prop_tab[0] == "firstname":
        query = "MATCH (m:Employee) WHERE m.firstname CONTAINS $prop2 RETURN m"
        results = tx.run(query, prop2=prop_tab[1]).data()
        return [{"employee": result['m']} for result in results]
    elif prop_tab[0] == "lastname":
        query = "MATCH (m:Employee) WHERE m.lastname CONTAINS $prop2 RETURN m"
        results = tx.run(query, prop2=prop_tab[1]).data()
        return [{"employee": result['m']} for result in results]
    elif prop_tab[0] == "position":
        query = "MATCH (m:Employee) WHERE m.position CONTAINS $prop2 RETURN m"
        results = tx.run(query, prop2=prop_tab[1]).data()
        return [{"employee": result['m']} for result in results]
    elif prop_tab[0] == "salary":
        query = "MATCH (m:Employee) WHERE m.salary = $prop2 RETURN m"
        results = tx.run(query, prop2=int(prop_tab[1])).data()
        return [{"employee": result['m']} for result in results]
    elif prop_tab[0] == "orderbyAsc":
        query = "MATCH (m:Employee) RETURN m ORDER BY m[$prop2]"
        results = tx.run(query, prop2=prop_tab[1]).data()
        return [{"employee": result['m']} for result in results]
    elif prop_tab[0] == "orderbyDesc":
        query = "MATCH (m:Employee) RETURN m ORDER BY m[$prop2] DESC"
        results = tx.run(query, prop2=prop_tab[1]).data()
        return [{"employee": result['m']} for result in results]

@app.route('/employees/<string:prop>', methods=['GET'])
def get_employees_props(prop):
    with driver.session() as session:
        employee = session.execute_read(get_emp_prop, prop)
        if not employee:
            return jsonify({"message": 'Employee not found'}), 404
        else:
            return jsonify(employee)

# Task 4 finished
def add_emp(tx, firstname, lastname, position, salary):
    query = "CREATE (m:Employee {firstname: $firstname, lastname: $lastname, position: $position, salary: $salary})"
    tx.run(query, firstname=firstname, lastname=lastname, position=position, salary=salary)

def is_unique(firstname, lastname):
    query = "MATCH (m:Employee {firstname: $firstname, lastname: $lastname}) RETURN COUNT(m) AS count"
    result = driver.session().run(query, firstname=firstname, lastname=lastname).single()
    return result["count"] == 0

@app.route('/employees', methods=['POST'])
def add_employee():
    required_parameters = ['firstname', 'lastname', 'position', 'salary']
    if all(parameter in request.json for parameter in required_parameters):
        firstname = request.json['firstname']
        lastname = request.json['lastname']
        position = request.json['position']
        salary = request.json['salary']
        if is_unique(firstname, lastname):
            with driver.session() as session:
                session.execute_write(add_emp, firstname, lastname, position, salary)

            return jsonify({"status": "Success. Employee added."})
        else:
            return jsonify({"status": "Failure. Employee already exists."}), 500
    else:
        return jsonify({"status": "Failure. Insufficient data."}), 500

# Task 5 finished
def put_emp(tx, employee_id, firstname, lastname, position, salary):
    query = "MATCH (e:Employee) WHERE ID(e)=$employee_id RETURN e"
    result = tx.run(query, employee_id=employee_id).data()
    if not result:
        return None
    else:
        query = "MATCH (e:Employee) WHERE ID(e)=$employee_id " \
                "SET e.firstname=$firstname, e.lastname=$lastname, e.position=$position, e.salary=$salary"
        tx.run(query, employee_id=employee_id, firstname=firstname, lastname=lastname, position=position, salary=salary)
        return {'firstname': firstname, 'lastname': lastname, 'position': position, 'salary': salary}


@app.route("/employees/<int:employee_id>", methods=['PUT'])
def put_employee(employee_id):
    firstname = request.json['firstname']
    lastname = request.json['lastname']
    position = request.json['position']
    salary = request.json['salary']
    with driver.session() as session:
        result = session.execute_write(put_emp, employee_id, firstname, lastname, position, salary)
    if not result:
        return jsonify({'message': 'Employee not found'}), 404
    else:
        return jsonify({'status': 'Success. Employee updated.'}, result)

# Task 6 unfinished
def check_position(tx, employee_id):
    check_position_query = "MATCH (e:Employee)-[:MANAGES]->(d:Department) WHERE ID(e)=$employee_id RETURN ID(d) as Id"
    results = tx.run(check_position_query, employee_id=employee_id).data()
    if results:
        return results

def find_new_menager(tx, employee_id):
    query = "MATCH (e:Employee)-[:WORKS_IN]->(d:Department)<-[:MANAGES]-(m:Employee) " \
            "WHERE ID(m) = $employee_id RETURN ID(e) as Id LIMIT 1"
    results = tx.run(query, employee_id=employee_id).data()
    if results:
        return results

def assign_new_manager(tx, new_id, department_id):
    query = "MATCH (e:Employee)-[r:WORKS_IN]->(d:Department) " \
            "WHERE ID(e) = $new_id AND ID(d) = $department_id " \
            "DELETE r " \
            "CREATE (e)-[:MANAGES]->(d)"
    result = tx.run(query, new_id=new_id, department_id=department_id).data()
    return result
def del_emp(tx, employee_id):
    query = "MATCH (e:Employee) WHERE ID(e)=$employee_id DETACH DELETE e"
    tx.run(query, employee_id=employee_id)
    return {'id': employee_id}
@app.route("/employees/<int:employee_id>", methods=['DELETE'])
def delete_employee(employee_id):
    with driver.session() as session:
        check_position_result = session.execute_read(check_position, employee_id)
        if check_position_result:
            department_id = check_position_result[0]['Id']
            find_new_manager_result = session.execute_read(find_new_menager, employee_id)
            if find_new_manager_result:
                new_id = find_new_manager_result[0]["Id"]
                assign_new_manager_result = session.execute_write(assign_new_manager, new_id, department_id)
                if assign_new_manager_result:
                    delete_manager = session.execute_write(del_emp, employee_id)
                    if delete_manager:
                        return jsonify({'status': 'Success. Manager deleted. New manager assigned.'})

        else:
            delete_employee_node = session.execute_write(del_emp, employee_id)
            if delete_employee_node:
                return jsonify({'status': 'Success. Employee deleted.'})
# Task 7 finished
def get_sub(tx, employee_id):
    query = "MATCH (m:Employee)-[:MANAGES]->(d:Department)<-[:WORKS_IN]-(e:Employee) " \
            "WHERE ID(m) = $employee_id RETURN e"
    results = tx.run(query, employee_id=employee_id).data()
    return [{"subordinate": result['e']} for result in results]

@app.route('/employees/<int:employee_id>/subordinates', methods=['GET'])
def get_subordinates(employee_id):
    with driver.session() as session:
        result = session.execute_read(get_sub, employee_id)
        return jsonify(result)

# Task 9 finished
def get_dep(tx):
    query = "MATCH (d:Department) RETURN d"
    results = tx.run(query).data()
    return results

@app.route('/departments', methods=['GET'])
def get_departments():
    with driver.session() as session:
        results = session.execute_read(get_dep)
        response = {'result': results}
        return jsonify(response)


# Task 9 extended finished
def get_dep_prop(tx, prop):
    prop_tab = prop.split("=")
    if prop_tab[0] == "name":
        query = "MATCH (d:Department) WHERE d.name CONTAINS $prop2 RETURN d"
        results = tx.run(query, prop2=prop_tab[1]).data()
        return [{"department": result['d']} for result in results]
    elif prop_tab[0] == "employees_number":
        query = "MATCH (d:Department)<-[:WORKS_IN]-(e:Employee) " \
                "WITH d AS Department, COUNT(e) AS Employees_number " \
                "WHERE Employees_number = $prop2 " \
                "RETURN Department, Employees_number"
        results = tx.run(query, prop2=int(prop_tab[1])).data()
        return results
    elif prop_tab[0] == "orderbyAsc":
        query = "MATCH (d:Department)<-[:WORKS_IN]-(e:Employee) " \
                "RETURN d as Department, Count(e) as Employees_number ORDER BY Department"
        results = tx.run(query).data()
        return results
    elif prop_tab[0] == "orderbyDesc":
        query = "MATCH (d:Department)<-[:WORKS_IN]-(e:Employee) " \
                "RETURN d as Department, Count(e) as Employees_number ORDER BY Department DESC"
        results = tx.run(query).data()
        return results

@app.route('/departments/<string:prop>', methods=['GET'])
def get_departments_prop(prop):
    with driver.session() as session:
        department = session.execute_read(get_dep_prop, prop)
        if not department:
            return jsonify({"message": 'Department not found'}), 404
        else:
            return jsonify(department)


# Task 10 finished
def get_dep_emp(tx, department_id):
    query = "MATCH (d:Department)<-[:WORKS_IN]-(e:Employee) WHERE ID(d) = $department_id RETURN e"
    results = tx.run(query, department_id=department_id).data()
    return [{"employee": result['e']} for result in results]


@app.route('/departments/<int:department_id>/employees', methods=['GET'])
def get_departments_employees(department_id):
    with driver.session() as session:
        employees = session.execute_read(get_dep_emp, department_id)
        return jsonify(employees)



if __name__ == '__main__':
    app.run()